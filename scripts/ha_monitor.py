#!/usr/bin/env python3
"""Home Assistant health monitor — check entity states, filter noise, alert on real problems."""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from collections import Counter

# ── Load .env.local if present (for cron sessions) ───────────
ENV_LOCAL = Path(__file__).parent.parent / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if key.strip() and val:
                os.environ.setdefault(key.strip(), val)

# Config
HA_URL = os.environ.get("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.environ.get("HOME_ASSISTANT_TOKEN", "")
STATE_FILE = Path(__file__).with_suffix(".state.json")

# Fast-fail: bail immediately if no token
if not HA_TOKEN:
    print("⚠️ HOME_ASSISTANT_TOKEN not set — check .env.local or environment")
    sys.exit(1)

# Thresholds for alerting
ALERT_THRESHOLD_UNAVAILABLE = 200   # Alert if unavailable count jumps above this
ALERT_DELTA_UNAVAILABLE = 50       # Or if it jumps by 50+ from last check
ALERT_THRESHOLD_UNKNOWN = 120

# Noise filters — domains/integrations we expect to be flaky
NOISE_DOMAINS = {"media_player", "device_tracker"}
NOISE_PATTERNS = ["emby_", "govee_", "ruuvitag_", "gvh"]

# Known orphaned Victron entities that are dead in HA but can't be removed via UI
# These are system-level ESS settings that no longer exist on the GX device
VICTRON_ORPHANS = {
    "binary_sensor.victron_settings_ess_feedinpowerlimit",
    "sensor.victron_settings_ess_acpowersetpoint",
    "sensor.victron_settings_ess_acpowersetpoint2",
    "sensor.victron_settings_ess_feedinpowerlimit",
    "sensor.victron_settings_ess_maxchargecurrent",
    "sensor.victron_settings_ess_maxchargepercentage",
    "sensor.victron_settings_ess_maxdischargepercentage",
    "sensor.victron_settings_ess_maxdischargepower",
    "sensor.victron_settings_ess_maxfeedinpower",
    "sensor.victron_settings_ess_overvoltagefeedin",
    "sensor.victron_settings_ess_preventfeedback",
    "sensor.victron_settings_systemsetup_maxchargevoltage",
    "sensor.victronsettings_systemssetup_acinput1100",
    "sensor.victronsettings_systemssetup_acinput2100",
}

# Critical integrations — alert immediately if these drop
CRITICAL_INTEGRATIONS = ["victron"]
CRITICAL_VICTRON_THRESHOLD = 10   # Alert if 10+ Victron entities down


def api(path):
    url = f"{HA_URL}/api{path}"
    req = Request(url, headers={
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except HTTPError as e:
        return {"_error": f"HTTP {e.code}: {e.reason}"}
    except URLError as e:
        return {"_error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"_error": str(e)}


def is_noise_entity(entity):
    """Check if an entity is expected noise (offline clients, BLE beacons, etc.)"""
    eid = entity["entity_id"]
    domain = eid.split(".")[0]
    if domain in NOISE_DOMAINS:
        return True
    for pattern in NOISE_PATTERNS:
        if pattern in eid.lower():
            return True
    # Known orphaned Victron ESS settings that are dead but undeletable via HA UI
    if eid in VICTRON_ORPHANS:
        return True
    return False


def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check():
    states = api("/states")
    if isinstance(states, dict) and "_error" in states:
        msg = f"⚠️ Home Assistant unreachable: {states['_error']}"
        print(msg)
        return msg

    total = len(states)
    unavailable = [e for e in states if e.get("state") == "unavailable"]
    unknown = [e for e in states if e.get("state") == "unknown"]

    # Filter noise
    noise_unavailable = [e for e in unavailable if is_noise_entity(e)]
    real_unavailable = [e for e in unavailable if not is_noise_entity(e)]

    # Critical integration checks (filter known orphans)
    victron_unavailable = [e for e in unavailable if "victron" in e["entity_id"].lower() and not is_noise_entity(e)]

    prev = load_state()
    prev_unavailable = prev.get("unavailable_count", 0)
    prev_unknown = prev.get("unknown_count", 0)
    prev_real = prev.get("real_unavailable_count", 0)
    # Version field for state migration — skip delta alerts on first new-format run
    prev_version = prev.get("_version", 0)
    is_fresh_state = prev_version < 2

    alerts = []

    # Critical integration alerts
    if len(victron_unavailable) >= CRITICAL_VICTRON_THRESHOLD:
        alerts.append(f"🚨 Victron DOWN: {len(victron_unavailable)} entities unavailable — solar monitoring broken")

    # General thresholds
    if len(real_unavailable) >= ALERT_THRESHOLD_UNAVAILABLE:
        alerts.append(f"Unavailable entities HIGH: {len(real_unavailable)} (filtered: {len(noise_unavailable)})")
    if not is_fresh_state and (len(real_unavailable) - prev_real) >= ALERT_DELTA_UNAVAILABLE:
        alerts.append(f"Unavailable entities jumped by {len(real_unavailable) - prev_real} (now {len(real_unavailable)})")
    if len(unknown) >= ALERT_THRESHOLD_UNKNOWN:
        alerts.append(f"Unknown entities HIGH: {len(unknown)}")

    # Summarize top real unavailable domains
    real_domains = Counter(e["entity_id"].split(".")[0] for e in real_unavailable)
    top_domains = real_domains.most_common(5)

    report = {
        "_version": 2,
        "total": total,
        "unavailable_count": len(unavailable),
        "real_unavailable_count": len(real_unavailable),
        "noise_unavailable_count": len(noise_unavailable),
        "unknown_count": len(unknown),
        "victron_down": len(victron_unavailable),
        "top_unavailable_domains": top_domains,
        "alerts": alerts,
    }

    save_state(report)

    # Build readable output
    lines = [
        f"🏠 HA Check — {len(real_unavailable)} real unavailable, {len(noise_unavailable)} noise, {len(unknown)} unknown / {total} total",
    ]
    if top_domains:
        lines.append("Top real unavailable: " + ", ".join(f"{d}:{c}" for d, c in top_domains))
    if victron_unavailable:
        lines.append(f"  Victron: {len(victron_unavailable)} down")
    if alerts:
        lines.append("")
        lines.append("🚨 ALERTS:")
        for a in alerts:
            lines.append(f"  • {a}")

    output = "\n".join(lines)
    print(output)
    return output


if __name__ == "__main__":
    check()
