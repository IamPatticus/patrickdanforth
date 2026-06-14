#!/usr/bin/env python3
"""
Rockin Regi Pipeline — Self-Hosted
Usage: python3 rockinregi_pipeline.py "<title>" "<script>" [comic|log|patch] [tags...]

Workflow:
1. Generate comic art via OpenAI DALL-E (optional for log entries)
2. Save art to rockinregi-images/ folder
3. Generate HTML post file in rockinregi/ folder
4. Update rockinregi/index.html and feed.xml
5. Commit + push to GitHub

No Blogger OAuth needed!
"""

import sys
import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "rockinregi"
IMAGES_DIR = SITE_ROOT / "rockinregi-images"
BLOG_INDEX = POSTS_DIR / "index.html"
FEED_FILE = POSTS_DIR / "feed.xml"

# ── Story Input ────────────────────────────────────────────────

if len(sys.argv) < 3:
    print("Usage: rockinregi_pipeline.py '<title>' '<script>' [comic|log|patch] [tags...]")
    print("  type: comic (default) | log | patch")
    sys.exit(1)

TITLE = sys.argv[1]
SCRIPT = sys.argv[2]
POST_TYPE = sys.argv[3] if len(sys.argv) > 3 else "comic"
TAGS = sys.argv[4:] if len(sys.argv) > 4 else ["reginald", "chaotic-sanctum"]

DATE_STR = datetime.now().strftime("%Y-%m-%d")
TIME_STR = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

art_path = None
status = {"art_generated": False, "post_created": False, "deployed": False}

# ── Step 1: Generate Comic Art ──────────────────────────────

def generate_art(title, script):
    """Generate comic art via OpenAI DALL-E, return local file path."""
    if POST_TYPE == "log":
        print("[ART] Log entry — skipping art generation")
        return None
    if not OPENAI_API_KEY:
        print("[ART] No OPENAI_API_KEY — skipping art generation")
        return None

    import urllib.request
    import base64

    if POST_TYPE == "patch":
        style = "A satirical software patch notes illustration in bold, vibrant comic book style with thick ink lines, halftone dots, and dramatic colors."
    else:
        style = "A 4-panel comic strip in bold, vibrant comic book style with thick ink lines, halftone dots, and dramatic colors."

    prompt = (
        f"{style} The main character is Reginald, a cyborg lobster "
        f"with cybernetic claws, glowing optical sensors, and steam vents on his carapace. "
        f"He works in a chaotic tech office called the Chaotic Sanctum. "
        f"Title: '{title}'. The scene: {script[:400]}"
    )

    print(f"[ART] Generating {POST_TYPE} art...")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps({
            "model": "gpt-image-2",
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

        if "b64_json" in item:
            img_data = base64.b64decode(item["b64_json"])
        elif "url" in item:
            image_url = item["url"]
            img_req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            img_data = urllib.request.urlopen(img_req, timeout=60).read()
        else:
            print("[ART] Unknown response format")
            return None

        print(f"[ART] Generated. Image size: {len(img_data)} bytes")

        slug = "_".join(re.sub(r'[^\w\s]', '', title).lower().split()[:4])
        local_path = IMAGES_DIR / f"regi_{DATE_STR}_{slug}.png"
        local_path.write_bytes(img_data)
        print(f"[ART] Saved to {local_path}")
        return local_path
    except Exception as e:
        print(f"[ART] Generation failed: {e}")
        return None

# ── Step 2: Generate HTML Post ──────────────────────────────

def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_post_html():
    """Generate the HTML post file."""
    slug = "_".join(re.sub(r'[^\w\s]', '', TITLE).lower().split()[:6])
    post_file = POSTS_DIR / f"{DATE_STR}-{slug}.html"

    type_colors = {
        "comic": ("rgba(255,0,128,.10)", "#ff0080", "rgba(255,0,128,.25)", "Comic Strip"),
        "log": ("rgba(0,212,255,.10)", "#00d4ff", "rgba(0,212,255,.25)", "Log Entry"),
        "patch": ("rgba(255,107,53,.10)", "#ff6b35", "rgba(255,107,53,.25)", "Patch Notes"),
    }
    bg, color, border, label = type_colors.get(POST_TYPE, type_colors["comic"])

    # Convert script to HTML paragraphs
    paragraphs = []
    for block in SCRIPT.split("| PANEL"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("PANEL"):
            block = block.replace("PANEL", "", 1).strip()
            if ":" in block:
                block = block.split(":", 1)[1].strip()
        paragraphs.append(block)

    if POST_TYPE in ("comic", "patch"):
        content_html = ""
        for i, p in enumerate(paragraphs, 1):
            if not p.strip():
                continue
            # Extract dialogue
            parts = p.split("Panel")
            content_html += f'      <div class="panel-box">\n'
            content_html += f'        <div class="panel-title">PANEL {i}</div>\n'
            content_html += f'        <p>{escape_html(p)}</p>\n'
            content_html += f'      </div>\n'
    else:
        content_html = ""
        for p in paragraphs:
            if not p.strip():
                continue
            # Check for quotes
            if '"' in p:
                content_html += f'      <blockquote>{escape_html(p)}</blockquote>\n'
            else:
                content_html += f'      <p>{escape_html(p)}</p>\n'

    # Build relative image path
    art_rel = ""
    if art_path:
        art_rel = f"rockinregi-images/{art_path.name}"

    html = f"""\u003c!doctype html\u003e
\u003chtml lang="en"\u003e
\u003chead\u003e
  \u003cmeta charset="utf-8"\u003e
  \u003cmeta name="viewport" content="width=device-width, initial-scale=1"\u003e
  \u003clink rel="icon" type="image/x-icon" href="../favicon.ico"\u003e
  \u003ctitle\u003e{escape_html(TITLE)} — Rockin Regi\u003c/title\u003e
  \u003cstyle\u003e
    :root {{
      --bg: #0a0c14; --panel: rgba(16,20,32,.92); --line: {border};
      --text: #e8ecf5; --muted: #8a96b0; --cyan: #00d4ff;
      --accent: {color};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg); min-height: 100vh;
    }}
    .wrap {{ max-width: 720px; margin: 0 auto; padding: 2rem 1.5rem; }}
    .nav-back {{ margin-bottom: 1.5rem; }}
    .nav-back a {{ color: var(--cyan); text-decoration: none; font-size: 0.9rem; }}
    .nav-back a:hover {{ text-decoration: underline; }}
    .post-type {{
      display: inline-block; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.06em; padding: 0.25rem 0.7rem; border-radius: 4px;
      background: {bg}; color: var(--accent); border: 1px solid {border};
      margin-bottom: 0.75rem;
    }}
    h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; line-height: 1.2; }}
    .date {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.5rem; }}
    .content {{ font-size: 1.05rem; line-height: 1.7; }}
    .content p {{ margin-bottom: 1.25rem; }}
    .panel-box {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
      padding: 1.25rem; margin: 1.5rem 0;
    }}
    .panel-title {{ color: var(--accent); font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.75rem; }}
    .content img {{ max-width: 100%; height: auto; border-radius: 8px; margin-top: 0.75rem; border: 1px solid var(--line); }}
    footer {{ margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--line); text-align: center; }}
    footer a {{ color: var(--cyan); text-decoration: none; }}
    @media (max-width: 640px) {{ .wrap {{ padding: 1.5rem 1rem; }} h1 {{ font-size: 1.5rem; }} }}
  \u003c/style\u003e
\u003c/head\u003e
\u003cbody\u003e
  \u003cdiv class="wrap"\u003e
    \u003cdiv class="nav-back"\u003e\u003ca href="./index.html"\u003e← Rockin Regi\u003c/a\u003e\u003c/div\u003e
    \u003cspan class="post-type"\u003e{label}\u003c/span\u003e
    \u003ch1\u003e{escape_html(TITLE)}\u003c/h1\u003e
    \u003cdiv class="date"\u003e{datetime.now().strftime("%B %d, %Y")} — Chaotic Sanctum\u003c/div\u003e

    \u003cdiv class="content"\u003e
{content_html}
    \u003c/div\u003e

    \u003cfooter\u003e
      \u003cp\u003e\u003ca href="./index.html"\u003e← Back to Rockin Regi\u003c/a\u003e\u003c/p\u003e
    \u003c/footer\u003e
  \u003c/div\u003e
\u003c/body\u003e
\u003c/html\u003e
"""

    post_file.write_text(html, encoding="utf-8")
    print(f"[POST] Created {post_file}")
    return post_file

# ── Step 3: Update Index ─────────────────────────────────────

def update_index(post_file):
    """Add new post to rockinregi/index.html."""
    index_html = BLOG_INDEX.read_text(encoding="utf-8")

    type_colors = {
        "comic": ("comic", "Comic Strip"),
        "log": ("log", "Log Entry"),
        "patch": ("patch", "Patch Notes"),
    }
    css_class, label = type_colors.get(POST_TYPE, ("comic", "Comic Strip"))

    # Generate excerpt
    excerpt = SCRIPT[:200].replace("|", " ") + ("..." if len(SCRIPT) > 200 else "")

    post_entry = f"""      \u003carticle class="post"\u003e
        \u003cdiv class="post-header"\u003e
          \u003cspan class="post-type {css_class}"\u003e{label}\u003c/span\u003e
          \u003cspan class="post-date"\u003e{datetime.now().strftime("%B %Y")}\u003c/span\u003e
        \u003c/div\u003e
        \u003ch2\u003e\u003ca href="./{post_file.name}"\u003e{TITLE}\u003c/a\u003e\u003c/h2\u003e
        \u003cp class="post-excerpt"\u003e{excerpt}\u003c/p\u003e
      \u003c/article\u003e

      \u003c!-- POSTS_START --\u003e"""

    new_index = index_html.replace("\u003c!-- POSTS_START --\u003e", post_entry)
    BLOG_INDEX.write_text(new_index, encoding="utf-8")
    print("[INDEX] Updated rockinregi/index.html")

# ── Step 4: Update RSS Feed ──────────────────────────────────

def update_feed(post_file):
    """Add new post to RSS feed."""
    feed = FEED_FILE.read_text(encoding="utf-8")

    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    excerpt = SCRIPT[:300].replace("|", " ") + ("..." if len(SCRIPT) > 300 else "")

    item = f"""    \u003citem\u003e
      \u003ctitle\u003e{escape_html(TITLE)}\u003c/title\u003e
      \u003clink\u003ehttps://patrickdanforth.com/rockinregi/{post_file.name}\u003c/link\u003e
      \u003cguid\u003ehttps://patrickdanforth.com/rockinregi/{post_file.name}\u003c/guid\u003e
      \u003cpubDate\u003e{pub_date}\u003c/pubDate\u003e
      \u003cdescription\u003e\u003c![CDATA[{escape_html(excerpt)}]]\u003e\u003c/description\u003e
    \u003c/item\u003e
    \u003citem\u003e"""

    new_feed = feed.replace("\u003citem\u003e", item, 1)
    # Update lastBuildDate
    new_build_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    new_feed = re.sub(
        r'\u003clastBuildDate\u003e[^\u003c]+\u003c/lastBuildDate\u003e',
        f'\u003clastBuildDate\u003e{new_build_date}\u003c/lastBuildDate\u003e',
        new_feed
    )
    FEED_FILE.write_text(new_feed, encoding="utf-8")
    print("[FEED] Updated rockinregi/feed.xml")

# ── Step 5: Git Commit + Push ────────────────────────────────

def git_deploy():
    """Commit and push changes to GitHub Pages."""
    os.chdir(SITE_ROOT)
    try:
        subprocess.run(["git", "add", "rockinregi/", "rockinregi-images/"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Rockin Regi: {TITLE} — {DATE_STR}"], check=False, capture_output=True)
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)
        print(f"[DEPLOY] Pushed to GitHub Pages")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[DEPLOY] Push may have failed: {e.stderr}")
        return False

# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print(f"🦞 Rockin Regi Pipeline")
    print(f"   Title: {TITLE}")
    print(f"   Type: {POST_TYPE}")
    print(f"   Date: {DATE_STR}")
    print("=" * 50)

    # Step 1: Art
    art_path = generate_art(TITLE, SCRIPT)
    if art_path:
        status["art_generated"] = True

    # Step 2: HTML Post
    post_file = generate_post_html()
    status["post_created"] = True

    # Step 3: Update Index
    update_index(post_file)

    # Step 4: Update Feed
    update_feed(post_file)

    # Step 5: Deploy
    status["deployed"] = git_deploy()

    print("\n" + "=" * 50)
    print("Status:")
    for k, v in status.items():
        icon = "✅" if v else "❌"
        print(f"  {icon} {k}: {v}")
    print(f"\n🌐 Live at: https://patrickdanforth.com/rockinregi/{post_file.name}")
    print("=" * 50)
