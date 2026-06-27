# Calendar Status

_Last checked: Saturday, June 27, 2026 — 12:04 AM UTC_

## Status: Unable to check

No calendar CLI is available and the existing Google token (`~/.config/google/token.json`) only has **Blogger** scope. Specifically:

- `gcalcli` is not installed
- `khal` / `calcurse` / `vdirsyncer` are not installed
- Google credentials in `~/.config/google/credentials.json` belong to project `ikaris-blog` with only Blogger scope

## Next Steps

To enable calendar checks, either:

1. Install `gcalcli` and re-authorize with Calendar scope, or
2. Provide a CalDAV URL/credentials for a self-hosted calendar
