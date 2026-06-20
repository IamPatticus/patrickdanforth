## Backburner / Future Projects

### Pi Zero 2 W ADS-B Plane Tracker
- **Status:** Planned — not started
- **Hardware needed:** Pi Zero 2 W + RTL-SDR dongle (NESDR or RTL2832U w/ R820T2 tuner, ~$25-35) + 1090MHz tuned antenna
- **Software stack:** `dump1090-mutability` or `dump1090-fa` for ADS-B decoding, optional PiAware / ADSBExchange feeder
- **Notes:** Zero 2 W quad-core A53 can comfortably decode hundreds of aircraft; low power draw (~1-3W), runs headless over WiFi. Simple ground-plane antenna can be DIY from coat-hanger wire. Whole thing can go in a weatherproof box with POE splitter on the roof.
- **Use case:** Local web map of nearby air traffic; optional feed to FlightAware/ADS-B Exchange
- **Added:** 2026-06-20

# projects.md

_Last updated: 2026-06-07_

## Active Projects

### Solar Systems
- **Status:** Active
- **Current state:** House (4,560W), shop (2,960W), and rolling array built on 2026-05-30
- **Recent change:** Public solar snapshot was last confirmed updated on 2026-05-31; freshness is currently lower priority than physical build work

### patrickdanforth.com
- **Status:** Active
- **Current state:** Personal site is live in-repo with `CNAME` set to `patrickdanforth.com`
- **Recent change:** Reginald Daily link was corrected on 2026-06-04 to point to the here.now deployment
- **DNS:** Squarespace registrar → GitHub Pages (CNAME + A records); full reference in `memory/patrickdanforth-dns-setup.md`

### Reginald Daily / Flipbook
- **Status:** Active
- **Current state:** Reginald pages and flipbook are part of the personal-site ecosystem
- **Recent change:** June 4 link corrected to here.now deployment

### Ikaris Daily
- **Status:** Blocked on auth
- **Current state:** Writing/image pipeline exists and can generate artwork; Blogger publish path is blocked
- **Recent change:** June 5 post ("The Last Cartographer of Silence") produced with art uploaded to Imgur, but browser-based OAuth re-auth is still needed

### Headache Log
- **Status:** Active
- **Current state:** Still an ongoing core app for headache, trigger, and medication tracking

### Memory / Automation Reliability
- **Status:** Needs watching
- **Current state:** `MEMORY.md` was lost due to a broken symlink on 2026-06-04 and rebuilt from daily notes and transcripts; now stable but the symlink fragility is a known gap
- **Recent change:** Daily note auto-creation missed multiple days in early June and had to self-heal (Jun 1, 4, 6, 7)
