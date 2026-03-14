#!/usr/bin/env python3
"""
Probe Angi.com - Phase 4:
1. Check if there's more contractor data in HTML beyond LD+JSON
2. Check pagination (page 2, 3, etc.)
3. Try API calls with proper Origin/Referer headers
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
fetcher = Fetcher()

# === Part 1: Extract ALL contractor data from listing HTML ===
print("=" * 60)
print("[*] Part 1: Deep HTML analysis of listing page")
print("=" * 60)

r = fetcher.get(
    "https://www.angi.com/companylist/us/tx/austin/plumbing.htm",
    proxy=PROXY,
    timeout=30,
)
html = r.body.decode('utf-8', errors='replace')

# Count all contractor detail URLs
detail_urls = re.findall(r'href="(/companylist/us/[^"]*reviews-[^"]+\.htm)"', html)
unique_urls = list(set(detail_urls))
print(f"[+] Total contractor detail URLs in HTML: {len(detail_urls)}")
print(f"[+] Unique contractor URLs: {len(unique_urls)}")
for url in unique_urls[:20]:
    print(f"    {url}")

# Look for pagination links
print(f"\n[*] Checking pagination...")
page_links = re.findall(r'href="([^"]*(?:page|p)=?\d+[^"]*)"', html, re.IGNORECASE)
page_links2 = re.findall(r'href="([^"]*plumbing[^"]*)"', html)
print(f"[*] Pagination links: {len(page_links)}")
for pl in page_links[:10]:
    print(f"    {pl}")
print(f"[*] Category-related links: {len(page_links2)}")
for pl in list(set(page_links2))[:10]:
    print(f"    {pl}")

# Look for "next page", "load more", pagination indicators
pagination_indicators = re.findall(r'(?:next.page|load.more|pagination|page.\d+|showing.\d+)', html, re.IGNORECASE)
print(f"[*] Pagination indicators: {pagination_indicators[:10]}")

# Look for total count of providers
count_patterns = re.findall(r'(\d+)\s*(?:pros?|providers?|contractors?|results?|businesses?)\s*(?:found|available|near|in)', html, re.IGNORECASE)
print(f"[*] Provider count mentions: {count_patterns[:10]}")

# === Part 2: Try paginated URLs ===
print("\n" + "=" * 60)
print("[*] Part 2: Try pagination")
print("=" * 60)

# Common pagination patterns for Angi
pagination_urls = [
    "https://www.angi.com/companylist/us/tx/austin/plumbing.htm?page=2",
    "https://www.angi.com/companylist/us/tx/austin/plumbing/2.htm",
    "https://www.angi.com/companylist/us/tx/austin/plumbing.htm?offset=10",
]

for url in pagination_urls:
    print(f"\n[*] Trying: {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=15)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}, Body: {len(body)} chars")
        if r.status == 200 and len(body) > 1000:
            # Check for different contractors
            urls_p2 = set(re.findall(r'href="(/companylist/us/[^"]*reviews-[^"]+\.htm)"', body))
            overlap = urls_p2.intersection(set(unique_urls))
            new = urls_p2 - set(unique_urls)
            print(f"    Contractors: {len(urls_p2)} ({len(new)} new, {len(overlap)} overlap)")
            if new:
                print(f"    New ones: {list(new)[:5]}")
    except Exception as e:
        print(f"    Error: {e}")

# === Part 3: Try API with proper Origin header ===
print("\n" + "=" * 60)
print("[*] Part 3: Try API with proper headers (as if from angi.com)")
print("=" * 60)

# Get token first
r = fetcher.get("https://api.angi.com/api/landing-pages/token", proxy=PROXY, timeout=15)
token = r.body.decode('utf-8').strip().strip('"')

# Try with proper origin/referer as the browser would send
browser_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.angi.com",
    "Referer": "https://www.angi.com/companylist/us/tx/austin/plumbing.htm",
    "X-Requested-With": "XMLHttpRequest",
}

# The 403 endpoints - try again with proper headers
retry_endpoints = [
    "https://api.angi.com/api/directory/listings?city=Austin&state=TX&category=plumbing",
    "https://api.angi.com/api/landing-pages/listings?city=Austin&state=TX&category=plumbing",
    "https://api.angi.com/api/landing-pages/directory?city=Austin&state=TX&category=plumbing",
    "https://api.angi.com/api/pro?city=Austin&state=TX",
]

for url in retry_endpoints:
    print(f"\n[*] Retry: {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=15, headers=browser_headers)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}")
        if r.status == 200:
            print(f"    [+] SUCCESS! Body: {body[:500]}")
        elif r.status != 404:
            # Check if it's a JSON error
            try:
                err = json.loads(body)
                print(f"    Error: {json.dumps(err, indent=2)[:300]}")
            except:
                print(f"    Body: {body[:200]}")
    except Exception as e:
        print(f"    Error: {e}")

# === Part 4: Check different category URLs ===
print("\n" + "=" * 60)
print("[*] Part 4: Check other construction categories")
print("=" * 60)

categories = [
    "electrical",
    "roofing",
    "hvac",
    "general-contractor",
    "painting",
]

for cat in categories:
    url = f"https://www.angi.com/companylist/us/tx/austin/{cat}.htm"
    print(f"\n[*] {cat}: {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=15)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}, Body: {len(body)} chars")
        if r.status == 200:
            urls_cat = set(re.findall(r'href="(/companylist/us/[^"]*reviews-[^"]+\.htm)"', body))
            # Extract LD+JSON count
            ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', body, re.DOTALL)
            for block in ld_blocks:
                try:
                    parsed = json.loads(block)
                    if isinstance(parsed, dict) and parsed.get('@type') == 'SearchResultsPage':
                        items = parsed.get('mainEntity', {}).get('itemListElement', [])
                        print(f"    LD+JSON contractors: {len(items)}")
                        if items:
                            print(f"    First: {items[0].get('item', {}).get('name', '?')}")
                except:
                    pass
            print(f"    HTML contractor URLs: {len(urls_cat)}")
    except Exception as e:
        print(f"    Error: {e}")

print("\n[*] Done.")
