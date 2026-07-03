# OpenClaw Heartbeat Log

## Last Checks
- **email**: 2026-07-03 16:55 UTC (401 Composio auth issue)
- **calendar**: 2026-07-03 16:55 UTC (no events in next 48h)
- **weather**: 2026-07-03 16:55 UTC (98°F, sunny, feels like 106°F in Walling, TN)
- **memory**: 2026-07-03 16:55 UTC (current)
- **health**: 2026-07-03 16:55 UTC
- **heartbeat_poll**: 2026-07-03 16:55 UTC ✅
- **cron_status**: 2026-07-03 16:55 UTC (5 ok, 2 error)
- **git_status**: 2026-07-03 16:55 UTC (working tree clean)
- **system_health**: 2026-07-03 17:00 UTC (load 0.10/0.37/0.50, 1.4Gi/7.7Gi, 68% disk)

## Current Status
- **Uptime**: gateway ~42m · system ~42m
- **Model**: openrouter/poolside/laguna-xs-2.1:free — confirmed working 2026-07-03 16:55 UTC
- **Tokens**: 19k in / 44 out (10% context usage)
- **Last heartbeat**: 2026-07-03 16:55 UTC - ✅ Healthy
- **System**: Load 1.18, 0.93, 0.69 | RAM 1.7Gi/7.7Gi (6.0Gi avail) | Disk 68% used
- **Weather**: 98°F, sunny, feels like 106°F (very hot in Walling, TN)
- **Calendar**: No events in next 48h
- **Email**: Unable to fetch (401 Composio auth issue)
- **Git**: Working tree clean, up to date
- **Cron jobs**: 5 ok, 2 error
  - `update_memory`: ❌ Error (Ollama weekly rate limit + all models at quota; next run 2026-07-04 00:00 UTC)
  - `Ikaris Nightly`: ❌ Error (model `ollama/kimi-k2.7-code:cloud` not in allowlist; next run 2026-07-04 ~00:00 UTC)
  - `Rockin Regi Weekly Comic`: ❌ Error (stale since 2026-06-28; next run 2026-07-05 11:00 UTC)

## Model Config
- Primary: `openrouter/poolside/laguna-xs-2.1:free`
- Fallback 1: `google/gemini-2.5-flash`
- Fallback 2: `openai/o3-mini`

## Known Issues
- **update_memory cron**: Failing due to Ollama weekly rate limit + all fallback models (ling-2.6-flash, gemini-2.5-flash, o3-mini) at quota limits
- **Ikaris Nightly**: Model `ollama/kimi-k2.7-code:cloud` needs to be added to allowlist or job needs model update
- **Gmail**: 401 Composio auth error - needs re-auth in direct session
- **OpenClaw Android app**: Connection issues over Tailscale (documented in MEMORY.md)
- **Whoop health integration**: OAuth flow pending
- **Image generation**: Text-only fallback due to OpenAI/OpenRouter credit limits
- **Memory search**: Using FTS/BM25 (semantic search disabled due to quota exhaustion)

## Next Checks Due
- Rotate checks every 30 minutes during active hours
- Email/calendar maintenance: daily
- Weather monitoring: as needed for travel planning

## Action Items
- **Low priority**: System healthy. No urgent actions required.
- **Deferred**: Composio Gmail re-auth, Ollama embeddings fix, image generation funding restoration.