#!/usr/bin/env python3
"""Analyze Pinterest boards for theme and audience research via Playwright.

Usage:
    python pinterest_boards.py --url "https://www.pinterest.com/username/boardname/" \
        --max-pins 30 --output json

    python pinterest_boards.py --search "wedding planning boards" \
        --max-boards 5 --output json

Extracts board metadata (name, description, pin count, followers, creator),
top pins with descriptions, and identifies themes/categories.

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
import urllib.parse
from collections import Counter
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

# Stopwords to exclude from theme extraction
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "that", "this", "was", "are",
    "be", "has", "had", "have", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "i", "you", "he", "she",
    "we", "they", "my", "your", "his", "her", "our", "their", "me",
    "him", "us", "them", "not", "no", "so", "if", "up", "out", "about",
    "just", "get", "been", "being", "as", "its", "than", "who", "what",
    "how", "when", "where", "which", "why", "all", "each", "every",
    "both", "few", "more", "most", "other", "some", "such", "only",
    "same", "very", "s", "t", "d", "m", "re", "ve", "ll", "don",
    "pin", "pins", "board", "boards", "pinterest", "ideas", "idea",
}


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


def extract_board_info(page):
    """Extract board metadata from a board page.

    Args:
        page: Playwright page object currently on a board URL.

    Returns:
        Dict with board name, description, pin_count_text,
        follower_count_text, and creator.
    """
    info = {
        "name": "",
        "description": "",
        "pin_count_text": "",
        "follower_count_text": "",
        "creator": "",
    }

    try:
        # Board name
        name_el = page.query_selector(
            'h1, [data-test-id="board-header"] h1'
        )
        if name_el:
            info["name"] = name_el.inner_text().strip()

        # Description
        desc_el = page.query_selector(
            '[data-test-id="board-description"], meta[name="description"]'
        )
        if desc_el:
            text = desc_el.inner_text().strip() if hasattr(desc_el, 'inner_text') else ""
            if not text:
                text = desc_el.get_attribute("content") or ""
            info["description"] = text.strip()

        # Pin count
        pin_count_el = page.query_selector(
            '[data-test-id="board-pin-count"], [data-test-id="pin-count"]'
        )
        if pin_count_el:
            info["pin_count_text"] = pin_count_el.inner_text().strip()

        # Follower count
        follower_el = page.query_selector(
            '[data-test-id="board-follower-count"]'
        )
        if follower_el:
            info["follower_count_text"] = follower_el.inner_text().strip()

        # Creator
        creator_el = page.query_selector(
            '[data-test-id="board-creator"], [data-test-id="creator-name"]'
        )
        if creator_el:
            info["creator"] = creator_el.inner_text().strip()

    except Exception as e:
        print(f"[board_info] Error extracting board info: {e}", file=sys.stderr)

    return info


def extract_board_pins(page, max_pins=30):
    """Extract pins from a board page.

    Args:
        page: Playwright page on a board URL.
        max_pins: Max pins to extract.

    Returns:
        List of pin dicts with description, pin_url, image_url.
    """
    pins = []

    try:
        # Scroll to load more pins
        for i in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(2, 3))

        # Find pin elements
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
                break

        for el in pin_elements[:max_pins]:
            pin = {"description": "", "pin_url": "", "image_url": ""}

            try:
                # Description
                desc_el = el.query_selector('[data-test-id="pinDescription"], [title], img[alt]')
                if desc_el:
                    text = desc_el.inner_text().strip() if hasattr(desc_el, 'inner_text') else ""
                    if not text:
                        text = desc_el.get_attribute("alt") or ""
                    pin["description"] = text

                # Pin URL
                link_el = el.query_selector('a[href*="/pin/"]')
                if link_el:
                    href = link_el.get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            pin["pin_url"] = f"{PINTEREST_BASE}{href}"
                        else:
                            pin["pin_url"] = href

                # Image
                img_el = el.query_selector("img[src]")
                if img_el:
                    pin["image_url"] = img_el.get_attribute("src") or ""

            except Exception as e:
                print(f"[board_pins] Error extracting pin: {e}", file=sys.stderr)

            if pin["description"] or pin["pin_url"]:
                pins.append(pin)

    except Exception as e:
        print(f"[board_pins] Error extracting board pins: {e}", file=sys.stderr)

    return pins


def identify_themes(pins):
    """Identify recurring themes from pin descriptions.

    Counts non-stopword tokens across all pin descriptions and returns
    the most frequent ones.

    Args:
        pins: List of pin dicts, each with a 'description' key.

    Returns:
        List of dicts with 'word' and 'count' keys, sorted by count descending.
    """
    if not pins:
        return []

    word_counts = Counter()

    for pin in pins:
        desc = pin.get("description", "")
        if not desc:
            continue

        # Tokenize: lowercase, split on non-alpha
        words = re.findall(r"[a-z]+", desc.lower())
        for word in words:
            if word not in STOPWORDS and len(word) > 2:
                word_counts[word] += 1

    # Only keep words appearing 2+ times
    themes = [
        {"word": word, "count": count}
        for word, count in word_counts.most_common(20)
        if count >= 2
    ]

    return themes


def search_boards(query, max_boards=5):
    """Search Pinterest for boards matching a query.

    Args:
        query: Search query for boards.
        max_boards: Maximum boards to return.

    Returns:
        List of board URL strings.
    """
    from playwright.sync_api import sync_playwright

    board_urls = []
    encoded = urllib.parse.quote_plus(query)
    search_url = f"{PINTEREST_BASE}/search/boards/?q={encoded}"

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
            print(f"[search_boards] Navigating to: {search_url}", file=sys.stderr)
            page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            random_delay(3, 5)

            # Find board links
            board_links = page.query_selector_all('a[href*="/board/"], a[href$="/"]')
            seen = set()

            for link in board_links:
                if len(board_urls) >= max_boards:
                    break
                href = link.get_attribute("href")
                if href and "/pin/" not in href and href not in seen:
                    if href.startswith("/"):
                        href = f"{PINTEREST_BASE}{href}"
                    seen.add(href)
                    board_urls.append(href)

        except Exception as e:
            print(f"[search_boards] Error searching boards: {e}", file=sys.stderr)
        finally:
            browser.close()

    return board_urls


def format_board_results(boards, query):
    """Format board analysis results for output.

    Args:
        boards: List of board result dicts.
        query: The search query or URL used.

    Returns:
        Dict with query, timestamp, total_boards, and boards list.
    """
    return {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_boards": len(boards),
        "boards": boards,
    }


def format_as_markdown(data):
    """Convert JSON output to a readable markdown document."""
    lines = []
    lines.append(f"# Pinterest Board Analysis: {data.get('query', '')}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Total Boards:** {data.get('total_boards', 0)}")
    lines.append("")

    for i, board in enumerate(data.get("boards", []), 1):
        lines.append(f"---")
        lines.append(f"## Board {i}: {board.get('name', 'Unknown')}")
        lines.append("")
        if board.get("description"):
            lines.append(f"**Description:** {board['description']}")
        if board.get("url"):
            lines.append(f"**URL:** {board['url']}")
        if board.get("pin_count_text"):
            lines.append(f"**Pins:** {board['pin_count_text']}")
        if board.get("follower_count_text"):
            lines.append(f"**Followers:** {board['follower_count_text']}")
        if board.get("creator"):
            lines.append(f"**Creator:** {board['creator']}")
        lines.append("")

        if board.get("themes"):
            lines.append("### Themes")
            for theme in board["themes"]:
                lines.append(f"- **{theme['word']}** ({theme['count']} mentions)")
            lines.append("")

        if board.get("pins"):
            lines.append(f"### Sample Pins ({len(board['pins'])})")
            for j, pin in enumerate(board["pins"][:10], 1):
                if pin.get("description"):
                    lines.append(f"{j}. {pin['description']}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for pinterest_boards CLI."""
    parser = argparse.ArgumentParser(
        description="Analyze Pinterest boards for theme and audience research."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        type=str,
        help="Direct board URL to analyze",
    )
    group.add_argument(
        "--search",
        type=str,
        help="Search query for finding boards",
    )
    parser.add_argument(
        "--max-pins",
        type=int,
        default=30,
        help="Maximum pins to extract per board (default: 30)",
    )
    parser.add_argument(
        "--max-boards",
        type=int,
        default=5,
        help="Maximum boards when using --search (default: 5)",
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

def analyze_single_board(board_url, max_pins=30):
    """Analyze a single board URL and return structured data.

    Args:
        board_url: Full URL of the Pinterest board.
        max_pins: Max pins to extract.

    Returns:
        Dict with board metadata, pins, and themes.
    """
    from playwright.sync_api import sync_playwright

    result = {
        "name": "",
        "description": "",
        "url": board_url,
        "pin_count_text": "",
        "follower_count_text": "",
        "creator": "",
        "pins": [],
        "themes": [],
    }

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
            print(f"[board] Navigating to: {board_url}", file=sys.stderr)
            page.goto(board_url, wait_until="domcontentloaded", timeout=30000)
            random_delay(3, 5)

            # Extract board metadata
            info = extract_board_info(page)
            result["name"] = info["name"]
            result["description"] = info["description"]
            result["pin_count_text"] = info["pin_count_text"]
            result["follower_count_text"] = info["follower_count_text"]
            result["creator"] = info["creator"]

            # Extract pins
            pins = extract_board_pins(page, max_pins)
            result["pins"] = pins

            # Identify themes
            result["themes"] = identify_themes(pins)

            print(
                f"[board] Extracted {len(pins)} pins, {len(result['themes'])} themes",
                file=sys.stderr,
            )

        except Exception as e:
            print(f"[board] Error analyzing board: {e}", file=sys.stderr)
        finally:
            browser.close()

    return result


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    boards_data = []

    if args.url:
        # Analyze a single board by URL
        print(f"[main] Analyzing board: {args.url}", file=sys.stderr)
        board = analyze_single_board(args.url, args.max_pins)
        boards_data.append(board)
        query = args.url
    else:
        # Search for boards
        print(f"[main] Searching for boards: {args.search}", file=sys.stderr)
        board_urls = search_boards(args.search, args.max_boards)
        print(f"[main] Found {len(board_urls)} board URLs", file=sys.stderr)

        for url in board_urls:
            board = analyze_single_board(url, args.max_pins)
            boards_data.append(board)
            random_delay(2, 4)

        query = args.search

    output = format_board_results(boards_data, query)

    if args.output == "markdown":
        print(format_as_markdown(output))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. {len(boards_data)} boards analyzed.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
