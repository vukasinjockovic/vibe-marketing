#!/usr/bin/env python3
"""Scrape customer reviews and testimonials for audience research.

Usage:
    python scrape_reviews.py --product "GymZilla Training Program" \
        --competitor-urls "https://competitor1.com" "https://competitor2.com"

Returns JSON with aggregated pain points, language patterns, and satisfaction themes.
Uses resolve_service.py to get web_scraping service credentials.
Falls back gracefully if web scraping is not configured.
"""

import argparse
import json
import subprocess
import sys
import os
from datetime import datetime


RESOLVE_SERVICE_PATH = "/var/www/vibe-marketing/scripts/resolve_service.py"


def resolve_scraping_service():
    """Resolve the web_scraping service from the registry."""
    try:
        result = subprocess.run(
            [sys.executable, RESOLVE_SERVICE_PATH, "web_scraping"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def scrape_url(service_config, url, extract_type="reviews"):
    """Scrape a URL using the configured web scraping service.

    Supports Crawl4AI (self-hosted) and Firecrawl (cloud).
    """
    service_name = service_config.get("name", "").lower()
    base_url = service_config.get("baseUrl", "")
    api_key = service_config.get("apiKey", "")

    try:
        import requests
    except ImportError:
        print("requests library required. Install with: pip install requests", file=sys.stderr)
        return None

    # Crawl4AI (self-hosted at localhost:11235)
    if "crawl4ai" in service_name or "localhost:11235" in base_url:
        endpoint = f"{base_url.rstrip('/')}/crawl"
        payload = {
            "urls": [url],
            "priority": 5,
            "extraction_config": {
                "type": "json_css",
                "params": {
                    "schema": {
                        "name": "reviews",
                        "baseSelector": "body",
                        "fields": [
                            {"name": "text_content", "selector": "body", "type": "text"}
                        ]
                    }
                }
            },
            "crawler_params": {
                "headless": True,
                "page_timeout": 30000,
                "word_count_threshold": 50
            }
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return {
                    "url": url,
                    "content": data.get("results", [{}])[0].get("markdown", "")
                        if data.get("results") else "",
                    "status": "success"
                }
        except Exception as e:
            print(f"Crawl4AI error for {url}: {e}", file=sys.stderr)
            return None

    # Firecrawl (cloud service)
    elif "firecrawl" in service_name or "api.firecrawl.dev" in base_url:
        endpoint = f"{base_url.rstrip('/')}/v0/scrape"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "url": url,
            "pageOptions": {"onlyMainContent": True}
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return {
                    "url": url,
                    "content": data.get("data", {}).get("markdown", ""),
                    "status": "success"
                }
        except Exception as e:
            print(f"Firecrawl error for {url}: {e}", file=sys.stderr)
            return None

    # Generic scraping service
    elif base_url:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        try:
            endpoint = f"{base_url.rstrip('/')}/scrape"
            payload = {"url": url}
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return {
                    "url": url,
                    "content": data.get("content", data.get("markdown", data.get("text", ""))),
                    "status": "success"
                }
        except Exception as e:
            print(f"Generic scraper error for {url}: {e}", file=sys.stderr)
            return None

    return None


def extract_review_themes(scraped_content):
    """Extract themes from scraped review/testimonial content.

    Does basic text analysis to categorize content into themes.
    The agent (opus model) will do deeper analysis -- this provides structure.
    """
    if not scraped_content:
        return {}

    content = scraped_content.lower()

    themes = {
        "satisfaction_signals": [],
        "pain_points": [],
        "language_samples": [],
        "demographic_signals": [],
        "feature_mentions": [],
        "competitor_mentions": [],
        "emotional_expressions": [],
        "objection_patterns": []
    }

    lines = scraped_content.split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 15:
            continue

        lower_line = line.lower()

        # Satisfaction signals
        satisfaction_words = ["love", "amazing", "best", "finally", "game changer",
                              "life changing", "recommend", "worth it", "exceeded"]
        if any(word in lower_line for word in satisfaction_words):
            themes["satisfaction_signals"].append(line[:300])

        # Pain points
        pain_words = ["frustrated", "disappointed", "waste", "doesn't work",
                      "overpriced", "confusing", "difficult", "poor", "terrible",
                      "wished", "wish it", "if only", "lacking"]
        if any(word in lower_line for word in pain_words):
            themes["pain_points"].append(line[:300])

        # Emotional expressions
        emotional_words = ["scared", "worried", "anxious", "excited", "thrilled",
                           "nervous", "overwhelmed", "relieved", "grateful",
                           "hopeful", "desperate"]
        if any(word in lower_line for word in emotional_words):
            themes["emotional_expressions"].append(line[:300])

        # Objection patterns
        objection_markers = ["too expensive", "not sure", "hesitant", "skeptical",
                             "almost didn't", "thought about", "on the fence",
                             "worried that", "concerned about"]
        if any(marker in lower_line for marker in objection_markers):
            themes["objection_patterns"].append(line[:300])

        # Demographic signals
        demo_markers = ["as a mom", "as a dad", "as a student", "in my 30s",
                        "in my 40s", "in my 50s", "in my 20s", "working professional",
                        "stay at home", "retired", "busy schedule", "full-time"]
        if any(marker in lower_line for marker in demo_markers):
            themes["demographic_signals"].append(line[:300])

        # Competitor mentions
        competitor_markers = ["switched from", "compared to", "better than",
                              "worse than", "used to use", "came from", "tried"]
        if any(marker in lower_line for marker in competitor_markers):
            themes["competitor_mentions"].append(line[:300])

    # Deduplicate and limit
    for key in themes:
        themes[key] = list(dict.fromkeys(themes[key]))[:30]

    return themes


def main():
    parser = argparse.ArgumentParser(description="Scrape reviews for audience research")
    parser.add_argument("--product", required=True,
                        help="Product name for context")
    parser.add_argument("--competitor-urls", nargs="+", default=[],
                        help="Competitor URLs to scrape for testimonials")
    parser.add_argument("--review-urls", nargs="*", default=[],
                        help="Direct URLs to review pages (G2, Capterra, Trustpilot)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Resolve scraping service
    service = resolve_scraping_service()
    if not service:
        result = {
            "status": "unavailable",
            "error": "web_scraping service not configured",
            "product": args.product,
            "scraped_pages": [],
            "aggregated_themes": {},
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "urls_requested": args.competitor_urls + args.review_urls
            }
        }
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        sys.exit(0)  # Graceful exit

    # Scrape all URLs
    all_urls = args.competitor_urls + args.review_urls
    scraped_pages = []
    all_themes = {
        "satisfaction_signals": [],
        "pain_points": [],
        "language_samples": [],
        "demographic_signals": [],
        "feature_mentions": [],
        "competitor_mentions": [],
        "emotional_expressions": [],
        "objection_patterns": []
    }

    for url in all_urls:
        print(f"Scraping: {url}", file=sys.stderr)
        page_result = scrape_url(service, url)

        if page_result and page_result.get("status") == "success":
            content = page_result.get("content", "")
            themes = extract_review_themes(content)

            scraped_pages.append({
                "url": url,
                "content_length": len(content),
                "themes_found": {k: len(v) for k, v in themes.items()},
                "raw_content_excerpt": content[:2000]  # First 2000 chars for agent review
            })

            # Merge themes
            for key in all_themes:
                all_themes[key].extend(themes.get(key, []))
        else:
            scraped_pages.append({
                "url": url,
                "content_length": 0,
                "themes_found": {},
                "error": "Failed to scrape"
            })

    # Deduplicate aggregated themes
    for key in all_themes:
        all_themes[key] = list(dict.fromkeys(all_themes[key]))[:50]

    result = {
        "status": "success",
        "product": args.product,
        "scraped_pages": scraped_pages,
        "pages_scraped": len([p for p in scraped_pages if p.get("content_length", 0) > 0]),
        "pages_failed": len([p for p in scraped_pages if p.get("error")]),
        "aggregated_themes": all_themes,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "urls_processed": all_urls,
            "service_used": service.get("name", "unknown")
        }
    }

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
