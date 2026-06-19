#!/usr/bin/env python3
"""Generate vitals.json for Mission Control dashboard."""
import json, subprocess, os, time

DEST = "/var/www/mission-control/vitals.json"

out = {"ts": int(time.time())}

# --- System uptime ---
try:
    with open("/proc/uptime") as f:
        secs = int(float(f.read().split()[0]))
        out["uptime"] = f"{secs // 3600}h {(secs % 3600) // 60}m"
except Exception:
    out["uptime"] = "—"

# --- Load ---
load = subprocess.run(["uptime"], capture_output=True, text=True).stdout
parts = load.strip().split("load average:")
out["load"] = parts[1].strip().split(",")[0] if len(parts) > 1 else "—"

# --- Memory ---
mem = subprocess.run(["free", "-h"], capture_output=True, text=True).stdout
for line in mem.splitlines():
    if line.startswith("Mem:"):
        out["mem"] = line.split()[-1].replace('i','') + " avail"
        break

# --- Disk ---
disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True).stdout
for line in disk.splitlines():
    if line.startswith("/"):
        bits = line.split()
        out["disk"] = bits[3] + " free"
        out["disk_used_pct"] = bits[4]
        break

# --- Gateway health ---
try:
    import urllib.request
    req = urllib.request.Request("http://localhost:18790/health")
    resp = urllib.request.urlopen(req, timeout=3)
    health = json.loads(resp.read())
    out["gateway_ok"] = health.get("ok", False)
except Exception:
    out["gateway_ok"] = False

# --- Caddy status ---
try:
    out["caddy"] = subprocess.run(["systemctl", "is-active", "caddy"], capture_output=True, text=True).stdout.strip()
except Exception:
    out["caddy"] = "unknown"

# --- Tailscale ---
try:
    ts = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True, timeout=5)
    if ts.returncode == 0:
        out["tailscale_ok"] = json.loads(ts.stdout).get("Self", {}).get("Online", False)
    else:
        out["tailscale_ok"] = False
except Exception:
    out["tailscale_ok"] = False

# --- Docker containers ---
try:
    dock = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True, timeout=5)
    out["containers"] = len(dock.stdout.strip().splitlines()) if dock.stdout.strip() else 0
except Exception:
    out["containers"] = "—"

with open(DEST, "w") as f:
    json.dump(out, f, indent=2)
print(f"Wrote {DEST}")
