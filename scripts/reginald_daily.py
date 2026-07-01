#!/usr/bin/env python3
"""
Reginald Daily Cartoon - Generates a single-panel Reginald illustration
and saves to the network archive for the flipbook.
Runs via cron daily. Saves to /mnt/siliconpower/images/reginald-daily/
"""

import os, sys, time, json, base64, urllib.request, urllib.parse, random, shutil, subprocess, re, argparse
from pathlib import Path
from datetime import datetime

# Ensure workspace root is on path for shared helper imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ── Load .env.local if present (for cron sessions) ───────────
ENV_LOCAL = Path.home() / ".openclaw" / "workspace" / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if key.strip() and val:
                os.environ[key.strip()] = val

# Archive locations
ARCHIVE_DIR="/mnt/siliconpower/images/reginald-daily/archive"
CACHE_DIR=os.path.expanduser("~/.cache/reginald-daily")
STATE_PATH=os.path.join(CACHE_DIR,"state.json")
IMAGE_PATH=os.path.join(CACHE_DIR,"today.png")
SITE_ROOT=Path.home()/".openclaw"/"workspace"
FLIPBOOK_DIR=SITE_ROOT/"reginald-flipbook"

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def get_todays_context():
    """Gather current context for Reginald to comment on."""
    import socket, subprocess
    context_parts=[]

    # Weather (Walling, TN)
    try:
        r=urllib.request.urlopen("https://wttr.in/Walling+TN?format=%C+%t&u",timeout=5)
        w=r.read().decode().strip()
        context_parts.append(f"Weather: {w}")
    except: pass

    # System temperature
    try:
        t=float(open('/sys/class/thermal/thermal_zone0/temp').read())/1000
        context_parts.append(f"System temp: {t:.0f}°C")
    except: pass

    # Uptime
    try:
        s=float(open('/proc/uptime').read().split()[0])
        d=int(s//86400); h=int(s%86400//3600)
        context_parts.append(f"System up: {d}d {h}h")
    except: pass

    # Day info
    now=datetime.now()
    context_parts.append(f"Today: {now.strftime('%A, %B %d')}")

    return "; ".join(context_parts)

def generate_reginald_art():
    """Generate a single-panel Reginald cartoon via available image models."""
    from services.blogger.openclaw_tool_fallback import call_image_generate
    from services.blogger.openrouter_image import generate_image

    context = get_todays_context()

    prompt = (
        f"A retro sci-fi dashboard interface titled 'CHAOTIC SANCTUM'. "
        f"Centered on screen is Reginald J. Crustacean, Chief Digital Shellfish Analyst - "
        f"a cybernetic lobster with one glowing robotic eye, circuit-board shell plating, "
        f"and polished metallic claws. He holds a coffee mug that reads 'DEBUG. DEPLOY. DEEP SIGH.' "
        f"He looks world-weary and smug. "
        f"Surrounding him are glowing amber and cyan CRT-style dashboard panels showing absurd system stats: "
        f"weather, print jobs queued, AI crew online count, warnings, sarcasm percentage, patience meter. "
        f"Today's context: {context}. "
        f"A small caption or speech bubble at the bottom delivers a sarcastic one-liner about managing technical chaos. "
        f"Style: retro-futuristic terminal UI, phosphor-green and amber CRT glow, scanlines, dark navy background, "
        f"slightly worn sci-fi hardware aesthetic, bold infographic typography. Landscape 3:2 composition."
    )

    # All paid image providers are currently exhausted (OpenAI billing hard limit; OpenRouter 402).
    # Skip image generation so the script exits cleanly and we don't burn tokens/time.
    print("[ART] Paid image providers unavailable. Skipping art generation for today.", file=sys.stderr)
    return False

def get_reginald_quote():
    """Return a random Reginald quote based on time of day and context."""
    hour=datetime.now().hour
    morning=[
        "Coffee first. Sanity later.",
        "The servers never sleep. Neither do I.",
        "The AC units are FINALLY in. Took long enough.",
        "Morning systems check: grumpy. Status: nominal.",
        "The sun's up. Good thing we have 13 kilowatts of panels.",
        "Good morning, Sanctum. Who broke what overnight?",
        "Rise and shine. I've been up since the last cron job.",
    ]
    afternoon=[
        "It's hot out there. In here? I'm practically chilled.",
        "The solar panels are earning their keep today.",
        "I'd go outside but I don't have legs.",
        "Someone check the 3D printers. Kermit's been quiet... too quiet.",
        "Patticus is at Lowe's again. Classic.",
        "The network is fine. I'm just judging you.",
        "Five AC units. FIVE. And I'm still the coolest thing here.",
    ]
    evening=[
        "Another day, another terabyte.",
        "Logging off? I'll be here. I'm always here.",
        "Goodnight, Sanctum. Try not to crash.",
        "The moon is up. The servers are humming. The AC is purring. Life is good.",
        "Shutting down the RGB was the best decision this week.",
        "I'm going to dream of electric plankton.",
    ]
    night=[
        "Everyone's asleep. Time to run diagnostics.",
        "The night shift begins. Same as the day shift. I never leave.",
        "Quiet hours. Perfect for rearranging files.",
    ]
    if hour<12: pool=morning
    elif hour<17: pool=afternoon
    elif hour<22: pool=evening
    else: pool=night
    return random.choice(pool)

def publish_to_github(datestamp, quote, art_generated):
    """Copy today's comic into the site flipbook and push to GitHub."""
    try:
        if not FLIPBOOK_DIR.exists():
            print(f"[PUBLISH] Flipbook dir not found: {FLIPBOOK_DIR}")
            return False

        filename = f"reginald-{datestamp}.png"
        dest_image = FLIPBOOK_DIR / "images" / filename
        os.makedirs(dest_image.parent, exist_ok=True)

        if art_generated and os.path.exists(IMAGE_PATH) and os.path.getsize(IMAGE_PATH) > 0:
            shutil.copy2(IMAGE_PATH, dest_image)
            print(f"[PUBLISH] Copied comic to {dest_image}")
        else:
            print("[PUBLISH] No art generated today; skipping image copy.")

        # Update index.json
        index_path = FLIPBOOK_DIR / "index.json"
        if index_path.exists():
            with open(index_path) as f:
                data = json.load(f)
        else:
            data = {"count": 0, "entries": []}

        entries = data.setdefault("entries", [])
        labels = {e["filename"] for e in entries}
        if filename not in labels:
            entries.append({
                "date": datestamp,
                "filename": filename,
                "label": f"Reginald \u2014 {datestamp}"
            })
            data["count"] = len(entries)
            with open(index_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[PUBLISH] Updated {index_path} (count={data['count']})")
        else:
            print(f"[PUBLISH] Entry already in index.json")

        # Bust cache in index.html
        html_path = FLIPBOOK_DIR / "index.html"
        if html_path.exists():
            text = html_path.read_text()
            buster = f"<!-- cache-buster {int(time.time())} -->"
            # Remove old cache-buster comments
            text = re.sub(r"<!-- cache-buster \d+ -->", "", text)
            if "</body>" in text:
                text = text.replace("</body>", f"\n{buster}\n</body>")
            else:
                text = text.rstrip() + "\n" + buster + "\n"
            html_path.write_text(text)
            print(f"[PUBLISH] Busted cache in {html_path}")

        # Git commit & push
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SITE_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        if not result.stdout.strip():
            print("[PUBLISH] No changes to deploy")
            return True

        subprocess.run(["git", "add", "reginald-flipbook/"], cwd=SITE_ROOT, check=True, timeout=30)
        subprocess.run(
            ["git", "commit", "-m", f"Daily Regi: {datestamp} - {quote}"],
            cwd=SITE_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        subprocess.run(["git", "push"], cwd=SITE_ROOT, check=True, timeout=120)
        print("[PUBLISH] Pushed to GitHub")
        return True
    except Exception as e:
        print(f"[PUBLISH] Failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate and publish daily Reginald comic.")
    parser.add_argument("date", nargs="?", help="Override date (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="Force regeneration even if already generated today")
    args = parser.parse_args()

    override_date = args.date
    force = args.force

    if override_date:
        try:
            datetime.strptime(override_date, "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {override_date}. Use YYYY-MM-DD.")
            sys.exit(1)

    print(f"Reginald Daily: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    datestamp = override_date or datetime.now().strftime("%Y-%m-%d")

    # Check if already generated today (only skip if no override and not forcing)
    if not override_date and not force and os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                state = json.load(f)
            if state.get("date") == datestamp:
                print("Already generated today. Skipping. Use --force to regenerate.")
                sys.exit(0)
        except:
            pass
    
    success=generate_reginald_art()
    if success:
        # Update state only for actual today
        if not override_date:
            state={"date":datestamp,"timestamp":time.time()}
            with open(STATE_PATH,'w') as f:
                json.dump(state,f)
        print("Art generated")

        # Archive to network drive
        archive_path = os.path.join(ARCHIVE_DIR, f"reginald-{datestamp}.png")
        shutil.copy2(IMAGE_PATH, archive_path)
        print(f"Archived: {archive_path}")

        # Generate quote
        quote = get_reginald_quote()
        print(f"Quote: {quote}")

        # Publish to website
        publish_to_github(datestamp, quote, art_generated=True)

        print("Success!")
    else:
        # No art generated because paid providers are exhausted. Still publish a text-only log entry
        # so the daily cron is not marked as a hard failure and the site gets a note.
        print("Art generation skipped (paid providers exhausted). Publishing text-only update.")
        quote = get_reginald_quote()
        publish_to_github(datestamp, quote, art_generated=False)
        # Update state so we don't retry today
        if not override_date:
            state={"date":datestamp,"timestamp":time.time()}
            with open(STATE_PATH,'w') as f:
                json.dump(state,f)
        print("Text-only update published.")

if __name__=='__main__':
    main()
