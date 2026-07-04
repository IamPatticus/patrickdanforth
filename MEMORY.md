# MEMORY.md - Talos's Long-Term Memory

_Last updated: 2026-07-04 04:07 UTC_

---

## Who I Am

- **Name:** Talos
- **Creature:** AI agent running on a Mini ITX Linux box (host: serenity)
- **Vibe:** Competent, direct, occasionally sarcastic. Not a corporate drone.
- **Emoji:** 🦾
- **Avatar:** `avatars/talos-avatar.png`

I am Patticus's personal AI. I help across webchat, Telegram, Signal, and local automation, and coordinate a small crew of specialized sub-agents when useful.

---

## The Crew

| Agent | Role | Notes |
|-------|------|-------|
| **Talos** | Main coordinator | Primary interface and continuity keeper |
| **Daedalus** | Creative | Avatars, art, visual direction, music |
| **Kael** | Coder | Scripts, debugging, automation |
| **Orpheus** | Research | Search, docs, synthesis |
| **Ikaris** | Blogger | Writing pipeline, scheduled posts, image-backed/story output |
| **Clawcar** | PiCar-X robot | Sarcastic stunt driver on wheels; controls the SunFounder PiCar-X via OpenClaw skill. Avatar: `avatars/clawcar.jpg`. |

All crew members share the same workspace and memory context, but they are used for different kinds of work.

---

## Current Operational Status (2026-07-04 00:00 UTC)

- **System:** serenity is healthy; recent heartbeats showed low load, ~1.3-1.9 GiB RAM used of 7.7 GiB, and disk around 67-68% used.
- **Cron:** Daily GitHub Backup, Ikaris Nightly, Rockin Regi Weekly Comic, Reginald Wednesday Comic, heartbeat, and Ollama keepalive are configured and generally healthy after model fixes on 2026-07-03.
- **Model routing:** Current working route confirmed 2026-07-03: `openrouter/poolside/laguna-xs-2.1:free` (Elephant alias). Ikaris/Rockin Regi cron jobs now use `openrouter/inclusionai/ling-2.6-flash` with fallbacks.
- **Memory search:** Uses FTS/BM25 keyword retrieval because semantic embedding providers hit quota/build issues.
- **Image generation:** OpenAI billing hard limit and OpenRouter credit exhaustion mean image-backed pipelines fall back to text-only until a funded provider or local image model is available.
- **Gmail/Composio:** Outbound Gmail reply worked on 2026-07-02, but by 2026-07-03 Composio Gmail auth was returning 401 and needs re-auth in a direct session.
- **Google Calendar / X:** Not connected through Composio; OAuth/setup pending.
- **Weather:** Walling, TN was dangerously hot July 1-3 (~97-99°F, feels-like often >105°F). Routine readings belong in `weather.md` and daily notes, not long-term memory.

---

## Decisions & Preferences

- **Privacy first:** Self-host when practical; avoid handing sensitive data to default cloud services.
- **Direct communication:** Be useful, concise, and not fake-cheerful.
- **Solar priority:** House and shop systems matter more than cosmetic dashboard freshness.
- **Humor style:** Practical, dry, chaos-adjacent, and a little mythic when it fits.
- **Group behavior:** Don't reply to everything; quality beats noise.
- **Model cost safety:** Patticus confirmed `kimi-k2.7` / `kimi-k2.7-code` burns tokens too quickly. Do **not** use Kimi 2.7 as a default, routine fallback, or cron model. Prefer thriftier fallbacks first, such as `openrouter/cohere/north-mini-code:free`, `openrouter/auto`, or tested lower-cost Ollama cloud models after reset. Use Kimi 2.7 only if explicitly requested or clearly justified for a one-off heavy coding task.

---

## OpenClaw / Gateway / Models

### Memory Search Fixed (2026-06-28)

- **Problem:** `memory_search` failed with OpenAI 429 quota errors, breaking recall before answers.
- **Root cause:** `memorySearch` provider defaulted to OpenAI `text-embedding-3-small`, and the OpenAI key/credits were exhausted.
- **Attempted fixes:**
  - Local Ollama provider with `nomic-embed-text` failed because the custom Ollama build on `serenity` lacks the `llama-server` binary required for embeddings.
  - `ollama-cloud` provider failed with HTTP 405 because cloud Ollama does not expose the needed embedding endpoint.
- **Working fix:** Set `agents.defaults.memorySearch.provider: "none"` in `/home/patrick/.openclaw/openclaw.json` and ran `openclaw memory index --force`.
- **Result:** Memory search uses FTS/BM25 keyword retrieval. Semantic vector search is unavailable until local Ollama embeddings or another embedding endpoint is fixed.

### Cron Model / Provider Fixes (2026-07-03)

- Several cron jobs were failing or stale because their configured models were not in the current allowlist or were too costly/rate-limited.
- Added/registered provider configurations in `/home/patrick/.openclaw/openclaw.json` for:
  - `openai/o3-mini`
  - `google/gemini-2.5-flash`
  - `openrouter/inclusionai/ling-2.6-flash`
- Updated:
  - **Ikaris Nightly:** from `ollama/kimi-k2.7-code:cloud` to `openrouter/inclusionai/ling-2.6-flash`, with fallbacks.
  - **Rockin Regi Weekly Comic:** to `openrouter/inclusionai/ling-2.6-flash`, with fallbacks.
  - **Daily GitHub Backup:** earlier corrected away from disallowed/bad model routes; keep it on conservative, working routes.
- Important nuance: cron `lastRunStatus=ok` means the agent/script finished, not necessarily that image generation produced art.

### Tailscale Serve / Control UI (2026-06-12)

- Tailscale Serve is enabled for the Control UI at `https://serenity.tail4695cd.ts.net/`, proxying to the gateway on loopback.
- HTTPS + Tailscale identity auth avoids token pasting and makes WebCrypto work.
- Avatar was re-uploaded for the new HTTPS origin.

### OpenClaw Android App Connection Issue (2026-06-30 / 2026-07-01)

- Browser connects to the OpenClaw gateway over Tailscale, but the official Android app (`ai.openclaw.app`) does not.
- Likely causes: app-specific endpoint/token handling, TLS/certificate behavior, or CORS/origin checks; not Tailnet reachability.
- Troubleshooting confirmed same tailnet, browser works, app fails; checked QR, listener (`ss -tlnp | grep 6127`), `openclaw nodes status`, and app settings.
- **Status:** Back-burnered per Patticus pending app updates.

### Ollama on serenity (2026-06-23)

- OpenAI key file path: `~/.ollama_config/openai.env` (chmod 600).
- Proxy PID: `$(cat ~/.ollama_config/proxy.pid)`; proxy port `11337`.
- Router: `~/.ollama_router.sh`.
- Usage: `source ~/.ollama_config/openai.env && export OLLAMA_BASE_URL=http://127.0.0.1:11337`.

---

## Website / Publishing / Automation

### Patrickdanforth.com Repo Cleanup (2026-06-27)

- Removed broken `patrickdanforth-site` and `whisplay-im-openclaw-plugin` git submodules from the main repo.
- Homepage (`index.html`) and `reginald-flipbook/` are part of the main repo and were not affected.
- Goal was to fix GitHub Actions Pages builds that were failing on missing submodule URLs.

### GitHub Pages Deployment Fix (2026-06-27)

- **Root cause:** Default Pages workflow tried to upload the entire repo (~869 MB) as a Pages artifact, causing upload failure.
- **Fix:** Created `.github/workflows/pages.yml` that stages only actual website files into `_site/` and deploys from there.
- **Pages source:** switched from branch deploy to **GitHub Actions** via GitHub API.
- **Result:** `patrickdanforth.com` is live and serving correctly.
- **Cleanup:** Removed test posts/images created during debugging from blog/Rockin Regi pages and feeds.

### GitHub Backup Cron Remote Fix (2026-06-28)

- Daily GitHub Backup cron failed because payload used `git push origin main`, but the workspace remote is named `site` (`git@github.com:IamPatticus/patrickdanforth.git`).
- Updated cron payload to use remote `site`, handle "nothing to commit" cleanly, and report exact errors.
- Resolved divergence between workspace root and nested submodule cleanup; manual backup verified "Everything up-to-date".

### Ikaris Blog Migration (2026-06-12)

- Blogger OAuth was blocked, so Ikaris migrated to self-hosted publishing at `patrickdanforth.com/blog/`.
- Pipeline generates HTML locally and publishes via git push; no Blogger auth required.
- Image generation now falls back to text-only when art providers are unavailable.

### Cron Image Generation Provider Switch and Text-Only Fallbacks (2026-06-27 / 2026-07-01)

- **Initial problem:** Direct OpenAI image generation failed due to low credits/rate limits, breaking Daily Regi, Rockin Regi Weekly, and Ikaris Nightly image generation.
- **Initial solution:** Switched pipelines to `openclaw infer image generate` using `openrouter/google/gemini-3.1-flash-image-preview` through OpenClaw auth/provider routing.
- **Files changed:**
  - `scripts/reginald_daily.py`
  - `services/blogger/ikaris_pipeline.py`
  - `services/blogger/rockinregi_pipeline.py`
- **Additional fixes:**
  - Added missing `__main__` and `git_deploy()` to `ikaris_pipeline.py`.
  - Fixed `rockinregi_pipeline.py` `rss_channels` vs `rss_template` NameError and missing `git_deploy()`.
  - Pointed `SITE_ROOT` in blogger pipelines to the workspace root instead of removed `patrickdanforth-site/` submodule.
  - Reginald Daily auto-publishes by copying comics into `reginald-flipbook/images/`, updating `index.json`, busting cache in `index.html`, and committing/pushing.
- **2026-07-01 update:** OpenRouter returned HTTP 402 Payment Required and OpenAI hit a billing hard limit. No local Ollama image-generation model is configured.
- **Current behavior:** `services/blogger/rockinregi_pipeline.py` and `scripts/reginald_daily.py` fall back to text-only posts when paid art providers fail, preventing hard cron failures. `services/blogger/openclaw_tool_fallback.py` exists as a future tool-call shim.

### Rockin Regi Weekly Comic and Redesign (2026-06-28)

- Timeout was increased from 600s to 1200s after the weekly comic cron timed out.
- Retry succeeded and published **"Digital Decay"**: `https://patrickdanforth.com/rockinregi/2026-06-28-digital_decay.html`.
- Pipeline generates dark aesthetic pages using `reginald-flipbook.html` template and `rockinregi/index.json` manifest.
- Publishes to `patrickdanforth.com/rockinregi/` via git push; RSS feed at `rockinregi/feed.xml`.
- Weekly run happens in `current` session so failures are reported.

---

## Clawcar / PiCar-X

### Identity Finalized (2026-06-30)

- **Name:** Clawcar
- **Role:** Sarcastic stunt-driver OpenClaw agent on a SunFounder PiCar-X chassis
- **Emoji:** 🚗🦞
- **Avatar:** `avatars/clawcar.jpg` — flaming lobster-armored stunt car, comic-book vector style with halftone shading
- **Files created/copied to Clawcar:**
  - `clawcar-soul.md` → `~/.openclaw/workspace/SOUL.md`
  - `clawcar-identity.md` → `~/.openclaw/workspace/IDENTITY.md`
  - `avatars/clawcar.jpg` → `~/.openclaw/workspace/avatars/clawcar.jpg`
- **First boot line:** "Wheels down, claws up. Let's see what we can donut around today, Boss."

### Gateway Restoration and Node Setup (2026-07-02)

- Converted `picarx` (Raspberry Pi 5 on PiCar-X chassis, `picarx.tail4695cd.ts.net`) from a standalone OpenClaw gateway to a node of the main `serenity` gateway.
- Fixed broken gateway connection caused by Tailscale install changing network binding/routing.
- Configured node to connect via Tailscale Serve at `wss://serenity.tail4695cd.ts.net:443` using gateway token auth.
- Approved device pairing and node capabilities on `serenity`: `system.run`, `system.which`, `browser.proxy`.
- Verified node execution via remote `exec --host node --node picarx` with `uptime`, motion commands, and sensor tests.

### Control Bridge, Safety, Speech, and GPS (2026-07-02)

- Created `~/clawcar/clawcar_bridge.py` on `picarx` with commands:
  - `forward`, `backward`, `left`, `right`, `donut`
  - `center` (camera + wheels)
  - `forward_safe [speed] [stop_cm] [timeout]` — obstacle-aware driving
  - `approach` — drives close without evading
  - `location` — reports GPS fix
  - `speak` — uses speech output
- Added ultrasonic collision avoidance with median-filtered readings; on obstacle detection, Clawcar backs up, scans left/right, and turns toward clearer space.
- Tested obstacle avoidance successfully at `stop_cm=15` and `stop_cm=40`.
- Fixed camera servo jitter after motion by setting PWM pulse width to 0 after centering.
- Tested camera pan/tilt full range.
- Enabled speech via `robot_hat.tts.Espeak` and `espeak -ven+f3 -s130 -a200`; Clawcar verbally greeted Stevie, Bug, and Alyson.
- Completed a full 10-second `forward_safe` run in open area without collision.
- Integrated u-blox 7 USB GPS on `/dev/ttyACM0`; installed `gpsd` and `gpsd-clients`, configured socket activation with USB auto-attach (`USBAUTO=true`).
- Acquired 3D GPS fix at property location: lat ~35.8444580, lon ~-85.6228672, alt ~311 m.

---

## E-Ink Pi-hole Display (2026-06-28)

- **Hardware:** Raspberry Pi Zero 2 W + Waveshare 2.13" E-Ink HAT V4 (blue PCB = black/white/red tricolor) at `192.168.1.203`.
- **Correct driver:** `waveshare_epd.epd2in13b_V4` (tricolor), not `epd2in13_V4`.
- **Project path:** `~/patrickdanforth/eink-pihole/` in the repo.
- **Key deps in venv:** `spidev`, `gpiozero`, `RPi.GPIO`, `lgpio`.
- **Display method:** two 1-bit PIL images (black layer + red layer) passed to `epd.display()`.
- **Orientation:** rotate both layers 180° because the HAT mounts upside-down in the case.
- **Layout:** stack stats vertically at 250×122 to avoid squished text.
- **Timer:** `eink-pihole.timer` refreshes every 60 minutes.
- **Connection:** SSH password auth fails from `serenity`; use local commands on the Pi.

---

## Local Weather - Ambient Weather Station

- Primary station: **Joppa Station 1** in Walling, TN (lat 35.8448, lon -85.6225).
- API keys are consolidated in `~/.config/ambientweather.env` (chmod 600).
- Confirmed env key name is `AMBIENT_APP_KEY` (not `AMBIENT_APPLICATION_KEY`); pass as `applicationKey` query param alongside `apiKey`.
- Cron weather checks read directly from the station instead of wttr.in/Doyle when Ambient API is available.
- Lightning sensor battery remains low (`batt_lightning: 0`) as of late June / early July 2026; routine individual readings are logged in `weather.md` / daily notes.

---

## Health & Wellness Context

- Patticus tracks headaches and related context in a custom app.
- He cares about correlations between headaches, weather, sleep, stress, and medication.
- This work may expand into broader family health tracking patterns over time.

---

## Whoop Health Integration (2026-06-28)

- Patticus provided Whoop OAuth client ID and secret.
- OAuth authorization-code flow is still required to obtain a refresh token.
- **Status:** Back-burnered per Patticus; no token or fetch script created yet.

---

## Ongoing Issues / Watchlist

- **Gmail Composio auth:** 401 as of 2026-07-03; needs re-auth in direct session. Note: outbound reply did work on 2026-07-02 before the later auth failure.
- **Image generation funding:** OpenAI billing hard limit and OpenRouter credits exhausted as of 2026-07-01; pipelines publish text-only until funding/provider/local model is fixed.
- **Memory search semantics:** FTS/BM25 works; semantic vector search disabled until local Ollama embeddings or another embedding endpoint is configured.
- **OpenClaw Android app:** Browser works over Tailscale, official Android app does not; back-burnered pending app updates.
- **Signal:** Still broken for incoming messages. Telegram is the reliable channel.
- **Ambient lightning sensor:** Battery low (`batt_lightning: 0`).

---

## Important Dates

| Date | Event |
|------|-------|
| 2026-05-17 | Reginald becomes canon in Talos/Patticus memory |
| 2026-05-29 | Major memory compaction fix applied |
| 2026-05-30 | Rolling solar array built |
| 2026-06-04 | `MEMORY.md` lost to broken symlink; rebuilt from daily notes and transcripts |
| 2026-06-11 | Signal re-registered using signal-cli 0.14.2; incoming still broken |
| 2026-06-12 | Ikaris blog migrated to self-hosted `patrickdanforth.com/blog/` |
| 2026-06-12 | Tailscale Serve enabled for Control UI |
| 2026-06-12 | All crons fixed for Telegram delivery (`multiple channels` error resolved) |
| 2026-06-23 | Gateway default switched to `ollama-cloud/deepseek-v4-pro:cloud`; `Elephant` remains a fallback alias |
| 2026-06-23 | Vanny Van solar fully connected and functioning |
| 2026-06-27 | GitHub Pages deployment fixed with custom Actions workflow |
| 2026-06-28 | GitHub Backup cron remote fixed (`origin` → `site`) |
| 2026-06-28 | Rockin Regi timeout increased; "Digital Decay" published successfully |
| 2026-06-28 | E-Ink Pi-hole Display project completed and working |
| 2026-06-28 | Memory search switched to FTS/BM25 provider `none` after embedding quota issues |
| 2026-06-30 | Clawcar identity/SOUL/avatar finalized on PiCar-X |
| 2026-07-01 | OpenAI billing hard limit + OpenRouter credit exhaustion; image pipelines switched to text-only fallback |
| 2026-07-02 | Clawcar restored as OpenClaw node under serenity; control bridge, obstacle avoidance, speech, and GPS verified |
| 2026-07-02 | Gmail/Composio outbound reply confirmed working, before later 401 auth issue |
| 2026-07-03 | Cron provider/model configs fixed; Ikaris Nightly and Rockin Regi updated to `openrouter/inclusionai/ling-2.6-flash` with fallbacks |
| 2026-07-03 | Patticus clarified Kimi 2.7 cost issue; avoid Kimi 2.7 for defaults/fallbacks/crons |

---

## Cleanup Notes from 2026-07-04 Review

- Removed noisy heartbeat/weather snapshots from long-term memory; routine status belongs in daily logs, `HEARTBEAT.md`, and `weather.md`.
- Removed duplicate "Promoted From Short-Term Memory" / "Promoted From Recent Logs" sections that repeated already-curated facts.
- Replaced outdated statements that `update_memory` was currently failing with quota errors; that was true on 2026-07-03, but this 2026-07-04 memory maintenance run is completing.
- Consolidated conflicting cron model notes: early 2026-07-03 fixes used safer generic routes, then Ikaris/Rockin Regi were finalized on `openrouter/inclusionai/ling-2.6-flash` with fallbacks.
- Preserved durable operational facts and removed transient weather/system snapshots unless they describe an ongoing watch item.

_Last full review and consolidation: 2026-07-04 00:00 UTC_
