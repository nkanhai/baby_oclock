Context
The Baby Feed Tracker currently has four feed types (Bottle, Nurse, Pump, Voice) displayed in a 2x2 action grid. The parents need diaper change tracking to monitor Esmé's diaper changes (pee, poop, or both) and see when the last diaper was changed. The voice functionality is not being used and needs to be hidden behind a feature flag, as it's currently not very usable.
Why This Change:

Diaper tracking is essential for baby care monitoring (as important as feeding)
Parents need to know when the last diaper was changed and track daily patterns
Voice input is experimental and not needed for current workflow
The UI grid has space for 4 buttons - diaper will replace voice's position

Key Requirements:

Add diaper tracking with pee/poop/both options
Show "last diaper change" timer on home screen
Track diaper changes in same Excel file using existing logging infrastructure
Hide voice functionality behind a simple feature flag (don't delete code)
Follow existing patterns exactly (button → modal → log flow)


Implementation Approach
Architecture Overview
The app already has a generic feed tracking system that works for any type:

Frontend sends {type, side, amount_ml, duration_min, notes} to /api/feeds
Backend's format_feed_type(type, side) converts to human-readable Excel format
Excel stores all entries in one table with generic columns

Key Insight: We'll reuse the "side" parameter for pee/poop/both (no schema changes needed):

{type: "diaper", side: "pee"} → Excel stores: "Diaper (Pee)"
{type: "diaper", side: "poop"} → Excel stores: "Diaper (Poop)"
{type: "diaper", side: "both"} → Excel stores: "Diaper (Both)"

This follows the exact pattern of nurse/pump tracking which already use "side" for left/right/both.

Critical Files to Modify

baby_oclock/templates/index.html (lines 691-694, ~700-850, ~900-1000+)

Add feature flag constant
Replace voice button with diaper button
Add diaper modal HTML
Add CSS for diaper styling
Add JavaScript event handlers
Extend logFeed() function
Add "last diaper change" display logic


baby_oclock/app.py (lines 74-92, 257-319, 366-413)

Extend format_feed_type() to handle "diaper" type
Add diaper counting to /api/stats endpoint
Add last_diaper_minutes_ago and last_diaper_summary to /api/feeds response


baby_oclock/tests/test_diaper.py (NEW FILE)

Create comprehensive test suite with 15+ test cases
Cover all diaper types, stats, edge cases, timer calculation


baby_oclock/tests/test_api_feeds.py

Add diaper test case to existing TestCreateFeed class


baby_oclock/CLAUDE.md (documentation update)

Add diaper tracking section
Document feature flag system
Update "Adding a New Feed Type" example




Detailed Implementation Steps
Phase 1: Feature Flag System (5 minutes)
File: baby_oclock/templates/index.html
Add feature flag constant after opening <script> tag (around line 1180):
javascript<script>
    // Feature Flags
    const FEATURE_FLAGS = {
        VOICE_INPUT_ENABLED: false  // Set to true to enable voice functionality
    };
Wrap voice button visibility check (modify existing code around line 1300):
javascript// OLD CODE:
if (!recognition) {
    voiceBtn.style.display = 'none';
}

// NEW CODE:
if (!FEATURE_FLAGS.VOICE_INPUT_ENABLED || !recognition) {
    voiceBtn.style.display = 'none';
}
Wrap voice event listener (modify existing code around line ~1350):
javascript// OLD CODE:
voiceBtn.addEventListener('click', () => {
    if (recognition) {
        openModal(voiceModal);
        startVoiceRecognition();
    }
});

// NEW CODE:
if (FEATURE_FLAGS.VOICE_INPUT_ENABLED) {
    voiceBtn.addEventListener('click', () => {
        if (recognition) {
            openModal(voiceModal);
            startVoiceRecognition();
        }
    });
}
Verification: Set flag to false → reload page → voice button hidden.

Phase 2: Diaper Button UI (10 minutes)
File: baby_oclock/templates/index.html
Replace voice button HTML (lines 691-694):
html<!-- OLD: Voice button -->
<button class="action-btn voice" id="voiceBtn">
    <span class="emoji">🎤</span>
    <span>Voice</span>
</button>

<!-- NEW: Diaper button -->
<button class="action-btn diaper" id="diaperBtn">
    <span class="emoji">🩱</span>
    <span>Diaper</span>
</button>
Add diaper CSS styles (add after pump styles, around line 140):
css.action-btn.diaper {
    border-color: #9C87E8;
}

.action-btn.diaper:active {
    transform: translateY(2px);
    box-shadow: 0 2px 8px rgba(156, 135, 232, 0.3);
}

.diaper-side-btn {
    border-color: #9C87E8;
}

.diaper-side-btn.selected {
    background: #9C87E8;
    color: white;
}
Verification: Diaper button appears in bottom-right position with purple border.

Phase 3: Diaper Modal HTML (10 minutes)
File: baby_oclock/templates/index.html
Add diaper modal after pumpModal (around line 850):
html<div class="modal" id="diaperModal">
    <div class="modal-content">
        <div class="modal-title">🩱 Diaper Change</div>

        <div class="side-selector">
            <button class="side-btn diaper-side-btn" data-type="pee">💧 Pee</button>
            <button class="side-btn diaper-side-btn" data-type="poop">💩 Poop</button>
            <button class="side-btn diaper-side-btn" data-type="both">Both</button>
        </div>

        <div class="expandable">
            <button class="expandable-toggle" id="diaperMoreToggle">+ More options</button>
            <div class="expandable-content" id="diaperMoreContent">
                <div class="custom-input-group">
                    <label>Notes</label>
                    <input type="text" class="custom-input" id="diaperNotes" placeholder="Optional notes (e.g., blowout, rash)">
                </div>
            </div>
        </div>

        <div class="modal-actions">
            <button class="modal-btn secondary" id="diaperCancel">Cancel</button>
        </div>
    </div>
</div>
Verification: Modal HTML is in place (won't be visible until JavaScript hooks it up).

Phase 4: Diaper JavaScript Event Handlers (15 minutes)
File: baby_oclock/templates/index.html
Get DOM elements (add after other modal element declarations, around line 1200):
javascriptconst diaperBtn = document.getElementById('diaperBtn');
const diaperModal = document.getElementById('diaperModal');
Add button click listener (around line 1350):
javascript// Open diaper modal
diaperBtn.addEventListener('click', () => openModal(diaperModal));

// Cancel button
document.getElementById('diaperCancel').addEventListener('click', () => closeModal(diaperModal));

// Diaper type selection buttons (immediate log)
document.querySelectorAll('#diaperModal .side-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const type = btn.dataset.type;  // "pee", "poop", or "both"
        logFeed('diaper', type);
    });
});

// Expandable toggle
document.getElementById('diaperMoreToggle').addEventListener('click', () => {
    const content = document.getElementById('diaperMoreContent');
    const toggle = document.getElementById('diaperMoreToggle');
    content.classList.toggle('open');
    toggle.textContent = content.classList.contains('open') ? '− Less options' : '+ More options';
});
Extend logFeed() function to handle diaper notes (find logFeed function around line 1450, add diaper case):
javascriptasync function logFeed(type, side = null, amountMl = null) {
    let duration = null;
    let notes = '';

    // Get optional fields based on type
    if (type === 'bottle') {
        // ... existing bottle code ...
    } else if (type === 'nurse') {
        // ... existing nurse code ...
    } else if (type === 'pump') {
        // ... existing pump code ...
    } else if (type === 'diaper') {
        // NEW: Get diaper notes
        notes = document.getElementById('diaperNotes').value || '';
    }

    // ... rest of function unchanged ...
}
Add diaper modal close in success handler (around line 1500):
javascript// Close appropriate modal
closeModal(bottleModal);
closeModal(nurseModal);
closeModal(pumpModal);
closeModal(diaperModal);  // NEW
Verification: Click diaper button → modal opens → click "Pee" → logs successfully.

Phase 5: Backend - Extend format_feed_type() (5 minutes)
File: baby_oclock/app.py (lines 74-92)
Add diaper case:
pythondef format_feed_type(feed_type, side=None):
    """Convert feed type and side into Excel-friendly string."""
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
        elif side == "right":
            return "Pump (Right)"
        else:
            return "Pump (Both)"
    elif feed_type == "diaper":
        # NEW: Handle diaper tracking
        if side == "pee":
            return "Diaper (Pee)"
        elif side == "poop":
            return "Diaper (Poop)"
        elif side == "both":
            return "Diaper (Both)"
        else:
            return "Diaper"
    return feed_type
Verification: POST diaper via curl → check Excel → sees "Diaper (Pee)".

Phase 6: Backend - Add Last Diaper Timer (10 minutes)
File: baby_oclock/app.py
Modify GET /api/feeds response (around lines 257-319):
Add after last_feed_summary calculation (around line 306):
python# Calculate last diaper change
last_diaper_minutes_ago = None
last_diaper_summary = None

for feed in feeds:  # Already sorted by timestamp descending
    if "Diaper" in feed["type"]:
        last_diaper_timestamp = datetime.fromisoformat(feed["timestamp"])
        # Remove timezone info if present
        if last_diaper_timestamp.tzinfo is not None:
            last_diaper_timestamp = last_diaper_timestamp.replace(tzinfo=None)
        last_diaper_minutes_ago = int((datetime.now() - last_diaper_timestamp).total_seconds() / 60)
        last_diaper_summary = f"{feed['type']} at {feed['time']}"
        break
Add to return statement (around line 313):
pythonreturn jsonify({
    "feeds": feeds,
    "last_feed_minutes_ago": last_feed_minutes_ago,
    "last_feed_summary": last_feed_summary,
    "last_diaper_minutes_ago": last_diaper_minutes_ago,  # NEW
    "last_diaper_summary": last_diaper_summary,  # NEW
    "total_ml_today": round(total_ml_today, 1),
    "total_feeds_today": total_feeds_today
})
Verification: GET /api/feeds → response includes last_diaper_minutes_ago field.

Phase 7: Backend - Add Diaper Stats (5 minutes)
File: baby_oclock/app.py (lines 366-413)
Add diaper counting in get_stats() function (around line 385):
python# Add after pump_ml calculation
diaper_changes = 0

for feed in feeds:
    # ... existing bottle/nurse/pump logic ...

    # Count diaper changes (NEW)
    if "Diaper" in feed["type"]:
        diaper_changes += 1
Add to return statement (around line 405):
pythonreturn jsonify({
    "today": {
        "total_ml": round(total_ml, 1),
        "total_feeds": total_feeds,
        "total_nursing_sessions": nursing_sessions,
        "total_pump_ml": round(pump_ml, 1),
        "avg_feed_interval_min": avg_interval,
        "total_diaper_changes": diaper_changes  # NEW
    }
})
Verification: GET /api/stats → response includes total_diaper_changes.

Phase 8: Frontend - Display Last Diaper Timer (10 minutes)
File: baby_oclock/templates/index.html
Modify loadFeeds() function (find around line 1550, add after last feed display):
javascript// Display last diaper change timer (NEW)
if (data.last_diaper_minutes_ago !== null) {
    const hours = Math.floor(data.last_diaper_minutes_ago / 60);
    const mins = data.last_diaper_minutes_ago % 60;
    let timeStr = hours > 0 ? `${hours}h ${mins}m ago` : `${mins}m ago`;

    lastFeedDiv.innerHTML += `
        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #404554;">
            <div style="font-size: 14px; color: #a8adb8;">Last diaper change</div>
            <div style="font-size: 24px; font-weight: 600; color: #9C87E8; margin-top: 4px;">
                ${timeStr}
            </div>
            <div style="font-size: 13px; color: #8a8f9e; margin-top: 2px;">
                ${data.last_diaper_summary}
            </div>
        </div>
    `;
}
Verification: Log a diaper → home screen shows "Last diaper change: 2m ago".

Phase 9: Testing (30 minutes)
Create new test file: baby_oclock/tests/test_diaper.py
python"""
Test diaper tracking functionality.
"""

import pytest
from datetime import datetime, timedelta


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
        timestamp = (datetime.now() - timedelta(minutes=30)).isoformat()
        client.post('/api/feeds', json={
            "type": "diaper",
            "side": "pee",
            "timestamp": timestamp
        })

        response = client.get('/api/feeds')
        data = response.get_json()

        assert data['last_diaper_minutes_ago'] is not None
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
Update existing test: baby_oclock/tests/test_api_feeds.py
Add to TestCreateFeed class:
pythondef test_log_diaper_change(self, client):
    """Log a diaper change"""
    response = client.post('/api/feeds', json={
        "type": "diaper",
        "side": "pee"
    })
    assert response.status_code == 201
Run tests:
bashcd baby_oclock
pytest tests/ -v
Expected: All tests pass including 7+ new diaper tests.

Phase 10: Documentation Update (5 minutes)
File: baby_oclock/CLAUDE.md
Add new section after "Core Functionality":
markdown### Diaper Tracking

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
- `last_diaper_summary` - Description of last diaper change

### Feature Flags

**VOICE_INPUT_ENABLED** (default: false)
- Controls visibility of voice input button and modal
- Set to `true` in JavaScript to enable voice functionality
- Location: `templates/index.html`, top of `<script>` section

Verification Checklist
After implementation, verify:
Basic Functionality

 Diaper button appears in bottom-right position (where voice was)
 Voice button is hidden (feature flag is false)
 Click diaper button → modal opens with 3 buttons (Pee, Poop, Both)
 Click "Pee" → logs successfully, toast shows "Diaper (Pee) logged"
 Click "Poop" → logs successfully
 Click "Both" → logs successfully

Excel Integration

 Open baby_oclock/feeds.xlsx
 Verify entries show as "Diaper (Pee)", "Diaper (Poop)", "Diaper (Both)"
 Verify Date, Time, Logged By columns are populated correctly
 Verify Notes column shows optional notes

Last Diaper Timer

 After logging diaper, home screen shows "Last diaper change: 0m ago"
 Wait 1 minute, refresh → updates to "1m ago"
 Log another diaper → timer resets to "0m ago"
 Log multiple diapers → shows most recent one

Stats Endpoint

 GET /api/stats → response includes total_diaper_changes
 Log 3 diapers → stats shows count of 3
 Verify diapers don't affect total_ml or total_feeds

Feature Flag

 Set FEATURE_FLAGS.VOICE_INPUT_ENABLED = true → voice button appears
 Set to false → voice button hidden, diaper button visible
 Voice functionality still works when flag is true

Edge Cases

 Can add notes to diaper changes via "More options"
 Can delete diaper entries from feed list
 Diaper entries appear in correct chronological order mixed with feeds
 "Mom" and "Dad" toggle works for diaper logging
 Logging at midnight works correctly

Tests

 Run pytest tests/ -v → all tests pass
 Run pytest tests/test_diaper.py -v → 7 diaper tests pass
 No regressions in existing feed tests


Implementation Time Estimate

Phase 1: Feature Flag (5 min)
Phase 2: Diaper Button UI (10 min)
Phase 3: Diaper Modal HTML (10 min)
Phase 4: JavaScript Handlers (15 min)
Phase 5: Backend format_feed_type (5 min)
Phase 6: Last Diaper Timer (10 min)
Phase 7: Diaper Stats (5 min)
Phase 8: Frontend Display (10 min)
Phase 9: Testing (30 min)
Phase 10: Documentation (5 min)

Total: ~1.5 hours

Rollback Strategy
If issues arise:
Disable diaper tracking:
html<!-- Comment out diaper button -->
<!-- <button class="action-btn diaper" id="diaperBtn">... -->
Re-enable voice:
javascriptFEATURE_FLAGS.VOICE_INPUT_ENABLED = true;
Remove diaper entries from Excel:

Open feeds.xlsx
Filter Type column for "Diaper"
Delete rows

No database migrations or complex rollback needed.

Success Criteria
Implementation is successful when:

✅ Diaper button replaces voice button in UI
✅ Parents can log pee/poop/both diaper changes in 2 taps
✅ "Last diaper change" timer appears on home screen
✅ Diaper entries appear in Excel file with correct formatting
✅ Stats endpoint includes diaper count
✅ Voice functionality is hidden but code remains intact
✅ All 111+ tests pass (including 7+ new diaper tests)
✅ No breaking changes to existing feed tracking
✅ Feature flag allows easy re-enabling of voice
✅ Implementation follows existing patterns exactly