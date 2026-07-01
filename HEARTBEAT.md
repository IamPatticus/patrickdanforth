# Heartbeat - OpenClaw

## Last Checks
- **lastChecked**: 2026-07-01 10:21 UTC
- **heartbeat**: OK — gateway responding, cron active with 8 jobs.
- **nextWakeAt**: 2026-07-01 10:42 UTC (openclaw_heartbeat)
- **pollResult**: OK, no urgent items.

## Quick Status
- **Uptime**: gateway 12h 19m · system 19h 53m
- **Model**: ollama/kimi-k2.7-code:cloud
- **Cron**: 8 jobs enabled; 6 ok, 2 error
- **`update_memory`**: Still `error` — delivery configured as Telegram `8284391571`, but dispatcher enforces Signal target validation. Next run 2026-07-02 00:00 UTC in ~14h. **Still needs attention.**
- **`Rockin Regi Weekly Comic`**: Still `error` from 3d ago (agent generated no response). Not due until 2026-07-05 11:00 UTC (~4 days). **Monitor before next run.**
- **`Reginald Daily Generation`**: July 1st 06:00 UTC run completed agent side, but image generation failed with OpenRouter HTTP 402 (depleted credits). No comic for July 1st. Next run 2026-07-02 06:00 UTC (~20h).
- **Queue**: steer (depth 0)
- **Active sessions**: 0
- **Git**: 4 files modified, last commit 07:27 UTC — will commit this heartbeat update.

## Notes
- `openclaw_heartbeat` runs every 30m; last run 09:42 UTC, next 10:12 UTC.
- `Ikaris Nightly` last OK; next run 2026-07-01 15:00 UTC (~5h).
- `Memory Dreaming Promotion` next run 2026-07-02 03:00 UTC (~17h).
- `Daily GitHub Backup` next run 2026-07-02 04:00 UTC (~18h).
- Weather/email/calendar handled by separate 4h cron; not checked in this heartbeat.
- Fallback model list still includes stale/depleted `ollama-cloud` providers after `ollama-cloud/kimi-k2.6:cloud` 404 and OpenRouter 402. Consider trimming to local Ollama models only until credits are restored.

## System
- Load: 0.07 / 0.11 / 0.09
- RAM: 1.7Gi used / 7.7Gi total, 6.0Gi available
- Swap: 30Mi used / 4.0Gi total
- Disk `/`: 36G used / 57G total (66%)

## Upcoming Cron Runs
- `openclaw_heartbeat`: 10:12 UTC (next ~17 min)
- `Ikaris Nightly`: 15:00 UTC (~5 h)
- `update_memory`: 2026-07-02 00:00 UTC (~14 h) — **watch this one**
- `Memory Dreaming Promotion`: 2026-07-02 03:00 UTC (~17 h)
- `Daily GitHub Backup`: 2026-07-02 04:00 UTC (~18 h)
- `Reginald Daily Generation`: 2026-07-02 06:00 UTC (~20 h)
- `Rockin Regi Weekly Comic`: 2026-07-05 11:00 UTC (4 days)

## Next Planned Checks
- Verify `update_memory` delivery succeeds at next run or escalate the Telegram-vs-Signal dispatcher issue.
- Re-run / inspect `Rockin Regi Weekly Comic` before its scheduled run on 2026-07-05.
- Decide whether to add OpenRouter credits or switch Reginald Daily image generation to a non-paid fallback.
- Trim `agents.defaults.model.fallbacks` to remove providers that currently fail (ollama-cloud, OpenRouter, OpenAI).

## Commands
- `session_status` — show runtime details
- `openclaw cron list` — cron health
- `sessions_list` — active sessions
