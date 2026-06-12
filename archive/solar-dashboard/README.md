# Solar Dashboard Archive

Archived: 2026-06-11

## What This Was

A live solar production dashboard that displayed real-time power generation
from house and shop solar arrays. Data was fetched from SolarEdge API and
rendered as a scoreboard-style HTML page hosted on patrickdanforth.com.

## Why It Was Archived

- Inconsistent reliability with API data updates
- Manual intervention required too frequently
- Not worth continued maintenance effort

## Files Included

| File | Purpose |
|------|---------|
| `solar_snapshot_generator.py` | Python script to fetch SolarEdge data |
| `solar_scoreboard_github_refresh.sh` | Shell script for GitHub Pages deployment |
| `solar-refresh.yml` | GitHub Actions workflow (copied from .github/workflows/) |
| `solar-scoreboard.html` | The HTML dashboard page |
| `solar-snapshot.json` | Last captured snapshot of solar data |

## To Restore (if ever desired)

1. Restore scripts to `/home/patrick/.openclaw/workspace/scripts/`
2. Restore workflow to `.github/workflows/solar-refresh.yml`
3. Add cron job: `*/15 * * * * cd /home/patrick/.openclaw/workspace && python3 scripts/solar_snapshot_generator.py`
4. Re-add `solar-scoreboard.html` to patrickdanforth-site/

## Notes

- Required SolarEdge API credentials (stored in .env)
- Site used GitHub Pages for hosting
- Cron job ran every 15 minutes on serenity (Mini ITX)
