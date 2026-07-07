#!/bin/bash
# Connect to Loomo via ADB over WiFi

LOOMO_IP="${1:-192.168.42.129}"
LOOMO_PORT="${2:-5555}"

echo "Connecting to Loomo at $LOOMO_IP:$LOOMO_PORT..."

# Check if ADB is installed
if ! command -v adb &> /dev/null; then
    echo "ERROR: ADB not found. Install with: sudo apt install android-tools-adb"
    exit 1
fi

# Connect
adb connect "$LOOMO_IP:$LOOMO_PORT"

# Check connection
adb devices

# Get Loomo info
echo ""
echo "=== Loomo Device Info ==="
adb -s "$LOOMO_IP:$LOOMO_PORT" shell getprop ro.product.model
adb -s "$LOOMO_IP:$LOOMO_PORT" shell getprop ro.build.version.release
echo ""
echo "=== Battery Level ==="
adb -s "$LOOMO_IP:$LOOMO_PORT" shell dumpsys battery | grep level
echo ""

echo "Connected! You can now run Python scripts."
