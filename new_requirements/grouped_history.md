# Grouped History Requirements

## Problem
Currently, the feed log resets at midnight (showing only "Today"). This causes loss of context for parents who need to see recent feeding patterns, especially overnight or when comparing recent days.

## Requirements
1.  **Retention**: Show feed history beyond the current day.
2.  **Grouping**:
    *   **Today**: Feeds for the current day.
    *   **Yesterday**: Feeds for the previous day.
    *   **Previous Days**: Grouped by Day/Date (e.g., "Monday, 10/02").
3.  **Visual Hierarchy**:
    *   "Tomorrow" logic (nesting): As midnight passes, "Today" becomes "Yesterday", "Yesterday" becomes the Day name.
    *   Older days should likely be collapsible to avoid clutter.
4.  **Performance**: Limit history (e.g., 7 days) to prevent infinite scrolling issues. Note: This only affects the *view*, all data is still saved to `feeds.xlsx`.

## Planned Approach

### Backend (`app.py`)
*   Update `get_feeds_from_excel` to support a `min_date` or `limit_days` parameter.
*   Update `GET /api/feeds` to accept `limit_days` query param.
    *   If `limit_days` is provided, fetch feeds from `today - limit` to `today`.
    *   Default behavior (no param) stays "Today only" to preserve backward compatibility.

### Frontend (`index.html`)
*   Update `loadFeeds` to fetch `limit_days=7`.
*   Implement grouping logic:
    *   Map feeds to dates.
    *   Create sections for "Today", "Yesterday", and older dates.
    *   Render headers for each section.
*   UI Enhancements:
    *   Style the headers clearly.
    *   Add expand/collapse formatting for "Previous Days" to keep the list manageable.
