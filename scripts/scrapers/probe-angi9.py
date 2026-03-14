#!/usr/bin/env python3
"""
Probe Angi.com - Phase 7: Extract the API config + all contractor data from RSC payload.
"""

import json
import re

# Read saved RSC payload
with open('/var/www/vibe-marketing/scripts/scrapers/angi-rsc-full.txt', 'r') as f:
    rsc = f.read()

lines = rsc.split('\n')

# === Part 1: Extract the config (Row 15) ===
print("=" * 60)
print("[*] Part 1: Extract API config from RSC Row 15")
print("=" * 60)

for line in lines:
    match = re.match(r'^15:(.+)$', line)
    if match:
        try:
            config = json.loads(match.group(1))
            print(json.dumps(config, indent=2))
            with open('/var/www/vibe-marketing/scripts/scrapers/angi-api-config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print("\n[+] Saved to angi-api-config.json")
        except:
            print(f"Raw: {match.group(1)[:1000]}")
        break

# === Part 2: Extract ALL contractor data from RSC ===
print("\n" + "=" * 60)
print("[*] Part 2: Extract contractor data from RSC payload")
print("=" * 60)

# Find all lines with serviceProviderId, businessName, businessInfo
contractors = []

for i, line in enumerate(lines):
    # Look for business detail blocks
    if 'serviceProviderName' in line or 'businessName' in line:
        # Try to extract the full JSON-like data
        # RSC format puts data in various forms - look for key patterns

        # Extract serviceProviderId
        sp_id_match = re.search(r'"serviceProviderId"[:\s]*(\d+)', line)
        sp_name_match = re.search(r'"serviceProviderName"[:\s]*"([^"]+)"', line)
        biz_name_match = re.search(r'"businessName"[:\s]*"([^"]+)"', line)
        desc_match = re.search(r'"businessDescription"[:\s]*"([^"]*)"', line)
        logo_match = re.search(r'"serviceProviderLogoUrl"[:\s]*"([^"]+)"', line)
        slug_match = re.search(r'"companyListSlug"[:\s]*"([^"]+)"', line)

        if sp_id_match or biz_name_match:
            contractor = {
                'line': i,
                'serviceProviderId': sp_id_match.group(1) if sp_id_match else None,
                'serviceProviderName': sp_name_match.group(1) if sp_name_match else None,
                'businessName': biz_name_match.group(1) if biz_name_match else None,
                'businessDescription': desc_match.group(1)[:100] if desc_match else None,
                'logoUrl': logo_match.group(1) if logo_match else None,
                'slug': slug_match.group(1) if slug_match else None,
            }
            contractors.append(contractor)

print(f"[+] Found {len(contractors)} contractor entries")
for c in contractors:
    name = c.get('businessName') or c.get('serviceProviderName') or '?'
    print(f"  ID={c.get('serviceProviderId', '?'):>12s}  {name}")
    if c.get('slug'):
        print(f"    Slug: {c['slug']}")

# === Part 3: Extract ALL unique data fields from RSC ===
print("\n" + "=" * 60)
print("[*] Part 3: Find all data fields in RSC (what's available)")
print("=" * 60)

# Find all JSON-like key names in the full payload
all_keys = set(re.findall(r'"([a-zA-Z_][a-zA-Z0-9_]{2,30})":', rsc))
interesting_keys = [k for k in sorted(all_keys) if any(
    term in k.lower() for term in [
        'address', 'phone', 'email', 'business', 'provider', 'service',
        'rating', 'review', 'city', 'state', 'zip', 'postal', 'street',
        'license', 'year', 'employee', 'website', 'url', 'name', 'contact',
        'price', 'cost', 'award', 'certif', 'insur', 'bond'
    ]
)]

print(f"[+] Data fields found ({len(interesting_keys)}):")
for k in interesting_keys:
    print(f"    {k}")

# === Part 4: Extract contact info blocks ===
print("\n" + "=" * 60)
print("[*] Part 4: Extract contact/address blocks")
print("=" * 60)

for i, line in enumerate(lines):
    if 'streetAddress' in line or 'postalCode' in line:
        # Try to get address data
        street = re.search(r'"streetAddress"[:\s]*"([^"]*)"', line)
        city = re.search(r'"addressLocality"[:\s]*"([^"]*)"', line)
        state = re.search(r'"addressRegion"[:\s]*"([^"]*)"', line)
        zip_code = re.search(r'"postalCode"[:\s]*"([^"]*)"', line)

        if street or city:
            addr = f"{street.group(1) if street else '?'}, {city.group(1) if city else '?'}, {state.group(1) if state else '?'} {zip_code.group(1) if zip_code else '?'}"
            print(f"  Line {i}: {addr}")

# === Part 5: Look for phone numbers, ratings, review counts ===
print("\n" + "=" * 60)
print("[*] Part 5: Extract ratings and review data")
print("=" * 60)

for i, line in enumerate(lines):
    if '"overallRating"' in line or '"numberOfRatings"' in line or '"aggregateRating"' in line:
        rating = re.search(r'"overallRating"[:\s]*"?(\d+\.?\d*)"?', line)
        count = re.search(r'"numberOfRatings"[:\s]*"?(\d+)"?', line)
        total = re.search(r'"totalNumberOfRatings"[:\s]*"?(\d+)"?', line)

        print(f"  Line {i}: rating={rating.group(1) if rating else '?'}, count={count.group(1) if count else '?'}, total={total.group(1) if total else '?'}")
        # Show context
        print(f"    Context: ...{line[max(0, line.find('Rating')-30):line.find('Rating')+80]}...")

# === Part 6: The biggest RSC row (371K chars) likely has everything ===
print("\n" + "=" * 60)
print("[*] Part 6: Analyze the largest RSC row (371K chars)")
print("=" * 60)

for line in lines:
    if len(line) > 300000:
        # This is the mega row
        print(f"[*] Mega row length: {len(line)}")

        # Count contractor mentions
        biz_mentions = len(re.findall(r'"businessName"', line))
        print(f"[*] businessName mentions: {biz_mentions}")

        sp_ids = re.findall(r'"serviceProviderId"[:\s]*(\d+)', line)
        print(f"[*] serviceProviderIds: {len(sp_ids)} -> {sp_ids}")

        # Extract a full contractor block
        # Find first serviceProviderId and grab surrounding context
        idx = line.find('"serviceProviderId"')
        if idx >= 0:
            block = line[max(0, idx-200):idx+2000]
            print(f"\n[*] Sample contractor block:")
            print(block[:2000])

        break

print("\n[*] Done.")
