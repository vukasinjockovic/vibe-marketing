#!/usr/bin/env python3
"""
Probe Angi.com - Phase 5: Find actual API calls.

Approach:
1. Try RSC (React Server Components) flight protocol — request with RSC:1 header
2. Extract JS chunk URLs from HTML and look for fetch/API patterns
3. Find the actual data-fetching endpoints the frontend uses
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
fetcher = Fetcher()

# === Part 1: RSC Flight Protocol ===
print("=" * 60)
print("[*] Part 1: Try RSC (React Server Components) flight request")
print("=" * 60)

# Next.js App Router: when navigating client-side, it sends these headers
# to get RSC payload instead of full HTML
rsc_headers = {
    "RSC": "1",
    "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22companylist%22%2C%7B%7D%5D%7D%5D",
    "Next-Router-Prefetch": "1",
    "Accept": "text/x-component",
}

url = "https://www.angi.com/companylist/us/tx/austin/plumbing.htm"
print(f"[*] Requesting with RSC:1 header: {url}")

r = fetcher.get(url, proxy=PROXY, timeout=30, headers=rsc_headers)
body = r.body.decode('utf-8', errors='replace')
print(f"[*] Status: {r.status}")
print(f"[*] Content-Type: {r.headers.get('content-type', 'unknown') if hasattr(r.headers, 'get') else 'N/A'}")
print(f"[*] Body length: {len(body)}")
print(f"[*] Body preview (first 1000 chars):")
print(body[:1000])
print("...")
print(f"[*] Body (last 500 chars):")
print(body[-500:])

# Save full RSC payload
with open('/var/www/vibe-marketing/scripts/scrapers/angi-rsc-payload.txt', 'w') as f:
    f.write(body)
print(f"\n[*] Saved to angi-rsc-payload.txt")

# Check if RSC payload contains structured data
# RSC format uses lines like "0:..." with JSON payloads
if body.startswith('0:') or '\n0:' in body or body.startswith('1:'):
    print("[+] RSC flight format detected! Parsing...")
    lines = body.split('\n')
    for i, line in enumerate(lines[:20]):
        print(f"  Line {i}: {line[:200]}")

# === Part 2: Try without RSC prefetch (full RSC render) ===
print("\n" + "=" * 60)
print("[*] Part 2: RSC without prefetch (full server component render)")
print("=" * 60)

rsc_headers2 = {
    "RSC": "1",
    "Accept": "*/*",
}

r2 = fetcher.get(url, proxy=PROXY, timeout=30, headers=rsc_headers2)
body2 = r2.body.decode('utf-8', errors='replace')
print(f"[*] Status: {r2.status}")
print(f"[*] Body length: {len(body2)}")
if body2 != body:
    print(f"[*] Different from prefetch! Preview:")
    print(body2[:1000])
    with open('/var/www/vibe-marketing/scripts/scrapers/angi-rsc-full.txt', 'w') as f:
        f.write(body2)
else:
    print("[*] Same as prefetch")

# === Part 3: Extract JS chunk URLs and find data-fetching code ===
print("\n" + "=" * 60)
print("[*] Part 3: Find JS chunks with API/fetch patterns")
print("=" * 60)

# Get fresh HTML (full page)
r_html = fetcher.get(url, proxy=PROXY, timeout=30)
html = r_html.body.decode('utf-8', errors='replace')

# Extract all _next/static chunk URLs
chunk_urls = re.findall(r'(https://[^"\']+/_next/static/[^"\']+\.js)', html)
chunk_urls = list(set(chunk_urls))
print(f"[*] Found {len(chunk_urls)} unique JS chunk URLs")

# Also find chunks from the static assets CDN
cdn_chunks = re.findall(r'(https://lpfe-static-assets\.angi\.com/[^"\']+\.js)', html)
cdn_chunks = list(set(cdn_chunks))
print(f"[*] Found {len(cdn_chunks)} CDN JS chunk URLs")

all_chunks = list(set(chunk_urls + cdn_chunks))
print(f"[*] Total unique chunks: {len(all_chunks)}")

# Show some samples
for c in sorted(all_chunks)[:10]:
    print(f"    {c}")

# Download a few key chunks and search for API patterns
# Look for: the main page chunk, app chunk, or anything with "api" in it
interesting_chunks = [c for c in all_chunks if any(kw in c.lower() for kw in ['page', 'app', 'main', 'layout'])]
print(f"\n[*] Interesting chunks (page/app/main/layout): {len(interesting_chunks)}")
for c in interesting_chunks[:5]:
    print(f"    {c}")

# Download first 3 largest-looking chunks and search for API patterns
api_keywords = ['api.angi.com', '/api/', 'fetch(', 'axios', 'graphql', '/directory/', '/listings/', '/pros/', 'companylist']

chunks_to_check = all_chunks[:8]  # Check first 8 chunks
print(f"\n[*] Checking {len(chunks_to_check)} chunks for API patterns...")

for chunk_url in chunks_to_check:
    try:
        r_chunk = fetcher.get(chunk_url, proxy=PROXY, timeout=10)
        js = r_chunk.body.decode('utf-8', errors='replace')

        matches = []
        for kw in api_keywords:
            if kw in js:
                # Find context around the keyword
                idx = js.find(kw)
                context = js[max(0, idx-80):idx+120]
                matches.append((kw, context))

        if matches:
            chunk_name = chunk_url.split('/')[-1]
            print(f"\n  [+] {chunk_name} ({len(js)} chars):")
            for kw, ctx in matches[:5]:
                # Clean up for display
                ctx_clean = ctx.replace('\n', ' ').strip()
                print(f"      [{kw}]: ...{ctx_clean}...")
    except Exception as e:
        pass

print("\n[*] Done.")
