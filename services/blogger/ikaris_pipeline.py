#!/usr/bin/env python3
"""
Ikaris Daily Blog Pipeline — Self-Hosted
Usage: python3 ikaris_pipeline.py "<title>" "<story>" [tags...]

Workflow:
1. Generate AI art via OpenAI DALL-E
2. Save art to ikaris-images/ folder
3. Generate HTML post file in blog/ folder
4. Commit + push to GitHub (instant publish, no OAuth!)
5. Update blog/index.html with new post entry

No more Blogger OAuth headaches!
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

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
SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"
IMAGES_DIR = SITE_ROOT / "ikaris-images"
BLOG_INDEX = POSTS_DIR / "index.html"
FEED_FILE = POSTS_DIR / "feed.xml"

# ── Story Input ────────────────────────────────────────────────

if len(sys.argv) < 3:
    print("Usage: ikaris_pipeline.py '<title>' '<story>' [tags...]")
    sys.exit(1)

TITLE = sys.argv[1]
STORY = sys.argv[2]
TAGS = sys.argv[3:] if len(sys.argv) > 3 else ["fiction", "ai-generated"]

DATE_STR = datetime.now().strftime("%Y-%m-%d")
TIME_STR = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

art_path = None
status = {"art_generated": False, "post_created": False, "deployed": False}

# ── Step 1: Generate AI Art ────────────────────────────────────

def generate_art(title, story):
    """Generate art via OpenClaw image generation, return local file path."""
    prompt = (
        f"A striking digital illustration for a sci-fi short story titled '{title}'. "
        f"Scene inspired by: {story[:300]}. "
        f"Style: bold comic book / graphic novel art with rich colors, cinematic lighting, "
        f"and a slightly surreal atmosphere. The Chaotic Sanctum aesthetic — retro-futuristic, "
        f"warm and cool neon accents, detailed linework. No text, no captions, no lettering."
    )

    slug = "_".join(title.lower().split()[:4]).replace(",", "").replace(".", "")
    local_path = IMAGES_DIR / f"ikaris_{DATE_STR}_{slug}.png"

    cmd = [
        "openclaw", "infer", "image", "generate",
        "--prompt", prompt,
        "--size", "1024x1024",
        "--output", str(local_path),
        "--model", "openrouter/google/gemini-3.1-flash-image-preview",
        "--timeout-ms", "120000"
    ]

    try:
        print(f"[ART] Generating image via OpenClaw...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        if result.returncode == 0 and local_path.exists() and local_path.stat().st_size > 0:
            print(f"[ART] Saved to {local_path}")
            return str(local_path.name)
        print(f"[ART] openclaw infer failed: {result.stderr}")
    except Exception as e:
        print(f"[ART] Failed: {e}")

    # Fallback to cached image
    import glob, os
    cached = sorted(glob.glob(str(IMAGES_DIR / "ikaris_*.png")), key=lambda x: -os.path.getmtime(x))
    if cached:
        cached_name = os.path.basename(cached[0])
        print(f"[ART] Using cached image: {cached_name}")
        return cached_name

    # No cache available - create a minimal SVG fallback
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
  <rect width="1024" height="1024" fill="#0a0a1a"/>
  <text x="512" y="512" font-family="monospace" font-size="24" fill="#7ae7ff" text-anchor="middle" dominant-baseline="middle">Ikaris</text>
  <text x="512" y="540" font-family="monospace" font-size="14" fill="#9aa7c2" text-anchor="middle" dominant-baseline="middle">Chaotic Sanctum Dispatch</text>
</svg>'''
    svg_path = IMAGES_DIR / f"ikaris_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fallback.svg"
    svg_path.write_text(svg_content)
    print(f"[ART] SVG fallback saved to {svg_path}")
    return str(svg_path.name)

# ── Step 2: Generate HTML Post ────────────────────────────────────

def create_post_html(title, story, art_filename=None, tags=None):
    """Create individual post HTML file."""
    slug = f"{DATE_STR}-" + "-".join(title.lower().split()[:4]).replace(",", "").replace(".", "")
    post_file = POSTS_DIR / f"{slug}.html"

    tags_html = "".join([f'<span class="tag pink">{t.title()}</span>' for t in tags[:2]])

    art_section = ""
    if art_filename:
        art_section = f'<img src="../ikaris-images/{art_filename}" alt="{title}" style="width:100%;">'

    prev_link = ""
    next_link = ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/x-icon" href="../favicon.ico">
<title>{title} — Letters From Ikaris</title>
<meta name="description" content="{story[:150]}">
<style>
:root {{ --bg:#06070b; --panel:rgba(15,18,27,.88); --line:rgba(130,177,255,.16); --text:#edf3ff; --muted:#9aa7c2; --cyan:#7ae7ff; --gold:#d7aa61; --pink:#f0a0c0; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ color:var(--text); font-family:Georgia,serif; background:radial-gradient(circle at 20% 10%, rgba(122,231,255,.12), transparent 24%), radial-gradient(circle at 80% 12%, rgba(215,170,97,.10), transparent 24%), radial-gradient(circle at 50% 90%, rgba(255,122,77,.08), transparent 20%), linear-gradient(180deg,#04050a 0%,#0b1020 55%,#090b12 100%); min-height:100vh; }}
.wrap {{ width:min(680px,calc(100% - 32px)); margin:0 auto; padding:40px 0 60px; position:relative; z-index:1; }}
.back-link {{ font-family:Inter,sans-serif; display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border:1px solid var(--line); border-radius:8px; color:var(--cyan); text-decoration:none; font-size:.82rem; margin-bottom:24px; background:rgba(255,255,255,.03); }}
.post-meta {{ font-family:Inter,sans-serif; font-size:.8rem; color:var(--muted); margin-bottom:24px; padding-bottom:16px; border-bottom:1px solid var(--line); }}
.post-body {{ font-size:1.08rem; line-height:1.85; color:var(--text); }}
.post-body p {{ margin-bottom:1.2em; }}
.post-body img {{ max-width:100%; border-radius:8px; margin:24px auto; display:block; }}
.footer {{ text-align:center; padding:32px 0 0; border-top:1px solid var(--line); color:var(--muted); font-size:.78rem; margin-top:40px; font-family:Inter,sans-serif; }}
.footer a {{ color:var(--cyan); text-decoration:none; }}
.tags {{ display:flex; flex-wrap:wrap; gap:6px; margin:16px 0; }}
.tag {{ display:inline-block; padding:3px 10px; border-radius:6px; font-family:Inter,sans-serif; font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; border:1px solid rgba(255,255,255,.08); background:rgba(255,255,255,.04); color:var(--muted); }}
.tag.pink {{ border-color:rgba(240,160,192,.2); color:var(--pink); }}
.tag.cyan {{ border-color:rgba(122,231,255,.2); color:var(--cyan); }}
h1 {{ font-family:Inter,sans-serif; font-size:2rem; font-weight:600; margin-bottom:12px; color:var(--cyan); }}
.post-nav {{ display:flex; justify-content:space-between; gap:12px; margin:32px 0; padding:20px 0; border-top:1px solid var(--line); border-bottom:1px solid var(--line); font-family:Inter,sans-serif; font-size:.85rem; flex-wrap:wrap; }}
.nav-next, .nav-prev {{ color:var(--cyan); text-decoration:none; padding:8px 14px; border:1px solid var(--line); border-radius:8px; background:rgba(255,255,255,.03); transition:all .22s ease; white-space:nowrap; }}
.nav-next:hover, .nav-prev:hover {{ border-color:var(--cyan); background:rgba(122,231,255,.08); }}
.nav-next:only-child {{ margin-left:auto; }}
.nav-prev:only-child {{ margin-right:auto; }}
@media(max-width:700px){{ h1{{font-size:1.5rem;}} .post-nav {{ flex-direction:column; gap:8px; }} .nav-next, .nav-prev {{ text-align:center; }} }}
</style>
</head>
<body>
<div class="wrap">
<a class="back-link" href="./index.html">← All Letters</a>
<h1>{title}</h1>
<div class="post-meta">{DATE_STR} · Letters From Ikaris</div>
<div class="tags">{tags_html}</div>
{art_section}
<div class="post-body">
<p>{story}</p>
</div>
<div class="post-nav">
  {prev_link}
  {next_link}
</div>
<div class="footer">
<p>Patrick Danforth · <a href="mailto:patticus@proton.me">patticus@proton.me</a></p>
<p style="margin-top:6px;opacity:.6;">Written by Talos ⬡ — Disciples of Controlled Chaos</p>
</div>
</div>
</body>
</html>
"""

    post_file.write_text(html)
    print(f"[POST] Created {post_file}")
    return post_file.name

# ── Step 3: Update Blog Index ───────────────────────────────────

def update_blog_index(title, story, filename, tags=None):
    """Add new post to blog/index.html."""
    index_content = BLOG_INDEX.read_text()

    # Insert new post card after the opening posts-list div
    excerpt = story[:120] + "..." if len(story) > 120 else story

    new_card = f"""
      <a class="post-card" href="./{filename}">
        <div class="post-date">{DATE_STR}</div>
        <div class="post-title">{title}</div>
        <div class="post-excerpt">{excerpt}</div>
        <div class="post-tags">
          <span class="tag pink">{tags[0].title() if tags else 'Fiction'}</span>
          <span class="tag cyan">AI-Generated</span>
        </div>
      </a>
"""

    # Insert after the first posts-list div
    marker = '<div class="posts-list">'
    pos = index_content.find(marker)
    if pos != -1:
        insert_pos = pos + len(marker)
        updated = index_content[:insert_pos] + "\n" + new_card + index_content[insert_pos:]
        BLOG_INDEX.write_text(updated)
        print(f"[INDEX] Added {title} to blog index")

# ── Step 4: Update RSS Feed ────────────────────────────────────

def update_rss_feed(title, story, filename, tags=None):
    """Full rewrite of blog/feed.xml as valid RSS 2.0."""
    pub_date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    # Only process files matching post pattern: YYYY-MM-DD-*.html
    post_files = [p for p in POSTS_DIR.glob("????-??-??-*.html")]
    post_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    items_xml = ""
    for p in post_files[:10]:
        name = p.stem
        date_part = name[:10]
        title_part = " ".join(name[11:].split("-")).title()
        with open(p, 'r') as f:
            content = f.read()
        items_xml += f"""    <item>
      <title>{title_part}</title>
      <link>https://patrickdanforth.com/blog/{p.name}</link>
      <guid>https://patrickdanforth.com/blog/{p.name}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{title_part}</description>
    </item>
"""
    
    rss_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Ikaris Daily — 2026</title>
    <link>https://patrickdanforth.com/blog/</link>
    <description>Ikaris Daily — Letters from the Chaotic Sanctum</description>
    <language>en</language>
    <lastBuildDate>{pub_date}</lastBuildDate>
    <ttl>60</ttl>
{items_xml}  </channel>
</rss>
"""
    FEED_FILE.write_text(rss_template)

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
            ["git", "commit", "-m", f"Ikaris Daily: {TITLE}"],
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

if __name__ == "__main__":
    print("=" * 50)
    print(f"✉️  Ikaris Daily Pipeline")
    print(f"   Title: {TITLE}")
    print(f"   Date: {DATE_STR}")
    print("=" * 50)

    # Step 1: Art
    art_filename = generate_art(TITLE, STORY)
    if art_filename:
        status["art_generated"] = True

    # Step 2: HTML Post
    post_filename = create_post_html(TITLE, STORY, art_filename, TAGS)
    status["post_created"] = True

    # Step 3: Update Blog Index
    update_blog_index(TITLE, STORY, post_filename, TAGS)

    # Step 4: Update RSS Feed
    update_rss_feed(TITLE, STORY, post_filename, TAGS)

    # Step 5: Deploy
    status["deployed"] = git_deploy()

    print("\n" + "=" * 50)
    print("Status:")
    for k, v in status.items():
        icon = "✅" if v else "❌"
        print(f"  {icon} {k}: {v}")
    print(f"\n🌐 Live at: https://patrickdanforth.com/blog/{post_filename}")
    print("=" * 50)