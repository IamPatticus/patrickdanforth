# Email Status

_Last checked: Tuesday, June 30, 2026 — 12:02 AM UTC_

## Status: No unread mail locally; no active IMAP/Bridge account

- **Evolution Mail:** `~/.local/share/evolution/mail` exists but is empty (trash only; 0 messages, 0 unread).
- **CLI tools:** `himalaya`, `mutt`/`neomutt`, `offlineimap`/`mbsync` are not installed.
- **Proton Mail Bridge:** not running; no Proton-related user services or maildirs found.
- **Stored credentials:** no IMAP/SMTP credentials found in `~/.config/` or `.env.local`.
- **Google token:** only has Blogger scope (`https://www.googleapis.com/auth/blogger`); Gmail is not accessible.

## Next Steps

If email checks should include a real inbox, configure an email sync tool or Proton Bridge and add non-secret account pointers to `TOOLS.md`.
