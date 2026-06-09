#!/usr/bin/env python3
"""
Reginald Weekly Comic Pipeline
Usage: python3 reginald_pipeline.py "<title>" "<script>" [tags...]

Steps:
1. Generate comic art via OpenAI DALL-E
2. Upload art to Imgur
3. Post comic + art to Blogger
4. Fall back to text-only if art generation fails
"""

import sys
import json
import os
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BLOGGER_BLOG_ID = "3957427683803276823"
GOOGLE_CREDS_PATH = Path.home() / ".config" / "google" / "credentials.json"
GOOGLE_TOKEN_PATH = Path.home() / ".config" / "google" / "token.json"
IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID", "")
OUTPUT_DIR = Path.home() / "Pictures" / "reginald"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/blogger"]

# ── Script Input ───────────────────────────────────────────────

if len(sys.argv) < 3:
    print("Usage: reginald_pipeline.py '<title>' '<script>' [tags...]")
    sys.exit(1)

TITLE = sys.argv[1]
SCRIPT = sys.argv[2]
TAGS = sys.argv[3:] if len(sys.argv) > 3 else ["reginald", "comic-strip", "cyborg-lobster", "chaotic-sanctum", "webcomic"]

art_url = None
status = {"art_generated": False, "imgur_uploaded": False, "blogger_posted": False}

# ── Step 1: Generate Comic Art ─────────────────────────────────

def generate_art(title, script):
    """Generate comic panel art via OpenAI DALL-E, return local file path."""
    if not OPENAI_API_KEY:
        print("[ART] No OPENAI_API_KEY — skipping art generation")
        return None

    # Craft a comic-style prompt from the script
    prompt = (
        f"A 4-panel comic strip in bold, vibrant comic book style with thick ink lines, "
        f"halftone dots, and dramatic colors. The main character is Reginald, a cyborg lobster "
        f"with cybernetic claws, glowing optical sensors, and steam vents on his carapace. "
        f"He works in a chaotic tech office called the Chaotic Sanctum. "
        f"Title: '{title}'. The scene: {script[:400]}"
    )

    print(f"[ART] Generating comic art...")
    print(f"[ART] Prompt preview: {prompt[:150]}...")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps({
            "model": "gpt-image-2",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "auto"
        }).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        item = data["data"][0]

        if "b64_json" in item:
            img_data = base64.b64decode(item["b64_json"])
        elif "url" in item:
            image_url = item["url"]
            img_req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            img_data = urllib.request.urlopen(img_req, timeout=60).read()
        else:
            print(f"[ART] Unknown response format: {list(item.keys())}")
            return None

        revised_prompt = item.get("revised_prompt", prompt)
        print(f"[ART] Generated. Image size: {len(img_data)} bytes")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_path = OUTPUT_DIR / f"reginald_{timestamp}.png"
        local_path.write_bytes(img_data)
        print(f"[ART] Saved to {local_path}")
        return str(local_path)

    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"[ART] OpenAI API error: {e.code} — {body[:200]}")
        return None
    except Exception as e:
        print(f"[ART] Failed: {e}")
        return None

# ── Step 2: Upload to Imgur ────────────────────────────────────

def upload_to_imgur(image_path):
    """Upload image to Imgur, return public URL."""
    if not IMGUR_CLIENT_ID:
        print("[IMGUR] No IMGUR_CLIENT_ID — trying anonymous upload...")
        client_id = "546c25a59c58ad7"
    else:
        client_id = IMGUR_CLIENT_ID

    print(f"[IMGUR] Uploading {image_path}...")

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    req = urllib.request.Request(
        "https://api.imgur.com/3/image",
        data=urllib.parse.urlencode({"image": img_b64, "type": "base64"}).encode(),
        headers={
            "Authorization": f"Client-ID {client_id}",
            "User-Agent": "Reginald-Pipeline/1.0"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        if data.get("success"):
            url = data["data"]["link"]
            print(f"[IMGUR] Uploaded: {url}")
            return url
        else:
            print(f"[IMGUR] Failed: {data}")
            return None
    except Exception as e:
        print(f"[IMGUR] Error: {e}")
        return None

# ── Step 3: Google OAuth ───────────────────────────────────────

def get_blogger_credentials():
    """Get or refresh Blogger OAuth credentials."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("[AUTH] Missing google-auth packages")
        return None

    creds = None
    if GOOGLE_TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_PATH), SCOPES)
        except Exception:
            pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(GOOGLE_TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
                return creds
            except Exception as e:
                print(f"[AUTH] Token refresh failed: {e}")
                return None
        else:
            if GOOGLE_CREDS_PATH.exists():
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CREDS_PATH), SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(GOOGLE_TOKEN_PATH, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"[AUTH] OAuth flow failed: {e}")
                    return None
            else:
                print("[AUTH] No credentials.json found")
                return None

    return creds

# ── Step 4: Post to Blogger ────────────────────────────────────

def format_script_html(script, art_url):
    """Convert comic script text into Blogger-friendly HTML."""

    # Clean up the script for display
    lines = script.strip().split("\n")
    panels_html = ""
    current_panel = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("panel "):
            if current_panel:
                panels_html += f'<div class="comic-panel">{current_panel.strip()}</div>\n'
            current_panel = f"<p>{line}</p>\n"
        else:
            current_panel += f"<p>{line}</p>\n"

    if current_panel:
        panels_html += f'<div class="comic-panel">{current_panel.strip()}</div>\n'

    # Build post HTML
    html = '<div class="reginald-comic">\n'

    if art_url:
        html += f'<div class="comic-art"><img src="{art_url}" alt="{TITLE}" style="max-width:100%;height:auto;border:3px solid #222;border-radius:8px;" /></div>\n'

    html += f'<div class="comic-script" style="margin-top:20px;font-family:Georgia,serif;">\n'
    html += f'<p><em>A Reginald comic by the Chaotic Sanctum</em></p>\n'
    html += panels_html
    html += '</div>\n</div>'

    return html


def post_to_blogger(title, script, art_url, tags):
    """Post the comic to Blogger."""
    print(f"[BLOGGER] Posting '{title}'...")

    html = format_script_html(script, art_url)

    creds = get_blogger_credentials()
    if creds:
        try:
            from googleapiclient.discovery import build
            service = build("blogger", "v3", credentials=creds)
            post_body = {
                "kind": "blogger#post",
                "title": title,
                "content": html,
                "labels": tags
            }
            post = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post_body).execute()
            url = post.get("url", "")
            print(f"[BLOGGER] Posted via OAuth: {url}")
            return url
        except Exception as e:
            print(f"[BLOGGER] OAuth post failed: {e}")
            return None
    else:
        api_key = os.environ.get("BLOGGER_API_KEY", "")
        if not api_key:
            print("[BLOGGER] No BLOGGER_API_KEY — cannot post")
            return None

        req = urllib.request.Request(
            f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts?key={api_key}",
            data=json.dumps({
                "kind": "blogger#post",
                "title": title,
                "content": html,
                "labels": tags
            }).encode(),
            headers={"Content-Type": "application/json"}
        )

        try:
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            url = data.get("url", "")
            print(f"[BLOGGER] API key post: {url}")
            return url
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            print(f"[BLOGGER] API error: {e.code} — {body[:300]}")
            return None

# ── Main Pipeline ──────────────────────────────────────────────

print("═" * 50)
print(f"🦞 Reginald Weekly Comic Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"📝 Title: {TITLE}")
print("═" * 50)

# Step 1: Art
art_path = generate_art(TITLE, SCRIPT)
if art_path:
    status["art_generated"] = True

    # Step 2: Imgur
    art_url = upload_to_imgur(art_path)
    if art_url:
        status["imgur_uploaded"] = True
else:
    print("[PIPELINE] Art generation failed — will post text-only")

# Step 3: Blogger
blog_url = post_to_blogger(TITLE, SCRIPT, art_url, TAGS)
if blog_url:
    status["blogger_posted"] = True

# ── Summary ────────────────────────────────────────────────────

print("═" * 50)
print("📊 Pipeline Complete")
print(f"   Art generated:  {'✅' if status['art_generated'] else '❌'}")
print(f"   Imgur uploaded: {'✅' if status['imgur_uploaded'] else '❌'}")
print(f"   Blogger posted: {'✅' if status['blogger_posted'] else '❌'}")
if art_url:
    print(f"   Art URL: {art_url}")
if blog_url:
    print(f"   Blog URL: {blog_url}")
print("═" * 50)

# Output JSON for programmatic use
print(json.dumps({"title": TITLE, "art_url": art_url, "blog_url": blog_url, "status": status}))
