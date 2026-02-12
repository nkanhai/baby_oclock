# Migration Guide: baby_oclock Server

This guide details how to move the `baby_oclock` application and its remote access (Cloudflare Tunnel) from your current MacBook to a dedicated "Server" MacBook.

**Goal:**
1.  Run the Flask Application automatically on the new machine.
2.  Run the Cloudflare Tunnel automatically on the new machine.
3.  Disable everything on the current machine to avoid conflicts.

---

## Phase 1: Prepare the New Machine (The Server)

Perform these steps on the **NEW** MacBook.

### 1.1 Install Prerequisites
Open Terminal and install Homebrew (if not installed), Python, and Git.

```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Cloudflared
brew install python3 cloudflared
```

### 1.2 Transfer Code and Data
You need to copy the project folder from your current Mac to the new one.
*   **Source:** `/Users/nicholaskanhai/Documents/Coding_Projects/Esme_oClock/baby_oclock`
*   **Destination:** `~/Documents/baby_oclock` (Recommended)

**Critical Data:**
Ensure `feeds.xlsx` is the most up-to-date version from your current Mac.

### 1.3 Install Python Dependencies
```bash
cd ~/Documents/baby_oclock
pip3 install -r requirements.txt
```

---

## Phase 2: Configure App Auto-Start (LaunchAgent)

On the **NEW** machine, we want the app to start automatically when the computer turns on (and logs in).

1.  **Create a LaunchAgent plist:**
    *   Change `YOUR_USER` to your actual username on the new Mac.

```bash
# Create the file
nano ~/Library/LaunchAgents/com.nicholaskanhai.babyoclock.plist
```

2.  **Paste this content:**
    *   *Note: Update the paths to match where you put the folder!*

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nicholaskanhai.babyoclock</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/Users/YOUR_USER/Documents/baby_oclock/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/baby_oclock.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/baby_oclock.err</string>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USER/Documents/baby_oclock</string>
</dict>
</plist>
```

3.  **Load the Service:**
```bash
launchctl load ~/Library/LaunchAgents/com.nicholaskanhai.babyoclock.plist
```
*(The app should now be running on port 8080).*

---

## Phase 3: Migrate Cloudflare Tunnel

We will move the **existing** tunnel credentials so you don't have to re-configure DNS or Cloudflare dashboards.

### 3.1 Transfer Credentials
Locate these files on your **OLD** Mac:
*   `/etc/cloudflared/config.yml` (or `~/.cloudflared/config.yml`)
*   `/Users/nicholaskanhai/.cloudflared/<UUID>.json` (The credentials file)

Copy them to the **NEW** Mac. Place them in a temporary folder first, e.g., `~/Downloads/tunnel_transfer/`.

### 3.2 Install Credentials on New Mac
```bash
# Create system directory
sudo mkdir -p /etc/cloudflared

# Move config and credentials
sudo cp ~/Downloads/tunnel_transfer/config.yml /etc/cloudflared/
sudo cp ~/Downloads/tunnel_transfer/*.json /etc/cloudflared/
```

### 3.3 Verify Token Path
Open `/etc/cloudflared/config.yml` on the new Mac.
```bash
sudo nano /etc/cloudflared/config.yml
```
**Important:** Ensure `credentials-file` points to `/etc/cloudflared/<UUID>.json` (update the path if it still points to `/Users/...`).

### 3.4 Install Cloudflared Service
Use the manual plist method that worked on the old machine.

1.  **Create the Plist:**
```bash
sudo tee /Library/LaunchDaemons/com.cloudflare.cloudflared.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>com.cloudflare.cloudflared</string>
		<key>ProgramArguments</key>
		<array>
			<string>/opt/homebrew/bin/cloudflared</string>
			<string>tunnel</string>
			<string>--config</string>
			<string>/etc/cloudflared/config.yml</string>
			<string>run</string>
		</array>
		<key>RunAtLoad</key>
		<true/>
		<key>KeepAlive</key>
		<dict>
			<key>SuccessfulExit</key>
			<false/>
		</dict>
	</dict>
</plist>
EOF
```

2.  **Load the Service:**
```bash
sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

---

## Phase 4: Decommission Old Machine (This Machine)

**Only do this once the New Machine is working!**

Run these commands in Terminal on the **OLD** Mac to stop it from fighting for the connection.

### 4.1 Stop and Uninstall Tunnel
```bash
# Unload the service
sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist

# Remove the plist
sudo rm /Library/LaunchDaemons/com.cloudflare.cloudflared.plist

# (Optional) Remove credentials if you want to clean up
# sudo rm -rf /etc/cloudflared
```

### 4.2 Stop the App
If you are running the python app manually in a terminal, just press `Ctrl+C`.
If you had a launch agent for it, unload it similarly to step 4.1.

---

## Testing

1.  Reboot the **NEW** Server.
2.  Wait 2 minutes.
3.  Visit `https://baby.nicholaskanhai.com`.
4.  If it loads, **Success!** You have successfully migrated.
