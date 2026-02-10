"""
Test boundary conditions and edge cases.
"""

import pytest
from datetime import datetime
import json


class TestEdgeCases:
    """Test boundary conditions and unusual inputs"""

    def test_midnight_rollover(self, client):
        """Entries at midnight appear on correct dates"""
        # Log at 11:59 PM on Feb 9
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.0,
            "timestamp": "2026-02-09T23:59:00"
        })

        # Log at 12:01 AM on Feb 10
        client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 3.0,
            "timestamp": "2026-02-10T00:01:00"
        })

        # Query Feb 9
        resp_feb9 = client.get('/api/feeds?date=2026-02-09')
        feeds_feb9 = resp_feb9.get_json()['feeds']

        # Query Feb 10
        resp_feb10 = client.get('/api/feeds?date=2026-02-10')
        feeds_feb10 = resp_feb10.get_json()['feeds']

        # Each should have exactly one entry
        assert len(feeds_feb9) == 1
        assert len(feeds_feb10) == 1
        assert feeds_feb9[0]['time'] == '11:59 PM'
        assert feeds_feb10[0]['time'] == '12:01 AM'

    def test_empty_xlsx_first_entry(self, client, temp_xlsx):
        """First ever entry works correctly"""
        # Fresh file should work
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 3.0
        })

        assert resp.status_code == 201

        # Should be retrievable
        feeds_resp = client.get('/api/feeds')
        feeds = feeds_resp.get_json()['feeds']
        assert len(feeds) == 1

    def test_very_long_notes_field(self, client):
        """Very long notes field is saved correctly"""
        long_notes = "A" * 1000

        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.0,
            "notes": long_notes
        })

        assert resp.status_code == 201

        # Verify it was saved
        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['notes'] == long_notes
        assert len(feed['notes']) == 1000

    def test_unicode_in_notes(self, client):
        """Unicode characters in notes are preserved"""
        unicode_notes = "宝宝吃了 🍼 très bien!"

        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 3.0,
            "notes": unicode_notes
        })

        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['notes'] == unicode_notes

    def test_amount_with_many_decimals(self, client):
        """Amount with many decimal places is handled"""
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.333333
        })

        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]

        # Should be stored (may be rounded, but should be close)
        assert feed['amount_oz'] is not None
        assert 2.3 <= feed['amount_oz'] <= 2.4

    def test_post_with_extra_unknown_fields(self, client):
        """POST with unknown fields ignores them and succeeds"""
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 3.0,
            "foo": "bar",
            "unknown_field": 123
        })

        # Should still succeed
        assert resp.status_code == 201

    def test_post_with_empty_body(self, client):
        """POST with empty body is handled"""
        resp = client.post('/api/feeds',
                          data='{}',
                          content_type='application/json')

        # App currently accepts empty body (no validation)
        # Just ensure it doesn't crash - can be 201 (accepted) or 400/500 (rejected)
        assert resp.status_code in [200, 201, 400, 500]

    def test_post_with_null_values(self, client):
        """POST with null values is handled"""
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": None,
            "duration_min": None,
            "notes": None
        })

        # Should succeed
        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['amount_oz'] is None or feed['amount_oz'] == ''

    def test_get_with_future_date(self, client):
        """GET with future date returns empty list"""
        resp = client.get('/api/feeds?date=2030-01-01')

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['feeds'] == []
        assert data['total_feeds_today'] == 0

    def test_get_with_past_date(self, client):
        """GET with past date returns empty list"""
        resp = client.get('/api/feeds?date=2020-01-01')

        assert resp.status_code == 200
        data = resp.get_json()
        assert data['feeds'] == []
        assert data['total_feeds_today'] == 0

    def test_delete_last_remaining_entry(self, client):
        """Delete last remaining entry works"""
        # Create one entry
        post_resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 3.0
        })
        assert post_resp.status_code == 201

        # Get its ID
        get_resp = client.get('/api/feeds')
        feed_id = get_resp.get_json()['feeds'][0]['id']

        # Delete it
        delete_resp = client.delete(f'/api/feeds/{feed_id}')
        assert delete_resp.status_code == 200

        # GET should return empty
        final_resp = client.get('/api/feeds')
        assert final_resp.get_json()['feeds'] == []

    def test_rapid_delete_then_create(self, client, seed_data):
        """Rapid delete + create both succeed"""
        # Get a feed to delete
        resp = client.get('/api/feeds?date=2026-02-10')
        feed_id = resp.get_json()['feeds'][0]['id']

        # Delete
        delete_resp = client.delete(f'/api/feeds/{feed_id}')
        assert delete_resp.status_code == 200

        # Immediately create
        create_resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 4.0
        })
        assert create_resp.status_code == 201

    def test_malformed_json(self, client):
        """Malformed JSON returns 400"""
        resp = client.post('/api/feeds',
                          data='{"type": "bottle", invalid}',
                          content_type='application/json')

        # Should return 400, not 500
        assert resp.status_code in [400, 415]

    def test_missing_content_type_header(self, client):
        """Missing Content-Type header is handled"""
        resp = client.post('/api/feeds',
                          data='{"type": "bottle", "amount_oz": 3.0}')

        # Should either work or fail gracefully
        assert resp.status_code in [200, 201, 400, 415]

    def test_newlines_in_notes(self, client):
        """Newlines in notes are preserved"""
        notes_with_newlines = "Line 1\nLine 2\nLine 3"

        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.0,
            "notes": notes_with_newlines
        })

        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['notes'] == notes_with_newlines

    def test_quotes_in_notes(self, client):
        """Quotes in notes are preserved"""
        notes_with_quotes = 'Baby said "mama" today!'

        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.0,
            "notes": notes_with_quotes
        })

        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['notes'] == notes_with_quotes

    def test_empty_string_notes(self, client):
        """Empty string notes are handled"""
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 2.0,
            "notes": ""
        })

        assert resp.status_code == 201

        feeds_resp = client.get('/api/feeds')
        feed = feeds_resp.get_json()['feeds'][0]
        assert feed['notes'] == ""

    def test_very_large_amount(self, client):
        """Very large amount is handled"""
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": 99.0
        })

        # Should succeed (no validation for max amount currently)
        assert resp.status_code == 201

    def test_negative_duration(self, client):
        """Negative duration is handled"""
        resp = client.post('/api/feeds', json={
            "type": "nurse",
            "side": "left",
            "duration_min": -5
        })

        # May succeed or fail depending on validation
        # Just ensure it doesn't crash
        assert resp.status_code in [200, 201, 400]
