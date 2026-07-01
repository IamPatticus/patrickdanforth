# Heartbeat - OpenClaw

## Last Checks
- **lastChecked**: 2026-07-01 11:49 UTC
- **heartbeat**: OK — gateway responding, cron active with 8 jobs.
- **nextWakeAt**: 2026-07-01 12:19 UTC
- **pollResult**: OK, no urgent items.

## Quick Status
- **Uptime**: gateway 13h 10m · system 20h 44m
- **Model**: ollama/kimi-k2.7-code:cloud
- **Cron**: 8 jobs enabled; 7 ok, 1 error
- **`update_memory`**: ✅ **Verified fixed** — manually forced run completed OK, MEMORY.md updated, delivery delivered via Telegram fallback. Next scheduled run 2026-07-02 00:00 UTC.
- **`Rockin Regi Weekly Comic`**: Still `error` from 3d ago. Not due until 2026-07-05 11:00 UTC (~4 days). **Monitor before next run.**
- **`Reginald Daily Generation`**: July 1st run agent-completed but image gen failed (OpenRouter 402). No July 1st comic. Next run 2026-07-02 06:00 UTC (~19h).
- **Queue**: steer (depth 0)
- **Active sessions**: 0
- **Git**: MEMORY.md and heartbeat updates committed.

## Notes
- `openclaw_heartbeat` runs every 30m; last run 11:19 UTC, next 11:49 UTC.
- `ollama_keepalive_serenity` runs every ~2m; next ~11:21 UTC.
- `Ikaris Nightly` last OK; next run 2026-07-01 15:00 UTC (~5h).
- `Memory Dreaming Promotion` next run 2026-07-02 03:00 UTC (~17h).
- `Daily GitHub Backup` next run 2026-07-02 04:00 UTC (~18h).
- Weather/email/calendar handled by separate 4h cron; not checked in this heartbeat.
- Fallback model list still includes stale/depleted `ollama-cloud` providers after `ollama-cloud/kimi-k2.6:cloud` 404 and OpenRouter 402. Consider trimming to local Ollama models only until credits are restored.

## System
- Load: 0.19 0.15 0.17 (1/5/15m)
- RAM: 1.8 Gi used / 7.7 Gi total (5.9 Gi available incl. cache)
- Swap: 30 Mi used / 4.0 Gi total
- Disk `/`: 36G used / 57G total (66%)

## Upcoming Cron Runs
- `ollama_keepalive_serenity`: ~11:21 UTC (next ~2 min)
- `openclaw_heartbeat`: 11:49 UTC (~30 min)
- `Ikaris Nightly`: 15:00 UTC (~4 h)
- `update_memory`: 2026-07-02 00:00 UTC (~13 h) — **watch this one**
- `Memory Dreaming Promotion`: 2026-07-02 03:00 UTC (~16 h)
- `Daily GitHub Backup`: 2026-07-02 04:00 UTC (~17 h)
- `Reginald Daily Generation`: 2026-07-02 06:00 UTC (~19 h)
- `Rockin Regi Weekly Comic`: 2026-07-05 11:00 UTC (4 days)

## Next Planned Checks
- ✅ `update_memory` delivery verified fixed.
- Inspect `Rockin Regi Weekly Comic` before 2026-07-05.
- Decide whether to fund OpenRouter or switch Reginald image gen to a non-paid fallback.
- Trim `agents.defaults.model.fallbacks` to remove failing providers (ollama-cloud, OpenRouter, OpenAI).

## Commands
- `session_status` — show runtime details
- `openclaw cron list` — cron health
- `sessions_list` — active sessions
