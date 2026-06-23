#!/usr/bin/env python3
import os, json, urllib.request, base64
from pathlib import Path

KEY = os.environ.get("OPENAI_API_KEY", "")
IMAGES = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site" / "ikaris-images"
POSTS = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site" / "blog"
LIMIT = 50


def gen_art(title, story):
    if not KEY:
        return None
    prompt = f"A dreamlike, ethereal sci-fi illustration inspired by '{title}'. Atmospheric, painterly, cosmic scale."
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps({"model": "gpt-image-1", "prompt": prompt, "n": 1, "size": "1024x1024", "quality": "auto"}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        item = json.loads(resp.read())["data"][0]
        if "b64_json" in item:
            return base64.b64decode(item["b64_json"])
        elif "url" in item:
            r2 = urllib.request.urlopen(urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60)
            return r2.read()
        return None
    except Exception as e:
        print(f"    API error: {e.__class__.__name__}, using fallback")
        return None

posts = []
for f in POSTS.glob("*.html"):
    if f.name == "index.html": continue
    c = f.read_text()
    import re
    if re.search(r"ikaris-images/ikaris_\d{8,}_", c):
        continue
    title = c.split("<h1>")[1].split("</h1>")[0] if "<h1>" in c else f.stem
    story = ""
    bi = c.split('class="post-body"')
    if len(bi) > 1 and "<p>" in bi[1]:
        story = bi[1].split("<p>")[1].split("</p>")[0]
    posts.append({"file": f, "title": title, "story": story})

print(f"Found {len(posts)} posts needing images")
print("="*50)

gen = 0
for i, p in enumerate(posts[:LIMIT]):
    print(f"[{i+1}/{min(LIMIT,len(posts))}] {p['title']}")
    data = gen_art(p["title"], p["story"])
    if data:
        fn = f"ikaris_{p['title'].lower().replace(' ', '_')[:30]}.png"
        (IMAGES/fn).write_bytes(data)
        print(f"  ✅ PNG: {fn}")
        html = p["file"].read_text()
        art = f'<img src="../ikaris-images/{fn}" alt="{p["title"]}" style="width:100%;">'
        for oldpat, newpat in [("</div>\n<div class=\"post-body\"", f"</div>\n{art}\n<div class=\"post-body\""),
                               ("</div>\n<div class=\"post-nav\"", f"</div>\n{art}\n<div class=\"post-nav\"")]:
            if oldpat in html:
                html = html.replace(oldpat, newpat)
                break
        p["file"].write_text(html)
        print(f"  🔄 Updated")
        gen += 1
    else:
        from datetime import datetime as dt
        svg_fn = f"ikaris_{p['title'].lower().replace(' ', '_')[:30]}_{dt.now().strftime('%Y%m%d_%H%M%S')}.svg"
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"><rect width="1024" height="1024" fill="#0a0a1a"/><text x="512" y="512" font-family="monospace" font-size="24" fill="#7ae7ff" text-anchor="middle" dominant-baseline="middle">{p["title"][:40]}</text><text x="512" y="540" font-family="monospace" font-size="14" fill="#9aa7c2" text-anchor="middle" dominant-baseline="middle">4-panel comic</text></svg>'
        (IMAGES/svg_fn).write_text(svg)
        print(f"  ✅ SVG: {svg_fn}")
        html = p["file"].read_text()
        art = f'<img src="../ikaris-images/{svg_fn}" alt="{p["title"]}" style="width:100%;">'
        for oldpat, newpat in [("</div>\n<div class=\"post-body\"", f"</div>\n{art}\n<div class=\"post-body\""),
                               ("</div>\n<div class=\"post-nav\"", f"</div>\n{art}\n<div class=\"post-nav\"")]:
            if oldpat in html:
                html = html.replace(oldpat, newpat)
                break
        p["file"].write_text(html)
        print(f"  🔄 Updated")
        gen += 1

print("="*50)
print(f"Done: {gen} generated/SVG out of {len(posts[:LIMIT])} processed")
print(f"Remaining: {len(posts)-gen} unreported out of {len(posts)} total")
