# Email Status

_Last checked: Saturday, June 27, 2026 — 4:03 AM UTC_

## Status: Unable to check

No configured email client or IMAP tool is available on this host. Specifically:

- `himalaya` is not installed
- `mutt` / `neomutt` is not installed
- `offlineimap` / `mbsync` is not installed
- Proton Mail Bridge is not running
- No `.env.local` or stored credentials reference an IMAP/SMTP account

## Next Steps

Install/configure an email tool and add account details to `~/.config/` or `TOOLS.md` (without exposing secrets in tracked Markdown) if you want this check to run automatically.
