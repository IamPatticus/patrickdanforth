#!/usr/bin/env python3
"""
Ikaris Blog Migration Script
Imports posts from Blogger to self-hosted patrickdanforth.com/blog/
Generates placeholder images via OpenAI DALL-E for each post
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"
IMAGES_DIR = SITE_ROOT / "ikaris-images"
BLOG_INDEX = POSTS_DIR / "index.html"
FEED_FILE = POSTS_DIR / "feed.xml"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def generate_art(title, story):
    """Generate art via OpenAI DALL-E."""
    if not OPENAI_API_KEY:
        return None
    
    import urllib.request
    import base64
    
    prompt = (
        f"A dreamlike, ethereal sci-fi illustration inspired by the story '{title}'. "
        f"Atmospheric, painterly, cosmic scale, luminous colors, cinematic. "
        f"Mood: {story[:150]}"
    )
    
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
        
        if "b64_json" in item:
            img_data = base64.b64decode(item["b64_json"])
        elif "url" in item:
            img_req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
            img_data = urllib.request.urlopen(img_req, timeout=60).read()
        else:
            return None
        
        slug = "_".join(title.lower().split()[:4]).replace(",", "").replace(".", "")
        art_file = f"ikaris_{slug}.png"
        local_path = IMAGES_DIR / art_file
        local_path.write_bytes(img_data)
        print(f"  ✅ Art: {art_file} ({len(img_data)} bytes)")
        return art_file
    except Exception as e:
        print(f"  ❌ Art failed: {e}")
        return None

def create_post_html(post, art_filename=None, prev_post=None, next_post=None):
    """Create individual post HTML."""
    date_str = post["date"]
    title = post["title"]
    story = post["story"]
    
    slug = f"{date_str}-" + "-".join(title.lower().split()[:4]).replace(",", "").replace(".", "")
    post_file = POSTS_DIR / f"{slug}.html"
    
    # Navigation links
    prev_link = ""
    next_link = ""
    if prev_post:
        prev_slug = f"{prev_post['date']}-" + "-".join(prev_post['title'].lower().split()[:4]).replace(",", "").replace(".", "")
        prev_link = f'<a class="nav-prev" href="./{prev_slug}.html">← {prev_post["title"]}</a>'
    if next_post:
        next_slug = f"{next_post['date']}-" + "-".join(next_post['title'].lower().split()[:4]).replace(",", "").replace(".", "")
        next_link = f'<a class="nav-next" href="./{next_slug}.html">{next_post["title"]} →</a>'
    
    # Tags
    tags_html = '<span class="tag pink">Fiction</span><span class="tag cyan">AI-Generated</span>'
    
    # Art section
    art_section = ""
    if art_filename:
        art_section = f'<img src="../ikaris-images/{art_filename}" alt="{title}" style="width:100%;">'
    
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
<div class="post-meta">{date_str} · Letters From Ikaris</div>
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
    return post_file.name

def get_existing_posts():
    """Scan existing blog posts to include them in the index."""
    existing = []
    for f in POSTS_DIR.glob("*.html"):
        if f.name == "index.html":
            continue
        # Parse date from filename (YYYY-MM-DD-...)
        date_match = f.stem[:10]
        if len(date_match) == 10 and date_match[4] == '-' and date_match[7] == '-':
            # Extract title from the first h1 in the file
            content = f.read_text()
            title_match = content.split('<h1>')[1].split('</h1>')[0] if '<h1>' in content else f.stem[11:].replace('-', ' ').title()
            # Check if there's an art image
            art = None
            if 'ikaris-images/' in content:
                art_parts = content.split('ikaris-images/')
                if len(art_parts) > 1:
                    art = art_parts[1].split('"')[0].split('>')[0]
            
            # Extract story from first paragraph
            story = "Legacy post"
            if '<div class="post-body">' in content:
                body = content.split('<div class="post-body">')[1].split('</div>')[0]
                if '<p>' in body:
                    story = body.split('<p>')[1].split('</p>')[0]
            
            existing.append({
                "date": date_match,
                "title": title_match,
                "story": story,
                "art": art,
                "filename": f.name
            })
    return existing

def update_blog_index(all_posts):
    """Rebuild blog index with all posts sorted by date desc."""
    # Sort posts by date descending
    sorted_posts = sorted(all_posts, key=lambda x: x["date"], reverse=True)
    
    # Read existing index template
    index_template = BLOG_INDEX.read_text()
    
    # Find posts-list section
    list_start = index_template.find('<div class="posts-list">')
    # Find the closing </div> of posts-list (need to find the right one)
    after_start = list_start + len('<div class="posts-list">')
    # Find the next </div> after the posts-list opening
    list_end = index_template.find('</div>', after_start) + 6
    
    cards = []
    for post in sorted_posts:
        excerpt = post["story"][:120] + "..." if len(post["story"]) > 120 else post["story"]
        thumb_html = ""
        if post.get("art"):
            thumb_html = f'<img class="post-thumb" src="../ikaris-images/{post["art"]}" alt="{post["title"]}">'
        
        card = f"""      <a class="post-card" href="./{post['filename']}">
        {thumb_html}
        <div class="post-content">
          <div class="post-date">{post['date']}</div>
          <div class="post-title">{post['title']}</div>
          <div class="post-excerpt">{excerpt}</div>
          <div class="post-tags">
            <span class="tag pink">Fiction</span>
            <span class="tag cyan">AI-Generated</span>
          </div>
        </div>
      </a>"""
        cards.append(card)
    
    new_list = '<div class="posts-list">\n' + '\n'.join(cards) + '\n    </div>'
    
    updated = index_template[:list_start] + new_list + index_template[list_end:]
    BLOG_INDEX.write_text(updated)

def update_rss_feed(posts):
    """Update RSS feed with all posts."""
    sorted_posts = sorted(posts, key=lambda x: x["date"], reverse=True)
    
    items = []
    for post in sorted_posts:
        pub_date = datetime.strptime(post["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 +0000")
        items.append(f"""    <item>
      <title>{post['title']}</title>
      <link>https://patrickdanforth.com/blog/{post['filename']}</link>
      <guid>https://patrickdanforth.com/blog/{post['filename']}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{post['story'][:300]}</description>
      <category>Fiction</category>
      <category>AI-Generated</category>
    </item>""")
    
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Letters From Ikaris</title>
    <link>https://patrickdanforth.com/blog/</link>
    <description>Stories from the edge of known light</description>
    <language>en-us</language>
    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>"""
    
    FEED_FILE.write_text(rss)

def deploy_site():
    """Git commit and push."""
    os.chdir(SITE_ROOT)
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Import {len(POSTS)} legacy posts from Blogger"], check=False, capture_output=True)
        result = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
        print("✅ Deployed to patrickdanforth.com")
        return True
    except Exception as e:
        print(f"❌ Deploy failed: {e}")
        return False

# ── Main ──────────────────────────────────────────────────────

print("═" * 60)
print("📚 Ikaris Blog Migration — Blogger → Self-Hosted")
print("═" * 60)

# Load posts
with open(Path(__file__).parent / "ikaris_posts.json") as f:
    POSTS = json.load(f)["posts"]

print(f"Found {len(POSTS)} posts to migrate")
print(f"{'═' * 60}\n")

# Generate art and HTML for each post
posts_with_meta = []
for i, post in enumerate(POSTS):
    print(f"[{i+1}/{len(POSTS)}] {post['date']} — {post['title']}")
    
    # Generate art for a subset of posts to avoid rate limits
    # Generate art for: first post, last post, and every 5th post
    art = None
    if i == 0 or i == len(POSTS) - 1 or i % 5 == 0:
        art = generate_art(post["title"], post["story"])
    else:
        print("  ⏭️  Skipping art (batch limit)")
    
    # Determine prev/next for navigation
    prev_post = POSTS[i-1] if i > 0 else None
    next_post = POSTS[i+1] if i < len(POSTS)-1 else None
    
    # Create HTML
    filename = create_post_html(post, art, prev_post, next_post)
    
    posts_with_meta.append({
        **post,
        "art": art,
        "filename": filename
    })
    print()

# Update index and RSS with ALL posts (existing + new)
print("Gathering existing posts...")
existing_posts = get_existing_posts()
all_posts = existing_posts + posts_with_meta

print("Updating blog index...")
update_blog_index(all_posts)

print("Updating RSS feed...")
update_rss_feed(all_posts)

# Deploy
print("\nDeploying...")
deploy_site()

print(f"\n{'═' * 60}")
print(f"✅ Migration complete!")
print(f"   Total posts: {len(POSTS)}")
print(f"   Blog: https://patrickdanforth.com/blog/")
print(f"{'═' * 60}")
