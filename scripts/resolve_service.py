#!/usr/bin/env python3
"""Resolve service chain for a capability.

Returns a JSON array of active services sorted by priority (fallback chain).
Supports campaign/batch-level overrides.

Usage:
  python scripts/resolve_service.py <capability_name>
  python scripts/resolve_service.py <capability_name> --campaign-id <id>
  python scripts/resolve_service.py <capability_name> --batch-id <id>

Examples:
  python scripts/resolve_service.py image_generation
  python scripts/resolve_service.py seo_keywords --campaign-id abc123
"""
import argparse
import json
import os
import subprocess
import sys


def run_convex(fn: str, args: dict) -> str:
    """Run a Convex function via CLI."""
    env = os.environ.copy()
    url = env.get("CONVEX_SELF_HOSTED_URL", "http://localhost:3210")

    cmd = ["npx", "convex", "run", fn, json.dumps(args), "--url", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error querying Convex: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Resolve service chain for a capability")
    parser.add_argument("capability", help="Capability/category name (e.g. image_generation)")
    parser.add_argument("--campaign-id", help="Campaign ID for override lookup")
    parser.add_argument("--batch-id", help="Content batch ID for override lookup")
    args = parser.parse_args()

    query_args: dict = {"categoryName": args.capability}

    if args.campaign_id or args.batch_id:
        fn = "services:resolveChainWithOverrides"
        if args.campaign_id:
            query_args["campaignId"] = args.campaign_id
        if args.batch_id:
            query_args["contentBatchId"] = args.batch_id
    else:
        fn = "services:resolveChain"

    result = run_convex(fn, query_args)

    if not result or result in ("null", "[]"):
        print(json.dumps({
            "error": f"No active services for capability: {args.capability}",
            "chain": [],
        }))
        sys.exit(1)

    chain = json.loads(result)
    if not isinstance(chain, list) or len(chain) == 0:
        print(json.dumps({
            "error": f"No active services for capability: {args.capability}",
            "chain": [],
        }))
        sys.exit(1)

    print(json.dumps(chain, indent=2))


if __name__ == "__main__":
    main()
