"""Composio + Gemini image generation fallback.

Uses the Composio v3.1 API to call GEMINI_GENERATE_IMAGE and downloads the
resulting image from the returned S3 URL.

Requires COMPOSIO_API_KEY in ~/.config/composio.env
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_KEY = None
ENV_FILE = Path.home() / ".config" / "composio.env"


def _load_api_key():
    global API_KEY
    if API_KEY:
        return API_KEY
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("COMPOSIO_API_KEY="):
                    API_KEY = line.strip().split("=", 1)[1]
                    break
    return API_KEY


def generate_image(prompt, output_path, model="gemini-2.5-flash-image", aspect_ratio="3:2", image_size="2K", timeout=300):
    """Generate an image via Composio GEMINI_GENERATE_IMAGE and save to output_path.

    Returns True on success, False on failure.
    """
    api_key = _load_api_key()
    if not api_key:
        print("[COMPOSIO_IMAGE] No COMPOSIO_API_KEY found in ~/.config/composio.env", file=sys.stderr)
        return False

    url = "https://backend.composio.dev/api/v3.1/tools/execute/GEMINI_GENERATE_IMAGE"
    payload = {
        "arguments": {
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
        }
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[COMPOSIO_IMAGE] HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[COMPOSIO_IMAGE] Request failed: {e}", file=sys.stderr)
        return False

    if not result.get("successful"):
        print(f"[COMPOSIO_IMAGE] Tool execution failed: {result.get('error')}", file=sys.stderr)
        return False

    image_info = result.get("data", {}).get("image", {})
    s3_url = image_info.get("s3url")
    if not s3_url:
        print("[COMPOSIO_IMAGE] No s3url in response", file=sys.stderr)
        return False

    try:
        dl_req = urllib.request.Request(
            s3_url,
            headers={"Accept": "image/png,image/jpeg,image/webp,*/*"},
        )
        with urllib.request.urlopen(dl_req, timeout=120) as resp:
            image_bytes = resp.read()
    except Exception as e:
        print(f"[COMPOSIO_IMAGE] Download failed: {e}", file=sys.stderr)
        return False

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"[COMPOSIO_IMAGE] Generated and saved: {output_path} ({len(image_bytes)} bytes)")
    return True
