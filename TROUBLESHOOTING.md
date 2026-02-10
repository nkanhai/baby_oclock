# Troubleshooting Guide

## "Authorization Required" or "Can't Connect" Error on Phone

### Quick Fix Options

Try these in order:

### Option 1: Allow Python Through Firewall (Recommended)

1. **Open System Settings** on your Mac
2. Go to **Network** → **Firewall** (or **Security & Privacy** → **Firewall** on older macOS)
3. If Firewall is ON, click **Options** or **Firewall Options**
4. Look for Python in the list
5. Make sure it's set to **Allow incoming connections**
6. If Python isn't listed, click the **+** button and add:
   - `/usr/bin/python3` or
   - The python in your venv: `/Users/nicholaskanhai/Documents/Coding_Projects/Esme_oClock/venv/bin/python`
7. Click **OK** and try accessing from your phone again

### Option 2: Temporarily Disable Firewall (Quick Test)

**WARNING: Only do this temporarily to test, then re-enable it!**

1. Open **System Settings** → **Network** → **Firewall**
2. Turn Firewall **Off**
3. Try accessing from your phone
4. If it works, turn Firewall back **On** and use Option 1 instead

### Option 3: Use a Different Port

Some ports are more likely to be blocked. Let's try port 8080:

1. Edit `app.py` - find the last line:
   ```python
   app.run(host="0.0.0.0", port=5000, debug=False)
   ```

2. Change it to:
   ```python
   app.run(host="0.0.0.0", port=8080, debug=False)
   ```

3. Restart the server: `./start.sh`

4. Access from phone using: `http://192.168.x.x:8080`

### Option 4: Disable AirPlay Receiver (Might Be Using Port 5000)

1. **System Settings** → **General** → **AirDrop & Handoff**
2. Turn off **AirPlay Receiver**
3. Restart the server
4. Try accessing from phone again

## Other Common Issues

### "Connection Refused" or "Can't Reach Server"

**Check 1: Are you on the same WiFi?**
- Make sure your Mac and phone are on the **same WiFi network**
- Not one on WiFi and one on cellular
- Not one on 5GHz and one on 2.4GHz (though usually this works)

**Check 2: Is the server actually running?**
- Look at the terminal - do you see "Running on http://0.0.0.0:5000"?
- If not, restart: `./start.sh`

**Check 3: What's your Mac's IP address?**
- Run this command in terminal:
  ```bash
  ipconfig getifaddr en0
  ```
- Or if that returns nothing, try:
  ```bash
  ipconfig getifaddr en1
  ```
- Use this IP on your phone

### "Page Not Found" or 404 Error

You connected to the server, but got the wrong URL.

- Make sure you're going to: `http://192.168.x.x:5000/`
- NOT `https://` (no S)
- NOT missing the `http://` part
- Include the `:5000` port number

### Voice Button Doesn't Appear

This is **normal** if you're not using Safari (iOS) or Chrome (Android).

- iOS: Use **Safari** (not Firefox, not Chrome)
- Android: Use **Chrome** (not Firefox, not Samsung Internet)
- Voice input only works in browsers with Web Speech API support

### "Excel File Corrupted" Error

The app will automatically:
1. Back up the corrupted file
2. Create a new clean `feeds.xlsx`
3. You can try to recover data from the backup manually

### Server Won't Start - "Address Already in Use"

**Option A: Stop what's using port 5000**

Find what's using it:
```bash
lsof -i :5000
```

Kill that process:
```bash
kill -9 <PID>
```

**Option B: Use a different port** (see Option 3 above)

## Getting Your Mac's IP Address

### Method 1: From the server startup
When you run `./start.sh`, it shows:
```
Open on your phone: http://192.168.x.x:5000
```

### Method 2: Terminal command
```bash
ipconfig getifaddr en0
```
or
```bash
ipconfig getifaddr en1
```

### Method 3: System Settings
1. **System Settings** → **Network**
2. Click your WiFi connection
3. Look for "IP Address"

### Method 4: Quick command that works on Mac
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'
```

## Testing Your Setup

### Test 1: Can you access from your Mac's browser?

1. Open browser on your Mac
2. Go to: `http://localhost:5000`
3. If this works, the server is fine - it's just a network/firewall issue

### Test 2: Can you ping your Mac from your phone?

1. Note your Mac's IP (e.g., 192.168.0.238)
2. Install a network utility app on your phone
3. Try to ping that IP
4. If ping fails, it's a network issue (wrong WiFi, firewall, etc.)

### Test 3: Try from a different device

- Try accessing from another phone on the same WiFi
- Or from another computer on the same WiFi
- If it works from one device but not another, the problem is with that specific device

## Still Not Working?

### Emergency Workaround: Use Only on Mac's Browser

If you can't get the network access working:

1. Just use the Mac's browser: `http://localhost:5000`
2. Keep the Mac near the baby's area
3. Both parents log directly on the Mac (not ideal, but works!)

### Nuclear Option: Expose Via ngrok (Advanced)

If you need remote access and nothing else works:

1. Install ngrok: `brew install ngrok`
2. Start server: `./start.sh`
3. In another terminal: `ngrok http 5000`
4. Use the ngrok URL from your phone (works from anywhere)

**WARNING**: This exposes your tracker to the internet. Only use temporarily!

## Contact for Help

Since this is a local project:
- Check Flask documentation: https://flask.palletsprojects.com/
- Check Python firewall issues for macOS
- Search: "flask can't connect from phone macos firewall"

---

## Most Common Fix

**95% of the time it's the firewall.**

1. System Settings → Network → Firewall → Options
2. Add Python
3. Allow incoming connections
4. Done!

Try that first before anything else.
