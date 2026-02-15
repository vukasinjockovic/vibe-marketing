#!/usr/bin/env python3
"""Deep voice-of-customer mining from Quora questions and answers.

Usage:
    python quora_voice_mine.py --topic "grandparent loneliness" --max-questions 10 --output json

Combines question discovery + answer extraction + NLP-style analysis to build
a rich audience voice profile from Quora content. This is the most valuable
script for audience research -- it extracts the raw emotional language of
the target market.

Extracts:
- pain_phrases: Exact phrases describing problems/frustrations
- desire_phrases: Exact phrases describing wants/goals
- objection_phrases: Phrases showing resistance/doubt
- emotional_vocabulary: High-emotion words/phrases used frequently
- question_patterns: How people frame their questions
- product_mentions: Specific products, services, or solutions mentioned
- demographic_signals: Age, gender, location, life stage signals

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
# Pain phrase extraction
# ---------------------------------------------------------------------------

PAIN_MARKERS = [
    r'(?:i\s+(?:feel|felt)\s+(?:so\s+)?(?:alone|lonely|frustrated|helpless|overwhelmed|stressed|anxious|depressed|lost|stuck|confused|scared|afraid|hopeless|defeated|exhausted|burned out|burned-out)(?:[^.!?]{0,80}))',
    r'(?:(?:the\s+)?(?:biggest|worst|hardest|most\s+difficult)\s+(?:problem|challenge|issue|struggle|frustration|thing)(?:[^.!?]{0,80}))',
    r'(?:i\s+(?:struggle|struggled|can\'t|cannot|couldn\'t)\s+(?:with|to)(?:[^.!?]{0,80}))',
    r'(?:(?:it\'s|it\s+is)\s+(?:so\s+)?(?:hard|difficult|impossible|frustrating|overwhelming|confusing|stressful|painful|exhausting)\s+(?:to|when|that)(?:[^.!?]{0,80}))',
    r'(?:nobody\s+(?:understands|cares|visits|calls|listens)(?:[^.!?]{0,60}))',
    r'(?:i\s+(?:hate|can\'t\s+stand|am\s+tired\s+of|am\s+sick\s+of|am\s+fed\s+up\s+with)(?:[^.!?]{0,80}))',
    r'(?:(?:keeps?\s+me|keeps?\s+us)\s+(?:up\s+at\s+night|awake|worried|stressed)(?:[^.!?]{0,60}))',
    r'(?:i\s+(?:worry|worried)\s+(?:about|that)(?:[^.!?]{0,80}))',
]


def extract_pain_phrases(texts):
    """Extract pain point phrases from a list of text strings.

    Looks for expressions of frustration, struggle, fear, loneliness,
    and other negative emotional states.

    Args:
        texts: List of text strings to analyze.

    Returns:
        List of extracted pain phrase strings, deduplicated.
    """
    if not texts:
        return []

    phrases = []
    for text in texts:
        text_lower = text.lower()
        for pattern in PAIN_MARKERS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                cleaned = match.strip().rstrip(".,;:!?")
                if cleaned and len(cleaned) > 10:
                    phrases.append(cleaned)

    return _dedupe_phrases(phrases)


# ---------------------------------------------------------------------------
# Desire phrase extraction
# ---------------------------------------------------------------------------

DESIRE_MARKERS = [
    r'(?:i\s+(?:just\s+)?(?:want|wish|hope|dream|long)\s+(?:to|for|that)(?:[^.!?]{0,80}))',
    r'(?:(?:my\s+)?(?:biggest|greatest|main|ultimate)\s+(?:goal|dream|wish|desire|hope)(?:[^.!?]{0,80}))',
    r'(?:i\s+(?:would\s+love|\'d\s+love)\s+(?:to|if)(?:[^.!?]{0,80}))',
    r'(?:if\s+(?:only|i\s+could|there\s+was\s+a\s+way)(?:[^.!?]{0,80}))',
    r'(?:i\s+need\s+(?:to|a|something\s+that)(?:[^.!?]{0,80}))',
    r'(?:(?:looking|searching|trying)\s+(?:for|to\s+find)\s+(?:a\s+way|something|someone)(?:[^.!?]{0,80}))',
    r'(?:i\s+wish\s+(?:i|there|someone|my)(?:[^.!?]{0,80}))',
]


def extract_desire_phrases(texts):
    """Extract desire/want phrases from a list of text strings.

    Looks for expressions of wants, wishes, goals, and aspirations.

    Args:
        texts: List of text strings to analyze.

    Returns:
        List of extracted desire phrase strings, deduplicated.
    """
    if not texts:
        return []

    phrases = []
    for text in texts:
        text_lower = text.lower()
        for pattern in DESIRE_MARKERS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                cleaned = match.strip().rstrip(".,;:!?")
                if cleaned and len(cleaned) > 10:
                    phrases.append(cleaned)

    return _dedupe_phrases(phrases)


# ---------------------------------------------------------------------------
# Objection phrase extraction
# ---------------------------------------------------------------------------

OBJECTION_MARKERS = [
    r'(?:(?:but|however|though)\s+(?:technology|it|that|this)\s+(?:is\s+)?(?:so\s+)?(?:confusing|complicated|expensive|hard|difficult|risky|overwhelming|unreliable)(?:[^.!?]{0,60}))',
    r'(?:i\s+(?:don\'t|do\s+not)\s+(?:think|believe|trust|see\s+how)(?:[^.!?]{0,80}))',
    r'(?:i\'m\s+not\s+sure\s+(?:this|that|if|whether|it)(?:[^.!?]{0,80}))',
    r'(?:(?:too\s+)?(?:expensive|costly|pricey|much\s+money|old|young|late|early|complicated|complex)(?:\s+for\s+(?:me|us|someone))(?:[^.!?]{0,60}))',
    r'(?:(?:what\s+if|i\'m\s+afraid)\s+(?:it|this|that|i)(?:[^.!?]{0,80}))',
    r'(?:(?:i\s+can\'t|i\s+cannot)\s+(?:afford|justify|see\s+the\s+point|understand|figure\s+out)(?:[^.!?]{0,80}))',
    r'(?:(?:sounds?\s+)?(?:too\s+good\s+to\s+be\s+true|like\s+a\s+scam|sketchy|unreliable)(?:[^.!?]{0,60}))',
]


def extract_objection_phrases(texts):
    """Extract objection/resistance phrases from a list of text strings.

    Looks for expressions of doubt, skepticism, price resistance,
    and technology/complexity concerns.

    Args:
        texts: List of text strings to analyze.

    Returns:
        List of extracted objection phrase strings, deduplicated.
    """
    if not texts:
        return []

    phrases = []
    for text in texts:
        text_lower = text.lower()
        for pattern in OBJECTION_MARKERS:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                cleaned = match.strip().rstrip(".,;:!?")
                if cleaned and len(cleaned) > 8:
                    phrases.append(cleaned)

    return _dedupe_phrases(phrases)


# ---------------------------------------------------------------------------
# Emotional vocabulary extraction
# ---------------------------------------------------------------------------

EMOTION_WORDS = {
    # Negative high-arousal
    "devastated", "heartbroken", "terrified", "furious", "enraged", "panicked",
    "horrified", "disgusted", "desperate", "agonizing", "excruciating", "miserable",
    "shattered", "crushed", "anguished", "tormented",
    # Negative low-arousal
    "hopeless", "helpless", "numb", "empty", "lonely", "isolated",
    "forgotten", "abandoned", "worthless", "defeated", "resigned", "drained",
    # Positive high-arousal
    "ecstatic", "thrilled", "overjoyed", "elated", "euphoric", "exhilarated",
    "passionate", "inspired", "energized", "empowered", "liberated", "triumphant",
    # Positive low-arousal
    "grateful", "peaceful", "content", "blessed", "cherished", "comforted",
    "fulfilled", "appreciated", "loved", "connected", "belonging", "anchored",
    # Universal emotional
    "priceless", "irreplaceable", "heartwarming", "life-changing", "transformative",
    "breathtaking", "unforgettable", "meaningful", "sentimental", "bittersweet",
    "overwhelming", "gut-wrenching",
}


def extract_emotional_vocabulary(texts):
    """Extract high-emotion words and phrases from text.

    Scans for known emotional vocabulary words and counts their frequency.
    Returns the most frequently used emotional terms.

    Args:
        texts: List of text strings to analyze.

    Returns:
        List of emotional words/phrases sorted by frequency, deduplicated.
    """
    if not texts:
        return []

    found = Counter()
    for text in texts:
        text_lower = text.lower()
        words = re.findall(r'\b[a-z-]+\b', text_lower)
        for word in words:
            if word in EMOTION_WORDS:
                found[word] += 1

    # Also check for emotional phrases
    emotional_phrase_patterns = [
        r'broke my heart',
        r'tears? (?:of|in) (?:joy|happiness|sadness)',
        r'made me (?:cry|weep|tear up|smile|laugh)',
        r'changed my life',
        r'saved my (?:life|marriage|relationship|sanity)',
        r'wish i had (?:known|started|done)',
        r'before it\'s too late',
        r'time is running out',
        r'never too late',
        r'second chance',
    ]
    for text in texts:
        text_lower = text.lower()
        for pattern in emotional_phrase_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                found[match.strip()] += 1

    # Return sorted by frequency
    return [word for word, _ in found.most_common(30)]


# ---------------------------------------------------------------------------
# Question pattern extraction
# ---------------------------------------------------------------------------

QUESTION_PATTERN_TEMPLATES = [
    (r'is it (?:normal|okay|ok|common|possible|safe|worth) (?:to|for|that|if)', "Is it normal/okay to..."),
    (r'how do (?:i|you|we) (?:deal|cope|handle|manage|live) with', "How do I deal with..."),
    (r'what(?:\'s| is) the best (?:way|method|approach|strategy|thing) to', "What's the best way to..."),
    (r'(?:should|can|could) i (?:\w+ ){1,3}', "Should/Can I..."),
    (r'how (?:can|do|should) i (?:stop|start|begin|avoid|prevent|improve|get|find|make)', "How can I..."),
    (r'(?:why|why do|why does|why is|why are) (?:i|my|people|we|it)', "Why do/does..."),
    (r'what (?:should|can|would) i do (?:if|when|about)', "What should I do if/when..."),
    (r'(?:has|have) anyone (?:else|ever|tried|experienced|dealt with)', "Has anyone else..."),
    (r'(?:am i|are we) (?:the only|wrong|crazy|selfish|overreacting)', "Am I the only one who..."),
    (r'(?:how|what) (?:long|much|many|often|far) (?:does|should|will|can)', "How long/much..."),
]


def extract_question_patterns(texts):
    """Extract how people frame their questions.

    Identifies common question framing patterns like "Is it normal to...",
    "How do I deal with...", "What's the best way to...".

    Args:
        texts: List of text strings (questions and answer-embedded questions).

    Returns:
        List of question pattern strings found, with examples.
    """
    if not texts:
        return []

    found_patterns = []
    seen_templates = set()

    for text in texts:
        text_lower = text.lower()
        for regex, template in QUESTION_PATTERN_TEMPLATES:
            match = re.search(regex, text_lower)
            if match:
                # Extract a bit more context for the example
                start = match.start()
                end = min(len(text_lower), match.end() + 40)
                example = text_lower[start:end].strip()
                # Trim at sentence boundary
                sentence_end = re.search(r'[.!?\n]', example[match.end()-start:])
                if sentence_end:
                    example = example[:match.end()-start + sentence_end.start()]

                if template not in seen_templates:
                    seen_templates.add(template)
                    found_patterns.append(f"{template} (e.g., \"{example.strip()}\")")

    return found_patterns


# ---------------------------------------------------------------------------
# Product mention extraction
# ---------------------------------------------------------------------------

def extract_product_mentions_from_texts(texts):
    """Extract product and service mentions from combined texts.

    Uses the same logic as quora_answers.extract_product_mentions
    but operates on a list of texts.

    Args:
        texts: List of text strings.

    Returns:
        List of unique product/brand mentions.
    """
    # Import from sibling module if possible, otherwise inline
    try:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, scripts_dir)
        from quora_answers import extract_product_mentions
        all_mentions = []
        for text in texts:
            all_mentions.extend(extract_product_mentions(text))
    except ImportError:
        # Fallback: basic brand detection
        BRANDS = [
            "Amazon", "Google", "YouTube", "FaceTime", "Skype", "WhatsApp",
            "Facebook", "Instagram", "Zoom", "Apple", "Samsung", "Alexa",
            "Kindle", "iPad", "iPhone", "Netflix", "Spotify",
        ]
        all_mentions = []
        for text in texts:
            for brand in BRANDS:
                if re.search(r'\b' + re.escape(brand) + r'\b', text, re.IGNORECASE):
                    all_mentions.append(brand)

    # Deduplicate
    seen = set()
    unique = []
    for m in all_mentions:
        if m.lower() not in seen:
            seen.add(m.lower())
            unique.append(m)
    return unique


# ---------------------------------------------------------------------------
# Demographic signal extraction
# ---------------------------------------------------------------------------

def extract_demographic_signals(texts):
    """Extract demographic information from self-descriptions in text.

    Identifies age ranges, gender, roles (parent, grandparent, teacher),
    location hints, and life stage signals.

    Args:
        texts: List of text strings.

    Returns:
        Dict with age_signals, gender_signals, role_signals,
        location_signals, life_stage_signals.
    """
    result = {
        "age_signals": [],
        "gender_signals": [],
        "role_signals": [],
        "location_signals": [],
        "life_stage_signals": [],
    }

    if not texts:
        return result

    combined = " ".join(texts).lower()

    # Age signals
    age_patterns = [
        (r'\b(\d{2})\s*[-]?\s*year\s*[-]?\s*old\b', "age"),
        (r'\bin my (\d{2})s\b', "decade"),
        (r'\b(teenager|teen|twenties|thirties|forties|fifties|sixties|seventies|eighties|nineties)\b', "age_word"),
        (r'\b(young adult|middle[- ]aged?|elderly|senior|retired|retiree)\b', "stage"),
    ]
    for pattern, kind in age_patterns:
        matches = re.findall(pattern, combined)
        for match in matches:
            if kind == "age":
                result["age_signals"].append(f"{match}-year-old")
            elif kind == "decade":
                result["age_signals"].append(f"in {match}s")
            else:
                result["age_signals"].append(match)

    # Gender signals
    gender_patterns = [
        (r'\b(?:as a|i\'?m a|i am a)\s+(man|woman|male|female|guy|girl|lady|gentleman)\b', "gender"),
        (r'\b(?:my husband|my wife|my boyfriend|my girlfriend)\b', "relationship"),
    ]
    for pattern, kind in gender_patterns:
        matches = re.findall(pattern, combined)
        for match in matches:
            result["gender_signals"].append(match)

    # Role signals
    role_patterns = [
        r'\b(?:as a|i\'?m a|i am a|being a)\s+(mother|father|parent|grandparent|grandmother|grandfather|grandma|grandpa|teacher|doctor|nurse|engineer|student|caregiver|spouse|single parent)\b',
        r'\b(?:mother of|father of|parent of|grandparent of)\s+(\w+)\b',
    ]
    for pattern in role_patterns:
        matches = re.findall(pattern, combined)
        for match in matches:
            result["role_signals"].append(match)

    # Life stage signals
    life_stage_patterns = [
        r'\b(retired|retiring|retirement)\b',
        r'\b(newlywed|newly married|just married)\b',
        r'\b(new parent|new mom|new dad|new baby|pregnant|expecting)\b',
        r'\b(empty nester|kids? (?:left|moved out|went to college))\b',
        r'\b(widow|widower|lost my (?:husband|wife|spouse|partner))\b',
        r'\b(divorced|separation|single again)\b',
        r'\b(college student|graduate student|grad school|undergrad)\b',
        r'\b(career change|job hunting|unemployed|laid off)\b',
    ]
    for pattern in life_stage_patterns:
        matches = re.findall(pattern, combined)
        for match in matches:
            if match not in result["life_stage_signals"]:
                result["life_stage_signals"].append(match)

    # Deduplicate all lists
    for key in result:
        result[key] = list(dict.fromkeys(result[key]))

    return result


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_results(topic, voice_data, questions_analyzed):
    """Format voice mining results for output.

    Args:
        topic: The search topic string.
        voice_data: Dict with pain_phrases, desire_phrases, etc.
        questions_analyzed: Number of questions analyzed.

    Returns:
        Dict with topic, timestamp, questions_analyzed, and voice_data.
    """
    return {
        "topic": topic,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "questions_analyzed": questions_analyzed,
        "voice_data": voice_data,
    }


def format_markdown(output_data):
    """Convert voice mining results to readable Markdown."""
    lines = []
    lines.append(f"# Quora Voice Mining: {output_data['topic']}")
    lines.append("")
    lines.append(f"**Generated:** {output_data['timestamp']}")
    lines.append(f"**Questions Analyzed:** {output_data['questions_analyzed']}")
    lines.append("")

    vd = output_data.get("voice_data", {})

    if vd.get("pain_phrases"):
        lines.append("## Pain Phrases")
        lines.append("*Exact phrases describing problems and frustrations*")
        lines.append("")
        for phrase in vd["pain_phrases"]:
            lines.append(f'- "{phrase}"')
        lines.append("")

    if vd.get("desire_phrases"):
        lines.append("## Desire Phrases")
        lines.append("*Exact phrases describing wants and goals*")
        lines.append("")
        for phrase in vd["desire_phrases"]:
            lines.append(f'- "{phrase}"')
        lines.append("")

    if vd.get("objection_phrases"):
        lines.append("## Objection Phrases")
        lines.append("*Phrases showing resistance and doubt*")
        lines.append("")
        for phrase in vd["objection_phrases"]:
            lines.append(f'- "{phrase}"')
        lines.append("")

    if vd.get("emotional_vocabulary"):
        lines.append("## Emotional Vocabulary")
        lines.append("*High-emotion words and phrases used frequently*")
        lines.append("")
        for word in vd["emotional_vocabulary"]:
            lines.append(f"- {word}")
        lines.append("")

    if vd.get("question_patterns"):
        lines.append("## Question Patterns")
        lines.append("*How people frame their questions*")
        lines.append("")
        for pattern in vd["question_patterns"]:
            lines.append(f"- {pattern}")
        lines.append("")

    if vd.get("product_mentions"):
        lines.append("## Product/Service Mentions")
        for mention in vd["product_mentions"]:
            lines.append(f"- {mention}")
        lines.append("")

    ds = vd.get("demographic_signals", {})
    if any(ds.values()):
        lines.append("## Demographic Signals")
        if ds.get("age_signals"):
            lines.append(f"- **Age:** {', '.join(ds['age_signals'])}")
        if ds.get("gender_signals"):
            lines.append(f"- **Gender:** {', '.join(ds['gender_signals'])}")
        if ds.get("role_signals"):
            lines.append(f"- **Roles:** {', '.join(ds['role_signals'])}")
        if ds.get("life_stage_signals"):
            lines.append(f"- **Life Stage:** {', '.join(ds['life_stage_signals'])}")
        if ds.get("location_signals"):
            lines.append(f"- **Location:** {', '.join(ds['location_signals'])}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dedupe_phrases(phrases, max_items=30):
    """Deduplicate phrases by lowercase match, return top N."""
    if not phrases:
        return []
    seen = set()
    unique = []
    for phrase in phrases:
        key = phrase.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(phrase.strip())
    return unique[:max_items]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    """Create argparse parser for quora_voice_mine CLI."""
    parser = argparse.ArgumentParser(
        description="Deep voice-of-customer mining from Quora questions and answers. "
                    "Extracts pain points, desires, objections, emotional language, "
                    "question patterns, product mentions, and demographic signals."
    )
    parser.add_argument(
        "--topic", required=True,
        help="Topic to mine voice data for (e.g., 'grandparent loneliness')"
    )
    parser.add_argument(
        "--max-questions", type=int, default=10,
        help="Maximum questions to analyze (default: 10)"
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

    # Import sibling modules for question discovery and answer extraction
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    from quora_questions import (
        search_quora_via_brave, search_quora_via_google, add_share_param,
    )
    from quora_answers import (
        parse_answer_element, _dismiss_login_modal, _scroll_and_expand,
    )

    # Step 1: Find Quora question URLs
    print(f"[search] Searching for Quora questions about: {args.topic}", file=sys.stderr)
    urls = search_quora_via_brave(args.topic, max_results=args.max_questions * 2)
    if not urls:
        print("[search] Brave API not available, falling back to Google...", file=sys.stderr)
        urls = search_quora_via_google(args.topic, max_results=args.max_questions * 2)

    urls = urls[:args.max_questions]

    if not urls:
        print("[search] No Quora questions found.", file=sys.stderr)
        empty_voice = {
            "pain_phrases": [],
            "desire_phrases": [],
            "objection_phrases": [],
            "emotional_vocabulary": [],
            "question_patterns": [],
            "product_mentions": [],
            "demographic_signals": {},
        }
        output = format_results(args.topic, empty_voice, 0)
        if args.output == "markdown":
            print(format_markdown(output))
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        sys.exit(0)

    print(f"[search] Found {len(urls)} Quora URLs to analyze", file=sys.stderr)

    # Step 2: Extract all text from questions and answers
    all_question_texts = []
    all_answer_texts = []
    questions_processed = 0

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
            for i, url in enumerate(urls):
                share_url = add_share_param(url)
                print(f"[extract] ({i+1}/{len(urls)}) Loading: {share_url}", file=sys.stderr)

                try:
                    page.goto(share_url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(random.uniform(3, 5))

                    _dismiss_login_modal(page)

                    # Extract question title
                    question_title = ""
                    for sel in ['.q-box.qu-userSelect--text', 'h1 span', 'h1']:
                        el = page.query_selector(sel)
                        if el:
                            question_title = el.inner_text().strip()
                            if question_title:
                                break

                    if question_title:
                        all_question_texts.append(question_title)
                        print(f"[extract] Question: {question_title[:60]}...", file=sys.stderr)

                    # Scroll and expand to load answers
                    _scroll_and_expand(page, max_answers=10)

                    # Extract answer text
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

                    for el in answer_elements[:10]:
                        ans = parse_answer_element(el)
                        if ans and ans.get("text"):
                            all_answer_texts.append(ans["text"])
                            # Also capture author credentials for demographic signals
                            if ans.get("author_credentials"):
                                all_answer_texts.append(ans["author_credentials"])

                    questions_processed += 1
                    print(f"[extract] Got {len(answer_elements)} answers", file=sys.stderr)

                except Exception as e:
                    print(f"[extract] Error processing {url}: {e}", file=sys.stderr)

                time.sleep(random.uniform(2, 4))

        finally:
            browser.close()

    # Step 3: Analyze all collected text
    all_texts = all_question_texts + all_answer_texts
    print(f"\n[analysis] Analyzing {len(all_texts)} text fragments...", file=sys.stderr)

    voice_data = {
        "pain_phrases": extract_pain_phrases(all_texts),
        "desire_phrases": extract_desire_phrases(all_texts),
        "objection_phrases": extract_objection_phrases(all_texts),
        "emotional_vocabulary": extract_emotional_vocabulary(all_texts),
        "question_patterns": extract_question_patterns(all_question_texts + all_answer_texts),
        "product_mentions": extract_product_mentions_from_texts(all_texts),
        "demographic_signals": extract_demographic_signals(all_texts),
    }

    # Step 4: Output
    output = format_results(args.topic, voice_data, questions_processed)

    if args.output == "markdown":
        print(format_markdown(output))
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))

    print(f"\n[main] Done. Analyzed {questions_processed} questions.", file=sys.stderr)
    print(f"[main] Found: {len(voice_data['pain_phrases'])} pain phrases, "
          f"{len(voice_data['desire_phrases'])} desire phrases, "
          f"{len(voice_data['objection_phrases'])} objection phrases, "
          f"{len(voice_data['emotional_vocabulary'])} emotional words", file=sys.stderr)


if __name__ == "__main__":
    main()
