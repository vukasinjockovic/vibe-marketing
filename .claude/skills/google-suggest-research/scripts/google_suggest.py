#!/usr/bin/env python3
"""Query Google Autocomplete/Suggest API to discover real search queries.

Usage:
    python google_suggest.py --seed-keywords "grandparent gift" "wedding planner" \
        --expand-alphabet \
        --expand-questions \
        --output json

Returns JSON or Markdown with all discovered suggestions, grouped by expansion type.
No API key needed. Uses only stdlib (urllib).
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter
from datetime import datetime, timezone


SUGGEST_URL = "http://suggestqueries.google.com/complete/search"

QUESTION_PREFIXES = [
    "what", "how", "why", "when", "where", "which", "who", "is", "can", "does"
]

PREPOSITION_SUFFIXES = [
    "for", "with", "without", "vs", "near", "like"
]

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

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
}


def fetch_suggestions(query, lang="en", country="us", max_retries=3):
    """Fetch autocomplete suggestions from Google for a single query.

    Returns a list of suggestion strings. Retries with exponential backoff
    on rate limiting (HTTP 429).
    """
    params = urllib.parse.urlencode({
        "client": "firefox",
        "q": query,
        "hl": lang,
        "gl": country,
    })
    url = f"{SUGGEST_URL}?{params}"

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                if isinstance(data, list) and len(data) >= 2:
                    return data[1]
                return []
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (2 ** attempt) * 1.0
                print(f"  Rate limited (429). Backing off {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                print(f"  HTTP error {e.code} for query '{query}'", file=sys.stderr)
                return []
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  Error fetching '{query}': {e}", file=sys.stderr)
            return []

    print(f"  Giving up on '{query}' after {max_retries} retries", file=sys.stderr)
    return []


def expand_seed(seed, lang, country, do_alphabet, do_questions, do_prepositions, delay):
    """Expand a single seed keyword with all requested expansion strategies.

    Returns a dict with direct, alphabet_expansions, question_expansions,
    and preposition_expansions results.
    """
    result = {
        "direct": [],
        "alphabet_expansions": {},
        "question_expansions": {},
        "preposition_expansions": {},
    }

    # Direct suggestions
    print(f"Fetching: {seed}...", file=sys.stderr)
    result["direct"] = fetch_suggestions(seed, lang, country)
    time.sleep(delay)

    # Alphabet expansion: "seed a", "seed b", ...
    if do_alphabet:
        print(f"  Alphabet expanding '{seed}'...", file=sys.stderr)
        for letter in ALPHABET:
            query = f"{seed} {letter}"
            print(f"  Fetching: {query}...", file=sys.stderr)
            suggestions = fetch_suggestions(query, lang, country)
            if suggestions:
                result["alphabet_expansions"][letter] = suggestions
            time.sleep(delay)

    # Question expansion: "what seed", "how seed", ...
    if do_questions:
        print(f"  Question expanding '{seed}'...", file=sys.stderr)
        for prefix in QUESTION_PREFIXES:
            query = f"{prefix} {seed}"
            print(f"  Fetching: {query}...", file=sys.stderr)
            suggestions = fetch_suggestions(query, lang, country)
            if suggestions:
                result["question_expansions"][prefix] = suggestions
            time.sleep(delay)

    # Preposition expansion: "seed for", "seed with", ...
    if do_prepositions:
        print(f"  Preposition expanding '{seed}'...", file=sys.stderr)
        for suffix in PREPOSITION_SUFFIXES:
            query = f"{seed} {suffix}"
            print(f"  Fetching: {query}...", file=sys.stderr)
            suggestions = fetch_suggestions(query, lang, country)
            if suggestions:
                result["preposition_expansions"][suffix] = suggestions
            time.sleep(delay)

    return result


def collect_all_suggestions(results):
    """Flatten all suggestions from all seeds into a single deduplicated list."""
    seen = set()
    unique = []
    for seed, data in results.items():
        for s in data.get("direct", []):
            lower = s.lower()
            if lower not in seen:
                seen.add(lower)
                unique.append(s)
        for group in ("alphabet_expansions", "question_expansions", "preposition_expansions"):
            for key, suggestions in data.get(group, {}).items():
                for s in suggestions:
                    lower = s.lower()
                    if lower not in seen:
                        seen.add(lower)
                        unique.append(s)
    return unique


def extract_top_themes(all_suggestions, seed_keywords):
    """Extract common themes/words from all suggestions.

    Groups words into categories based on frequency, excluding seed words
    and common stopwords.
    """
    # Build set of seed words to exclude
    seed_words = set()
    for kw in seed_keywords:
        for w in kw.lower().split():
            seed_words.add(w)

    # Count all non-seed, non-stopword tokens
    word_counts = Counter()
    for suggestion in all_suggestions:
        words = suggestion.lower().split()
        for word in words:
            word = word.strip(".,!?()[]\"'")
            if word and word not in STOPWORDS and word not in seed_words and len(word) > 1:
                word_counts[word] += 1

    # Only keep words that appear 2+ times
    frequent = {w: c for w, c in word_counts.items() if c >= 2}

    # Sort by frequency descending, take top 30
    top_words = sorted(frequent.items(), key=lambda x: -x[1])[:30]

    # Simple heuristic grouping
    occasions = []
    product_types = []
    modifiers = []
    actions = []
    other = []

    occasion_hints = {
        "christmas", "birthday", "wedding", "anniversary", "baby",
        "shower", "holiday", "valentines", "mother", "father",
        "graduation", "easter", "thanksgiving", "housewarming",
        "retirement", "funeral", "memorial", "day", "year", "new",
    }
    modifier_hints = {
        "best", "unique", "homemade", "cheap", "luxury", "personalized",
        "custom", "funny", "cute", "creative", "easy", "simple", "quick",
        "free", "top", "great", "good", "popular", "cool", "small",
        "big", "large", "mini", "diy", "handmade", "special", "perfect",
        "affordable", "expensive", "premium", "budget",
    }
    action_hints = {
        "buy", "make", "find", "get", "choose", "order", "send",
        "plan", "create", "design", "build", "give", "ship",
    }

    for word, count in top_words:
        if word in occasion_hints:
            occasions.append(word)
        elif word in modifier_hints:
            modifiers.append(word)
        elif word in action_hints:
            actions.append(word)
        else:
            # Guess product type vs other
            product_types.append(word)

    themes = {}
    if occasions:
        themes["occasions"] = occasions
    if product_types:
        themes["product_types"] = product_types
    if modifiers:
        themes["modifiers"] = modifiers
    if actions:
        themes["actions"] = actions
    if other:
        themes["other"] = other

    return themes


def format_markdown(output_data):
    """Convert the JSON output structure to readable Markdown."""
    lines = []
    lines.append(f"# Google Suggest Research")
    lines.append(f"")
    lines.append(f"**Generated:** {output_data['timestamp']}")
    lines.append(f"**Seeds:** {', '.join(output_data['seed_keywords'])}")
    lines.append(f"**Total unique suggestions:** {output_data['total_suggestions']}")
    lines.append("")

    for seed, data in output_data["results"].items():
        lines.append(f"## Seed: {seed}")
        lines.append("")

        if data["direct"]:
            lines.append("### Direct Suggestions")
            for s in data["direct"]:
                lines.append(f"- {s}")
            lines.append("")

        if data["alphabet_expansions"]:
            lines.append("### Alphabet Expansions")
            for letter, suggestions in sorted(data["alphabet_expansions"].items()):
                lines.append(f"**{letter.upper()}:** {', '.join(suggestions)}")
            lines.append("")

        if data["question_expansions"]:
            lines.append("### Question Expansions")
            for prefix, suggestions in data["question_expansions"].items():
                lines.append(f"**{prefix}:**")
                for s in suggestions:
                    lines.append(f"- {s}")
            lines.append("")

        if data["preposition_expansions"]:
            lines.append("### Preposition Expansions")
            for suffix, suggestions in data["preposition_expansions"].items():
                lines.append(f"**{suffix}:**")
                for s in suggestions:
                    lines.append(f"- {s}")
            lines.append("")

    if output_data.get("top_themes"):
        lines.append("## Top Themes")
        lines.append("")
        for category, words in output_data["top_themes"].items():
            lines.append(f"**{category.replace('_', ' ').title()}:** {', '.join(words)}")
        lines.append("")

    if output_data.get("all_unique_suggestions"):
        lines.append("## All Unique Suggestions")
        lines.append("")
        for s in output_data["all_unique_suggestions"]:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Query Google Autocomplete to discover real search queries. "
                    "Free, no API key needed."
    )
    parser.add_argument(
        "--seed-keywords", nargs="+", required=True,
        help="1-10 seed keywords to expand (e.g., 'grandparent gift' 'wedding planner')"
    )
    parser.add_argument(
        "--expand-alphabet", action="store_true",
        help="Query 'seed a', 'seed b', ... 'seed z' for long-tail discovery"
    )
    parser.add_argument(
        "--expand-questions", action="store_true",
        help="Query 'what seed', 'how seed', 'why seed', etc. for FAQ/intent discovery"
    )
    parser.add_argument(
        "--expand-prepositions", action="store_true",
        help="Query 'seed for', 'seed with', 'seed vs', etc."
    )
    parser.add_argument(
        "--output", choices=["json", "markdown"], default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--lang", default="en",
        help="Language code (default: en)"
    )
    parser.add_argument(
        "--country", default="us",
        help="Country code for localization (default: us)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.3,
        help="Delay between requests in seconds (default: 0.3)"
    )

    args = parser.parse_args()

    if len(args.seed_keywords) > 10:
        print("Error: Maximum 10 seed keywords allowed.", file=sys.stderr)
        sys.exit(1)

    # Expand each seed
    results = {}
    for seed in args.seed_keywords:
        seed = seed.strip()
        if not seed:
            continue
        results[seed] = expand_seed(
            seed,
            lang=args.lang,
            country=args.country,
            do_alphabet=args.expand_alphabet,
            do_questions=args.expand_questions,
            do_prepositions=args.expand_prepositions,
            delay=args.delay,
        )

    # Collect all unique suggestions
    all_unique = collect_all_suggestions(results)

    # Extract themes
    top_themes = extract_top_themes(all_unique, args.seed_keywords)

    # Build output
    output_data = {
        "seed_keywords": args.seed_keywords,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_suggestions": len(all_unique),
        "results": results,
        "all_unique_suggestions": all_unique,
        "top_themes": top_themes,
    }

    if args.output == "markdown":
        print(format_markdown(output_data))
    else:
        print(json.dumps(output_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
