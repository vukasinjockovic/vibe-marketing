#!/usr/bin/env python3
"""Analyze competitor websites for audience intelligence.

Usage:
    python analyze_competitors.py \
        --urls "https://competitor1.com" "https://competitor2.com" \
        --product-name "My Product"

Scrapes competitor marketing copy (headlines, value props, testimonials).
Extracts target audience signals, messaging angles, and USPs.
Returns JSON competitive analysis.
Uses resolve_service.py for web_scraping service discovery.
"""

import argparse
import json
import subprocess
import sys
import os
import re
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


def scrape_url(service_config, url):
    """Scrape a URL using the configured web scraping service."""
    service_name = service_config.get("name", "").lower()
    base_url = service_config.get("baseUrl", "")
    api_key = service_config.get("apiKey", "")

    try:
        import requests
    except ImportError:
        print("requests library required. Install with: pip install requests", file=sys.stderr)
        return None

    # Crawl4AI (self-hosted)
    if "crawl4ai" in service_name or "localhost:11235" in base_url:
        endpoint = f"{base_url.rstrip('/')}/crawl"
        payload = {
            "urls": [url],
            "priority": 5,
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
                results = data.get("results", [{}])
                return results[0].get("markdown", "") if results else ""
        except Exception as e:
            print(f"Crawl4AI error for {url}: {e}", file=sys.stderr)

    # Firecrawl (cloud)
    elif "firecrawl" in service_name or "api.firecrawl.dev" in base_url:
        endpoint = f"{base_url.rstrip('/')}/v0/scrape"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"url": url, "pageOptions": {"onlyMainContent": True}}

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("markdown", "")
        except Exception as e:
            print(f"Firecrawl error for {url}: {e}", file=sys.stderr)

    # Generic
    elif base_url:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        try:
            endpoint = f"{base_url.rstrip('/')}/scrape"
            response = requests.post(endpoint, json={"url": url}, headers=headers, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data.get("content", data.get("markdown", data.get("text", "")))
        except Exception as e:
            print(f"Scraper error for {url}: {e}", file=sys.stderr)

    return None


def analyze_marketing_content(content, url):
    """Extract audience intelligence from marketing page content.

    Identifies headlines, value props, testimonials, target audience signals,
    and messaging patterns. The agent will do deeper analysis; this provides
    structured extraction.
    """
    if not content:
        return {
            "url": url,
            "status": "no_content",
            "headlines": [],
            "value_propositions": [],
            "testimonials": [],
            "audience_signals": [],
            "messaging_angles": [],
            "pricing_signals": [],
            "faq_topics": [],
            "cta_text": []
        }

    analysis = {
        "url": url,
        "status": "analyzed",
        "content_length": len(content),
        "headlines": [],
        "value_propositions": [],
        "testimonials": [],
        "audience_signals": [],
        "messaging_angles": [],
        "pricing_signals": [],
        "faq_topics": [],
        "cta_text": []
    }

    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        lower_line = line.lower()

        # Headlines (markdown headings or short impactful lines)
        if line.startswith("#") or (len(line) < 120 and not line.endswith(".")):
            clean = line.lstrip("#").strip()
            if clean and len(clean) > 10:
                analysis["headlines"].append(clean[:200])

        # Testimonials (quoted text or review-like patterns)
        if (line.startswith('"') and line.endswith('"')) or \
           (line.startswith("'") and line.endswith("'")) or \
           " - " in line and any(w in lower_line for w in ["great", "love", "best", "changed"]):
            analysis["testimonials"].append(line[:300])

        # Audience targeting signals
        audience_markers = ["for professionals", "for beginners", "for teams",
                            "for small business", "for enterprise", "for creators",
                            "designed for", "built for", "made for", "perfect for",
                            "ideal for", "whether you", "if you're a"]
        if any(marker in lower_line for marker in audience_markers):
            analysis["audience_signals"].append(line[:300])

        # Value propositions
        value_markers = ["save time", "save money", "increase", "reduce", "eliminate",
                         "automate", "simplify", "streamline", "boost", "grow",
                         "transform", "achieve", "unlock", "discover"]
        if any(marker in lower_line for marker in value_markers):
            analysis["value_propositions"].append(line[:300])

        # Pricing signals
        price_markers = ["$", "per month", "per year", "/mo", "/yr", "free",
                         "starter", "pro plan", "enterprise", "pricing",
                         "free trial", "money back", "guarantee"]
        if any(marker in lower_line for marker in price_markers):
            analysis["pricing_signals"].append(line[:300])

        # FAQ topics
        if "?" in line and len(line) < 200:
            analysis["faq_topics"].append(line[:200])

        # CTA text
        cta_markers = ["get started", "sign up", "try free", "start now",
                       "join now", "learn more", "book a demo", "start trial",
                       "download", "claim your", "get your"]
        if any(marker in lower_line for marker in cta_markers):
            analysis["cta_text"].append(line[:200])

        # Messaging angles (problem-solution framing)
        problem_solution = ["tired of", "stop wasting", "no more", "say goodbye",
                            "finally", "imagine", "what if", "instead of"]
        if any(marker in lower_line for marker in problem_solution):
            analysis["messaging_angles"].append(line[:300])

    # Deduplicate all lists
    for key in analysis:
        if isinstance(analysis[key], list):
            analysis[key] = list(dict.fromkeys(analysis[key]))[:25]

    # Add raw content excerpt for agent's own analysis
    analysis["raw_content_excerpt"] = content[:3000]

    return analysis


def generate_competitive_summary(analyses, product_name):
    """Generate a summary across all competitor analyses."""
    summary = {
        "product_name": product_name,
        "competitors_analyzed": len(analyses),
        "common_value_props": [],
        "common_audience_signals": [],
        "messaging_gaps": [],
        "pricing_landscape": [],
        "common_objections_addressed": []
    }

    all_value_props = []
    all_audience_signals = []
    all_pricing = []
    all_faq = []

    for analysis in analyses:
        all_value_props.extend(analysis.get("value_propositions", []))
        all_audience_signals.extend(analysis.get("audience_signals", []))
        all_pricing.extend(analysis.get("pricing_signals", []))
        all_faq.extend(analysis.get("faq_topics", []))

    # Find recurring themes (appear in multiple competitors)
    def find_recurring(items, min_count=2):
        """Find themes that appear across multiple items."""
        word_counts = {}
        for item in items:
            words = set(item.lower().split())
            for word in words:
                if len(word) > 4:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        return [w for w, c in sorted(word_counts.items(), key=lambda x: -x[1])
                if c >= min_count][:20]

    summary["common_themes"] = find_recurring(all_value_props)
    summary["common_audience_signals"] = list(dict.fromkeys(all_audience_signals))[:20]
    summary["pricing_landscape"] = list(dict.fromkeys(all_pricing))[:15]
    summary["common_objections_addressed"] = list(dict.fromkeys(all_faq))[:20]

    return summary


def main():
    parser = argparse.ArgumentParser(description="Analyze competitor websites")
    parser.add_argument("--urls", nargs="+", required=True,
                        help="Competitor website URLs to analyze")
    parser.add_argument("--product-name", required=True,
                        help="Your product name (for context)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Resolve scraping service
    service = resolve_scraping_service()
    if not service:
        result = {
            "status": "unavailable",
            "error": "web_scraping service not configured",
            "product_name": args.product_name,
            "analyses": [],
            "summary": {},
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "urls_requested": args.urls
            }
        }
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        sys.exit(0)  # Graceful exit

    # Scrape and analyze each competitor
    analyses = []
    for url in args.urls:
        print(f"Analyzing competitor: {url}", file=sys.stderr)
        content = scrape_url(service, url)
        analysis = analyze_marketing_content(content, url)
        analyses.append(analysis)

    # Generate cross-competitor summary
    summary = generate_competitive_summary(analyses, args.product_name)

    result = {
        "status": "success",
        "product_name": args.product_name,
        "analyses": analyses,
        "summary": summary,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "urls_processed": args.urls,
            "service_used": service.get("name", "unknown"),
            "successful_scrapes": len([a for a in analyses if a.get("status") == "analyzed"]),
            "failed_scrapes": len([a for a in analyses if a.get("status") != "analyzed"])
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
