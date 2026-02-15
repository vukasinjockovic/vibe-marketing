#!/usr/bin/env python3
"""Search Pinterest for trending pins, visual content ideas, and engagement data.

Usage:
    python pinterest_search.py --query "grandparent gifts" --max-pins 20 --output json
    python pinterest_search.py --query "wedding centerpieces" --max-pins 50 --output markdown

Scrapes Pinterest search results via Playwright (no API key needed).
Extracts pin descriptions, engagement signals, image URLs, pinner info.

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
import urllib.parse
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

PINTEREST_BASE = "https://www.pinterest.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_playwright():
    """Check if playwright is available and provide install instructions if not."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        print(
            "ERROR: playwright is not installed.\n"
            "Install with:\n"
            "  pip install playwright && python -m playwright install chromium\n",
            file=sys.stderr,
        )
        return False


def random_delay(min_sec=2.0, max_sec=4.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def build_search_url(query):
    """Build a Pinterest search URL for the given query.

    Args:
        query: Search query string.

    Returns:
        Full Pinterest search URL.
    """
    encoded = urllib.parse.quote_plus(query)
    return f"{PINTEREST_BASE}/search/pins/?q={encoded}"


def parse_repin_count(text):
    """Parse repin/save count from text like '1.2k saves', '500 saves', '2.5M saves'.

    Args:
        text: Raw text containing a count.

    Returns:
        Integer count. Returns 0 if text is empty or unparseable.
    """
    if not text:
        return 0

    text = text.strip().lower()

    # Match patterns like "1.2k", "500", "2.5m"
    match = re.search(r"([\d,.]+)\s*([kmb]?)", text)
    if not match:
        return 0

    num_str = match.group(1).replace(",", "")
    multiplier_char = match.group(2)

    try:
        num = float(num_str)
    except ValueError:
        return 0

    multipliers = {"k": 1000, "m": 1000000, "b": 1000000000}
    multiplier = multipliers.get(multiplier_char, 1)

    return int(num * multiplier)


def parse_pin_element(element):
    """Extract pin data from a Playwright DOM element.

    Args:
        element: A Playwright ElementHandle representing a pin card.

    Returns:
        Dict with pin data: description, pin_url, image_url, repin_count,
        pinner_name, board_name.
    """
    pin = {
        "description": "",
        "pin_url": "",
        "image_url": "",
        "repin_count": 0,
        "pinner_name": "",
        "board_name": "",
    }

    try:
        # Description / title
        desc_el = element.query_selector(
            '[data-test-id="pinDescription"], [title]'
        )
        if desc_el:
            pin["description"] = desc_el.inner_text().strip()

        # Pin URL
        link_el = element.query_selector('a[href*="/pin/"]')
        if link_el:
            href = link_el.get_attribute("href")
            if href:
                if href.startswith("/"):
                    pin["pin_url"] = f"{PINTEREST_BASE}{href}"
                elif href.startswith("http"):
                    pin["pin_url"] = href
                else:
                    pin["pin_url"] = f"{PINTEREST_BASE}/{href}"

        # Image URL
        img_el = element.query_selector("img[src]")
        if img_el:
            src = img_el.get_attribute("src")
            if src:
                pin["image_url"] = src

        # Repin / save count
        repin_el = element.query_selector(
            '[data-test-id="pin-repin-count"], '
            '[aria-label*="repin"], '
            '[aria-label*="save"]'
        )
        if repin_el:
            repin_text = repin_el.inner_text().strip()
            pin["repin_count"] = parse_repin_count(repin_text)

        # Pinner name
        pinner_el = element.query_selector('[data-test-id="pinner-name"]')
        if pinner_el:
            pin["pinner_name"] = pinner_el.inner_text().strip()

        # Board name (sometimes present)
        board_el = element.query_selector('[data-test-id="board-name"]')
        if board_el:
            pin["board_name"] = board_el.inner_text().strip()

    except Exception as e:
        print(f"[parse_pin] Error extracting pin data: {e}", file=sys.stderr)

    return pin


def format_results(query, pins):
    """Format extracted pins into the final output structure.

    Sorts pins by repin count (descending) when available.

    Args:
        query: The original search query.
        pins: List of pin dicts.

    Returns:
        Dict with query, timestamp, total_pins, and sorted pins list.
    """
    # Sort by repin count descending
    sorted_pins = sorted(pins, key=lambda p: p.get("repin_count", 0), reverse=True)

    return {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_pins": len(sorted_pins),
        "pins": sorted_pins,
    }


def format_as_markdown(data):
    """Convert JSON output to a readable markdown document."""
    lines = []
    lines.append(f"# Pinterest Search: {data.get('query', '')}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Total Pins:** {data.get('total_pins', 0)}")
    lines.append("")

    for i, pin in enumerate(data.get("pins", []), 1):
        lines.append(f"---")
        lines.append(f"### Pin {i}")
        lines.append("")
        if pin.get("description"):
            lines.append(f"**Description:** {pin['description']}")
        if pin.get("pin_url"):
            lines.append(f"**URL:** {pin['pin_url']}")
        if pin.get("image_url"):
            lines.append(f"**Image:** {pin['image_url']}")
        if pin.get("repin_count"):
            lines.append(f"**Saves:** {pin['repin_count']:,}")
        if pin.get("pinner_name"):
            lines.append(f"**Pinner:** {pin['pinner_name']}")
        if pin.get("board_name"):
            lines.append(f"**Board:** {pin['board_name']}")
        lines.append("")

    return "\n".join(lines)


def _is_blocked(page):
    """Detect if Pinterest is blocking or showing a wall."""
    try:
        content = page.content().lower()
        block_indicators = [
            "something went wrong",
            "blocked",
            "unusual traffic",
            "captcha",
            "please verify",
        ]
        return any(ind in content for ind in block_indicators)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for pinterest_search CLI."""
    parser = argparse.ArgumentParser(
        description="Search Pinterest for pins via Playwright. "
                    "Extracts descriptions, engagement data, and image URLs."
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Pinterest search query (e.g., 'grandparent gifts')",
    )
    parser.add_argument(
        "--max-pins",
        type=int,
        default=20,
        help="Maximum number of pins to extract (default: 20)",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help='Output format: "json" or "markdown" (default: "json")',
    )
    parser.add_argument(
        "--scroll-count",
        type=int,
        default=5,
        help="Number of times to scroll down for infinite scroll (default: 5)",
    )
    return parser


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_pins(query, max_pins=20, scroll_count=5):
    """Scrape Pinterest search results for the given query.

    Args:
        query: Search query string.
        max_pins: Maximum number of pins to collect.
        scroll_count: Number of scroll-down actions for infinite scroll.

    Returns:
        List of pin dicts.
    """
    from playwright.sync_api import sync_playwright

    pins = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--disable-extensions",
                "--disable-gpu",
                "--lang=en-US,en",
            ],
        )
        ua = random.choice(USER_AGENTS)
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Stealth: override navigator properties
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
        """)

        page = context.new_page()

        try:
            search_url = build_search_url(query)
            print(f"[search] Navigating to: {search_url}", file=sys.stderr)

            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            random_delay(3, 5)

            if _is_blocked(page):
                print("[search] Pinterest appears to be blocking. Aborting.", file=sys.stderr)
                browser.close()
                return pins

            # Infinite scroll to load more pins
            for i in range(scroll_count):
                if len(pins) >= max_pins:
                    break
                print(f"[search] Scrolling ({i + 1}/{scroll_count})...", file=sys.stderr)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                random_delay(2, 4)

            # Extract pin elements
            # Pinterest uses various selectors for pin containers
            pin_selectors = [
                '[data-test-id="pin"]',
                '[data-test-id="pinWrapper"]',
                '[role="listitem"]',
                'div[data-grid-item="true"]',
            ]

            pin_elements = []
            for sel in pin_selectors:
                pin_elements = page.query_selector_all(sel)
                if pin_elements:
                    print(f"[search] Found {len(pin_elements)} pins with selector: {sel}", file=sys.stderr)
                    break

            if not pin_elements:
                print("[search] No pins found with known selectors. Trying fallback...", file=sys.stderr)
                # Fallback: look for any elements containing pin links
                pin_elements = page.query_selector_all('a[href*="/pin/"]')
                pin_elements = [el.evaluate_handle("el => el.closest('div[class]')") for el in pin_elements]
                pin_elements = [el for el in pin_elements if el]

            print(f"[search] Extracting data from {min(len(pin_elements), max_pins)} pins...", file=sys.stderr)

            for el in pin_elements[:max_pins]:
                pin = parse_pin_element(el)
                if pin.get("description") or pin.get("pin_url") or pin.get("image_url"):
                    pins.append(pin)

        except Exception as e:
            print(f"[search] Error during scraping: {e}", file=sys.stderr)
        finally:
            browser.close()

    return pins


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    print(f"[main] Searching Pinterest for: {args.query}", file=sys.stderr)
    print(f"[main] Max pins: {args.max_pins}", file=sys.stderr)

    pins = scrape_pins(
        query=args.query,
        max_pins=args.max_pins,
        scroll_count=args.scroll_count,
    )

    output = format_results(args.query, pins)

    if args.output == "markdown":
        print(format_as_markdown(output))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. {len(pins)} pins collected.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
