# 🍼 Baby Feed Tracker for Esmé

A dead-simple feed and diaper tracker designed for sleep-deprived parents. Big buttons, minimal steps, and all data saved to an Excel file you can open anytime.

## Features

- **Quick logging**: Log a bottle feed in seconds with the intuitive Tumbler UI (0-99 ml)
- **Diaper tracking**: Log pee, poop, or both with 2 taps — see "last diaper change" timer on home screen
- **Voice input**: Hands-free logging using your phone's built-in speech recognition (hidden behind feature flag)
- **Last feed status**: See at a glance how long it's been since the last feed
- **Last diaper status**: See how long since the last diaper change
- **Today's log**: View all feeds for the day in reverse chronological order
- **History**: View the last 7 days of feeds and diaper changes, grouped by Today, Yesterday, and date
- **Excel export**: All data automatically saved to `feeds.xlsx` — open it in Excel, Google Sheets, or Numbers
- **Mobile-optimized**: Big touch targets, dark mode, works great on phones
- **Local network**: Access from any phone on your WiFi — no cloud, no accounts
- **Large Clock**: See the current time prominently displayed for easy reference

## Tech Stack

- **Backend**: Python 3 + Flask
- **Frontend**: Single HTML page (no frameworks)
- **Data**: Excel `.xlsx` file via `openpyxl`
- **Voice**: Browser Web Speech API (Safari/Chrome)

## Quick Start

### Option 1: One-command start (recommended)

```bash
./start.sh
```

### Option 2: Manual setup

1. Install Python 3.8 or higher

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the server:
   ```bash
   python app.py
   ```

4. The app will display URLs like:
   ```
   📱 Open on your phone:
      http://192.168.1.123:8080

   💻 Or on this computer:
      http://localhost:8080
   ```

5. **On your phone**: Open the URL and bookmark it to your home screen for quick access

## Usage

### Tracking Feeds

1. **Bottle**: Tap 🍼 → Select amount (ml) → Done
2. **Nursing**: Tap 🤱 → Select side (Left/Right/Both) → Done
3. **Pumping**: Tap 💧 → Select side → Select amount → Done
4. **Diaper**: Tap 🍑 → Select type (Pee/Poop/Both) → Done

### Voice Input Examples

The voice parser handles natural language:

- "Bottle 90 ml"
- "Fed 120 ml"
- "Nurse left"
- "Nursed on the right for 10 minutes"
- "Pump both 150 ml"
- "Pumped both sides 180 ml"

### Data Storage

All feeds are saved to `feeds.xlsx` in the project directory. The Excel file contains:

| Column | Description |
|--------|-------------|
| Date | Date of feed (YYYY-MM-DD) |
| Time | Time of feed (12-hour format) |
| Type | Feed (Bottle), Nurse (Left/Right/Both), Pump (Left/Right/Both), or Diaper (Pee/Poop/Both) |
| Amount (ml) | Quantity in milliliters |
| Duration (min) | Duration in minutes (optional) |
| Notes | Free-text notes (optional) |
| Logged By | Who logged it (Mom/Dad) |
| Timestamp | ISO 8601 timestamp for sorting |

You can open this file in Excel, Google Sheets, or Numbers anytime to view or analyze the data.

## Network Access

The app binds to `0.0.0.0:8080` so it's accessible on your local network. Both parents can access it from their phones as long as they're on the same WiFi.

### Finding Your IP Address

**On macOS:**
```bash
ipconfig getifaddr en0
```

**On Linux:**
```bash
hostname -I | awk '{print $1}'
```

**On Windows:**
```cmd
ipconfig
```
(Look for "IPv4 Address" under your active network adapter)

## Tips for Sleep-Deprived Parents

1. **Bookmark to home screen**: On iOS, tap Share → Add to Home Screen. On Android, tap the menu → Add to Home Screen. This gives you a one-tap launch.

2. **Use the "Who" toggle**: Switch between Mom/Dad at the top so you don't have to select it each time.

3. **Quick bottle logging**: The tumbler interface makes selecting amounts (e.g. 90-120 ml) very fast.

4. **Quick diaper logging**: Tap Diaper → tap Pee/Poop/Both — done in 2 taps.

5. **Leave it running**: The server can run 24/7 on a laptop. Both parents can log from their phones anytime.

6. **Undo mistakes**: After logging, you have 5 seconds to tap "Undo" if you made a mistake.

## Troubleshooting

**Q: Voice button doesn't appear**
A: Voice input is currently disabled by default behind a feature flag. To enable it, set `FEATURE_FLAGS.VOICE_INPUT_ENABLED = true` in the `<script>` section of `templates/index.html`. Voice input requires Safari (iOS) or Chrome (Android).

**Q: Can't access from phone**
A: Make sure both your computer and phone are on the same WiFi network. Check your firewall settings — port 8080 needs to be open.

**Q: Excel file is corrupted**
A: The app includes basic corruption detection. If the file gets corrupted, it will back up the old file and create a new one.

**Q: Two parents logged at the exact same time**
A: The app uses file locking to prevent corruption from concurrent writes. One write will wait for the other to finish.

## Project Structure

```
baby-tracker/
├── app.py                 # Flask server
├── templates/
│   └── index.html         # Single-page UI
├── feeds.xlsx             # Auto-created data file
├── tests/                 # 117+ automated tests
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── start.sh               # One-command launcher
```

## What This App Doesn't Do

- No cloud hosting or sync
- No user accounts or authentication
- No complex charts or analytics
- No mobile apps (it's a web app — just bookmark it)
- No internet required (works entirely on your local network)

## Success Criteria

A sleep-deprived parent at 3am can:

1. ✅ Open the bookmark on their phone
2. ✅ See immediately how long it's been since the last feed
3. ✅ Log a bottle feed in under 5 seconds and 3 taps
4. ✅ Log a diaper change in 2 taps
5. ✅ See today's feed and diaper history at a glance
6. ✅ Know that all data is safely written to an Excel file they can open anytime

---

## License

This is a personal project. Use it however you want. No warranty. If it breaks at 3am, you're on your own (but it probably won't).

## Credits

Built with ❤️ for Esmé by a couple of very tired parents.
