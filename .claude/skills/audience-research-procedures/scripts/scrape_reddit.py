#!/usr/bin/env python3
"""Scrape Reddit for audience research data.

Usage:
    python scrape_reddit.py --subreddits "r/fitness" "r/loseit" \
        --queries "can't lose weight" "stuck at plateau" \
        --limit 50

Returns JSON array of posts with title, body, top comments, and upvotes.
Uses resolve_service.py to get API credentials for social_scraping_reddit.
Falls back gracefully if Reddit API is not configured.
"""

import argparse
import json
import subprocess
import sys
import os
from datetime import datetime


RESOLVE_SERVICE_PATH = "/var/www/vibe-marketing/scripts/resolve_service.py"


def resolve_reddit_service():
    """Resolve the social_scraping_reddit service from the registry."""
    try:
        result = subprocess.run(
            [sys.executable, RESOLVE_SERVICE_PATH, "social_scraping_reddit"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None


def search_reddit_api(service_config, subreddit, query, limit=25):
    """Search Reddit using the configured API service.

    Supports both direct Reddit API and third-party scraping services.
    """
    posts = []

    service_name = service_config.get("name", "").lower()
    base_url = service_config.get("baseUrl", "")
    api_key = service_config.get("apiKey", "")

    # Direct Reddit API (OAuth)
    if "reddit" in service_name or "oauth.reddit.com" in base_url:
        import requests

        client_id = service_config.get("clientId", api_key)
        client_secret = service_config.get("clientSecret", "")
        user_agent = service_config.get("userAgent", "vibe-marketing-researcher/1.0")

        # Get OAuth token
        auth_response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": user_agent},
            timeout=15
        )

        if auth_response.status_code != 200:
            print(f"Reddit OAuth failed: {auth_response.status_code}", file=sys.stderr)
            return posts

        token = auth_response.json().get("access_token", "")
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": user_agent
        }

        # Clean subreddit name
        sub = subreddit.replace("r/", "").strip()

        # Search the subreddit
        search_url = f"https://oauth.reddit.com/r/{sub}/search"
        params = {
            "q": query,
            "sort": "relevance",
            "limit": min(limit, 100),
            "restrict_sr": "true",
            "t": "year"
        }

        response = requests.get(search_url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Reddit search failed: {response.status_code}", file=sys.stderr)
            return posts

        data = response.json()
        for child in data.get("data", {}).get("children", []):
            post_data = child.get("data", {})
            post = {
                "subreddit": sub,
                "title": post_data.get("title", ""),
                "body": post_data.get("selftext", "")[:2000],
                "upvotes": post_data.get("ups", 0),
                "num_comments": post_data.get("num_comments", 0),
                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                "created_utc": post_data.get("created_utc", 0),
                "top_comments": []
            }

            # Fetch top comments for high-engagement posts
            if post_data.get("num_comments", 0) > 5:
                try:
                    permalink = post_data.get("permalink", "")
                    comments_url = f"https://oauth.reddit.com{permalink}"
                    comments_params = {"limit": 10, "sort": "top", "depth": 1}
                    comments_response = requests.get(
                        comments_url, headers=headers,
                        params=comments_params, timeout=10
                    )
                    if comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        if len(comments_data) > 1:
                            for comment_child in comments_data[1].get("data", {}).get("children", [])[:5]:
                                comment_data = comment_child.get("data", {})
                                if comment_data.get("body"):
                                    post["top_comments"].append({
                                        "body": comment_data["body"][:500],
                                        "upvotes": comment_data.get("ups", 0)
                                    })
                except Exception:
                    pass  # Comments are best-effort

            posts.append(post)

    # Generic scraping service fallback
    elif base_url:
        import requests

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key

        sub = subreddit.replace("r/", "").strip()
        endpoint = f"{base_url.rstrip('/')}/search"
        params = {
            "subreddit": sub,
            "query": query,
            "limit": limit
        }

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                result_data = response.json()
                # Normalize to our format
                for item in result_data if isinstance(result_data, list) else result_data.get("posts", []):
                    posts.append({
                        "subreddit": sub,
                        "title": item.get("title", ""),
                        "body": item.get("body", item.get("selftext", ""))[:2000],
                        "upvotes": item.get("upvotes", item.get("ups", 0)),
                        "num_comments": item.get("num_comments", 0),
                        "url": item.get("url", ""),
                        "created_utc": item.get("created_utc", 0),
                        "top_comments": item.get("top_comments", [])
                    })
        except Exception as e:
            print(f"Scraping service error: {e}", file=sys.stderr)

    return posts


def extract_language_patterns(posts):
    """Extract useful language patterns from Reddit posts.

    Returns phrases, emotional expressions, and identity markers.
    """
    patterns = {
        "phrases": [],
        "emotional_expressions": [],
        "identity_markers": [],
        "problem_descriptions": [],
        "frustrations": []
    }

    for post in posts:
        text_sources = [post.get("title", ""), post.get("body", "")]
        for comment in post.get("top_comments", []):
            text_sources.append(comment.get("body", ""))

        for text in text_sources:
            if not text:
                continue

            # Look for quoted speech or strong emotional language
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line or len(line) < 10:
                    continue

                # Identity markers: "as a [X], I..."
                if "as a " in line.lower() or "i'm a " in line.lower() or "i am a " in line.lower():
                    patterns["identity_markers"].append(line[:200])

                # Frustration markers
                frustration_words = ["frustrated", "annoyed", "tired of", "sick of",
                                     "hate", "can't stand", "giving up", "done with"]
                if any(word in line.lower() for word in frustration_words):
                    patterns["frustrations"].append(line[:200])

                # Problem descriptions: "I've been...", "I can't...", "I don't know..."
                problem_starters = ["i've been", "i can't", "i don't know",
                                    "i'm struggling", "i've tried", "nothing works",
                                    "why can't i", "how do i"]
                if any(line.lower().startswith(starter) or f" {starter}" in line.lower()
                       for starter in problem_starters):
                    patterns["problem_descriptions"].append(line[:200])

    # Deduplicate
    for key in patterns:
        patterns[key] = list(dict.fromkeys(patterns[key]))[:50]

    return patterns


def main():
    parser = argparse.ArgumentParser(description="Scrape Reddit for audience research")
    parser.add_argument("--subreddits", nargs="+", required=True,
                        help="Subreddit names (e.g., r/fitness r/loseit)")
    parser.add_argument("--queries", nargs="+", required=True,
                        help="Search queries to use")
    parser.add_argument("--limit", type=int, default=25,
                        help="Max results per query per subreddit (default: 25)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Resolve Reddit service
    service = resolve_reddit_service()
    if not service:
        result = {
            "status": "unavailable",
            "error": "social_scraping_reddit service not configured",
            "posts": [],
            "language_patterns": {"phrases": [], "emotional_expressions": [],
                                  "identity_markers": [], "problem_descriptions": [],
                                  "frustrations": []},
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "subreddits_requested": args.subreddits,
                "queries_requested": args.queries
            }
        }
        output = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        sys.exit(0)  # Graceful exit, not error

    # Scrape across all subreddit+query combinations
    all_posts = []
    for subreddit in args.subreddits:
        for query in args.queries:
            print(f"Searching {subreddit} for: {query}", file=sys.stderr)
            posts = search_reddit_api(service, subreddit, query, args.limit)
            all_posts.extend(posts)

    # Deduplicate by URL
    seen_urls = set()
    unique_posts = []
    for post in all_posts:
        url = post.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_posts.append(post)
        elif not url:
            unique_posts.append(post)

    # Extract language patterns
    language_patterns = extract_language_patterns(unique_posts)

    result = {
        "status": "success",
        "posts": unique_posts,
        "post_count": len(unique_posts),
        "language_patterns": language_patterns,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "subreddits_searched": args.subreddits,
            "queries_used": args.queries,
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
