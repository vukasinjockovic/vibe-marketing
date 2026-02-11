#!/usr/bin/env python3
"""Scan Convex activities for focus-group-related discoveries.

Usage:
    python scan_recent_mentions.py <project_id> [--days N] [--focus-groups fg1,fg2,...]

Reads activities from Convex via subprocess call to npx, then filters for
activities mentioning focus group names or enrichment-relevant keywords.

Output: JSON array of relevant activity summaries.
"""
import json
import subprocess
import sys
import argparse
from datetime import datetime, timedelta


ENRICHMENT_KEYWORDS = [
    "focus group",
    "audience",
    "awareness",
    "sophistication",
    "pain point",
    "objection",
    "belief",
    "language pattern",
    "emotional trigger",
    "buying behavior",
    "purchase",
    "competitor",
    "influence",
    "content preference",
]


def fetch_activities(project_id: str, convex_url: str = "http://localhost:3210") -> list[dict]:
    """Fetch recent activities for a project from Convex."""
    try:
        result = subprocess.run(
            [
                "npx", "convex", "run", "activities:listByProject",
                json.dumps({"projectId": project_id}),
                "--url", convex_url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"Warning: Failed to fetch activities: {result.stderr}", file=sys.stderr)
            return []
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Warning: Error fetching activities: {e}", file=sys.stderr)
        return []


def filter_relevant(
    activities: list[dict],
    focus_group_names: list[str] | None = None,
    days: int = 7,
) -> list[dict]:
    """Filter activities to those relevant to focus group enrichment.

    Args:
        activities: Raw activity list from Convex.
        focus_group_names: Optional list of focus group names to look for.
        days: Only include activities from the last N days.

    Returns:
        List of relevant activity summaries.
    """
    cutoff = (datetime.now() - timedelta(days=days)).timestamp() * 1000  # Convex uses ms
    relevant = []

    fg_names_lower = [n.lower() for n in (focus_group_names or [])]

    for activity in activities:
        # Skip old activities
        created = activity.get("_creationTime", 0)
        if created < cutoff:
            continue

        content = (activity.get("content") or "").lower()
        activity_type = (activity.get("type") or "").lower()
        agent = activity.get("agentName") or ""

        # Check for keyword matches
        matched_keywords = []
        for kw in ENRICHMENT_KEYWORDS:
            if kw in content:
                matched_keywords.append(kw)

        # Check for focus group name mentions
        matched_fg = []
        for fg_name in fg_names_lower:
            if fg_name in content:
                matched_fg.append(fg_name)

        if matched_keywords or matched_fg:
            relevant.append({
                "activityId": activity.get("_id"),
                "timestamp": created,
                "agentName": agent,
                "type": activity_type,
                "matchedKeywords": matched_keywords,
                "matchedFocusGroups": matched_fg,
                "contentSnippet": content[:200],
            })

    return relevant


def main():
    parser = argparse.ArgumentParser(description="Scan activities for focus group mentions")
    parser.add_argument("project_id", help="Convex project ID")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    parser.add_argument("--focus-groups", help="Comma-separated focus group names")
    parser.add_argument("--convex-url", default="http://localhost:3210", help="Convex URL")
    args = parser.parse_args()

    fg_names = args.focus_groups.split(",") if args.focus_groups else None

    activities = fetch_activities(args.project_id, args.convex_url)
    relevant = filter_relevant(activities, fg_names, args.days)

    print(json.dumps(relevant, indent=2))


if __name__ == "__main__":
    main()
