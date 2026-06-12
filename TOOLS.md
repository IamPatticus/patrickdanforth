# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Signal

- **Working binary:** `~/bin/signal-cli-0.14.2`
- **Signal number (CLI):** +19313660659
- **Personal number:** +13159216500
- **Data directory:** `~/.local/share/signal-cli/data/`

**Usage:**
```bash
~/bin/signal-cli-0.14.2 -a +19313660659 send +13159216500 -m "Message here"
```

**Important:** Version 0.14.4.1 has JSON serialization bugs that break sending. Stay on 0.14.2.

---

## Related

- [Agent workspace](/concepts/agent-workspace)
