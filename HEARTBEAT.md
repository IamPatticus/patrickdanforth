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
- `1782562831068` (Sat 2026-06-27 12:20 UTC): Ambient API 401 from cron shell; used wttr.in fallback (Walling, TN 76°F sunny). Disk 61% (33G/57G), memory OK. Committed heartbeat-state update. Memory search still offline (OpenAI quota). No urgent items.
- `1782562951089` (Sat 2026-06-27 12:22 UTC): wttr.in fallback: Sunny, 76°F, 76% humidity, 0.00 in rain, 2 mph wind. Disk 61% (33G/57G), memory OK (1.8G used/5.9G available), clean git tree. No urgent items.

## Notes

- Ambient Weather API is flaky from cron shells: returns 401 in non-interactive `source ... && curl` invocations but works in some interactive contexts. Use wttr.in fallback when Ambient fails.
- wttr.in fallback source: Walling, TN (matches Joppa Station 1 location).
- Email/calendar/Signal remain blocked until tooling is configured.
- code_execution sandbox is unavailable due to xAI API credits; use local python3 fallback for quick checks.
