#!/usr/bin/env python3
"""
Ikaris Daily Blogger Pipeline
Usage: python3 ikaris_pipeline.py "<title>" "<story>" [tags...]

Steps:
1. Generate AI art via OpenAI DALL-E
2. Upload art to Imgur
3. Post story + art to Blogger
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
import pickle
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BLOGGER_BLOG_ID = "17325791"
GOOGLE_CREDS_PATH = Path.home() / ".config" / "google" / "credentials.json"
GOOGLE_TOKEN_PATH = Path.home() / ".config" / "google" / "token.json"
IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID", "")
OUTPUT_DIR = Path.home() / "Pictures" / "ikaris"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/blogger"]

# ── Story Input ────────────────────────────────────────────────

if len(sys.argv) < 3:
    print("Usage: ikaris_pipeline.py '<title>' '<story>' [tags...]")
    sys.exit(1)

TITLE = sys.argv[1]
STORY = sys.argv[2]
TAGS = sys.argv[3:] if len(sys.argv) > 3 else ["ikaris", "mythical-ai", "short-story", "ai-fiction"]

art_url = None
status = {"art_generated": False, "imgur_uploaded": False, "blogger_posted": False}

# ── Step 1: Generate AI Art ────────────────────────────────────

def generate_art(title, story):
    """Generate art via OpenAI DALL-E, return local file path."""
    if not OPENAI_API_KEY:
        print("[ART] No OPENAI_API_KEY — skipping art generation")
        return None

    prompt = (
        f"A dreamlike, ethereal sci-fi illustration inspired by the story titled '{title}'. "
        f"Atmospheric, painterly, cosmic scale, luminous color palette, cinematic composition. "
        f"The mood: {story[:200]}"
    )

    print(f"[ART] Generating image...")
    print(f"[ART] Prompt: {prompt[:120]}...")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps({
            "model": "gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "auto"
        }).encode(),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        data = json.loads(resp.read())
        item = data["data"][0]

        # Newer models return b64_json directly, older ones return a URL
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
        local_path = OUTPUT_DIR / f"ikaris_{timestamp}.png"
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
        # Try anonymous upload as fallback
        client_id = "546c25a59c58ad7"  # Imgur public anonymous client ID
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
            "User-Agent": "Ikaris-Pipeline/1.0"
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
        except Exception as e:
            print(f"[AUTH] Failed to load token: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[AUTH] Refreshing expired token...")
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(GOOGLE_TOKEN_PATH, "w") as f:
                    f.write(creds.to_json())
                print("[AUTH] Token refreshed")
            except Exception as e:
                print(f"[AUTH] Token refresh failed: {e}")
                return None
        else:
            print("[AUTH] No valid credentials — needs interactive OAuth")
            return None

    return creds

# ── Step 4: Post to Blogger ────────────────────────────────────

def post_to_blogger(title, story, image_url, tags):
    """Post story to Blogger via Google API."""
    creds = get_blogger_credentials()
    if not creds:
        print("[BLOGGER] No valid credentials — falling back to text-only via API key")

    # Build HTML content
    html = f"<p>{story}</p>"
    if image_url:
        html = (
            f'<div style="text-align:center;margin:20px 0;">'
            f'<img src="{image_url}" alt="{title}" style="max-width:100%;border-radius:8px;" />'
            f'</div>\n{html}'
        )

    if creds:
        # Use OAuth
        import googleapiclient.discovery
        service = googleapiclient.discovery.build("blogger", "v3", credentials=creds)
        post_body = {
            "kind": "blogger#post",
            "title": title,
            "content": html,
            "labels": tags
        }
        try:
            post = service.posts().insert(blogId=BLOGGER_BLOG_ID, body=post_body).execute()
            url = post["url"]
            print(f"[BLOGGER] Posted: {url}")
            return url
        except Exception as e:
            print(f"[BLOGGER] OAuth post failed: {e}")
            return None
    else:
        # Try using Blogger API v3 with API key if available
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
print(f"📖 Ikaris Daily Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"📝 Title: {TITLE}")
print("═" * 50)

# Step 1: Art
art_path = generate_art(TITLE, STORY)
if art_path:
    status["art_generated"] = True

    # Step 2: Imgur
    art_url = upload_to_imgur(art_path)
    if art_url:
        status["imgur_uploaded"] = True
else:
    print("[PIPELINE] Art generation failed — will post text-only")

# Step 3: Blogger
blog_url = post_to_blogger(TITLE, STORY, art_url, TAGS)
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
