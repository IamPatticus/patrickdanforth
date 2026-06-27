- [ ] Check Signal messages (blocked: need phone number in USER.md)
- [x] Check unread emails: Evolution maildir is empty (0 messages). No active IMAP/Bridge account. (see `email.md`)
- [x] Check upcoming calendar events: Evolution system calendar has 0 events in next 48h. (see `calendar.md`)
- [x] Check weather: **Walling, TN** — 77°F, clear, 72% humidity, ↖5mph. (Ambient API keys unavailable in cron shell; used wttr.in fallback.) No recent rain.
- [x] Check disk and memory usage: 61% disk, memory OK
- [x] Check git workspace status: clean, ahead of site/main by 1
- [x] Update heartbeat state file

## Notes

- Ambient Weather API works; the env var is `AMBIENT_APP_KEY` and must be passed as the `applicationKey` query param (separate from `apiKey`).
- Email/calendar/Signal remain blocked until tooling is configured.
