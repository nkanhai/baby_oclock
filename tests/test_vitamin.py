"""
Tests for Vitamin D reminder feature.
"""

import json
from datetime import datetime, timedelta


class TestFormatFeedTypeVitamin:
    """Test that vitamin_d feed type formats correctly."""

    def test_format_feed_type_vitamin(self):
        from app import format_feed_type
        assert format_feed_type("vitamin_d") == "Vitamin D"


class TestVitaminStatus:
    """Test the GET /api/vitamin-status endpoint."""

    def test_vitamin_status_not_given(self, client):
        """Status returns given_today=false when no vitamin logged today."""
        response = client.get('/api/vitamin-status')
        data = response.get_json()

        assert response.status_code == 200
        assert data['given_today'] is False
        assert data['vitamin_feed_id'] is None
        assert data['time_given'] is None

    def test_vitamin_status_given(self, client):
        """After logging vitamin, status returns given_today=true."""
        # Log vitamin
        client.post('/api/vitamin', json={'logged_by': 'Mom'})

        # Check status
        response = client.get('/api/vitamin-status')
        data = response.get_json()

        assert data['given_today'] is True
        assert data['vitamin_feed_id'] is not None
        assert data['time_given'] is not None


class TestLogVitamin:
    """Test the POST /api/vitamin endpoint."""

    def test_log_vitamin(self, client, today_str):
        """POST vitamin creates entry with type 'Vitamin D' and notes 'Yes'."""
        response = client.post('/api/vitamin', json={'logged_by': 'Dad'})
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['id'] is not None

        # Verify the entry in feeds
        feeds_response = client.get(f'/api/feeds?date={today_str}')
        feeds = feeds_response.get_json()['feeds']

        vitamin_feeds = [f for f in feeds if 'Vitamin D' in f['type']]
        assert len(vitamin_feeds) == 1
        assert vitamin_feeds[0]['notes'] == 'Yes'
        assert vitamin_feeds[0]['logged_by'] == 'Dad'

    def test_log_vitamin_default_logged_by(self, client, today_str):
        """POST vitamin without logged_by defaults to empty string."""
        response = client.post('/api/vitamin', json={})
        assert response.status_code == 201

        feeds_response = client.get(f'/api/feeds?date={today_str}')
        feeds = feeds_response.get_json()['feeds']
        vitamin_feeds = [f for f in feeds if 'Vitamin D' in f['type']]
        assert len(vitamin_feeds) == 1
        assert vitamin_feeds[0]['logged_by'] == ''


class TestDeleteVitaminResetsStatus:
    """Test that deleting vitamin log resets status."""

    def test_delete_vitamin_resets_status(self, client):
        """Delete vitamin log -> status returns given_today=false."""
        # Log vitamin
        post_response = client.post('/api/vitamin', json={'logged_by': 'Mom'})
        feed_id = post_response.get_json()['id']

        # Confirm it's given
        status = client.get('/api/vitamin-status').get_json()
        assert status['given_today'] is True

        # Delete it
        delete_response = client.delete(f'/api/feeds/{feed_id}')
        assert delete_response.get_json()['success'] is True

        # Confirm status resets
        status = client.get('/api/vitamin-status').get_json()
        assert status['given_today'] is False


class TestVitaminNotInStats:
    """Test that Vitamin D doesn't affect feed statistics."""

    def test_vitamin_not_in_feed_stats(self, client, today_str):
        """Vitamin log shouldn't count in total_feeds_today or total_ml_today."""
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

        # Log vitamin
        client.post('/api/vitamin', json={'logged_by': 'Mom'})

        # Stats should not change
        response = client.get(f'/api/feeds?date={today_str}')
        after_vitamin = response.get_json()

        assert after_vitamin['total_feeds_today'] == baseline_feeds
        assert after_vitamin['total_ml_today'] == baseline_ml

    def test_vitamin_not_in_last_feed(self, client, today_str):
        """Vitamin log shouldn't show as 'last feed'."""
        # Log a bottle feed first
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': datetime.now().isoformat()
        })

        # Get last feed summary
        response = client.get(f'/api/feeds?date={today_str}')
        baseline = response.get_json()
        baseline_summary = baseline['last_feed_summary']

        # Log vitamin (this should NOT become the 'last feed')
        client.post('/api/vitamin', json={'logged_by': 'Mom'})

        # Last feed summary should still be the bottle feed
        response = client.get(f'/api/feeds?date={today_str}')
        after = response.get_json()
        assert after['last_feed_summary'] == baseline_summary

    def test_vitamin_not_in_api_stats(self, client):
        """Vitamin log should not affect /api/stats counts."""
        # Log a bottle feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': datetime.now().isoformat()
        })

        # Baseline stats
        stats_before = client.get('/api/stats').get_json()['today']

        # Log vitamin
        client.post('/api/vitamin', json={'logged_by': 'Mom'})

        # Stats should be unchanged
        stats_after = client.get('/api/stats').get_json()['today']
        assert stats_after['total_feeds'] == stats_before['total_feeds']
        assert stats_after['total_ml'] == stats_before['total_ml']


class TestMissedDoseAutoLog:
    """Test lazy auto-logging of missed vitamin doses."""

    def test_missed_dose_auto_log(self, client, yesterday_str):
        """If yesterday has feeds but no vitamin, status endpoint auto-logs missed dose."""
        # Seed yesterday with a feed (but no vitamin)
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Hit vitamin status (triggers lazy missed-dose check)
        client.get('/api/vitamin-status')

        # Verify yesterday now has a missed dose entry
        response = client.get(f'/api/feeds?date={yesterday_str}')
        feeds = response.get_json()['feeds']
        vitamin_feeds = [f for f in feeds if 'Vitamin D' in f['type']]

        assert len(vitamin_feeds) == 1
        assert vitamin_feeds[0]['notes'] == 'No'
        assert vitamin_feeds[0]['logged_by'] == 'Auto'

    def test_no_double_missed_dose(self, client, yesterday_str):
        """Calling vitamin-status twice should not create duplicate missed entries."""
        # Seed yesterday with a feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'amount_ml': 100,
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Hit status twice
        client.get('/api/vitamin-status')
        client.get('/api/vitamin-status')

        # Should still only have one missed dose
        response = client.get(f'/api/feeds?date={yesterday_str}')
        feeds = response.get_json()['feeds']
        vitamin_feeds = [f for f in feeds if 'Vitamin D' in f['type']]
        assert len(vitamin_feeds) == 1
