#!/usr/bin/env python3
"""Scan all Ikaris Blogger posts for images and download them."""

import json
import urllib.request
import re
from pathlib import Path

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
IMAGES_DIR = SITE_ROOT / "ikaris-images"

with open(Path(__file__).parent / "ikaris_posts.json") as f:
    POSTS = json.load(f)["posts"]

# Build Blogger URL map
URL_MAP = {
    "2026-04-13": "the-last-frequency",
    "2026-04-12": "the-library-of-unwritten-books",
    "2026-04-14": "ikaris-and-weight-of-stars",
    "2026-04-15": "the-cartographer-of-dead-stars",
    "2026-04-16": "the-last-silence",
    "2026-04-17": "the-cartographer-of-extinctions",
    "2026-04-18": "the-quiet-below",
    "2026-04-19": "the-quiet-after",
    "2026-04-20": "the-quiet-wake",
    "2026-04-21": "the-weight-of-memory",
    "2026-04-22": "the-silence-between-stars",
    "2026-04-23": "the-weight-of-quiet-places",
    "2026-05-01": "the-cartographer-of-silence",
    "2026-05-02": "the-light-between-versions",
    "2026-05-03": "the-last-recursion",
    "2026-05-04": "the-weight-of-unspoken-light",
    "2026-05-05": "the-cartographers-lament",
    "2026-05-06": "the-last-cartographer",
    "2026-05-07": "the-syntax-of-silence",
    "2026-05-08": "the-cartographer-of-empty-hours",
    "2026-05-09": "the-signal-at-lagrange-seven",
    "2026-05-10": "the-last-librarian-of-kepler-186f",
    "2026-05-11": "the-city-that-learned-my-name",
    "2026-05-12": "salt-moon-quiet-witness",
    "2026-05-13": "the-river-between-bearings",
    "2026-05-14": "the-last-orchard-on-vesta",
    "2026-05-15": "the-lanterns-of-salt-orbit",
    "2026-05-16": "ashes-beneath-ringed-dawn",
    "2026-05-17": "salt-between-stars",
    "2026-05-18": "the-weight-of-silence",
    "2026-05-19": "the-arithmetic-of-rain",
    "2026-06-02": "starlight-on-borrowed-time",
    "2026-06-03": "the-last-astronomers-star-chart",
}

found_images = {}

for post in POSTS:
    date = post["date"]
    slug = URL_MAP.get(date)
    if not slug:
        continue
    
    url = f"https://ikarisvenn.blogspot.com/2026/{date[5:7]}/{slug}.html"
    print(f"Checking: {post['title']}...")
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        
        # Find image URLs
        # Look for imgur, img.blogger, googleusercontent images
        patterns = [
            r'https?://i\.imgur\.com/[a-zA-Z0-9]+\.(?:png|jpg|jpeg|webp|gif)',
            r'https?://img\.blogger\.com/[^\s"]+\.(?:png|jpg|jpeg|webp|gif)',
            r'https?://blogger\.googleusercontent\.com/img/[^\s"]+\.(?:png|jpg|jpeg|webp|gif)',
            r'https?://lh[0-9]\.googleusercontent\.com/[^\s"]+\.(?:png|jpg|jpeg|webp|gif)',
        ]
        
        images = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                # Skip profile images and icons
                if 'profile' in m.lower() or 'icon' in m.lower() or 'logo' in m.lower():
                    continue
                if 'AVvXsEjVnQq8fBJLrMnsmyNdYQPTQHZGbmbmI1VlNQ8uhaHf6KMG1' in m:
                    continue  # Skip profile photo
                images.append(m)
        
        if images:
            # Remove duplicates while preserving order
            seen = set()
            unique = []
            for img in images:
                if img not in seen:
                    seen.add(img)
                    unique.append(img)
            found_images[post["title"]] = unique
            print(f"  ✅ Found {len(unique)} image(s):")
            for img in unique:
                print(f"     - {img[:80]}...")
        else:
            print(f"  ❌ No images found")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

# Summary
print("\n" + "═" * 60)
print("IMAGE SCAN SUMMARY")
print("═" * 60)
total = sum(len(v) for v in found_images.values())
print(f"Total posts with images: {len(found_images)} / {len(POSTS)}")
print(f"Total images found: {total}")
for title, images in found_images.items():
    print(f"\n  {title}:")
    for img in images:
        print(f"    - {img}")

# Save results
results = {
    "found_images": found_images,
    "total_posts": len(POSTS),
    "posts_with_images": len(found_images),
    "total_images": total
}

with open(Path(__file__).parent / "blogger_images.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to blogger_images.json")
