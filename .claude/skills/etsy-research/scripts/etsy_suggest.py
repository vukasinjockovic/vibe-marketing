#!/usr/bin/env python3
"""Etsy autocomplete suggestions for keyword discovery.

Usage:
    python etsy_suggest.py --seed-keywords "grandparent gift" --expand-alphabet --output json

Tries Etsy's AJAX autocomplete API first (fast, zero deps).
Falls back to Playwright browser automation if the API requires authentication.

Returns JSON with all discovered suggestions, grouped by expansion type.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ETSY_SUGGEST_URL = "https://www.etsy.com/api/v3/ajax/search/autocomplete"

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")


# ---------------------------------------------------------------------------
# Pure helper functions (testable without browser/network)
# ---------------------------------------------------------------------------

def build_suggest_url(query):
    """Build Etsy autocomplete API URL for a query."""
    encoded = urllib.parse.quote_plus(query)
    return f"{ETSY_SUGGEST_URL}?query={encoded}"


def dedupe_suggestions(suggestions):
    """Deduplicate suggestions case-insensitively, preserving first occurrence.

    Returns list of unique suggestions.
    """
    seen = set()
    unique = []
    for s in suggestions:
        key = s.lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def generate_alphabet_queries(seed):
    """Generate 26 queries: 'seed a', 'seed b', ... 'seed z'.

    Returns list of 26 query strings.
    """
    return [f"{seed} {letter}" for letter in ALPHABET]


# ---------------------------------------------------------------------------
# Fetch functions
# ---------------------------------------------------------------------------

def fetch_suggestions_api(query, max_retries=2):
    """Try to fetch suggestions from Etsy's AJAX autocomplete API.

    Returns (suggestions_list, success_bool).
    If the API requires auth or fails, returns ([], False).
    """
    url = build_suggest_url(query)

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://www.etsy.com/",
                "X-Requested-With": "XMLHttpRequest",
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                # Parse response - Etsy may return different formats
                if isinstance(data, list):
                    return data, True
                if isinstance(data, dict):
                    # Try common keys
                    results = (
                        data.get("results", [])
                        or data.get("suggestions", [])
                        or data.get("queries", [])
                        or data.get("items", [])
                    )
                    if results:
                        # Results might be strings or dicts with 'query' key
                        suggestions = []
                        for item in results:
                            if isinstance(item, str):
                                suggestions.append(item)
                            elif isinstance(item, dict):
                                suggestions.append(
                                    item.get("query", "")
                                    or item.get("text", "")
                                    or item.get("name", "")
                                )
                        return [s for s in suggestions if s], True
                return [], True  # API worked but no results
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                print(f"[api] Auth required ({e.code}). Will fall back to browser.", file=sys.stderr)
                return [], False
            if e.code == 429:
                wait = (2 ** attempt) * 1.0
                print(f"[api] Rate limited (429). Backing off {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"[api] HTTP error {e.code} for query '{query}'", file=sys.stderr)
            return [], False
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"[api] Error: {e}", file=sys.stderr)
            return [], False

    return [], False


def fetch_suggestions_browser(page, query):
    """Fetch suggestions by typing into Etsy's search box and reading dropdown.

    Returns list of suggestion strings.
    """
    suggestions = []

    try:
        # Type query into search box
        search_input = page.query_selector(
            'input[name="search_query"], input#search-query, '
            'input[type="search"], input[placeholder*="Search"]'
        )
        if not search_input:
            print(f"[browser] Could not find search input for '{query}'", file=sys.stderr)
            return suggestions

        # Clear and type
        search_input.click()
        time.sleep(0.5)
        search_input.fill("")
        time.sleep(0.3)

        # Type character by character for more natural behavior
        for char in query:
            search_input.type(char, delay=50)
        time.sleep(1.5)  # Wait for suggestions to appear

        # Extract suggestions from dropdown
        suggestion_selectors = [
            '[data-suggestion]',
            '.search-suggestions li',
            '.wt-menu__item',
            '[role="option"]',
            '.autosuggest li',
            'ul[role="listbox"] li',
        ]

        for selector in suggestion_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                for el in elements:
                    text = el.inner_text().strip()
                    if text and text.lower() != query.lower():
                        suggestions.append(text)
                break

        # Clear search box for next query
        search_input.fill("")
        time.sleep(0.3)

    except Exception as e:
        print(f"[browser] Error fetching suggestions for '{query}': {e}", file=sys.stderr)

    return suggestions


# ---------------------------------------------------------------------------
# Expansion logic
# ---------------------------------------------------------------------------

def expand_seed(seed, do_alphabet, fetch_fn, delay=0.3):
    """Expand a single seed keyword.

    Args:
        seed: the base keyword
        do_alphabet: if True, also query 'seed a' through 'seed z'
        fetch_fn: callable(query) -> list of suggestions
        delay: seconds between requests

    Returns dict with direct and alphabet_expansions.
    """
    result = {
        "direct": [],
        "alphabet_expansions": {},
    }

    # Direct suggestions
    print(f"[expand] Fetching: {seed}", file=sys.stderr)
    result["direct"] = fetch_fn(seed)
    time.sleep(delay)

    # Alphabet expansion
    if do_alphabet:
        print(f"[expand] Alphabet expanding '{seed}'...", file=sys.stderr)
        queries = generate_alphabet_queries(seed)
        for query in queries:
            letter = query[-1]
            print(f"[expand]   {query}", file=sys.stderr)
            suggestions = fetch_fn(query)
            if suggestions:
                result["alphabet_expansions"][letter] = suggestions
            time.sleep(delay)

    return result


def collect_all_suggestions(results):
    """Flatten all suggestions into a deduplicated list."""
    all_suggestions = []
    for seed, data in results.items():
        all_suggestions.extend(data.get("direct", []))
        for letter, suggestions in data.get("alphabet_expansions", {}).items():
            all_suggestions.extend(suggestions)
    return dedupe_suggestions(all_suggestions)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_as_markdown(output_data):
    """Convert output to markdown."""
    lines = []
    lines.append("# Etsy Suggest Research")
    lines.append("")
    lines.append(f"**Generated:** {output_data['timestamp']}")
    lines.append(f"**Seeds:** {', '.join(output_data['seed_keywords'])}")
    lines.append(f"**Total unique suggestions:** {output_data['total_suggestions']}")
    lines.append(f"**Method:** {output_data.get('method', 'unknown')}")
    lines.append("")

    for seed, data in output_data["results"].items():
        lines.append(f"## Seed: {seed}")
        lines.append("")

        if data["direct"]:
            lines.append("### Direct Suggestions")
            for s in data["direct"]:
                lines.append(f"- {s}")
            lines.append("")

        if data.get("alphabet_expansions"):
            lines.append("### Alphabet Expansions")
            for letter, suggestions in sorted(data["alphabet_expansions"].items()):
                lines.append(f"**{letter.upper()}:** {', '.join(suggestions)}")
            lines.append("")

    if output_data.get("all_unique_suggestions"):
        lines.append("## All Unique Suggestions")
        lines.append("")
        for s in output_data["all_unique_suggestions"]:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Etsy autocomplete suggestions for keyword discovery"
    )
    parser.add_argument(
        "--seed-keywords", nargs="+", required=True,
        help="Seed keywords to expand (e.g., 'grandparent gift' 'wedding planner')"
    )
    parser.add_argument(
        "--expand-alphabet", action="store_true",
        help="Query 'seed a', 'seed b', ... 'seed z' for long-tail discovery"
    )
    parser.add_argument(
        "--output", choices=["json", "markdown"], default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.3,
        help="Delay between requests in seconds (default: 0.3)"
    )
    parser.add_argument(
        "--force-browser", action="store_true",
        help="Skip API attempt and use Playwright browser directly"
    )

    args = parser.parse_args()

    if len(args.seed_keywords) > 10:
        print("Error: Maximum 10 seed keywords allowed.", file=sys.stderr)
        sys.exit(1)

    # Determine fetch method: try API first, fall back to browser
    use_browser = args.force_browser
    method = "browser" if use_browser else "api"

    if not use_browser:
        # Test API with first seed
        print("[main] Testing Etsy autocomplete API...", file=sys.stderr)
        test_results, api_works = fetch_suggestions_api(args.seed_keywords[0])
        if not api_works:
            print("[main] API requires auth. Falling back to Playwright browser.", file=sys.stderr)
            use_browser = True
            method = "browser_fallback"
        else:
            print(f"[main] API works. Got {len(test_results)} results for test query.", file=sys.stderr)
            method = "api"

    # Set up fetch function
    page = None
    browser = None
    context = None

    if use_browser:
        # Check playwright
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print(
                "ERROR: Playwright needed for browser fallback.\n"
                "Install with: pip install playwright && python -m playwright install chromium",
                file=sys.stderr,
            )
            sys.exit(1)

        import random

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]

        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        page = context.new_page()

        # Navigate to Etsy homepage
        print("[main] Loading Etsy homepage for browser mode...", file=sys.stderr)
        try:
            page.goto("https://www.etsy.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            # Dismiss cookie banner
            for selector in ['button:has-text("Accept")', 'button:has-text("Accept All")']:
                el = page.query_selector(selector)
                if el and el.is_visible():
                    el.click()
                    time.sleep(1)
                    break
        except Exception as e:
            print(f"[main] Homepage load error: {e}", file=sys.stderr)

        def fetch_fn(query):
            return fetch_suggestions_browser(page, query)
    else:
        def fetch_fn(query):
            results, _ = fetch_suggestions_api(query)
            return results

    try:
        # Expand each seed
        results = {}
        for seed in args.seed_keywords:
            seed = seed.strip()
            if not seed:
                continue
            results[seed] = expand_seed(
                seed,
                do_alphabet=args.expand_alphabet,
                fetch_fn=fetch_fn,
                delay=args.delay,
            )

        # Collect all unique suggestions
        all_unique = collect_all_suggestions(results)

        # Build output
        output_data = {
            "seed_keywords": args.seed_keywords,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "total_suggestions": len(all_unique),
            "results": results,
            "all_unique_suggestions": all_unique,
        }

        if args.output == "markdown":
            print(format_as_markdown(output_data))
        else:
            print(json.dumps(output_data, indent=2, ensure_ascii=False))

    finally:
        if browser:
            browser.close()


if __name__ == "__main__":
    main()
