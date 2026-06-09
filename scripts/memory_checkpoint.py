#!/usr/bin/env python3
"""
memory_checkpoint.py — Aggressive session checkpointing

Run this periodically (cron every 30 min or heartbeat) to:
1. Verify today's daily note exists
2. Check that MEMORY.md was updated within last 7 days
3. Summarize current session state to a temp backup file
4. Alert if memory health looks bad
"""

import os
import sys
import json
import datetime

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
DAILY_FMT = "%Y-%m-%d.md"
STATE_FILE = os.path.join(MEMORY_DIR, "checkpoint-state.json")
ALERT_FILE = os.path.join(MEMORY_DIR, ".memory-alert")


def today_str():
    return datetime.datetime.now().strftime(DAILY_FMT)


def file_age_days(path):
    if not os.path.exists(path):
        return 999
    mtime = os.path.getmtime(path)
    return (
        datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)
    ).total_seconds() / 86400


def check_daily_note():
    today_file = os.path.join(MEMORY_DIR, today_str())
    if os.path.exists(today_file):
        age_hours = file_age_days(today_file) * 24
        return True, f"Daily note exists ({age_hours:.1f}h old): {today_file}"
    return False, f"MISSING: {today_file}"


def check_memory_md():
    mm = os.path.join(WORKSPACE, "MEMORY.md")
    age = file_age_days(mm)
    if age < 7:
        return True, f"MEMORY.md updated {age:.1f} days ago"
    return False, f"STALE: MEMORY.md not updated in {age:.1f} days"


def check_working_context():
    wc = os.path.join(WORKSPACE, "vault", "Agent-Talos", "working-context.md")
    age = file_age_days(wc)
    if age < 3:
        return True, f"working-context.md updated {age:.1f} days ago"
    return False, f"STALE: working-context.md not updated in {age:.1f} days"


def write_checkpoint_state(checks):
    state = {
        "lastRun": datetime.datetime.now().isoformat(),
        "checks": checks,
        "allHealthy": all(c["ok"] for c in checks),
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    checks = []
    ok, msg = check_daily_note()
    checks.append({"name": "daily-note", "ok": ok, "msg": msg})
    ok, msg = check_memory_md()
    checks.append({"name": "memory-md", "ok": ok, "msg": msg})
    ok, msg = check_working_context()
    checks.append({"name": "working-context", "ok": ok, "msg": msg})

    write_checkpoint_state(checks)

    all_ok = all(c["ok"] for c in checks)
    if all_ok:
        # Clear any previous alert
        if os.path.exists(ALERT_FILE):
            os.remove(ALERT_FILE)
        print("OK: Memory health checks passed.")
        return 0
    else:
        # Write alert file for heartbeat to pick up
        alert = "\n".join(c["msg"] for c in checks if not c["ok"])
        with open(ALERT_FILE, "w") as f:
            f.write(alert)
        print(f"ALERT:\n{alert}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
