#!/usr/bin/env python3
"""
Reginald Daily Cartoon — Generates a single-panel Reginald illustration
and saves to the network archive for the flipbook.
Runs via cron daily. Saves to /mnt/siliconpower/images/reginald-daily/
"""

import os, sys, time, json, base64, urllib.request, urllib.parse, random, shutil
from pathlib import Path
from datetime import datetime

# Archive locations
ARCHIVE_DIR="/mnt/siliconpower/images/reginald-daily/archive"
CACHE_DIR=os.path.expanduser("~/.cache/reginald-daily")
STATE_PATH=os.path.join(CACHE_DIR,"state.json")
IMAGE_PATH=os.path.join(CACHE_DIR,"today.png")

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
    """Generate a single-panel Reginald cartoon using OpenAI."""
    context=get_todays_context()
    
    prompt=(
        f"A single-panel comic panel of Reginald, a cyborg lobster. "
        f"Reginald has circuit-board shell patterns, a glowing cyan cybernetic eye, "
        f"and metallic claws. He lives inside a computer network called the Chaotic Sanctum. "
        f"He is sardonic, witty, and slightly grumpy — the world-weary Chief Digital Shellfish Analyst. "
        f"He comments on the tech chaos, solar systems, print farm, and AI crew (Talos, Ikaris, Daedalus). "
        f"Today's context: {context}. "
        f"Style: bold comic book line art with flat vibrant colors, dark background, "
        f"red and orange neon accents. Comic book panel layout — Reginald should be the focus "
        f"in a single comic panel with a small caption area at the bottom. "
        f"A small dialogue bubble or caption below the character. "
        f"Landscape composition — a wide single comic panel that fills a 3:2 screen. "
        f"Reginald centered in the frame with the Chaotic Sanctum network environment around him. "
    )
    
    try:
        from openai import OpenAI
        client=OpenAI()
        response=client.images.generate(
            prompt=prompt,
            model="gpt-image-2",
            size="1536x1024",
            quality="medium",
            n=1
        )
        img_data=response.data[0]
        if img_data.url:
            import requests as req
            r=req.get(img_data.url,timeout=60)
            if r.status_code==200:
                with open(IMAGE_PATH,'wb') as f:
                    f.write(r.content)
                return True
        elif img_data.b64_json:
            with open(IMAGE_PATH,'wb') as f:
                f.write(base64.b64decode(img_data.b64_json))
            return True
    except Exception as e:
        print(f"Generation error: {e}",file=sys.stderr)
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

def main():
    print(f"Reginald Daily: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Check if already generated today
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH) as f:
                state = json.load(f)
            if state.get("date") == datetime.now().strftime("%Y-%m-%d"):
                print("Already generated today. Skipping.")
                sys.exit(0)
        except:
            pass
    
    success=generate_reginald_art()
    if success:
        datestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Update state
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
        
        print("Success!")
    else:
        print("Generation failed")
        sys.exit(1)

if __name__=='__main__':
    main()
