#!/bin/bash
# Quick connectivity test for Baby Feed Tracker

echo "🔍 Baby Feed Tracker - Connectivity Test"
echo "=========================================="
echo ""

# Get IP address
if command -v ipconfig &> /dev/null; then
    # macOS
    IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
else
    # Linux
    IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$IP" ]; then
    echo "❌ Could not determine local IP address"
    exit 1
fi

echo "✅ Local IP: $IP"
echo ""

# Check if server is running
PORT=8080
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Server is running on port $PORT"
else
    echo "❌ Server is NOT running on port $PORT"
    echo "   Run: ./start.sh"
    exit 1
fi
echo ""

# Test local access
echo "Testing local access..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/ | grep -q "200"; then
    echo "✅ Local access works (http://localhost:$PORT)"
else
    echo "❌ Local access failed"
fi
echo ""

# Test network access
echo "Testing network access..."
if curl -s -o /dev/null -w "%{http_code}" http://$IP:$PORT/ | grep -q "200"; then
    echo "✅ Network access works (http://$IP:$PORT)"
else
    echo "⚠️  Network access may be blocked by firewall"
fi
echo ""

# Check firewall on macOS
if [ "$(uname)" == "Darwin" ]; then
    echo "Checking macOS Firewall..."
    if /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -q "enabled"; then
        echo "⚠️  Firewall is ENABLED"
        echo "   You may need to allow Python in:"
        echo "   System Settings → Network → Firewall → Options"
        echo "   Add Python and set to 'Allow incoming connections'"
    else
        echo "✅ Firewall is disabled"
    fi
    echo ""

    # Check for AirPlay Receiver (which uses port 5000)
    echo "Checking AirPlay Receiver..."
    if defaults read com.apple.NetworkServices AirPlayReceiver 2>/dev/null | grep -q "Enabled = 1"; then
        echo "ℹ️  AirPlay Receiver is enabled (uses port 5000)"
        echo "   This app uses port $PORT to avoid conflicts"
    fi
fi

echo ""
echo "=========================================="
echo "📱 URL to use on your phone:"
echo "   http://$IP:$PORT"
echo ""
echo "💡 Troubleshooting tips:"
echo "   1. Make sure phone is on same WiFi"
echo "   2. Update bookmark to use :$PORT (not :5000)"
echo "   3. If blocked, allow Python in Firewall settings"
echo "   4. Try disabling firewall temporarily to test"
echo "=========================================="
