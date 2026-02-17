#!/usr/bin/env python3
"""Higgsfield AI image generation service.

Uses the official higgsfield-client SDK.
Install: pip install higgsfield-client

Env vars required (pick one):
  HF_KEY              — combined "api_key:api_secret" format
  HF_API_KEY          — API key from https://cloud.higgsfield.ai/
  HF_API_SECRET       — API secret from https://cloud.higgsfield.ai/
"""

import json
import os
import sys
import urllib.request

try:
    import higgsfield_client
except ImportError:
    print(json.dumps({"error": "higgsfield-client not installed. Run: pip install higgsfield-client"}))
    sys.exit(1)

# ── Defaults ──────────────────────────────────────────────
DEFAULT_MODEL = "higgsfield/nano-banana-pro/text-to-image"
DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT_RATIO = "1:1"

MODELS = {
    "nano-banana-pro": "higgsfield/nano-banana-pro/text-to-image",
    "soul": "higgsfield/soul/image-to-image",
    "seedream-4": "bytedance/seedream/v4/text-to-image",
    "flux-kontext-max": "flux-pro/kontext/max/text-to-image",
}


def generate(
    prompt: str,
    model: str = "nano-banana-pro",
    resolution: str = DEFAULT_RESOLUTION,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    output_path: str | None = None,
) -> dict:
    """Generate an image via Higgsfield API.

    Args:
        prompt: Text description of the image.
        model: Model key (nano-banana-pro, soul, seedream-4, flux-kontext-max).
        resolution: "2K" or "4K".
        aspect_ratio: e.g. "1:1", "16:9", "9:16", "2:3".
        output_path: If set, download the image to this path.

    Returns:
        dict with image_url, model, and metadata.
    """
    # Support both combined HF_KEY="key:secret" and separate vars
    hf_key = os.environ.get("HF_KEY", "")
    if ":" in hf_key:
        api_key, secret = hf_key.split(":", 1)
    else:
        api_key = os.environ.get("HF_API_KEY", "")
        secret = os.environ.get("HF_API_SECRET", "")

    if not api_key or not secret:
        return {"error": "Set HF_KEY='key:secret' or both HF_API_KEY and HF_API_SECRET"}

    endpoint = MODELS.get(model, DEFAULT_MODEL)

    higgsfield_client.api_key = api_key
    higgsfield_client.api_secret = secret

    arguments = {
        "prompt": prompt,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
    }

    try:
        result = higgsfield_client.subscribe(endpoint, arguments=arguments)
    except Exception as e:
        return {"error": f"Higgsfield API call failed: {e}"}

    # Extract image URL from result
    image_url = None
    if isinstance(result, dict):
        images = result.get("images") or result.get("output") or []
        if isinstance(images, list) and len(images) > 0:
            first = images[0]
            image_url = first.get("url") if isinstance(first, dict) else first
        elif result.get("url"):
            image_url = result["url"]
        elif result.get("image_url"):
            image_url = result["image_url"]

    if not image_url:
        return {"error": "No image URL in response", "raw_response": str(result)[:500]}

    # Download if output path specified
    if output_path and image_url:
        try:
            urllib.request.urlretrieve(image_url, output_path)
        except Exception as e:
            return {"error": f"Image downloaded failed: {e}", "image_url": image_url}

    return {
        "image_url": image_url,
        "model": model,
        "endpoint": endpoint,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "output_path": output_path,
    }


def main():
    """CLI entrypoint: echo '{"prompt":"..."}' | python generate.py"""
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        params = json.loads(raw)
    except json.JSONDecodeError:
        params = {"prompt": raw}

    if "prompt" not in params:
        print(json.dumps({"error": "Missing 'prompt' parameter"}))
        sys.exit(1)

    result = generate(
        prompt=params["prompt"],
        model=params.get("model", "nano-banana-pro"),
        resolution=params.get("resolution", DEFAULT_RESOLUTION),
        aspect_ratio=params.get("aspect_ratio", DEFAULT_ASPECT_RATIO),
        output_path=params.get("output_path"),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
