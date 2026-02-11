"""
Test history filtering logic for /api/feeds.
"""

import pytest
from datetime import datetime, timedelta

class TestHistoryFeeds:
    """Test GET /api/feeds with limit_days"""

    def test_get_history_feeds(self, client, seed_data):
        """Test fetching 7 days of history"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        eight_days_ago = today - timedelta(days=8)

        # Add feed for today
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 50,
            "timestamp": today.isoformat()
        })

        # Add yesterday feed
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 100,
            "timestamp": yesterday.isoformat()
        })

        # Add 8 days ago feed
        client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left",
            "timestamp": eight_days_ago.isoformat()
        })

        # Request 7 days history
        response = client.get('/api/feeds?limit_days=7')
        assert response.status_code == 200
        data = response.get_json()
        feeds = data['feeds']

        dates = [f['date'] for f in feeds]
        
        # Should include today (from seed or default)
        assert today.strftime("%Y-%m-%d") in dates
        
        # Should include yesterday
        assert yesterday.strftime("%Y-%m-%d") in dates
        
        # Should NOT include 8 days ago
        assert eight_days_ago.strftime("%Y-%m-%d") not in dates

    def test_default_behavior_is_still_today_only(self, client):
        """Test default behavior remains unchanged"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # Add yesterday feed
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 100,
            "timestamp": yesterday.isoformat()
        })

        # Request default
        response = client.get('/api/feeds')
        data = response.get_json()
        feeds = data['feeds']

        dates = [f['date'] for f in feeds]
        
        # Should include today
        # (Assuming we have today's feeds from setup or empty if none)
        
        # Should NOT include yesterday
        assert yesterday.strftime("%Y-%m-%d") not in dates
