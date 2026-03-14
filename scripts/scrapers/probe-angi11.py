#!/usr/bin/env python3
"""
Probe for phone/email/license/website:
1. Try detail page via RSC:1 header (CF blocked normal HTML, but RSC might work)
2. Check HomeAdvisor rated page (returned 200 earlier) for provider data
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
fetcher = Fetcher()

# === Probe 1: Detail page via RSC ===
print("=" * 60)
print("[*] Probe 1: Detail page via RSC:1 header")
print("=" * 60)

detail_url = "https://www.angi.com/companylist/us/tx/round-rock/torres-plumbing-llc-reviews-2.htm"
print(f"[*] {detail_url}")

r = fetcher.get(
    detail_url,
    proxy=PROXY,
    timeout=30,
    headers={"RSC": "1", "Accept": "*/*"},
)
body = r.body.decode('utf-8', errors='replace')
print(f"[*] Status: {r.status}, Length: {len(body)}")

if r.status == 200 and len(body) > 1000:
    print("[+] GOT DETAIL PAGE VIA RSC!")

    # Look for phone, email, website, license
    for field in ['phone', 'email', 'website', 'license', 'url', 'Phone', 'Email', 'Website']:
        matches = re.findall(f'"{field}"[:\s]*"([^"]*)"', body, re.IGNORECASE)
        if matches:
            print(f"  {field}: {matches[:3]}")

    # Look for contact block
    for pattern in [r'"phone[^"]*"[:\s]*"([^"]+)"', r'\(\d{3}\)\s*\d{3}-\d{4}', r'\d{3}[-.]?\d{3}[-.]?\d{4}']:
        phones = re.findall(pattern, body)
        if phones:
            print(f"  Phone matches: {phones[:5]}")

    # Save for analysis
    with open('/var/www/vibe-marketing/scripts/scrapers/angi-detail-rsc.txt', 'w') as f:
        f.write(body)
    print(f"  Saved to angi-detail-rsc.txt")

    # Show first few lines
    lines = body.split('\n')
    print(f"\n  Lines: {len(lines)}")
    for line in lines[:5]:
        print(f"  {line[:200]}")
else:
    print(f"[-] Blocked (status {r.status})")
    print(f"  Preview: {body[:200]}")

# === Probe 2: HomeAdvisor rated page ===
print("\n" + "=" * 60)
print("[*] Probe 2: HomeAdvisor rated page (returned 200 before)")
print("=" * 60)

ha_url = "https://www.homeadvisor.com/rated.Plumbers.12013.html"
print(f"[*] {ha_url}")

r = fetcher.get(ha_url, proxy=PROXY, timeout=30)
body = r.body.decode('utf-8', errors='replace')
print(f"[*] Status: {r.status}, Length: {len(body)}")

if r.status == 200:
    # Search for phone numbers
    phones = re.findall(r'[\(]?\d{3}[\)]?[-.\s]?\d{3}[-.\s]?\d{4}', body)
    print(f"[*] Phone numbers: {len(phones)}")
    if phones:
        print(f"  Samples: {phones[:10]}")

    # Search for provider data patterns
    for field in ['phoneNumber', 'phone', 'businessPhone', 'website', 'webUrl',
                   'licenseNumber', 'license', 'email']:
        matches = re.findall(f'"{field}"[:\s]*"([^"]*)"', body, re.IGNORECASE)
        if matches:
            print(f"  {field}: {matches[:5]}")

    # Check for __NEXT_DATA__ or similar
    next_data = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.DOTALL)
    if next_data:
        print(f"\n[+] HomeAdvisor has __NEXT_DATA__!")
        data = json.loads(next_data.group(1))
        print(f"  Keys: {list(data.keys())}")
        if 'props' in data:
            pp = data.get('props', {}).get('pageProps', {})
            print(f"  pageProps keys: {list(pp.keys())[:15]}")
            with open('/var/www/vibe-marketing/scripts/scrapers/ha-nextdata.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"  Saved to ha-nextdata.json")

    # Check for LD+JSON
    ld_blocks = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', body, re.DOTALL)
    if ld_blocks:
        print(f"\n[+] HomeAdvisor LD+JSON blocks: {len(ld_blocks)}")
        for i, block in enumerate(ld_blocks):
            try:
                parsed = json.loads(block)
                if isinstance(parsed, dict):
                    t = parsed.get('@type', '?')
                    print(f"  [{i}] @type={t}")
                    if 'telephone' in str(parsed):
                        print(f"    HAS PHONE DATA!")
                        print(f"    {json.dumps(parsed, indent=2)[:500]}")
            except:
                pass

    # Check for window.__INITIAL_STATE__ or similar data injection
    state_match = re.search(r'window\.__(?:INITIAL_STATE|DATA|PROPS|PRELOADED)__\s*=\s*({.+?});?\s*</script>', body, re.DOTALL)
    if state_match:
        print(f"\n[+] Found window state injection!")
        try:
            state = json.loads(state_match.group(1))
            print(f"  Keys: {list(state.keys())[:10]}")
        except:
            print(f"  Raw: {state_match.group(1)[:300]}")

    # Save HA page
    with open('/var/www/vibe-marketing/scripts/scrapers/ha-rated-page.html', 'w') as f:
        f.write(body)
    print(f"\n  Saved HTML to ha-rated-page.html")

print("\n[*] Done.")
