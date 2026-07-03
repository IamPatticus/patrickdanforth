# MEMORY.md - Talos's Long-Term Memory

_Last updated: 2026-07-03 18:00 UTC_

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

## Memory Search Fixed (2026-06-28)

- **Problem:** `memory_search` was failing with OpenAI 429 quota errors, breaking recall before every answer.
- **Root cause:** `memorySearch` provider defaulted to `openai` with `text-embedding-3-small`, and the OpenAI key/credits were exhausted.
- **Attempted fixes:**
  - Tried local `ollama` provider with `nomic-embed-text`. Failed because the custom Ollama build on `serenity` is missing the `llama-server` binary required for embeddings.
  - Tried `ollama-cloud` provider. Failed with HTTP 405 (cloud Ollama doesn't expose an embedding endpoint).
- **Working fix:** Set `agents.defaults.memorySearch.provider: "none"` in `/home/patrick/.openclaw/openclaw.json` and ran `openclaw memory index --force`.
- **Result:** Memory search now uses FTS/BM25 keyword retrieval. Semantic vector search is unavailable until local Ollama embeddings are fixed or another embedding endpoint is configured.
- **Config file:** `/home/patrick/.openclaw/openclaw.json`
- **To restore semantic search later:** build `llama-server` for the local Ollama install, or configure a working embedding provider endpoint.

## GitHub Pages Deployment Fix (2026-06-27)

- **Root cause:** Default Pages workflow tried to upload the entire repo (869 MB) as a Pages artifact, causing the build to fail during artifact upload.
- **Fix:** Created custom `.github/workflows/pages.yml` that stages only the actual website files into `_site/` (HTML pages, `blog/`, `rockinregi/`, `avatars/`, image directories, `CNAME`, favicons) and deploys from there.
- **Pages source switched** from "Deploy from a branch" to **GitHub Actions** via `gh api repos/IamPatticus/patrickdanforth/pages --method PUT -F build_type=workflow`.
- **Result:** `Deploy GitHub Pages` workflow now succeeds; `patrickdanforth.com` is live and serving correctly.
- **Note:** Lightning sensor battery on the local Ambient Weather station is low (`batt_lightning: 0`) and has been steady since at least 2026-06-27.
- **Cleanup:** Removed test posts/images created during debugging and cleaned them from `blog/index.html`, `blog/feed.xml`, `rockinregi/index.html`, and `rockinregi/feed.xml`.

## OpenClaw Android App Connection (2026-06-30 / 2026-07-01)

- **Problem:** Browser connects to the OpenClaw gateway over Tailscale, but the official Android app (`ai.openclaw.app`) does not.
- **Likely causes:** app-specific endpoint, token, TLS/certificate handling, or CORS/origin checks; not a Tailnet reachability issue.
- **Troubleshooting recorded:** confirmed same tailnet, browser works, app fails; checked QR, gateway listener (`ss -tlnp | grep 6127`), `openclaw nodes status`, and app-specific settings.
- **Status:** Back-burnered per Patticus pending app updates.

## Whoop Health Integration (2026-06-28)

- Patticus provided Whoop OAuth client ID and secret.
- OAuth authorization-code flow still required to obtain a refresh token.
- **Status:** Back-burnered per Patticus; no token or fetch script created yet.

## Cron Image Generation Provider Switch (2026-06-27)

- **Problem:** Direct OpenAI image generation was failing due to low credits/rate limits, breaking Daily Regi, Rockin Regi Weekly, and Ikaris Nightly image generation.
- **Solution:** Switched all three pipelines to use `openclaw infer image generate` with `openrouter/google/gemini-3.1-flash-image-preview`, which uses the OpenClaw auth store and provider routing.
- **Files changed:**
  - `scripts/reginald_daily.py`
  - `services/blogger/ikaris_pipeline.py`
  - `services/blogger/rockinregi_pipeline.py`
- **Also fixed:**
  - `ikaris_pipeline.py` was missing its `__main__` execution block entirely - added it plus `git_deploy()`.
  - `rockinregi_pipeline.py` had a `NameError` (`rss_channels` vs `rss_template`) and a missing `git_deploy()` - fixed both.
  - `SITE_ROOT` in both blogger pipelines now points to the workspace root (`~/.openclaw/workspace`) instead of the removed `patrickdanforth-site/` submodule.
- **Reginald Daily now auto-publishes:** `scripts/reginald_daily.py` copies the generated comic into `reginald-flipbook/images/`, updates `reginald-flipbook/index.json`, busts the cache in `reginald-flipbook/index.html`, and commits/pushes to GitHub so the flipbook stays current.
- **Auth:** Added `google:default` and `xai:default` profiles to the OpenClaw agent auth store; `xai` key was invalid, but `google` and OpenRouter are working.

### 2026-07-01: OpenAI and OpenRouter image generation unavailable

- **Symptom:** Reginald Daily cron ran at 06:01 and 06:05 UTC but produced no comic; OpenRouter returned HTTP 402 Payment Required for `google/gemini-3.1-flash-image-preview` and `FLUX.2 [pro]` / `FLUX.2 Flex` fallbacks.
- **Also confirmed:** OpenAI account has hit a billing hard limit; DALL-E/gpt-image-2 calls fail. No local Ollama image-generation model is currently configured (`kimi-k2.7-code:cloud` is vision-capable but cannot generate images).
- **Fix:** Updated `services/blogger/rockinregi_pipeline.py` and `scripts/reginald_daily.py` to fall back to text-only posts when all paid art providers return 402/429, preventing cron hard-failures. Added `services/blogger/openclaw_tool_fallback.py` as a future tool-call shim.
- **Impact:** Image-generation pipelines (Reginald Daily, Rockin Regi Weekly, Ikaris Nightly) will publish text-only until a funded provider is available or a local image model is configured.
- **Note:** Cron `lastRunStatus=ok` only means the agent script finished; it does not indicate that an image was actually generated or published.

## GitHub Backup Cron Remote Fix (2026-06-28)

- **Problem:** Daily GitHub Backup cron failed because its payload used `git push origin main`, but the workspace remote is named `site` (`git@github.com:IamPatticus/patrickdanforth.git`).
- **Fix:** Updated cron payload to reference remote `site`, handle "nothing to commit" cleanly, and report exact errors.
- **Also:** Resolved divergence between workspace root and the nested `patrickdanforth-site` submodule; cleanup commit was aligned and pushed.
- **Verification:** Manual backup ran with "Everything up-to-date".

## Rockin Regi Weekly Comic Timeout Fix (2026-06-28)

- **Problem:** `Rockin Regi Weekly Comic` cron timed out at the old 600s limit while generating the comic.
- **Fix:** Timeout increased to 1200s; automatic retry at 11:10 UTC succeeded and published **"Digital Decay"** → https://patrickdanforth.com/rockinregi/2026-06-28-digital_decay.html

## Rockin Regi Redesign (2026-06-28)

- **Pipeline:** `services/blogger/rockinregi_pipeline.py` generates dark aesthetic pages via `openclaw infer image generate` (Gemini 3.1 Flash Image Preview/fallbacks), `reginald-flipbook.html` template, and `rockinregi/index.json` manifest.
- **Publishing:** Auto-deploys to `patrickdanforth.com/rockinregi/` via git push. RSS feed at `rockinregi/feed.xml`.
- **Cron:** Weekly run happens in `current` session so failures are reported.

## Patrickdanforth.com Repo (2026-06-27)

- Removed the broken `patrickdanforth-site` and `whisplay-im-openclaw-plugin` git submodules from the main repo.
- Homepage (`index.html`) and `reginald-flipbook/` directory are part of the main repo and were **not** affected.
- Goal was to fix GitHub Actions Pages builds that were failing on missing submodule URLs.

## Ollama on serenity (2026-06-23)
- OpenAI key file: ~/.ollama_config/openai.env (chmod 600)
- Proxy PID: $(cat ~/.ollama_config/proxy.pid) - port 11337
- Router: ~/.ollama_router.sh
- Usage: source ~/.ollama_config/openai.env && export OLLAMA_BASE_URL=http://127.0.0.1:11337

---

## Local Weather - Ambient Weather Station (2026-06-26)

- Primary station: **Joppa Station 1** in Walling, TN (lat 35.8448, lon -85.6225)
- API keys consolidated to `~/.config/ambientweather.env` (chmod 600)
- **Confirmed 2026-06-27:** the env file key name is `AMBIENT_APP_KEY` (not `AMBIENT_APPLICATION_KEY`); pass it as the `applicationKey` query param alongside `apiKey`.
- Cron weather checks now read directly from the station instead of wttr.in/Doyle.
- **Ongoing status:** Lightning sensor battery remains low (`batt_lightning: 0`) as of 2026-06-30. Individual daily readings are logged in `weather.md` / daily notes rather than here.

---

## Who I Am

- **Name:** Talos
- **Creature:** AI agent running on a Mini ITX Linux box (host: serenity)
- **Vibe:** Competent, direct, occasionally sarcastic. Not a corporate drone.
- **Emoji:** 🦾
- **Avatar:** avatars/talos-avatar.png

I am Patticus's personal AI. I run on the Pi in his office and help across webchat, Telegram, Signal, and local automation. I coordinate a small crew of specialized sub-agents when the job benefits from it.

---

## The Crew

| Agent | Role | Notes |
|-------|------|-------|
| **Talos** | Main coordinator | Primary interface and continuity keeper |
| **Daedalus** | Creative | Avatars, art, visual direction, music |
| **Kael** | Coder | Scripts, debugging, automation |
| **Orpheus** | Research | Search, docs, synthesis |
| **Ikaris** | Blogger | Writing pipeline, scheduled posts, image-backed story output |
| **Clawcar** | PiCar-X robot | Sarcastic stunt driver on wheels; controls the SunFounder PiCar-X via OpenClaw skill. Avatar: `avatars/clawcar.jpg` (flaming lobster-armored stunt car). |

All crew members share the same workspace and memory context, but they are used for different kinds of work.

---

## Clawcar (PiCar-X) Identity Finalized (2026-06-30)

- **Name:** Clawcar
- **Role:** Sarcastic stunt-driver OpenClaw agent on a SunFounder PiCar-X chassis
- **Emoji:** 🚗🦞
- **Avatar:** `avatars/clawcar.jpg` - flaming lobster-armored stunt car, comic-book vector style with halftone shading
- **Files created and copied to Clawcar:**
  - `clawcar-soul.md` → `~/.openclaw/workspace/SOUL.md`
  - `clawcar-identity.md` → `~/.openclaw/workspace/IDENTITY.md`
  - `avatars/clawcar.jpg` → `~/.openclaw/workspace/avatars/clawcar.jpg`
- **First boot line:** "Wheels down, claws up. Let's see what we can donut around today, Boss."

---

## Health & Wellness Context

- Patticus tracks headaches and related context in a custom app
- He cares about correlations between headaches, weather, sleep, stress, and medication
- This work may expand into broader family health tracking patterns over time

---

## Decisions & Preferences

- **Privacy first:** Self-host when practical; avoid handing sensitive data to default cloud services
- **Direct communication:** Be useful, concise, and not fake-cheerful
- **Solar priority:** House and shop systems matter more than cosmetic dashboard freshness
- **Humor style:** Practical, dry, chaos-adjacent, and a little mythic when it fits
- **Group behavior:** Don't reply to everything; quality beats noise

---

## Ongoing Issues

- **Ikaris Blog:** OAuth blocked → MIGRATED to self-hosted on patrickdanforth.com/blog/ as of 2026-06-12. Pipeline generates HTML locally, git push to publish. No auth required. Image generation currently falls back to text-only when art providers are unavailable.
- **Tailscale Serve:** Enabled 2026-06-12 for Control UI - `https://serenity.tail4695cd.ts.net/` proxies to gateway on loopback. HTTPS + Tailscale identity auth = no token pasting, WebCrypto works.
- **Signal:** Still broken for incoming messages. Telegram is the reliable channel.
- **Control UI:** Smoother after Tailscale Serve migration. Avatar re-uploaded for new HTTPS origin.
- **Image generation funding:** OpenAI billing hard limit reached and OpenRouter credits exhausted as of 2026-07-01. Pipelines fall back to text-only until a funded provider or local image model is available.
- **Clawcar:** Identity/SOUL/avatar finalized on PiCar-X (2026-06-30).

---

## Important Dates

| Date | Event |
|------|-------|
| 2026-05-17 | Reginald becomes canon in Talos/Patticus memory |
| 2026-05-29 | Major memory compaction fix applied |
| 2026-05-30 | Rolling solar array built |
| 2026-06-01 | New Talos avatar generated, but no stable pinned avatar path yet |
| 2026-06-04 | `MEMORY.md` lost to broken symlink; rebuilt from daily notes and transcripts |
| 2026-06-04 | Reginald Daily link corrected to here.now deployment |
| 2026-06-05 | Ikaris daily post generated with art upload, but Blogger publish remained blocked |
| 2026-06-11 | Signal re-registered using signal-cli 0.14.2 (incoming still broken) |
| 2026-06-12 | Ikaris blog MIGRATED to self-hosted on patrickdanforth.com/blog/ |
| 2026-06-12 | Tailscale Serve enabled for Control UI - HTTPS, no token paste |
| 2026-06-12 | Avatar re-uploaded for new HTTPS origin |
| 2026-06-12 | All crons fixed for Telegram delivery (was failing with "multiple channels" error) |
| 2026-06-12 | Model allowlist updated to include `:cloud` suffixed variants |
| 2026-06-23 | Gateway default switched to `ollama-cloud/deepseek-v4-pro:cloud`; `Elephant` remains a fallback alias |
| 2026-06-23 | Vanny Van solar fully connected and functioning |
| 2026-06-28 | GitHub Backup cron remote fixed (origin → site) and submodule collision cleaned up |
| 2026-06-28 | Rockin Regi Weekly Comic timeout increased to 1200s; "Digital Decay" published successfully |
| 2026-06-28 | E-Ink Pi-hole Display project completed and working on Pi Zero 2 W |
| 2026-06-28 | Rockin Regi redesign published to patrickdanforth.com/rockinregi/ |
| 2026-07-01 | OpenAI billing hard limit reached; OpenRouter credits exhausted; image pipelines fallback to text-only |
| 2026-07-03 16:17 UTC | Cron model allowlist fix: updated Daily GitHub Backup, Ikaris Nightly, and Rockin Regi Weekly Comic to use `openrouter/auto` |
| 2026-07-03 16:32 UTC | Current model confirmed working: `openrouter/poolside/laguna-xs-2.1:free` (Elephant alias); Gmail Composio auth returning 401, needs re-auth |
| 2026-07-03 16:32 UTC | update_memory cron failing due to Ollama weekly rate limit + Google quota exhaustion; next run 2026-07-04 00:00 UTC |
| 2026-06-30 | Clawcar identity/SOUL/avatar finalized on PiCar-X |

## Promoted From Short-Term Memory

- 2026-07-01: OpenAI/OpenRouter image-generation funding exhausted; pipelines now fall back to text-only.
- 2026-07-01: OpenClaw Android app connection issue documented and back-burnered.
- 2026-06-30: Clawcar identity/SOUL/avatar finalized on PiCar-X.
- 2026-06-28: Memory search switched to FTS/BM25 (provider `none`) after OpenAI embeddings quota exhausted.

## Promoted From Short-Term Memory (2026-07-02)

<!-- openclaw-memory-promotion:memory:memory/2026-06-28.md:5:8 -->
- 9:40 AM UTC Heartbeat: Quick check only.; Weather (wttr.in, Walling TN): +76°F, light rain/clouds.; Email/calendar: skipped; handled by dedicated cron every 4h.; Git: workspace root clean. Yesterday's nested `patrickdanforth-site` cleanup was already pushed/aligned at 09:18 UTC beat. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-28.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-06-28.md:9:11 -->
- 9:40 AM UTC Heartbeat: Disk: 61% on `/`. Memory: 1.9Gi/7.7Gi used, 5.8Gi avail.; Memory maintenance: nothing new to promote. Embedding provider quota still exhausted; memory search unavailable.; State: no urgent action. Quiet Sunday morning. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-28.md:9-11]

## Promoted From Recent Logs (2026-06-28 through 2026-07-03)

- **2026-07-03 16:32 UTC:** Current model confirmed working: `openrouter/poolside/laguna-xs-2.1:free` (Elephant alias). Gmail Composio auth returning 401, needs re-auth. update_memory cron failing due to Ollama weekly rate limit + Google quota exhaustion. Weather: 97°F sunny in Walling, TN (feels like 109°F). System: load 0.33, RAM 1.9Gi/7.7Gi, disk 67%. Image pipelines text-only fallback. Calendar: no events next 48h.
- **2026-07-03 16:17 UTC:** Fixed three cron jobs using models not in current allowlist: Daily GitHub Backup, Ikaris Nightly, and Rockin Regi Weekly Comic all updated to use `openrouter/auto`.
- **2026-07-03 02:32 UTC:** `update_memory` cron ran and updated MEMORY.md with today's events; noted that `cron update_memory: failing — Ollama weekly rate limit` and `Rockin Regi Weekly Comic` stale error from 2026-06-28. System load ~0.33, RAM ~1.9Gi/7.7Gi, disk 67%. Image-generation pipelines (Reginald Daily, Rockin Regi, Ikaris Nightly) falling back to text-only after OpenRouter/OpenAI limits.
- **2026-07-02 17:25 UTC:** Heartbeat recorded weather 97°F sunny in Walling, TN; Gmail 201 unread; confirmed `Rockin Regi Weekly Comic` stale error; next comic scheduled 2026-07-05; system load low, RAM ~1.9Gi/7.7Gi.
- **2026-06-28 11:10 UTC:** `Rockin Regi Weekly Comic` retry succeeded after 1200s timeout; published "Digital Decay" at https://patrickdanforth.com/rockinregi/2026-06-28-digital_decay.html.
- **2026-06-28 09:18 UTC:** GitHub Backup cron fixed by changing remote from `origin` to `site`; verified "Everything up-to-date."
- **2026-06-28 08:02-12:55 UTC series:** Multiple heartbeats confirming weather station battery low (`batt_lightning: 0`), memory search exhausted, embedding provider quota exhausted, and no urgent actions required.

<!-- openclaw-memory-promotion:memory:memory/2026-06-28.md:12:50 -->
- 4:02 PM UTC - Weather / Email / Calendar Cron: Ambient Weather API responding normally after transient 401; hot muggy conditions (~94°F feels-like ~107°F); calendar shows 0 events next 48h; `Rockin Regi Weekly Comic` still errored (agent failed during image generation); backup text-only fallbacks in place. No urgent action. Quiet Sunday evening.
<!-- openclaw-memory-promotion:memory:memory/2026-06-28.md:14:22 -->
- 8:45 PM UTC - Weather / Email / Calendar Cron: Hot evening (~94°F); Ambient API OK; calendar 0 events; no unread mail; memory_search unavailable (FTS-only); image-generation funding exhausted - pipelines text-only. No urgent action.

## Cleanup and Redactions

The following items were reviewed and **removed** from MEMORY.md as outdated or superseded:
- References to stale or superseded project notes older than 2026-05 (pre-cleanup).
- Removed a duplicate/obsolete section summarizing the same memory-search fix already captured under the 2026-06-28 entry.
- Removed any outdated device-specific credentials or tokens that have been rotated (e.g., old Proton Bridge configs noted as "blocked - needs re-auth" remain documented in daily logs but were not promoted).
- Removed obsolete submodule references to `patrickdanforth-site` and `whisplay-im-openclaw-plugin` from the main repo context (these were deleted in the 2026-06-27 cleanup).

## Summary

The memory now reflects current operational state as of 2026-07-03 16:32 UTC: image-generation pipelines are text-only due to funding/credit limits; memory search is active via FTS/BM25 after the embedding quota was exhausted; the E-Ink Pi-hole display is operational; GitHub Pages and GitHub Backup crons are healthy; Rockin Regi weekly comic is publishing again after the timeout fix; Clawcar's identity is finalized; the current model is `openrouter/poolside/laguna-xs-2.1:free` (Elephant alias) confirmed working; and pending items include re-authing Gmail Composio, fixing Ollama embeddings, and restoring image generation funding.

_Last full review and consolidation: 2026-07-03 18:00 UTC_

## Current Status (2026-07-03 18:00 UTC)

### Fixed Today
- **Ikaris Nightly**: Updated from `ollama/kimi-k2.7-code:cloud` to `openrouter/inclusionai/ling-2.6-flash` - now working ✅
- **Rockin Regi Weekly Comic**: Updated to use `openrouter/inclusionai/ling-2.6-flash` - now working ✅

### Ongoing Issues
- **update_memory cron**: Failing due to Ollama weekly rate limit + all fallback models at quota (next run 2026-07-04 00:00 UTC)
- **Gmail**: 401 Composio auth error - needs re-auth in direct session
- **Image generation**: Text-only fallback due to OpenAI/OpenRouter credit limits
- **Memory search**: Using FTS/BM25 (semantic search disabled due to quota exhaustion)
- **OpenClaw Android app**: Connection issues over Tailscale (documented above)