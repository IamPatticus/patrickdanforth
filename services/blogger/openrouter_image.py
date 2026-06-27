#!/usr/bin/env python3
"""
OpenRouter direct image generation helper.
Uses OpenRouter's /api/v1/images endpoint for models like FLUX.2 Flex.
"""

import os
import json
import base64
import urllib.request
from pathlib import Path

DEFAULT_IMAGE_MODEL = "black-forest-labs/flux.2-flex"


def get_openrouter_key():
    """Find an OpenRouter API key from env or OpenClaw config."""
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
    if key:
        return key
    # Try to read from OpenClaw config
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            key = data.get("models", {}).get("providers", {}).get("openrouter", {}).get("apiKey")
            if key and key != "***":
                return key
        except Exception:
            pass
    return None


def generate_image(prompt: str, output_path: str, model: str = DEFAULT_IMAGE_MODEL,
                   width: int = 1024, height: int = 1024, timeout: int = 180) -> bool:
    """Generate an image via OpenRouter's dedicated image endpoint.

    Returns True on success and writes the decoded PNG/JPEG to output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    key = get_openrouter_key()
    if not key:
        print("[OpenRouter Image] No API key found in env or config", file=__import__("sys").stderr)
        return False

    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/images",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Response can be b64_json or url
        b64 = data.get("data", [{}])[0].get("b64_json")
        if b64:
            output_path.write_bytes(base64.b64decode(b64))
            print(f"[OpenRouter Image] Saved {output_path} ({model})")
            return True

        url = data.get("data", [{}])[0].get("url")
        if url:
            urllib.request.urlretrieve(url, output_path)
            print(f"[OpenRouter Image] Saved {output_path} from URL ({model})")
            return True

        print(f"[OpenRouter Image] Unexpected response: {data}", file=__import__("sys").stderr)
    except Exception as e:
        print(f"[OpenRouter Image] Generation failed: {e}", file=__import__("sys").stderr)

    return False
