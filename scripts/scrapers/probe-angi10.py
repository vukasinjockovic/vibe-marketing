#!/usr/bin/env python3
"""
Probe Angi.com - Phase 8:
1. Try the LPFE proxy with POST (it's a BFF proxy)
2. Try HomeAdvisor API with the leaked credentials
3. Download remaining chunks and find proListApi usage
"""

import json
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
fetcher = Fetcher()

# Get fresh token
r = fetcher.get("https://api.angi.com/api/landing-pages/token", proxy=PROXY, timeout=15)
token = r.body.decode('utf-8').strip().strip('"')
print(f"[*] Token: {token[:50]}...")

# === Part 1: Try LPFE proxy with POST ===
print("\n" + "=" * 60)
print("[*] Part 1: Try LPFE proxy with POST requests")
print("=" * 60)

proxy_url = "https://api.angi.com/api/lpfe/proxy"

# Different possible POST payloads the BFF might accept
payloads = [
    # GraphQL style
    {
        "label": "GraphQL query",
        "body": json.dumps({
            "query": "{ providers(city: \"Austin\", state: \"TX\", category: \"plumbing\") { name address rating } }"
        }),
    },
    # REST proxy style - route to pro-list service
    {
        "label": "Pro list proxy",
        "body": json.dumps({
            "path": "/pro-list",
            "params": {"city": "Austin", "state": "TX", "taskName": "plumbing"}
        }),
    },
    # Direct endpoint proxy
    {
        "label": "Directory endpoint",
        "body": json.dumps({
            "url": "/directory/listings",
            "city": "Austin",
            "state": "TX",
            "category": "plumbing"
        }),
    },
    # Minimal - just see what error we get
    {
        "label": "Empty POST",
        "body": "{}",
    },
]

for payload in payloads:
    print(f"\n[*] Trying: {payload['label']}")
    try:
        r = fetcher.post(
            proxy_url,
            proxy=PROXY,
            timeout=15,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://www.angi.com",
                "Referer": "https://www.angi.com/companylist/us/tx/austin/plumbing.htm",
            },
            data=payload['body'],
        )
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}")
        if body:
            try:
                data = json.loads(body)
                print(f"    JSON: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"    Raw: {body[:300]}")
    except Exception as e:
        print(f"    Error: {e}")

# === Part 2: Try HomeAdvisor API ===
print("\n" + "=" * 60)
print("[*] Part 2: Probe HomeAdvisor API with leaked credentials")
print("=" * 60)

# Found in config:
# haApiUsername: "angi_web_enroll"
# haApiAccesskey: "3savmTT6"
# haBaseUrl: "https://www.homeadvisor.com"

ha_endpoints = [
    # Common HA API patterns
    "https://www.homeadvisor.com/api/pro/search?taskId=12013&zip=78701",
    "https://www.homeadvisor.com/api/v1/pros?zip=78701&task=plumbing",
    "https://www.homeadvisor.com/api/directory?zip=78701&category=plumbing",
    # Pro profile API
    "https://www.homeadvisor.com/rated.Plumbers.12013.html",
]

ha_headers = {
    "Accept": "application/json",
    "x-api-username": "angi_web_enroll",
    "x-api-accesskey": "3savmTT6",
}

for url in ha_endpoints:
    print(f"\n[*] {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=15, headers=ha_headers)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}, Length: {len(body)}")
        if r.status == 200 and len(body) > 500:
            # Check if it's JSON
            try:
                data = json.loads(body)
                print(f"    [+] JSON response! Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                print(f"    Preview: {json.dumps(data, indent=2)[:800]}")
            except:
                # Check if it's HTML with data
                if 'serviceProviderId' in body or 'proName' in body:
                    print(f"    [+] HTML contains provider data!")
                else:
                    print(f"    HTML page ({len(body)} chars)")
    except Exception as e:
        print(f"    Error: {e}")

# === Part 3: Try the internal .angi.cloud endpoints ===
print("\n" + "=" * 60)
print("[*] Part 3: Try internal .angi.cloud endpoints")
print("=" * 60)

# From config: customerAttributesTraitsServiceBaseUrl: "https://customer-attributes-traits-service.proda.angi.cloud"
# And: unifiedProUpgradeBaseUrl: "https://unified-pro-upgrade-bff.proda.angi.cloud"
# These are internal services - probably not publicly accessible, but let's check

internal_urls = [
    "https://customer-attributes-traits-service.proda.angi.cloud/",
    "https://unified-pro-upgrade-bff.proda.angi.cloud/",
]

for url in internal_urls:
    print(f"\n[*] {url}")
    try:
        r = fetcher.get(url, proxy=PROXY, timeout=10)
        body = r.body.decode('utf-8', errors='replace')
        print(f"    Status: {r.status}, Length: {len(body)}")
        if body:
            print(f"    Preview: {body[:200]}")
    except Exception as e:
        print(f"    Error: {e}")

print("\n[*] Done.")
