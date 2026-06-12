#!/usr/bin/env python3
"""Generate missing images for blog posts that don't have artwork."""

import os
import json
import urllib.request
import base64
from pathlib import Path

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
IMAGES_DIR = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site" / "ikaris-images"
POSTS_DIR = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site" / "blog"

def generate_art(title, story):
    """Generate art via OpenAI DALL-E."""
    if not OPENAI_API_KEY:
        return None
    
    prompt = (
        f"A dreamlike, ethereal sci-fi illustration inspired by the story '{title}'. "
        f"Atmospheric, painterly, cosmic scale, luminous colors, cinematic composition. "
        f"Mood: {story[:200]}"
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
        
        return img_data
    except Exception as e:
        print(f"    ❌ Generation failed: {e}")
        return None

# Find posts without images
posts_needing_images = []
for f in POSTS_DIR.glob("*.html"):
    if f.name == "index.html":
        continue
    content = f.read_text()
    if "ikaris-images/" not in content:
        title = content.split("<h1>")[1].split("</h1>")[0] if "<h1>" in content else f.stem
        story = ""
        if 'class="post-body"' in content:
            body = content.split('class="post-body"')[1]
            if "<p>" in body:
                story = body.split("<p>")[1].split("</p>")[0]
        posts_needing_images.append({"file": f, "title": title, "story": story})

print(f"Found {len(posts_needing_images)} posts needing images")
print("═" * 60)

# Generate images (limit to 5 per run to avoid rate limits)
LIMIT = 5
generated = 0

for i, post in enumerate(posts_needing_images[:LIMIT]):
    print(f"[{i+1}/{min(LIMIT, len(posts_needing_images))}] {post['title']}")
    
    img_data = generate_art(post['title'], post['story'])
    if img_data:
        safe = "_".join(post['title'].lower().split()[:4]).replace(",", "").replace(".", "").replace("'", "")
        filename = f"ikaris_generated_{safe}.png"
        path = IMAGES_DIR / filename
        path.write_bytes(img_data)
        print(f"  ✅ Saved: {filename} ({len(img_data)} bytes)")
        
        # Update post HTML
        content = post['file'].read_text()
        art_section = f'<img src="../ikaris-images/{filename}" alt="{post['title']}" style="width:100%;">'
        
        if '</div>\n<div class="post-body"' in content:
            content = content.replace(
                '</div>\n<div class="post-body"',
                f'</div>\n{art_section}\n<div class="post-body"'
            )
        elif '</div>\n<div class="post-nav"' in content:
            content = content.replace(
                '</div>\n<div class="post-nav"',
                f'</div>\n{art_section}\n<div class="post-nav"'
            )
        
        post['file'].write_text(content)
        print(f"  🔄 Updated post HTML")
        generated += 1

print(f"\n{'═' * 60}")
print(f"✅ Generated {generated} images out of {len(posts_needing_images)} needed")
print(f"Remaining: {len(posts_needing_images) - generated} posts still need images")
print(f"{'═' * 60}")
