#!/usr/bin/env python3
"""
Probe Angi.com - Phase 3: Decode JWT token and probe directory API endpoints.
The token endpoint returned roles including DIRECTORY_LISTING_GET and PRO_API_GET.
"""

import json
import base64
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"

# === Step 1: Get fresh token ===
print("=" * 60)
print("[*] Step 1: Get fresh JWT token")
print("=" * 60)

fetcher = Fetcher()
r = fetcher.get("https://api.angi.com/api/landing-pages/token", proxy=PROXY, timeout=15)
token = r.body.decode('utf-8').strip().strip('"')

# Decode JWT (no verification needed, just inspect)
parts = token.split('.')
header = json.loads(base64.b64decode(parts[0] + '=='))
payload = json.loads(base64.b64decode(parts[1] + '=='))

print(f"[+] Header: {json.dumps(header, indent=2)}")
print(f"[+] Payload: {json.dumps(payload, indent=2)}")
print(f"[+] Roles: {payload.get('roles', '')}")
print(f"[+] Entity ID: {payload.get('eid', '')}")

# Roles found:
# GEO_DATA_MSA_ZIPS_RETRIEVE
# DIRECTORY_LISTING_GET  <-- this is what we want
# ANGI_CMS_GET
# PRO_API_GATEWAY_UPDATE
# PRO_API_GET
# PRO_API_GATEWAY_GET

# === Step 2: Probe API endpoints with the token ===
print("\n" + "=" * 60)
print("[*] Step 2: Probe API endpoints with Bearer token")
print("=" * 60)

auth_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Based on the roles, try various endpoint patterns
endpoints = [
    # Directory listing endpoints
    ("GET", "https://api.angi.com/api/directory/listings?city=Austin&state=TX&category=plumbing", "Directory listings"),
    ("GET", "https://api.angi.com/api/directory/listing?city=Austin&state=TX&category=plumbing", "Directory listing (singular)"),
    ("GET", "https://api.angi.com/api/v1/directory/listings?city=Austin&state=TX", "Directory v1"),
    ("GET", "https://api.angi.com/api/v2/directory/listings?city=Austin&state=TX", "Directory v2"),

    # Pro API endpoints
    ("GET", "https://api.angi.com/api/pro?city=Austin&state=TX", "Pro search"),
    ("GET", "https://api.angi.com/api/pros?city=Austin&state=TX&category=plumbing", "Pros search"),
    ("GET", "https://api.angi.com/api/v1/pros?city=Austin&state=TX", "Pros v1"),

    # Landing pages endpoints (we know this prefix works)
    ("GET", "https://api.angi.com/api/landing-pages/listings?city=Austin&state=TX&category=plumbing", "LP listings"),
    ("GET", "https://api.angi.com/api/landing-pages/directory?city=Austin&state=TX&category=plumbing", "LP directory"),
    ("GET", "https://api.angi.com/api/landing-pages/providers?city=Austin&state=TX&category=plumbing", "LP providers"),

    # LPFE proxy (might proxy to other services)
    ("GET", "https://api.angi.com/api/lpfe/proxy/directory?city=Austin&state=TX", "LPFE proxy directory"),

    # GEO data
    ("GET", "https://api.angi.com/api/geo/msa/zips?postalCode=78701", "Geo MSA zips"),
    ("GET", "https://api.angi.com/api/geo/msa?postalCode=78701", "Geo MSA"),

    # CMS
    ("GET", "https://api.angi.com/api/cms/categories", "CMS categories"),
    ("GET", "https://api.angi.com/api/angi/cms/categories", "Angi CMS categories"),

    # Cost guide (we saw this in the HTML)
    ("GET", "https://api.angi.com/api/cost-guide/task?taskName=plumbing", "Cost guide task"),

    # Common patterns for Next.js apps
    ("GET", "https://api.angi.com/api/search?q=plumbing&location=Austin,TX", "Search"),
    ("GET", "https://api.angi.com/api/companylist?city=Austin&state=TX&category=plumbing", "Company list"),
]

for method, url, label in endpoints:
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=10, headers=auth_headers)
        body = r.body.decode('utf-8', errors='replace')
        status = r.status

        # Skip 404 HTML error pages
        if status == 404 and '<html' in body.lower():
            print(f"  [{status}] {label}: HTML 404")
            continue

        if status in (200, 201):
            print(f"\n  [+] [{status}] {label}: {url}")
            try:
                data = json.loads(body)
                print(f"      JSON type: {type(data).__name__}")
                if isinstance(data, dict):
                    print(f"      Keys: {list(data.keys())[:10]}")
                    print(f"      Preview: {json.dumps(data, indent=2)[:800]}")
                elif isinstance(data, list):
                    print(f"      Items: {len(data)}")
                    if data:
                        print(f"      [0]: {json.dumps(data[0], indent=2)[:500]}")
                else:
                    print(f"      Value: {str(data)[:500]}")

                # Save any successful responses
                safe_label = label.replace(' ', '-').replace('/', '-')
                with open(f'/var/www/vibe-marketing/scripts/scrapers/angi-api-{safe_label}.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            except:
                print(f"      Raw: {body[:300]}")
        elif status == 401:
            print(f"  [401] {label}: Auth required (token not accepted)")
        elif status == 403:
            print(f"  [403] {label}: Forbidden")
        elif status == 405:
            print(f"  [405] {label}: Method not allowed")
        else:
            print(f"  [{status}] {label}")

    except Exception as e:
        print(f"  [ERR] {label}: {e}")

# === Step 3: Check the full LD+JSON SearchResultsPage data ===
print("\n" + "=" * 60)
print("[*] Step 3: Analyze SearchResultsPage LD+JSON (already saved)")
print("=" * 60)

try:
    with open('/var/www/vibe-marketing/scripts/scrapers/angi-ldjson-6-SearchResultsPage.json') as f:
        search_data = json.load(f)

    items = search_data.get('mainEntity', {}).get('itemListElement', [])
    print(f"[+] Total contractors in SearchResultsPage: {len(items)}")

    for item in items[:5]:
        biz = item.get('item', {})
        addr = biz.get('address', {})
        review = biz.get('review', {})
        print(f"\n  Business: {biz.get('name', '?')}")
        print(f"  Type: {biz.get('@type', '?')}")
        print(f"  Area: {biz.get('areaServed', '?')}")
        print(f"  Address: {addr.get('streetAddress', '?')}, {addr.get('addressLocality', '?')}, {addr.get('addressRegion', '?')} {addr.get('postalCode', '?')}")
        print(f"  URL: {biz.get('url', '?')}")
        print(f"  Review by: {review.get('author', {}).get('name', '?')}")
except Exception as e:
    print(f"[-] Error: {e}")

print("\n[*] Probe complete.")
