"""
Test diaper tracking functionality.
"""

import pytest
from datetime import datetime, timedelta
import json

class TestDiaperTracking:
    """Test diaper change logging"""

    def test_log_diaper_pee(self, client):
        """Log a diaper change with pee only"""
        response = client.post('/api/feeds', json={
            "type": "diaper",
            "side": "pee",
            "logged_by": "Mom"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    def test_log_diaper_poop(self, client):
        """Log a diaper change with poop only"""
        response = client.post('/api/feeds', json={
            "type": "diaper",
            "side": "poop",
            "logged_by": "Dad"
        })
        assert response.status_code == 201

    def test_log_diaper_both(self, client):
        """Log a diaper change with both pee and poop"""
        response = client.post('/api/feeds', json={
            "type": "diaper",
            "side": "both",
            "notes": "Blowout - changed outfit"
        })
        assert response.status_code == 201

    def test_diaper_formatting_in_excel(self, client):
        """Verify diaper entries are formatted correctly"""
        client.post('/api/feeds', json={"type": "diaper", "side": "pee"})
        client.post('/api/feeds', json={"type": "diaper", "side": "poop"})
        client.post('/api/feeds', json={"type": "diaper", "side": "both"})

        response = client.get('/api/feeds')
        feeds = response.get_json()['feeds']

        diaper_feeds = [f for f in feeds if 'Diaper' in f['type']]
        assert len(diaper_feeds) == 3

        types = [f['type'] for f in diaper_feeds]
        assert "Diaper (Pee)" in types
        assert "Diaper (Poop)" in types
        assert "Diaper (Both)" in types

    def test_last_diaper_change_calculation(self, client):
        """Verify last diaper change timer is calculated correctly"""
        # Timestamp 30 mins ago
        timestamp = (datetime.now() - timedelta(minutes=30)).isoformat()
        client.post('/api/feeds', json={
            "type": "diaper",
            "side": "pee",
            "timestamp": timestamp
        })

        response = client.get('/api/feeds')
        data = response.get_json()

        assert data['last_diaper_minutes_ago'] is not None
        # Allow small margin for execution time
        assert 28 <= data['last_diaper_minutes_ago'] <= 32

    def test_diaper_stats_count(self, client):
        """Verify diaper changes are counted in stats"""
        client.post('/api/feeds', json={"type": "bottle", "amount_ml": 90})
        client.post('/api/feeds', json={"type": "diaper", "side": "pee"})
        client.post('/api/feeds', json={"type": "diaper", "side": "poop"})

        response = client.get('/api/stats')
        stats = response.get_json()['today']

        assert stats['total_diaper_changes'] == 2

    def test_no_diapers_returns_null(self, client):
        """When no diapers logged, last_diaper fields should be null"""
        client.post('/api/feeds', json={"type": "bottle", "amount_ml": 90})

        response = client.get('/api/feeds')
        data = response.get_json()

        assert data['last_diaper_minutes_ago'] is None
        assert data['last_diaper_summary'] is None
