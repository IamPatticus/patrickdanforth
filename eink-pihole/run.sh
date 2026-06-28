#!/bin/bash
# Run the E-Ink Pi-hole display once.
set -e
cd "$(dirname "$0")"
export PIHOLE_URL="${PIHOLE_URL:-http://192.168.1.203}"
./venv/bin/python3 display.py
