#!/usr/bin/env python3
"""Quick connectivity test for Higgsfield AI service."""

import json
import os
import sys

def test():
    api_key = os.environ.get("HIGGSFIELD_API_KEY")
    secret = os.environ.get("HIGGSFIELD_SECRET")

    if not api_key or not secret:
        return {"status": "error", "message": "HIGGSFIELD_API_KEY and HIGGSFIELD_SECRET not set"}

    try:
        import higgsfield_client
    except ImportError:
        return {"status": "error", "message": "higgsfield-client not installed. Run: pip install higgsfield-client"}

    higgsfield_client.api_key = api_key
    higgsfield_client.api_secret = secret

    # Light check — attempt a minimal generation to verify credentials
    try:
        result = higgsfield_client.subscribe(
            "higgsfield/nano-banana-pro/text-to-image",
            arguments={"prompt": "a single red dot on white background", "resolution": "2K", "aspect_ratio": "1:1"},
        )
        if isinstance(result, dict) and (result.get("images") or result.get("url") or result.get("output")):
            return {"status": "ok", "message": "Higgsfield API connected and generating"}
        return {"status": "warning", "message": "Connected but unexpected response format", "response": str(result)[:200]}
    except Exception as e:
        return {"status": "error", "message": f"API call failed: {e}"}


if __name__ == "__main__":
    result = test()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "ok" else 1)
