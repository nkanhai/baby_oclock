# Fix Feed Count Stats & Add Swipe Navigation

## Summary
Two major improvements:
1. **Bug Fix**: Corrected feed statistics to exclude pumps, diapers, and vitamins from daily totals.
2. **New Feature**: Added swipe navigation to switch between Tracker and Charts tabs on mobile.

## Changes

### 1. Feed Count Logic Fix
- **Backend (`app.py`)**: Updated `get_feeds` to explicitly filter types (Bottle/Nurse only) for totals.
- **Frontend (`index.html`)**: Updated "Today" stats calculation to match backend logic.
- **Tests**: Added regression test `test_pump_and_diaper_excluded_from_totals`.

### 2. Swipe Navigation
- **Frontend (`index.html`)**:
    - Refactored tab switching into a reusable `switchTab` function.
    - Added `touchstart` and `touchend` event listeners.
    - Implemented swipe logic (Left -> Charts, Right -> Tracker).

### 3. Documentation
- Updated `README.md` to include Swipe Navigation in feature list.
- Updated `CLAUDE.md` with implementation details for both features.

## Verification
- **Automated Tests**: Ran full test suite. All tests passed.
- **Manual Verification**: 
  - Verified feed counts in browser (Bottles/Nurse only).
  - Verified swipe navigation in browser simulation.

## Related Issues
- Incorrect feed tallies next to day tabs.
- User request for swipe navigation.
