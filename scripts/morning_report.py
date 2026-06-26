#!/usr/bin/env python3
"""
Morning Report — Daily system summary for Talos
Runs at 08:00 via cron. Gathers weather, system health, and project status.
Output is plain-text, suitable for Telegram delivery.
"""

import os
import sys
import time
import json
import urllib.request
from datetime import datetime
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
CACHE_DIR = os.path.expanduser("~/.cache/reginald-daily")
STATE_PATH = os.path.join(CACHE_DIR, "state.json")


def get_uptime():
    """Return human-readable uptime."""
    try:
        s = float(open("/proc/uptime").read().split()[0])
        d = int(s // 86400)
        h = int((s % 86400) // 3600)
        m = int((s % 3600) // 60)
        return f"{d}d {h}h {m}m"
    except:
        return "unknown"


def get_load():
    """Return load averages."""
    try:
        parts = open("/proc/loadavg").read().split()[:3]
        return " ".join(parts)
    except:
        return "unknown"


def get_memory():
    """Return memory summary line."""
    try:
        lines = open("/proc/meminfo").readlines()
        total = int([l for l in lines if "MemTotal" in l][0].split()[1]) // 1024
        avail = int([l for l in lines if "MemAvailable" in l][0].split()[1]) // 1024
        used = total - avail
        pct = int((used / total) * 100)
        return f"{used}M / {total}M ({pct}%)"
    except:
        return "unknown"


def get_disk(path="/"):
    """Return disk usage for a path."""
    try:
        import shutil
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        pct = int((usage.used / usage.total) * 100)
        return f"{used_gb:.1f}G / {total_gb:.1f}G ({pct}%)"
    except:
        return "unknown"


def get_pi_temp():
    """Return Pi CPU temp in °C."""
    try:
        t = float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
        return f"{t:.0f}°C"
    except:
        return "unknown"


def get_weather():
    """Get current weather for Walling, TN."""
    try:
        url = "https://wttr.in/Walling+TN?format=%C+%t+%h+%w&u"
        r = urllib.request.urlopen(url, timeout=5)
        return r.read().decode().strip()
    except:
        return "unavailable"


def get_forecast_today():
    """Get short forecast summary."""
    try:
        url = "https://wttr.in/Walling+TN?format=3&u"
        r = urllib.request.urlopen(url, timeout=5)
        return r.read().decode().strip()
    except:
        return ""


def get_top_processes(n=5):
    """Return top CPU processes."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["ps", "-eo", "pcpu,comm", "--sort=-pcpu", "--no-headers"],
            text=True, timeout=5
        )
        lines = out.strip().split("\n")[:n]
        return ", ".join(
            f"{l.split()[1]}:{l.split()[0]}%"
            for l in lines if len(l.split()) >= 2
        )
    except:
        return "unknown"


def get_reginald_status():
    """Check if Reginald daily art was generated today."""
    try:
        if os.path.exists(STATE_PATH):
            state = json.load(open(STATE_PATH))
            if state.get("date") == datetime.now().strftime("%Y-%m-%d"):
                return "✅ Today's cartoon ready"
        return "❌ Not yet generated"
    except:
        return "unknown"


def get_tailscale_peers():
    """Count online tailscale peers."""
    try:
        import subprocess
        out = subprocess.check_output(["tailscale", "status"], text=True, timeout=5)
        lines = out.strip().split("\n")
        online = sum(1 for l in lines if l and "offline" not in l)
        total = len(lines)
        return f"{online}/{total} online"
    except:
        return "unknown"


def get_ollama_status():
    """Check if ollama is running and which model is loaded."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["systemctl", "is-active", "ollama"], text=True, timeout=3
        )
        return f"ollama: {out.strip()}"
    except:
        return "ollama: inactive"


def get_nvme_status():
    """Check NVMe drive status."""
    try:
        import shutil
        usage = shutil.disk_usage("/mnt/nvme")
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        pct = int((usage.used / usage.total) * 100)
        return f"{used_gb:.1f}G / {total_gb:.1f}G ({pct}%)"
    except:
        return "not mounted"


def main():
    now = datetime.now()
    report_date = now.strftime("%A, %B %d, %Y")

    lines = []
    lines.append(f"☀️ Morning Report — {report_date}")
    lines.append("")
    lines.append(f"🌤 Weather: {get_weather()}")
    forecast = get_forecast_today()
    if forecast:
        lines.append(f"   Forecast: {forecast}")
    lines.append("")
    lines.append("⚙️ System Health")
    lines.append(f"   Uptime: {get_uptime()}  |  Load: {get_load()}")
    lines.append(f"   RAM: {get_memory()}  |  Temp: {get_pi_temp()}")
    lines.append(f"   Root: {get_disk('/')}  |  NVMe: {get_nvme_status()}")
    lines.append(f"   Top CPU: {get_top_processes()}")
    lines.append("")
    lines.append("🔗 Services")
    lines.append(f"   {get_ollama_status()}  |  Tailscale: {get_tailscale_peers()}")
    lines.append(f"   Reginald: {get_reginald_status()}")
    lines.append("")
    lines.append("💡 Projects & Notes")
    lines.append("   Pi 5 | Kernel 6.18 | ZRAM swap (zstd)")
    lines.append("   Syncthing | pironman5-service | tailscaled")
    lines.append("")
    lines.append("Have a great day, Patticus! 🦞")

    report = "\n".join(lines)
    print(report)
    return report


if __name__ == "__main__":
    main()
