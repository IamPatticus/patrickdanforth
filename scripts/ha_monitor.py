#!/usr/bin/env python3
"""Home Assistant health monitor — check entity states and alert on problems."""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Config
HA_URL = os.environ.get("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.environ.get("HOME_ASSISTANT_TOKEN", "")
STATE_FILE = Path(__file__).with_suffix(".state.json")
ALERT_THRESHOLD_UNAVAILABLE = 200   # Alert if unavailable count jumps above this
ALERT_DELTA_UNAVAILABLE = 50       # Or if it jumps by 50+ from last check
ALERT_THRESHOLD_UNKNOWN = 120


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
    victron_down = sum(1 for e in unavailable if "victron" in e["entity_id"].lower())
    spoolman_down = sum(1 for e in unknown if "spoolman" in e["entity_id"].lower())

    prev = load_state()
    prev_unavailable = prev.get("unavailable_count", 0)
    prev_unknown = prev.get("unknown_count", 0)

    alerts = []
    if len(unavailable) >= ALERT_THRESHOLD_UNAVAILABLE:
        alerts.append(f"Unavailable entities HIGH: {len(unavailable)}")
    if len(unavailable) - prev_unavailable >= ALERT_DELTA_UNAVAILABLE:
        alerts.append(f"Unavailable entities jumped by {len(unavailable) - prev_unavailable} (now {len(unavailable)})")
    if len(unknown) >= ALERT_THRESHOLD_UNKNOWN:
        alerts.append(f"Unknown entities HIGH: {len(unknown)}")
    if victron_down >= 50 and prev.get("victron_down", 0) < 50:
        alerts.append(f"Victron connection DOWN: {victron_down} entities unavailable")
    if victron_down < 50 and prev.get("victron_down", 0) >= 50:
        alerts.append(f"Victron connection RESTORED")
    if spoolman_down >= 20 and prev.get("spoolman_down", 0) < 20:
        alerts.append(f"Spoolman connection DOWN: {spoolman_down} entities unknown")
    if spoolman_down < 20 and prev.get("spoolman_down", 0) >= 20:
        alerts.append(f"Spoolman connection RESTORED")

    # Summarize top unavailable domains
    from collections import Counter
    domains = Counter(e["entity_id"].split(".")[0] for e in unavailable)
    top_domains = domains.most_common(5)

    report = {
        "timestamp": json.dumps(None),  # placeholder
        "total": total,
        "unavailable_count": len(unavailable),
        "unknown_count": len(unknown),
        "victron_down": victron_down,
        "spoolman_down": spoolman_down,
        "top_unavailable_domains": top_domains,
        "alerts": alerts,
    }

    save_state(report)

    # Build readable output
    lines = [
        f"🏠 HA Check — {len(unavailable)} unavailable, {len(unknown)} unknown / {total} total",
    ]
    if top_domains:
        lines.append("Top unavailable: " + ", ".join(f"{d}:{c}" for d, c in top_domains))
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
