#!/usr/bin/env python3
"""Analyze an Etsy shop for competitive intelligence via Playwright.

Usage:
    python etsy_shop.py --url "https://www.etsy.com/shop/ShopName" --max-listings 20 --output json
    python etsy_shop.py --shop-name "DuncanandStone" --max-listings 20 --output json

Returns JSON with shop metadata (sales, reviews, rating, location),
top listings, and pricing strategy analysis.

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
from datetime import datetime, timezone
from statistics import median


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


# ---------------------------------------------------------------------------
# Pure helper functions (testable without browser)
# ---------------------------------------------------------------------------

def parse_sales_count(text):
    """Parse sales count from text like '1,234 sales'.

    Returns 0 for empty/None/unparseable input.
    """
    if not text:
        return 0
    text = str(text)
    match = re.search(r"([\d,]+)\s*sale", text, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0


def build_shop_url(name_or_url):
    """Build an Etsy shop URL from a shop name or return existing URL.

    If already a URL (contains 'http'), returns as-is.
    Otherwise, constructs https://www.etsy.com/shop/{name}.
    """
    if name_or_url.startswith("http"):
        return name_or_url
    return f"https://www.etsy.com/shop/{name_or_url}"


def analyze_pricing_strategy(listings):
    """Analyze pricing patterns from a list of shop listings.

    Each listing should have: price (float), reviews (int).
    Returns dict with price_range, average_price, median_price, pricing_tiers.
    """
    if not listings:
        return {
            "price_range": {"min": 0, "max": 0},
            "average_price": 0,
            "median_price": 0,
            "pricing_tiers": [],
            "bestseller_price_range": {"min": 0, "max": 0},
        }

    prices = [l.get("price", 0) for l in listings if l.get("price", 0) > 0]
    if not prices:
        return {
            "price_range": {"min": 0, "max": 0},
            "average_price": 0,
            "median_price": 0,
            "pricing_tiers": [],
            "bestseller_price_range": {"min": 0, "max": 0},
        }

    avg = round(sum(prices) / len(prices), 2)
    med = round(median(prices), 2)

    # Identify pricing tiers (group by $10 ranges)
    tiers = {}
    for p in prices:
        tier_key = int(p // 10) * 10
        tier_label = f"${tier_key}-${tier_key + 9}"
        tiers[tier_label] = tiers.get(tier_label, 0) + 1

    tier_list = sorted(tiers.items(), key=lambda x: -x[1])

    # Bestseller price range (top reviewed listings)
    sorted_by_reviews = sorted(listings, key=lambda l: l.get("reviews", 0), reverse=True)
    top_sellers = sorted_by_reviews[:max(1, len(sorted_by_reviews) // 3)]
    top_prices = [l.get("price", 0) for l in top_sellers if l.get("price", 0) > 0]

    return {
        "price_range": {
            "min": round(min(prices), 2),
            "max": round(max(prices), 2),
        },
        "average_price": avg,
        "median_price": med,
        "pricing_tiers": [{"range": k, "count": v} for k, v in tier_list],
        "bestseller_price_range": {
            "min": round(min(top_prices), 2) if top_prices else 0,
            "max": round(max(top_prices), 2) if top_prices else 0,
        },
    }


def parse_price(text):
    """Parse a price string into a float."""
    if not text:
        return 0.0
    text = str(text)
    match = re.search(r"[\d,]+\.?\d*", text)
    if match:
        try:
            return float(match.group().replace(",", ""))
        except ValueError:
            return 0.0
    return 0.0


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

def random_delay(min_sec=2.0, max_sec=4.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def dismiss_cookie_banner(page):
    """Try to dismiss Etsy's cookie consent banner."""
    try:
        selectors = [
            'button[data-gdpr-single-choice-accept="true"]',
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
        ]
        for selector in selectors:
            el = page.query_selector(selector)
            if el and el.is_visible():
                el.click()
                time.sleep(1)
                return True
    except Exception:
        pass
    return False


def _is_captcha(page):
    """Detect CAPTCHA or bot detection page."""
    try:
        content = page.content().lower()
        indicators = ["captcha", "please verify", "unusual traffic", "access denied"]
        return any(ind in content for ind in indicators)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Scraping functions
# ---------------------------------------------------------------------------

def scrape_shop(page, shop_url, max_listings):
    """Navigate to an Etsy shop page and extract shop data + listings.

    Returns (shop_info, listings_list).
    """
    shop_info = {
        "shop_name": "",
        "total_sales": 0,
        "total_reviews": 0,
        "average_rating": 0.0,
        "member_since": "",
        "location": "",
        "about_text": "",
        "shop_url": shop_url,
    }
    listings = []

    try:
        page.goto(shop_url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)
        dismiss_cookie_banner(page)

        if _is_captcha(page):
            print(f"[shop] CAPTCHA on {shop_url}", file=sys.stderr)
            return shop_info, listings

        # Shop name
        name_el = page.query_selector(
            'h1, [data-shop-name], .shop-name-and-title h1, '
            '.wt-text-heading'
        )
        if name_el:
            shop_info["shop_name"] = name_el.inner_text().strip()

        # Sales count
        sales_el = page.query_selector(
            '[data-shop-sales-count], .shop-sales-count, '
            'span:has-text("sales")'
        )
        if sales_el:
            shop_info["total_sales"] = parse_sales_count(sales_el.inner_text())

        # Reviews / rating
        review_el = page.query_selector(
            '[data-shop-reviews], .shop-reviews, '
            'span:has-text("reviews"), a[href*="reviews"]'
        )
        if review_el:
            text = review_el.inner_text()
            count_match = re.search(r"([\d,]+)", text)
            if count_match:
                shop_info["total_reviews"] = int(count_match.group(1).replace(",", ""))

        rating_el = page.query_selector(
            'input[name="rating"], [data-rating], '
            '[aria-label*="star"]'
        )
        if rating_el:
            val = (
                rating_el.get_attribute("value")
                or rating_el.get_attribute("data-rating")
                or rating_el.get_attribute("aria-label")
                or ""
            )
            match = re.search(r"(\d+(?:\.\d+)?)", str(val))
            if match:
                shop_info["average_rating"] = float(match.group(1))

        # Member since
        member_el = page.query_selector(
            '[data-member-since], .shop-member-since, '
            'span:has-text("member since"), span:has-text("On Etsy since")'
        )
        if member_el:
            text = member_el.inner_text()
            year_match = re.search(r"(\d{4})", text)
            if year_match:
                shop_info["member_since"] = year_match.group(1)

        # Location
        location_el = page.query_selector(
            '[data-shop-location], .shop-location, '
            'span:has-text("Located in")'
        )
        if location_el:
            shop_info["location"] = location_el.inner_text().strip()
            # Clean up prefix
            shop_info["location"] = re.sub(
                r"^(?:Located in|Location:)\s*", "", shop_info["location"], flags=re.IGNORECASE
            ).strip()

        # About text
        about_el = page.query_selector(
            '.shop-about-text, [data-about], .wt-text-body-01'
        )
        if about_el:
            shop_info["about_text"] = about_el.inner_text().strip()[:500]

        # Scroll to load listings
        for i in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            random_delay(1.5, 2.5)

        # Extract listings
        listing_els = page.query_selector_all(
            '[data-listing-id], .listing-link, '
            '.v2-listing-card, .wt-grid__item-xs-6'
        )
        print(f"[shop] Found {len(listing_els)} listing elements", file=sys.stderr)

        for el in listing_els:
            if len(listings) >= max_listings:
                break

            listing = _extract_shop_listing(el)
            if listing and listing.get("title"):
                listings.append(listing)

        print(f"[shop] Extracted {len(listings)} listings", file=sys.stderr)

    except Exception as e:
        print(f"[shop] Error scraping shop: {e}", file=sys.stderr)

    return shop_info, listings


def _extract_shop_listing(el):
    """Extract listing data from a shop page listing card."""
    listing = {
        "title": "",
        "price": 0.0,
        "reviews": 0,
        "favorites": 0,
        "listing_url": "",
        "bestseller": False,
    }

    try:
        # Title
        title_el = el.query_selector('h3, a[title], .v2-listing-card__title')
        if title_el:
            listing["title"] = (
                title_el.get_attribute("title") or title_el.inner_text().strip()
            )

        if not listing["title"]:
            return None

        # Price
        price_el = el.query_selector(
            '.currency-value, .wt-text-title-01, '
            'span.currency-value, p.wt-text-title-01'
        )
        if price_el:
            listing["price"] = parse_price(price_el.inner_text())

        # Reviews
        review_el = el.query_selector(
            '.v2-listing-card__rating span, '
            'span:has-text("review")'
        )
        if review_el:
            text = review_el.inner_text()
            match = re.search(r"[\d,]+", text)
            if match:
                listing["reviews"] = int(match.group().replace(",", ""))

        # Listing URL
        link_el = el.query_selector('a[href*="/listing/"]')
        if link_el:
            href = link_el.get_attribute("href") or ""
            if href.startswith("/"):
                href = f"https://www.etsy.com{href}"
            listing["listing_url"] = href.split("?")[0]

        # Bestseller badge
        html = el.inner_html().lower()
        listing["bestseller"] = "bestseller" in html or "best seller" in html

    except Exception as e:
        print(f"[extract] Error: {e}", file=sys.stderr)

    return listing


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_as_markdown(data):
    """Convert JSON output to markdown."""
    lines = []
    shop = data.get("shop_info", {})
    lines.append(f"# Etsy Shop Analysis: {shop.get('shop_name', 'Unknown')}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Shop URL:** {shop.get('shop_url', '')}")
    lines.append("")
    lines.append("## Shop Overview")
    lines.append("")
    lines.append(f"- **Total Sales:** {shop.get('total_sales', 0):,}")
    lines.append(f"- **Total Reviews:** {shop.get('total_reviews', 0):,}")
    lines.append(f"- **Average Rating:** {shop.get('average_rating', 0)}")
    lines.append(f"- **Member Since:** {shop.get('member_since', 'N/A')}")
    lines.append(f"- **Location:** {shop.get('location', 'N/A')}")
    lines.append("")

    if shop.get("about_text"):
        lines.append("### About")
        lines.append(f"> {shop['about_text'][:300]}")
        lines.append("")

    pricing = data.get("pricing_analysis", {})
    if pricing:
        lines.append("## Pricing Strategy")
        lines.append("")
        pr = pricing.get("price_range", {})
        lines.append(f"- **Price Range:** ${pr.get('min', 0):.2f} - ${pr.get('max', 0):.2f}")
        lines.append(f"- **Average Price:** ${pricing.get('average_price', 0):.2f}")
        lines.append(f"- **Median Price:** ${pricing.get('median_price', 0):.2f}")
        bpr = pricing.get("bestseller_price_range", {})
        if bpr.get("min") or bpr.get("max"):
            lines.append(f"- **Bestseller Price Range:** ${bpr.get('min', 0):.2f} - ${bpr.get('max', 0):.2f}")
        lines.append("")

        tiers = pricing.get("pricing_tiers", [])
        if tiers:
            lines.append("### Pricing Tiers")
            for tier in tiers:
                lines.append(f"- {tier['range']}: {tier['count']} listings")
            lines.append("")

    listings = data.get("listings", [])
    if listings:
        lines.append(f"## Top Listings ({len(listings)})")
        lines.append("")
        for i, listing in enumerate(listings, 1):
            badges = []
            if listing.get("bestseller"):
                badges.append("Bestseller")
            badge_str = f" [{', '.join(badges)}]" if badges else ""
            lines.append(f"### {i}. {listing.get('title', 'Unknown')}{badge_str}")
            lines.append(f"- **Price:** ${listing.get('price', 0):.2f}")
            lines.append(f"- **Reviews:** {listing.get('reviews', 0)}")
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
        description="Analyze an Etsy shop for competitive intelligence"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url", type=str,
        help="Direct Etsy shop URL (e.g., https://www.etsy.com/shop/ShopName)"
    )
    group.add_argument(
        "--shop-name", type=str,
        help="Etsy shop name (e.g., DuncanandStone)"
    )
    parser.add_argument(
        "--max-listings", type=int, default=20,
        help="Maximum listings to extract (default: 20)"
    )
    parser.add_argument(
        "--output", type=str, choices=["json", "markdown"], default="json",
        help='Output format (default: json)'
    )

    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    from playwright.sync_api import sync_playwright

    shop_url = args.url if args.url else build_shop_url(args.shop_name)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
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
            },
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            # Warm up session
            print("[main] Warming up session...", file=sys.stderr)
            try:
                page.goto("https://www.etsy.com/", wait_until="domcontentloaded", timeout=30000)
                random_delay(2, 4)
                dismiss_cookie_banner(page)
            except Exception as e:
                print(f"[main] Homepage warm-up failed: {e}", file=sys.stderr)

            # Scrape shop
            shop_info, listings = scrape_shop(page, shop_url, args.max_listings)

        finally:
            browser.close()

    # Pricing analysis
    pricing = analyze_pricing_strategy(listings)

    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "shop_info": shop_info,
        "listings_count": len(listings),
        "listings": listings,
        "pricing_analysis": pricing,
    }

    if args.output == "markdown":
        print(format_as_markdown(output_data))
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. Shop: {shop_info.get('shop_name', 'Unknown')}, "
        f"{len(listings)} listings extracted.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
