#!/usr/bin/env python3
"""
Probe Angi.com - Phase 6:
1. Parse the RSC flight payload for contractor data
2. Download the page chunk and 9269 chunk to find ALL API endpoints
3. Find lpbeApiDomain value
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
fetcher = Fetcher()

# === Part 1: Parse RSC payload ===
print("=" * 60)
print("[*] Part 1: Parse RSC flight payload")
print("=" * 60)

# Read saved RSC payload
with open('/var/www/vibe-marketing/scripts/scrapers/angi-rsc-full.txt', 'r') as f:
    rsc = f.read()

print(f"[*] RSC payload: {len(rsc)} chars")

# RSC flight format: each line is "id:payload"
# Look for JSON data embedded in the payload
lines = rsc.split('\n')
print(f"[*] Total lines: {len(lines)}")

# Find lines with contractor-related data
for i, line in enumerate(lines):
    # Look for business names, addresses, reviews
    if any(kw in line for kw in ['HomeAndConstruction', 'LocalBusiness', 'plumb', 'Plumb',
                                  'contractor', 'Torres', 'reviews-', 'streetAddress',
                                  'rating', 'ReviewAction', 'aggregateRating']):
        print(f"\n  Line {i} ({len(line)} chars):")
        # Show a relevant snippet
        for kw in ['HomeAndConstruction', 'LocalBusiness', 'streetAddress', 'rating',
                    'aggregateRating', 'Torres', 'reviews-']:
            idx = line.find(kw)
            if idx >= 0:
                snippet = line[max(0, idx-50):idx+150]
                print(f"    [{kw}]: ...{snippet}...")
                break

# Find all JSON-like objects in the RSC payload
print(f"\n[*] Extracting JSON objects from RSC payload...")
# RSC embeds JSON after the line ID prefix
json_objects = []
for line in lines:
    # Match patterns like "b:[[...JSON...]]" or "c:{...JSON...}"
    match = re.match(r'^([0-9a-f]+):(.+)$', line)
    if match:
        row_id, payload = match.groups()
        # Try to find JSON starting points
        if payload.startswith('[') or payload.startswith('{') or payload.startswith('"'):
            try:
                data = json.loads(payload)
                if isinstance(data, (dict, list)):
                    size = len(payload)
                    if size > 100:  # Skip tiny entries
                        json_objects.append((row_id, size, data))
            except:
                pass

print(f"[*] Found {len(json_objects)} JSON objects > 100 chars")
for row_id, size, data in sorted(json_objects, key=lambda x: -x[1])[:10]:
    print(f"  Row {row_id}: {size} chars, type={type(data).__name__}")
    if isinstance(data, dict):
        print(f"    Keys: {list(data.keys())[:10]}")
    elif isinstance(data, list):
        print(f"    Length: {len(data)}")
        if data and isinstance(data[0], (dict, str)):
            print(f"    [0]: {str(data[0])[:200]}")

# Save all large JSON objects
with open('/var/www/vibe-marketing/scripts/scrapers/angi-rsc-json-objects.json', 'w') as f:
    json.dump([(rid, size, data) for rid, size, data in json_objects], f, indent=2, default=str)

# === Part 2: Download the page-specific JS chunk ===
print("\n" + "=" * 60)
print("[*] Part 2: Download page chunk + find API endpoints")
print("=" * 60)

# The page chunk for companylist
page_chunk_url = "https://lpfe-static-assets.angi.com/static/landing-pages-frontend/_next/static/chunks/app/companylist/%5Bslugorcountry%5D/%5Bstateortask%5D/%5Bcity%5D/%5Btaskorproprofile%5D/page-f2f4f2b190c8f6ef.js"
print(f"[*] Downloading page chunk...")

r = fetcher.get(page_chunk_url, proxy=PROXY, timeout=15)
page_js = r.body.decode('utf-8', errors='replace')
print(f"[*] Page chunk: {len(page_js)} chars")

# Search for ALL API-related patterns
api_patterns_to_find = [
    r'["\']([^"\']*api[^"\']*(?:search|listing|directory|provider|pro|company)[^"\']*)["\']',
    r'["\']([^"\']*\/v\d\/[^"\']+)["\']',
    r'fetch\s*\(["\']([^"\']+)["\']',
    r'["\']([^"\']*lpbe[^"\']*)["\']',
    r'["\']([^"\']*gateway[^"\']*)["\']',
    r'(lpbeApiDomain|apiDomain|baseUrl|apiUrl|apiBase|API_URL|API_BASE)["\']?\s*[:=]\s*["\']([^"\']+)',
    r'["\']([^"\']*\.angi\.com[^"\']*)["\']',
]

for pattern in api_patterns_to_find:
    matches = re.findall(pattern, page_js)
    if matches:
        print(f"\n  Pattern '{pattern[:40]}...':")
        for m in set(matches) if isinstance(matches[0], str) else matches:
            if isinstance(m, tuple):
                print(f"    {m}")
            else:
                if len(m) < 200:
                    print(f"    {m}")

# === Part 3: Download the 9269 chunk (has API calls) ===
print("\n" + "=" * 60)
print("[*] Part 3: Analyze 9269 chunk (contains API endpoints)")
print("=" * 60)

chunk_9269_url = "https://lpfe-static-assets.angi.com/static/landing-pages-frontend/_next/static/chunks/9269-584b7f46f2a86ad3.js"
r = fetcher.get(chunk_9269_url, proxy=PROXY, timeout=15)
js_9269 = r.body.decode('utf-8', errors='replace')
print(f"[*] 9269 chunk: {len(js_9269)} chars")

# Find ALL URL-building patterns
url_patterns = re.findall(r'concat\([^)]*(?:api|Api|domain|Domain|url|Url)[^)]*\)', js_9269)
print(f"\n[*] URL concat patterns: {len(url_patterns)}")
for p in url_patterns[:20]:
    print(f"    {p}")

# Find all string literals that look like API paths
api_paths = re.findall(r'["\'](/[a-z0-9/_-]*(?:api|search|listing|directory|pro|company|provider|autocomplete)[^"\']*)["\']', js_9269, re.IGNORECASE)
print(f"\n[*] API paths found: {len(api_paths)}")
for p in set(api_paths):
    print(f"    {p}")

# Find config/domain references
config_refs = re.findall(r'(\w+(?:Api|api|Domain|domain|Url|url|Base|base|Host|host)\w*)', js_9269)
config_refs = list(set(config_refs))
print(f"\n[*] Config references: {len(config_refs)}")
for c in sorted(config_refs):
    print(f"    {c}")

# Save the full chunk for manual review
with open('/var/www/vibe-marketing/scripts/scrapers/angi-chunk-9269.js', 'w') as f:
    f.write(js_9269)

# Also save page chunk
with open('/var/www/vibe-marketing/scripts/scrapers/angi-page-chunk.js', 'w') as f:
    f.write(page_js)

print("\n[*] Saved both chunks for manual review")
print("[*] Done.")
