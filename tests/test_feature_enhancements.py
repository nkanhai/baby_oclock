import pytest
from app import format_feed_type, add_feed_to_excel, get_feeds_from_excel

def test_format_feed_type_bottle_types():
    """Test that bottle types are formatted correctly."""
    assert format_feed_type("bottle", "formula") == "Feed (Bottle - Formula)"
    assert format_feed_type("bottle", "milk") == "Feed (Bottle - Milk)"
    assert format_feed_type("bottle", None) == "Feed (Bottle)"
    assert format_feed_type("bottle", "") == "Feed (Bottle)"

def test_add_formula_feed(client, temp_xlsx):
    """Test logging a formula feed via API."""
    response = client.post("/api/feeds", json={
        "type": "bottle",
        "side": "formula",
        "amount_ml": 120,
        "logged_by": "Dad"
    })
    assert response.status_code == 201
    
    # Verify in Excel/Get
    feeds = get_feeds_from_excel()
    assert len(feeds) > 0
    latest = feeds[0]
    assert latest["type"] == "Feed (Bottle - Formula)"
    assert latest["amount_ml"] == 120

def test_add_milk_feed(client, temp_xlsx):
    """Test logging a milk feed via API."""
    response = client.post("/api/feeds", json={
        "type": "bottle",
        "side": "milk",
        "amount_ml": 90,
        "logged_by": "Mom"
    })
    assert response.status_code == 201
    
    # Verify in Excel/Get
    feeds = get_feeds_from_excel()
    assert len(feeds) > 0
    latest = feeds[0]
    assert latest["type"] == "Feed (Bottle - Milk)"
    assert latest["amount_ml"] == 90
