#!/usr/bin/env python3
"""Search Etsy listings via Playwright and extract product data.

Usage:
    python etsy_search.py --query "grandparent memory book" --max-listings 20 --sort relevancy --output json

Returns JSON with listing data including titles, prices, ratings, badges,
and computed market metrics (average price, price range, % free shipping, etc.).

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
from datetime import datetime, timezone
from urllib.parse import quote_plus


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

SORT_OPTIONS = {
    "relevancy": "",
    "most_recent": "most_recent",
    "highest_price": "highest_price",
    "lowest_price": "lowest_price",
    "top_reviews": "top_reviews",
}


# ---------------------------------------------------------------------------
# Pure helper functions (testable without browser)
# ---------------------------------------------------------------------------

def parse_price(text):
    """Parse a price string into a float.

    Handles: "$24.99", "$1,299.00", "EUR 24.99", "$12.99 - $45.99", etc.
    Returns 0.0 for empty/None/unparseable input.
    """
    if not text:
        return 0.0
    text = str(text)
    # Find the first price-like pattern (digits with optional comma grouping and decimal)
    match = re.search(r"[\d,]+\.?\d*", text)
    if match:
        price_str = match.group().replace(",", "")
        try:
            return float(price_str)
        except ValueError:
            return 0.0
    return 0.0


def parse_rating(text):
    """Parse a star rating from text like '4.5 out of 5 stars' or just '4.8'.

    Returns 0.0 for empty/None/unparseable input.
    """
    if not text:
        return 0.0
    text = str(text)
    # Try "X out of 5" pattern first
    match = re.search(r"(\d+(?:\.\d+)?)\s+out\s+of\s+5", text)
    if match:
        return float(match.group(1))
    # Try standalone number
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return 0.0


def parse_review_count(text):
    """Parse review count from text like '1,234 reviews' or '(1,234)'.

    Returns 0 for empty/None/unparseable input.
    """
    if not text:
        return 0
    text = str(text)
    match = re.search(r"[\d,]+", text)
    if match:
        return int(match.group().replace(",", ""))
    return 0


def build_search_url(query, sort="relevancy"):
    """Build Etsy search URL with query and sort parameters."""
    encoded_query = quote_plus(query)
    base = f"https://www.etsy.com/search?q={encoded_query}"
    sort_value = SORT_OPTIONS.get(sort, "")
    if sort_value:
        base += f"&order={sort_value}"
    return base


def compute_search_metrics(listings):
    """Compute aggregate metrics from a list of listing dicts.

    Each listing should have: price (float), free_shipping (bool), bestseller (bool).
    Returns dict with: average_price, price_range, pct_free_shipping, pct_bestseller.
    """
    if not listings:
        return {
            "average_price": 0,
            "price_range": {"min": 0, "max": 0},
            "pct_free_shipping": 0,
            "pct_bestseller": 0,
        }

    prices = [l.get("price", 0) for l in listings]
    n = len(listings)

    avg_price = sum(prices) / n if n > 0 else 0
    free_shipping_count = sum(1 for l in listings if l.get("free_shipping", False))
    bestseller_count = sum(1 for l in listings if l.get("bestseller", False))

    return {
        "average_price": round(avg_price, 2),
        "price_range": {
            "min": min(prices),
            "max": max(prices),
        },
        "pct_free_shipping": round(free_shipping_count / n * 100, 2) if n > 0 else 0,
        "pct_bestseller": round(bestseller_count / n * 100, 2) if n > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def random_delay(min_sec=2.0, max_sec=4.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def dismiss_cookie_banner(page):
    """Try to dismiss Etsy's cookie consent banner if present."""
    try:
        # Etsy uses various cookie consent patterns
        selectors = [
            'button[data-gdpr-single-choice-accept="true"]',
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("Accept Cookies")',
            '[data-testid="cookie-banner-accept"]',
            '.cookie-consent button',
        ]
        for selector in selectors:
            el = page.query_selector(selector)
            if el and el.is_visible():
                el.click()
                print("[cookie] Dismissed cookie banner", file=sys.stderr)
                time.sleep(1)
                return True
    except Exception as e:
        print(f"[cookie] Could not dismiss banner: {e}", file=sys.stderr)
    return False


def _is_captcha(page):
    """Detect if the current page shows a CAPTCHA or bot detection."""
    try:
        content = page.content()
        captcha_indicators = [
            "captcha",
            "please verify you are a human",
            "i'm not a robot",
            "unusual traffic",
            "access denied",
            "blocked",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in captcha_indicators)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Scraping functions
# ---------------------------------------------------------------------------

def scrape_search_results(page, query, sort, max_listings, scroll_count=4):
    """Navigate to Etsy search and extract listing data.

    Returns list of listing dicts.
    """
    url = build_search_url(query, sort)
    print(f"[search] Navigating to: {url}", file=sys.stderr)
    listings = []

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)

        # Dismiss cookie banner on first load
        dismiss_cookie_banner(page)

        if _is_captcha(page):
            print("[search] CAPTCHA detected. Aborting.", file=sys.stderr)
            return listings

        # Scroll to load more results (Etsy uses lazy loading)
        for i in range(scroll_count):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            random_delay(1.5, 3.0)
            print(f"[search] Scroll {i + 1}/{scroll_count}", file=sys.stderr)

        # Scroll back to top for extraction
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # Extract listing cards
        # Etsy search results use .v2-listing-card or [data-listing-id] containers
        listing_selectors = [
            '[data-listing-id]',
            '.v2-listing-card',
            '.wt-grid__item-xs-6',
        ]

        result_items = []
        for selector in listing_selectors:
            result_items = page.query_selector_all(selector)
            if result_items:
                print(f"[search] Found {len(result_items)} items with selector: {selector}", file=sys.stderr)
                break

        if not result_items:
            print("[search] No listing elements found on page.", file=sys.stderr)
            return listings

        for item in result_items:
            if len(listings) >= max_listings:
                break

            listing = _extract_listing(item, page)
            if listing and listing.get("title"):
                listings.append(listing)

        print(f"[search] Extracted {len(listings)} listings", file=sys.stderr)

    except Exception as e:
        print(f"[search] Error during search: {e}", file=sys.stderr)

    return listings


def _extract_listing(item, page):
    """Extract data from a single listing card DOM element."""
    listing = {
        "title": "",
        "price": 0.0,
        "shop_name": "",
        "rating": 0.0,
        "review_count": 0,
        "listing_url": "",
        "image_url": "",
        "bestseller": False,
        "star_seller": False,
        "ad": False,
        "free_shipping": False,
    }

    try:
        # Listing ID
        listing_id = item.get_attribute("data-listing-id") or ""

        # Title - from the listing card link's title attribute or text
        title_el = item.query_selector(
            'h3, .v2-listing-card__title, [data-listing-card-title], '
            'a[title], .wt-text-caption'
        )
        if title_el:
            listing["title"] = (
                title_el.get_attribute("title")
                or title_el.inner_text().strip()
            )

        if not listing["title"]:
            return None

        # Price
        price_el = item.query_selector(
            '.currency-value, .lc-price .wt-text-title-01, '
            'span.currency-value, .search-collage-promotion-price, '
            '.wt-text-title-small, p.wt-text-title-01'
        )
        if price_el:
            listing["price"] = parse_price(price_el.inner_text())

        # Shop name
        shop_el = item.query_selector(
            '.v2-listing-card__shop, .shop-name, '
            'p.wt-text-gray, [data-shop-name]'
        )
        if shop_el:
            listing["shop_name"] = shop_el.inner_text().strip()

        # Rating (stars)
        rating_el = item.query_selector(
            '[aria-label*="star"], .v2-listing-card__rating input, '
            '.stars-svg, .wt-icon--star'
        )
        if rating_el:
            aria = rating_el.get_attribute("aria-label") or ""
            listing["rating"] = parse_rating(aria)

        # Review count
        review_el = item.query_selector(
            '.v2-listing-card__rating span, '
            '.wt-text-gray:has-text("review"), '
            '.wt-text-body-01'
        )
        if review_el:
            listing["review_count"] = parse_review_count(review_el.inner_text())

        # Listing URL
        link_el = item.query_selector('a[href*="/listing/"]')
        if link_el:
            href = link_el.get_attribute("href") or ""
            if href.startswith("/"):
                href = f"https://www.etsy.com{href}"
            listing["listing_url"] = href.split("?")[0]  # Remove tracking params

        # Image URL
        img_el = item.query_selector('img')
        if img_el:
            listing["image_url"] = (
                img_el.get_attribute("src")
                or img_el.get_attribute("data-src")
                or ""
            )

        # Badges: Bestseller
        item_html = item.inner_html().lower()
        listing["bestseller"] = "bestseller" in item_html or "best seller" in item_html

        # Badges: Star Seller
        listing["star_seller"] = "star seller" in item_html or "star_seller" in item_html

        # Ad/Promoted
        listing["ad"] = (
            "ad by" in item_html
            or "promoted" in item_html
            or item.query_selector('[data-ad]') is not None
        )

        # Free shipping
        listing["free_shipping"] = (
            "free shipping" in item_html
            or "free delivery" in item_html
        )

    except Exception as e:
        print(f"[extract] Error extracting listing: {e}", file=sys.stderr)

    return listing


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_as_markdown(data):
    """Convert JSON output to a readable markdown document."""
    lines = []
    lines.append(f"# Etsy Search Research: {data.get('query', '')}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Sort:** {data.get('sort', 'relevancy')}")
    lines.append(f"**Listings Found:** {data.get('listings_count', 0)}")
    lines.append("")

    metrics = data.get("metrics", {})
    if metrics:
        lines.append("## Market Metrics")
        lines.append("")
        lines.append(f"- **Average Price:** ${metrics.get('average_price', 0):.2f}")
        pr = metrics.get("price_range", {})
        lines.append(f"- **Price Range:** ${pr.get('min', 0):.2f} - ${pr.get('max', 0):.2f}")
        lines.append(f"- **Free Shipping:** {metrics.get('pct_free_shipping', 0):.1f}%")
        lines.append(f"- **Bestsellers:** {metrics.get('pct_bestseller', 0):.1f}%")
        lines.append("")

    for i, listing in enumerate(data.get("listings", []), 1):
        lines.append(f"### {i}. {listing.get('title', 'Unknown')}")
        lines.append(f"- **Price:** ${listing.get('price', 0):.2f}")
        lines.append(f"- **Shop:** {listing.get('shop_name', 'N/A')}")
        lines.append(f"- **Rating:** {listing.get('rating', 0)} ({listing.get('review_count', 0)} reviews)")
        badges = []
        if listing.get("bestseller"):
            badges.append("Bestseller")
        if listing.get("star_seller"):
            badges.append("Star Seller")
        if listing.get("ad"):
            badges.append("Ad")
        if listing.get("free_shipping"):
            badges.append("Free Shipping")
        if badges:
            lines.append(f"- **Badges:** {', '.join(badges)}")
        lines.append(f"- **URL:** {listing.get('listing_url', '')}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def check_playwright():
    """Check if playwright is available."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Search Etsy listings via Playwright and extract product data"
    )
    parser.add_argument(
        "--query", type=str, required=True,
        help="Search query (e.g., 'grandparent memory book')"
    )
    parser.add_argument(
        "--max-listings", type=int, default=20,
        help="Maximum listings to extract (default: 20)"
    )
    parser.add_argument(
        "--sort", type=str, default="relevancy",
        choices=list(SORT_OPTIONS.keys()),
        help="Sort order (default: relevancy)"
    )
    parser.add_argument(
        "--output", type=str, choices=["json", "markdown"], default="json",
        help='Output format (default: json)'
    )
    parser.add_argument(
        "--scroll-count", type=int, default=4,
        help="Number of times to scroll for more results (default: 4)"
    )

    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    from playwright.sync_api import sync_playwright

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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Stealth: override navigator.webdriver
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
        """)

        page = context.new_page()

        try:
            # Warm up: visit Etsy homepage to establish session cookies
            print("[main] Warming up session (visiting Etsy homepage)...", file=sys.stderr)
            try:
                page.goto("https://www.etsy.com/", wait_until="domcontentloaded", timeout=30000)
                random_delay(2, 4)
                dismiss_cookie_banner(page)
            except Exception as e:
                print(f"[main] Homepage warm-up failed: {e}", file=sys.stderr)

            # Search
            listings = scrape_search_results(
                page, args.query, args.sort, args.max_listings, args.scroll_count
            )

        finally:
            browser.close()

    # Compute metrics
    metrics = compute_search_metrics(listings)

    # Build output
    output_data = {
        "query": args.query,
        "sort": args.sort,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "listings_count": len(listings),
        "listings": listings,
        "metrics": metrics,
    }

    if args.output == "markdown":
        print(format_as_markdown(output_data))
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. {len(listings)} listings extracted.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
