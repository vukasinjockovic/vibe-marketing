#!/usr/bin/env python3
"""
Probe Angi.com - parse the 1.5MB HTML body for __NEXT_DATA__ and API endpoints.
"""

import json
import re
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"

def probe_page(url, label):
    print(f"\n{'='*60}")
    print(f"[*] Probing {label}: {url}")
    print(f"{'='*60}")

    fetcher = Fetcher()
    response = fetcher.get(url, proxy=PROXY, timeout=30)

    print(f"[*] Status: {response.status}")
    html = response.body.decode('utf-8', errors='replace')
    print(f"[*] HTML length: {len(html)} chars")

    # === 1. __NEXT_DATA__ ===
    next_data_match = re.search(
        r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )

    if next_data_match:
        print(f"\n[+] FOUND __NEXT_DATA__! ({len(next_data_match.group(1))} chars)")
        try:
            data = json.loads(next_data_match.group(1))
            print(f"[+] Top keys: {list(data.keys())}")

            if 'props' in data:
                props = data['props']
                print(f"[+] props keys: {list(props.keys())}")

                if 'pageProps' in props:
                    pp = props['pageProps']
                    print(f"[+] pageProps keys: {list(pp.keys())}")

                    # Recursively show structure (2 levels deep)
                    for k, v in pp.items():
                        if isinstance(v, dict):
                            print(f"    {k}: dict with keys {list(v.keys())[:10]}")
                            for k2, v2 in list(v.items())[:5]:
                                if isinstance(v2, dict):
                                    print(f"      {k2}: dict {list(v2.keys())[:8]}")
                                elif isinstance(v2, list):
                                    print(f"      {k2}: list[{len(v2)}]")
                                    if v2 and isinstance(v2[0], dict):
                                        print(f"        [0] keys: {list(v2[0].keys())[:10]}")
                                else:
                                    print(f"      {k2}: {type(v2).__name__} = {str(v2)[:80]}")
                        elif isinstance(v, list):
                            print(f"    {k}: list[{len(v)}]")
                            if v and isinstance(v[0], dict):
                                print(f"      [0] keys: {list(v[0].keys())[:15]}")
                                # Show a sample entry
                                sample = v[0]
                                for sk, sv in list(sample.items())[:8]:
                                    print(f"        {sk}: {str(sv)[:100]}")
                        else:
                            print(f"    {k}: {type(v).__name__} = {str(v)[:100]}")

            # Save full data
            outfile = f'/var/www/vibe-marketing/scripts/scrapers/angi-{label}-nextdata.json'
            with open(outfile, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\n[+] Saved to {outfile}")

        except json.JSONDecodeError as e:
            print(f"[-] JSON parse error: {e}")
            raw = next_data_match.group(1)[:5000]
            print(f"[*] Raw preview: {raw[:500]}")
    else:
        print("\n[-] No __NEXT_DATA__ found")

    # === 2. API endpoints in HTML ===
    api_patterns = [
        (r'https?://[^"\'\s<>]*api[^"\'\s<>]*', 'API URLs'),
        (r'https?://[^"\'\s<>]*/graphql[^"\'\s<>]*', 'GraphQL'),
        (r'"(/api/[^"]+)"', 'Relative /api/ paths'),
        (r'"(/_next/data/[^"]+)"', 'Next.js data routes'),
        (r'fetch\(["\']([^"\']+)["\']', 'fetch() calls'),
    ]

    print(f"\n[*] Scanning for API endpoints...")
    for pattern, name in api_patterns:
        matches = set(re.findall(pattern, html))
        matches = {m for m in matches if len(m) < 300 and 'data:' not in m}
        if matches:
            print(f"\n[+] {name} ({len(matches)} found):")
            for m in sorted(matches)[:15]:
                print(f"    {m}")

    # === 3. Schema.org LD+JSON ===
    ld_blocks = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL
    )
    if ld_blocks:
        print(f"\n[+] Schema.org LD+JSON ({len(ld_blocks)} blocks):")
        for i, block in enumerate(ld_blocks):
            try:
                parsed = json.loads(block)
                if isinstance(parsed, dict):
                    print(f"    [{i}] @type={parsed.get('@type', '?')}, keys={list(parsed.keys())[:8]}")
                elif isinstance(parsed, list):
                    for item in parsed[:3]:
                        if isinstance(item, dict):
                            print(f"    [{i}] @type={item.get('@type', '?')}")
            except:
                print(f"    [{i}] parse error ({len(block)} chars)")

    return html


# Probe listing page
html1 = probe_page(
    "https://www.angi.com/companylist/us/tx/austin/plumbing.htm",
    "listing"
)

# Extract a contractor detail URL from the listing page
detail_urls = re.findall(r'href="(/companylist/us/[^"]*reviews-[^"]+\.htm)"', html1)
if detail_urls:
    print(f"\n[*] Found {len(detail_urls)} contractor detail URLs in listing")
    print(f"[*] Sample: {detail_urls[0]}")

    # Probe first contractor detail page
    probe_page(
        f"https://www.angi.com{detail_urls[0]}",
        "detail"
    )
else:
    print("\n[-] No contractor detail URLs found in listing HTML")
    # Try alternate patterns
    alt_urls = re.findall(r'href="([^"]*reviews-\d+[^"]*)"', html1)
    if alt_urls:
        print(f"[*] Found alternate review URLs: {alt_urls[:5]}")

print("\n[*] Probe complete.")
