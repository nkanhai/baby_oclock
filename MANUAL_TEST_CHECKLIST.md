# Manual Test Checklist for Baby Feed Tracker

Use this checklist to verify all functionality works in real-world scenarios. Test on both Mom's and Dad's phones.

---

## Pre-Test Setup

- [ ] Server is running (`./start.sh`)
- [ ] Note the IP address shown in terminal: `http://_______________:8080`
- [ ] Both phones are on the same WiFi network
- [ ] Both phones have the app bookmarked to home screen

---

## Test 1: Initial Access & UI

**Phone: Mom's**

- [ ] Open the app from home screen bookmark
- [ ] Page loads within 2 seconds
- [ ] Dark mode is active (dark background)
- [ ] See header: "🍼 Esmé's Feed Tracker"
- [ ] See "Mom / Dad" toggle at top
- [ ] "Mom" is highlighted by default
- [ ] See "Last feed" box (says "Loading..." then shows status)
- [ ] See 4 big action buttons: 🍼 Bottle, 🤱 Nurse, 💧 Pump, 🎤 Voice
- [ ] See "Today's Log" section below
- [ ] All text is readable (not too small)
- [ ] No scrolling required to see all 4 buttons

**Phone: Dad's**

- [ ] Repeat all checks above
- [ ] Switch toggle to "Dad" - it highlights blue

---

## Test 2: Log Bottle Feed (Quick Path)

**Phone: Mom's**

- [ ] Tap "🍼 Bottle" button
- [ ] Modal opens with amount options
- [ ] See buttons: 1 oz, 2 oz, 3 oz, 4 oz, 5 oz, 6 oz
- [ ] Tap "3 oz"
- [ ] Modal closes immediately
- [ ] Toast appears at bottom: "✓ Bottle — 3 oz logged"
- [ ] Toast shows "Undo" button for 5 seconds
- [ ] "Last feed" updates to show "Just now" or "0 min ago"
- [ ] New entry appears in "Today's Log": time + "Bottle • 3 oz • Mom"
- [ ] Stats update: "1 feeds • 3 oz"

**Time this**: From tap "Bottle" to toast appearing should be **under 5 seconds**.

---

## Test 3: Log Bottle with Custom Amount

**Phone: Dad's**

- [ ] Switch toggle to "Dad"
- [ ] Tap "🍼 Bottle"
- [ ] Scroll down to see "Custom amount" input
- [ ] Tap input field
- [ ] Keyboard appears
- [ ] Type "2.5"
- [ ] Press Enter/Return on keyboard
- [ ] Modal closes
- [ ] Toast: "✓ Bottle — 2.5 oz logged"
- [ ] Entry appears: "Bottle • 2.5 oz • Dad"
- [ ] Stats update: "2 feeds • 5.5 oz"

---

## Test 4: Log Bottle with Optional Fields

**Phone: Mom's**

- [ ] Tap "🍼 Bottle"
- [ ] Tap "3 oz"
- [ ] Before it closes, tap "+ More options"
- [ ] See "Duration (minutes)" field
- [ ] Type "10"
- [ ] See "Notes" field
- [ ] Type "baby was sleepy"
- [ ] Tap outside modal or press done
- [ ] Entry shows: "Bottle • 3 oz • 10 min • Mom"
- [ ] Can see notes when viewing in log

---

## Test 5: Log Nursing Session

**Phone: Mom's**

- [ ] Tap "🤱 Nurse"
- [ ] Modal opens with three buttons: Left, Right, Both
- [ ] Tap "Left"
- [ ] Modal closes
- [ ] Toast: "✓ Nurse (left) logged"
- [ ] Entry appears: "Nurse (Left) • Mom"
- [ ] Stats update feed count (but not oz total)

**Then:**

- [ ] Tap "🤱 Nurse" again
- [ ] Tap "Both"
- [ ] Before closing, tap "+ More options"
- [ ] Enter duration: "15"
- [ ] Enter notes: "good latch"
- [ ] Entry shows: "Nurse (Both) • 15 min • Mom"

---

## Test 6: Log Pump Session

**Phone: Mom's**

- [ ] Tap "💧 Pump"
- [ ] Modal opens with: Left, Right, Both
- [ ] Tap "Both"
- [ ] Amount section appears
- [ ] Tap "4 oz"
- [ ] Modal closes
- [ ] Toast: "✓ Pump (both) — 4 oz logged"
- [ ] Entry appears: "Pump (Both) • 4 oz • Mom"
- [ ] Stats show pump oz added to total

---

## Test 7: Voice Input (Safari/Chrome only)

**Phone: Mom's (must use Safari on iOS or Chrome on Android)**

- [ ] Tap "🎤 Voice"
- [ ] Modal opens showing "Listening..."
- [ ] See microphone animation pulsing
- [ ] See example phrases
- [ ] Say clearly: **"Bottle 3 ounces"**
- [ ] Your speech appears as text
- [ ] Parsed data shows:
  - Type: bottle
  - Amount: 3 oz
- [ ] "Confirm" button appears
- [ ] Tap "Confirm"
- [ ] Entry is logged correctly

**Try more phrases:**

- [ ] "Nurse left 10 minutes" → Type: nurse, Side: left, Duration: 10
- [ ] "Pumped both 4 oz" → Type: pump, Side: both, Amount: 4.0
- [ ] "Fed baby three ounces" → Type: bottle, Amount: 3.0

**If voice button doesn't appear:**
- You're not using Safari (iOS) or Chrome (Android) - this is expected behavior

---

## Test 8: Delete Entry

**Phone: Either**

- [ ] Find any entry in "Today's Log"
- [ ] See small "×" button on the right
- [ ] Tap "×"
- [ ] Browser asks "Delete this feed entry?"
- [ ] Tap "OK"
- [ ] Entry disappears immediately
- [ ] Stats update correctly
- [ ] "Last feed" updates if you deleted the most recent

---

## Test 9: Undo Feature

**Phone: Either**

- [ ] Log a new bottle feed (any amount)
- [ ] Toast appears with "Undo" button
- [ ] Quickly tap "Undo" (within 5 seconds)
- [ ] Entry disappears
- [ ] Stats revert
- [ ] Toast disappears

**Then:**

- [ ] Log another feed
- [ ] Wait more than 5 seconds
- [ ] Toast should disappear automatically
- [ ] Entry stays (can't undo after timeout)

---

## Test 10: Concurrent Logging (Critical Test!)

**BOTH PHONES SIMULTANEOUSLY**

**Setup:**
- Mom and Dad both have app open
- Both ready to tap Bottle button

**Execute:**
- [ ] Mom taps "🍼 Bottle" → "2 oz" (at same time)
- [ ] Dad taps "🍼 Bottle" → "3 oz" (at same time)
- [ ] Both get success toasts
- [ ] Refresh both phones
- [ ] **Both entries appear** in the log
- [ ] One shows "Mom", one shows "Dad"
- [ ] Stats show both feeds (total 5 oz)
- [ ] Open `feeds.xlsx` on computer
- [ ] Both entries are in the Excel file
- [ ] No corruption or missing data

**This is the most important test** - it verifies both parents can log at the same time!

---

## Test 11: Last Feed Timer

**Phone: Either**

- [ ] Note the "Last feed" time (e.g., "5 min ago")
- [ ] Wait 1-2 minutes (do something else)
- [ ] App auto-updates every 30 seconds
- [ ] Timer should update without refreshing
- [ ] After ~30-60 seconds, check it changed (e.g., "6 min ago")

---

## Test 12: Today's Log Display

**Phone: Either**

- [ ] Entries are in **reverse chronological order** (newest first)
- [ ] Each entry shows:
  - Time in 12-hour format (e.g., "3:02 AM")
  - Type and details (e.g., "Bottle • 3 oz")
  - Who logged it (Mom or Dad)
- [ ] Times are correct for your timezone
- [ ] No duplicate entries
- [ ] Scroll works if more than ~6 entries

---

## Test 13: Date Boundary (Midnight Rollover)

**Late night test - only if testing around midnight:**

- [ ] Log a feed at 11:50 PM
- [ ] Wait until after midnight (12:01 AM)
- [ ] Log another feed
- [ ] Late night feed shows "11:50 PM"
- [ ] After midnight feed shows "12:01 AM"
- [ ] Both appear in "Today's Log" for their respective dates
- [ ] Stats only count today's date

---

## Test 14: Excel File Verification

**On computer:**

- [ ] Stop the server (Ctrl+C)
- [ ] Open `feeds.xlsx` in Excel, Numbers, or Google Sheets
- [ ] See header row: Date, Time, Type, Amount (oz), Duration (min), Notes, Logged By, Timestamp
- [ ] All logged entries are present
- [ ] Data matches what you see in the app
- [ ] Times are correct
- [ ] Special characters preserved (emojis in notes work)
- [ ] No blank rows or corrupted data

---

## Test 15: Phone Rotation & Orientation

**Phone: Either**

- [ ] Hold phone in portrait (vertical)
- [ ] Everything looks good
- [ ] Rotate to landscape (horizontal)
- [ ] App adjusts or stays usable
- [ ] No overlapping text
- [ ] Buttons still tappable

---

## Test 16: One-Handed Use

**Phone: Either**

- [ ] Hold phone in one hand only
- [ ] Try to log a bottle feed using only your thumb
- [ ] Can you reach all buttons?
- [ ] Can you tap amount buttons?
- [ ] Can you close modal?

**Test with baby in other arm:**
- Actually hold something in other arm
- Try logging a feed one-handed
- Is it realistic at 3am?

---

## Test 17: Dark Environment Test

**At night or in dark room:**

- [ ] Open app
- [ ] Is text readable in the dark?
- [ ] Is screen brightness not too bright?
- [ ] No harsh white backgrounds
- [ ] Blue action buttons visible but not glaring
- [ ] Can use without waking baby

---

## Test 18: Quick Reload Test

**Phone: Either**

- [ ] Refresh page (pull down or reload button)
- [ ] Page loads quickly (under 2 seconds)
- [ ] All data still there
- [ ] Last feed status correct
- [ ] Today's log populated

---

## Test 19: Network Interruption

**Phone: Either**

- [ ] Turn on Airplane Mode
- [ ] Try to log a feed
- [ ] Should get an error or fail
- [ ] Turn off Airplane Mode
- [ ] Try again - should work
- [ ] Previous data is still there

---

## Test 20: Multiple Days of Use

**Over several days:**

- [ ] Day 1: Log several feeds
- [ ] Day 2: Open app - see "Last feed: X hours ago"
- [ ] Day 2: "Today's Log" shows only Day 2 feeds
- [ ] Day 2: Log more feeds
- [ ] Open Excel file
- [ ] Entries from both days present
- [ ] Dates are correct (YYYY-MM-DD format)

---

## Test 21: Who's Logging Toggle

**Phone: Either**

- [ ] Toggle is set to "Mom"
- [ ] Log a feed
- [ ] Entry shows "Mom"
- [ ] Switch toggle to "Dad"
- [ ] Log a feed
- [ ] Entry shows "Dad"
- [ ] Toggle stays set when you log multiple feeds
- [ ] Refresh page - toggle resets to "Mom" (expected)

---

## Test 22: Stats Accuracy

**Phone: Either**

After logging several feeds today:

- [ ] Total feeds count is correct
- [ ] Total oz includes bottles + pumps (not nursing)
- [ ] Count matches number of visible entries
- [ ] Stats update after each new feed
- [ ] Stats update after deleting a feed

---

## Test 23: Edge Cases

### Very Long Notes
- [ ] Log feed with 500-character note
- [ ] Note is preserved
- [ ] No truncation in Excel

### Unicode and Emojis
- [ ] Log feed with note: "Baby said 👶 and smiled 😊"
- [ ] Emojis display correctly
- [ ] Check Excel - emojis preserved

### Decimal Amounts
- [ ] Log bottle with 2.5 oz
- [ ] Log bottle with 3.75 oz
- [ ] Decimals preserved in log
- [ ] Decimals preserved in Excel
- [ ] Stats calculate correctly

### Zero Amount
- [ ] Try logging bottle with 0 oz
- [ ] (Should work - maybe a failed feed attempt)

---

## Test 24: Server Restart

**Scenario: Server crashes and needs restart**

- [ ] Have several feeds logged
- [ ] Stop server on computer (Ctrl+C)
- [ ] Restart server (`./start.sh`)
- [ ] Refresh app on phone
- [ ] All previous feeds still visible
- [ ] Can log new feeds
- [ ] No data loss

---

## Test 25: Two-Parent Workflow

**Real-world scenario:**

**Time: 2:30 AM**
- [ ] Mom nurses baby (Dad's asleep)
- [ ] Mom logs: Nurse (Left) 15 min
- [ ] Mom goes back to bed

**Time: 5:00 AM**
- [ ] Dad gives bottle (Mom's asleep)
- [ ] Dad logs: Bottle 3 oz
- [ ] Dad sees last feed was 2.5 hrs ago (Mom's nursing session)

**Time: 7:30 AM**
- [ ] Mom wakes up, checks app
- [ ] Sees both entries (her nursing + Dad's bottle)
- [ ] Last feed shows correct time
- [ ] Total feeds: 2
- [ ] This workflow is smooth and clear

---

## Test 26: Bookmark & Home Screen Icon

**Phone: Both**

- [ ] App is bookmarked/added to home screen
- [ ] Tap icon - opens immediately
- [ ] No URL bar visible (feels like native app)
- [ ] Icon has baby bottle emoji or text label
- [ ] Easy to find among other apps

---

## Test 27: Performance Under Load

**Stress test:**

- [ ] Log 20 feeds in a row (mix of types)
- [ ] App stays responsive
- [ ] No lag when opening modals
- [ ] Scroll through log is smooth
- [ ] Excel file opens without issues
- [ ] File size is reasonable (<1 MB)

---

## Test 28: Accessibility

**Large font test:**
- [ ] Go to phone Settings → Display → Text Size
- [ ] Increase text size to Large
- [ ] Open app
- [ ] Text scales appropriately
- [ ] No overlapping UI elements

**Touch target test:**
- [ ] All buttons easy to tap
- [ ] No mis-taps on adjacent buttons
- [ ] Delete button (×) is easy to hit

---

## Pass/Fail Criteria

### Critical (Must Pass)
- ✅ Can log feeds from both phones
- ✅ Concurrent logging works (no data loss)
- ✅ Data persists after server restart
- ✅ Excel file has all entries
- ✅ Last feed timer is accurate
- ✅ Quick bottle logging is under 5 seconds

### Important (Should Pass)
- ✅ Voice input works (if available)
- ✅ Delete and undo work
- ✅ Stats are accurate
- ✅ Dark mode is comfortable at night
- ✅ One-handed use is feasible

### Nice to Have
- ✅ Smooth animations
- ✅ No scrolling for main actions
- ✅ Quick page loads

---

## Found Issues? Document Here:

**Issue 1:**
- Date/Time: ___________
- Phone: ___________
- What happened:
- Expected:
- Steps to reproduce:

**Issue 2:**
- Date/Time: ___________
- Phone: ___________
- What happened:
- Expected:
- Steps to reproduce:

---

## Final Checklist

After completing all tests:

- [ ] Both phones can access the app
- [ ] Both parents can log feeds successfully
- [ ] Concurrent logging works without issues
- [ ] Excel file contains all data
- [ ] No critical bugs found
- [ ] App is ready for real use with baby

---

## Notes for Real-World Use

**When baby arrives:**
- Keep server running 24/7 (or use auto-start script)
- Keep both phones charged
- Bookmark is easy to find
- Backup `feeds.xlsx` regularly (copy to Dropbox/iCloud)

**At 3 AM:**
- Dark mode helps
- Big buttons work even when exhausted
- Voice input is great if hands are full
- Toggle stays set to your name
- Quick tap → amount → done = logged

**Good luck with Esmé! 👶🍼**

---

## Test Completion

**Tested by:** ___________
**Date:** ___________
**Result:** ⬜ All Pass  ⬜ Minor Issues  ⬜ Major Issues
**Ready for use:** ⬜ Yes  ⬜ No

**Notes:**
