# Working Context — Talos Sykeus

_Last updated: 2026-06-02 18:00 CDT_

## Current Session
- **Task:** Evening heartbeat — 6pm CDT. All systems nominal. No active user session.

## Active Context
- OpenClaw **2026.5.22** — upgraded 2026-05-24 via install script (reliable path)
- **Primary model:** `ollama/kimi-k2.6:cloud` (switched from deepseek-v4-pro, which was occasionally slipping into Chinese)
- **Fallbacks:** DeepSeek V4 Flash → GPT-5.4-mini → Minimax → Elephant
- **Proton Pass:** Migrated 2026-05-27; now source of truth for crew credentials. Talos AI agent expires 2027-05-27.
- **Nexus sidekick:** Built 2026-05-27, running on Pi Zero 2 W with Whisplay LCD. Polling solar + Talos messages. Sleep schedule 10pm off / 8am on.
- **Ragnar security appliance:** Tuned 2026-05-27 after overload. Swappiness 10, AI commentary disabled, minimal cron jobs.
- **Anker Solix F3800:** Delivered 2026-05-23 at $1,800. Rolling solar canopy blueprint saved to NVMe.
- **Credential migration:** Home Assistant, Google Blogger, OpenAI API all now read from Proton Pass via `passbridge.py`.
- **Solar systems:** House (4,560W + 20kWh), Shop (2,960W + 19.2kWh), AC array (3,150W), Mini-splits (1,410W + 1,110W). Total: 13,190W solar, 39.2kWh battery.
- **Pironman 5 Max:** RGB schedule ON 8am / OFF 10pm. IR receiver on GPIO 13 untested.

## Recent Activity (last 3 days)
- **2026-06-01:** Memory health checkpoints — nightly flagged missing daily note (auto-created), morning all green.
- **2026-06-02:** Quiet day. No user interactions logged. Morning health checkpoint all green. Evening heartbeat in progress.
- **2026-05-31 08:01:** Morning report delivered via Telegram successfully.
- **Patticus communication preference:** Control UI for real conversations, Telegram for important pings. (Noted 2026-05-30 evening.)

## Blocked / Waiting
- Shelly firmware update (1.7.5 lockup bug)
- Strix random shutdowns (Modern Standby suspected)
- ComfyUI bridge (network reachability / Windows Firewall)
- Headache Log Wear OS tile verification
- Whoop dashboard (API 404s)
- YouTube Music skill (HttpOnly cookie auth blocked)
- Pi Connect screen sharing (client-side connection fails)
- Bluetooth keyboard (BLE SSP mismatch)
- Touchscreen (ADS7846 hardware fault suspected)

## Memory Health
- Nightly GitHub backup: **healthy** (last: 2026-05-31 03:00 CDT)
- Daily notes: current through 2026-06-02
- Vector memory: PostgreSQL + pgvector, flush after meaningful updates
- This file will be updated every session start and every 3-5 tool calls

---
_Write at session start, every 3-5 tool calls, and at task completion._
