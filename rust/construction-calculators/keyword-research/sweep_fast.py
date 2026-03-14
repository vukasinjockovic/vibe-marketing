#!/usr/bin/env python3
"""
Google Autocomplete Sweep for Construction Calculator Keywords
Uses concurrent requests for speed.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

OUTDIR = "/var/www/vibe-marketing/rust/construction-calculators/keyword-research"
CATDIR = os.path.join(OUTDIR, "categories")
os.makedirs(CATDIR, exist_ok=True)

def fetch_suggestions(query):
    """Fetch Google autocomplete suggestions for a query."""
    encoded = urllib.parse.quote(query)
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={encoded}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception as e:
        pass
    return []

def build_queries(base_keyword):
    """Build base + a-z queries for a keyword."""
    queries = [base_keyword]
    for c in "abcdefghijklmnopqrstuvwxyz":
        queries.append(f"{base_keyword} {c}")
    return queries

def sweep_category(name, keywords, executor):
    """Sweep all keywords in a category."""
    all_queries = []
    for kw in keywords:
        all_queries.extend(build_queries(kw))
    
    results = set()
    futures = {executor.submit(fetch_suggestions, q): q for q in all_queries}
    
    done_count = 0
    for future in as_completed(futures):
        done_count += 1
        suggestions = future.result()
        for s in suggestions:
            results.add(s)
    
    # Save category file
    cat_file = os.path.join(CATDIR, f"{name}.txt")
    sorted_results = sorted(results)
    with open(cat_file, "w") as f:
        for r in sorted_results:
            f.write(r + "\n")
    
    print(f"  {name}: {len(results)} unique suggestions from {len(all_queries)} queries")
    return name, results


# Define all categories
CATEGORIES = {
    "core-materials": [
        "concrete calculator",
        "lumber calculator",
        "roofing calculator",
        "drywall calculator",
        "paint calculator",
        "gravel calculator",
        "mulch calculator",
        "fence calculator",
        "deck calculator",
        "flooring calculator",
        "tile calculator",
        "brick calculator",
        "insulation calculator",
        "siding calculator",
        "stucco calculator",
    ],
    "construction-tasks": [
        "how many bags of concrete",
        "how much gravel do i need",
        "how much paint do i need",
        "how many shingles do i need",
        "how much flooring do i need",
        "how many deck boards do i need",
        "how much mulch do i need",
        "how many bricks do i need",
        "how much concrete do i need",
        "how much lumber do i need",
    ],
    "cost-calculators": [
        "concrete cost calculator",
        "roofing cost calculator",
        "deck cost calculator",
        "fence cost calculator",
        "flooring cost calculator",
        "drywall cost calculator",
        "siding cost calculator",
        "patio cost calculator",
    ],
    "unit-conversions": [
        "cubic yards to bags of concrete",
        "square feet to squares roofing",
        "board feet calculator",
        "cubic yards calculator",
        "square footage calculator",
    ],
    "electrical-plumbing": [
        "wire gauge calculator",
        "voltage drop calculator",
        "electrical load calculator",
        "pipe sizing calculator",
    ],
    "landscaping": [
        "paver calculator",
        "retaining wall calculator",
        "topsoil calculator",
        "sod calculator",
        "landscape rock calculator",
    ],
}

def main():
    start = time.time()
    print("=== Google Autocomplete Sweep ===")
    print(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    all_suggestions = set()
    category_counts = {}
    category_results = {}
    
    # Process categories sequentially but queries within each category in parallel
    # Use 15 threads to avoid hammering too hard
    with ThreadPoolExecutor(max_workers=15) as executor:
        for cat_name, keywords in CATEGORIES.items():
            name, results = sweep_category(cat_name, keywords, executor)
            category_counts[name] = len(results)
            category_results[name] = results
            all_suggestions.update(results)
            # Small pause between categories
            time.sleep(0.5)
    
    # Write merged file
    final_file = os.path.join(OUTDIR, "autocomplete-suggestions.txt")
    sorted_all = sorted(all_suggestions)
    with open(final_file, "w") as f:
        for s in sorted_all:
            f.write(s + "\n")
    
    elapsed = time.time() - start
    print(f"\n=== COMPLETE in {elapsed:.1f}s ===")
    print(f"Total unique suggestions: {len(all_suggestions)}")
    print(f"\nPer-category counts:")
    for name, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")
    print(f"\nOutput: {final_file}")
    
    # Also write category results as JSON for the summary script
    with open(os.path.join(OUTDIR, "category-data.json"), "w") as f:
        json.dump({k: sorted(v) for k, v in category_results.items()}, f, indent=2)

if __name__ == "__main__":
    main()
