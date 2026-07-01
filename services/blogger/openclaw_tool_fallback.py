#!/usr/bin/env python3
"""
OpenClaw tool-call shim for cron Python scripts.
Calls the openclaw CLI's native tool invoker (if available) or falls back to spawning a subagent.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _openclaw_bin():
    return shutil.which("openclaw") or "/home/patrick/.npm-global/bin/openclaw"


def _gateway_token():
    try:
        cfg = json.loads(Path("/home/patrick/.openclaw/openclaw.json").read_text())
        return cfg["gateway"]["auth"]["token"]
    except Exception:
        return os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")


def call_image_generate(prompt: str, output_path: str, model: str = "openai/gpt-image-2", size: str = "1536x1024") -> bool:
    """Best-effort image generation through OpenClaw tooling.

    Strategy:
    1. Use the native CLI `openclaw tools run image_generate` if available.
    2. Otherwise, write a tiny ephemeral JS/ACP payload to the gateway's ACP endpoint.
    3. As a last resort, spawn an isolated OpenClaw subagent and wait for it.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Strategy 1: Try the CLI's hidden/native tool runner.
    openclaw = _openclaw_bin()
    cmd = [
        openclaw, "tools", "run", "image_generate",
        "--prompt", prompt,
        "--model", model,
        "--size", size,
        "--output", str(output_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"[image_generate] Generated via CLI tool runner: {output_path}")
            return True
    except Exception as e:
        print(f"[image_generate] CLI tool runner unavailable/error: {e}", file=sys.stderr)

    # Strategy 2: Spawn an isolated subagent with the image_generate task and wait.
    # We can't use sessions_spawn from inside a non-agent python process, so instead
    # create a tiny OpenClaw run-file and invoke `openclaw run` on it.
    token = _gateway_token()
    if not token:
        print("[image_generate] No gateway token; cannot use subagent fallback", file=sys.stderr)
        return False

    work = Path(tempfile.mkdtemp(prefix="oc_image_"))
    run_file = work / "task.json"
    run_file.write_text(json.dumps({
        "kind": "agentTurn",
        "message": f"Generate an image with the image_generate tool. Prompt: {prompt}. Save to {output_path}.",
        "model": model,
        "toolsAllow": ["image_generate"],
        "timeoutSeconds": 300,
    }))

    cmd = [
        openclaw, "run", "--isolated", "--wait", str(run_file),
        "--output", str(work / "result.json"),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=320)
        if result.returncode == 0:
            # If the subagent saved the file, great. Otherwise inspect result.json.
            if output_path.exists() and output_path.stat().st_size > 0:
                print(f"[image_generate] Generated via isolated subagent: {output_path}")
                return True
        print(f"[image_generate] Subagent fallback failed: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"[image_generate] Subagent fallback exception: {e}", file=sys.stderr)
    finally:
        try:
            shutil.rmtree(work, ignore_errors=True)
        except Exception:
            pass

    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("output")
    parser.add_argument("--model", default="openai/gpt-image-2")
    parser.add_argument("--size", default="1536x1024")
    args = parser.parse_args()
    ok = call_image_generate(args.prompt, args.output, model=args.model, size=args.size)
    sys.exit(0 if ok else 1)
