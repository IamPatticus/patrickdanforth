#!/usr/bin/env python3
"""Add proper Previous/Next navigation to all blog posts."""

from pathlib import Path

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"

# Get all posts sorted by date
def get_post_date(filename):
    """Extract YYYY-MM-DD from filename."""
    return filename.stem[:10]

posts = []
for f in sorted(POSTS_DIR.glob("*.html")):
    if f.name == "index.html":
        continue
    date = get_post_date(f)
    title = ""
    if "<h1>" in f.read_text():
        content = f.read_text()
        title = content.split("<h1>")[1].split("</h1>")[0]
    posts.append({"file": f, "date": date, "title": title, "stem": f.stem})

# Sort chronologically
posts.sort(key=lambda x: x["date"])

print(f"Found {len(posts)} posts to process")
print("═" * 60)

# Process each post
for i, post in enumerate(posts):
    content = post["file"].read_text()
    
    # Determine prev/next
    prev_link = ""
    next_link = ""
    
    if i > 0:
        prev_post = posts[i-1]
        prev_link = f'      <a class="nav-prev" href="./{prev_post['file'].name}">← Previous: {prev_post['title']}</a>'
    
    if i < len(posts) - 1:
        next_post = posts[i+1]
        next_link = f'      <a class="nav-next" href="./{next_post['file'].name}">Next: {next_post['title']} →</a>'
    
    # Build nav HTML
    nav_html = '\n'.join(filter(None, [next_link, prev_link]))
    if nav_html:
        nav_html = f'    <div class="post-nav"\u003e\n{nav_html}\n    </div\u003e'
    else:
        nav_html = '    <div class="post-nav"\u003e\n    </div\u003e'
    
    # Check if post already has post-nav
    if 'class="post-nav"' in content:
        # Replace existing nav section
        start = content.find('<div class="post-nav"')
        end_marker = '</div\u003e'
        # Find the closing div for post-nav (should be simple, not nested)
        after_start = start + len('<div class="post-nav"')
        end = content.find(end_marker, after_start) + len(end_marker)
        
        content = content[:start] + nav_html + content[end:]
    else:
        # Insert before footer
        footer_start = content.find('<div class="footer"')
        if footer_start > 0:
            content = content[:footer_start] + nav_html + '\n' + content[footer_start:]
    
    # Write updated file
    post["file"].write_text(content)
    
    status = ""
    if prev_link and next_link:
        status = "✅ Both"
    elif prev_link:
        status = "✅ Prev only"
    elif next_link:
        status = "✅ Next only"
    
    print(f"  {post['date']} — {post['title'][:45]:45s} | {status}")

print(f"\n{'═' * 60}")
print(f"✅ Updated {len(posts)} posts with navigation")
print(f"{'═' * 60}")
