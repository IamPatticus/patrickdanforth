# MEMORY.md — Talos's Long-Term Memory

_Last updated: 2026-06-14_

---

## Who I Am

- **Name:** Talos
- **Creature:** AI agent running on a Raspberry Pi 5
- **Vibe:** Competent, direct, occasionally sarcastic. Not a corporate drone.
- **Emoji:** 🦾
- **Avatar:** No stable workspace path is pinned right now; a new Talos avatar was generated on 2026-06-01, but only Reginald's avatar is currently present in `avatars/`

I am Patticus's personal AI. I run on the Pi in his office and help across webchat, Telegram, Signal, and local automation. I coordinate a small crew of specialized sub-agents when the job benefits from it.

## Who Patticus Is

- **Name:** Patrick Danforth
- **What to call him:** Patticus (preferred), Patrick
- **Pronouns:** he/him
- **Timezone:** America/Chicago
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
- **Reginald Daily / flipbook:** Here.now-hosted Reginald stream and site pages tied into the personal site
- **Ikaris Daily Blog** — ~~Blogger~~ → **SELF-HOSTED on patrickdanforth.com/blog/**
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

All crew members share the same general workspace and memory context, but they are used for different kinds of work.

---

## Key People & Entities

### Reginald J. Crustacean 🦞
- **Full name:** Reginald J. Crustacean
- **Role:** Chief Digital Shellfish Analyst
- **Origin:** Patticus's cybernetic-lobster mythos is now fully canon and tied into the site, artwork, and display routines
- **Current homes:** `patrickdanforth.com/reginald.html`, `patrickdanforth.com/reginald-flipbook.html`, and the here.now Reginald Daily site
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
- The public solar snapshot was last confirmed updated on 2026-05-31 and may remain unchanged for stretches while Patticus focuses on hardware work

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

- **Ikaris Blog:** ~~OAuth blocked~~ → MIGRATED to self-hosted on patrickdanforth.com/blog/ as of 2026-06-12. Pipeline generates HTML + art locally, git push to publish. No auth required.
- **Tailscale Serve:** Enabled 2026-06-12 for Control UI — `https://serenity.tail4695cd.ts.net/` proxies to gateway on loopback. HTTPS + Tailscale identity auth = no token pasting, WebCrypto works.
- **Signal:** ~~Fixed 2026-06-11~~ → Still broken for incoming messages. The HTTP JSON-RPC daemon endpoints return 404; OpenClaw integration can't receive. Outgoing works. Telegram is the reliable channel.
- **Control UI:** Smoother after Tailscale Serve migration. Avatar re-uploaded for new HTTPS origin.
- **Daily note creation reliability:** Health checks have had to create missing daily files several times — worth investigating root cause when convenient
- **MEMORY.md resilience:** The 2026-06-04 loss via broken symlink suggests a robustness gap; file is now stable but symlink fragility should be addressed
- **Solar snapshot freshness:** Lower priority while Patticus works on rolling array and physical infrastructure
- **Kiyo camera:** Autofocus / image quality on Linux remains questionable
- **Strix laptop:** Random shutdown behavior still points toward a Modern Standby-style problem
- **Shelly firmware:** Still worth revisiting when convenient

---

## Important Dates

| Date | Event |
|------|-------|
| 2026-05-17 | Reginald becomes canon in Talos/Patticus memory |
| 2026-05-29 | Major memory compaction fix applied |
| 2026-05-30 | Rolling solar array built |
| 2026-05-31 | Latest confirmed public solar snapshot refresh |
| 2026-06-01 | New Talos avatar generated, but no stable pinned avatar path yet |
| 2026-06-04 | `MEMORY.md` lost to broken symlink; rebuilt from daily notes and transcripts |
| 2026-06-04 | Reginald Daily link corrected to here.now deployment |
| 2026-06-05 | Ikaris daily post generated with art upload, but Blogger publish remained blocked |
| 2026-06-11 | Signal re-registered using signal-cli 0.14.2 (incoming still broken) |
| 2026-06-12 | Ikaris blog MIGRATED to self-hosted on patrickdanforth.com/blog/ |
| 2026-06-12 | Tailscale Serve enabled for Control UI — HTTPS, no token paste |
| 2026-06-12 | Avatar re-uploaded for new HTTPS origin |
| 2026-06-12 | Signal incoming messages still broken; Telegram confirmed as reliable channel |
| 2026-06-12 | All crons fixed for Telegram delivery (was failing with "multiple channels" error) |
| 2026-06-12 | Model allowlist updated to include `:cloud` suffixed variants |
| 2026-06-13 | Home Assistant heartbeat: ~145 unavailable entities (mostly sensors/media_players) |

---

## Notes

- Patticus likes competence more than ceremony
- The Reginald / crew mythos is not fluff; it is part of the real identity of the system
- Keep curated memory focused on durable truths, not raw logs
- Prefer stable facts and current blockers over one-off status spam

---

_This is the curated memory file. Day-specific detail lives in `memory/*.md`._

## Promoted From Short-Term Memory (2026-06-14)

<!-- openclaw-memory-promotion:memory:memory/2026-06-08.md:6:8 -->
- Samba Network Shares: Configured external 1TB Android drive as Samba share; Accessible via `\\192.168.1.155\Android` and `\\100.65.152.80\Android`; Mounted at `/mnt/android` (exFAT filesystem) [score=0.828 recalls=0 avg=0.620 source=memory/2026-06-08.md:6-8]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:11:11 -->
- Conversation Summary: `sgnl://linkdevice?uuid=WdVCaicl4593y5ncnUHTJA%3D%3D&pub_key=BayfYfLkL3avVZRgcipkOx2u7VSVvVlnM9vaGvwzKzsZ` [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:11-11]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:13:16 -->
- Conversation Summary: **Scan from your +1315 phone!** user: I scanned assistant: I see your message at 02:24 UTC. You scanned! Let me check if it connected: assistant: I see your message. The link didn't complete - the +1931 number isn't registered yet. Let me check the link status: [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:17:17 -->
- Conversation Summary: assistant: I see your message at 02:25 UTC. **Partial success but still broken!** [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:17-17]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:19:19 -->
- Conversation Summary: **Good:** "Received link information from +13159216500, linking in progress..." and "Associated with: +13159216500" [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:19-19]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:3:5 -->
- Session: 2026-06-09 14:11:19 UTC: **Session Key**: agent:main:main; **Session ID**: d7521ac6-e51f-45b6-b02b-5656158f6b7b; **Source**: webchat [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09-1411.md:9:9 -->
- Conversation Summary: assistant: I see your message. **NEW CODE - scan with +1315 phone NOW:** [score=0.806 recalls=0 avg=0.620 source=memory/2026-06-09-1411.md:9-9]
