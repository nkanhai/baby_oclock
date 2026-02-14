"""
Test CRUD operations for the /api/feeds endpoint.
"""

import pytest
from datetime import datetime, timedelta


class TestCreateFeed:
    """Test POST /api/feeds"""

    def test_log_bottle_feed_with_amount(self, client):
        """Log a bottle feed with amount"""
        response = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'id' in data

    def test_log_nursing_with_side_and_duration(self, client):
        """Log a nursing session with side and duration"""
        response = client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left",
            "duration_min": 12
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    def test_log_pump_with_side_and_amount(self, client):
        """Log a pump with side and amount"""
        response = client.post('/api/feeds', json={
            "type": "pump",
            "side": "both",
            "amount_ml": 120.0
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    def test_log_without_timestamp_uses_current_time(self, client):
        """Log without timestamp - server should use current time"""
        before = datetime.now()
        response = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0
        })
        after = datetime.now()

        assert response.status_code == 201

        # Verify timestamp is recent by checking the feed
        feeds_response = client.get('/api/feeds')
        feeds = feeds_response.get_json()['feeds']
        latest_feed = feeds[0]  # Most recent first

        feed_time = datetime.fromisoformat(latest_feed['timestamp'])
        if feed_time.tzinfo:
            feed_time = feed_time.replace(tzinfo=None)
        assert before <= feed_time <= after + timedelta(seconds=5)

    def test_log_with_explicit_timestamp(self, client):
        """Log with explicit timestamp"""
        timestamp = "2026-02-10T03:00:00"
        response = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0,
            "timestamp": timestamp
        })
        assert response.status_code == 201

        # Verify the timestamp was used
        feeds_response = client.get('/api/feeds?date=2026-02-10')
        feeds = feeds_response.get_json()['feeds']
        assert any(f['timestamp'].startswith('2026-02-10T03:00') for f in feeds)

    def test_log_with_logged_by_field(self, client):
        """Log with logged_by field"""
        response = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "logged_by": "Dad"
        })
        assert response.status_code == 201

        feeds_response = client.get('/api/feeds')
        feeds = feeds_response.get_json()['feeds']
        assert feeds[0]['logged_by'] == "Dad"

    def test_log_with_notes(self, client):
        """Log with notes"""
        response = client.post('/api/feeds', json={
            "type": "nurse",
            "side": "right",
            "notes": "baby was fussy"
        })
        assert response.status_code == 201

        feeds_response = client.get('/api/feeds')
        feeds = feeds_response.get_json()['feeds']
        assert feeds[0]['notes'] == "baby was fussy"

    def test_log_with_zero_amount(self, client):
        """Log with amount_ml = 0"""
        response = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 0
        })
        assert response.status_code == 201

        feeds_response = client.get('/api/feeds')
        feeds = feeds_response.get_json()['feeds']
        assert feeds[0]['amount_ml'] == 0

    def test_log_nurse_without_amount(self, client):
        """Log nurse with no amount (common case)"""
        response = client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left"
        })
        assert response.status_code == 201

        feeds_response = client.get('/api/feeds')
        feeds = feeds_response.get_json()['feeds']
        assert feeds[0]['amount_ml'] is None or feeds[0]['amount_ml'] == ''

    def test_log_diaper_change(self, client):
        """Log a diaper change"""
        response = client.post('/api/feeds', json={
            "type": "diaper",
            "side": "pee"
        })
        assert response.status_code == 201


class TestReadFeeds:
    """Test GET /api/feeds"""

    def test_get_todays_feeds_default(self, client, seed_data, today_str):
        """Get today's feeds (default behavior)"""
        # First, add a feed for today
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })

        response = client.get('/api/feeds')
        assert response.status_code == 200
        data = response.get_json()

        assert 'feeds' in data
        assert isinstance(data['feeds'], list)

        # All feeds should be from today
        for feed in data['feeds']:
            assert feed['date'] == today_str

    def test_get_feeds_for_specific_date(self, client, seed_data):
        """Get feeds for a specific date"""
        response = client.get('/api/feeds?date=2026-02-09')
        assert response.status_code == 200
        data = response.get_json()

        # Should only get feeds from 2026-02-09
        for feed in data['feeds']:
            assert feed['date'] == '2026-02-09'

    def test_empty_day_returns_empty_list(self, client):
        """Empty day returns empty list"""
        response = client.get('/api/feeds?date=2025-01-01')
        assert response.status_code == 200
        data = response.get_json()

        assert data['feeds'] == []
        assert data['last_feed_minutes_ago'] is None
        assert data['total_feeds_today'] == 0

    def test_feeds_in_reverse_chronological_order(self, client):
        """Feeds are returned in reverse chronological order"""
        # Create feeds with known timestamps
        timestamps = [
            "2026-02-10T10:00:00",
            "2026-02-10T12:00:00",
            "2026-02-10T11:00:00",
        ]

        for ts in timestamps:
            client.post('/api/feeds', json={
                "type": "bottle",
                "amount_ml": 30.0,
                "timestamp": ts
            })

        response = client.get('/api/feeds?date=2026-02-10')
        feeds = response.get_json()['feeds']

        # Should be sorted newest first: 12:00, 11:00, 10:00
        assert feeds[0]['time'] == '12:00 PM'
        assert feeds[1]['time'] == '11:00 AM'
        assert feeds[2]['time'] == '10:00 AM'

    def test_response_includes_last_feed_minutes_ago(self, client):
        """Response includes last_feed_minutes_ago"""
        now = datetime.now()
        thirty_min_ago = now - timedelta(minutes=30)

        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": thirty_min_ago.isoformat()
        })

        # Request the specific date properly to handle midnight boundary
        query_date = thirty_min_ago.strftime("%Y-%m-%d")
        response = client.get(f'/api/feeds?date={query_date}')
        data = response.get_json()

        # Should be approximately 30 minutes (allow some tolerance)
        assert data['last_feed_minutes_ago'] is not None
        assert 29 <= data['last_feed_minutes_ago'] <= 31

    def test_response_includes_total_ml_today(self, client, today_str):
        """Response includes total_ml_today"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0,
            "timestamp": f"{today_str}T11:00:00"
        })

        response = client.get('/api/feeds')
        data = response.get_json()

        assert data['total_ml_today'] == 150.0

    def test_response_includes_total_feeds_today(self, client, today_str):
        """Response includes total_feeds_today"""
        for i in range(3):
            client.post('/api/feeds', json={
                "type": "bottle",
                "amount_ml": 60.0,
                "timestamp": f"{today_str}T{10+i}:00:00"
            })

        response = client.get('/api/feeds')
        data = response.get_json()

        assert data['total_feeds_today'] == 3


    def test_pump_and_diaper_excluded_from_totals(self, client, today_str):
        """Pump and diaper entries should not count towards total feeds or ml"""
        # Add a bottle feed (should count)
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 100.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        
        # Add a pump session (should NOT count)
        client.post('/api/feeds', json={
            "type": "pump",
            "side": "both",
            "amount_ml": 150.0,
            "timestamp": f"{today_str}T11:00:00"
        })
        
        # Add a diaper change (should NOT count)
        client.post('/api/feeds', json={
            "type": "diaper",
            "side": "pee",
            "timestamp": f"{today_str}T12:00:00"
        })

        response = client.get('/api/feeds')
        data = response.get_json()

        # Should only count the 1 bottle feed
        assert data['total_feeds_today'] == 1
        # Should only sum the 1 bottle amount
        assert data['total_ml_today'] == 100.0


class TestDeleteFeed:
    """Test DELETE /api/feeds/<id>"""

    def test_delete_existing_entry(self, client, seed_data):
        """Delete an existing entry"""
        # Get current feeds
        response = client.get('/api/feeds?date=2026-02-10')
        feeds_before = response.get_json()['feeds']
        count_before = len(feeds_before)

        # Remember the timestamp of the feed we're deleting
        feed_to_delete = feeds_before[0]
        feed_id = feed_to_delete['id']
        deleted_timestamp = feed_to_delete['timestamp']

        delete_response = client.delete(f'/api/feeds/{feed_id}')
        assert delete_response.status_code == 200

        # Verify count decreased
        response = client.get('/api/feeds?date=2026-02-10')
        feeds_after = response.get_json()['feeds']
        assert len(feeds_after) == count_before - 1

        # Verify the deleted feed's timestamp is not in the list
        assert all(f['timestamp'] != deleted_timestamp for f in feeds_after)

    def test_delete_nonexistent_entry(self, client):
        """Delete non-existent entry returns 404"""
        response = client.delete('/api/feeds/9999')
        assert response.status_code == 404

    def test_delete_doesnt_affect_other_entries(self, client, seed_data):
        """Delete doesn't affect other entries"""
        # Get feeds
        response = client.get('/api/feeds?date=2026-02-09')
        feeds_before = response.get_json()['feeds']

        # Delete middle entry
        middle_feed = feeds_before[1]
        middle_timestamp = middle_feed['timestamp']
        client.delete(f'/api/feeds/{middle_feed["id"]}')

        # Check other entries still exist
        response = client.get('/api/feeds?date=2026-02-09')
        feeds_after = response.get_json()['feeds']

        # Should have 1 fewer entry
        assert len(feeds_after) == len(feeds_before) - 1

        # Other timestamps should still be present
        remaining_timestamps = [f['timestamp'] for f in feeds_after]
        assert feeds_before[0]['timestamp'] in remaining_timestamps
        assert feeds_before[2]['timestamp'] in remaining_timestamps
        assert middle_timestamp not in remaining_timestamps


class TestUpdateFeed:
    """Test PUT /api/feeds/<id>"""

    def test_update_amount(self, client, seed_data):
        """Update amount of an entry"""
        # Get a feed
        response = client.get('/api/feeds?date=2026-02-10')
        feed = response.get_json()['feeds'][0]
        feed_id = feed['id']

        # Update amount
        update_response = client.put(f'/api/feeds/{feed_id}', json={
            "type": feed['type'].split()[0].lower(),
            "amount_ml": 150.0
        })
        assert update_response.status_code == 200

        # Verify update
        response = client.get('/api/feeds?date=2026-02-10')
        updated_feed = next(f for f in response.get_json()['feeds'] if f['id'] == feed_id)
        assert updated_feed['amount_ml'] == 150.0

    def test_update_notes(self, client, seed_data):
        """Update notes of an entry"""
        # Get a feed
        response = client.get('/api/feeds?date=2026-02-10')
        feed = response.get_json()['feeds'][0]
        feed_id = feed['id']

        # Update notes
        update_response = client.put(f'/api/feeds/{feed_id}', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "notes": "Added note after the fact"
        })
        assert update_response.status_code == 200

        # Verify update
        response = client.get('/api/feeds?date=2026-02-10')
        updated_feed = next(f for f in response.get_json()['feeds'] if f['id'] == feed_id)
        assert updated_feed['notes'] == "Added note after the fact"

    def test_update_nonexistent_entry(self, client):
        """Update non-existent entry returns 404"""
        response = client.put('/api/feeds/9999', json={
            "type": "bottle",
            "amount_ml": 90.0
        })
        assert response.status_code == 404
