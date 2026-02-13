# Claude Agent Context - Baby Feed Tracker

## Project Overview

This is a **mobile-first web application** for tracking baby feeding sessions (bottle, nursing, pump) and diaper changes (pee, poop, both). Built for **sleep-deprived parents** using their phones at 3am, so simplicity and reliability are paramount.

**Target Users:** Two parents (Mom & Dad) simultaneously logging feeds on their phones
**Critical Requirement:** No data loss when both parents log feeds at the exact same time
**Baby's Name:** Esmé (used in UI)

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend** | Flask (Python 3.8+) | Simple, minimal dependencies |
| **Data Storage** | Excel (.xlsx via openpyxl) | Parents can open/view anytime in Excel/Sheets |
| **Frontend** | Single HTML file with inline CSS/JS | No build step, works offline after first load |
| **Voice Input** | Browser Web Speech API | Built into Safari/Chrome, no API keys needed |
| **Charts** | Chart.js (v4 CDN) | Lightweight, mobile-friendly canvas rendering |
| **Server** | Development server on port 8080 | Runs on local network, no internet required |

**Key Design Decision:** Everything is intentionally simple and self-contained. No databases, no frameworks, no cloud services.

---

## Architecture

### File Structure

```
Esme_oClock/
├── app.py                          # Flask backend - ALL server logic
├── templates/
│   └── index.html                  # Single-page UI (HTML + CSS + JS all inline)
├── static/
│   └── manifest.json               # PWA manifest for "Add to Home Screen"
├── feeds.xlsx                      # Data file (auto-created, gitignored)
├── voice_parser.py                 # Python voice parser (mirrors JS frontend logic)
├── venv/                           # Virtual environment
├── requirements.txt                # flask, openpyxl
├── requirements-test.txt           # pytest, pytest-flask
├── tests/                          # 128+ automated tests
│   ├── conftest.py                 # Test fixtures
│   ├── test_api_feeds.py           # CRUD endpoint tests
│   ├── test_diaper.py              # Diaper tracking tests
│   ├── test_vitamin.py             # Vitamin D tests
│   ├── test_excel.py               # Data integrity tests
│   ├── test_concurrent.py          # Thread safety tests
│   ├── test_edge_cases.py          # Boundary condition tests
│   ├── test_voice_parser.py        # Voice parsing tests
│   └── test_stats.py               # Stats endpoint tests
├── start.sh                        # One-command launcher
└── [documentation files]
```

---

## Core Functionality

### Data Flow

1. **User taps button** on phone → JavaScript in `index.html`
2. **Frontend sends POST** to `/api/feeds` with JSON payload
3. **Flask endpoint** receives request → calls `add_feed_to_excel()`
4. **Excel write** happens with thread lock (prevents corruption)
5. **Response sent** back to frontend
6. **Frontend updates UI** with new entry and stats

### Excel File Schema

**File:** `feeds.xlsx`
**Sheet:** "Feed Log"

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Date | String (YYYY-MM-DD) | Date of feed | "2026-02-10" |
| Time | String (HH:MM AM/PM) | Time in 12-hour format | "3:02 AM" |
| Type | String | Formatted feed type | "Feed (Bottle)", "Nurse (Left)", "Pump (Both)", "Diaper (Pee)" |
| Amount (oz) | Float or blank | Quantity in ounces | 3.5 |
| Duration (min) | Integer or blank | Duration in minutes | 12 |
| Notes | String | Free text | "baby was fussy" |
| Logged By | String | Who logged it | "Mom" or "Dad" |
| Timestamp | String (ISO 8601) | Full timestamp for sorting | "2026-02-10T03:02:00" |

**Row 1:** Headers (bold, centered)
**Row 2+:** Data entries (appended to bottom)

---

## Critical Implementation Details

### 1. Thread Safety (CRITICAL!)

**Problem:** Both parents can log feeds simultaneously from different phones.

**Solution:** Thread lock in `app.py`:

```python
file_lock = threading.Lock()

def add_feed_to_excel(feed_data):
    with file_lock:
        # Excel write operations here
```

**Why it matters:** Without this, concurrent writes can corrupt the Excel file. This is tested extensively in `tests/test_concurrent.py`.

**Gotcha:** The lock is in-memory, so it only works for a single server process. Don't run multiple instances of the server on different ports.

---

### 2. Configurable Excel File Path (for Testing)

**Implementation:**

```python
app.config['FEED_FILE'] = os.environ.get('FEED_FILE', 'feeds.xlsx')

def get_excel_file():
    """Get the current Excel file path from app config."""
    return app.config.get('FEED_FILE', 'feeds.xlsx')
```

**Why:** Tests need to use temporary files. Every function that touches the Excel file calls `get_excel_file()` instead of using a hardcoded path.

**Gotcha:** Originally `EXCEL_FILE` was a module-level constant. This was changed to support testing. If you see any remaining references to a bare `EXCEL_FILE` variable, they should be `get_excel_file()`.

---

### 3. Timezone-Aware vs Naive Datetime Bug (FIXED)

**The Bug:** Excel stores ISO 8601 timestamps as strings like `"2026-02-10T03:02:00"`. When parsing with `datetime.fromisoformat()`, these can be timezone-aware or naive depending on format. `datetime.now()` returns a naive datetime. Subtracting them causes:

```
TypeError: can't subtract offset-naive and offset-aware datetimes
```

**The Fix (in `app.py` around line 100 & 200):** Incoming UTC timestamps from the frontend (`new Date().toISOString()`) are converted to the server's local time using `.astimezone()`. Mixed naive/aware timestamps in `get_stats` are handled by stripping timezone info before comparison.

**Why it happened:** Some timestamps were saved with timezone info, others without. This defensively handles both.

**Gotcha:** If you migrate to SQLite, use timezone-naive datetimes throughout OR make everything timezone-aware consistently.

---

### 4. Feed Type Formatting

**User Input → Excel Storage:**

```python
def format_feed_type(feed_type, side=None):
    if feed_type == "bottle":
        return "Feed (Bottle)"
    elif feed_type == "nurse":
        if side == "left":
            return "Nurse (Left)"
        elif side == "right":
            return "Nurse (Right)"
        else:
            return "Nurse (Both)"
    elif feed_type == "pump":
        if side == "left":
            return "Pump (Left)"
        # ... etc
    elif feed_type == "diaper":
        if side == "pee":
            return "Diaper (Pee)"
        elif side == "poop":
            return "Diaper (Poop)"
        elif side == "both":
            return "Diaper (Both)"
        else:
            return "Diaper"
```

**API accepts:** `{"type": "bottle", "side": null}` or `{"type": "diaper", "side": "pee"}`
**Excel stores:** `"Feed (Bottle)"` or `"Diaper (Pee)"`

**Why:** Makes Excel file human-readable. Parents can open it and immediately understand what each entry means.

---

### 5. Row IDs (Important!)

**How IDs work:**
- Feed ID = Excel row number - 1 (to account for header row)
- Row 2 in Excel = Feed ID 1
- Row 3 in Excel = Feed ID 2

**Critical Gotcha:** When you delete a row, subsequent rows shift up and their IDs change.

**Example:**
```
Before delete:
  Row 2 (ID 1): 3 oz bottle
  Row 3 (ID 2): Nurse left
  Row 4 (ID 3): 2 oz bottle

Delete ID 2 (row 3):

After delete:
  Row 2 (ID 1): 3 oz bottle
  Row 3 (ID 2): 2 oz bottle  ← This WAS ID 3!
```

**Why this matters:** Tests originally checked if IDs were preserved after delete, but they aren't. Tests were updated to verify by timestamp instead of ID.

**If you add a real database:** Use auto-incrementing integer primary keys that don't change.

---

### 6. Port Configuration

**Current:** Port 8080
**Why not 5000?** Port 5000 conflicts with macOS AirPlay Receiver service.

**Implementation (app.py bottom):**

```python
PORT = 8080  # Using 8080 to avoid firewall/AirPlay conflicts on port 5000
app.run(host="0.0.0.0", port=PORT, debug=False)
```

**Gotcha:** The startup message was originally hardcoded to 5000. It's now a variable. If you see port mismatches in startup messages, check that `PORT` is used consistently.

---

### 7. Voice Input (Client-Side Only)

**JavaScript Implementation (in `index.html`):**

```javascript
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = true;
recognition.lang = 'en-US';
```

**Parser Logic:**
1. Listens to speech
2. Converts to text via browser API
3. Parses text with regex/keyword matching
4. Shows parsed result to user
5. User confirms
6. Sends to API as normal feed entry

**Python Mirror:** `voice_parser.py` contains the same parsing logic in Python for testing purposes.

**Browser Support:**
- ✅ Safari (iOS)
- ✅ Chrome (Android, Desktop)
- ❌ Firefox (no support)
- ❌ Other browsers

**Gotcha - Keyword Order Matters:**

```python
# WRONG - "breastfed" contains "fed" so it matches bottle first
if 'fed' in lower:
    type = 'bottle'
elif 'breastfed' in lower:
    type = 'nurse'

# CORRECT - Check specific terms first
if 'breastfed' in lower or 'nurse' in lower:
    type = 'nurse'
elif 'fed' in lower:
    type = 'bottle'
```

This bug was fixed in commit that reordered keyword checks.

---

### 8. Tumbler vs Input Conflict Resolution
(Implemented Feb 2026)

**Problem:** Users can select amount via Tumbler wheel OR type in "Custom Amount" input. If they do both, which one wins?
**Solution:** "Last Interaction Wins" logic.
- If user scrolls/clicks Tumbler → Custom Input is cleared.
- If user types in Custom Input → It overrides the Tumbler (standard behavior).
- **Implementation:** `createTumbler()` attaches scroll/click listeners that clear the linked input field.

### 9. Manual Time Entry Logic
(Implemented Feb 2026)

**Feature:** Users can edit the time of a feed in the "More options" section.
**New Log:** Defaults to current time ("now").
**Editing Log:** Pre-fills with the *original* time of the log.
**Gotcha (Fixed Bug):** Previously, opening the edit modal would reset the time to "now" because `openModal` didn't distinguish between new and edit modes.
**Fix:** `openModal` now checks `if (editingFeedId === null)` before setting the time to "now".

### 10. Client-Side Logic Updates (Feb 2026)

**Next Feed Timer:**
- Calculated entirely in client (JS).
- Logic: Last non-diaper feed time + 3 hours.
- Updates every time `loadFeeds()` runs.
- **Visuals:** Shows "Next feed in..." or red "Overdue by..." text.

**Daily Goal Progress:**
- Tracks "Today's" total milk intake vs 500ml goal.
- **Visuals:** Progress bar with gradient (Blue → Purple).
- **Thresholds:**
  - < 400ml: "Keep going"
  - 400-449ml: "Minimum met"
  - 450-499ml: "Almost there" (Purple zone)
  - 500ml+: "Goal Met"

**Undo Logic Fix:**
- The "Undo" button (in toast) is **only** shown for newly created feeds (`POST`).
- It is hidden for edits (`PUT`) to avoid confusion/bugs where undo wouldn't revert edits.

### 11. Charts Implementation (Feb 2026)

**Architecture:**
- **Client-Side Aggregation:** `loadChartData(days)` fetches raw feed JSON from `/api/feeds` and groups/sums data in JavaScript.
- **No New Endpoints:** Reuses existing API with `?limit_days=N`.
- **Rendering:** 3 separate `<canvas>` elements using Chart.js v4.

**Chart Types:**
1. **Milk Intake:** Bar chart + Goal Line (500ml).
2. **Diapers:** Stacked bar (Pee/Poop/Both).
3. **Timeline:** Scatter plot.
   - **Y-Axis Logic:** Linear scale 0-24. 12am=0, 12pm=12, 11:59pm=23.9. Formatted via callback.
   - **X-Axis:** Categorical dates.

**State:**
- Charts are re-rendered on tab switch or range change (7/14/30 days).
- Uses `destroy()` on chart instances before re-creating to prevent canvas reuse errors.

---

## API Endpoints

### GET /
Returns the HTML UI (`templates/index.html`)

### GET /api/feeds
**Query Params:**
- `date` (optional): YYYY-MM-DD format, defaults to today (if `limit_days` not strictly provided)
- `limit_days` (optional): Integer (e.g. 7). If provided, returns feeds for the last N days.

**Returns:**
```json
{
  "feeds": [
    {
      "id": 1,
      "date": "2026-02-10",
      "time": "3:02 AM",
      "type": "Feed (Bottle)",
      "amount_ml": 90,
      "duration_min": null,
      "notes": "",
      "logged_by": "Dad",
      "timestamp": "2026-02-10T03:02:00"
    }
  ],
  "last_feed_minutes_ago": 47,
  "last_feed_summary": "Bottle — 90 ml at 3:02 AM",
  "total_ml_today": 370,
  "total_feeds_today": 5
}
```

**Gotcha:** Feeds are sorted in reverse chronological order (newest first).

### POST /api/feeds
**Request Body:**
```json
{
  "type": "bottle",        // "bottle", "nurse", "pump", or "diaper"
  "side": null,            // "left", "right", "both" (nurse/pump) or "pee", "poop", "both" (diaper)
  "amount_ml": 90,         // integer or null
  "duration_min": 10,      // integer or null
  "notes": "",             // string
  "logged_by": "Mom",      // string
  "timestamp": "2026-02-10T03:02:00"  // ISO 8601, optional (defaults to now)
}
```

**Returns (201 Created):**
```json
{
  "success": true,
  "id": 5,
  "message": "Feed logged successfully"
}
```

**Gotcha:** Originally returned 200 instead of 201. Fixed to return proper 201 status code.

### DELETE /api/feeds/<id>
Deletes feed entry by ID (row number - 1).

**Returns (200):**
```json
{
  "success": true,
  "message": "Feed deleted"
}
```

**Returns (404):** If ID doesn't exist

### PUT /api/feeds/<id>
Updates feed entry by ID.

**Request Body:** Same as POST

**Returns (200):** On success
**Returns (404):** If ID doesn't exist

### GET /api/stats
**Returns:**
```json
{
  "today": {
    "total_ml": 350.0,
    "total_feeds": 5,
    "total_nursing_sessions": 2,
    "total_pump_ml": 120.0,
    "avg_feed_interval_min": 150,
    "total_diaper_changes": 3
  }
}
```

---

### Diaper Tracking

**Added:** February 2026

The app tracks diaper changes using the same infrastructure as feed tracking.

**Types:**
- Pee only (`side: "pee"`)
- Poop only (`side: "poop"`)
- Both (`side: "both"`)

**Excel Format:**
- Stored as: `"Diaper (Pee)"`, `"Diaper (Poop)"`, `"Diaper (Both)"`
- Uses the "side" parameter (repurposed from nurse/pump functionality)

**API:**
```json
POST /api/feeds
{
    "type": "diaper",
    "side": "pee",
    "notes": "Optional notes",
    "logged_by": "Mom"
}
```

**Stats:**
- `total_diaper_changes` - Count of diaper changes today
- `last_diaper_minutes_ago` - Minutes since last diaper change
- `total_diaper_changes` - Count of diaper changes today
- `last_diaper_minutes_ago` - Minutes since last diaper change
- `last_diaper_summary` - Description of last diaper change

### Vitamin D Reminder

**Added:** February 2026

**Feature:** Daily tappable banner reminding parents to give Vitamin D drops.

**Logic:**
- Banner appears at midnight for the new day.
- Tapping it logs a "Vitamin D" entry.
- **Lazy Auto-Log:** If a user opens the app today, and *yesterday* had feeds but NO vitamin log, the system automatically logs a "Missed" entry for yesterday.

**API:**
- `GET /api/vitamin-status` - Checks if vitamin was given today.
- `POST /api/vitamin` - Logs administration.

**Stats:**
- Vitamin D entries are **excluded** from:
  - Last feed timer
  - Total ml today
  - Feed counts
  - Diaper stats

### Feature Flags

**VOICE_INPUT_ENABLED** (default: false)
- Controls visibility of voice input button and modal
- Set to `true` in JavaScript to enable voice functionality
- Location: `templates/index.html`, top of `<script>` section

```javascript
const FEATURE_FLAGS = {
    VOICE_INPUT_ENABLED: false  // Set to true to enable voice functionality
};
```

---

## Frontend Implementation (index.html)

### Key Design Principles

1. **Single HTML file** - No external CSS or JS files
2. **Inline everything** - Works offline after first load
3. **Mobile-first** - Designed for phone screens
4. **Big buttons** - Minimum 60px tall, ideally 80px+
5. **Dark mode** - Default (easier on eyes at night)
6. **No scrolling** - Main actions visible without scrolling

### State Management

**Client-side state:**
- `currentWho`: "Mom" or "Dad" (who's logging)
- `lastCreatedFeedId`: For undo functionality
- `pumpSelectedSide`: Tracks pump side selection
- `voiceParsedData`: Holds parsed voice input

**State is ephemeral** - No localStorage, no persistence. When you refresh, it resets.

**Why:** Simplicity. The source of truth is the Excel file on the server.

### Auto-Refresh

**Every 30 seconds:** JavaScript polls `/api/feeds` to update "last feed" timer

```javascript
setInterval(loadFeeds, 30000);  // 30 seconds
```

**Why:** Shows "5 min ago" → "6 min ago" without manual refresh.

**Gotcha:** If server is down, this silently fails. No error shown to user.

### Modal Flow Example (Bottle Feed)

1. User taps "🍼 Bottle"
2. Modal opens (`openModal(bottleModal)`)
3. User selects "90 ml"
4. `logFeed('bottle', null, 90)` called
5. POST to `/api/feeds`
6. Modal closes (`closeModal(bottleModal)`)
7. Toast shows "✓ Bottle — 90 ml logged"
8. `loadFeeds()` refreshes the feed list
9. Stats update
10. **Display**: Feeds are grouped by date (Today, Yesterday, etc.) in the UI.

**Gotcha:** If the POST fails (network error, server down), the modal still closes and toast still shows success. There's minimal error handling.

**TODO for production:** Add proper error handling and retry logic.

---

## Testing

### Test Structure

**Total Tests:** 117+
**Execution Time:** ~1.3 seconds
**All passing:** ✅

### Test Fixtures (`tests/conftest.py`)

```python
@pytest.fixture
def temp_xlsx(tmp_path):
    """Creates temporary Excel file for each test"""

@pytest.fixture
def app(temp_xlsx):
    """Flask test app configured to use temp file"""

@pytest.fixture
def client(app):
    """Flask test client for HTTP requests"""

@pytest.fixture
def seed_data(client):
    """Pre-populates DB with 5 known feeds"""
```

**Key Insight:** Every test gets a fresh Excel file in a temp directory. Tests never touch the real `feeds.xlsx`.

### Important Test Gotchas

**1. Feed IDs change after delete** (see "Row IDs" section above)
- Tests use timestamps for verification, not IDs

**2. Timezone handling** (see "Timezone-Aware vs Naive" section)
- Tests may create timestamps without timezone info
- App defensively strips timezone before comparisons

**3. Voice parser is tested separately**
- `voice_parser.py` is a Python implementation
- Frontend JavaScript has the same logic but isn't directly tested
- If you change JS voice parsing, update Python version and re-run tests

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific suite
pytest tests/test_concurrent.py -v

# With output (debugging)
pytest tests/ -v -s

# Just one test
pytest tests/test_api_feeds.py::TestCreateFeed::test_log_bottle_feed_with_amount -v
```

---

## Common Development Tasks

### Adding a New Feed Type

**Example:** Add "Diaper Change" tracking

1. **Update Frontend** (`templates/index.html`):
   - Add new button in action grid
   - Create modal for diaper change options
   - Add event handlers

2. **Update Backend** (`app.py`):
   - Update `format_feed_type()` to handle new type
   - No other changes needed (API is generic)

3. **Update Voice Parser** (`voice_parser.py`):
   - Add keywords for voice recognition

4. **Update Tests**:
   - Add test cases for new type
   - Update seed data if needed

5. **Update Excel**:
   - Type column already supports any string
   - No schema changes needed

**Example (Diaper Tracking - Implemented Feb 2026):**
Diaper tracking was added by reusing the `side` parameter for pee/poop/both.
The `format_feed_type()` function maps `{"type": "diaper", "side": "pee"}` → `"Diaper (Pee)"`.
Frontend uses the same modal pattern with type-selection buttons that call `logFeed('diaper', type)`.

### Migrating to SQLite

**Current Pain Points with Excel:**
- File locking is primitive
- Can't do complex queries
- No foreign keys or relationships
- Large files (1000+ entries) get slow

**Migration Steps:**

1. **Create schema:**
```sql
CREATE TABLE feeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    type TEXT NOT NULL,
    amount_ml INTEGER,
    duration_min INTEGER,
    notes TEXT,
    logged_by TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX idx_date ON feeds(date);
CREATE INDEX idx_timestamp ON feeds(timestamp);
```

2. **Replace Excel functions:**
- `init_excel_file()` → `init_database()`
- `add_feed_to_excel()` → `add_feed_to_db()`
- `get_feeds_from_excel()` → `get_feeds_from_db()`
- etc.

3. **Keep thread lock** (SQLite can handle concurrent reads, but writes still need serialization)

4. **Add export function:**
```python
def export_to_excel():
    """Export SQLite data to Excel for parent viewing"""
```

5. **Update tests:**
- Update fixtures to use SQLite
- Most tests should pass with minimal changes

**Gotcha:** SQLite datetimes should be stored as TEXT in ISO 8601 format, just like current Excel timestamps.

### Adding Google Sheets Export

**Approach:** Use Google Sheets API

**Requirements:**
- Service account credentials (JSON file)
- `gspread` library
- Google Sheet ID from parents

**Implementation:**
```python
def export_to_google_sheets():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key('SHEET_ID').sheet1

    # Get all feeds
    feeds = get_all_feeds()

    # Clear and write
    sheet.clear()
    sheet.append_row(['Date', 'Time', 'Type', ...])  # Headers
    for feed in feeds:
        sheet.append_row([feed['date'], feed['time'], ...])
```

**Gotcha:** Rate limits! Google Sheets API has quotas. Don't export on every feed entry. Use a scheduled task (cron) or manual button.

---

## Deployment Considerations

### Current State (Development)
- Flask development server
- Runs on local network only
- No HTTPS
- No authentication
- Port 8080

### For Production Use

**Option 1: Keep It Local (Recommended for Home Use)**
- Keep running on local network
- Parents access via WiFi only
- Set up server to auto-start on boot
- Use a dedicated computer (old laptop, Raspberry Pi)

**Option 2: Cloud Deployment**
- Would need authentication (don't want data public)
- Use Gunicorn instead of Flask dev server
- Set up HTTPS with SSL certificate
- Consider using proper database (PostgreSQL)
- **Not recommended** - overkill for 2 users

### Auto-Start on macOS

**Create LaunchAgent:** `~/Library/LaunchAgents/com.babytracker.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.babytracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/Esme_oClock/start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/Esme_oClock</string>
</dict>
</plist>
```

Load it: `launchctl load ~/Library/LaunchAgents/com.babytracker.plist`

---

## Known Issues & Limitations

### 1. No Error Handling in Frontend
**Issue:** If API request fails, frontend shows success toast anyway
**Impact:** Low (server is local and reliable)
**Fix:** Add error handling to all `fetch()` calls

### 2. No Input Validation
**Issue:** Can enter negative amounts, huge numbers, etc.
**Impact:** Low (trusted users, garbage in = garbage out)
**Fix:** Add validation in backend and frontend

### 3. No Data Backup
**Issue:** If `feeds.xlsx` is deleted, all data is lost
**Impact:** HIGH (could lose weeks of data)
**Fix:** Implement automatic daily backup to Dropbox/iCloud

### 4. Single Point of Failure
**Issue:** If server computer dies, app is unavailable
**Impact:** Medium (parents can track on paper temporarily)
**Fix:** Use cloud hosting (but loses simplicity)

### 5. No Multi-Device Sync
**Issue:** Data only exists on one computer
**Impact:** Low (both parents use same server)
**Fix:** Google Sheets export gives backup + viewability

### 6. Voice Recognition Accuracy
**Issue:** Misinterprets speech sometimes
**Impact:** Low (users confirm before saving)
**Fix:** None - it's a browser API limitation

### 7. Network Dependency
**Issue:** Requires both phone and server on same WiFi
**Impact:** Medium (what if WiFi is down?)
**Fix:** Could add offline mode with localStorage + sync

---

## Performance Characteristics

### Current Performance
- **API response time:** <50ms for most requests
- **Excel file size:** ~5KB for 50 entries, ~50KB for 500 entries
- **Page load:** <1 second on local network
- **Max tested:** 1000+ entries in Excel file

### Bottlenecks

1. **Excel file I/O** - Becomes slow with 5000+ entries
2. **No caching** - Every request reads entire Excel file
3. **Full table scan** - No indexing in Excel

### Optimization Opportunities

1. **Cache today's feeds in memory** (invalidate on write)
2. **Migrate to SQLite** (indexed queries)
3. **Paginate feed list** (only load last 50)
4. **Lazy load stats** (don't calculate on every request)

**Current verdict:** No optimizations needed yet. Wait until parents report slowness.

---

## Troubleshooting Guide for AI Agents

### "Server won't start"

**Check:**
1. Is port 8080 already in use? `lsof -i :8080`
2. Is virtual environment activated? `source venv/bin/activate`
3. Are dependencies installed? `pip list | grep flask`
4. Python version >= 3.8? `python --version`

**Fix:**
```bash
pkill -f "python.*app.py"  # Kill old servers
source venv/bin/activate
pip install -r requirements.txt
./start.sh
```

### "Can't access from phone"

**Check:**
1. Same WiFi network?
2. Firewall blocking port 8080?
3. Using correct IP address?
4. Bookmark has old port (:5000)?

**Fix:**
```bash
./test_connectivity.sh  # Diagnoses issues
```

### "API returns 500 error"

**Check:**
1. Server logs for stack trace
2. Excel file exists and readable?
3. Timezone datetime bug?

**Debug:**
```bash
# Check server logs
tail -f server.log

# Test API manually
curl http://localhost:8080/api/feeds
```

### "Tests failing"

**Common causes:**
1. Fixture not providing temp file
2. Timezone handling changed
3. Row ID assumptions after delete
4. Voice parser logic diverged from JS

**Fix:**
```bash
pytest tests/test_api_feeds.py -v -s  # Run with output
pytest tests/test_concurrent.py -v    # Thread safety
```

### "Data lost / Excel corrupt"

**Recovery:**
1. Check for backup files (`feeds.xlsx~`, etc.)
2. Look in system temp directories
3. Check git history if tracked

**Prevention:**
```bash
# Add daily backup cron job
0 0 * * * cp /path/to/feeds.xlsx /path/to/backups/feeds-$(date +\%Y\%m\%d).xlsx
```

---

## Code Conventions

### Python Style
- Follow PEP 8
- Docstrings on all functions
- Type hints not used (kept simple)
- Comments explain WHY, not WHAT

### JavaScript Style
- camelCase for variables
- Comments for complex logic
- No semicolons (consistent with codebase)

### Naming
- `feed_data` - snake_case in Python
- `feedData` - camelCase in JavaScript
- `EXCEL_FILE` - UPPER_CASE for constants (legacy, now uses function)

### Commit Messages
Follow format:
```
Short summary (imperative mood)

- Bullet point details
- What changed and why

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## AI Agent Onboarding Checklist

Before making changes, verify:

- [ ] Read this entire document
- [ ] Run tests: `pytest tests/ -v` (should be 111 passing)
- [ ] Start server: `./start.sh`
- [ ] Test from browser: `http://localhost:8080`
- [ ] Check Excel file exists: `ls -la feeds.xlsx`
- [ ] Review critical sections:
  - [ ] Thread safety (file_lock)
  - [ ] Timezone handling
  - [ ] Row ID behavior
  - [ ] Voice parser keyword order

Before committing:

- [ ] Run tests: `pytest tests/ -v`
- [ ] Manual smoke test:
  - [ ] Log a bottle feed
  - [ ] Log a nursing session
  - [ ] Check Excel file has entries
  - [ ] Delete an entry
  - [ ] Verify stats update
- [ ] Update this document if architecture changed
- [ ] Update tests if behavior changed
- [ ] Git commit with descriptive message

---

## Future Enhancements (Potential)

### High Priority
1. **Automated backups** - Daily export to cloud
2. **Data export** - Google Sheets integration
3. **Error handling** - Better frontend error messages
4. **Input validation** - Prevent negative amounts, etc.

### Medium Priority
5. **SQLite migration** - Better performance at scale
6. **Offline mode** - localStorage + sync when online
7. **Night mode toggle** - Manual dark/light switch

### Low Priority
9. **Multi-baby support** - Track twins
10. **Reminders** - "It's been 3 hours, check baby"
11. **Export to PDF** - Weekly summary reports
12. **Voice commands** - "Log last feed" without opening app

### Won't Do
- Authentication (only 2 trusted users on home network)
- Social features (this is personal data)
- Mobile apps (web app works fine)
- Complex analytics (parents just need simple tracking)

---

## Contact & Resources

**GitHub:** https://github.com/nkanhai/baby_oclock
**Baby:** Esmé (6 days old as of initial commit)
**Built for:** Exhausted parents at 3am

**Key Documentation:**
- `README.md` - User-facing documentation
- `SETUP.md` - Installation and setup guide
- `MANUAL_TEST_CHECKLIST.md` - 28 real-world test scenarios
- `TEST_SUMMARY.md` - Automated test documentation
- `TROUBLESHOOTING.md` - Common issues and fixes
- `CLAUDE.md` - This file (AI agent context)

**Testing:**
- Run all tests: `pytest tests/ -v`
- Test specific file: `pytest tests/test_api_feeds.py -v`
- Test with output: `pytest tests/ -v -s`

**Questions to Ask User:**
- SQLite vs Excel preference?
- Google Sheets export priority?
- Any pain points with current implementation?
- Performance issues with large datasets?

---

## Version History

**v1.0 (Initial)** - February 10, 2026
- Flask backend with Excel storage
- Mobile-first UI with dark mode
- Voice input support
- 111 automated tests (all passing)
- Thread-safe concurrent writes
- Timezone bug fixed
- Timezone bug fixed
- Port changed to 8080 (from 5000)

**v1.1 (Charts)** - February 13, 2026
- Added Charts tab with 3 visualizations
- Daily Milk Intake, Diaper Changes, Feed Timeline
- 7/14/30 day date ranges

---

## Final Notes for AI Agents

This codebase is intentionally simple. Don't over-engineer it. The parents need:
1. **Reliability** - No data loss
2. **Speed** - Log in under 5 seconds
3. **Simplicity** - Works at 3am when exhausted

Before adding complexity, ask: "Does this make it easier for a sleep-deprived parent to log a feed at 3am?"

If the answer is no, don't add it.

Good luck! 🍼👶
