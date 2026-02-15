#!/usr/bin/env python3
"""Extract answers from Quora question pages via Playwright.

Usage:
    python quora_answers.py --url "https://www.quora.com/What-is-the-best-gift-for-grandparents" \
        --max-answers 10 --output json

    python quora_answers.py --topic "wedding planning tips" \
        --max-questions 5 --answers-per-question 5 --output json

Strategy:
    - URL mode: Load a single Quora question page and extract answers.
    - Topic mode: Search for Quora questions (reuses quora_questions logic),
      then extract answers from the top questions.
    - Appends ?share=1 to bypass Quora login wall.
    - Detects persuasion patterns (personal stories, authority, recommendations).
    - Extracts product/service mentions and links from answers.

Requires: pip install playwright && python -m playwright install chromium
"""

import argparse
import json
import re
import sys
import time
import random
import os
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

# Well-known product/service/brand names to detect in answers
KNOWN_BRANDS = [
    "Amazon", "Grammarly", "Canva", "Shopify", "WordPress", "Wix",
    "Squarespace", "Mailchimp", "HubSpot", "Salesforce", "Slack",
    "Zoom", "Google", "YouTube", "FaceTime", "Skype", "WhatsApp",
    "Facebook", "Instagram", "TikTok", "LinkedIn", "Twitter", "Reddit",
    "Etsy", "eBay", "Walmart", "Target", "Costco", "Netflix",
    "Spotify", "Apple", "Samsung", "Nike", "Adidas", "Peloton",
    "Fitbit", "Garmin", "Ring", "Nest", "Alexa", "Siri",
    "ChatGPT", "Notion", "Trello", "Asana", "Monday.com",
    "Calendly", "Stripe", "PayPal", "Venmo", "QuickBooks",
    "Audible", "Kindle", "iPad", "iPhone",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_delay(min_sec=3.0, max_sec=5.0):
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def detect_persuasion_patterns(text):
    """Detect persuasion patterns used in a Quora answer.

    Identifies:
    - personal_story: Author shares a personal anecdote
    - authority: Author cites credentials or expertise
    - specific_recommendation: Author recommends a specific product/service
    - social_proof: References to what many people do or think
    - data_evidence: Uses numbers, statistics, or research

    Args:
        text: The answer text string.

    Returns:
        List of pattern name strings detected (e.g., ["personal_story", "authority"]).
    """
    if not text:
        return []

    patterns = []
    text_lower = text.lower()

    # Personal story patterns
    personal_story_markers = [
        r'\b(?:when i|i was|i had|i found|i tried|i personally|my experience|in my case)\b',
        r'\b(?:i remember|i once|i used to|years ago i|back when i)\b',
        r'\b(?:happened to me|my story|let me tell you|let me share)\b',
    ]
    for marker in personal_story_markers:
        if re.search(marker, text_lower):
            patterns.append("personal_story")
            break

    # Authority patterns
    authority_markers = [
        r'\b(?:as a|i am a|i\'m a)\s+(?:doctor|lawyer|engineer|professor|expert|specialist|certified|licensed|therapist|advisor|consultant|researcher|scientist|teacher|nurse|coach)\b',
        r'\b(?:\d+\s+years?\s+(?:of\s+)?experience|decades?\s+of\s+experience)\b',
        r'\b(?:in my professional|professionally speaking|from a professional)\b',
        r'\b(?:with a degree|with a phd|with my expertise|board certified)\b',
    ]
    for marker in authority_markers:
        if re.search(marker, text_lower):
            patterns.append("authority")
            break

    # Specific recommendation patterns
    recommendation_markers = [
        r'\b(?:i recommend|i highly recommend|i would recommend|i suggest|i\'d suggest)\b',
        r'\b(?:you should (?:try|use|get|buy|check out|look into))\b',
        r'\b(?:the best (?:option|choice|solution|product|tool|service) is)\b',
        r'\b(?:definitely (?:try|use|get|check out))\b',
    ]
    for marker in recommendation_markers:
        if re.search(marker, text_lower):
            patterns.append("specific_recommendation")
            break

    # Social proof patterns
    social_proof_markers = [
        r'\b(?:most people|many people|everyone i know|a lot of people)\b',
        r'\b(?:widely used|widely recommended|popular choice|commonly)\b',
        r'\b(?:millions of|thousands of|hundreds of)\s+(?:people|users|customers)\b',
    ]
    for marker in social_proof_markers:
        if re.search(marker, text_lower):
            patterns.append("social_proof")
            break

    # Data/evidence patterns
    data_markers = [
        r'\b(?:according to|research shows|studies show|data shows|evidence suggests)\b',
        r'\b(?:statistics|a study|survey)\b.*\b(?:found|shows|indicates|revealed)\b',
        r'\b\d+(?:\.\d+)?%\b',
    ]
    for marker in data_markers:
        if re.search(marker, text_lower):
            patterns.append("data_evidence")
            break

    return patterns


def extract_product_mentions(text):
    """Extract product, service, and brand mentions from answer text.

    Checks against a list of known brands and also looks for patterns
    that indicate product recommendations (e.g., capitalized multi-word names).

    Args:
        text: The answer text string.

    Returns:
        List of product/brand name strings found.
    """
    if not text:
        return []

    mentions = []

    # Check known brands
    for brand in KNOWN_BRANDS:
        if re.search(r'\b' + re.escape(brand) + r'\b', text, re.IGNORECASE):
            mentions.append(brand)

    # Look for capitalized product-like names (e.g., "Blue Apron", "Dollar Shave Club")
    capitalized_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
    caps_matches = re.findall(capitalized_pattern, text)
    for match in caps_matches:
        # Filter out common sentence starters and generic phrases
        if match.lower() not in {
            "the best", "in my", "i would", "you should", "for the",
            "this is", "it was", "there are", "if you", "one of",
        } and match not in mentions and len(match) > 3:
            # Heuristic: if it appears near recommendation words, likely a product
            context_window = text[max(0, text.find(match) - 50):text.find(match) + len(match) + 50]
            rec_context = re.search(
                r'\b(?:recommend|try|use|buy|get|check out|called|app|tool|product|service|software|platform)\b',
                context_window,
                re.IGNORECASE,
            )
            if rec_context:
                mentions.append(match)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for m in mentions:
        if m.lower() not in seen:
            seen.add(m.lower())
            unique.append(m)

    return unique


def extract_links(text):
    """Extract URLs from text.

    Args:
        text: Text that may contain URLs.

    Returns:
        List of URL strings.
    """
    if not text:
        return []
    pattern = r'https?://[^\s<>"\')\]]+(?:\([^\s<>"\')\]]*\))?[^\s<>"\')\],.]'
    return re.findall(pattern, text)


def parse_answer_element(element):
    """Extract data from a single Quora answer DOM element.

    Args:
        element: A Playwright element handle for an answer container.

    Returns:
        Dict with text, author_name, author_credentials, upvote_count,
        date, product_mentions, links, persuasion_patterns.
    """
    result = {
        "text": "",
        "author_name": "",
        "author_credentials": "",
        "upvote_count": 0,
        "date": "",
        "product_mentions": [],
        "links": [],
        "persuasion_patterns": [],
    }

    try:
        # Answer text - try multiple selectors
        text_selectors = [
            '.q-box.qu-userSelect--text span',
            '[class*="answer_content"] span',
            '.q-text span',
        ]
        for sel in text_selectors:
            el = element.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and len(text) > 10:
                    result["text"] = text
                    break

        # Fall back to element's own text
        if not result["text"]:
            try:
                full_text = element.inner_text().strip()
                if full_text:
                    result["text"] = full_text
            except Exception:
                pass

        # Author name
        author_selectors = [
            '[class*="user"] a',
            '.q-box a[href*="/profile/"]',
            'a[class*="user_name"]',
        ]
        for sel in author_selectors:
            el = element.query_selector(sel)
            if el:
                result["author_name"] = el.inner_text().strip()
                break

        # Author credentials
        cred_selectors = [
            '[class*="credential"]',
            '.q-box [class*="credential"]',
            '[class*="bio"]',
        ]
        for sel in cred_selectors:
            el = element.query_selector(sel)
            if el:
                result["author_credentials"] = el.inner_text().strip()
                break

        # Upvote count
        upvote_selectors = [
            '[class*="upvote"] [class*="count"]',
            'button[class*="upvote"]',
            '[aria-label*="upvote"]',
        ]
        for sel in upvote_selectors:
            el = element.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                match = re.search(r'(\d[\d,.]*[KkMm]?)', text)
                if match:
                    result["upvote_count"] = _parse_count(match.group(1))
                break

        # Links in the answer
        link_els = element.query_selector_all('a[href]')
        for link_el in link_els:
            try:
                href = link_el.get_attribute("href")
                if href and href.startswith("http") and "quora.com" not in href:
                    result["links"].append(href)
            except Exception:
                pass

        # Analyze text for patterns
        if result["text"]:
            result["persuasion_patterns"] = detect_persuasion_patterns(result["text"])
            result["product_mentions"] = extract_product_mentions(result["text"])

    except Exception as e:
        print(f"[parse] Error parsing answer: {e}", file=sys.stderr)

    return result


def _parse_count(text):
    """Parse a count string like '1.2K' or '42' into an integer."""
    if not text:
        return 0
    text = text.strip().upper().replace(",", "")
    multiplier = 1
    if text.endswith("K"):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith("M"):
        multiplier = 1000000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def format_results(url, question_title, answers):
    """Format answer results for output.

    Args:
        url: The Quora question URL.
        question_title: The question title string.
        answers: List of answer dicts.

    Returns:
        Dict with url, question, timestamp, total_answers, and answers list.
    """
    return {
        "url": url,
        "question": question_title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_answers": len(answers),
        "answers": answers,
    }


def format_results_topic(topic, question_answers):
    """Format results for topic mode (multiple questions with answers).

    Args:
        topic: The search topic.
        question_answers: List of dicts, each with question_title, url, answers.

    Returns:
        Dict with topic, timestamp, questions list.
    """
    total = sum(len(qa.get("answers", [])) for qa in question_answers)
    return {
        "topic": topic,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_questions": len(question_answers),
        "total_answers": total,
        "questions": question_answers,
    }


def format_markdown(output_data):
    """Convert output to readable Markdown."""
    lines = []

    if "topic" in output_data:
        lines.append(f"# Quora Answers Research: {output_data['topic']}")
        lines.append("")
        lines.append(f"**Generated:** {output_data['timestamp']}")
        lines.append(f"**Questions:** {output_data['total_questions']}")
        lines.append(f"**Total Answers:** {output_data['total_answers']}")
        lines.append("")

        for qa in output_data.get("questions", []):
            lines.append(f"## {qa.get('question_title', 'Unknown')}")
            lines.append(f"**URL:** {qa.get('url', '')}")
            lines.append("")
            _format_answers_md(lines, qa.get("answers", []))
    else:
        lines.append(f"# Quora Answers: {output_data.get('question', '')}")
        lines.append("")
        lines.append(f"**URL:** {output_data.get('url', '')}")
        lines.append(f"**Generated:** {output_data['timestamp']}")
        lines.append(f"**Total Answers:** {output_data['total_answers']}")
        lines.append("")
        _format_answers_md(lines, output_data.get("answers", []))

    return "\n".join(lines)


def _format_answers_md(lines, answers):
    """Format a list of answers into markdown lines."""
    for i, ans in enumerate(answers, 1):
        author = ans.get("author_name", "Anonymous")
        creds = ans.get("author_credentials", "")
        lines.append(f"### Answer {i} - {author}")
        if creds:
            lines.append(f"*{creds}*")
        lines.append(f"- **Upvotes:** {ans.get('upvote_count', 0)}")
        if ans.get("persuasion_patterns"):
            lines.append(f"- **Persuasion Patterns:** {', '.join(ans['persuasion_patterns'])}")
        if ans.get("product_mentions"):
            lines.append(f"- **Products Mentioned:** {', '.join(ans['product_mentions'])}")
        lines.append("")
        text = ans.get("text", "")[:500]
        lines.append(f"> {text}")
        lines.append("")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for quora_answers CLI."""
    parser = argparse.ArgumentParser(
        description="Extract answers from Quora question pages via Playwright."
    )
    parser.add_argument(
        "--url", type=str,
        help="Quora question URL to extract answers from"
    )
    parser.add_argument(
        "--topic", type=str,
        help="Topic to search for (finds questions first, then extracts answers)"
    )
    parser.add_argument(
        "--max-answers", type=int, default=10,
        help="Max answers per question in URL mode (default: 10)"
    )
    parser.add_argument(
        "--max-questions", type=int, default=5,
        help="Max questions to process in topic mode (default: 5)"
    )
    parser.add_argument(
        "--answers-per-question", type=int, default=5,
        help="Max answers per question in topic mode (default: 5)"
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


def _add_share_param(url):
    """Add ?share=1 to URL."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    if "share" in params:
        return url
    new_query = (parsed.query + "&share=1") if parsed.query else "share=1"
    return urllib.parse.urlunparse(parsed._replace(query=new_query))


def _dismiss_login_modal(page):
    """Try to dismiss Quora's login modal."""
    try:
        page.evaluate("""
            document.querySelectorAll('.q-box.qu-overflowHidden').forEach(el => el.remove());
            document.querySelectorAll('[class*="modal"], [class*="Modal"], [class*="signup"], [class*="login"]').forEach(el => {
                if (el.style) { el.style.display = 'none'; }
            });
            document.body.style.overflow = 'auto';
            document.documentElement.style.overflow = 'auto';
        """)
    except Exception:
        pass


def _scroll_and_expand(page, max_answers):
    """Scroll down and click 'More Answers' / expand collapsed answers."""
    for scroll_pct in [0.3, 0.5, 0.7, 0.85, 1.0]:
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {scroll_pct})")
        time.sleep(1)

    # Try to click "More Answers" or "Continue Reading" buttons
    expand_selectors = [
        'button:has-text("More Answers")',
        'a:has-text("More Answers")',
        'button:has-text("Continue Reading")',
        '[class*="more_answers"]',
    ]
    for sel in expand_selectors:
        try:
            buttons = page.query_selector_all(sel)
            for btn in buttons[:3]:
                btn.click()
                time.sleep(1.5)
        except Exception:
            pass

    # Expand collapsed "Show more" in answers
    try:
        show_more = page.query_selector_all('button:has-text("more"), [class*="truncated"]')
        for btn in show_more[:max_answers]:
            try:
                btn.click()
                time.sleep(0.5)
            except Exception:
                pass
    except Exception:
        pass


def _extract_answers_from_page(page, max_answers):
    """Extract answer elements from the current Quora page."""
    _dismiss_login_modal(page)
    _scroll_and_expand(page, max_answers)

    # Find answer containers
    answer_selectors = [
        '[class*="Answer"]:not([class*="AnswerHeader"])',
        '.q-box[class*="answer"]',
        '[class*="AnswerBase"]',
    ]

    answer_elements = []
    for sel in answer_selectors:
        answer_elements = page.query_selector_all(sel)
        if answer_elements:
            break

    answers = []
    for el in answer_elements[:max_answers]:
        ans = parse_answer_element(el)
        if ans and ans.get("text"):
            answers.append(ans)

    return answers


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.url and not args.topic:
        print("ERROR: Must specify either --url or --topic", file=sys.stderr)
        sys.exit(1)

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
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()
        page.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2,ttf,eot}",
            lambda route: route.abort(),
        )

        try:
            if args.url:
                # URL mode: single question
                share_url = _add_share_param(args.url)
                print(f"[main] Loading: {share_url}", file=sys.stderr)
                page.goto(share_url, wait_until="domcontentloaded", timeout=30000)
                random_delay(3, 5)

                # Get question title
                question_title = ""
                title_el = page.query_selector('.q-box.qu-userSelect--text, h1 span, h1')
                if title_el:
                    question_title = title_el.inner_text().strip()
                if not question_title:
                    question_title = re.sub(r'\s*[-|]\s*Quora\s*$', '', page.title()).strip()

                answers = _extract_answers_from_page(page, args.max_answers)
                output = format_results(args.url, question_title, answers)

                if args.output == "markdown":
                    print(format_markdown(output))
                else:
                    print(json.dumps(output, indent=2, ensure_ascii=False))

                print(f"\n[main] Done. {len(answers)} answers extracted.", file=sys.stderr)

            else:
                # Topic mode: find questions then extract answers
                # Import question-finding logic
                scripts_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, scripts_dir)
                from quora_questions import search_quora_via_brave, search_quora_via_google, add_share_param as qs_share

                print(f"[main] Searching for Quora questions about: {args.topic}", file=sys.stderr)
                urls = search_quora_via_brave(args.topic, max_results=args.max_questions * 2)
                if not urls:
                    urls = search_quora_via_google(args.topic, max_results=args.max_questions * 2)

                urls = urls[:args.max_questions]
                question_answers = []

                for i, url in enumerate(urls):
                    share_url = _add_share_param(url)
                    print(f"[main] ({i+1}/{len(urls)}) Loading: {share_url}", file=sys.stderr)

                    try:
                        page.goto(share_url, wait_until="domcontentloaded", timeout=30000)
                        random_delay(3, 5)

                        question_title = ""
                        title_el = page.query_selector('.q-box.qu-userSelect--text, h1 span, h1')
                        if title_el:
                            question_title = title_el.inner_text().strip()
                        if not question_title:
                            question_title = re.sub(r'\s*[-|]\s*Quora\s*$', '', page.title()).strip()

                        answers = _extract_answers_from_page(page, args.answers_per_question)
                        question_answers.append({
                            "question_title": question_title,
                            "url": url,
                            "answers": answers,
                        })
                        print(f"[main] Got {len(answers)} answers for: {question_title[:60]}", file=sys.stderr)

                    except Exception as e:
                        print(f"[main] Error processing {url}: {e}", file=sys.stderr)

                output = format_results_topic(args.topic, question_answers)
                if args.output == "markdown":
                    print(format_markdown(output))
                else:
                    print(json.dumps(output, indent=2, ensure_ascii=False))

                total = sum(len(qa.get("answers", [])) for qa in question_answers)
                print(f"\n[main] Done. {len(question_answers)} questions, {total} answers.", file=sys.stderr)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
