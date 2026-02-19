"""
Tests for Mom pill daily reminder feature.
Covers all 6 pill slots: prenatal, moringa_am, moringa_pm, stool_am, stool_pm, vitamin_d.
"""

from datetime import datetime, timedelta
import pytest


# ---------------------------------------------------------------------------
# format_feed_type tests
# ---------------------------------------------------------------------------

class TestFormatFeedTypeMomPills:
    """Test that all mom pill types format correctly."""

    def test_format_prenatal(self):
        from app import format_feed_type
        assert format_feed_type("mom_prenatal") == "Pre-Natal (Mom)"

    def test_format_moringa_am(self):
        from app import format_feed_type
        assert format_feed_type("mom_moringa_am") == "Moringa AM (Mom)"

    def test_format_moringa_pm(self):
        from app import format_feed_type
        assert format_feed_type("mom_moringa_pm") == "Moringa PM (Mom)"

    def test_format_stool_am(self):
        from app import format_feed_type
        assert format_feed_type("mom_stool_am") == "Stool Softener AM (Mom)"

    def test_format_stool_pm(self):
        from app import format_feed_type
        assert format_feed_type("mom_stool_pm") == "Stool Softener PM (Mom)"

    def test_format_mom_vitamin_d(self):
        from app import format_feed_type
        assert format_feed_type("mom_vitamin_d") == "Vitamin D (Mom)"


# ---------------------------------------------------------------------------
# GET /api/mom-pills-status tests
# ---------------------------------------------------------------------------

class TestMomPillsStatus:
    """Test the GET /api/mom-pills-status endpoint."""

    def test_status_all_pending_when_nothing_logged(self, client):
        """Fresh state: all slots return given=false and remaining=6."""
        response = client.get('/api/mom-pills-status')
        data = response.get_json()

        assert response.status_code == 200
        for key in ['prenatal', 'moringa_am', 'moringa_pm', 'stool_am', 'stool_pm', 'vitamin_d']:
            assert data[key]['given'] is False, f"Expected {key} not given"
            assert data[key]['feed_id'] is None
        assert data['remaining'] == 6

    def test_status_given_after_logging(self, client):
        """After logging prenatal, its slot shows given=true."""
        client.post('/api/mom-pill', json={'pill': 'prenatal', 'logged_by': 'Mom'})

        response = client.get('/api/mom-pills-status')
        data = response.get_json()

        assert data['prenatal']['given'] is True
        assert data['prenatal']['feed_id'] is not None
        assert data['prenatal']['time'] is not None
        assert data['remaining'] == 5

    def test_remaining_decrements_correctly(self, client):
        """remaining count decrements as pills are logged."""
        pills = ['prenatal', 'moringa_am', 'moringa_pm']
        for pill in pills:
            client.post('/api/mom-pill', json={'pill': pill})

        data = client.get('/api/mom-pills-status').get_json()
        assert data['remaining'] == 3

    def test_all_taken_remaining_zero(self, client):
        """remaining=0 when all 6 pills logged."""
        for pill in ['prenatal', 'moringa_am', 'moringa_pm', 'stool_am', 'stool_pm', 'vitamin_d']:
            client.post('/api/mom-pill', json={'pill': pill})

        data = client.get('/api/mom-pills-status').get_json()
        assert data['remaining'] == 0


# ---------------------------------------------------------------------------
# POST /api/mom-pill tests
# ---------------------------------------------------------------------------

class TestLogMomPill:
    """Test the POST /api/mom-pill endpoint."""

    def test_log_prenatal(self, client, today_str):
        """POST prenatal creates an entry with correct type and notes."""
        response = client.post('/api/mom-pill', json={'pill': 'prenatal', 'logged_by': 'Mom'})
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert data['id'] is not None
        assert data['label'] == 'Pre-Natal'

        # Verify in feeds
        feeds = client.get(f'/api/feeds?date={today_str}').get_json()['feeds']
        prenatal_feeds = [f for f in feeds if f['type'] == 'Pre-Natal (Mom)']
        assert len(prenatal_feeds) == 1
        assert prenatal_feeds[0]['notes'] == 'Yes'
        assert prenatal_feeds[0]['logged_by'] == 'Mom'

    def test_log_unknown_pill_returns_400(self, client):
        """POSTing an unknown pill key returns 400."""
        response = client.post('/api/mom-pill', json={'pill': 'unicorn_pill'})
        assert response.status_code == 400
        assert response.get_json()['success'] is False

    def test_log_all_six_pills(self, client, today_str):
        """All 6 pill keys can be logged successfully."""
        keys = ['prenatal', 'moringa_am', 'moringa_pm', 'stool_am', 'stool_pm', 'vitamin_d']
        for key in keys:
            r = client.post('/api/mom-pill', json={'pill': key})
            assert r.status_code == 201, f"Failed to log {key}"


# ---------------------------------------------------------------------------
# Delete / undo tests
# ---------------------------------------------------------------------------

class TestDeleteMomPill:
    """Test that deleting a mom pill entry resets its status."""

    def test_delete_resets_status(self, client):
        """Deleting a prenatal entry reverts its status to not-given."""
        # Log it
        log_resp = client.post('/api/mom-pill', json={'pill': 'prenatal'})
        feed_id = log_resp.get_json()['id']

        # Verify given
        assert client.get('/api/mom-pills-status').get_json()['prenatal']['given'] is True

        # Delete
        del_resp = client.delete(f'/api/feeds/{feed_id}')
        assert del_resp.get_json()['success'] is True

        # Verify reverted
        status = client.get('/api/mom-pills-status').get_json()
        assert status['prenatal']['given'] is False
        assert status['remaining'] == 6


# ---------------------------------------------------------------------------
# Stats exclusion tests
# ---------------------------------------------------------------------------

class TestMomPillsExcludedFromBabyStats:
    """Mom pill entries must not appear in baby feed statistics."""

    def test_mom_pills_excluded_from_total_feeds(self, client, today_str):
        """total_feeds_today ignores mom pill entries."""
        # Log a mom pill
        client.post('/api/mom-pill', json={'pill': 'prenatal'})

        feeds_data = client.get(f'/api/feeds?date={today_str}').get_json()
        assert feeds_data['total_feeds_today'] == 0

    def test_mom_pills_excluded_from_total_ml(self, client, today_str):
        """total_ml_today ignores mom pill entries."""
        client.post('/api/mom-pill', json={'pill': 'moringa_am'})

        feeds_data = client.get(f'/api/feeds?date={today_str}').get_json()
        assert feeds_data['total_ml_today'] == 0

    def test_mom_pills_excluded_from_last_feed(self, client, today_str):
        """last_feed_summary ignores mom pill entries."""
        client.post('/api/mom-pill', json={'pill': 'stool_am'})

        feeds_data = client.get(f'/api/feeds?date={today_str}').get_json()
        assert feeds_data['last_feed_summary'] is None

    def test_mom_pills_excluded_from_api_stats(self, client):
        """GET /api/stats ignores mom pill entries."""
        client.post('/api/mom-pill', json={'pill': 'vitamin_d'})

        stats = client.get('/api/stats').get_json()['today']
        assert stats['total_feeds'] == 0
        assert stats['total_ml'] == 0


# ---------------------------------------------------------------------------
# Missed-dose auto-logging tests
# ---------------------------------------------------------------------------

class TestMomPillsMissedDoseAutoLogging:
    """Test that missed doses for yesterday are auto-logged."""

    def test_missed_dose_auto_logged_when_no_yesterday_entry(self, client, today_str):
        """If yesterday had feeds but no mom pills, auto-log missed entries."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Create a real feed yesterday so the auto-logging condition triggers
        client.post('/api/feeds', json={
            'type': 'bottle',
            'side': 'formula',
            'amount_ml': 100,
            'duration_min': None,
            'notes': '',
            'logged_by': 'Mom',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Trigger status check (this runs auto-logging)
        client.get('/api/mom-pills-status')

        # Verify all 6 mom pill types appear yesterday with notes='No'
        from app import get_feeds_from_excel
        yesterday_feeds = get_feeds_from_excel(yesterday)
        missed_types = {f['type'] for f in yesterday_feeds if f.get('notes') == 'No' and '(Mom)' in f['type']}
        expected_types = {
            'Pre-Natal (Mom)', 'Moringa AM (Mom)', 'Moringa PM (Mom)',
            'Stool Softener AM (Mom)', 'Stool Softener PM (Mom)', 'Vitamin D (Mom)'
        }
        assert expected_types == missed_types

    def test_auto_logging_is_idempotent(self, client):
        """Calling status twice doesn't create duplicate missed entries."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Yesterday feed
        client.post('/api/feeds', json={
            'type': 'bottle',
            'side': 'formula',
            'amount_ml': 80,
            'duration_min': None,
            'notes': '',
            'logged_by': 'Mom',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        })

        # Call twice
        client.get('/api/mom-pills-status')
        client.get('/api/mom-pills-status')

        from app import get_feeds_from_excel
        yesterday_feeds = get_feeds_from_excel(yesterday)
        prenatal_missed = [f for f in yesterday_feeds if f['type'] == 'Pre-Natal (Mom)' and f.get('notes') == 'No']
        assert len(prenatal_missed) == 1
