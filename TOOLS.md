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

### Weather

- Primary station: **Joppa Station 1** in Walling, TN (Ambient Weather)
- API keys: `~/.config/ambientweather.env` (chmod 600)
- Station MAC: `94:3C:C6:91:91:AB`
- API endpoint: `https://api.ambientweather.net/v1/devices`
- Backup source: `wttr.in/Walling+TN`
- Note: applicationKey is the Ambient app key, apiKey is the read-only user API key
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
