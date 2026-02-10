"""
Test fixtures and configuration for Baby Feed Tracker tests.
"""

import pytest
import tempfile
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


# Seed data for tests
SEED_FEEDS = [
    {
        "type": "bottle",
        "side": None,
        "amount_oz": 3.0,
        "duration_min": None,
        "notes": "",
        "logged_by": "Dad",
        "timestamp": "2026-02-10T03:02:00"
    },
    {
        "type": "nurse",
        "side": "left",
        "amount_oz": None,
        "duration_min": 12,
        "notes": "",
        "logged_by": "Mom",
        "timestamp": "2026-02-10T01:15:00"
    },
    {
        "type": "pump",
        "side": "both",
        "amount_oz": 4.0,
        "duration_min": 15,
        "notes": "good output",
        "logged_by": "Mom",
        "timestamp": "2026-02-09T23:30:00"
    },
    {
        "type": "bottle",
        "side": None,
        "amount_oz": 2.5,
        "duration_min": None,
        "notes": "",
        "logged_by": "Dad",
        "timestamp": "2026-02-09T21:00:00"
    },
    {
        "type": "nurse",
        "side": "right",
        "amount_oz": None,
        "duration_min": 8,
        "notes": "fussy",
        "logged_by": "Mom",
        "timestamp": "2026-02-09T18:45:00"
    }
]


@pytest.fixture
def temp_xlsx(tmp_path):
    """
    Create a temporary Excel file for testing.
    Returns the file path and cleans up after the test.
    """
    temp_file = tmp_path / "test_feeds.xlsx"
    yield str(temp_file)
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def app(temp_xlsx):
    """
    Create a Flask test app instance configured to use a temp xlsx file.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['FEED_FILE'] = temp_xlsx

    # Initialize the Excel file
    from app import init_excel_file
    init_excel_file()

    yield flask_app

    # Cleanup: reset to default
    flask_app.config['FEED_FILE'] = 'feeds.xlsx'


@pytest.fixture
def client(app):
    """
    Flask test client for making HTTP requests.
    """
    return app.test_client()


@pytest.fixture
def seed_data(client):
    """
    Pre-populate the test database with known seed data.
    Returns the seed data for verification.
    """
    created_feeds = []

    for feed in SEED_FEEDS:
        response = client.post('/api/feeds', json=feed)
        assert response.status_code in [200, 201], f"Failed to seed data: {response.get_json()}"
        created_feeds.append(response.get_json())

    return created_feeds


@pytest.fixture
def today_str():
    """Return today's date as YYYY-MM-DD string."""
    return datetime.now().strftime("%Y-%m-%d")


@pytest.fixture
def yesterday_str():
    """Return yesterday's date as YYYY-MM-DD string."""
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")
