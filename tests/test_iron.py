"""
Tests for Iron supplement reminder feature.
Mirrors tests/test_vitamin.py exactly, using Iron-specific values.
"""

from datetime import datetime, timedelta


class TestFormatFeedTypeIron:
    """Test that iron feed type formats correctly."""

    def test_format_feed_type_iron(self):
        from app import format_feed_type
        assert format_feed_type("iron") == "Iron"


class TestIronStatus:
    """Test the GET /api/iron-status endpoint."""

    def test_iron_status_not_given(self, client):
        """Status returns given_today=false when no iron logged today."""
        response = client.get('/api/iron-status')
        data = response.get_json()

        assert response.status_code == 200
        assert data['given_today'] is False
        assert data['iron_feed_id'] is None
        assert data['time_given'] is None

    def test_iron_status_given(self, client):
        """After logging iron, status returns given_today=true."""
        client.post('/api/iron', json={'logged_by': 'Mom'})

        response = client.get('/api/iron-status')
        data = response.get_json()

        assert data['given_today'] is True
        assert data['iron_feed_id'] is not None
        assert data['time_given'] is not None


class TestLogIron:
    """Test the POST /api/iron endpoint."""

    def test_log_iron(self, client, today_str):
        """POST iron creates entry with type 'Iron' and notes 'Yes'."""
        response = client.post('/api/iron', json={'logged_by': 'Dad'})
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['id'] is not None

        # Verify the entry appears in feeds
        feeds_response = client.get(f'/api/feeds?date={today_str}')
        feeds = feeds_response.get_json()['feeds']

        iron_feeds = [f for f in feeds if 'Iron' in f['type']]
        assert len(iron_feeds) == 1
        assert iron_feeds[0]['notes'] == 'Yes'
        assert iron_feeds[0]['logged_by'] == 'Dad'

    def test_log_iron_default_logged_by(self, client, today_str):
        """POST iron without logged_by defaults to empty string."""
        response = client.post('/api/iron', json={})
        assert response.status_code == 201

        feeds_response = client.get(f'/api/feeds?date={today_str}')
        feeds = feeds_response.get_json()['feeds']
        iron_feeds = [f for f in feeds if 'Iron' in f['type']]
        assert len(iron_feeds) == 1
        assert iron_feeds[0]['logged_by'] == ''


class TestDeleteIronResetsStatus:
    """Test that deleting iron log resets status."""

    def test_delete_iron_resets_status(self, client):
        """Delete iron log -> status returns given_today=false."""
        # Log iron
        post_response = client.post('/api/iron', json={'logged_by': 'Mom'})
        feed_id = post_response.get_json()['id']

        # Confirm it's given
        status = client.get('/api/iron-status').get_json()
        assert status['given_today'] is True

        # Delete it
        delete_response = client.delete(f'/api/feeds/{feed_id}')
        assert delete_response.get_json()['success'] is True

        # Confirm status resets
        status = client.get('/api/iron-status').get_json()
        assert status['given_today'] is False


class TestIronNotInStats:
    """Test that Iron does not affect feed statistics."""

    def test_iron_not_in_feed_stats(self, client, today_str):
        """Iron log shouldn't count in total_feeds_today or total_ml_today."""
        # Log a bottle feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': datetime.now().isoformat()
        })

        # Get baseline stats
        response = client.get(f'/api/feeds?date={today_str}')
        baseline = response.get_json()
        baseline_feeds = baseline['total_feeds_today']
        baseline_ml = baseline['total_ml_today']

        # Log iron
        client.post('/api/iron', json={'logged_by': 'Mom'})

        # Stats should not change
        response = client.get(f'/api/feeds?date={today_str}')
        after_iron = response.get_json()

        assert after_iron['total_feeds_today'] == baseline_feeds
        assert after_iron['total_ml_today'] == baseline_ml

    def test_iron_not_in_last_feed(self, client, today_str):
        """Iron log shouldn't show as 'last feed'."""
        # Log a bottle feed first
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': datetime.now().isoformat()
        })

        # Get last feed summary
        response = client.get(f'/api/feeds?date={today_str}')
        baseline_summary = response.get_json()['last_feed_summary']

        # Log iron (this should NOT become the 'last feed')
        client.post('/api/iron', json={'logged_by': 'Mom'})

        # Last feed summary should still be the bottle feed
        response = client.get(f'/api/feeds?date={today_str}')
        after = response.get_json()
        assert after['last_feed_summary'] == baseline_summary

    def test_iron_not_in_api_stats(self, client):
        """Iron log should not affect /api/stats counts."""
        # Log a bottle feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': datetime.now().isoformat()
        })

        # Baseline stats
        stats_before = client.get('/api/stats').get_json()['today']

        # Log iron
        client.post('/api/iron', json={'logged_by': 'Mom'})

        # Stats should be unchanged
        stats_after = client.get('/api/stats').get_json()['today']
        assert stats_after['total_feeds'] == stats_before['total_feeds']
        assert stats_after['total_ml'] == stats_before['total_ml']


class TestMissedIronDoseAutoLog:
    """Test lazy auto-logging of missed iron doses."""

    def test_missed_dose_auto_log(self, client, yesterday_str):
        """If yesterday has feeds but no iron, status endpoint auto-logs missed dose."""
        # Seed yesterday with a feed (but no iron)
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Hit iron status (triggers lazy missed-dose check)
        client.get('/api/iron-status')

        # Verify yesterday now has a missed dose entry
        response = client.get(f'/api/feeds?date={yesterday_str}')
        feeds = response.get_json()['feeds']
        iron_feeds = [f for f in feeds if 'Iron' in f['type']]

        assert len(iron_feeds) == 1
        assert iron_feeds[0]['notes'] == 'No'
        assert iron_feeds[0]['logged_by'] == 'Auto'

    def test_no_double_missed_dose(self, client, yesterday_str):
        """Calling iron-status twice should not create duplicate missed entries."""
        # Seed yesterday with a feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Hit status twice
        client.get('/api/iron-status')
        client.get('/api/iron-status')

        # Should still only have one missed dose
        response = client.get(f'/api/feeds?date={yesterday_str}')
        feeds = response.get_json()['feeds']
        iron_feeds = [f for f in feeds if 'Iron' in f['type']]
        assert len(iron_feeds) == 1
