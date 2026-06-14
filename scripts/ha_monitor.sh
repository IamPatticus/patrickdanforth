#!/usr/bin/env bash
# Source env and run HA monitor
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load .env.local if present
if [ -f .env.local ]; then
    export $(grep -v '^#' .env.local | xargs 2>/dev/null || true)
fi

exec python3 scripts/ha_monitor.py
