#!/usr/bin/env python3
"""Resolve the best available service for a capability.

Usage: python scripts/resolve_service.py <capability_name>
Example: python scripts/resolve_service.py seo_keywords

Returns JSON with the service config, or exits 1 if none available.
"""
import json
import subprocess
import sys
import os


def run_convex(fn: str, args: dict) -> str:
    """Run a Convex function via CLI."""
    env = os.environ.copy()
    url = env.get("CONVEX_SELF_HOSTED_URL", "http://localhost:3210")
    key = env.get("CONVEX_SELF_HOSTED_ADMIN_KEY", "")

    cmd = [
        "npx", "convex", "run", fn, json.dumps(args),
        "--url", url, "--admin-key", key,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error querying Convex: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_service.py <capability_name>", file=sys.stderr)
        sys.exit(1)

    capability = sys.argv[1]
    result = run_convex("services:resolve", {"categoryName": capability})

    if not result or result == "null":
        print(json.dumps({"error": f"No active service found for capability: {capability}"}))
        sys.exit(1)

    # Parse and output the service config
    service = json.loads(result)
    print(json.dumps(service, indent=2))


if __name__ == "__main__":
    main()
