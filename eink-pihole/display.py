#!/usr/bin/env python3
"""Render Pi-hole stats on Waveshare 2.13" E-Ink HAT V4 (black/white/red)."""
import os
import sys
import time
import traceback
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    from waveshare_epd import epd2in13b_V4
except ImportError as e:
    print(f"waveshare_epd import failed: {e}", file=sys.stderr)
    sys.exit(1)

from pihole_client import PiHoleClient, load_password

WIDTH = 250
HEIGHT = 122
MARGIN = 4
LINE_H = 14


def get_font(size=12):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fetch_data():
    base = os.environ.get("PIHOLE_URL", "http://127.0.0.1")
    pw = load_password()
    if not pw:
        return None, "No password in ~/eink-pihole/.pihole_pass"
    try:
        client = PiHoleClient(base)
        summary = client.get_summary()
        return summary, None
    except Exception as e:
        return None, str(e)


def format_number(n):
    if n is None:
        return "-"
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        bbox = font.getbbox(test)
        w_px = bbox[2] - bbox[0] if bbox else 0
        if w_px <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def render(summary, error=None):
    black = Image.new('1', (WIDTH, HEIGHT), 255)
    draw_b = ImageDraw.Draw(black)
    red = Image.new('1', (WIDTH, HEIGHT), 255)

    font_bold = get_font(14)
    font = get_font(12)
    font_small = get_font(10)

    draw_b.rectangle([0, 0, WIDTH - 1, 18], fill=0)
    draw_b.text((MARGIN, 2), "PI-HOLE STATUS", font=font_bold, fill=255)

    y = 22

    if error:
        draw_b.text((MARGIN, y), "Error:", font=font, fill=0)
        y += LINE_H
        for line in wrap_text(error, font_small, WIDTH - MARGIN * 2):
            draw_b.text((MARGIN, y), line, font=font_small, fill=0)
            y += LINE_H - 1
            if y > HEIGHT - 10:
                break
        return black, red

    queries = summary.get("queries", {})
    clients = summary.get("clients", {})
    gravity = summary.get("gravity", {})

    total = queries.get("total", 0)
    blocked = queries.get("blocked", 0)
    percent = queries.get("percent_blocked", 0)
    unique_clients = clients.get("active", 0)
    blocklist_domains = gravity.get("domains_being_blocked", 0)

    draw_b.text((MARGIN, y), f"Queries: {format_number(total)}", font=font, fill=0)
    draw_b.text((WIDTH // 2, y), f"Blocked: {format_number(blocked)}", font=font, fill=0)
    y += LINE_H + 2

    draw_b.text((MARGIN, y), f"Blocked %: {percent}%", font=font, fill=0)
    draw_b.text((WIDTH // 2, y), f"Clients: {unique_clients}", font=font, fill=0)
    y += LINE_H + 2

    draw_b.line([MARGIN, y, WIDTH - MARGIN, y], fill=0, width=1)
    y += 4

    draw_b.text((MARGIN, y), f"Blocklist: {format_number(blocklist_domains)} domains", font=font_small, fill=0)
    y += LINE_H

    now = time.strftime("%Y-%m-%d %H:%M")
    draw_b.text((MARGIN, HEIGHT - 12), f"Updated: {now}", font=font_small, fill=0)

    return black, red


def update_display(black, red):
    epd = epd2in13b_V4.EPD()
    epd.init()
    epd.display(epd.getbuffer(black), epd.getbuffer(red))
    epd.sleep()


def main():
    summary, error = fetch_data()
    black, red = render(summary, error)
    try:
        update_display(black, red)
        print("Display updated.")
    except Exception:
        debug_path = Path.home() / "eink-pihole" / "debug_black.png"
        black.save(debug_path)
        traceback.print_exc()
        print(f"Saved debug render to {debug_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
