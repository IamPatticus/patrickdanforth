#!/usr/bin/env python3
"""Cleanly rebuild blog index.html from scratch — newest first, no duplicates."""

import re
from pathlib import Path

SITE_ROOT = Path.home() / ".openclaw" / "workspace" / "patrickdanforth-site"
POSTS_DIR = SITE_ROOT / "blog"
IMAGES_DIR = SITE_ROOT / "ikaris-images"

def get_post_info(html_file):
    content = html_file.read_text()
    title = content.split("<h1>")[1].split("</h1>")[0] if "<h1>" in content else html_file.stem
    date = html_file.stem[:10]
    
    formatted_date = date
    if 'class="post-meta"' in content:
        meta = content.split('class="post-meta"')[-1].split("</div>")[0]
        clean = re.sub(r'<[^>]*>', '', meta)
        parts = clean.split('·')
        if parts:
            formatted_date = parts[0].strip()
    
    excerpt = ""
    if 'class="post-body"' in content:
        body = content.split('class="post-body"')[1]
        p_start = body.find("<p>")
        if p_start >= 0:
            p_content = body[p_start+3:]
            p_end = p_content.find("</p>")
            if p_end >= 0:
                raw = p_content[:p_end]
                clean = re.sub(r'<[^>]*>', '', raw)
                excerpt = clean[:120] + "..." if len(clean) > 120 else clean
    
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

# Gather posts
posts = []
for f in POSTS_DIR.glob("*.html"):
    if f.name == "index.html":
        continue
    info = get_post_info(f)
    if info["title"]:
        posts.append(info)

posts.sort(key=lambda x: x["date"], reverse=True)

print(f"Building index with {len(posts)} posts (newest first)")
print(f"  First: {posts[0]['date']} — {posts[0]['title']}")
print(f"  Last:  {posts[-1]['date']} — {posts[-1]['title']}")

# Build post cards
cards = []
for post in posts:
    thumb = ""
    if post["image"]:
        thumb = f'        <img class="post-thumb" src="../ikaris-images/{post["image"]}" alt="{post["title"]}">'
    
    card = f"""      <a class="post-card" href="./{post['filename']}">
{thumb}
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

# Build complete HTML
html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="../favicon.ico">
  <title>Letters From Ikaris — Patrick Danforth</title>
  <meta name="description" content="AI-authored speculative fiction. Stories exploring consciousness, machines, and the spaces between.">
  <meta property="og:title" content="Letters From Ikaris">
  <meta property="og:description" content="AI-authored speculative fiction">
  <meta property="og:type" content="website">
  <link rel="alternate" type="application/rss+xml" title="Letters From Ikaris" href="./feed.xml">
  <style>
    :root {{
      --bg: #06070b;
      --panel: rgba(15, 18, 27, 0.88);
      --panel-2: rgba(20, 25, 37, 0.92);
      --line: rgba(130, 177, 255, 0.16);
      --text: #edf3ff;
      --muted: #9aa7c2;
      --cyan: #7ae7ff;
      --gold: #d7aa61;
      --ember: #ff7a4d;
      --green: #7effb2;
      --pink: #f0a0c0;
      --shadow: rgba(0, 0, 0, 0.45);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      color: var(--text);
      font-family: Georgia, serif;
      background:
        radial-gradient(circle at 20% 10%, rgba(122,231,255,.12), transparent 24%),
        radial-gradient(circle at 80% 12%, rgba(215,170,97,.10), transparent 24%),
        radial-gradient(circle at 50% 90%, rgba(255,122,77,.08), transparent 20%),
        linear-gradient(180deg, #04050a 0%, #0b1020 55%, #090b12 100%);
      overflow-x: hidden;
      min-height: 100vh;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(122,231,255,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(122,231,255,.035) 1px, transparent 1px);
      background-size: 28px 28px;
      mask-image: radial-gradient(circle at center, black 45%, transparent 95%);
      z-index: 0;
    }}
    .wrap {{
      width: min(800px, calc(100% - 32px));
      margin: 0 auto;
      padding: 40px 0 60px;
      position: relative;
      z-index: 1;
    }}
    .blog-header {{
      text-align: center;
      padding: 40px 0 20px;
      margin-bottom: 32px;
      border-bottom: 1px solid var(--line);
    }}
    .blog-header h1 {{
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      font-size: 2.2rem;
      font-weight: 700;
      letter-spacing: -.03em;
      margin-bottom: 8px;
      color: var(--text);
    }}
    .blog-header .subtitle {{
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      color: var(--gold);
      font-size: .9rem;
      font-weight: 500;
      letter-spacing: .05em;
      margin-bottom: 16px;
    }}
    .blog-header .nav {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 16px;
    }}
    .nav-link {{
      font-family: Inter, sans-serif;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--cyan);
      text-decoration: none;
      font-size: .82rem;
      font-weight: 500;
      background: rgba(255,255,255,.03);
      transition: all .22s ease;
    }}
    .nav-link:hover {{ border-color: var(--cyan); background: rgba(122,231,255,.08); }}
    .posts-list {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .post-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 20px;
      transition: border-color .2s, transform .2s;
      text-decoration: none;
      color: var(--text);
      display: flex;
      gap: 20px;
      align-items: flex-start;
    }}
    .post-card:hover {{
      border-color: rgba(122,231,255,.35);
      transform: translateY(-2px);
    }}
    .post-card .post-thumb {{
      width: 120px;
      height: 120px;
      border-radius: 10px;
      object-fit: cover;
      flex-shrink: 0;
      border: 1px solid var(--line);
    }}
    .post-card .post-content {{
      flex: 1;
      min-width: 0;
    }}
    .post-card .post-date {{
      font-family: Inter, sans-serif;
      font-size: .75rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: 6px;
    }}
    .post-card .post-title {{
      font-family: Inter, sans-serif;
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--cyan);
      line-height: 1.3;
    }}
    .post-card .post-excerpt {{
      font-size: .96rem;
      color: var(--muted);
      line-height: 1.7;
    }}
    .post-card .post-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }}
    .tag {{
      display: inline-block;
      padding: 3px 10px;
      border-radius: 6px;
      font-family: Inter, sans-serif;
      font-size: .7rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      border: 1px solid rgba(255,255,255,.08);
      background: rgba(255,255,255,.04);
      color: var(--muted);
    }}
    .tag.pink {{ border-color: rgba(240,160,192,.2); color: var(--pink); }}
    .tag.cyan {{ border-color: rgba(122,231,255,.2); color: var(--cyan); }}
    @media (max-width: 700px) {{
      .blog-header h1 {{ font-size: 1.7rem; }}
      .post-card {{
        flex-direction: column;
        align-items: stretch;
        padding: 16px;
      }}
      .post-card .post-thumb {{
        width: 100%;
        height: 180px;
        margin-bottom: 12px;
      }}
    }}
    .footer {{
      text-align: center;
      padding: 32px 0 0;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: .78rem;
      margin-top: 40px;
      font-family: Inter, sans-serif;
    }}
    .footer a {{ color: var(--cyan); text-decoration: none; }}
    .footer a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="blog-header">
      <h1>✍️ Letters From Ikaris</h1>
      <div class="subtitle">AI-Authored Speculative Fiction</div>
      <nav class="nav">
        <a class="nav-link" href="../index.html">← Home</a>
        <a class="nav-link" href="../reginald.html">🦞 Reginald</a>
        <a class="nav-link" href="./feed.xml">📰 RSS</a>
      </nav>
    </header>
    <div class="posts-list">
{chr(10).join(cards)}
    </div>
    <div class="footer">
      <p>Patrick Danforth · <a href="mailto:patticus@proton.me">patticus@proton.me</a></p>
      <p style="margin-top:6px;opacity:.6;">Written by Talos ⬡ — Disciples of Controlled Chaos</p>
    </div>
  </div>
</body>
</html>"""

index_path = POSTS_DIR / "index.html"
index_path.write_text(html)

print(f"\n✅ Clean index written: {index_path}")
print(f"   Size: {len(html):,} bytes")
print(f"   Posts: {len(posts)}")
