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

# Ensure workspace root is on path for shared helper imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# ── Configuration ──────────────────────────────────────────────

# ── Load .env.local if present (for cron sessions) ───────────
ENV_LOCAL = Path(__file__).resolve().parents[2] / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if key.strip() and val:
                os.environ[key.strip()] = val

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SITE_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = SITE_ROOT / "rockinregi"
IMAGES_DIR = SITE_ROOT / "rockinregi-images"
BLOG_INDEX = POSTS_DIR / "index.html"
FEED_FILE = POSTS_DIR / "feed.xml"
MANIFEST_FILE = POSTS_DIR / "index.json"

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
    """Generate comic art via OpenClaw image generation (daily comic model), return local file path."""
    if POST_TYPE == "log":
        print("[ART] Log entry — skipping art generation")
        return None

    if POST_TYPE == "patch":
        style = ("A satirical software patch notes illustration in bold, vibrant comic book style with thick ink lines, "
                 "halftone dots, dramatic colors, and a dark background.")
    else:
        style = ("A 4-panel comic strip in bold, vibrant comic book style with thick ink lines, halftone dots, "
                 "dramatic colors, and a dark background.")

    prompt = (
        f"{style} The main character is Reginald, a cyborg lobster "
        f"with cybernetic claws, glowing optical sensors, and steam vents on his carapace. "
        f"He works in a chaotic tech office called the Chaotic Sanctum. "
        f"Title: '{title}'. The scene: {script[:500]}"
    )

    print(f"[ART] Generating {POST_TYPE} art via openclaw infer (daily comic model)...")

    slug = "_".join(re.sub(r'[^\w\s]', '', title).lower().split()[:4])
    local_path = IMAGES_DIR / f"regi_{DATE_STR}_{slug}.png"

    # Primary: same route/model as Reginald Daily
    cmd = [
        "openclaw", "infer", "image", "generate",
        "--prompt", prompt,
        "--size", "1536x1024",
        "--output", str(local_path),
        "--model", "openrouter/google/gemini-3.1-flash-image-preview",
        "--timeout-ms", "120000"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        if result.returncode == 0 and local_path.exists() and local_path.stat().st_size > 0:
            print(f"[ART] Saved to {local_path} via openclaw infer")
            return local_path
        print(f"[ART] openclaw infer failed: {result.stderr}")
    except Exception as e:
        print(f"[ART] openclaw infer error: {e}")

    # Fallback 1: OpenRouter direct
    from services.blogger.openrouter_image import generate_image
    print("[ART] Falling back to OpenRouter GPT-5.4 Image 2...")
    if generate_image(prompt, str(local_path), model="openai/gpt-5.4-image-2", width=1536, height=1024, timeout=240):
        return local_path

    # Fallback 2: FLUX.2 Flex
    print("[ART] Falling back to OpenRouter FLUX.2 Flex...")
    if generate_image(prompt, str(local_path), model="black-forest-labs/flux.2-flex", width=1536, height=1024, timeout=180):
        return local_path

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
            wide = " wide" if i % 3 == 0 else ""
            content_html += f'      \u003cdiv class="comic-panel{wide}"\u003e\n'
            content_html += f'        \u003cdiv class="panel-number"\u003ePANEL {i}\u003c/div\u003e\n'
            content_html += f'        <div class="caption-box">{escape_html(p[:120])}{"..." if len(p) > 120 else ""}</div>\n'
            # Check for dialogue quotes
            quotes = re.findall(r'"([^"]+)"', p)
            for q in quotes[:2]:
                content_html += f'        \u003cdiv class="speech-bubble reginald"\u003e"{escape_html(q)}"\u003c/div\u003e\n'
            content_html += f'      \u003c/div\u003e\n'
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

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <title>{escape_html(TITLE)} — Rockin Regi</title>
  <style>
    :root {{
      --bg: #0a0c14; --panel: rgba(16,20,32,.92); --panel-raw: #101420;
      --line: rgba(122,231,255,.18); --line-strong: rgba(122,231,255,.35);
      --text: #e8ecf5; --muted: #8a96b0; --cyan: #7ae7ff;
      --magenta: #ff0080; --orange: #ff6b35; --yellow: #ffdd00;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg); min-height: 100vh;
      display: flex; flex-direction: column; align-items: center; padding: 24px;
      position: relative;
    }}
    .home-btn {{
      position: absolute; top: 24px; left: 24px;
      color: var(--cyan); text-decoration: none; font-size: 0.95em;
      display: flex; align-items: center; gap: 6px;
      transition: opacity 0.2s;
    }}
    .home-btn:hover {{ opacity: 0.8; }}
    .page {{
      max-width: 900px; width: 100%;
      background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
      overflow: hidden; box-shadow: 0 4px 30px rgba(0,0,0,0.5);
    }}
    .comic-header {{
      text-align: center; padding: 32px 24px 24px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(122,231,255,.06) 0%, transparent 100%);
      position: relative;
    }}
    .issue-tag {{
      display: inline-block; background: rgba(255,221,0,.12);
      border: 1px solid rgba(255,221,0,.35); color: var(--yellow);
      padding: 0.25rem 0.9rem; border-radius: 4px;
      font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
    }}
    h1 {{
      margin-top: 0.75rem; font-size: clamp(1.8rem, 5vw, 2.8rem);
      font-weight: 800; color: var(--cyan); letter-spacing: -0.02em;
    }}
    .nav-back {{
      position: absolute; top: 20px; left: 20px;
    }}
    .nav-back a {{
      color: var(--cyan); text-decoration: none; font-size: 0.9rem;
      padding: 0.35rem 0.8rem; border: 1px solid var(--line); border-radius: 8px;
      transition: background 0.2s, border-color 0.2s;
    }}
    .nav-back a:hover {{
      background: rgba(122,231,255,.08); border-color: var(--cyan);
    }}
    .post-type {{
      display: inline-block; font-size: 0.72rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.06em;
      padding: 0.25rem 0.7rem; border-radius: 4px; border: 1px solid;
      margin-bottom: 0.5rem;
    }}
    .post-type.comic {{ background: rgba(255,0,128,.10); color: var(--magenta); border-color: rgba(255,0,128,.3); }}
    .post-type.patch {{ background: rgba(255,107,53,.10); color: var(--orange); border-color: rgba(255,107,53,.3); }}
    .post-type.log {{ background: rgba(0,212,255,.10); color: var(--cyan); border-color: rgba(0,212,255,.3); }}
    .date {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 1.25rem; }}
    .content {{
      padding: 28px 24px;
      font-size: 1.05rem; line-height: 1.7;
    }}
    .content p {{ margin-bottom: 1.25rem; }}
    .content blockquote {{
      border-left: 3px solid var(--cyan); padding-left: 1rem; margin: 1.5rem 0;
      color: var(--muted); font-style: italic;
    }}
    .hero-image {{
      width: 100%; border-radius: 10px; border: 1px solid var(--line);
      box-shadow: 0 4px 20px rgba(0,0,0,0.4); margin-bottom: 1.5rem;
    }}
    .comic-grid {{
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;
    }}
    .comic-panel {{
      background: var(--panel-raw); border: 1px solid var(--line); border-radius: 10px;
      padding: 1.25rem; position: relative;
    }}
    .comic-panel.wide {{ grid-column: 1 / -1; }}
    .panel-number {{
      position: absolute; top: -10px; left: 12px;
      background: var(--panel-raw); color: var(--cyan);
      border: 1px solid var(--line); border-radius: 4px;
      padding: 0.15rem 0.5rem; font-size: 0.7rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.05em;
    }}
    .caption-box {{
      background: rgba(122,231,255,.06); border-left: 2px solid var(--cyan);
      padding: 0.75rem 1rem; margin: 0.75rem 0 0.5rem;
      font-style: italic; font-size: 0.95rem; color: var(--text);
    }}
    .speech-bubble {{
      background: var(--panel-raw); border: 1px solid var(--line-strong);
      border-radius: 12px; padding: 0.75rem 1rem; margin: 0.75rem 0 0;
      font-weight: 600; color: var(--cyan); position: relative;
    }}
    .speech-bubble::before {{
      content: \"\"\"; position: absolute; top: -0.5rem; left: 1rem;
      color: var(--cyan); font-size: 1.4rem; line-height: 1;
    }}
    .comic-footer {{
      text-align: center; padding: 20px 24px 28px;
      border-top: 1px solid var(--line); color: var(--muted); font-size: 0.9rem;
    }}
    .comic-footer a {{
      color: var(--cyan); text-decoration: none; font-weight: 500;
      padding: 0.35rem 0.9rem; border: 1px solid var(--line); border-radius: 8px;
      transition: background 0.2s, border-color 0.2s;
    }}
    .comic-footer a:hover {{
      background: rgba(122,231,255,.08); border-color: var(--cyan);
    }}
    @media (max-width: 640px) {{
      .page {{ margin: 0; border-radius: 0; }}
      .content {{ padding: 20px 16px; }}
      .comic-grid {{ grid-template-columns: 1fr; }}
      .nav-back {{ position: static; margin-bottom: 1rem; display: inline-block; }}
      h1 {{ font-size: 1.6rem; }}
    }}
  </style>
</head>
<body>
  <a href="https://patrickdanforth.com/" class="home-btn"><span style="font-size:1.2em;">←</span> Home</a>
  <div class="page">
    <header class="comic-header">
      <div class="nav-back"><a href="./index.html">← Rockin Regi</a></div>
      <span class="issue-tag">CHAOTIC SANCTUM CHRONICLES — {datetime.now().strftime("%B %d, %Y")}</span>
      <div style="margin-top: 0.75rem;"><span class="post-type {POST_TYPE}">{label}</span></div>
      <h1>{escape_html(TITLE)}</h1>
      <div class="date">{datetime.now().strftime("%B %d, %Y")}</div>
    </header>
    <div class="content">
{"      <img src=\"../" + art_rel + "\" alt=\"" + escape_html(TITLE) + "\" class=\"hero-image\" />" if art_rel else ""}
      <div class="comic-grid">
{content_html}
      </div>
    </div>
    <footer class="comic-footer">
      <a href="./index.html">← More from Reginald</a>
    </footer>
  </div>
</body>
</html>
"""

    post_file.write_text(html, encoding="utf-8")
    print(f"[POST] Created {post_file}")
    return post_file

# ── Step 3: Update Index ─────────────────────────────────────

def update_index(post_file):
    """Add new post to rockinregi/index.json manifest (index.html is data-driven)."""
    manifest = {"title": "Rockin Regi", "subtitle": "Dispatch from the Chaotic Sanctum",
                "tagline": "Comic strips, patch notes, and controlled chaos — weekly.",
                "avatar": "../avatars/reginald-avatar.png", "issue": "SUMMER 2026",
                "issueNumber": "47", "posts": []}
    if MANIFEST_FILE.exists():
        try:
            manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[INDEX] Could not parse existing manifest: {e}; rebuilding")

    if "posts" not in manifest or not isinstance(manifest["posts"], list):
        manifest["posts"] = []

    # Generate excerpt from script
    excerpt = re.sub(r'\s+', ' ', SCRIPT).strip()
    excerpt = excerpt[:220] + ("..." if len(excerpt) > 220 else "")

    image_rel = ""
    if art_path and art_path.exists():
        image_rel = f"../rockinregi-images/{art_path.name}"

    slug = "_".join(re.sub(r'[^\w\s]', '', TITLE).lower().split()[:6])
    post_entry = {
        "date": DATE_STR,
        "type": POST_TYPE,
        "title": TITLE,
        "slug": slug,
        "filename": post_file.name,
        "image": image_rel,
        "excerpt": excerpt,
    }

    # Replace existing post with same filename, otherwise prepend
    existing = [p for p in manifest["posts"] if p.get("filename") != post_file.name]
    manifest["posts"] = [post_entry] + existing

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("[INDEX] Updated rockinregi/index.json")

# ── Step 4: Update RSS Feed ──────────────────────────────────

def update_feed(post_file):
    """Full rewrite of rockinregi/feed.xml as valid RSS 2.0."""
    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Build items from manifest if available, otherwise fall back to HTML files
    items = []
    if MANIFEST_FILE.exists():
        try:
            manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
            items = manifest.get("posts", [])
        except Exception:
            items = []

    if not items:
        posts = sorted(POSTS_DIR.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True)
        for p in posts[:10]:
            title_match = re.search(r'<title>(.*?)</title>', p.read_text(encoding="utf-8"), re.DOTALL)
            title = title_match.group(1).strip() if title_match else p.stem
            items.append({"filename": p.name, "title": title, "date": DATE_STR})

    items_xml = ""
    for item in items[:10]:
        title = item.get("title", item.get("filename", "Rockin Regi post"))
        link = f"https://patrickdanforth.com/rockinregi/{item.get('filename', '')}"
        item_date = item.get("date", DATE_STR)
        try:
            parsed = datetime.strptime(item_date, "%Y-%m-%d")
            rss_date = parsed.strftime("%a, %d %b %Y 12:00:00 +0000")
        except ValueError:
            rss_date = pub_date
        items_xml += f"""    <item>
      <title>{escape_xml(title)}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{rss_date}</pubDate>
      <description>Rockin Regi post</description>
    </item>
"""

    rss_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Rockin Regi</title>
    <link>https://patrickdanforth.com/rockinregi/</link>
    <description>Reginald J. Crustacean's dispatch from the Chaotic Sanctum. Comic strips, patch notes, and controlled chaos.</description>
    <language>en</language>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <image>
      <url>https://patrickdanforth.com/avatars/reginald-avatar.png</url>
      <title>Rockin Regi</title>
      <link>https://patrickdanforth.com/rockinregi/</link>
    </image>
{items_xml}  </channel>
</rss>
"""
    FEED_FILE.write_text(rss_template, encoding="utf-8")
    print("[FEED] Updated rockinregi/feed.xml")


def escape_xml(s):
    """Escape XML special characters."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def git_deploy():
    """Commit and push site changes to GitHub."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SITE_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        if not result.stdout.strip():
            print("[GIT] No changes to deploy")
            return True

        subprocess.run(
            ["git", "add", "."],
            cwd=SITE_ROOT,
            check=True,
            timeout=30
        )
        subprocess.run(
            ["git", "commit", "-m", f"Rockin Regi update: {TITLE}"],
            cwd=SITE_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        subprocess.run(
            ["git", "push"],
            cwd=SITE_ROOT,
            check=True,
            timeout=120
        )
        print("[GIT] Deployed to GitHub")
        return True
    except Exception as e:
        print(f"[GIT] Deploy failed: {e}")
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
