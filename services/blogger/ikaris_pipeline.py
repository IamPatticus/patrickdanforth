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
ENV_LOCAL = Path(__file__).parent.parent / ".env.local"
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
    """Generate art via OpenAI DALL-E, return local file path."""
    if not OPENAI_API_KEY:
        print("[ART] No OPENAI_API_KEY — skipping art generation")
        return None

    import urllib.request
    import base64

    prompt = (
        "A 4-panel comic strip: Reginald the cyborg lobster in the Chaotic Sanctum office."
    )

    print(f"[ART] Generating image...")

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
            print(f"[ART] Unknown response format")
            return None

        print(f"[ART] Generated. Image size: {len(img_data)} bytes")

        slug = "_".join(title.lower().split()[:4]).replace(",", "").replace(".", "")
        local_path = IMAGES_DIR / f"ikaris_{DATE_STR}_{slug}.png"
        local_path.write_bytes(img_data)
        print(f"[ART] Saved to {local_path}")
        return str(local_path.name)

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
  <text x="512" y="512" font-family="monospace" font-size="24" fill="#7ae7ff" text-anchor="middle" dominant-baseline="middle">Reginald the Lobster</text>
  <text x="512" y="540" font-family="monospace" font-size="14" fill="#9aa7c2" text-anchor="middle" dominant-baseline="middle">4-panel comic — Chaotic Sanctum</text>
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
    """Add new post to feed.xml."""
    feed_content = FEED_FILE.read_text()

    new_item = f"""    <item>
      <title>{title}</title>
      <link>https://patrickdanforth.com/blog/{filename}</link>
      <guid>https://patrickdanforth.com/blog/{filename}</guid>
      <pubDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
      <description>{story[:300]}</description>
      <category>Fiction</category>
      <category>AI-Generated</category>
    </item>
"""

    marker = "</channel>"
    pos = feed_content.find(marker)
    if pos != -1:
        updated = feed_content[:pos] + "\n" + new_item + "\n  " + feed_content[pos:]
        FEED_FILE.write_text(updated)
        print(f"[RSS] Added {title} to RSS feed")

# ── Step 5: Git Commit + Push ───────────────────────────────────

def deploy_site():
    """Commit and push to GitHub."""
    print("[DEPLOY] Committing and pushing...")

    os.chdir(SITE_ROOT)

    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"New post: {TITLE}"],
            check=False,
            capture_output=True
        )
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"[DEPLOY] ✅ Deployed! https://patrickdanforth.com/blog/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[DEPLOY] Git error: {e.stderr}")
        return False

# ── Main Pipeline ──────────────────────────────────────────────

print("═" * 50)
print(f"📖 Ikaris Self-Hosted Pipeline — {DATE_STR}")
print(f"📝 Title: {TITLE}")
print("═" * 50)

# Step 1: Art
art_filename = generate_art(TITLE, STORY)
if art_filename:
    status["art_generated"] = True
else:
    print("[PIPELINE] Art generation failed — posting without image")

# Step 2: Post
post_filename = create_post_html(TITLE, STORY, art_filename, TAGS)
status["post_created"] = True

# Step 3: Index
update_blog_index(TITLE, STORY, post_filename, TAGS)

# Step 4: RSS
update_rss_feed(TITLE, STORY, post_filename, TAGS)

# Step 5: Deploy
if deploy_site():
    status["deployed"] = True

# ── Summary ────────────────────────────────────────────────────
print("═" * 50)
print("📊 Pipeline Complete")
print(f"   Art generated:  {'✅' if status['art_generated'] else '❌'}")
print(f"   Post created:   {'✅' if status['post_created'] else '❌'}")
print(f"   Deployed:       {'✅' if status['deployed'] else '❌'}")
print(f"   Blog URL:       https://patrickdanforth.com/blog/{post_filename}")
print("═" * 50)

# Output JSON for programmatic use
print(json.dumps({"title": TITLE, "post_url": f"https://patrickdanforth.com/blog/{post_filename}", "status": status}))
