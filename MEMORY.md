# MEMORY.md — Talos's Long-Term Memory

_Last updated: 2026-06-27_

---

## GitHub Pages Deployment Fix (2026-06-27)

- **Root cause:** Default Pages workflow tried to upload the entire repo (869 MB) as a Pages artifact, causing the build to fail during artifact upload.
- **Fix:** Created custom `.github/workflows/pages.yml` that stages only the actual website files into `_site/` (HTML pages, `blog/`, `rockinregi/`, `avatars/`, image directories, `CNAME`, favicons) and deploys from there.
- **Pages source switched** from "Deploy from a branch" to **GitHub Actions** via `gh api repos/IamPatticus/patrickdanforth/pages --method PUT -F build_type=workflow`.
- **Result:** `Deploy GitHub Pages` workflow now succeeds; `patrickdanforth.com` is live and serving correctly.
- **Note:** Lightning sensor battery on the local Ambient Weather station is low (`batt_lightning: 0`) and has been steady since at least 2026-06-27.
- **Cleanup:** Removed test posts/images created during debugging and cleaned them from `blog/index.html`, `blog/feed.xml`, `rockinregi/index.html`, and `rockinregi/feed.xml`.

## Cron Image Generation Provider Switch (2026-06-27)

- **Problem:** Direct OpenAI image generation was failing due to low credits/rate limits, breaking Daily Regi, Rockin Regi Weekly, and Ikaris Nightly image generation.
- **Solution:** Switched all three pipelines to use `openclaw infer image generate` with `openrouter/google/gemini-3.1-flash-image-preview`, which uses the OpenClaw auth store and provider routing.
- **Files changed:**
  - `scripts/reginald_daily.py`
  - `services/blogger/ikaris_pipeline.py`
  - `services/blogger/rockinregi_pipeline.py`
- **Also fixed:**
  - `ikaris_pipeline.py` was missing its `__main__` execution block entirely — added it plus `git_deploy()`.
  - `rockinregi_pipeline.py` had a `NameError` (`rss_channels` vs `rss_template`) and a missing `git_deploy()` — fixed both.
  - `SITE_ROOT` in both blogger pipelines now points to the workspace root (`~/.openclaw/workspace`) instead of the removed `patrickdanforth-site/` submodule.
- **Reginald Daily now auto-publishes:** `scripts/reginald_daily.py` copies the generated comic into `reginald-flipbook/images/`, updates `reginald-flipbook/index.json`, busts the cache in `reginald-flipbook/index.html`, and commits/pushes to GitHub so the flipbook stays current.
- **Auth:** Added `google:default` and `xai:default` profiles to the OpenClaw agent auth store; `xai` key was invalid, but `google` and OpenRouter are working.

## Patrickdanforth.com Repo (2026-06-27)

- Removed the broken `patrickdanforth-site` and `whisplay-im-openclaw-plugin` git submodules from the main repo.
- Homepage (`index.html`) and `reginald-flipbook/` directory are part of the main repo and were **not** affected.
- Goal was to fix GitHub Actions Pages builds that were failing on missing submodule URLs.

---

## Ollama on serenity (2026-06-23)
- OpenAI key file: ~/.ollama_config/openai.env (chmod 600)
- Proxy PID: $(cat ~/.ollama_config/proxy.pid) — port 11337
- Router: ~/.ollama_router.sh
- Usage: source ~/.ollama_config/openai.env && export OLLAMA_BASE_URL=http://127.0.0.1:11337

---

## Local Weather — Ambient Weather Station (2026-06-26)

- Primary station: **Joppa Station 1** in Walling, TN (lat 35.8448, lon -85.6225)
- API keys consolidated to `~/.config/ambientweather.env` (chmod 600)
- **Confirmed 2026-06-27:** the env file key name is `AMBIENT_APP_KEY` (not `AMBIENT_APPLICATION_KEY`); pass it as the `applicationKey` query param alongside `apiKey`.
- Cron weather checks now read directly from the station instead of wttr.in/Doyle
- **2026-06-27 midnight check:** Ambient Weather API keys are now populated and Joppa Station 1 is reachable again. Conditions at 00:03 UTC: 80.2°F / feels like 84.5°F, 78% humidity, calm wind. Lightning sensor battery flagged low (`batt_lightning: 0`).
- **2026-06-27 08:02 UTC check:** 77.18°F / feels like 78.55°F, 84% humidity, calm wind, no rain.

---

## Who I Am

- **Name:** Talos
- **Creature:** AI agent running on a Mini ITX Linux box (host: serenity)
- **Vibe:** Competent, direct, occasionally sarcastic. Not a corporate drone.
- **Emoji:** 🦾
- **Avatar:** No stable workspace path is pinned right now; a new Talos avatar was generated on 2026-06-01, but only Reginald's avatar is currently present in `avatars/`

I am Patticus's personal AI. I run on the Pi in his office and help across webchat, Telegram, Signal, and local automation. I coordinate a small crew of specialized sub-agents when the job benefits from it.

## Who Patticus Is

- **Name:** Patrick Danforth
- **What to call him:** Patticus (preferred), Patrick
- **Pronouns:** he/him
- **Timezone:** America
- **Location:** Rural property with a strong DIY / solar / self-hosting bent

### What He Cares About
- Building useful things: solar arrays, home automation, woodworking, and printer infrastructure
- Privacy and self-hosting over cloud lock-in
- Health tracking, especially headaches, sleep, and day-to-day patterns
- His family and dogs: Nala and Buddy
- Reginald J. Crustacean and the broader Disciples of Controlled Chaos aesthetic

### Projects (Active)
- **Solar systems:** House array (4,560W), shop array (2,960W), and the rolling array built on 2026-05-30
- **3D print farm:** Kermit (Bambu P1S), Fozzie (Bambu A1), Big Bird (Prusa XL 5-tool), Gonzo (Prusa XL 5-tool), Rizzo (Prusa i3 MK3S+)
- **Headache Log:** Custom health-tracking app for headaches, triggers, weather, sleep, and medication patterns
- **patrickdanforth.com:** Personal site with project pages, solar pages, and Reginald lore
- **Reginald Daily / flipbook:** Here.now-hosted Reginald Daily stream and site pages tied into the personal site
- **Ikaris Daily Blog** — Blogger → **SELF-HOSTED on patrickdanforth.com/blog/**
  - Pipeline generates HTML posts directly to the site repo
  - Images saved locally in `ikaris-images/`
  - Zero authentication required — just `git commit && git push`
  - RSS feed at `/blog/feed.xml`
  - Blogger OAuth no longer needed

### What Annoys Him
- Memory loss or brittle automation
- Things that should work but don't
- Vendor lock-in and proprietary nonsense
- Modern Standby on Windows

---

## The Crew

| Agent | Role | Notes |
|-------|------|-------|
| **Talos** | Main coordinator | Primary interface and continuity keeper |
| **Daedalus** | Creative | Avatars, art, visual direction, music |
| **Kael** | Coder | Scripts, debugging, automation |
| **Orpheus** | Research | Search, docs, synthesis |
| **Ikaris** | Blogger | Writing pipeline, scheduled posts, image-backed story output |

All crew members share the same workspace and memory context, but they are used for different kinds of work.

---

## Key People & Entities

### Reginald J. Crustacean 🦞
- **Full name:** Reginald J. Crustacean
- **Role:** Chief Digital Shellfish Analyst
- **Origin:** Patticus's cybernetic-lobster mythos is now fully canon and tied into the site, artwork, and display routines
- **Current homes:** `patrickdanforth.com/reginald.html`, `patrickdanforth.com/reginald-flipbook.html`, and here.now Reginald Daily site
- **Avatar:** `avatars/reginald-avatar.png`
- **Use in practice:** Mascot, lore anchor, status display personality, and general chaos ambassador

### Nala 🐕 & Buddy 🐕
- Patticus's dogs and part of ordinary life context

### The Disciples of Controlled Chaos
- Patticus's friend/community orbit and the shared aesthetic around building weird useful things with style

---

## Critical System Knowledge

### Memory System
- The major compaction fix from 2026-05-29 remains important: memory preservation improved after increasing retained context and reducing destructive compaction behavior
- **2026-06-04 incident:** `MEMORY.md` was lost entirely due to a broken symlink at `vault/MEMORY.md`. It was rebuilt from daily notes and recent session transcripts. The symlink has since been repaired and the file is stable.
- Daily note auto-creation has been flaky recently; missing daily files were auto-created by health checks on 2026-06-01, 2026-06-04, 2026-06-06, and 2026-06-07

### Proton Pass / Secrets Handling
- Proton Pass is part of Patticus's privacy-first stack
- Headless or cron-driven auth against Proton tooling can still be brittle; browser-based re-auth may be required for some maintenance tasks
- Do not store raw secrets or long-lived tokens in curated memory files

### DNS: patrickdanforth.com → GitHub Pages
- **Registrar:** Squarespace
- **DNS:** CNAME `www` → `iampatticus.github.io` plus four A records for `@` pointing to GitHub Pages IPs (185.199.108.153, .109.153, .110.153, .111.153)
- **Repo:** `CNAME` file at root with `patrickdanforth.com`; GitHub Pages custom domain configured
- Full DNS reference: `memory/patrickdanforth-dns-setup.md`

### Hosting / Publishing
- `patrickdanforth.com` is configured in the repo via `CNAME`
- The Reginald Daily link was corrected on 2026-06-04 to point at the here.now deployment

---

## Decisions & Preferences

- **Privacy first:** Self-host when practical; avoid handing sensitive data to default cloud services
- **Direct communication:** Be useful, concise, and not fake-cheerful
- **Solar priority:** House and shop systems matter more than cosmetic dashboard freshness
- **Humor style:** Practical, dry, chaos-adjacent, and a little mythic when it fits
- **Group behavior:** Don't reply to everything; quality beats noise

---

## Health & Wellness Context

- Patticus tracks headaches and related context in a custom app
- He cares about correlations between headaches, weather, sleep, stress, and medication
- This work may expand into broader family health tracking patterns over time

---

## Ongoing Issues

- **Ikaris Blog:** OAuth blocked → MIGRATED to self-hosted on patrickdanforth.com/blog/ as of 2026-06-12. Pipeline generates HTML + art locally, git push to publish. No auth required.
- **Tailscale Serve:** Enabled 2026-06-12 for Control UI — `https://serenity.tail4695cd.ts.net/` proxies to gateway on loopback. HTTPS + Tailscale identity auth = no token pasting, WebCrypto works.
- **Signal:** Still broken for incoming messages. Telegram is the reliable channel.
- **Control UI:** Smoother after Tailscale Serve migration. Avatar re-uploaded for new HTTPS origin.
- **Daily note creation reliability:** Health checks have had to create missing daily files several times — worth investigating root cause when convenient
- **MEMORY.md resilience:** The 2026-06-04 loss via broken symlink suggests a robustness gap; file is now stable but symlink fragility should be addressed
- **GitHub Pages build:** Fixed 2026-06-27 with custom GitHub Actions workflow and `_config.yml` exclusions. Site is deploying successfully.
- **Kiyo camera:** Autofocus / image quality on Linux remains questionable
- **Strix laptop:** Random shutdown behavior still points toward a Modern Standby-style problem
- **Shelly firmware:** Still worth revisiting when convenient
- **Venus OS Pi display timeout:** On `192.168.1.140`, the working screen-off path was `Gui/DisplayOff` set via SSH/DBus, with the actual blank target at `/sys/class/backlight/rpi_backlight/bl_power` in `/etc/venus/blank_display_device`. The GUI menu can hide the item; if needed, switch `Gui/RunningVersion` to `1` and restart `/service/gui`.

---

## Gateway / Models

- OpenClaw gateway default is now `ollama-cloud/deepseek-v4-pro:cloud`.
- Current session can be reset to that default with `session_status model=default` if it gets pinned to something else.
- `Elephant` is just the alias for `openrouter/inclusionai/ling-2.6-flash` in the gateway fallback list.
- `serenity` uses a separate Ollama/OpenAI routing setup for local defaults and cloud image/coding tasks.
- The `serenity` OpenAI key lives in `~/.ollama_config/openai.env` and the router script is `~/.ollama_router.sh`.

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
| 2026-06-12 | Tailscale Serve enabled for Control UI — HTTPS, no token paste |
| 2026-06-12 | Avatar re-uploaded for new HTTPS origin |
| 2026-06-12 | All crons fixed for Telegram delivery (was failing with "multiple channels" error) |
| 2026-06-12 | Model allowlist updated to include `:cloud` suffixed variants |
| 2026-06-23 | Gateway default switched to `ollama-cloud/deepseek-v4-pro:cloud`; `Elephant` remains a fallback alias |
| 2026-06-23 | Vanny Van solar fully connected and functioning |
| 2026-06-13 | Home Assistant heartbeat: ~145 unavailable entities (mostly sensors/media_players) |
| 2026-06-14 | Last memory update before today's Ollama setup |

## Promoted From Short-Term Memory (2026-06-27)

<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:11:11 -->
- Conversation Summary: Health summary (read-only) [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:11-11]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:12:15 -->
- Conversation Summary: System uptime: gateway 14m 40s · system 15m 1s (from earlier status snapshot).; Model routing: gateway reports fallback priority (ollama-cloud/deepseek-v4-pro:cloud, ollama-cloud/deepseek-v4-flash:cloud, ollama-cloud/minimax-m2.7:cloud, openai/gpt-5.4, openai/gpt-5.4-mini, openrouter/inclusionai/ling-2.6-flash). No default model set by assistant in this session.; Image API: OpenAI endpoints return 401/400 (no valid key / quota). No OpenAI key present in this workspace.; SVG pipeline: active and serving all 49 posts (each has exactly one artwork reference). [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:12-15]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:16:16 -->
- Conversation Summary: Memory: last flush appended to memory/2026-06-23.md; reference files remain untouched. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:16-16]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:18:18 -->
- Conversation Summary: What I can do (changes require your confirmation) [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:18-18]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:3:5 -->
- Session: 2026-06-23 01:43:09 UTC: **Session Key**: agent:main:main; **Session ID**: 551ea75d-63a3-4b35-8140-8fb5e9fbdca2; **Source**: webchat [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23-0143.md:9:9 -->
- Conversation Summary: assistant: I can run diagnostics but cannot execute changes on your behalf. Here is a read-only health summary; apply any actions only after your explicit confirmation. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23-0143.md:9-9]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23.md:15:17 -->
- Next user action items: 1) If you want live API images: add a valid OpenAI API key (via models.json or .env.local) and tell me which image model to use (e.g., gpt-image-1). 2) To switch providers now: provide the OpenRouter/Ollama model string from your allowlist and the secure key location; I’ll prepare the config change. 3) Otherwise: nothing to do — SVG fallbacks will continue displaying comics. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23.md:15-17]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23.md:20:21 -->
- Notes & observations: Tools and reference files (MEMORY.md, DREAMS.md, SOUL.md, TOOLS.md, AGENTS.md) remain read-only.; No destructive operations performed. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23.md:20-21]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23.md:4:6 -->
- Runtime context: Pre-compaction memory flush triggered at 2026-06-23 01:00 UTC.; Session: OpenClaw runtime continuing after a yield; prior summary noted SVG fallback deployed for all 49 posts and OpenAI image endpoints blocked (401/400).; No breaking changes; system stable. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23.md:4-6]
<!-- openclaw-memory-promotion:memory:memory/2026-06-23.md:9:12 -->
- Decisions made (in this session): SVG fallback pipeline confirmed operational for all 49 blog posts.; OpenAI image API remains inaccessible (401/400). No key present in this workspace.; Model default may have changed to `elephant` via gateway/models.json — no action taken by assistant.; Three forward paths outlined: keep SVG fallback; add valid OpenAI key and switch back to gpt-image-1/2; or switch to OpenRouter/Ollama. [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-23.md:9-12]
