# Quick Setup Guide for Baby Feed Tracker

## For the Impatient (TL;DR)

```bash
./start.sh
```

Then open the URL shown on your phone and bookmark it to your home screen.

---

## Detailed Setup

### 1. First-Time Setup

**Requirements:**
- Python 3.8 or higher
- WiFi network (both computer and phones on the same network)

**Steps:**

1. Navigate to the project directory:
   ```bash
   cd /path/to/Esme_oClock
   ```

2. Run the start script:
   ```bash
   ./start.sh
   ```

   This will:
   - Create a Python virtual environment (if needed)
   - Install Flask and openpyxl
   - Start the server
   - Display the URL to access from your phone

3. You'll see output like:
   ```
   Starting Baby Tracker...
   Open on your phone: http://192.168.0.238:5000

   📊 Data saved to: feeds.xlsx
   ```

### 2. Access from Your Phone

1. **On your phone**, open Safari (iOS) or Chrome (Android)

2. Navigate to the URL shown (e.g., `http://192.168.0.238:5000`)

3. **Bookmark to home screen** for one-tap access:
   - **iOS**: Tap Share → Add to Home Screen → Add
   - **Android**: Tap Menu (⋮) → Add to Home Screen → Add

4. Done! You now have a home screen icon that works like an app.

### 3. Daily Use

Once set up, you just need to:

1. Start the server on your computer:
   ```bash
   ./start.sh
   ```

2. Tap the home screen icon on your phone

3. Start tracking feeds!

---

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Common Issues

### "Address already in use" Error

Port 5000 might be used by another service (often AirPlay on macOS).

**Solution 1 (Recommended)**: Disable AirPlay Receiver
- macOS: System Settings → General → AirDrop & Handoff → Turn off "AirPlay Receiver"

**Solution 2**: Use a different port by editing `app.py`:
```python
# Change the last line from:
app.run(host="0.0.0.0", port=5000, debug=False)

# To:
app.run(host="0.0.0.0", port=5001, debug=False)
```

Then access at `http://192.168.x.x:5001` instead.

### "Can't connect from phone"

1. Make sure your computer and phone are on the **same WiFi network**
2. Check your computer's firewall settings — port 5000 needs to be open
3. Verify the IP address is correct by running:
   ```bash
   # macOS
   ipconfig getifaddr en0

   # Linux
   hostname -I
   ```

### "Voice button doesn't appear"

Voice input requires Safari (iOS) or Chrome (Android). If your browser doesn't support the Web Speech API, the voice button will be hidden automatically. This is normal — just use the regular buttons.

---

## Data Management

### Where is my data?

All feeds are saved to `feeds.xlsx` in the project directory.

### Opening the Excel file

You can open `feeds.xlsx` anytime in:
- Microsoft Excel
- Google Sheets (upload the file)
- Apple Numbers
- LibreOffice Calc

### Backing up your data

Just copy `feeds.xlsx` to another location:
```bash
cp feeds.xlsx ~/Dropbox/baby-feeds-backup-$(date +%Y%m%d).xlsx
```

### Sharing data with your partner

Both parents can access the web app from their phones on the same network. The data is shared automatically since it's stored on the computer running the server.

If you want to send a copy of the data:
1. Email the `feeds.xlsx` file
2. Or upload it to Google Drive/Dropbox/iCloud

---

## Tips & Tricks

### Run the server in the background

```bash
nohup ./start.sh > server.log 2>&1 &
```

Then you can close the terminal and the server keeps running.

To stop it later:
```bash
pkill -f "python.*app.py"
```

### Auto-start on computer boot (macOS)

Create a LaunchAgent:

1. Create file: `~/Library/LaunchAgents/com.babytracker.plist`
2. Contents:
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
   </dict>
   </plist>
   ```
3. Load it:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.babytracker.plist
   ```

### View stats in Excel

The Excel file has all the data. You can:
- Create pivot tables
- Calculate total oz per day
- Make charts showing feeding patterns
- Track trends over time

### Using with multiple babies

Just create separate folders with separate instances:
```bash
cp -r Esme_oClock Esme_oClock_Baby2
cd Esme_oClock_Baby2
# Edit app.py to use port 5001 instead
./start.sh
```

---

## Architecture Notes

This is intentionally simple:

- **No database**: Excel file is the database
- **No authentication**: It's on your home network
- **No cloud**: All data stays on your computer
- **No build step**: HTML/CSS/JS are inline
- **No frameworks**: Pure Flask + vanilla JS

This means:
- ✅ Fast to start
- ✅ Easy to modify
- ✅ No dependencies that break
- ✅ You own your data
- ✅ Works without internet

---

## Customization Ideas

### Change who's logging options

Edit `templates/index.html`, find:
```html
<button class="who-btn active" data-who="Mom">Mom</button>
<button class="who-btn" data-who="Dad">Dad</button>
```

Change "Mom" and "Dad" to whatever you want (e.g., "Parent 1", "Parent 2", or names).

### Add more quick amounts

Edit the bottle and pump modals in `templates/index.html`. Find:
```html
<button class="quick-btn" data-oz="1">1 oz</button>
...
<button class="quick-btn" data-oz="6">6 oz</button>
```

Add more buttons like:
```html
<button class="quick-btn" data-oz="7">7 oz</button>
<button class="quick-btn" data-oz="8">8 oz</button>
```

### Change colors

Edit the CSS in `templates/index.html`. Main colors are:
- Background: `#1a1f2e`
- Bottle blue: `#4A90D9`
- Nurse pink: `#E8877C`
- Pump teal: `#5CB8B2`

---

## Support

This is a personal project with no official support. But here are resources:

- **Flask docs**: https://flask.palletsprojects.com/
- **openpyxl docs**: https://openpyxl.readthedocs.io/
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

For issues or questions, check the code comments or search online. The codebase is intentionally small and readable.

---

## License

This is a personal project. Do whatever you want with it. No warranty. If you use it and it helps, that's great! If it doesn't work, sorry — you're on your own.

Good luck with the new baby! 👶🍼
