# HEARTBEAT.md

- [ ] Check Signal messages (blocked: need phone number in USER.md)
- [ ] Check unread emails (blocked: no email CLI installed — see `email.md`)
- [ ] Check upcoming calendar events (blocked: no calendar CLI, Google token has only Blogger scope — see `calendar.md`)
- [x] Check weather: **Walling, TN** — 76.82°F / feels like 78.15°F, 84% humidity, wind 36° @0.67 mph gusting 2.24 mph. (Ambient API key fix still working.) No rain, last rain Wed Jun 23 03:36 UTC. Lightning sensor battery still low.
- [x] Check disk and memory usage
- [x] Check git workspace status
- [x] Update heartbeat state file

## Notes

- Ambient Weather API works; the env var is `AMBIENT_APP_KEY` and must be passed as the `applicationKey` query param (separate from `apiKey`).
- Email/calendar/Signal remain blocked until tooling is configured.
