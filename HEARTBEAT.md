- [ ] Check Signal messages (blocked: need phone number in USER.md)
- [ ] Check unread emails: Evolution maildir is empty (0 messages). No active IMAP/Bridge account. (see `email.md`)
- [ ] Check upcoming calendar events: Evolution system calendar has 0 events in next 48h. (see `calendar.md`)
- [ ] Check weather: Walling, TN — source Joppa Station 1 via Ambient Weather API
- [ ] Check disk and memory usage
- [ ] Check git workspace status
- [ ] Update heartbeat state file

## Recent Runs

- `1782554789625` (Sat 2026-06-27 10:06 UTC): weather refresh, disk, git, memory. No urgent items.
- `1782561750900` (Sat 2026-06-27 12:02 UTC): weather refresh, disk, git, memory. No urgent items.

## Notes

- Ambient Weather API works; env has both `AMBIENT_API_KEY` (apiKey param) and `AMBIENT_APP_KEY` (applicationKey param).
- Email/calendar/Signal remain blocked until tooling is configured.
- code_execution sandbox is unavailable due to xAI API credits; use local python3 fallback for quick checks.
