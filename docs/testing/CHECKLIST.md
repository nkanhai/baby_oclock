# Baby Feed Tracker — Getting Started Checklist

## Initial Setup (Do Once)

- [ ] Make sure Python 3.8+ is installed (`python3 --version`)
- [ ] Navigate to the project directory
- [ ] Run `./start.sh` to start the server
- [ ] Note the IP address shown (e.g., `http://192.168.0.238:5000`)
- [ ] On Mom's phone: Open the URL in Safari/Chrome
- [ ] On Mom's phone: Add to home screen (Share → Add to Home Screen)
- [ ] On Dad's phone: Open the URL in Safari/Chrome
- [ ] On Dad's phone: Add to home screen
- [ ] Test logging a feed from each phone
- [ ] Verify the Excel file (`feeds.xlsx`) was created
- [ ] Open `feeds.xlsx` in Excel/Sheets to verify data is there

## Daily Use

- [ ] Start the server: `./start.sh`
- [ ] Keep the terminal window open (or run in background)
- [ ] Both parents can now log feeds from their phones
- [ ] To stop the server: Press `Ctrl+C` in the terminal

## Optional Setup

- [ ] Set up auto-start on boot (see `SETUP.md`)
- [ ] Create automated backups of `feeds.xlsx`
- [ ] Customize the "Who's logging" options (Mom/Dad → your names)
- [ ] Adjust quick amount buttons if needed

## Troubleshooting

If you run into issues:

- [ ] Check `SETUP.md` for common problems
- [ ] Verify both devices are on the same WiFi
- [ ] Try disabling AirPlay Receiver on macOS (System Settings → General → AirDrop & Handoff)
- [ ] Check firewall settings (port 5000 must be open)
- [ ] Restart the server and try again

## First 24 Hours Testing

To make sure everything works before you really need it:

- [ ] Log a bottle feed from Mom's phone
- [ ] Log a nursing session from Dad's phone
- [ ] Test voice input ("Bottle 3 ounces")
- [ ] Delete a feed entry to test the undo/delete function
- [ ] Open `feeds.xlsx` and verify all entries are there
- [ ] Test logging feeds while holding the baby (one-handed use)
- [ ] Try using it in the dark (test the dark mode UI)

## When Baby Arrives

You'll be grateful you:

- [ ] Bookmarked to both home screens
- [ ] Know where the Excel file is saved
- [ ] Tested voice input beforehand
- [ ] Have the server auto-starting (optional but nice)
- [ ] Know how to quickly restart if needed

---

## Quick Reference Card

Keep this info handy:

- **Server start**: `./start.sh`
- **Server stop**: `Ctrl+C`
- **Access URL**: `http://192.168.x.x:5000` (check terminal for actual IP)
- **Data location**: `feeds.xlsx` in project folder
- **Bookmark location**: Phone home screen
- **Common amounts**: 1-6 oz (tap for instant log)

---

## Success Metrics

You'll know it's working when:

✅ You can log a feed in under 5 seconds
✅ Both parents can access from their phones
✅ The "time since last feed" updates automatically
✅ All feeds appear in the Excel file
✅ Voice input recognizes your commands
✅ You can use it one-handed in the dark at 3am

---

## Help! It's 3am and Nothing Works

**Don't panic.** You can always:

1. Track feeds on paper temporarily
2. Enter them into the app later
3. Or just restart the server: `./start.sh`

The app is a helper, not critical infrastructure. If it's down, your baby will still be fine. You've got this! 👶💪

---

Good luck! 🍀
