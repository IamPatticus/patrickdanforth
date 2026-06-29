# Heartbeat Checklist

Rotate through 2-4 checks per heartbeat.

- [x] Email — covered by `weather-email-calendar-check` cron every 4h; no local mail tool
- [x] Calendar — covered by `weather-email-calendar-check` cron every 4h; reports 0 events next 48h
- [x] Weather — covered by `weather-email-calendar-check` cron every 4h; see WEATHER.md/weather.md
- [x] Git — workspace has routine uncommitted changes in `DREAM_DIARY.md`, `memory/.dreams/events.jsonl`, and `memory/heartbeat-state.json`
- [ ] Memory — `memory_search` now works via FTS/BM25 (provider: none); reviewed daily notes/MEMORY.md, nothing to promote
- [ ] Disk/health — disk 61% used, load ~0.10, routine

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