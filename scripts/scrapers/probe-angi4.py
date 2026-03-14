#!/usr/bin/env python3
"""
Probe Angi.com - Phase 2: Extract LD+JSON contractor data + probe API endpoints.
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"

fetcher = Fetcher()

# === Part 1: Extract LD+JSON from listing page ===
print("=" * 60)
print("[*] Part 1: Extract Schema.org data from listing page")
print("=" * 60)

response = fetcher.get(
    "https://www.angi.com/companylist/us/tx/austin/plumbing.htm",
    proxy=PROXY,
    timeout=30,
)

html = response.body.decode('utf-8', errors='replace')
print(f"[*] Got {len(html)} chars")

ld_blocks = re.findall(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
    html,
    re.DOTALL
)

for i, block in enumerate(ld_blocks):
    try:
        parsed = json.loads(block)
        if isinstance(parsed, dict):
            t = parsed.get('@type', '')
            if t in ('ItemList', 'SearchResultsPage', 'LocalBusiness', 'Organization'):
                print(f"\n[+] Block {i}: @type={t}")
                print(json.dumps(parsed, indent=2, default=str)[:3000])
                with open(f'/var/www/vibe-marketing/scripts/scrapers/angi-ldjson-{i}-{t}.json', 'w') as f:
                    json.dump(parsed, f, indent=2, default=str)
                print(f"\n[+] Saved to angi-ldjson-{i}-{t}.json")
    except:
        pass

# === Part 2: Look for contractor data in HTML (non-JSON) ===
print("\n" + "=" * 60)
print("[*] Part 2: Search HTML for contractor data patterns")
print("=" * 60)

# Look for business names, phone numbers, ratings in the HTML
# Angi might render server-side without __NEXT_DATA__
phone_pattern = r'\(\d{3}\)\s*\d{3}-\d{4}'
phones = re.findall(phone_pattern, html)
print(f"[*] Phone numbers found: {len(phones)}")
if phones:
    print(f"    Samples: {phones[:5]}")

# Look for rating patterns
rating_pattern = r'(\d\.\d)\s*(?:out of|/)\s*5'
ratings = re.findall(rating_pattern, html)
print(f"[*] Ratings found: {len(ratings)}")

# Look for review counts
review_pattern = r'(\d+)\s*(?:reviews?|verified reviews?)'
reviews = re.findall(review_pattern, html, re.IGNORECASE)
print(f"[*] Review counts found: {len(reviews)}")
if reviews:
    print(f"    Samples: {reviews[:5]}")

# Look for data attributes that might contain JSON
data_attrs = re.findall(r'data-(?:props|state|config|initial|page)="([^"]*)"', html)
print(f"[*] Data attributes found: {len(data_attrs)}")
for da in data_attrs[:3]:
    if len(da) > 50:
        # Might be JSON-encoded
        try:
            decoded = json.loads(da.replace('&quot;', '"').replace('&amp;', '&'))
            print(f"    Decoded JSON: {json.dumps(decoded, indent=2)[:500]}")
        except:
            print(f"    Raw: {da[:200]}")

# === Part 3: Probe API endpoints ===
print("\n" + "=" * 60)
print("[*] Part 3: Probe api.angi.com endpoints")
print("=" * 60)

api_endpoints = [
    # Token endpoint - might give us an auth token
    ("https://api.angi.com/api/landing-pages/token", "Token endpoint"),
    # Postal code lookup
    ("https://api.angi.com/api/postalcode?postalcode=78701", "Postal code (Austin)"),
    # City suggestions
    ("https://api.angi.com/api/landing-pages/city/suggestions?q=austin&state=TX", "City suggestions"),
    # The proxy endpoint - might be interesting
    ("https://api.angi.com/api/lpfe/proxy", "LPFE proxy"),
]

for url, label in api_endpoints:
    print(f"\n[*] Probing: {label}")
    print(f"    URL: {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=15)
        status = r.status
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {status}")
        print(f"    Body length: {len(body)}")
        if body:
            # Try to parse as JSON
            try:
                data = json.loads(body)
                print(f"    JSON: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"    Raw: {body[:300]}")
    except Exception as e:
        print(f"    Error: {e}")

# === Part 4: Check if there's a _next/data route ===
print("\n" + "=" * 60)
print("[*] Part 4: Check Next.js data routes")
print("=" * 60)

# Extract buildId from HTML
build_id_match = re.search(r'"buildId":"([^"]+)"', html)
if build_id_match:
    build_id = build_id_match.group(1)
    print(f"[+] Found buildId: {build_id}")

    # Try the _next/data route
    next_data_url = f"https://www.angi.com/_next/data/{build_id}/companylist/us/tx/austin/plumbing.json"
    print(f"[*] Trying: {next_data_url}")
    try:
        r = fetcher.get(next_data_url, proxy=PROXY, timeout=15)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}")
        print(f"    Body: {body[:1000]}")
        if r.status == 200:
            try:
                data = json.loads(body)
                print(f"[+] GOT NEXT.JS DATA ROUTE!")
                with open('/var/www/vibe-marketing/scripts/scrapers/angi-nextdata-route.json', 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"[+] Saved to angi-nextdata-route.json")
            except:
                pass
    except Exception as e:
        print(f"    Error: {e}")
else:
    print("[-] No buildId found in HTML")

    # Try to find it another way
    build_match = re.search(r'/_next/static/([^/]+)/_', html)
    if build_match:
        build_id = build_match.group(1)
        print(f"[+] Found buildId from static path: {build_id}")

print("\n[*] Probe complete.")
