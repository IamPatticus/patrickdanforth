- [ ] Check Signal messages (blocked: need phone number in USER.md)
- [ ] Check unread emails (blocked: no email CLI installed — see `email.md`)
- [ ] Check upcoming calendar events (blocked: no calendar CLI, Google token has only Blogger scope — see `calendar.md`)
- [x] Check weather: **Walling, TN** — 77°F, clear, 72% humidity, ↖5mph. (Ambient API keys unavailable in cron shell; used wttr.in fallback.) No recent rain.
- [x] Check disk and memory usage
- [x] Check git workspace status
- [x] Update heartbeat state file

## Notes

- Ambient Weather API works; the env var is `AMBIENT_APP_KEY` and must be passed as the `applicationKey` query param (separate from `apiKey`).
- Email/calendar/Signal remain blocked until tooling is configured.
