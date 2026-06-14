# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Home Assistant Health Check
- Run: /home/patrick/.openclaw/workspace/scripts/ha_monitor.sh
- Report alerts via Telegram if any found
- Track: unavailable entities, Victron status, Spoolman status
