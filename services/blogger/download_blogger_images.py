#!/usr/bin/env python3
"""Download Blogger images from Imgur and update blog posts."""

import json
import urllib.request
from pathlib import Path

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"
IMAGES_DIR = SITE_ROOT / "ikaris-images"

with open(Path(__file__).parent / "blogger_images.json") as f:
    DATA = json.load(f)

# Build title → filename map from existing posts
TITLE_TO_FILE = {}
for f in POSTS_DIR.glob("*.html"):
    if f.name == "index.html":
        continue
    content = f.read_text()
    if "<h1>" in content:
        title = content.split("<h1>")[1].split("</h1>")[0]
        TITLE_TO_FILE[title] = f

print("═" * 60)
print("📸 Downloading Blogger Images & Updating Posts")
print("═" * 60)

downloaded = 0
updated = 0

for title, images in DATA["found_images"].items():
    if not images:
        continue
    
    post_file = TITLE_TO_FILE.get(title)
    if not post_file:
        print(f"⚠️ Post not found: {title}")
        continue
    
    print(f"\n📝 {title}")
    
    # Download the first image
    img_url = images[0]
    ext = img_url.split('.')[-1].split('?')[0]
    if ext not in ['png', 'jpg', 'jpeg', 'webp', 'gif']:
        ext = 'png'
    
    # Create safe filename
    safe_title = "_".join(title.lower().split()[:4]).replace(",", "").replace(".", "").replace("'", "")
    local_name = f"ikaris_legacy_{safe_title}.{ext}"
    local_path = IMAGES_DIR / local_name
    
    try:
        # Download image
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urllib.request.urlopen(req, timeout=30).read()
        local_path.write_bytes(img_data)
        print(f"  ✅ Downloaded: {local_name} ({len(img_data)} bytes)")
        downloaded += 1
        
        # Update HTML post to use local image
        content = post_file.read_text()
        
        # Check if there's already an image section
        if 'ikaris-images/' in content:
            # Replace existing image reference
            old_img = content.split('ikaris-images/')[1].split('"')[0].split('>')[0]
            content = content.replace(f'ikaris-images/{old_img}', f'ikaris-images/{local_name}')
            print(f"  🔄 Updated existing image reference")
        else:
            # Add image section after tags div
            art_section = f'<img src="../ikaris-images/{local_name}" alt="{title}" style="width:100%;">'
            # Insert after the tags div closing
            if '</div>\n<div class="post-body"' in content:
                content = content.replace(
                    '</div>\n<div class="post-body"',
                    f'</div>\n{art_section}\n<div class="post-body"'
                )
                print(f"  🔄 Added image to post")
            elif '</div>\n<div class="post-nav"' in content:
                content = content.replace(
                    '</div>\n<div class="post-nav"',
                    f'</div>\n{art_section}\n<div class="post-nav"'
                )
                print(f"  🔄 Added image to post")
        
        post_file.write_text(content)
        updated += 1
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")

print(f"\n{'═' * 60}")
print(f"✅ Done! Downloaded: {downloaded} images, Updated: {updated} posts")
print(f"{'═' * 60}")
