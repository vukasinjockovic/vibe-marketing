#!/usr/bin/env python3
"""Scrape construction article content via Crawl4AI and save as markdown.

Reads pending URLs from SQLite (populated by discover-construction-urls.sh),
scrapes via Crawl4AI (localhost:11235), saves as markdown with YAML frontmatter.

Usage:
    python3 scrape-construction-content.py                          # Scrape all pending
    python3 scrape-construction-content.py --domain fixr.com        # Single domain
    python3 scrape-construction-content.py --limit 50               # First N articles
    python3 scrape-construction-content.py --delay 10               # Override rate limit
    python3 scrape-construction-content.py --status                 # Show progress
    python3 scrape-construction-content.py --retry-failed           # Re-attempt failures
    python3 scrape-construction-content.py --dry-run                # Preview only
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

# ─── Config ─────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_FILE = PROJECT_DIR / "knowledge" / "construction" / "web-archives" / "url-inventory.db"
OUTPUT_DIR = PROJECT_DIR / "knowledge" / "construction" / "blogs"
DOMAINS_JSON = SCRIPT_DIR / "config" / "domains.json"

CRAWL4AI_URL = "http://localhost:11235"
CRAWL4AI_ENDPOINT = f"{CRAWL4AI_URL}/crawl"

DEFAULT_DELAY = 3
DEFAULT_MIN_WORDS = 200

# ─── Domain Config ──────────────────────────────────────────────────────────────

def load_domain_config():
    """Load domain configs from domains.json."""
    if DOMAINS_JSON.exists():
        with open(DOMAINS_JSON) as f:
            return json.load(f)
    return {}

def get_domain_delay(domain, domain_configs, override=None):
    """Get scrape delay for a domain."""
    if override is not None:
        return override
    cfg = domain_configs.get(domain, {})
    return cfg.get("scrape_delay", DEFAULT_DELAY)

def get_domain_min_words(domain, domain_configs):
    """Get minimum word count for a domain."""
    cfg = domain_configs.get(domain, {})
    return cfg.get("scrape_min_words", DEFAULT_MIN_WORDS)

# ─── Database ───────────────────────────────────────────────────────────────────

def get_db():
    """Get SQLite connection."""
    if not DB_FILE.exists():
        print(f"Database not found: {DB_FILE}", file=sys.stderr)
        print("Run discover-construction-urls.sh first.", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def get_pending_urls(conn, domain=None, limit=None, retry_failed=False):
    """Get URLs pending scraping."""
    if retry_failed:
        status = "failed"
    else:
        status = "pending"

    sql = f"SELECT url, domain, path, category, content_type FROM urls WHERE scrape_status = ?"
    params = [status]

    if domain:
        sql += " AND domain = ?"
        params.append(domain)

    sql += " ORDER BY domain, url"

    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    return conn.execute(sql, params).fetchall()

def update_url_status(conn, url, status, title=None, word_count=None, content_hash=None):
    """Update URL scrape status in DB."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """UPDATE urls SET scrape_status = ?, scraped_at = ?, title = ?, word_count = ?, content_hash = ?
           WHERE url = ?""",
        (status, now, title, word_count, content_hash, url)
    )
    conn.commit()

# ─── Crawl4AI ───────────────────────────────────────────────────────────────────

def check_crawl4ai():
    """Check if Crawl4AI is running."""
    try:
        resp = requests.get(f"{CRAWL4AI_URL}/health", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False

def scrape_url(url):
    """Scrape a URL via Crawl4AI, return markdown content or None."""
    payload = {
        "urls": [url],
        "priority": 5,
        "crawler_params": {
            "headless": True,
            "page_timeout": 30000,
            "word_count_threshold": 50,
        },
    }

    try:
        resp = requests.post(CRAWL4AI_ENDPOINT, json=payload, timeout=90)
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"

        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None, "No results"

        result = results[0]
        # Prefer fit_markdown (boilerplate-stripped) over raw_markdown
        md = ""
        md_field = result.get("markdown", "")
        if isinstance(md_field, dict):
            md = md_field.get("fit_markdown", "") or md_field.get("raw_markdown", "")
        elif isinstance(md_field, str):
            md = md_field
        if not md:
            md_v2 = result.get("markdown_v2", {})
            if isinstance(md_v2, dict):
                md = md_v2.get("fit_markdown", "") or md_v2.get("raw_markdown", "")
        if not md:
            md = result.get("text", "")

        return md, None

    except requests.Timeout:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)

# ─── Content Cleaning ──────────────────────────────────────────────────────────

def clean_markdown(md):
    """Strip nav, footer, ad, and boilerplate content from markdown."""
    # Phase 1: Strip everything before first heading (nav/header boilerplate)
    h1_match = re.search(r'^#{1,2}\s+\S', md, re.MULTILINE)
    if h1_match:
        md = md[h1_match.start():]

    lines = md.split("\n")
    cleaned = []
    footer_started = False

    for line in lines:
        lower = line.lower().strip()

        # Once we hit footer markers, skip everything after
        if not footer_started and any(marker in lower for marker in [
            "© 20", "all rights reserved", "footer",
        ]):
            footer_started = True
            continue

        if footer_started:
            continue

        # Skip boilerplate lines
        if any(marker in lower for marker in [
            "skip to content", "skip to main", "toggle navigation",
            "privacy policy", "cookie policy", "terms of use",
            "terms of service", "subscribe to our newsletter",
            "sign up for our", "advertisement", "sponsored content",
            "comments are closed", "leave a reply",
        ]):
            continue

        # Skip social media link clusters
        if re.match(r'^[\s]*\[?(facebook|twitter|pinterest|instagram|youtube|linkedin)', lower):
            continue

        # Skip empty link lines like [](url)
        if re.match(r'^\s*\[?\s*\]\(', line):
            continue

        # Skip lines that are just clusters of links (nav menus)
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', line))
        if link_count >= 4 and len(line.strip()) < link_count * 80:
            continue

        cleaned.append(line)

    result = "\n".join(cleaned)

    # Collapse 3+ consecutive blank lines to 2
    result = re.sub(r'\n{4,}', '\n\n\n', result)

    return result.strip()

def extract_title(md):
    """Extract first H1 or H2 from markdown as title."""
    for line in md.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    return None

def count_words(text):
    """Count words in text."""
    return len(text.split())

def content_hash(text):
    """Generate short content hash."""
    return hashlib.md5(text.encode()).hexdigest()[:16]

# ─── File Output ────────────────────────────────────────────────────────────────

def domain_slug(domain):
    """Convert domain to filesystem-safe slug."""
    return domain.replace("www.", "").replace(".", "-").replace("/", "")

def url_to_slug(url):
    """Convert URL path to filename slug."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    # Use last 2 path segments for uniqueness
    parts = path.split("/")
    slug_parts = parts[-2:] if len(parts) >= 2 else parts
    slug = "-".join(slug_parts)
    # Clean up
    slug = re.sub(r'[^a-zA-Z0-9\-]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:120] or "index"

def save_article(url, domain, category, content_type, md, title, wc, chash):
    """Save article as markdown with YAML frontmatter."""
    dslug = domain_slug(domain)
    article_dir = OUTPUT_DIR / dslug / "articles"
    article_dir.mkdir(parents=True, exist_ok=True)

    slug = url_to_slug(url)
    filepath = article_dir / f"{slug}.md"

    # Avoid overwriting (add hash suffix if collision)
    if filepath.exists():
        filepath = article_dir / f"{slug}-{chash[:6]}.md"

    now = datetime.now(timezone.utc).isoformat()

    frontmatter = f"""---
title: "{(title or '').replace('"', '\\"')}"
source_url: "{url}"
domain: "{domain}"
category: "{category or 'general'}"
content_type: "{content_type or 'article'}"
word_count: {wc}
content_hash: "{chash}"
scraped_at: "{now}"
---
"""
    filepath.write_text(frontmatter + "\n" + md, encoding="utf-8")
    return filepath

def save_domain_index(domain):
    """Create/update _index.json for a domain directory."""
    dslug = domain_slug(domain)
    article_dir = OUTPUT_DIR / dslug / "articles"
    if not article_dir.exists():
        return

    articles = list(article_dir.glob("*.md"))
    index = {
        "domain": domain,
        "slug": dslug,
        "article_count": len(articles),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    index_path = OUTPUT_DIR / dslug / "_index.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

# ─── Status ─────────────────────────────────────────────────────────────────────

def show_status():
    """Show scraping progress."""
    conn = get_db()

    print("=== Scraping Progress ===\n")

    rows = conn.execute("""
        SELECT domain,
               COUNT(*) as total,
               SUM(CASE WHEN scrape_status = 'pending' THEN 1 ELSE 0 END) as pending,
               SUM(CASE WHEN scrape_status = 'scraped' THEN 1 ELSE 0 END) as scraped,
               SUM(CASE WHEN scrape_status = 'failed' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN scrape_status = 'skipped' THEN 1 ELSE 0 END) as skipped
        FROM urls
        GROUP BY domain
        ORDER BY total DESC
    """).fetchall()

    print(f"{'Domain':<30} {'Total':>7} {'Pending':>8} {'Scraped':>8} {'Failed':>7} {'Skipped':>8}")
    print("-" * 78)
    for row in rows:
        print(f"{row['domain']:<30} {row['total']:>7} {row['pending']:>8} {row['scraped']:>8} {row['failed']:>7} {row['skipped']:>8}")

    totals = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN scrape_status = 'pending' THEN 1 ELSE 0 END) as pending,
               SUM(CASE WHEN scrape_status = 'scraped' THEN 1 ELSE 0 END) as scraped,
               SUM(CASE WHEN scrape_status = 'failed' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN scrape_status = 'skipped' THEN 1 ELSE 0 END) as skipped
        FROM urls
    """).fetchone()

    print("-" * 78)
    print(f"{'TOTAL':<30} {totals['total']:>7} {totals['pending']:>8} {totals['scraped']:>8} {totals['failed']:>7} {totals['skipped']:>8}")

    # Show on-disk stats
    print(f"\nOutput directory: {OUTPUT_DIR}")
    if OUTPUT_DIR.exists():
        for d in sorted(OUTPUT_DIR.iterdir()):
            if d.is_dir():
                articles = list((d / "articles").glob("*.md")) if (d / "articles").exists() else []
                print(f"  {d.name}/: {len(articles)} articles on disk")

    conn.close()

# ─── Main Scraping Loop ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape construction content via Crawl4AI")
    parser.add_argument("--domain", type=str, help="Only scrape URLs from this domain")
    parser.add_argument("--limit", type=int, help="Maximum number of URLs to scrape")
    parser.add_argument("--delay", type=float, help="Override delay between requests (seconds)")
    parser.add_argument("--status", action="store_true", help="Show scraping progress")
    parser.add_argument("--retry-failed", action="store_true", help="Re-attempt failed URLs")
    parser.add_argument("--dry-run", action="store_true", help="Preview URLs without scraping")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    # Check Crawl4AI
    if not args.dry_run and not check_crawl4ai():
        print("Crawl4AI not available at localhost:11235", file=sys.stderr)
        print("Start it with: docker compose -f docker-compose.services.yml up -d crawl4ai", file=sys.stderr)
        sys.exit(1)

    domain_configs = load_domain_config()
    conn = get_db()

    urls = get_pending_urls(conn, domain=args.domain, limit=args.limit, retry_failed=args.retry_failed)

    if not urls:
        print("No pending URLs to scrape.")
        if args.domain:
            print(f"  (filtered by domain: {args.domain})")
        return

    print(f"Found {len(urls)} URLs to scrape")
    if args.dry_run:
        for row in urls[:20]:
            print(f"  {row['domain']:<25} {row['category']:<15} {row['url']}")
        if len(urls) > 20:
            print(f"  ... and {len(urls) - 20} more")
        return

    # Scrape loop
    scraped = 0
    failed = 0
    skipped = 0
    current_domain = None

    for i, row in enumerate(urls):
        url = row["url"]
        domain = row["domain"]
        category = row["category"]
        ct = row["content_type"]

        # Show progress
        pct = ((i + 1) / len(urls)) * 100
        print(f"[{i+1}/{len(urls)} {pct:.0f}%] {domain}: {url[:80]}...")

        # Scrape
        md, error = scrape_url(url)

        if error:
            print(f"  FAILED: {error}")
            update_url_status(conn, url, "failed")
            failed += 1
            delay = get_domain_delay(domain, domain_configs, args.delay)
            time.sleep(delay)
            continue

        if not md:
            print(f"  SKIPPED: empty content")
            update_url_status(conn, url, "skipped")
            skipped += 1
            continue

        # Clean and validate
        md = clean_markdown(md)
        wc = count_words(md)
        min_words = get_domain_min_words(domain, domain_configs)

        if wc < min_words:
            print(f"  SKIPPED: {wc} words (min {min_words})")
            update_url_status(conn, url, "skipped", word_count=wc)
            skipped += 1
            continue

        # Extract metadata
        title = extract_title(md)
        chash = content_hash(md)

        # Save
        filepath = save_article(url, domain, category, ct, md, title, wc, chash)
        update_url_status(conn, url, "scraped", title=title, word_count=wc, content_hash=chash)
        scraped += 1

        print(f"  OK: {wc} words → {filepath.relative_to(PROJECT_DIR)}")

        # Update domain index periodically
        if current_domain != domain:
            if current_domain:
                save_domain_index(current_domain)
            current_domain = domain

        # Rate limit
        delay = get_domain_delay(domain, domain_configs, args.delay)
        time.sleep(delay)

    # Final domain index
    if current_domain:
        save_domain_index(current_domain)

    conn.close()

    # Summary
    print(f"\n=== Scraping Complete ===")
    print(f"  Scraped: {scraped}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {scraped + failed + skipped}")
    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
