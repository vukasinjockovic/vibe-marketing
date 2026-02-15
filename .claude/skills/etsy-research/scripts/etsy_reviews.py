#!/usr/bin/env python3
"""Extract reviews from Etsy product listings via Playwright.

Usage:
    python etsy_reviews.py --url "https://www.etsy.com/listing/12345/product-name" \
        --max-reviews 30 --stars "1,5" --output json

    python etsy_reviews.py --search "grandparent journal" \
        --max-products 3 --reviews-per-product 15 --stars "1,2,5" --output json

Returns JSON with product reviews and customer voice analysis including
love/hate phrases, product gaps, and gift mention detection.

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
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


# ---------------------------------------------------------------------------
# Pure helper functions (testable without browser)
# ---------------------------------------------------------------------------

def filter_reviews_by_stars(reviews, star_list):
    """Filter reviews to only include specified star ratings.

    Args:
        reviews: list of review dicts with 'stars' key
        star_list: list of ints, e.g. [1, 5]

    Returns:
        Filtered list of reviews.
    """
    star_set = set(star_list)
    return [r for r in reviews if r.get("stars") in star_set]


def dedupe_and_rank(phrases, max_items=20):
    """Deduplicate phrases (case-insensitive) and return most common ones."""
    if not phrases:
        return []

    # Normalize: keep first-seen casing per lowered key
    normalized = {}
    for phrase in phrases:
        key = phrase.lower().strip()
        if key and key not in normalized:
            normalized[key] = phrase.strip()

    # Count occurrences of the lowered version
    counts = Counter(p.lower().strip() for p in phrases if p.strip())
    ranked = sorted(normalized.keys(), key=lambda k: counts.get(k, 0), reverse=True)

    return [normalized[k] for k in ranked[:max_items]]


def analyze_etsy_reviews(reviews):
    """Analyze review text for voice mining patterns.

    Extracts love phrases, hate phrases, product gaps, and gift mentions
    using the 1-star + 5-star strategy.

    Args:
        reviews: list of review dicts with 'stars' and 'text' keys.

    Returns:
        dict with love_phrases, hate_phrases, product_gaps, gift_mentions.
    """
    love_phrases = []
    hate_phrases = []
    gap_phrases = []
    gift_phrases = []

    positive_texts = []
    negative_texts = []

    for review in reviews:
        text = review.get("text", "")
        stars = review.get("stars", 3)
        if not text:
            continue

        if stars >= 4:
            positive_texts.append(text)
        if stars <= 2:
            negative_texts.append(text)

    # Love phrase patterns (from 4-5 star reviews)
    love_patterns = [
        r"(?:i |we |my \w+ )(?:love|adore|cherish)(?:s|d)?\s+(.{10,80})",
        r"(?:absolutely|totally|really|so) (?:love|amazing|beautiful|perfect|gorgeous)(.{0,60})",
        r"made (?:me|my \w+|us) (?:cry|tear up|smile|laugh|happy)(.{0,60})",
        r"(?:perfect|best|ideal|wonderful|beautiful|gorgeous) (?:gift|present|idea|quality)(.{0,60})",
        r"(?:treasure|cherish|keep) (?:this|it) (?:forever|always)(.{0,40})",
        r"(?:exceeded|surpassed) (?:my |our )?expectations(.{0,40})",
        r"(?:highly|definitely|would) recommend(.{0,60})",
        r"(?:can't|cannot) (?:say enough|recommend enough|stop)(.{0,60})",
        r"(?:better than|even better than) (?:i |what i )?(?:expected|imagined|hoped)(.{0,60})",
        r"(?:stunning|incredible|remarkable|exquisite|gorgeous) (?:quality|craftsmanship|detail|work)(.{0,60})",
    ]

    # Hate phrase patterns (from 1-2 star reviews)
    hate_patterns = [
        r"(?:too |way too )(?:small|big|large|short|thin|thick|flimsy|generic|expensive)(.{0,60})",
        r"(?:fell apart|broke|damaged|ripped|torn|faded|peeled)(.{0,60})",
        r"not enough (?:space|room|pages|options|detail)(.{0,60})",
        r"(?:disappointed|disappointing|waste|terrible|horrible|awful)(.{0,60})",
        r"(?:returned|returning|sent back|refund|refunded)(.{0,60})",
        r"(?:cheaply|poorly) (?:made|constructed|built|designed|printed|packaged)(.{0,60})",
        r"(?:don't|do not|wouldn't|would not) (?:buy|recommend|waste|bother)(.{0,60})",
        r"not (?:worth|as described|what i expected|what was shown|like the picture)(.{0,60})",
        r"(?:wrong|incorrect|missing|broken|damaged) (?:item|product|order|size|color)(.{0,60})",
    ]

    # Product gap patterns (all reviews)
    gap_patterns = [
        r"(?:wish|wished|hoping|hope) (?:it |this |they |there )(?:had|was|were|would|could)(.{10,80})",
        r"(?:would be|it'd be) (?:nice|great|better|perfect) (?:if|to have)(.{10,80})",
        r"(?:only|my only) (?:complaint|issue|problem|concern|wish)(.{10,80})",
        r"(?:needs?|needed|missing|lacks?) (.{10,80})",
        r"(?:should have|should've|could use|could have) (.{10,80})",
        r"(?:if only|the only thing)(.{10,80})",
    ]

    # Gift mention patterns (all reviews)
    gift_patterns = [
        r"(?:bought|got|ordered|purchased) (?:this |it )?(?:for|as a) (?:gift |present )?(?:for )?(?:my )?(\w+.{0,40})",
        r"(?:christmas|birthday|mother'?s?\s*day|father'?s?\s*day|grandparent'?s?\s*day|anniversary|wedding|baby shower|retirement|graduation|valentine)",
        r"(?:gift|present) (?:for|to) (.{5,60})",
    ]

    # Process positive reviews
    for text in positive_texts:
        for pattern in love_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.strip().rstrip(".,;:!?")
                if phrase and len(phrase) > 5:
                    love_phrases.append(phrase)
                else:
                    full_match = re.search(pattern, text, re.IGNORECASE)
                    if full_match:
                        start = max(0, full_match.start() - 5)
                        end = min(len(text), full_match.end() + 30)
                        love_phrases.append(text[start:end].strip())

    # Process negative reviews
    for text in negative_texts:
        for pattern in hate_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.strip().rstrip(".,;:!?")
                if phrase and len(phrase) > 5:
                    hate_phrases.append(phrase)
                else:
                    full_match = re.search(pattern, text, re.IGNORECASE)
                    if full_match:
                        start = max(0, full_match.start() - 5)
                        end = min(len(text), full_match.end() + 30)
                        hate_phrases.append(text[start:end].strip())

    # Process all reviews for gaps and gifts
    all_texts = positive_texts + negative_texts
    for review in reviews:
        text = review.get("text", "")
        if not text:
            continue
        if text not in all_texts:
            all_texts.append(text)

    for text in all_texts:
        for pattern in gap_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.strip().rstrip(".,;:!?")
                if phrase and len(phrase) > 8:
                    gap_phrases.append(f"Customers want {phrase}")

        for pattern in gift_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip().rstrip(".,;:!?")
                if cleaned:
                    gift_phrases.append(cleaned)

    # Deduplicate and rank
    love_phrases = dedupe_and_rank(love_phrases, max_items=20)
    hate_phrases = dedupe_and_rank(hate_phrases, max_items=20)
    gap_phrases = dedupe_and_rank(gap_phrases, max_items=15)
    gift_phrases = dedupe_and_rank(gift_phrases, max_items=15)

    return {
        "love_phrases": love_phrases,
        "hate_phrases": hate_phrases,
        "product_gaps": gap_phrases,
        "gift_mentions": gift_phrases,
    }


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
            'button:has-text("Accept Cookies")',
        ]
        for selector in selectors:
            el = page.query_selector(selector)
            if el and el.is_visible():
                el.click()
                print("[cookie] Dismissed cookie banner", file=sys.stderr)
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

def search_etsy_products(page, query, max_products):
    """Search Etsy for products and return basic info for review scraping."""
    from urllib.parse import quote_plus

    url = f"https://www.etsy.com/search?q={quote_plus(query)}"
    print(f"[search] Navigating to: {url}", file=sys.stderr)
    products = []

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)
        dismiss_cookie_banner(page)

        if _is_captcha(page):
            print("[search] CAPTCHA detected.", file=sys.stderr)
            return products

        # Find listing links
        link_els = page.query_selector_all('a[href*="/listing/"]')
        seen_urls = set()

        for link_el in link_els:
            if len(products) >= max_products:
                break

            href = link_el.get_attribute("href") or ""
            if not href or "/listing/" not in href:
                continue

            # Normalize URL
            if href.startswith("/"):
                href = f"https://www.etsy.com{href}"
            clean_url = href.split("?")[0]

            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)

            # Get title from the link or nearby element
            title = link_el.get_attribute("title") or ""
            if not title:
                title_el = link_el.query_selector("h3, span, div")
                if title_el:
                    title = title_el.inner_text().strip()

            products.append({
                "title": title or "Untitled Listing",
                "url": clean_url,
            })
            print(f"[search] Found: {title[:60]}...", file=sys.stderr)

    except Exception as e:
        print(f"[search] Error: {e}", file=sys.stderr)

    return products


def scrape_listing_reviews(page, listing_url, max_reviews):
    """Navigate to an Etsy listing page and extract reviews.

    Returns (product_info, reviews_list).
    """
    info = {
        "title": "",
        "url": listing_url,
        "price": "",
        "rating": 0.0,
        "total_reviews": 0,
    }
    reviews = []

    try:
        page.goto(listing_url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)
        dismiss_cookie_banner(page)

        if _is_captcha(page):
            print(f"[listing] CAPTCHA on {listing_url}", file=sys.stderr)
            return info, reviews

        # Extract product info
        title_el = page.query_selector('h1, [data-listing-page-title]')
        if title_el:
            info["title"] = title_el.inner_text().strip()

        price_el = page.query_selector(
            'p[data-buy-box-listing-price], .wt-text-title-larger, '
            '[data-selector="price-only"] p'
        )
        if price_el:
            info["price"] = price_el.inner_text().strip()

        # Rating
        rating_el = page.query_selector(
            '[data-rating], input[name="rating"], '
            '[aria-label*="star"]'
        )
        if rating_el:
            val = rating_el.get_attribute("data-rating") or rating_el.get_attribute("aria-label") or ""
            match = re.search(r"(\d+(?:\.\d+)?)", val)
            if match:
                info["rating"] = float(match.group(1))

        # Total review count
        review_count_el = page.query_selector(
            '[data-reviews-count], '
            'a[href*="#reviews"]'
        )
        if review_count_el:
            text = review_count_el.inner_text()
            match = re.search(r"[\d,]+", text)
            if match:
                info["total_reviews"] = int(match.group().replace(",", ""))

        # Scroll to reviews section
        reviews_section = page.query_selector('#reviews, [data-reviews], .reviews')
        if reviews_section:
            reviews_section.scroll_into_view_if_needed()
            random_delay(1, 2)
        else:
            # Scroll down progressively to find reviews
            for pct in [0.4, 0.6, 0.8, 1.0]:
                page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {pct})")
                time.sleep(1)

        random_delay(1, 2)

        # Extract reviews
        # Etsy review elements have various selectors depending on page version
        review_selectors = [
            '[data-review-region]',
            '.review-item',
            '.wt-grid__item-xs-12 .wt-display-flex-xs',
        ]

        review_elements = []
        for selector in review_selectors:
            review_elements = page.query_selector_all(selector)
            if review_elements:
                print(f"[reviews] Found {len(review_elements)} review elements with: {selector}", file=sys.stderr)
                break

        # If still no reviews, try loading more
        collected = 0
        page_num = 0

        while collected < max_reviews:
            for rev_el in review_elements:
                if collected >= max_reviews:
                    break

                review = _extract_single_review(rev_el)
                if review and review.get("text"):
                    reviews.append(review)
                    collected += 1

            # Try to load more reviews (click "Load more" or pagination)
            if collected < max_reviews:
                more_loaded = _load_more_reviews(page)
                if not more_loaded:
                    break
                page_num += 1
                if page_num > 10:  # Safety limit
                    break

                # Re-fetch review elements after loading more
                for selector in review_selectors:
                    review_elements = page.query_selector_all(selector)
                    if review_elements:
                        # Only process new ones (skip already collected count)
                        review_elements = review_elements[collected:]
                        break

        print(f"[reviews] Collected {len(reviews)} reviews from {listing_url}", file=sys.stderr)

    except Exception as e:
        print(f"[listing] Error scraping {listing_url}: {e}", file=sys.stderr)

    return info, reviews


def _extract_single_review(rev_el):
    """Extract data from a single review DOM element."""
    review = {
        "stars": 0,
        "text": "",
        "reviewer_name": "",
        "date": "",
        "verified_purchase": False,
        "has_photos": False,
    }

    try:
        # Star rating
        star_el = rev_el.query_selector(
            'input[name="rating"], [data-rating], '
            '[aria-label*="star"], .stars-svg'
        )
        if star_el:
            val = (
                star_el.get_attribute("value")
                or star_el.get_attribute("data-rating")
                or star_el.get_attribute("aria-label")
                or ""
            )
            match = re.search(r"(\d+(?:\.\d+)?)", str(val))
            if match:
                review["stars"] = int(float(match.group(1)))

        # Review text
        text_el = rev_el.query_selector(
            'p[data-review-text], .wt-text-body-01, '
            '.review-text, p.wt-content-toggle__body'
        )
        if text_el:
            review["text"] = text_el.inner_text().strip()

        # Reviewer name
        name_el = rev_el.query_selector(
            'p[data-review-username], .reviewer-name, '
            'a[href*="/people/"], span.wt-text-caption'
        )
        if name_el:
            review["reviewer_name"] = name_el.inner_text().strip()

        # Date
        date_el = rev_el.query_selector(
            'p[data-review-date], .review-date, '
            'span.wt-text-gray, time'
        )
        if date_el:
            date_text = date_el.get_attribute("datetime") or date_el.inner_text().strip()
            review["date"] = _parse_date(date_text)

        # Verified purchase (Etsy marks these differently)
        rev_html = rev_el.inner_html().lower()
        review["verified_purchase"] = "verified" in rev_html or "purchased this item" in rev_html

        # Has photos
        review["has_photos"] = rev_el.query_selector('img[src*="review"]') is not None

    except Exception as e:
        print(f"[extract] Error extracting review: {e}", file=sys.stderr)

    return review


def _parse_date(date_str):
    """Parse an Etsy review date string."""
    if not date_str:
        return ""
    # Try ISO format first
    match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if match:
        return match.group(1)
    # Try "Month Day, Year"
    match = re.search(r"(\w+\s+\d{1,2},?\s+\d{4})", date_str)
    if match:
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(match.group(1).replace(",", ""), "%B %d %Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            pass
    return date_str.strip()


def _load_more_reviews(page):
    """Try to load more reviews via pagination or 'Load more' button.

    Returns True if more reviews were loaded.
    """
    try:
        # Try "Load more" button
        load_more_selectors = [
            'button:has-text("Load more")',
            'button:has-text("Show more")',
            'a:has-text("Next")',
            '[data-reviews-pagination] a',
        ]
        for selector in load_more_selectors:
            el = page.query_selector(selector)
            if el and el.is_visible():
                el.click()
                random_delay(2, 3)
                return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_as_markdown(data):
    """Convert JSON output to markdown."""
    lines = []
    lines.append(f"# Etsy Reviews Research: {data.get('query', 'Direct URL')}")
    lines.append("")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Products Scraped:** {data.get('products_scraped', 0)}")
    lines.append(f"**Total Reviews Collected:** {data.get('total_reviews_collected', 0)}")
    lines.append("")

    for product in data.get("products", []):
        lines.append("---")
        lines.append(f"## {product.get('title', 'Unknown')}")
        lines.append(f"- **URL:** {product.get('url', '')}")
        lines.append(f"- **Price:** {product.get('price', 'N/A')}")
        lines.append(f"- **Rating:** {product.get('rating', 0)}")
        lines.append(f"- **Total Reviews:** {product.get('total_reviews', 0)}")
        lines.append("")

        reviews = product.get("reviews", [])
        if reviews:
            lines.append(f"### Reviews ({len(reviews)} collected)")
            lines.append("")
            for i, review in enumerate(reviews, 1):
                stars = review.get("stars", "?")
                star_str = "*" * int(stars) if isinstance(stars, (int, float)) else str(stars)
                lines.append(f"**{i}. [{star_str}] {review.get('reviewer_name', 'Anonymous')}** ({review.get('date', '')})")
                if review.get("verified_purchase"):
                    lines.append("   _Verified Purchase_")
                lines.append(f"   > {review.get('text', '')[:500]}")
                lines.append("")

    va = data.get("voice_analysis", {})
    if va:
        lines.append("---")
        lines.append("## Voice Analysis")
        lines.append("")

        if va.get("love_phrases"):
            lines.append("### Love Phrases (4-5 star)")
            for phrase in va["love_phrases"]:
                lines.append(f'- "{phrase}"')
            lines.append("")

        if va.get("hate_phrases"):
            lines.append("### Hate Phrases (1-2 star)")
            for phrase in va["hate_phrases"]:
                lines.append(f'- "{phrase}"')
            lines.append("")

        if va.get("product_gaps"):
            lines.append("### Product Gaps")
            for gap in va["product_gaps"]:
                lines.append(f"- {gap}")
            lines.append("")

        if va.get("gift_mentions"):
            lines.append("### Gift Mentions")
            for gm in va["gift_mentions"]:
                lines.append(f"- {gm}")
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
        description="Extract reviews from Etsy product listings via Playwright"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url", type=str,
        help="Direct Etsy listing URL to scrape reviews from"
    )
    group.add_argument(
        "--search", type=str,
        help="Search Etsy for products, then scrape reviews"
    )
    parser.add_argument(
        "--max-reviews", type=int, default=30,
        help="Max reviews to extract from a single listing (default: 30)"
    )
    parser.add_argument(
        "--max-products", type=int, default=3,
        help="Max products to scrape when using --search (default: 3)"
    )
    parser.add_argument(
        "--reviews-per-product", type=int, default=15,
        help="Reviews per product when using --search (default: 15)"
    )
    parser.add_argument(
        "--stars", type=str, default="1,2,3,4,5",
        help='Comma-separated star ratings to include (default: "1,2,3,4,5"). Tip: "1,5" for best voice data.'
    )
    parser.add_argument(
        "--output", type=str, choices=["json", "markdown"], default="json",
        help='Output format (default: json)'
    )

    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    from playwright.sync_api import sync_playwright

    # Parse star filters
    star_filters = []
    for s in args.stars.split(","):
        s = s.strip()
        if s in ("1", "2", "3", "4", "5"):
            star_filters.append(int(s))
    if not star_filters:
        print("ERROR: No valid star ratings specified.", file=sys.stderr)
        sys.exit(1)

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
            print("[main] Warming up session (visiting Etsy homepage)...", file=sys.stderr)
            try:
                page.goto("https://www.etsy.com/", wait_until="domcontentloaded", timeout=30000)
                random_delay(2, 4)
                dismiss_cookie_banner(page)
            except Exception as e:
                print(f"[main] Homepage warm-up failed: {e}", file=sys.stderr)

            products_data = []

            if args.url:
                # Direct URL mode
                max_rev = args.max_reviews
                info, reviews = scrape_listing_reviews(page, args.url, max_rev)
                # Apply star filter client-side
                reviews = filter_reviews_by_stars(reviews, star_filters)
                products_data.append({
                    **info,
                    "reviews": reviews,
                })

            else:
                # Search mode
                products = search_etsy_products(page, args.search, args.max_products)
                for prod in products:
                    print(f"\n[main] Scraping reviews for: {prod['title'][:60]}...", file=sys.stderr)
                    random_delay(2, 4)
                    info, reviews = scrape_listing_reviews(
                        page, prod["url"], args.reviews_per_product
                    )
                    reviews = filter_reviews_by_stars(reviews, star_filters)
                    products_data.append({
                        **info,
                        "reviews": reviews,
                    })
                    print(f"[main] Collected {len(reviews)} reviews", file=sys.stderr)

        finally:
            browser.close()

    # Voice analysis across all reviews
    all_reviews = []
    for pd in products_data:
        all_reviews.extend(pd.get("reviews", []))

    print(f"\n[main] Running voice analysis on {len(all_reviews)} reviews...", file=sys.stderr)
    voice = analyze_etsy_reviews(all_reviews)

    total_reviews = sum(len(pd.get("reviews", [])) for pd in products_data)
    output_data = {
        "query": args.search or args.url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "products_scraped": len(products_data),
        "total_reviews_collected": total_reviews,
        "products": products_data,
        "voice_analysis": voice,
    }

    if args.output == "markdown":
        print(format_as_markdown(output_data))
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))

    print(
        f"\n[main] Done. {len(products_data)} products, {total_reviews} reviews.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
