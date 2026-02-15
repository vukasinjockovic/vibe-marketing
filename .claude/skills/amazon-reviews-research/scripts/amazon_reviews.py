#!/usr/bin/env python3
"""Extract customer voice data from Amazon product reviews via Playwright.

Usage:
    python amazon_reviews.py --search "grandparent journal" \
        --max-products 3 \
        --reviews-per-product 20 \
        --stars "1,2,5" \
        --output json

    python amazon_reviews.py --product-urls "https://www.amazon.com/dp/B07EXAMPLE" \
        --reviews-per-product 30 \
        --output markdown

Returns JSON (or markdown) with product reviews, customer voice analysis including
love/hate phrases, product gaps, buyer-vs-user dynamics, and emotional triggers.

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
# Helpers
# ---------------------------------------------------------------------------

def random_delay(min_sec=2.0, max_sec=4.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def extract_asin_from_url(url):
    """Extract ASIN from an Amazon product URL."""
    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/product-reviews/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"asin=([A-Z0-9]{10})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def parse_date(date_str):
    """Parse Amazon review date string into ISO format."""
    # Common formats: "Reviewed in the United States on December 28, 2025"
    match = re.search(
        r"on\s+(\w+\s+\d{1,2},\s+\d{4})", date_str
    )
    if match:
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(match.group(1), "%B %d, %Y")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            pass
    # Fallback: try to find any date-like pattern
    match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if match:
        return match.group(1)
    return date_str.strip() if date_str else ""


def parse_helpful_votes(text):
    """Parse helpful votes from text like '45 people found this helpful'."""
    if not text:
        return 0
    match = re.search(r"(\d+)\s+people?\s+found\s+this\s+helpful", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    if "one person found this helpful" in text.lower():
        return 1
    return 0


def parse_star_rating(element_text):
    """Parse star rating from text like '5.0 out of 5 stars' or aria labels."""
    match = re.search(r"(\d+(?:\.\d+)?)\s+out\s+of\s+5", element_text)
    if match:
        return float(match.group(1))
    match = re.search(r"(\d+(?:\.\d+)?)\s+star", element_text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0


# ---------------------------------------------------------------------------
# Scraping functions
# ---------------------------------------------------------------------------

def search_products(page, query, max_products):
    """Search Amazon for products and return list of {title, asin, url}."""
    products = []
    search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    print(f"[search] Navigating to: {search_url}", file=sys.stderr)

    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)

        # Check for CAPTCHA
        if _is_captcha(page):
            print("[search] CAPTCHA detected on search page. Aborting search.", file=sys.stderr)
            return products

        # Extract product results
        # Amazon search results use data-asin attributes on result cards
        result_items = page.query_selector_all('[data-asin]:not([data-asin=""])')
        print(f"[search] Found {len(result_items)} result items", file=sys.stderr)

        for item in result_items:
            if len(products) >= max_products:
                break

            asin = item.get_attribute("data-asin")
            if not asin or len(asin) != 10:
                continue

            # Get product title
            title_el = item.query_selector("h2 a span, h2 span")
            title = title_el.inner_text().strip() if title_el else ""

            if not title:
                continue

            # Get product URL
            link_el = item.query_selector("h2 a")
            href = link_el.get_attribute("href") if link_el else ""
            product_url = f"https://www.amazon.com/dp/{asin}"
            if href and href.startswith("/"):
                product_url = f"https://www.amazon.com{href}"

            # Get price
            price_el = item.query_selector(".a-price .a-offscreen")
            price = price_el.inner_text().strip() if price_el else ""

            # Get rating
            rating_el = item.query_selector('[aria-label*="out of 5 stars"]')
            rating_text = rating_el.get_attribute("aria-label") if rating_el else ""
            overall_rating = parse_star_rating(rating_text) if rating_text else 0

            # Get review count
            review_count_el = item.query_selector('[aria-label*="rating"] + span, a[href*="customerReviews"] span')
            review_count_text = review_count_el.inner_text().strip() if review_count_el else "0"
            total_reviews = 0
            review_count_match = re.search(r"[\d,]+", review_count_text)
            if review_count_match:
                total_reviews = int(review_count_match.group().replace(",", ""))

            products.append({
                "title": title,
                "asin": asin,
                "url": f"https://www.amazon.com/dp/{asin}",
                "price": price,
                "overall_rating": overall_rating,
                "total_reviews": total_reviews,
            })
            print(f"[search] Found product: {title[:60]}... (ASIN: {asin})", file=sys.stderr)

    except Exception as e:
        print(f"[search] Error during search: {e}", file=sys.stderr)

    return products


def scrape_product_page(page, asin, star_filters, reviews_per_product):
    """Navigate to product page and extract metadata + reviews.

    Amazon requires sign-in for /product-reviews/ pages, so we scrape
    reviews directly from the product detail page instead. The product
    page shows ~8-11 "Top reviews" without authentication.

    Returns (info_dict, reviews_list).
    """
    product_url = f"https://www.amazon.com/dp/{asin}"
    info = {
        "title": "",
        "price": "",
        "overall_rating": 0,
        "total_reviews": 0,
    }
    reviews = []

    try:
        page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)

        if _is_captcha(page):
            print(f"[product] CAPTCHA on product page {asin}", file=sys.stderr)
            return info, reviews

        # Scroll down to load the reviews section (lazy-loaded)
        for scroll_pct in [0.3, 0.5, 0.7, 0.85, 1.0]:
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {scroll_pct})")
            time.sleep(0.8)

        random_delay(1, 2)

        # --- Product metadata ---

        # Title
        title_el = page.query_selector("#productTitle")
        if title_el:
            info["title"] = title_el.inner_text().strip()

        # Price
        price_el = page.query_selector(".a-price .a-offscreen, #priceblock_ourprice, #priceblock_dealprice")
        if price_el:
            info["price"] = price_el.inner_text().strip()

        # Overall rating
        rating_el = page.query_selector('#acrPopover [aria-label*="out of 5"], .a-icon-star span')
        if rating_el:
            rating_text = rating_el.get_attribute("aria-label") or rating_el.inner_text()
            info["overall_rating"] = parse_star_rating(rating_text)

        # Total reviews
        review_el = page.query_selector("#acrCustomerReviewText")
        if review_el:
            text = review_el.inner_text().strip()
            match = re.search(r"[\d,]+", text)
            if match:
                info["total_reviews"] = int(match.group().replace(",", ""))

        # --- Reviews from product page ---

        review_elements = page.query_selector_all('[data-hook="review"]')
        print(
            f"[reviews] Found {len(review_elements)} reviews on product page for {asin}",
            file=sys.stderr,
        )

        star_filter_set = set(star_filters) if star_filters else None
        collected = 0

        for rev_el in review_elements:
            if collected >= reviews_per_product:
                break

            review = _extract_single_review(rev_el)
            if not review or not review.get("text"):
                continue

            # Apply star filter if specified
            if star_filter_set and review["stars"] not in star_filter_set:
                continue

            reviews.append(review)
            collected += 1

    except Exception as e:
        print(f"[product] Error scraping product page for {asin}: {e}", file=sys.stderr)

    return info, reviews


def _extract_single_review(rev_el):
    """Extract data from a single review DOM element."""
    review = {
        "stars": 0,
        "title": "",
        "text": "",
        "date": "",
        "helpful_votes": 0,
        "verified": False,
    }

    try:
        # Star rating from the review element itself
        star_el = rev_el.query_selector('[data-hook="review-star-rating"] span, .a-icon-star span')
        if star_el:
            star_text = star_el.inner_text()
            parsed = parse_star_rating(star_text)
            if parsed > 0:
                review["stars"] = int(parsed)

        # Review title
        title_el = rev_el.query_selector('[data-hook="review-title"] span:not(.a-icon-alt), [data-hook="review-title"]')
        if title_el:
            # The title element often contains spans; get the last meaningful text
            spans = rev_el.query_selector_all('[data-hook="review-title"] span')
            if spans:
                # Usually the actual title text is in the last span
                for span in reversed(spans):
                    text = span.inner_text().strip()
                    if text and "out of 5 stars" not in text:
                        review["title"] = text
                        break
            if not review["title"]:
                review["title"] = title_el.inner_text().strip()
                # Clean star rating text from title
                review["title"] = re.sub(r"\d+\.\d+\s+out\s+of\s+5\s+stars?\s*", "", review["title"]).strip()

        # Review body text
        body_el = rev_el.query_selector('[data-hook="review-body"] span')
        if body_el:
            review["text"] = body_el.inner_text().strip()

        # Date
        date_el = rev_el.query_selector('[data-hook="review-date"]')
        if date_el:
            review["date"] = parse_date(date_el.inner_text())

        # Helpful votes
        helpful_el = rev_el.query_selector('[data-hook="helpful-vote-statement"]')
        if helpful_el:
            review["helpful_votes"] = parse_helpful_votes(helpful_el.inner_text())

        # Verified purchase
        verified_el = rev_el.query_selector('[data-hook="avp-badge"], .a-color-state')
        if verified_el:
            text = verified_el.inner_text().lower()
            review["verified"] = "verified" in text

    except Exception as e:
        print(f"[extract] Error extracting review: {e}", file=sys.stderr)

    return review


def _is_captcha(page):
    """Detect if the current page shows a CAPTCHA."""
    try:
        content = page.content()
        captcha_indicators = [
            "captcha",
            "Type the characters you see in this image",
            "Enter the characters you see below",
            "Sorry, we just need to make sure you're not a robot",
            "api-services-support@amazon.com",
        ]
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in captcha_indicators)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Voice analysis
# ---------------------------------------------------------------------------

def analyze_voice(products_data):
    """Aggregate voice analysis across all scraped reviews.

    Returns dict with love_phrases, hate_phrases, product_gaps,
    buyer_vs_user, emotional_triggers, gift_occasions.
    """
    love_phrases = []
    hate_phrases = []
    gap_phrases = []
    gift_phrases = []
    emotional_phrases = []
    all_positive_text = []
    all_negative_text = []

    for product in products_data:
        for review in product.get("reviews", []):
            text = review.get("text", "")
            title = review.get("title", "")
            stars = review.get("stars", 3)
            combined = f"{title}. {text}"

            if stars >= 4:
                all_positive_text.append(combined)
            if stars <= 2:
                all_negative_text.append(combined)

    # Extract love phrases from positive reviews
    love_markers = [
        r"(?:i |we |my \w+ )(?:love|adore|cherish)(?:s|d)?\s+(.{10,80})",
        r"(?:absolutely|totally|really|so) (?:love|amazing|beautiful|perfect)(.{0,60})",
        r"made (?:me|my \w+|us) (?:cry|tear up|smile|laugh|happy)(.{0,60})",
        r"(?:perfect|best|ideal|wonderful|beautiful) (?:gift|present|idea)(.{0,60})",
        r"wish (?:i|we|I) (?:had |would have )?(?:started|bought|gotten|found)(.{0,60})",
        r"(?:treasure|cherish|keep) (?:this|it) (?:forever|always)(.{0,40})",
        r"(?:exceeded|surpassed) (?:my |our )?expectations(.{0,40})",
        r"(?:highly|definitely|would) recommend(.{0,60})",
        r"(?:can't|cannot) (?:say enough|recommend enough|stop)(.{0,60})",
    ]

    hate_markers = [
        r"(?:too |way too )(?:small|big|large|short|thin|thick|flimsy|generic)(.{0,60})",
        r"(?:fell apart|broke|damaged|ripped|torn)(.{0,60})",
        r"not enough (?:space|room|pages|prompts|options)(.{0,60})",
        r"(?:disappointed|disappointing|waste|terrible|horrible|awful)(.{0,60})",
        r"(?:returned|returning|sent back|refund)(.{0,60})",
        r"(?:cheaply|poorly) (?:made|constructed|built|designed)(.{0,60})",
        r"(?:don't|do not|wouldn't|would not) (?:buy|recommend|waste)(.{0,60})",
        r"(?:prompts|questions) (?:are |were )?(?:too |very )?(?:generic|vague|boring|repetitive)(.{0,60})",
    ]

    gap_markers = [
        r"(?:wish|wished|hoping|hope) (?:it |this |they |there )(?:had|was|were|would|could)(.{10,80})",
        r"(?:would be|it'd be) (?:nice|great|better|perfect) (?:if|to have)(.{10,80})",
        r"(?:only|my only) (?:complaint|issue|problem|concern|wish)(.{10,80})",
        r"(?:needs?|needed|missing|lacks?) (.{10,80})",
        r"(?:should have|should've|could use|could have) (.{10,80})",
        r"(?:if only|the only thing)(.{10,80})",
    ]

    gift_markers = [
        r"(?:bought|got|ordered|purchased) (?:this |it )?(?:for|as a) (?:gift |present )?(?:for )?(?:my )?(\w+.{0,40})",
        r"(?:christmas|birthday|mother'?s?\s*day|father'?s?\s*day|grandparent'?s?\s*day|anniversary|wedding|baby shower|retirement|graduation|valentine)",
        r"(?:gift|present) (?:for|to) (.{5,60})",
    ]

    emotional_markers = [
        r"(?:legacy|memories|remember|before it'?s too late|future generations|pass down|hand down)",
        r"(?:connection|connected|bonding|bond|closer|together)",
        r"(?:priceless|irreplaceable|meaningful|sentimental|heartfelt|touching)",
        r"(?:tears|crying|emotional|moved|heartwarming|heartbreaking)",
    ]

    # Process positive reviews
    for text in all_positive_text:
        for pattern in love_markers:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.strip().rstrip(".,;:!?")
                if phrase and len(phrase) > 5:
                    love_phrases.append(phrase)
                else:
                    # Use context around the match
                    full_match = re.search(pattern, text, re.IGNORECASE)
                    if full_match:
                        start = max(0, full_match.start() - 5)
                        end = min(len(text), full_match.end() + 30)
                        love_phrases.append(text[start:end].strip())

    # Process negative reviews
    for text in all_negative_text:
        for pattern in hate_markers:
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

    # Process all reviews for gaps, gifts, emotions
    all_text = all_positive_text + all_negative_text
    for text in all_text:
        for pattern in gap_markers:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.strip().rstrip(".,;:!?")
                if phrase and len(phrase) > 8:
                    gap_phrases.append(f"Customers want {phrase}")

        for pattern in gift_markers:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                gift_phrases.append(match.strip().rstrip(".,;:!?"))

        for pattern in emotional_markers:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                emotional_phrases.append(match.strip().lower())

    # Deduplicate and rank by frequency
    love_phrases = _dedupe_and_rank(love_phrases, max_items=20)
    hate_phrases = _dedupe_and_rank(hate_phrases, max_items=20)
    gap_phrases = _dedupe_and_rank(gap_phrases, max_items=15)
    emotional_triggers = _dedupe_and_rank(emotional_phrases, max_items=15)

    # Gift occasions - normalize and count
    gift_occasions = _extract_gift_occasions(all_text)

    # Buyer vs. user analysis
    buyer_user = _analyze_buyer_vs_user(all_text)

    return {
        "love_phrases": love_phrases,
        "hate_phrases": hate_phrases,
        "product_gaps": gap_phrases,
        "gift_occasions": gift_occasions,
        "buyer_vs_user": buyer_user,
        "emotional_triggers": emotional_triggers,
    }


def _dedupe_and_rank(phrases, max_items=20):
    """Deduplicate phrases (case-insensitive) and return most common ones."""
    if not phrases:
        return []

    # Normalize
    normalized = {}
    for phrase in phrases:
        key = phrase.lower().strip()
        if key not in normalized:
            normalized[key] = phrase.strip()

    # Count occurrences of the lowered version
    counts = Counter(p.lower().strip() for p in phrases)
    ranked = sorted(normalized.keys(), key=lambda k: counts.get(k, 0), reverse=True)

    return [normalized[k] for k in ranked[:max_items]]


def _extract_gift_occasions(texts):
    """Extract and normalize gift occasion mentions."""
    occasions_map = {
        "christmas": "Christmas",
        "xmas": "Christmas",
        "birthday": "Birthday",
        "mother's day": "Mother's Day",
        "mothers day": "Mother's Day",
        "father's day": "Father's Day",
        "fathers day": "Father's Day",
        "grandparent's day": "Grandparents Day",
        "grandparents day": "Grandparents Day",
        "anniversary": "Anniversary",
        "wedding": "Wedding",
        "baby shower": "Baby Shower",
        "retirement": "Retirement",
        "graduation": "Graduation",
        "valentine": "Valentine's Day",
        "valentines": "Valentine's Day",
        "easter": "Easter",
        "hanukkah": "Hanukkah",
        "chanukah": "Hanukkah",
    }

    found = Counter()
    combined = " ".join(texts).lower()
    for key, label in occasions_map.items():
        count = combined.count(key)
        if count > 0:
            found[label] += count

    return [occasion for occasion, _ in found.most_common(10)]


def _analyze_buyer_vs_user(texts):
    """Detect buyer-vs-user dynamics from review text."""
    buyer_signals = []
    user_signals = []
    mismatch_signals = []

    buyer_patterns = [
        r"(?:bought|got|ordered|purchased) (?:this |it )?(?:for|as a gift for) (?:my )?(\w[\w\s]{2,30})",
        r"(?:gave|giving) (?:this |it )?to (?:my )?(\w[\w\s]{2,30})",
    ]

    user_patterns = [
        r"(?:i|my \w+) (?:use|used|fill|filled|write|wrote|started|enjoy)(.{5,40})",
        r"(?:hard to |difficult to |easy to |fun to )(?:write|fill|use|read)(.{0,40})",
    ]

    mismatch_patterns = [
        r"(?:loved the idea|great idea|great concept) but (.{10,80})",
        r"(?:they|she|he|my \w+) (?:said|found|thinks|thought) (.{10,80})",
        r"(?:i|the buyer) (?:loved|liked) it but (?:they|she|he|my \w+)(.{10,60})",
    ]

    combined = " ".join(texts)

    for pattern in buyer_patterns:
        matches = re.findall(pattern, combined, re.IGNORECASE)
        buyer_signals.extend(matches)

    for pattern in user_patterns:
        matches = re.findall(pattern, combined, re.IGNORECASE)
        user_signals.extend(matches)

    for pattern in mismatch_patterns:
        matches = re.findall(pattern, combined, re.IGNORECASE)
        mismatch_signals.extend(matches)

    # Summarize
    buyer_roles = _dedupe_and_rank(buyer_signals, max_items=5)
    user_activities = _dedupe_and_rank(user_signals, max_items=5)
    mismatches = _dedupe_and_rank(mismatch_signals, max_items=5)

    result = {
        "buyers": ", ".join(buyer_roles) if buyer_roles else "Not enough data to determine buyer profile",
        "users": ", ".join(user_activities) if user_activities else "Not enough data to determine user profile",
        "mismatch": "; ".join(mismatches) if mismatches else "No clear buyer/user mismatch detected",
    }

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_as_markdown(data):
    """Convert JSON output to a readable markdown document."""
    lines = []
    lines.append(f"# Amazon Reviews Research: {data.get('query', 'Direct URLs')}")
    lines.append(f"")
    lines.append(f"**Generated:** {data.get('timestamp', '')}")
    lines.append(f"**Products Scraped:** {data.get('products_scraped', 0)}")
    lines.append(f"**Total Reviews Collected:** {data.get('total_reviews_collected', 0)}")
    lines.append("")

    for product in data.get("products", []):
        lines.append(f"---")
        lines.append(f"## {product.get('title', 'Unknown Product')}")
        lines.append(f"")
        lines.append(f"- **ASIN:** {product.get('asin', '')}")
        lines.append(f"- **URL:** {product.get('url', '')}")
        lines.append(f"- **Price:** {product.get('price', 'N/A')}")
        lines.append(f"- **Overall Rating:** {product.get('overall_rating', 'N/A')}")
        lines.append(f"- **Total Reviews:** {product.get('total_reviews', 'N/A')}")
        lines.append("")

        reviews = product.get("reviews", [])
        if reviews:
            lines.append(f"### Reviews ({len(reviews)} collected)")
            lines.append("")
            for i, review in enumerate(reviews, 1):
                stars = review.get("stars", "?")
                star_display = "*" * int(stars) if isinstance(stars, (int, float)) else str(stars)
                lines.append(f"**{i}. [{star_display}] {review.get('title', '')}**")
                if review.get("verified"):
                    lines.append(f"   _Verified Purchase_ | {review.get('date', '')} | {review.get('helpful_votes', 0)} helpful votes")
                else:
                    lines.append(f"   {review.get('date', '')} | {review.get('helpful_votes', 0)} helpful votes")
                lines.append(f"")
                lines.append(f"   > {review.get('text', '')[:500]}")
                lines.append("")
        lines.append("")

    # Voice analysis
    va = data.get("voice_analysis", {})
    if va:
        lines.append("---")
        lines.append("## Voice Analysis")
        lines.append("")

        if va.get("love_phrases"):
            lines.append("### Love Phrases (from 4-5 star reviews)")
            for phrase in va["love_phrases"]:
                lines.append(f'- "{phrase}"')
            lines.append("")

        if va.get("hate_phrases"):
            lines.append("### Hate Phrases (from 1-2 star reviews)")
            for phrase in va["hate_phrases"]:
                lines.append(f'- "{phrase}"')
            lines.append("")

        if va.get("product_gaps"):
            lines.append("### Product Gaps")
            for gap in va["product_gaps"]:
                lines.append(f"- {gap}")
            lines.append("")

        if va.get("gift_occasions"):
            lines.append("### Gift Occasions")
            for occasion in va["gift_occasions"]:
                lines.append(f"- {occasion}")
            lines.append("")

        bvu = va.get("buyer_vs_user", {})
        if bvu:
            lines.append("### Buyer vs. User Dynamics")
            lines.append(f"- **Buyers:** {bvu.get('buyers', 'N/A')}")
            lines.append(f"- **Users:** {bvu.get('users', 'N/A')}")
            lines.append(f"- **Mismatch:** {bvu.get('mismatch', 'N/A')}")
            lines.append("")

        if va.get("emotional_triggers"):
            lines.append("### Emotional Triggers")
            for trigger in va["emotional_triggers"]:
                lines.append(f"- {trigger}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract customer voice data from Amazon product reviews via Playwright"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--search",
        type=str,
        help="Amazon search query (finds products then scrapes reviews)",
    )
    group.add_argument(
        "--product-urls",
        nargs="+",
        help="Direct Amazon product URLs (alternative to --search)",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=3,
        help="Max products to scrape (default: 3)",
    )
    parser.add_argument(
        "--reviews-per-product",
        type=int,
        default=20,
        help="Max reviews per product (default: 20)",
    )
    parser.add_argument(
        "--stars",
        type=str,
        default="1,2,3,4,5",
        help='Comma-separated star ratings to focus on (default: "1,2,3,4,5"). Tip: "1,5" gives the most useful voice data.',
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help='Output format: "json" or "markdown" (default: "json")',
    )
    parser.add_argument(
        "--sort",
        type=str,
        choices=["recent", "helpful"],
        default="helpful",
        help='Sort reviews by "recent" or "helpful" (default: "helpful")',
    )

    args = parser.parse_args()

    # Validate playwright
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

    # Determine products to scrape
    products_to_scrape = []  # list of {title, asin, url, price, overall_rating, total_reviews}

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

        # Stealth: override navigator properties to avoid bot detection
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        page = context.new_page()

        # Block unnecessary resources to speed up scraping
        page.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}",
            lambda route: route.abort(),
        )

        try:
            # Warm up: visit Amazon homepage to establish session cookies
            # Without this, Amazon returns "Sorry! Something went wrong!" errors
            print("[main] Warming up session (visiting homepage)...", file=sys.stderr)
            try:
                page.goto("https://www.amazon.com/", wait_until="domcontentloaded", timeout=30000)
                random_delay(2, 4)
            except Exception as e:
                print(f"[main] Homepage warm-up failed: {e}", file=sys.stderr)

            if args.search:
                # Search for products
                products_to_scrape = search_products(
                    page, args.search, args.max_products
                )
                if not products_to_scrape:
                    print(
                        "[main] No products found for search query. "
                        "Try a different query or use --product-urls.",
                        file=sys.stderr,
                    )
            else:
                # Direct URLs -- just collect ASINs, we'll get info from product page
                for url in args.product_urls[: args.max_products]:
                    asin = extract_asin_from_url(url)
                    if not asin:
                        print(f"[main] Could not extract ASIN from URL: {url}", file=sys.stderr)
                        continue
                    products_to_scrape.append(
                        {
                            "title": "",
                            "asin": asin,
                            "url": f"https://www.amazon.com/dp/{asin}",
                            "price": "",
                            "overall_rating": 0,
                            "total_reviews": 0,
                        }
                    )

            # Scrape product pages for both metadata and reviews.
            # Amazon requires sign-in for /product-reviews/ pages, so we
            # extract reviews directly from the product detail page.
            # Each product page shows ~8-11 "Top reviews" without auth.
            products_data = []
            for prod in products_to_scrape:
                print(
                    f"\n[main] Scraping product page: {prod['title'][:60] or prod['asin']}... (ASIN: {prod['asin']})",
                    file=sys.stderr,
                )

                info, reviews = scrape_product_page(
                    page,
                    prod["asin"],
                    star_filters,
                    args.reviews_per_product,
                )

                products_data.append(
                    {
                        "title": info["title"] or prod["title"] or f"Product {prod['asin']}",
                        "asin": prod["asin"],
                        "url": prod["url"],
                        "price": info["price"] or prod["price"],
                        "overall_rating": info["overall_rating"] or prod["overall_rating"],
                        "total_reviews": info["total_reviews"] or prod["total_reviews"],
                        "reviews": reviews,
                    }
                )

                print(
                    f"[main] Collected {len(reviews)} reviews for {prod['asin']}",
                    file=sys.stderr,
                )
                random_delay(2, 4)

        finally:
            browser.close()

    # Voice analysis
    print("\n[main] Running voice analysis...", file=sys.stderr)
    voice = analyze_voice(products_data)

    # Build output
    total_reviews = sum(len(p.get("reviews", [])) for p in products_data)
    output_data = {
        "query": args.search or ", ".join(args.product_urls or []),
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
        f"\n[main] Done. {len(products_data)} products, {total_reviews} reviews collected.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
