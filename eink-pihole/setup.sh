#!/bin/bash
# E-Ink Pi-hole Display Setup for Raspberry Pi Zero 2 W + Waveshare 2.13" V4 HAT
# Run this on the Pi directly.

set -e

PIHOLE_IP="${PIHOLE_IP:-192.168.1.203}"

echo "== E-Ink Pi-hole Display Setup =="
echo "Target Pi-hole: $PIHOLE_IP"

# Update and install dependencies
echo "[1/6] Updating packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-pil libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev libwebp-dev libharfbuzz-dev libfribidi-dev git

# Create venv
echo "[2/6] Creating Python venv..."
python3 -m venv ~/eink-pihole/venv
source ~/eink-pihole/venv/bin/activate

# Install Python deps
echo "[3/6] Installing Python packages..."
pip install --upgrade pip
pip install pillow requests waveshare-epd

# SPI enable
echo "[4/6] Enabling SPI..."
sudo raspi-config nonint do_spi 0

# Create password file (user must edit)
echo "[5/6] Creating config..."
if [ ! -f ~/eink-pihole/.pihole_pass ]; then
  echo "changeme" > ~/eink-pihole/.pihole_pass
  chmod 600 ~/eink-pihole/.pihole_pass
  echo "    Created ~/eink-pihole/.pihole_pass with placeholder password."
  echo "    EDIT THIS FILE to match your Pi-hole web admin password."
else
  echo "    ~/eink-pihole/.pihole_pass already exists."
fi

# Copy scripts
echo "[6/6] Installing scripts..."
mkdir -p ~/eink-pihole
if [ -f display.py ]; then cp display.py ~/eink-pihole/display.py; fi
if [ -f pihole_client.py ]; then cp pihole_client.py ~/eink-pihole/pihole_client.py; fi
if [ -f run.sh ]; then cp run.sh ~/eink-pihole/run.sh && chmod +x ~/eink-pihole/run.sh; fi
if [ -f eink-pihole.service ]; then
  sudo cp eink-pihole.service /etc/systemd/system/eink-pihole.service
  sudo sed -i "s/%%USER%%/${USER}/g" /etc/systemd/system/eink-pihole.service
  echo "    systemd service installed."
fi
if [ -f eink-pihole.timer ]; then
  sudo cp eink-pihole.timer /etc/systemd/system/eink-pihole.timer
  sudo systemctl daemon-reload
  sudo systemctl enable eink-pihole.service
  sudo systemctl enable eink-pihole.timer
  echo "    systemd timer installed and enabled (refresh every 60 minutes)."
fi

echo ""
echo "Setup complete. Next steps:"
echo "  1. Edit ~/eink-pihole/.pihole_pass with your Pi-hole password."
echo "  2. Run ~/eink-pihole/run.sh to test the display."
echo "  3. Start the service: sudo systemctl start eink-pihole"
echo ""
echo "You may need to reboot for SPI changes to take full effect."
