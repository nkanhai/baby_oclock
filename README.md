# 🍼 Baby Feed Tracker for Esmé

A dead-simple feed tracker designed for sleep-deprived parents. Big buttons, minimal steps, and all data saved to an Excel file you can open anytime.

## Features

- **Quick logging**: Log a bottle feed in under 5 seconds with 3 taps
- **Voice input**: Hands-free logging using your phone's built-in speech recognition
- **Last feed status**: See at a glance how long it's been since the last feed
- **Today's log**: View all feeds for the day in reverse chronological order
- **Excel export**: All data automatically saved to `feeds.xlsx` — open it in Excel, Google Sheets, or Numbers
- **Mobile-optimized**: Big touch targets, dark mode, works great on phones
- **Local network**: Access from any phone on your WiFi — no cloud, no accounts

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
      http://192.168.1.123:5000

   💻 Or on this computer:
      http://localhost:5000
   ```

5. **On your phone**: Open the URL and bookmark it to your home screen for quick access

## Usage

### Tracking Feeds

1. **Bottle**: Tap 🍼 → Select amount (1-6 oz or custom) → Done
2. **Nursing**: Tap 🤱 → Select side (Left/Right/Both) → Done
3. **Pumping**: Tap 💧 → Select side → Select amount → Done
4. **Voice**: Tap 🎤 → Say "Bottle 3 ounces" or "Nurse left 10 minutes" → Confirm

### Voice Input Examples

The voice parser handles natural language:

- "Bottle 3 ounces"
- "Fed three ounces"
- "Nurse left"
- "Nursed on the right for 10 minutes"
- "Pump both 4 oz"
- "Pumped both sides 4 ounces"

### Data Storage

All feeds are saved to `feeds.xlsx` in the project directory. The Excel file contains:

| Column | Description |
|--------|-------------|
| Date | Date of feed (YYYY-MM-DD) |
| Time | Time of feed (12-hour format) |
| Type | Feed (Bottle), Nurse (Left/Right/Both), or Pump (Left/Right/Both) |
| Amount (oz) | Quantity in ounces |
| Duration (min) | Duration in minutes (optional) |
| Notes | Free-text notes (optional) |
| Logged By | Who logged it (Mom/Dad) |
| Timestamp | ISO 8601 timestamp for sorting |

You can open this file in Excel, Google Sheets, or Numbers anytime to view or analyze the data.

## Network Access

The app binds to `0.0.0.0:5000` so it's accessible on your local network. Both parents can access it from their phones as long as they're on the same WiFi.

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

3. **Quick bottle logging**: The most common amounts (1-6 oz) are one tap away. For the first few weeks, you'll probably use 2-3 oz most often.

4. **Voice is great for nursing**: When you're nursing and can't reach the phone, just say "Nurse left" and confirm.

5. **Leave it running**: The server can run 24/7 on a laptop. Both parents can log from their phones anytime.

6. **Undo mistakes**: After logging, you have 5 seconds to tap "Undo" if you made a mistake.

## Troubleshooting

**Q: Voice button doesn't appear**
A: Voice input requires Safari (iOS) or Chrome (Android). If your browser doesn't support the Web Speech API, the voice button will be hidden.

**Q: Can't access from phone**
A: Make sure both your computer and phone are on the same WiFi network. Check your firewall settings — port 5000 needs to be open.

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
4. ✅ Optionally use voice to log hands-free
5. ✅ See today's feed history at a glance
6. ✅ Know that all data is safely written to an Excel file they can open anytime

---

## License

This is a personal project. Use it however you want. No warranty. If it breaks at 3am, you're on your own (but it probably won't).

## Credits

Built with ❤️ for Esmé by a couple of very tired parents.
