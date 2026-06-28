# E-Ink Pi-hole Display

Status screen for a Raspberry Pi Zero 2 W + Waveshare 2.13" E-Ink HAT V4, showing stats from a local Pi-hole v6 instance.

## Hardware

- Raspberry Pi Zero 2 W
- Waveshare 2.13inch E-Ink Display HAT V4 (250x122, black/white, SPI)

## Install on the Pi

```bash
cd ~
git clone https://github.com/IamPatticus/patrickdanforth.git patrickdanforth
cd patrickdanforth/eink-pihole
chmod +x setup.sh
./setup.sh
```

Then edit the Pi-hole password file:

```bash
nano ~/eink-pihole/.pihole_pass
```

Replace `changeme` with your Pi-hole web admin password.

## Test the display

```bash
~/eink-pihole/run.sh
```

## Run automatically

The setup script installs a systemd service. Start it:

```bash
sudo systemctl start eink-pihole
```

To refresh every 5 minutes, add a cron job:

```bash
crontab -e
```

Add:

```
*/5 * * * * /home/pi/eink-pihole/run.sh
```

## Config

- `PIHOLE_URL` — base URL of the Pi-hole instance (default: `http://192.168.1.203`)
- `~/eink-pihole/.pihole_pass` — Pi-hole web admin password (chmod 600)

## Notes

- Pi-hole v6 API is used (`/api/stats/summary`).
- E-Ink full refresh takes ~2 seconds.
- The script creates a debug PNG if the E-Ink update fails.
