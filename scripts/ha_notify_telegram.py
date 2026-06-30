#!/usr/bin/env python3
"""Send HA check report to Telegram via bot API."""
import json, os, sys, datetime, urllib.request, urllib.error
from pathlib import Path

REPORT_FILE = Path(__file__).with_suffix(".state.json")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        print("⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT not set")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=15)
        print("✅ Telegram sent")
    except urllib.error.HTTPError as e:
        print(f"❌ Telegram error HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def main():
    from pathlib import Path
    if not REPORT_FILE.exists():
        print("ℹ️ No HA report state file found, skipping Telegram")
        return
    with open(REPORT_FILE) as f:
        report = json.load(f)
    # Only send if there are alerts
    alerts = report.get("alerts", [])
    if not alerts:
        # Optionally send a clean "all good" message — keep quiet by default
        print("ℹ️ No alerts — skipping Telegram")
        return
    text = "⚠️ Home Assistant Alert\n" + "\n".join(alerts)
    send_telegram(text)

if __name__ == "__main__":
    from pathlib import Path
    main()