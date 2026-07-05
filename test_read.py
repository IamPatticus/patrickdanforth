#!/usr/bin/env python3
import sys
from pathlib import Path

# Read openrouter_image.py
path = Path("/home/patrick/.openclaw/workspace/services/blogger/openrouter_image.py")
if path.exists():
    content = path.read_text()
    print(f"File size: {len(content)} bytes")
    print("First 500 chars:")
    print(content[:500])
else:
    print("File not found")

# Read openclaw.json
path2 = Path("/home/patrick/.openclaw/openclaw.json")
if path2.exists():
    content2 = path2.read_text()
    print(f"\nopenclaw.json size: {len(content2)} bytes")
    print("First 500 chars:")
    print(content2[:500])
else:
    print("openclaw.json not found")