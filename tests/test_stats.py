"""
Test /api/stats endpoint - summary statistics.
"""

import pytest
from datetime import datetime


class TestStatsEndpoint:
    """Test GET /api/stats"""

    def test_total_oz_bottles_only(self, client, today_str):
        """Total ml from bottles only"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 75.0,
            "timestamp": f"{today_str}T12:00:00"
        })

        response = client.get('/api/stats')
        assert response.status_code == 200
        data = response.get_json()

        assert data['today']['total_ml'] == 165.0

    def test_total_oz_bottles_and_pumps(self, client, today_str):
        """Total ml includes bottles and pumps"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "pump",
            "side": "both",
            "amount_ml": 120.0,
            "timestamp": f"{today_str}T12:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['total_ml'] == 90.0
        assert data['total_pump_ml'] == 120.0

    def test_total_feeds_today(self, client, today_str):
        """Total feeds count is correct"""
        # 3 bottles + 2 nurse sessions = 5 total
        for i in range(3):
            client.post('/api/feeds', json={
                "type": "bottle",
                "amount_ml": 60.0,
                "timestamp": f"{today_str}T{10+i}:00:00"
            })

        for i in range(2):
            client.post('/api/feeds', json={
                "type": "nurse",
                "side": "left",
                "timestamp": f"{today_str}T{13+i}:00:00"
            })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        # Stats only count Bottles, so should be 3
        assert data['total_feeds'] == 3
        # Nurse sessions tracked separately
        assert data['total_nursing_sessions'] == 2

    def test_nursing_session_count(self, client, today_str):
        """Nursing session count is correct"""
        client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left",
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "nurse",
            "side": "right",
            "timestamp": f"{today_str}T12:00:00"
        })
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T14:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['total_nursing_sessions'] == 2

    def test_average_feed_interval(self, client, today_str):
        """Average feed interval is calculated correctly"""
        # Feeds at 1:00, 3:00, 5:00 = 2-hour (120 min) intervals
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0,
            "timestamp": f"{today_str}T01:00:00"
        })
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0,
            "timestamp": f"{today_str}T03:00:00"
        })
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 60.0,
            "timestamp": f"{today_str}T05:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['avg_feed_interval_min'] == 120

    def test_no_feeds_today(self, client):
        """Stats with no feeds return zeros/nulls"""
        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['total_ml'] == 0
        assert data['total_feeds'] == 0
        assert data['total_nursing_sessions'] == 0
        assert data['total_pump_ml'] == 0

    def test_single_feed_no_interval(self, client, today_str):
        """Single feed means no interval can be calculated"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['total_feeds'] == 1
        assert data['avg_feed_interval_min'] is None

    def test_stats_only_count_today(self, client, today_str, yesterday_str):
        """Stats only count today's feeds, not yesterday's"""
        # Add 3 feeds today
        for i in range(3):
            client.post('/api/feeds', json={
                "type": "bottle",
                "amount_ml": 60.0,
                "timestamp": f"{today_str}T{10+i}:00:00"
            })

        # Add 2 feeds yesterday
        for i in range(2):
            client.post('/api/feeds', json={
                "type": "bottle",
                "amount_ml": 60.0,
                "timestamp": f"{yesterday_str}T{10+i}:00:00"
            })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        # Should only count today's 3 feeds
        assert data['total_feeds'] == 3
        assert data['total_ml'] == 180.0

    def test_nursing_doesnt_count_in_total_oz(self, client, today_str):
        """Nursing sessions without amount don't count in total ml"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left",
            "duration_min": 15,
            "timestamp": f"{today_str}T12:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        # Total ml should only be from bottle
        assert data['total_ml'] == 90.0
        # But total feeds should be 1 (stats only count bottles)
        assert data['total_feeds'] == 1

    def test_pump_oz_separate_from_bottle_oz(self, client, today_str):
        """Pump ml is tracked separately"""
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_ml": 90.0,
            "timestamp": f"{today_str}T10:00:00"
        })
        client.post('/api/feeds', json={
            "type": "pump",
            "side": "both",
            "amount_ml": 150.0,
            "timestamp": f"{today_str}T12:00:00"
        })

        response = client.get('/api/stats')
        data = response.get_json()['today']

        assert data['total_ml'] == 90.0  # Only bottles
        assert data['total_pump_ml'] == 150.0  # Just pump
