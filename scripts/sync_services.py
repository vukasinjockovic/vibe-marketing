#!/usr/bin/env python3
"""Sync service plugin manifests to Convex.

Reads services/*/manifest.json and upserts each capability to the Convex
services table. Preserves isActive, priority, apiKeyConfigured, apiKeyValue
(only updates metadata fields).

Usage: python scripts/sync_services.py
"""
import glob
import json
import os
import subprocess
import sys


def run_convex(fn: str, args: dict) -> str:
    """Run a Convex mutation/query via CLI."""
    env = os.environ.copy()
    url = env.get("CONVEX_SELF_HOSTED_URL", "http://localhost:3210")

    cmd = [
        "npx", "convex", "run", fn, json.dumps(args),
        "--url", url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return json.dumps({"error": result.stderr.strip()})
    return result.stdout.strip()


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "services")
    base_dir = os.path.abspath(base_dir)

    manifests = sorted(glob.glob(os.path.join(base_dir, "*/manifest.json")))
    if not manifests:
        print("No manifests found in services/*/manifest.json")
        sys.exit(1)

    print(f"Found {len(manifests)} manifests")

    created = 0
    updated = 0
    errors = []

    for path in manifests:
        folder = os.path.basename(os.path.dirname(path))
        if folder.startswith("_"):
            continue  # Skip template

        with open(path) as f:
            manifest = json.load(f)

        name = manifest["name"]
        caps = manifest.get("capabilities", [])
        if not caps:
            errors.append(f"{name}: no capabilities defined")
            continue

        for cap in caps:
            category_name = cap["category"]
            default_priority = cap.get("defaultPriority", 99)
            use_cases = cap.get("useCases", [])

            auth = manifest.get("auth", {})
            primary_env = auth.get("primaryEnvVar") or ""
            docs_url = auth.get("docsUrl")

            cost = manifest.get("costInfo", {})
            cost_summary = cost.get("summary", "") if isinstance(cost, dict) else str(cost)
            free_tier = cost.get("freeTier", False) if isinstance(cost, dict) else False

            mcp_config = manifest.get("mcp")
            mcp_server = mcp_config.get("serverName") if mcp_config else None

            self_hosted = manifest.get("selfHosted")
            self_hosted_config = None
            if self_hosted:
                self_hosted_config = {
                    "dockerCompose": self_hosted.get("dockerCompose"),
                    "healthCheckUrl": self_hosted.get("healthCheckUrl"),
                    "defaultPort": self_hosted.get("defaultPort"),
                }

            # Build service name — for multi-capability services, append category
            svc_name = name if len(caps) == 1 else f"{name}-{category_name}"

            args = {
                "categoryName": category_name,
                "name": svc_name,
                "displayName": manifest["displayName"],
                "description": manifest["description"],
                "scriptPath": manifest.get("scriptPath", f"services/{folder}/query.py"),
                "apiKeyEnvVar": primary_env,
                "costInfo": cost_summary,
                "useCases": use_cases,
                "defaultPriority": default_priority,
                "integrationType": manifest.get("integrationType", "script"),
                "freeTier": free_tier,
            }
            if mcp_server:
                args["mcpServer"] = mcp_server
            if docs_url:
                args["docsUrl"] = docs_url
            if manifest.get("version"):
                args["manifestVersion"] = manifest["version"]
            if self_hosted_config:
                args["selfHostedConfig"] = self_hosted_config

            result_str = run_convex("services:upsertFromManifest", args)
            try:
                result = json.loads(result_str)
                if "error" in result:
                    errors.append(f"{svc_name}: {result['error']}")
                elif result.get("action") == "created":
                    created += 1
                    print(f"  + {svc_name} ({category_name})")
                else:
                    updated += 1
                    print(f"  ~ {svc_name} ({category_name})")
            except json.JSONDecodeError:
                errors.append(f"{svc_name}: unexpected response: {result_str[:200]}")

    print(f"\nSynced {created + updated} services from {len(manifests) - 1} manifests.")
    print(f"  New: {created}, Updated: {updated}, Errors: {len(errors)}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ! {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
