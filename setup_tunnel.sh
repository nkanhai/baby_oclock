#!/bin/bash
set -e

# Ensure we have sudo
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo)"
  exit 1
fi

echo "=== Configuring Cloudflare Tunnel ==="

# 1. Setup directory
if [ ! -d "/etc/cloudflared" ]; then
    echo "Creating /etc/cloudflared..."
    mkdir -p /etc/cloudflared
fi

# 2. Copy credentials
echo "Copying credentials from ~/Downloads/tunnel_transfer/..."
# Remove old credentials if they exist to avoid confusion
rm -f /etc/cloudflared/*.json /etc/cloudflared/config.yml
cp /Users/nicholaskanhai/Downloads/tunnel_transfer/* /etc/cloudflared/

# 3. Update paths in config.yml (if they point to user home)
echo "Updating config paths..."
sed -i '' 's|/Users/nicholaskanhai/.cloudflared/|/etc/cloudflared/|g' /etc/cloudflared/config.yml

# 4. Create LaunchDaemon
echo "Creating LaunchDaemon..."
cat <<EOF > /Library/LaunchDaemons/com.cloudflare.cloudflared.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>com.cloudflare.cloudflared</string>
		<key>ProgramArguments</key>
		<array>
			<string>/usr/local/bin/cloudflared</string>
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
        <key>StandardOutPath</key>
        <string>/tmp/cloudflared.out</string>
        <key>StandardErrorPath</key>
        <string>/tmp/cloudflared.err</string>
	</dict>
</plist>
EOF

# 5. Load service
echo "Loading service..."
launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist 2>/dev/null || true
launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist

echo "=== Done! Cloudflare Tunnel service installed & started. ==="
echo "You can check status with: sudo launchctl list | grep cloudflare"
