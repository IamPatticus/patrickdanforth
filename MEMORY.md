# MEMORY.md — Talos's Long-Term Memory

_Last updated: 2026-06-07_

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
- **Ikaris Daily:** AI-assisted writing pipeline with image generation and upload support; Blogger publishing is currently blocked on OAuth re-auth

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

- **Ikaris Blogger auth:** OAuth is currently blocked; the pipeline can still generate content and images, but publishing needs fresh browser-based re-auth (last attempted 2026-06-05, produced post + art but could not publish)
- **Daily note creation reliability:** Health checks have had to create missing daily files several times this week — worth investigating root cause when convenient
- **MEMORY.md resilience:** The 2026-06-04 loss via broken symlink suggests a robustness gap; the file is now stable but the underlying cause (symlink fragility) should be addressed
- **Solar snapshot freshness:** Lower priority while Patticus works on the rolling array and other physical infrastructure
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

---

## Notes

- Patticus likes competence more than ceremony
- The Reginald / crew mythos is not fluff; it is part of the real identity of the system
- Keep curated memory focused on durable truths, not raw logs
- Prefer stable facts and current blockers over one-off status spam

---

_This is the curated memory file. Day-specific detail lives in `memory/*.md`._
