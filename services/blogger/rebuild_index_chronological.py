#!/usr/bin/env python3
"""Rebuild blog index with posts sorted newest-first (descending by date)."""

import re
from pathlib import Path

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"
IMAGES_DIR = SITE_ROOT / "ikaris-images"
BLOG_INDEX = POSTS_DIR / "index.html"

def get_post_info(html_file):
    """Extract title, date, excerpt, and image from a post HTML file."""
    content = html_file.read_text()
    
    # Title
    title = ""
    if "<h1>" in content:
        title = content.split("<h1>")[1].split("</h1>")[0]
    
    # Date from filename (YYYY-MM-DD)
    date = html_file.stem[:10]
    
    # Also try to get formatted date from meta
    formatted_date = date
    if 'class="post-meta"' in content:
        meta = content.split('class="post-meta"')[-1].split("</div>")[0]
        clean = re.sub(r'<[^>]*>', '', meta)
        parts = clean.split('·')
        if parts:
            formatted_date = parts[0].strip()
    
    # Excerpt (from first paragraph in post-body)
    excerpt = ""
    if 'class="post-body"' in content:
        body = content.split('class="post-body"')[1]
        # Find first <p> tag
        p_start = body.find("<p>")
        if p_start >= 0:
            p_content = body[p_start+3:]
            p_end = p_content.find("</p>")
            if p_end >= 0:
                raw = p_content[:p_end]
                # Remove any nested tags
                clean = re.sub(r'<[^>]*>', '', raw)
                excerpt = clean[:120] + "..." if len(clean) > 120 else clean
    
    # Image
    image = None
    if "ikaris-images/" in content:
        img_match = re.search(r'ikaris-images/([^"\s>]+)', content)
        if img_match:
            image = img_match.group(1)
    
    return {
        "title": title,
        "date": date,
        "formatted_date": formatted_date,
        "excerpt": excerpt,
        "image": image,
        "filename": html_file.name
    }

# Collect all posts
posts = []
for f in POSTS_DIR.glob("*.html"):
    if f.name == "index.html":
        continue
    info = get_post_info(f)
    if info["title"]:
        posts.append(info)

# Sort by date descending (newest first)
posts.sort(key=lambda x: x["date"], reverse=True)

print(f"Found {len(posts)} posts")
print("═" * 60)
for p in posts:
    img_status = "🖼️" if p["image"] else ""
    print(f"  {p['date']} — {p['title'][:50]:50s} {img_status}")

# Read current index
index_content = BLOG_INDEX.read_text()

# Find posts-list section
list_start = index_content.find('<div class="posts-list">')
after_start = list_start + len('<div class="posts-list">')
# Find the matching closing </div> (simple approach - first one after)
list_end = index_content.find('</div>', after_start) + 6

# Build new post cards - NEWEST FIRST
cards = []
for post in posts:
    thumb_html = ""
    if post["image"]:
        thumb_html = f'<img class="post-thumb" src="../ikaris-images/{post["image"]}" alt="{post["title"]}">'
    
    card = f"""      <a class="post-card" href="./{post['filename']}">
        {thumb_html}
        <div class="post-content">
          <div class="post-date">{post['formatted_date']}</div>
          <div class="post-title">{post['title']}</div>
          <div class="post-excerpt">{post['excerpt']}</div>
          <div class="post-tags">
            <span class="tag pink">Fiction</span>
            <span class="tag cyan">AI-Generated</span>
          </div>
        </div>
      </a>"""
    cards.append(card)

new_list = '<div class="posts-list">\n' + '\n'.join(cards) + '\n    </div>'

updated = index_content[:list_start] + new_list + index_content[list_end:]
BLOG_INDEX.write_text(updated)

print(f"\n{'═' * 60}")
print(f"✅ Blog index rebuilt: {len(posts)} posts sorted NEWEST FIRST")
print(f"   First: {posts[0]['date']} — {posts[0]['title']}")
print(f"   Last:  {posts[-1]['date']} — {posts[-1]['title']}")
print(f"{'═' * 60}")
