#!/bin/bash
# Script to link signal-cli to your Signal account

echo "Starting Signal device linking process..."
echo "You will need your Signal app on your phone ready."
echo ""
echo "When prompted, open Signal on your phone:"
echo "Settings -> Linked Devices -> Link New Device"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Run signal-cli link and output the QR code as text
signal-cli link -n "Talos" &
LINK_PID=$!

# Wait for the link data
sleep 2

echo ""
echo "If no QR code appeared above, try running this manually:"
echo "  signal-cli link -n 'Talos'"
echo ""
echo "Or use this command to get a device link URI:"
echo "  signal-cli link -n 'Talos' --qr-code-format text"
echo ""

wait $LINK_PID 2>/dev/null
