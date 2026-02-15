#!/usr/bin/env python3
"""Find Quora questions via web search + Playwright extraction.

Usage:
    python quora_questions.py --topic "grandparent gifts" --max-questions 20 --output json

Strategy:
    1. Build a site:quora.com search query
    2. Search via Brave Search API (or fall back to Google via urllib)
    3. Extract Quora question URLs from results
    4. Visit each URL with Playwright, appending ?share=1 to bypass login wall
    5. Extract question metadata (title, description, answer count, followers, etc.)
    6. Output sorted by engagement (followers + upvotes)

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
import os
import urllib.request
import urllib.parse
import urllib.error
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

# Paths that are NOT question pages on Quora
NON_QUESTION_PATH_PREFIXES = [
    "/topic/",
    "/profile/",
    "/space/",
    "/about",
    "/contact",
    "/privacy",
    "/tos",
    "/press",
    "/careers",
    "/answer/",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_delay(min_sec=3.0, max_sec=5.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def build_search_query(topic):
    """Build a site:quora.com search query for finding Quora question pages.

    Args:
        topic: The topic to search for.

    Returns:
        A search query string like 'site:quora.com "grandparent gifts"'.
    """
    topic = topic.strip()
    return f'site:quora.com "{topic}"' if topic else 'site:quora.com'


def extract_quora_urls(html):
    """Extract unique Quora question URLs from search result HTML.

    Filters out topic pages, profile pages, and other non-question URLs.
    Deduplicates by normalized URL.

    Args:
        html: Raw HTML string from a search results page.

    Returns:
        List of unique Quora question URL strings.
    """
    if not html:
        return []

    # Find all Quora URLs in the HTML
    pattern = r'https?://(?:www\.)?quora\.com/[A-Za-z0-9_-]+'
    raw_urls = re.findall(pattern, html)

    seen = set()
    urls = []
    for url in raw_urls:
        # Normalize
        url = url.rstrip("/")
        if not url.startswith("https://"):
            url = url.replace("http://", "https://")
        if "www.quora.com" not in url:
            url = url.replace("quora.com", "www.quora.com")

        # Parse path
        parsed = urllib.parse.urlparse(url)
        path = parsed.path

        # Filter out non-question pages
        is_question = True
        for prefix in NON_QUESTION_PATH_PREFIXES:
            if path.startswith(prefix):
                is_question = False
                break

        # Root path is not a question
        if path == "/" or path == "":
            is_question = False

        if not is_question:
            continue

        # Deduplicate
        norm_key = parsed.netloc + parsed.path
        if norm_key in seen:
            continue
        seen.add(norm_key)
        urls.append(url)

    return urls


def add_share_param(url):
    """Add ?share=1 to a Quora URL to bypass the login wall.

    If the URL already has share=1, returns it unchanged.
    Preserves any existing query parameters.

    Args:
        url: A Quora URL string.

    Returns:
        The URL with share=1 appended.
    """
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)

    if "share" in params:
        return url

    # Add share=1
    if parsed.query:
        new_query = parsed.query + "&share=1"
    else:
        new_query = "share=1"

    new_parsed = parsed._replace(query=new_query)
    return urllib.parse.urlunparse(new_parsed)


def search_quora_via_brave(topic, max_results=30):
    """Search for Quora questions using the Brave Search API.

    Requires BRAVE_API_KEY environment variable.

    Args:
        topic: Search topic.
        max_results: Maximum number of URLs to return.

    Returns:
        List of Quora question URLs, or empty list if API unavailable.
    """
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return []

    query = build_search_query(topic)
    params = urllib.parse.urlencode({
        "q": query,
        "count": min(max_results, 20),
    })
    url = f"https://api.search.brave.com/res/v1/web/search?{params}"

    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = data.get("web", {}).get("results", [])
            urls = []
            for r in results:
                link = r.get("url", "")
                if "quora.com/" in link:
                    urls.append(link)
            return extract_quora_urls("\n".join(f'<a href="{u}">' for u in urls))
    except Exception as e:
        print(f"[search] Brave Search API error: {e}", file=sys.stderr)
        return []


def search_quora_via_google(topic, max_results=30):
    """Search for Quora questions using Google Search via urllib.

    Args:
        topic: Search topic.
        max_results: Maximum number of URLs to return.

    Returns:
        List of Quora question URLs.
    """
    query = build_search_query(topic)
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={min(max_results, 30)}"

    try:
        req = urllib.request.Request(search_url, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
            return extract_quora_urls(html)
    except Exception as e:
        print(f"[search] Google Search error: {e}", file=sys.stderr)
        return []


def parse_question_page(page):
    """Extract question metadata from a loaded Quora question page.

    Args:
        page: A Playwright page object with a Quora question loaded.

    Returns:
        Dict with question_title, url, description, answer_count,
        follower_count, upvote_count, tags, date_asked.
    """
    result = {
        "question_title": "",
        "url": page.url,
        "description": "",
        "answer_count": 0,
        "follower_count": 0,
        "upvote_count": 0,
        "tags": [],
        "date_asked": "",
    }

    try:
        # Try to dismiss login modal if present
        try:
            page.evaluate("""
                // Remove login modal overlay
                document.querySelectorAll('.q-box.qu-overflowHidden').forEach(el => el.remove());
                document.querySelectorAll('[class*="modal"], [class*="Modal"], [class*="signup"], [class*="login"]').forEach(el => {
                    if (el.style) { el.style.display = 'none'; }
                });
                // Re-enable scrolling
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
            """)
        except Exception:
            pass

        # Question title - try multiple selectors
        title_selectors = [
            '.q-box.qu-userSelect--text',
            '[class*="question_title"]',
            '.puppeteer_test_question_title',
            'h1 span',
            'h1',
            '.q-text[class*="bold"]',
        ]
        for sel in title_selectors:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and len(text) > 5:
                    result["question_title"] = text
                    break

        # Fall back to page title
        if not result["question_title"]:
            page_title = page.title()
            if page_title:
                # Remove " - Quora" suffix
                result["question_title"] = re.sub(r'\s*[-|]\s*Quora\s*$', '', page_title).strip()

        # Question description/details
        desc_selectors = [
            '[class*="question_details"]',
            '.q-box.qu-userSelect--text + .q-box',
        ]
        for sel in desc_selectors:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and text != result["question_title"]:
                    result["description"] = text
                    break

        # Answer count - count answer elements on the page
        answer_selectors = [
            '[class*="Answer"]',
            '.q-box.qu-borderAll',
            '[class*="answer"]',
        ]
        for sel in answer_selectors:
            answers = page.query_selector_all(sel)
            if answers:
                result["answer_count"] = len(answers)
                break

        # Try extracting answer count from text like "42 Answers"
        try:
            text_content = page.evaluate("document.body.innerText")
            answer_match = re.search(r'(\d+)\s+[Aa]nswers?', text_content)
            if answer_match:
                count = int(answer_match.group(1))
                if count > result["answer_count"]:
                    result["answer_count"] = count
        except Exception:
            pass

        # Follower count
        try:
            text_content = page.evaluate("document.body.innerText") if not text_content else text_content
            follower_match = re.search(r'(\d[\d,]*)\s+[Ff]ollowers?', text_content)
            if follower_match:
                result["follower_count"] = int(follower_match.group(1).replace(",", ""))
        except Exception:
            pass

        # Upvote count
        try:
            upvote_match = re.search(r'(\d[\d,]*)\s+[Uu]pvotes?', text_content)
            if upvote_match:
                result["upvote_count"] = int(upvote_match.group(1).replace(",", ""))
        except Exception:
            pass

        # Tags/topics
        tag_selectors = [
            '[class*="topic"] a',
            '.q-box a[href*="/topic/"]',
        ]
        for sel in tag_selectors:
            tag_els = page.query_selector_all(sel)
            if tag_els:
                for tag_el in tag_els[:10]:
                    try:
                        tag_text = tag_el.inner_text().strip()
                        if tag_text and tag_text not in result["tags"]:
                            result["tags"].append(tag_text)
                    except Exception:
                        pass
                break

    except Exception as e:
        print(f"[parse] Error parsing question page: {e}", file=sys.stderr)

    return result


def format_results(topic, questions):
    """Format question results for output.

    Sorts questions by engagement (follower_count + upvote_count descending).

    Args:
        topic: The search topic string.
        questions: List of question dicts.

    Returns:
        Dict with topic, timestamp, total_questions, and sorted questions list.
    """
    # Sort by engagement
    sorted_questions = sorted(
        questions,
        key=lambda q: q.get("follower_count", 0) + q.get("upvote_count", 0),
        reverse=True,
    )

    return {
        "topic": topic,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_questions": len(sorted_questions),
        "questions": sorted_questions,
    }


def format_markdown(output_data):
    """Convert JSON output to readable Markdown.

    Args:
        output_data: The dict from format_results().

    Returns:
        Markdown string.
    """
    lines = []
    lines.append(f"# Quora Questions Research: {output_data['topic']}")
    lines.append("")
    lines.append(f"**Generated:** {output_data['timestamp']}")
    lines.append(f"**Total Questions Found:** {output_data['total_questions']}")
    lines.append("")

    for i, q in enumerate(output_data["questions"], 1):
        lines.append(f"## {i}. {q.get('question_title', 'Unknown')}")
        lines.append("")
        lines.append(f"- **URL:** {q.get('url', '')}")
        lines.append(f"- **Answers:** {q.get('answer_count', 0)}")
        lines.append(f"- **Followers:** {q.get('follower_count', 0)}")
        lines.append(f"- **Upvotes:** {q.get('upvote_count', 0)}")
        if q.get("tags"):
            lines.append(f"- **Tags:** {', '.join(q['tags'])}")
        if q.get("description"):
            lines.append(f"- **Details:** {q['description'][:200]}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for quora_questions CLI."""
    parser = argparse.ArgumentParser(
        description="Find Quora questions via web search + Playwright extraction. "
                    "Discovers question URLs via Brave Search or Google, then extracts "
                    "metadata from each question page."
    )
    parser.add_argument(
        "--topic", required=True,
        help="Topic to search for (e.g., 'grandparent gifts')"
    )
    parser.add_argument(
        "--max-questions", type=int, default=20,
        help="Maximum number of questions to extract (default: 20)"
    )
    parser.add_argument(
        "--output", choices=["json", "markdown"], default="json",
        help="Output format (default: json)"
    )
    return parser


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
    parser = create_parser()
    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    from playwright.sync_api import sync_playwright

    # Step 1: Find Quora question URLs via search
    print(f"[search] Searching for Quora questions about: {args.topic}", file=sys.stderr)

    quora_urls = search_quora_via_brave(args.topic, max_results=args.max_questions * 2)
    if not quora_urls:
        print("[search] Brave API not available, falling back to Google...", file=sys.stderr)
        quora_urls = search_quora_via_google(args.topic, max_results=args.max_questions * 2)

    if not quora_urls:
        print("[search] No Quora question URLs found. Try a different topic.", file=sys.stderr)
        output = format_results(args.topic, [])
        if args.output == "markdown":
            print(format_markdown(output))
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        sys.exit(0)

    print(f"[search] Found {len(quora_urls)} Quora URLs", file=sys.stderr)

    # Limit to max_questions
    quora_urls = quora_urls[:args.max_questions]

    # Step 2: Extract question data from each URL
    questions = []

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
            },
        )

        # Stealth overrides
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        # Block heavy resources
        page.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}",
            lambda route: route.abort(),
        )

        try:
            for i, url in enumerate(quora_urls):
                share_url = add_share_param(url)
                print(f"[extract] ({i+1}/{len(quora_urls)}) Loading: {share_url}", file=sys.stderr)

                try:
                    page.goto(share_url, wait_until="domcontentloaded", timeout=30000)
                    random_delay(3, 5)

                    # Scroll to load content
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                    time.sleep(1)

                    question = parse_question_page(page)
                    if question and question.get("question_title"):
                        questions.append(question)
                        print(f"[extract] Got: {question['question_title'][:60]}...", file=sys.stderr)
                    else:
                        print(f"[extract] Could not extract question data from {url}", file=sys.stderr)

                except Exception as e:
                    print(f"[extract] Error loading {url}: {e}", file=sys.stderr)

        finally:
            browser.close()

    # Step 3: Output results
    output = format_results(args.topic, questions)

    if args.output == "markdown":
        print(format_markdown(output))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"\n[main] Done. {len(questions)} questions extracted.", file=sys.stderr)


if __name__ == "__main__":
    main()
