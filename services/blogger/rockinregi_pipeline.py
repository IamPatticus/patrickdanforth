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
SITE_ROOT = Path(__file__).resolve().parents[3]
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
    """Generate comic art via OpenClaw image generation, return local file path."""
    if POST_TYPE == "log":
        print("[ART] Log entry — skipping art generation")
        return None

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

    print(f"[ART] Generating {POST_TYPE} art via OpenRouter FLUX...")

    slug = "_".join(re.sub(r'[^\w\s]', '', title).lower().split()[:4])
    local_path = IMAGES_DIR / f"regi_{DATE_STR}_{slug}.png"

    from services.blogger.openrouter_image import generate_image
    if generate_image(prompt, str(local_path), model="openai/gpt-5.4-image-2", width=1024, height=1024, timeout=240):
        return local_path

    # Fallback to FLUX.2 Flex
    print("[ART] Falling back to OpenRouter FLUX.2 Flex...")
    if generate_image(prompt, str(local_path), model="black-forest-labs/flux.2-flex", width=1024, height=1024, timeout=180):
        return local_path

    # Final fallback to openclaw route
    print("[ART] Falling back to openclaw infer...")
    cmd = [
        "openclaw", "infer", "image", "generate",
        "--prompt", prompt,
        "--size", "1024x1024",
        "--output", str(local_path),
        "--model", "openrouter/google/gemini-3.1-flash-image-preview",
        "--timeout-ms", "120000"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        if result.returncode == 0 and local_path.exists() and local_path.stat().st_size > 0:
            print(f"[ART] Saved to {local_path} via fallback")
            return local_path
        print(f"[ART] openclaw infer fallback failed: {result.stderr}")
    except Exception as e:
        print(f"[ART] Fallback failed: {e}")
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

    html = f"""\u003c!doctype html\u003e
\u003chtml lang="en"\u003e
\u003chead\u003e
  \u003cmeta charset="utf-8"\u003e
  \u003cmeta name="viewport" content="width=device-width, initial-scale=1"\u003e
  \u003clink rel="icon" type="image/x-icon" href="../favicon.ico"\u003e
  \u003ctitle\u003e{escape_html(TITLE)} — Rockin Regi\u003c/title\u003e
  \u003clink href="https://fonts.googleapis.com/css2?family=Bangers\u0026family=Comic+Neue:wght@400;700\u0026display=swap" rel="stylesheet"\u003e
  \u003cstyle\u003e
    :root {{
      --paper: #f5f0e6; --paper-dark: #e8e0d0; --ink: #1a1a2e;
      --accent: #ff0080; --cyan: #00d4ff; --burst-yellow: #ffdd00;
      --burst-red: #ff3333; --panel-border: #1a1a2e;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      color: var(--ink); font-family: 'Comic Neue', cursive;
      background: #2a2a3e; min-height: 100vh; padding: 1rem;
    }}
    .comic-page {{
      max-width: 900px; margin: 0 auto; background: var(--paper);
      border: 4px solid var(--ink);
      box-shadow: 0 0 0 2px var(--paper-dark), 0 10px 40px rgba(0,0,0,0.4), inset 0 0 100px rgba(0,0,0,0.05);
      padding: 1.5rem; position: relative;
    }}
    .comic-page::before {{
      content: ""; position: absolute; inset: 8px; border: 2px solid var(--ink);
      pointer-events: none; opacity: 0.3;
    }}
    .comic-page::after {{
      content: ""; position: absolute; inset: 0;
      background-image: radial-gradient(circle, rgba(0,0,0,0.03) 1px, transparent 1px);
      background-size: 4px 4px; pointer-events: none;
    }}
    .comic-header {{
      text-align: center; margin-bottom: 1.5rem; padding-bottom: 1rem;
      border-bottom: 3px solid var(--ink); position: relative; z-index: 1;
    }}
    .issue-tag {{
      display: inline-block; background: var(--burst-yellow); border: 2px solid var(--ink);
      padding: 0.3rem 1rem; font-family: 'Bangers', cursive; font-size: 0.9rem;
      letter-spacing: 1px; transform: rotate(-2deg); box-shadow: 3px 3px 0 var(--ink);
    }}
    .comic-header h1 {{
      font-family: 'Bangers', cursive; font-size: clamp(2rem, 5vw, 3.5rem);
      letter-spacing: 2px; text-transform: uppercase; color: var(--ink);
      text-shadow: 3px 3px 0 rgba(255,0,128,0.3); margin: 0.75rem 0 0.5rem;
    }}
    .nav-back {{
      position: absolute; top: 1rem; left: 1rem; font-family: 'Bangers', cursive;
      font-size: 0.85rem; z-index: 10;
    }}
    .nav-back a {{
      color: var(--ink); text-decoration: none; background: var(--burst-yellow);
      border: 2px solid var(--ink); padding: 0.3rem 0.8rem; display: inline-block;
      transform: rotate(-3deg); box-shadow: 2px 2px 0 var(--ink); transition: transform 0.2s;
    }}
    .nav-back a:hover {{ transform: rotate(0deg) scale(1.05); }}
    .hero-image {{
      width: 100%; border: 3px solid var(--ink); margin-bottom: 1.5rem;
      display: block; box-shadow: 4px 4px 0 rgba(0,0,0,0.2); position: relative; z-index: 1;
    }}
    .comic-grid {{
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;
      margin-bottom: 1.5rem; position: relative; z-index: 1;
    }}
    .comic-panel {{
      background: #fff; border: 3px solid var(--panel-border); padding: 1rem;
      position: relative; box-shadow: 3px 3px 0 rgba(0,0,0,0.15);
    }}
    .comic-panel.wide {{ grid-column: 1 / -1; }}
    .comic-panel.full {{ grid-column: 1 / -1; }}
    .panel-number {{
      position: absolute; top: -12px; left: 10px; background: var(--burst-yellow);
      border: 2px solid var(--ink); padding: 0.15rem 0.6rem;
      font-family: 'Bangers', cursive; font-size: 0.8rem; letter-spacing: 1px;
      box-shadow: 2px 2px 0 var(--ink); z-index: 2;
    }}
    .speech-bubble {{
      background: #fff; border: 2px solid var(--ink); border-radius: 50%;
      padding: 1rem 1.5rem; margin: 0.75rem 0; position: relative;
      font-family: 'Comic Neue', cursive; font-weight: 700; font-size: 1rem;
      line-height: 1.4; text-align: center;
    }}
    .speech-bubble::after {{
      content: ""; position: absolute; bottom: -15px; left: 30%;
      width: 0; height: 0; border-left: 15px solid transparent;
      border-right: 15px solid transparent; border-top: 20px solid var(--ink);
    }}
    .speech-bubble::before {{
      content: ""; position: absolute; bottom: -11px; left: calc(30% + 2px);
      width: 0; height: 0; border-left: 13px solid transparent;
      border-right: 13px solid transparent; border-top: 17px solid #fff; z-index: 1;
    }}
    .speech-bubble.reginald {{ background: #e6f7ff; border-color: var(--cyan); }}
    .speech-bubble.reginald::after {{ border-top-color: var(--cyan); }}
    .speech-bubble.reginald::before {{ border-top-color: #e6f7ff; }}
    .caption-box {{
      background: var(--paper-dark); border: 2px solid var(--ink);
      padding: 0.75rem 1rem; margin: 0.75rem 0;
      font-family: 'Comic Neue', cursive; font-style: italic; font-size: 0.95rem;
    }}
    .caption-box::before {{ content: "📍 "; }}
    .burst {{
      display: inline-block; background: var(--burst-yellow); border: 3px solid var(--ink);
      padding: 0.5rem 1rem; font-family: 'Bangers', cursive; font-size: 1.3rem;
      letter-spacing: 2px; text-transform: uppercase; transform: rotate(-5deg);
      box-shadow: 3px 3px 0 var(--ink); margin: 0.5rem 0;
    }}
    .burst.red {{ background: var(--burst-red); color: #fff; }}
    .comic-footer {{
      text-align: center; margin-top: 2rem; padding-top: 1rem;
      border-top: 3px solid var(--ink); font-family: 'Bangers', cursive;
      font-size: 0.9rem; letter-spacing: 1px; position: relative; z-index: 1;
    }}
    .comic-footer a {{
      color: var(--ink); text-decoration: none; background: var(--burst-yellow);
      border: 2px solid var(--ink); padding: 0.3rem 1rem; display: inline-block;
      box-shadow: 2px 2px 0 var(--ink);
    }}
    @media (max-width: 640px) {{
      .comic-grid {{ grid-template-columns: 1fr; }}
      .comic-page {{ padding: 1rem; margin: 0.5rem; }}
      .comic-header h1 {{ font-size: 1.8rem; }}
      .nav-back {{ position: static; margin-bottom: 1rem; text-align: center; }}
    }}
  \u003c/style\u003e
\u003c/head\u003e
\u003cbody\u003e
  \u003cdiv class="comic-page"\u003e
    \u003cdiv class="nav-back"\u003e\u003ca href="./index.html"\u003e← BACK TO ROCKIN REGI\u003c/a\u003e\u003c/div\u003e
    \u003cdiv class="comic-header"\u003e
      \u003cdiv class="issue-tag"\u003eCHAOTIC SANCTUM CHRONICLES — {datetime.now().strftime("%B %d, %Y")}\u003c/div\u003e
      \u003ch1\u003e{escape_html(TITLE)}\u003c/h1\u003e
    \u003c/div\u003e
{"    \u003cimg src=\"../" + art_rel + "\" alt=\"" + escape_html(TITLE) + "\" class=\"hero-image\" /\u003e" if art_rel else ""}
    \u003cdiv class="comic-grid"\u003e
{content_html}
    \u003c/div\u003e
    \u003cdiv class="comic-footer"\u003e
      \u003ca href="./index.html"\u003e← MORE FROM REGINALD\u003c/a\u003e
    \u003c/div\u003e
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
        "comic": ("comic", "COMIC STRIP"),
        "log": ("log", "LOG ENTRY"),
        "patch": ("patch", "PATCH NOTES"),
    }
    css_class, label = type_colors.get(POST_TYPE, ("comic", "COMIC STRIP"))

    # Generate excerpt
    excerpt = SCRIPT[:200].replace("|", " ") + ("..." if len(SCRIPT) > 200 else "")

    # Build thumbnail if art exists
    thumb_html = ""
    if art_path:
        thumb_name = art_path.name
        thumb_html = f'    \u003cimg class="post-thumbnail" src="../rockinregi-images/{thumb_name}" alt="{TITLE}"\u003e\n    '

    post_entry = f"""      \u003carticle class="post-card"\u003e
{thumb_html}\u003cdiv class="post-header"\u003e
          \u003cspan class="post-type {css_class}"\u003e{label}\u003c/span\u003e
          \u003cdiv class="post-date"\u003e{datetime.now().strftime("%B %d, %Y")}\u003c/div\u003e
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
    """Full rewrite of rockinregi/feed.xml as valid RSS 2.0."""
    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    # Read existing posts directory to get all entries
    posts = []
    for p in POSTS_DIR.glob("*.html"):
        posts.append(p)
    
    # Sort by date (most recent first)
    posts.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    items_xml = ""
    for p in posts[:10]:  # Last 10 posts
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
        title_match = re.search(r'<h1.*?>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else p.stem
        items_xml += f"""    <item>
      <title>{re.escape(title)}</title>
      <link>https://patrickdanforth.com/rockinregi/{p.name}</link>
      <guid>https://patrickdanforth.com/rockinregi/{p.name}</guid>
      <pubDate>{pub_date}</pubDate>
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
    FEED_FILE.write_text(rss_template, encoding='utf-8')

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
