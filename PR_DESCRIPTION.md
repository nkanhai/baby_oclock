# PR: Manual Time Editing & Tumbler Conflict Fix

## Summary
This PR implements several key features and bug fixes requested to improve the usability of feed logging, specifically focusing on timestamp accuracy and conflict resolution between input methods.

## Changes

### 1. Manual Time Editing (Fixes Bug)
- **Problem**: Previously, editing a log entry would reset its time to "now", losing the original timestamp.
- **Fix**: The `editFeed` function now preserves the original time.
- **Feature**: Added a `time` input field to the "More options" section of all modals (Bottle, Nurse, Pump, Diaper), allowing parents to effectively "backdate" feeds or correct timestamps.

### 2. Pump Time Tracking
- **Feature**: Added the "Time" input field to the Pump modal.
- **Implementation**: Updated `editFeed` and `logFeed` to correctly handle time updates for Pump entries, ensuring parity with other feed types.

### 3. Tumbler vs Custom Input Resolution (Last Interaction Wins)
- **Problem**: Users could unintentionally set conflicting amounts by using both the Tumbler wheel and the Custom Amount input.
- **Fix**: Implemented "Last Interaction Wins" logic.
    - Interacting with the **Tumbler** (scroll/click) automatically **clears** the Custom Amount input.
    - Typing in the **Custom Amount** input overrides the Tumbler (standard behavior).
- **Benefit**: Removes ambiguity and ensures the logged amount matches the user's last distinct action.

### 4. Documentation
- Updated `README.md` with new feature descriptions.
- Updated `docs/dev/CLAUDE.md` with technical implementation details of the new features and logic.

## Verification
- **Automated Tests**: All 117 existing tests passed.
- **Manual Verification**:
    - Confirmed editing a log retains original time.
    - Confirmed changing time in "More options" updates the log correctly.
    - Confirmed Pump modal supports time editing.
    - Confirmed scrolling Tumbler clears custom amount input.
