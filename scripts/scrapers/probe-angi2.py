#!/usr/bin/env python3
"""
Probe Angi.com - debug response object.
"""

import json
from scrapling import Fetcher

PROXY = "http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823"
TARGET_URL = "https://www.angi.com/companylist/us/tx/austin/plumbing.htm"

fetcher = Fetcher()
response = fetcher.get(
    TARGET_URL,
    proxy=PROXY,
    timeout=30,
)

print(f"Status: {response.status}")
print(f"Type: {type(response)}")
print(f"Dir: {[x for x in dir(response) if not x.startswith('_')]}")
print()

# Try different ways to access content
for attr in ['text', 'content', 'body', 'html', 'raw', 'data', 'page_source']:
    try:
        val = getattr(response, attr, None)
        if val is not None:
            if isinstance(val, (str, bytes)):
                print(f"response.{attr}: type={type(val).__name__}, len={len(val)}")
                if len(val) > 0:
                    preview = val[:500] if isinstance(val, str) else val[:500].decode('utf-8', errors='replace')
                    print(f"  Preview: {preview[:300]}")
            else:
                print(f"response.{attr}: type={type(val).__name__}, val={str(val)[:200]}")
    except Exception as e:
        print(f"response.{attr}: ERROR {e}")

print()

# Check headers
try:
    headers = response.headers if hasattr(response, 'headers') else None
    if headers:
        print("Response headers:")
        for k, v in (headers.items() if hasattr(headers, 'items') else []):
            print(f"  {k}: {v}")
except Exception as e:
    print(f"Headers error: {e}")

# Check encoding
try:
    print(f"\nEncoding: {response.encoding if hasattr(response, 'encoding') else 'N/A'}")
except:
    pass

# Try the underlying response
try:
    if hasattr(response, 'adaptor'):
        print(f"\nAdaptor: {type(response.adaptor)}")
        print(f"Adaptor dir: {[x for x in dir(response.adaptor) if not x.startswith('_')]}")
except:
    pass
