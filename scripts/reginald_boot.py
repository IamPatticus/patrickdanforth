#!/usr/bin/env python3
"""
Reginald Boot — Restore the daily Reginald image to the SPI display framebuffer.
Runs at 8am to bring the screen back after overnight blanking.
"""

from PIL import Image, ImageEnhance
import os, sys, random

CACHE_DIR = os.path.expanduser("~/.cache/reginald-daily")
IMAGE_PATH = os.path.join(CACHE_DIR, "today.png")


def find_spi_fb():
    """Find the SPI display framebuffer (fb_ili9486)."""
    for i in range(3):
        try:
            with open(f"/sys/class/graphics/fb{i}/name") as f:
                if "ili9486" in f.read():
                    return f"/dev/fb{i}"
        except Exception:
            pass
    return "/dev/fb0"


def rgb888_to_rgb565_dithered(img):
    """Convert PIL image to RGB565 with error-dither via random noise."""
    img = img.convert("RGB")
    pixels = list(img.getdata())
    w, h = img.size
    out = bytearray(w * h * 2)
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[y * w + x]
            r16 = int((r * 31 + random.random() * 255) // 255)
            g16 = int((g * 63 + random.random() * 255) // 255)
            b16 = int((b * 31 + random.random() * 255) // 255)
            val = (r16 << 11) | (g16 << 5) | b16
            idx = (y * w + x) * 2
            out[idx] = val >> 8
            out[idx + 1] = val & 0xFF
    return bytes(out)


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"No cached image at {IMAGE_PATH}", file=sys.stderr)
        sys.exit(1)

    img = Image.open(IMAGE_PATH).resize((480, 320), Image.LANCZOS)

    # Match the enhancement pipeline from reginald_daily.py
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.4)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.5)

    buf = rgb888_to_rgb565_dithered(img)
    fb_path = find_spi_fb()
    with open(fb_path, "wb") as fb:
        fb.write(buf)
    print(f"Reginald boot: wrote {len(buf)} bytes to {fb_path}")


if __name__ == "__main__":
    main()
