#!/usr/bin/env python3
"""
Probe Angi.com to understand their data delivery mechanism.
Single request - no spamming. Uses scrapling with browser impersonation.
"""

import json
import re
import sys
from scrapling import Fetcher

# DataImpulse residential proxy
PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"

# A real contractor listing page (plumbers in Austin TX - common search)
TARGET_URL = "https://www.angi.com/companylist/us/tx/austin/plumbing.htm"

def probe_listing_page():
    """Probe a category listing page to understand the data structure."""
    print(f"[*] Probing: {TARGET_URL}")
    print(f"[*] Using DataImpulse residential proxy")
    print()

    fetcher = Fetcher()
    response = fetcher.get(
        TARGET_URL,
        proxy=PROXY,
        timeout=30,
    )

    print(f"[*] Status: {response.status}")
    print(f"[*] Content length: {len(response.text)} chars")
    print()

    html = response.text

    # === Check 1: __NEXT_DATA__ (Next.js SSR) ===
    next_data_match = re.search(
        r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )

    if next_data_match:
        print("[+] FOUND __NEXT_DATA__ - Next.js SSR detected!")
        try:
            data = json.loads(next_data_match.group(1))
            print(f"[+] JSON keys: {list(data.keys())}")
            if 'props' in data:
                print(f"[+] props keys: {list(data['props'].keys())}")
                if 'pageProps' in data['props']:
                    page_props = data['props']['pageProps']
                    print(f"[+] pageProps keys: {list(page_props.keys())}")
                    # Save full structure for analysis
                    with open('/var/www/vibe-marketing/scripts/scrapers/angi-next-data.json', 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    print(f"[+] Full __NEXT_DATA__ saved to angi-next-data.json")
        except json.JSONDecodeError as e:
            print(f"[-] JSON parse error: {e}")
            # Save raw for inspection
            with open('/var/www/vibe-marketing/scripts/scrapers/angi-next-data-raw.txt', 'w') as f:
                f.write(next_data_match.group(1)[:10000])
            print(f"[*] Raw data saved (first 10K chars)")
    else:
        print("[-] No __NEXT_DATA__ found")

    # === Check 2: Look for API endpoints in the HTML/JS ===
    api_patterns = [
        r'(https?://[^"\'\s]*api[^"\'\s]*)',
        r'(https?://[^"\'\s]*/graphql[^"\'\s]*)',
        r'(/api/[^"\'\s]+)',
        r'(/_next/data/[^"\'\s]+)',
    ]

    print()
    print("[*] Scanning for API endpoints...")
    found_apis = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, html)
        for m in matches:
            if len(m) < 200:  # skip data URIs
                found_apis.add(m)

    if found_apis:
        print(f"[+] Found {len(found_apis)} API-like URLs:")
        for url in sorted(found_apis)[:30]:
            print(f"    {url}")
    else:
        print("[-] No API endpoints found in HTML")

    # === Check 3: Look for inline JSON data (React hydration) ===
    print()
    print("[*] Scanning for inline JSON data blocks...")
    json_scripts = re.findall(
        r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )
    if json_scripts:
        print(f"[+] Found {len(json_scripts)} application/json script blocks")
        for i, block in enumerate(json_scripts[:5]):
            try:
                parsed = json.loads(block)
                print(f"    Block {i}: {type(parsed).__name__}, keys={list(parsed.keys()) if isinstance(parsed, dict) else 'N/A'}")
            except:
                print(f"    Block {i}: {len(block)} chars (not valid JSON)")

    # === Check 4: Look for structured data (Schema.org) ===
    print()
    print("[*] Scanning for Schema.org structured data...")
    ld_json = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )
    if ld_json:
        print(f"[+] Found {len(ld_json)} LD+JSON blocks (Schema.org)")
        for i, block in enumerate(ld_json):
            try:
                parsed = json.loads(block)
                if isinstance(parsed, dict):
                    print(f"    Block {i}: @type={parsed.get('@type', '?')}")
                elif isinstance(parsed, list):
                    for item in parsed[:3]:
                        print(f"    Block {i}: @type={item.get('@type', '?')}")
            except:
                print(f"    Block {i}: parse error")

    # === Check 5: Extract any contractor names visible in HTML ===
    print()
    print("[*] Checking if contractor data is in the HTML...")

    # Save full HTML for manual inspection
    with open('/var/www/vibe-marketing/scripts/scrapers/angi-probe-response.html', 'w') as f:
        f.write(html)
    print(f"[*] Full HTML saved to angi-probe-response.html ({len(html)} chars)")


def probe_contractor_page():
    """Also probe a single contractor detail page."""
    # We'll extract a contractor URL from the listing page if we can
    detail_url = "https://www.angi.com/companylist/us/tx/austin/abc-home-and-commercial-services-reviews-117702.htm"
    print()
    print(f"[*] Probing contractor detail page: {detail_url}")

    fetcher = Fetcher()
    response = fetcher.get(
        detail_url,
        proxy=PROXY,
        timeout=30,
    )

    print(f"[*] Status: {response.status}")
    html = response.text

    next_data_match = re.search(
        r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )

    if next_data_match:
        print("[+] FOUND __NEXT_DATA__ on detail page!")
        try:
            data = json.loads(next_data_match.group(1))
            page_props = data.get('props', {}).get('pageProps', {})
            print(f"[+] pageProps keys: {list(page_props.keys())}")

            with open('/var/www/vibe-marketing/scripts/scrapers/angi-detail-data.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"[+] Detail page __NEXT_DATA__ saved to angi-detail-data.json")
        except json.JSONDecodeError as e:
            print(f"[-] JSON parse error: {e}")
    else:
        print("[-] No __NEXT_DATA__ on detail page")

    # Save HTML
    with open('/var/www/vibe-marketing/scripts/scrapers/angi-detail-response.html', 'w') as f:
        f.write(html)
    print(f"[*] Detail HTML saved ({len(html)} chars)")


if __name__ == "__main__":
    probe_listing_page()
    probe_contractor_page()
    print()
    print("[*] Done. Check the saved files for analysis.")
