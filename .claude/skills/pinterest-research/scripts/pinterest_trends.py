#!/usr/bin/env python3
"""Scrape Pinterest Trends page for trending topics and seasonal data.

Usage:
    python pinterest_trends.py --category "weddings" --output json
    python pinterest_trends.py --output json
    python pinterest_trends.py --category "home" --output markdown

Attempts Web Fetch (urllib) first; falls back to Playwright if needed.
Extracts trending searches, trending pins, and seasonal trends.

Requires (for Playwright fallback): pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PINTEREST_TRENDS_BASE = "https://trends.pinterest.com"

SUPPORTED_CATEGORIES = [
    "weddings",
    "home",
    "food",
    "diy",
    "fashion",
    "beauty",
    "travel",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_playwright():
    """Check if playwright is available."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


def random_delay(min_sec=2.0, max_sec=4.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def get_trends_url(category=None):
    """Build the Pinterest Trends URL for a given category.

    Args:
        category: One of the SUPPORTED_CATEGORIES, or None for general trends.

    Returns:
        Full URL string for the trends page.
    """
    if category and category.lower() in SUPPORTED_CATEGORIES:
        return f"{PINTEREST_TRENDS_BASE}/?category={category.lower()}"
    return f"{PINTEREST_TRENDS_BASE}/"


def parse_trend_item(element):
    """Parse a single trend item from a DOM element.

    Args:
        element: Playwright ElementHandle for a trend item.

    Returns:
        Dict with 'term' and optionally 'growth' keys.
    """
    result = {"term": "", "growth": ""}

    try:
        text = element.inner_text().strip()
        # The main text is the trend term; sometimes growth is nested
        # Split on newlines - first line is usually the term
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            result["term"] = lines[0]

        # Try to find growth indicator
        growth_el = element.query_selector(
            '[class*="growth"], [class*="change"], [data-test-id*="growth"], [data-test-id*="change"]'
        )
        if growth_el:
            growth_text = growth_el.inner_text().strip()
            if growth_text:
                result["growth"] = growth_text

    except Exception as e:
        print(f"[parse_trend] Error parsing trend item: {e}", file=sys.stderr)

    return result


def format_trends_results(category, trends):
    """Format trends data for output.

    Args:
        category: Category string or None.
        trends: List of trend dicts.

    Returns:
        Dict with category, timestamp, total_trends, and trends list.
    """
    return {
        "category": category if category else "general",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_trends": len(trends),
        "trends": trends,
    }


def format_as_markdown(data):
    """Convert JSON output to a readable markdown document."""
    lines = []
    cat = data.get("category", "general")
    lines.append(f"# Pinterest Trends: {cat.title()}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Category:** {cat}")
    lines.append(f"**Total Trends:** {data.get('total_trends', 0)}")
    lines.append("")

    if data.get("trends"):
        lines.append("## Trending Topics")
        lines.append("")
        for i, trend in enumerate(data["trends"], 1):
            growth = f" ({trend['growth']})" if trend.get("growth") else ""
            lines.append(f"{i}. **{trend['term']}**{growth}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scraping: urllib attempt first
# ---------------------------------------------------------------------------

def try_urllib_fetch(url):
    """Try to fetch trends page with urllib (no JS rendering).

    Returns HTML string or None if it fails or returns no useful data.
    """
    try:
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(url, headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
            # Check if page has meaningful content (not just a JS shell)
            if len(html) > 5000 and ("trend" in html.lower() or "search" in html.lower()):
                return html
            return None
    except Exception as e:
        print(f"[urllib] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def extract_trends_from_html(html):
    """Extract trend terms from raw HTML using regex patterns.

    This is a best-effort extraction for when urllib returns server-rendered content.

    Args:
        html: Raw HTML string.

    Returns:
        List of trend dicts, or empty list if nothing found.
    """
    trends = []

    # Look for JSON-LD or embedded data
    json_patterns = [
        r'"trendingSearches"\s*:\s*\[(.*?)\]',
        r'"trends"\s*:\s*\[(.*?)\]',
        r'"searchTerms"\s*:\s*\[(.*?)\]',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                # Try to parse as JSON array content
                raw = f"[{match.group(1)}]"
                items = json.loads(raw)
                for item in items:
                    if isinstance(item, str):
                        trends.append({"term": item, "growth": ""})
                    elif isinstance(item, dict):
                        term = item.get("term") or item.get("query") or item.get("name", "")
                        growth = item.get("growth") or item.get("change", "")
                        if term:
                            trends.append({"term": term, "growth": str(growth)})
            except (json.JSONDecodeError, TypeError):
                continue

    # Fallback: look for trend items in structured HTML
    if not trends:
        # Try to find trend terms in common patterns
        term_pattern = r'data-test-id="trend[^"]*"[^>]*>([^<]+)<'
        matches = re.findall(term_pattern, html)
        for m in matches:
            term = m.strip()
            if term and len(term) > 2:
                trends.append({"term": term, "growth": ""})

    return trends


# ---------------------------------------------------------------------------
# Scraping: Playwright fallback
# ---------------------------------------------------------------------------

def scrape_trends_playwright(url):
    """Scrape trends page using Playwright for full JS rendering.

    Args:
        url: Full trends URL.

    Returns:
        List of trend dicts.
    """
    from playwright.sync_api import sync_playwright

    trends = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
                "--disable-gpu",
                "--lang=en-US,en",
            ],
        )
        ua = random.choice(USER_AGENTS)
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        page = context.new_page()

        try:
            print(f"[playwright] Navigating to: {url}", file=sys.stderr)
            page.goto(url, wait_until="networkidle", timeout=30000)
            random_delay(3, 5)

            # Scroll to load content
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 2.5))

            # Try various selectors for trend items
            trend_selectors = [
                '[data-test-id*="trend"]',
                '[class*="trend"] [class*="title"]',
                '[class*="TrendCard"]',
                '[class*="trending"]',
                'li[class*="trend"]',
                'div[class*="trend"]',
            ]

            trend_elements = []
            for sel in trend_selectors:
                trend_elements = page.query_selector_all(sel)
                if trend_elements:
                    print(f"[playwright] Found {len(trend_elements)} trends with: {sel}", file=sys.stderr)
                    break

            for el in trend_elements:
                trend = parse_trend_item(el)
                if trend["term"]:
                    trends.append(trend)

            # If no structured trends found, try extracting from page text
            if not trends:
                html = page.content()
                trends = extract_trends_from_html(html)

        except Exception as e:
            print(f"[playwright] Error scraping trends: {e}", file=sys.stderr)
        finally:
            browser.close()

    return trends


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for pinterest_trends CLI."""
    parser = argparse.ArgumentParser(
        description="Scrape Pinterest Trends for trending topics and seasonal data."
    )
    parser.add_argument(
        "--category",
        type=str,
        default="",
        help=f"Trend category: {', '.join(SUPPORTED_CATEGORIES)} (default: general/all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help='Output format: "json" or "markdown" (default: "json")',
    )
    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = create_parser()
    args = parser.parse_args()

    category = args.category if args.category else None
    url = get_trends_url(category)

    print(f"[main] Fetching Pinterest trends for: {category or 'general'}", file=sys.stderr)
    print(f"[main] URL: {url}", file=sys.stderr)

    # Strategy 1: Try urllib first (faster, no browser)
    print("[main] Trying urllib fetch first...", file=sys.stderr)
    html = try_urllib_fetch(url)
    trends = []

    if html:
        trends = extract_trends_from_html(html)
        if trends:
            print(f"[main] Extracted {len(trends)} trends via urllib", file=sys.stderr)

    # Strategy 2: Fall back to Playwright if urllib didn't work
    if not trends:
        print("[main] urllib returned no trends. Falling back to Playwright...", file=sys.stderr)
        if check_playwright():
            trends = scrape_trends_playwright(url)
        else:
            print(
                "ERROR: Could not extract trends via urllib, and playwright is not installed.\n"
                "Install playwright for full JS rendering:\n"
                "  pip install playwright && python -m playwright install chromium\n",
                file=sys.stderr,
            )
            sys.exit(1)

    output = format_trends_results(category, trends)

    if args.output == "markdown":
        print(format_as_markdown(output))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. {len(trends)} trends collected.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
