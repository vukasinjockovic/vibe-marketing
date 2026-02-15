#!/usr/bin/env python3
"""Google Trends research tool for the vibe-marketing platform.

Usage:
    python google_trends.py --keywords "grandparent gift" "wedding planner" \
        --timeframe "today 12-m" --geo "US" --output json

Pulls interest over time, related queries, related topics, regional interest,
and computes seasonal peaks from Google Trends. Free, no API key required.
Uses the pytrends library (unofficial Google Trends API).

Returns JSON or markdown to stdout. Agents capture the output.
"""

import argparse
import json
import sys
import time
from datetime import datetime

try:
    from pytrends.request import TrendReq
except ImportError:
    print(
        "ERROR: pytrends is not installed.\n"
        "Install it with: pip install pytrends\n"
        "This is a free library -- no API key required.",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print(
        "ERROR: pandas is not installed.\n"
        "Install it with: pip install pandas",
        file=sys.stderr,
    )
    sys.exit(1)


# Delay between API calls to avoid rate limiting (seconds)
REQUEST_DELAY = 2.0

# Month names for seasonal peak detection
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def create_pytrends_client():
    """Create a TrendReq client with sensible defaults."""
    try:
        client = TrendReq(hl="en-US", tz=360, timeout=(10, 30))
        return client
    except Exception as e:
        print(f"ERROR: Failed to create pytrends client: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_interest_over_time(client, keywords, timeframe, geo, category):
    """Fetch interest-over-time data for the given keywords.

    Returns a dict mapping keyword -> list of {date, value} dicts.
    """
    result = {}
    for kw in keywords:
        result[kw] = []

    try:
        client.build_payload(keywords, cat=category, timeframe=timeframe, geo=geo)
        df = client.interest_over_time()

        if df.empty:
            print("WARNING: interest_over_time returned empty data.", file=sys.stderr)
            return result

        # Drop the isPartial column if present
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])

        for kw in keywords:
            if kw in df.columns:
                series = df[kw]
                entries = []
                for date_idx, value in series.items():
                    entries.append({
                        "date": date_idx.strftime("%Y-%m-%d"),
                        "value": int(value),
                    })
                result[kw] = entries

    except Exception as e:
        print(f"WARNING: interest_over_time failed: {e}", file=sys.stderr)

    return result


def fetch_related_queries(client, keywords, timeframe, geo, category):
    """Fetch related queries (rising and top) for each keyword.

    Returns a dict mapping keyword -> {rising: [...], top: [...]}.
    """
    result = {}
    for kw in keywords:
        result[kw] = {"rising": [], "top": []}

    try:
        # Payload should already be built from interest_over_time,
        # but rebuild to be safe
        client.build_payload(keywords, cat=category, timeframe=timeframe, geo=geo)
        related = client.related_queries()

        for kw in keywords:
            if kw not in related:
                continue

            kw_data = related[kw]

            # Rising queries
            if kw_data.get("rising") is not None and not kw_data["rising"].empty:
                df_rising = kw_data["rising"]
                for _, row in df_rising.iterrows():
                    query_text = str(row.get("query", ""))
                    value = row.get("value", 0)
                    if query_text:
                        result[kw]["rising"].append({
                            "query": query_text,
                            "value": str(value),
                        })

            # Top queries
            if kw_data.get("top") is not None and not kw_data["top"].empty:
                df_top = kw_data["top"]
                for _, row in df_top.iterrows():
                    query_text = str(row.get("query", ""))
                    value = row.get("value", 0)
                    if query_text:
                        result[kw]["top"].append({
                            "query": query_text,
                            "value": int(value),
                        })

    except Exception as e:
        print(f"WARNING: related_queries failed: {e}", file=sys.stderr)

    return result


def fetch_related_topics(client, keywords, timeframe, geo, category):
    """Fetch related topics (rising and top) for each keyword.

    Returns a dict mapping keyword -> {rising: [...], top: [...]}.
    """
    result = {}
    for kw in keywords:
        result[kw] = {"rising": [], "top": []}

    try:
        client.build_payload(keywords, cat=category, timeframe=timeframe, geo=geo)
        topics = client.related_topics()

        for kw in keywords:
            if kw not in topics:
                continue

            kw_data = topics[kw]

            # Rising topics
            if kw_data.get("rising") is not None and not kw_data["rising"].empty:
                df_rising = kw_data["rising"]
                for _, row in df_rising.iterrows():
                    topic_title = str(row.get("topic_title", ""))
                    topic_type = str(row.get("topic_type", ""))
                    value = row.get("value", 0)
                    if topic_title:
                        result[kw]["rising"].append({
                            "topic": topic_title,
                            "type": topic_type,
                            "value": str(value),
                        })

            # Top topics
            if kw_data.get("top") is not None and not kw_data["top"].empty:
                df_top = kw_data["top"]
                for _, row in df_top.iterrows():
                    topic_title = str(row.get("topic_title", ""))
                    topic_type = str(row.get("topic_type", ""))
                    value = row.get("value", 0)
                    if topic_title:
                        result[kw]["top"].append({
                            "topic": topic_title,
                            "type": topic_type,
                            "value": int(value),
                        })

    except Exception as e:
        print(f"WARNING: related_topics failed: {e}", file=sys.stderr)

    return result


def fetch_interest_by_region(client, keywords, timeframe, geo, category):
    """Fetch interest by region (US states or country sub-regions).

    Returns a dict mapping keyword -> list of {state, value} dicts.
    """
    result = {}
    for kw in keywords:
        result[kw] = []

    try:
        client.build_payload(keywords, cat=category, timeframe=timeframe, geo=geo)
        df = client.interest_by_region(resolution="REGION", inc_low_vol=True, inc_geo_code=False)

        if df.empty:
            print("WARNING: interest_by_region returned empty data.", file=sys.stderr)
            return result

        for kw in keywords:
            if kw in df.columns:
                series = df[kw].sort_values(ascending=False)
                entries = []
                for region_name, value in series.items():
                    val = int(value)
                    if val > 0:
                        entries.append({
                            "state": str(region_name),
                            "value": val,
                        })
                result[kw] = entries

    except Exception as e:
        print(f"WARNING: interest_by_region failed: {e}", file=sys.stderr)

    return result


def compute_seasonal_peaks(interest_over_time):
    """Compute seasonal peaks from interest-over-time data.

    A month is considered a peak if its average interest is above
    the overall average for that keyword.

    Returns a dict mapping keyword -> list of month names.
    """
    result = {}

    for kw, entries in interest_over_time.items():
        if not entries:
            result[kw] = []
            continue

        # Group values by month
        month_values = {}
        for entry in entries:
            try:
                date = datetime.strptime(entry["date"], "%Y-%m-%d")
                month = date.month
                if month not in month_values:
                    month_values[month] = []
                month_values[month].append(entry["value"])
            except (ValueError, KeyError):
                continue

        if not month_values:
            result[kw] = []
            continue

        # Compute average per month
        month_averages = {}
        for month, values in month_values.items():
            month_averages[month] = sum(values) / len(values)

        # Compute overall average
        all_values = []
        for values in month_values.values():
            all_values.extend(values)
        overall_avg = sum(all_values) / len(all_values) if all_values else 0

        # Find months above average
        peak_months = []
        for month in sorted(month_averages.keys()):
            if month_averages[month] > overall_avg:
                peak_months.append(MONTH_NAMES[month - 1])

        result[kw] = peak_months

    return result


def format_as_markdown(data):
    """Format the research data as a human-readable markdown report."""
    lines = []
    lines.append(f"# Google Trends Research Report")
    lines.append(f"")
    lines.append(f"**Generated:** {data['timestamp']}")
    lines.append(f"**Keywords:** {', '.join(data['keywords'])}")
    lines.append(f"**Timeframe:** {data['timeframe']}")
    lines.append(f"**Region:** {data['geo']}")
    lines.append(f"")

    # Interest Over Time Summary
    lines.append(f"## Interest Over Time")
    lines.append(f"")
    for kw in data["keywords"]:
        entries = data["interest_over_time"].get(kw, [])
        if entries:
            values = [e["value"] for e in entries]
            avg_val = sum(values) / len(values)
            max_val = max(values)
            min_val = min(values)
            latest = entries[-1]["value"] if entries else 0
            lines.append(f"### {kw}")
            lines.append(f"- **Data points:** {len(entries)}")
            lines.append(f"- **Average interest:** {avg_val:.1f}")
            lines.append(f"- **Peak interest:** {max_val}")
            lines.append(f"- **Lowest interest:** {min_val}")
            lines.append(f"- **Latest value:** {latest}")
            lines.append(f"")
        else:
            lines.append(f"### {kw}")
            lines.append(f"- No data available")
            lines.append(f"")

    # Seasonal Peaks
    lines.append(f"## Seasonal Peaks")
    lines.append(f"")
    for kw in data["keywords"]:
        peaks = data["seasonal_peaks"].get(kw, [])
        if peaks:
            lines.append(f"- **{kw}:** {', '.join(peaks)}")
        else:
            lines.append(f"- **{kw}:** No clear seasonal peaks")
    lines.append(f"")

    # Related Queries
    lines.append(f"## Related Queries")
    lines.append(f"")
    for kw in data["keywords"]:
        queries = data["related_queries"].get(kw, {"rising": [], "top": []})
        lines.append(f"### {kw}")
        lines.append(f"")

        if queries["rising"]:
            lines.append(f"**Rising queries** (gaining popularity):")
            for q in queries["rising"][:10]:
                lines.append(f"- {q['query']} ({q['value']})")
            lines.append(f"")

        if queries["top"]:
            lines.append(f"**Top queries** (most searched):")
            for q in queries["top"][:10]:
                lines.append(f"- {q['query']} ({q['value']})")
            lines.append(f"")

        if not queries["rising"] and not queries["top"]:
            lines.append(f"- No related queries found")
            lines.append(f"")

    # Related Topics
    lines.append(f"## Related Topics")
    lines.append(f"")
    for kw in data["keywords"]:
        topics = data["related_topics"].get(kw, {"rising": [], "top": []})
        lines.append(f"### {kw}")
        lines.append(f"")

        if topics["rising"]:
            lines.append(f"**Rising topics:**")
            for t in topics["rising"][:10]:
                lines.append(f"- {t['topic']} ({t['type']}) - {t['value']}")
            lines.append(f"")

        if topics["top"]:
            lines.append(f"**Top topics:**")
            for t in topics["top"][:10]:
                lines.append(f"- {t['topic']} ({t['type']}) - {t['value']}")
            lines.append(f"")

        if not topics["rising"] and not topics["top"]:
            lines.append(f"- No related topics found")
            lines.append(f"")

    # Regional Interest
    lines.append(f"## Regional Interest (Top 15)")
    lines.append(f"")
    for kw in data["keywords"]:
        regions = data["interest_by_region"].get(kw, [])
        lines.append(f"### {kw}")
        lines.append(f"")
        if regions:
            for r in regions[:15]:
                lines.append(f"- {r['state']}: {r['value']}")
        else:
            lines.append(f"- No regional data available")
        lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Google Trends research tool for vibe-marketing platform. "
        "Pulls keyword trends, related queries, regional interest, and seasonal peaks."
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        required=True,
        help="1-5 keywords to research (e.g., 'grandparent gift' 'wedding planner')",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="today 12-m",
        help="Pytrends timeframe string (default: 'today 12-m'). "
        "Options: 'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y'",
    )
    parser.add_argument(
        "--geo",
        type=str,
        default="US",
        help="Geographic region (default: 'US'). Use '' for worldwide.",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="Output format: 'json' (structured) or 'markdown' (human-readable report)",
    )
    parser.add_argument(
        "--category",
        type=int,
        default=0,
        help="Google Trends category ID (default: 0 = all categories)",
    )

    args = parser.parse_args()

    # Validate keyword count
    if len(args.keywords) > 5:
        print(
            "ERROR: Google Trends supports a maximum of 5 keywords per query. "
            f"You provided {len(args.keywords)}.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Researching {len(args.keywords)} keyword(s): {', '.join(args.keywords)}",
        file=sys.stderr,
    )
    print(f"Timeframe: {args.timeframe} | Region: {args.geo}", file=sys.stderr)

    client = create_pytrends_client()

    # 1. Interest over time
    print("Fetching interest over time...", file=sys.stderr)
    interest_over_time = fetch_interest_over_time(
        client, args.keywords, args.timeframe, args.geo, args.category
    )
    time.sleep(REQUEST_DELAY)

    # 2. Related queries
    print("Fetching related queries...", file=sys.stderr)
    related_queries = fetch_related_queries(
        client, args.keywords, args.timeframe, args.geo, args.category
    )
    time.sleep(REQUEST_DELAY)

    # 3. Related topics
    print("Fetching related topics...", file=sys.stderr)
    related_topics = fetch_related_topics(
        client, args.keywords, args.timeframe, args.geo, args.category
    )
    time.sleep(REQUEST_DELAY)

    # 4. Interest by region
    print("Fetching interest by region...", file=sys.stderr)
    interest_by_region = fetch_interest_by_region(
        client, args.keywords, args.timeframe, args.geo, args.category
    )

    # 5. Compute seasonal peaks from interest over time
    print("Computing seasonal peaks...", file=sys.stderr)
    seasonal_peaks = compute_seasonal_peaks(interest_over_time)

    # Assemble output
    data = {
        "keywords": args.keywords,
        "timeframe": args.timeframe,
        "geo": args.geo,
        "timestamp": datetime.now(tz=__import__('datetime').timezone.utc).isoformat(),
        "interest_over_time": interest_over_time,
        "related_queries": related_queries,
        "related_topics": related_topics,
        "interest_by_region": interest_by_region,
        "seasonal_peaks": seasonal_peaks,
    }

    if args.output == "json":
        print(json.dumps(data, indent=2))
    elif args.output == "markdown":
        print(format_as_markdown(data))

    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
