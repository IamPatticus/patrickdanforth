# Solar / Victron TRMNL Plugin

FastAPI service that serves live solar/Victron summary screens to TRMNL devices.

## Run locally

```bash
cd services/trmnl-plugins/solar
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn python-multipart
python app.py
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Human landing page |
| POST | `/install` | TRMNL install handshake |
| POST | `/markup` | Screen markup (called every refresh) |
| GET | `/manage` | Plugin management page |
| POST | `/uninstall` | Uninstall webhook |

## TRMNL plugin registration

Visit `https://trmnl.com/plugins/my/new` and use:

- **Installation URL**: `https://YOUR_HOST/install`
- **Plugin Markup URL**: `https://YOUR_HOST/markup`
- **Plugin Management URL**: `https://YOUR_HOST/manage`
- **Uninstallation Webhook URL**: `https://YOUR_HOST/uninstall`

# Solar / Victron TRMNL Plugin (Private)

FastAPI service that serves live solar/Victron summary screens to a private
TRMNL BYOD plugin. No public internet, no OAuth install flow.

## Run locally

```bash
cd services/trmnl-plugins/solar
python3 -m uvicorn app:app --host 127.0.0.1 --port 8123 --reload
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Human landing page |
| POST | `/markup` | Screen markup (called every TRMNL refresh) |
| GET | `/health` | Data freshness + current values |

## Data source

Reads `/var/www/venus/venus-mqtt.json` written by `venus_mqtt_bridge.py`.
That bridge connects to multiple Venus OS MQTT brokers (house + shop Cerbo GX),
listens to the full Victron topic tree, and writes a merged JSON file.

## Tailscale Serve setup (private)

Add a route on `serenity` so TRMNL's servers can reach the plugin over your
Tailnet:

```bash
tailscale serve --https=443 --set-path=/trmnl-solar --bg http://127.0.0.1:8123
```

Then in TRMNL, create a **Private Plugin** and set the Markup URL to:

```
https://serenity.tail4695cd.ts.net/trmnl-solar/markup
```

If you want a cleaner subdomain instead of a path, use:

```bash
tailscale serve --https=443 --bg 8123
```

Then the URL is `https://serenity.tail4695cd.ts.net/markup`.

## systemd services

Two services are provided:

- `venus-mqtt-bridge.service` — collects data from Venus OS MQTT brokers
- `trmnl-solar.service` — serves the FastAPI app

Install:

```bash
sudo cp venus-mqtt-bridge.service trmnl-solar.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now venus-mqtt-bridge
sudo systemctl enable --now trmnl-solar
```

## Silicon Power backup

Mirrored at `/mnt/siliconpower/Solar/trmnl-plugin/solar/`.

Keep in sync:

```bash
rsync -a /home/patrick/.openclaw/workspace/services/trmnl-plugins/solar/ /mnt/siliconpower/Solar/trmnl-plugin/solar/
```

## TODO

- [ ] Confirm house Cerbo GX MQTT broker host in `venus_mqtt_bridge.py`
- [ ] Start both systemd services
- [ ] Configure Tailscale Serve route
- [ ] Create Private Plugin in TRMNL with the Tailscale URL
- [ ] Verify live data appears on TRMNL BYOD device
