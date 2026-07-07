# OpenClaw Heartbeat Artifact

## Purpose
Batch periodic checks for an OpenClaw agent: environment readiness, storage/entropy, and critical skills (browser, notion, portainer). Designed to be run ~every 30 minutes via Cron.

## Run Schema
- runId: string (ISO timestamp or UUID)
- timestamp: ISO timestamp
- hostname: string
- checks:
  - env: { status: "ok" | "warn" | "fail", details: string }
  - storage: { status: "ok" | "warn" | "fail", details: string }
  - entropy: { status: "ok" | "warn" | "fail", details: string }
  - skills: { [skillName]: { status: "ok" | "warn" | "fail", details: string } }
- summary: string
- recommendations: string[]
- nextDue: ISO timestamp

## Last Checks
```json
{
  "runId": "caca8ecb-8ffc-4739-87e9-b9c0f4590de6",
  "timestamp": "2026-07-06T08:06:19Z",
  "hostname": "serenity",
  "checks": {
    "env": { "status": "ok", "details": "OPENCLAW_SERVICE_KIND=gateway, OPENCLAW_SERVICE_VERSION=2026.6.11, PATH includes expected locations" },
    "storage": { "status": "ok", "details": "Root filesystem 70% used (57G total, 38G used, 17G avail)" },
    "entropy": { "status": "ok", "details": "Sufficient entropy available (256 bits)" },
    "skills": {
      "browser-automation": { "status": "ok", "details": "Skill directory present under ~/.openclaw/extensions/whisplay-im/ and contains valid SKILL.md" },
      "notion": { "status": "warn", "details": "No top-level notion/SKILL.md found in ~/.openclaw/skills/; may be installed as plugin under agents/" },
      "portainer": { "status": "ok", "details": "Skill file present at ~/.openclaw/workspace/skills/portainer/SKILL.md with valid metadata" }
    }
  },
  "summary": "All critical checks passed. Environment healthy; storage at 70% (ok); entropy sufficient; browser-automation and portainer skills available. Notion skill not found at expected location — verify if plugin-only deployment is intended.",
  "recommendations": [],
  "nextDue": "2026-07-06T08:36:00Z"
}
```

## Quick Links
- Skills: list available via OpenClaw API (`openclaw gateway skills list` equivalent).
- Heartbeat template: this file.
- Subagent task: run batched checks and update this artifact.

## Recommendations
- None at this time.

## Next Run
Scheduled for ~2026-07-06T08:36:00Z (30 minutes after last run).

## Run 20260706090500
- timestamp: Mon 2026-07-06 09:05 UTC
- runId: 20260706090500
- hostname: serenity
- checks:
  - env: ok
  - storage: ok  
  - entropy: ok
  - skills: browser-automation=ok, notion=ok

## Run 20260706154400 (current heartbeat poll)
- timestamp: 2026-07-06T15:44:40Z
- runId: 20260706154400
- hostname: serenity
- checks:
  - env: ok
  - storage: ok
  - entropy: ok
  - skills: browser-automation=ok, notion=ok, portainer=ok
- summary: All good — heartbeat poll responded successfully.
- recommendations: none
- nextDue: 2026-07-06T16:14:40Z
## Run 20260707035309
- timestamp: 2026-07-07T03:53:09Z
- env: ok
- storage: warn
- entropy: ok
- skills: browser=warn, notion=ok
