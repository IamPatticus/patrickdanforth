# Heartbeat - OpenClaw

## Last Checks
- **lastChecked**: 2026-07-01 10:57 UTC
- **heartbeat**: OK — gateway responding, cron active with 8 jobs.
- **nextWakeAt**: 2026-07-01 11:27 UTC
- **pollResult**: OK, no urgent items.

## Quick Status
- **Uptime**: gateway 12h 33m · system 20h 06m
- **Model**: ollama/kimi-k2.7-code:cloud
- **Cron**: 8 jobs enabled; 7 ok, 1 error
- **`update_memory`**: ✅ **Fixed** — delivery was resolved to Signal with no target. Forced the job delivery to `telegram:8284391571` and reset consecutive errors. Next run 2026-07-02 00:00 UTC in ~13h. Will verify tomorrow.
- **`Rockin Regi Weekly Comic`**: Still `error` from 3d ago (agent generated no response). Not due until 2026-07-05 11:00 UTC (~4 days). **Monitor before next run.**
- **`Reginald Daily Generation`**: July 1st 06:00 UTC run completed agent side, but image generation failed with OpenRouter HTTP 402 (depleted credits). No comic for July 1st. Next run 2026-07-02 06:00 UTC (~19h).
- **Queue**: steer (depth 0)
- **Active sessions**: 0
- **Git**: will commit this heartbeat update.

## Notes
- `openclaw_heartbeat` runs every 30m; last run 10:12 UTC, next 10:42 UTC.
- `ollama_keepalive_serenity` runs every ~2m; next 10:27 UTC.
- `Ikaris Nightly` last OK; next run 2026-07-01 15:00 UTC (~5h).
- `Memory Dreaming Promotion` next run 2026-07-02 03:00 UTC (~17h).
- `Daily GitHub Backup` next run 2026-07-02 04:00 UTC (~18h).
- Weather/email/calendar handled by separate 4h cron; not checked in this heartbeat.
- Fallback model list still includes stale/depleted `ollama-cloud` providers after `ollama-cloud/kimi-k2.6:cloud` 404 and OpenRouter 402. Consider trimming to local Ollama models only until credits are restored.

## System
- Load: unknown this poll
- RAM: unknown this poll
- Swap: unknown this poll
- Disk `/`: unknown this poll

## Upcoming Cron Runs
- `ollama_keepalive_serenity`: 11:27 UTC (next ~30 min)
- `openclaw_heartbeat`: 11:27 UTC (~30 min)
- `Ikaris Nightly`: 15:00 UTC (~4 h)
- `update_memory`: 2026-07-02 00:00 UTC (~13 h) — **watch this one**
- `Memory Dreaming Promotion`: 2026-07-02 03:00 UTC (~16 h)
- `Daily GitHub Backup`: 2026-07-02 04:00 UTC (~17 h)
- `Reginald Daily Generation`: 2026-07-02 06:00 UTC (~19 h)
- `Rockin Regi Weekly Comic`: 2026-07-05 11:00 UTC (4 days)

## Next Planned Checks
- ✅ `update_memory` delivery patched; verify it succeeds at next run.
- Re-run / inspect `Rockin Regi Weekly Comic` before its scheduled run on 2026-07-05.
- Decide whether to add OpenRouter credits or switch Reginald Daily image generation to a non-paid fallback.
- Trim `agents.defaults.model.fallbacks` to remove providers that currently fail (ollama-cloud, OpenRouter, OpenAI).

## Commands
- `session_status` — show runtime details
- `openclaw cron list` — cron health
- `sessions_list` — active sessions
