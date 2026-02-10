# Baby Feed Tracker — Test Spec

## Overview

Automated tests for the Baby Feed Tracker app. The app is a Flask + openpyxl backend with a single-page HTML/JS frontend. Tests should catch the most common and painful bugs — data loss, incorrect logging, API failures, and voice parsing errors.

---

## Test Stack

| Tool | Purpose |
|------|---------|
| `pytest` | Test runner and assertions |
| `pytest-flask` (or Flask's built-in test client) | HTTP endpoint testing |
| `openpyxl` | Verify Excel file contents directly |
| `threading` | Concurrent write tests |
| `tempfile` | Isolated test environments so tests don't touch real data |

### Install

Add to `requirements-test.txt`:
```
pytest
pytest-flask
```

---

## Project Structure

```
baby-tracker/
├── app.py
├── templates/
│   └── index.html
├── tests/
│   ├── conftest.py            # Fixtures: test client, temp xlsx, cleanup
│   ├── test_api_feeds.py      # CRUD endpoint tests
│   ├── test_excel.py          # Excel read/write integrity
│   ├── test_concurrent.py     # Simultaneous write safety
│   ├── test_edge_cases.py     # Boundary conditions and error handling
│   ├── test_voice_parser.py   # Voice input text parsing
│   └── test_stats.py          # Stats/summary endpoint
└── requirements-test.txt
```

---

## Fixtures (`conftest.py`)

### Core Fixtures Needed

1. **`temp_xlsx`** — Creates a fresh temporary xlsx file for each test. Tears it down after. Tests must NEVER touch the real `feeds.xlsx`.

2. **`app`** — Creates a Flask test app instance configured to use the temp xlsx file. This likely means the app needs a config variable or environment variable for the xlsx path (e.g., `FEED_FILE_PATH`). If the app doesn't support this yet, **add it** — it's a one-line change and essential for testability.

3. **`client`** — Flask test client from the app fixture. Used by all API tests.

4. **`seed_data`** — A fixture that pre-populates the temp xlsx with a known set of entries for read/query tests. Example seed data:

```python
SEED_FEEDS = [
    {"type": "bottle", "side": None, "amount_oz": 3.0, "duration_min": None, "notes": "", "logged_by": "Dad", "timestamp": "2026-02-10T03:02:00"},
    {"type": "nurse", "side": "left", "amount_oz": None, "duration_min": 12, "notes": "", "logged_by": "Mom", "timestamp": "2026-02-10T01:15:00"},
    {"type": "pump", "side": "both", "amount_oz": 4.0, "duration_min": 15, "notes": "good output", "logged_by": "Mom", "timestamp": "2026-02-09T23:30:00"},
    {"type": "bottle", "side": None, "amount_oz": 2.5, "duration_min": None, "notes": "", "logged_by": "Dad", "timestamp": "2026-02-09T21:00:00"},
    {"type": "nurse", "side": "right", "amount_oz": None, "duration_min": 8, "notes": "fussy", "logged_by": "Mom", "timestamp": "2026-02-09T18:45:00"},
]
```

---

## Test Suites

### 1. `test_api_feeds.py` — CRUD Operations

These are the highest-priority tests. If the API is broken, nothing works.

#### POST /api/feeds (Create)

| Test | Input | Expected |
|------|-------|----------|
| Log a bottle feed with amount | `{"type": "bottle", "amount_oz": 3.0}` | 201, entry returned with correct type and amount |
| Log a nursing session with side and duration | `{"type": "nurse", "side": "left", "duration_min": 12}` | 201, type = "Nurse (Left)", duration = 12 |
| Log a pump with side and amount | `{"type": "pump", "side": "both", "amount_oz": 4.0}` | 201, type = "Pump (Both)" |
| Log with no timestamp (server uses now) | `{"type": "bottle", "amount_oz": 2.0}` (no timestamp field) | 201, timestamp is approximately now (within 5 seconds) |
| Log with explicit timestamp | `{"type": "bottle", "amount_oz": 2.0, "timestamp": "2026-02-10T03:00:00"}` | 201, timestamp matches what was sent |
| Log with logged_by field | `{"type": "bottle", "amount_oz": 3.0, "logged_by": "Dad"}` | 201, logged_by = "Dad" |
| Log with notes | `{"type": "nurse", "side": "right", "notes": "baby was fussy"}` | 201, notes preserved |
| Log with amount_oz = 0 | `{"type": "bottle", "amount_oz": 0}` | 201, amount stored as 0 (valid — maybe a failed attempt) |
| Log nurse with no amount (common case) | `{"type": "nurse", "side": "left"}` | 201, amount_oz is null/blank |
| Missing type field | `{"amount_oz": 3.0}` | 400, error message |
| Invalid type | `{"type": "snack"}` | 400, error message |
| Invalid side value | `{"type": "nurse", "side": "middle"}` | 400, error message |
| Negative amount | `{"type": "bottle", "amount_oz": -2}` | 400, error message |
| Very large amount (sanity check) | `{"type": "bottle", "amount_oz": 99}` | 201 or 400 — decide on a reasonable max and test the boundary |

#### GET /api/feeds (Read)

| Test | Setup | Expected |
|------|-------|----------|
| Get today's feeds (default) | Seed data with today's entries | Returns only today's entries |
| Get feeds for specific date | Seed with entries across multiple dates | `?date=2026-02-09` returns only that date's entries |
| Empty day | No entries for requested date | Returns empty list, last_feed_minutes_ago = null |
| Feeds are in reverse chronological order | Seed with multiple entries | Most recent first |
| Response includes last_feed_minutes_ago | Seed with a known entry | Value is approximately correct |
| Response includes total_oz_today | Seed with known amounts | Sum is correct |
| Response includes total_feeds_today | Seed data | Count is correct |
| Invalid date format | `?date=not-a-date` | 400 or falls back to today gracefully |

#### DELETE /api/feeds/<id> (Delete)

| Test | Setup | Expected |
|------|-------|----------|
| Delete existing entry | Seed, delete by ID | 200, entry no longer appears in GET |
| Delete non-existent entry | Delete ID 9999 | 404 |
| Delete and verify xlsx row removed | Seed, delete, read xlsx directly | Row is gone from the file |
| Delete doesn't affect other entries | Seed 3 entries, delete middle one | Other 2 still present and correct |

#### PUT /api/feeds/<id> (Update)

| Test | Setup | Expected |
|------|-------|----------|
| Update amount | Seed, PUT with new amount | 200, amount updated in GET response |
| Update type | Change bottle to nurse | 200, type updated |
| Update notes | Add a note to an entry | 200, notes updated |
| Update non-existent entry | PUT to ID 9999 | 404 |
| Update with invalid data | PUT with negative amount | 400 |
| Verify xlsx reflects update | Update, then read xlsx directly | Cell values match |

---

### 2. `test_excel.py` — Data Integrity

These tests read the xlsx file directly with openpyxl to verify the backend is writing correctly.

| Test | What to verify |
|------|---------------|
| File auto-creation | Delete the xlsx, make a request, verify file is created with correct headers |
| Header row is correct | Open xlsx, check row 1 matches expected column names exactly |
| Entry matches API response | POST via API, open xlsx, verify the last row matches what was returned |
| Column types are correct | Date column has date-like strings, Amount column has numbers or blanks, Timestamp is ISO format |
| Multiple entries append correctly | POST 5 entries, verify xlsx has 5 data rows (plus header) |
| Special characters in notes | POST with notes containing emojis, quotes, newlines | Characters preserved in xlsx |
| Amount precision | POST amount_oz=2.5, verify xlsx cell is 2.5 (not rounded or truncated) |
| File is valid xlsx after many writes | POST 50 entries in a loop, then open the file with openpyxl and verify it's not corrupted |
| File survives server restart | POST entries, restart the Flask app, GET feeds — data is still there |

---

### 3. `test_concurrent.py` — Simultaneous Write Safety

This is critical — both parents will be logging at the same time.

| Test | Method | Expected |
|------|--------|----------|
| Two simultaneous POSTs | Use `threading.Thread` to fire 2 POSTs at the exact same time | Both entries are saved, no data loss, no corruption |
| Five rapid-fire POSTs | 5 threads, all POST at once | All 5 entries present in xlsx |
| Read during write | One thread POSTs while another GETs | GET returns valid response (may or may not include the in-flight POST, but must not error) |
| Ten sequential rapid POSTs | Loop 10 POSTs with no delay | All 10 saved correctly |
| Verify no duplicate entries | POST once, verify only one row added | Exactly one new row |

Implementation approach:
```python
import threading

def test_concurrent_writes(client):
    results = []
    
    def post_feed(amount):
        resp = client.post('/api/feeds', json={
            "type": "bottle",
            "amount_oz": amount,
            "logged_by": "Mom" if amount % 2 == 0 else "Dad"
        })
        results.append(resp.status_code)
    
    threads = [threading.Thread(target=post_feed, args=(i,)) for i in range(1, 6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert all(code == 201 for code in results)
    
    # Verify all entries exist in xlsx
    resp = client.get('/api/feeds')
    feeds = resp.get_json()["feeds"]
    assert len(feeds) == 5
```

---

### 4. `test_edge_cases.py` — Boundary Conditions

| Test | Scenario | Expected |
|------|----------|----------|
| Midnight rollover | Log entry at 11:59 PM, another at 12:01 AM. Query both dates. | Each appears on the correct date |
| Empty xlsx (first ever entry) | Fresh file, POST one entry | Works, entry is saved |
| Very long notes field | Notes = 1000 characters | Saved and retrieved correctly, no truncation |
| Unicode in notes | Notes = "宝宝吃了 🍼" | Saved and retrieved correctly |
| Amount with many decimals | amount_oz = 2.333333 | Stored reasonably (round to 1-2 decimal places or store as-is) |
| POST with extra unknown fields | `{"type": "bottle", "amount_oz": 3, "foo": "bar"}` | Ignores unknown fields, succeeds |
| POST with empty body | `{}` | 400 |
| POST with null values | `{"type": "bottle", "amount_oz": null}` | 201, amount is blank/null |
| GET with future date | `?date=2030-01-01` | Empty list, no error |
| GET with past date | `?date=2020-01-01` | Empty list, no error |
| Delete last remaining entry | Seed 1 entry, delete it | Success, GET returns empty list |
| Rapid delete + create | Delete entry, immediately create new one | Both operations succeed |
| Server handles malformed JSON | POST with invalid JSON body | 400, not 500 |
| Content-Type header missing | POST without application/json header | 400 or handles gracefully |

---

### 5. `test_voice_parser.py` — Voice Input Parsing

If the voice parsing logic is in Python (server-side), test it directly. If it's purely in JavaScript (client-side), create a parallel Python implementation for testing, or document these as manual test cases.

**The parser function should accept a raw transcript string and return a structured object.**

#### Bottle Feed Phrases

| Input transcript | Expected output |
|-----------------|-----------------|
| `"bottle 3 ounces"` | type=bottle, amount=3.0 |
| `"fed three ounces"` | type=bottle, amount=3.0 |
| `"3 ounce bottle"` | type=bottle, amount=3.0 |
| `"bottle feed 2.5 oz"` | type=bottle, amount=2.5 |
| `"fed baby 4 ounces"` | type=bottle, amount=4.0 |
| `"bottle"` (no amount) | type=bottle, amount=None (should prompt for amount) |
| `"fed 2 and a half ounces"` | type=bottle, amount=2.5 |

#### Nursing Phrases

| Input transcript | Expected output |
|-----------------|-----------------|
| `"nurse left"` | type=nurse, side=left |
| `"nursed on the left side"` | type=nurse, side=left |
| `"breastfed right 10 minutes"` | type=nurse, side=right, duration=10 |
| `"nursing both sides"` | type=nurse, side=both |
| `"left side 15 minutes"` | type=nurse, side=left, duration=15 |
| `"nursed"` (no side) | type=nurse, side=None (should prompt for side) |

#### Pump Phrases

| Input transcript | Expected output |
|-----------------|-----------------|
| `"pumped 4 ounces both"` | type=pump, side=both, amount=4.0 |
| `"pump left 2 ounces"` | type=pump, side=left, amount=2.0 |
| `"pumped right side 3 oz"` | type=pump, side=right, amount=3.0 |
| `"pump both sides 5 ounces"` | type=pump, side=both, amount=5.0 |
| `"pumped"` (no details) | type=pump, side=None, amount=None |

#### Ambiguous / Edge Cases

| Input transcript | Expected behavior |
|-----------------|------------------|
| `""` (empty string) | Returns None or error — nothing to parse |
| `"hello"` (no feed keywords) | Returns None or unrecognized — prompt user to try again |
| `"3 ounces"` (no type keyword) | Best guess: type=bottle (most common), or return ambiguous |
| `"left 10 minutes"` (no type) | Best guess: type=nurse, or return ambiguous |
| `"bottle left 3 ounces"` (bottle with side?) | type=bottle, amount=3.0 (ignore side for bottles) |
| `"two"` (just a number) | Ambiguous, prompt for more info |
| `"nursed three ounces left"` | type=nurse, side=left, amount=3.0 (unusual but valid — pumped milk in bottle while nursing?) |

#### Number Word Conversion

| Input | Expected number |
|-------|----------------|
| `"one"` | 1 |
| `"two"` | 2 |
| `"three"` | 3 |
| `"four"` | 4 |
| `"five"` | 5 |
| `"six"` | 6 |
| `"seven"` | 7 |
| `"eight"` | 8 |
| `"nine"` | 9 |
| `"ten"` | 10 |
| `"half"` or `"a half"` | 0.5 |
| `"two and a half"` | 2.5 |
| `"one and a half"` | 1.5 |

---

### 6. `test_stats.py` — Summary Endpoint

| Test | Setup | Expected |
|------|-------|----------|
| Total oz today (bottles only) | Seed: 3oz + 2.5oz bottles today | total_oz = 5.5 |
| Total oz today (bottles + pumps) | Seed: 3oz bottle + 4oz pump | total_oz = 7.0 (or separate bottle_oz and pump_oz) |
| Total feeds today | Seed: 3 bottle + 2 nurse | total_feeds = 5 |
| Nursing session count | Seed: 2 nurse sessions | total_nursing_sessions = 2 |
| Average feed interval | Seed: feeds at 1:00, 3:00, 5:00 | avg_interval = 120 min |
| No feeds today | Empty seed | All values = 0 or null |
| Single feed today | One entry | Interval = null (can't calculate with 1 data point) |
| Stats only count today | Seed: 3 today + 2 yesterday | Stats reflect only today's 3 |

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific suite
pytest tests/test_api_feeds.py -v

# Run with print output (for debugging)
pytest tests/ -v -s

# Run just the concurrent tests
pytest tests/test_concurrent.py -v
```

---

## Implementation Notes for Claude Code

1. **Make the xlsx path configurable.** The app MUST accept the xlsx file path via a config variable, environment variable, or constructor argument. Without this, tests can't use isolated temp files. Something like:
   ```python
   app.config['FEED_FILE'] = os.environ.get('FEED_FILE', 'feeds.xlsx')
   ```

2. **If voice parsing is in JavaScript**, either:
   - (Preferred) Extract the parsing logic into a pure function that can be tested with a simple Node.js test script or inline `<script>` test page.
   - Or duplicate the parsing logic in Python for server-side testing.

3. **Test isolation is critical.** Every test should start with a clean xlsx file. Use `tmp_path` (pytest built-in) or `tempfile.mkdtemp()`. Never share state between tests.

4. **Don't mock openpyxl.** The whole point is to verify real Excel file integrity. Write to real temp files and read them back.

5. **Keep tests fast.** No `time.sleep()` except in concurrent tests where a brief sleep is needed to simulate timing. Total test suite should run in under 10 seconds.

6. **If any test requires changes to `app.py`** (like making the file path configurable), make those changes. Testability improvements to the main code are in scope.