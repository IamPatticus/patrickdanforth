# Heartbeat Checklist

Rotate through these checks a few times per day.

- Email: any urgent unread messages?
- Calendar: events in the next 24-48h?
- Social mentions/notifications
- Weather if human is going out
- Memory maintenance: review recent daily notes, update MEMORY.md

## Notes

- Email/calendar are handled by the dedicated `weather-email-calendar-check` cron job every 4 hours (isolated session, no chat delivery). The main heartbeat can skip them unless something urgent is suspected.
- Embedding provider quota is currently exhausted, so `memory_search` via embeddings is unavailable. Use file reads for memory maintenance.
