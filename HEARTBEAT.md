# Heartbeat Checklist

Rotate through 2-4 checks per heartbeat.

- [x] Email — covered by `weather-email-calendar-check` cron every 4h; no local mail tool
- [x] Calendar — covered by `weather-email-calendar-check` cron every 4h; reports 0 events next 48h
- [x] Weather — covered by `weather-email-calendar-check` cron every 4h; see WEATHER.md/weather.md
- [x] Git — workspace has routine uncommitted changes in `memory/.dreams/events.jsonl`, `memory/heartbeat-state.json`, and `scripts/venus_mqtt_bridge.py`; untracked `services/trmnl-plugins/`
- [x] Memory — `memory_search` works via FTS/BM25 (provider: none); reviewed daily notes/MEMORY.md, nothing to promote
- [x] Disk/health — disk 62% used, load 0.74/0.36/0.23, mem 1.8G used / 5.9G avail, routine

## Reach Out When

- Important email arrives
- Calendar event <2h away
- Something interesting found
- >8h since last message

## Stay Quiet When

- Late night (23:00-08:00) unless urgent
- Human clearly busy
- Nothing new since last check
- Checked <30 min ago