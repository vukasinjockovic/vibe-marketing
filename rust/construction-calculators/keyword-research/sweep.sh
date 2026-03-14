#!/bin/bash
# Google Autocomplete Sweep for Construction Calculator Keywords
# Fetches suggestions for base queries + alphabet expansions

OUTDIR="/var/www/vibe-marketing/rust/construction-calculators/keyword-research"
RAWFILE="$OUTDIR/raw-suggestions.txt"
CATDIR="$OUTDIR/categories"
mkdir -p "$CATDIR"

> "$RAWFILE"

fetch_suggestions() {
    local query="$1"
    local category="$2"
    local encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")
    local result=$(curl -s "https://suggestqueries.google.com/complete/search?client=firefox&q=${encoded}" 2>/dev/null)
    if [ -n "$result" ]; then
        # Extract suggestions from JSON array
        echo "$result" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if len(data) > 1:
        for s in data[1]:
            print(s)
except:
    pass
" >> "$CATDIR/$category.txt"
    fi
}

run_category() {
    local category="$1"
    shift
    local queries=("$@")

    echo "=== Category: $category ==="
    > "$CATDIR/$category.txt"

    for query in "${queries[@]}"; do
        echo "  Fetching: $query"
        fetch_suggestions "$query" "$category"
        # Small delay to be polite
        sleep 0.15

        # Alphabet expansion
        for letter in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
            fetch_suggestions "$query $letter" "$category"
            sleep 0.1
        done
    done

    # Deduplicate category file
    sort -u "$CATDIR/$category.txt" -o "$CATDIR/$category.txt"
    local count=$(wc -l < "$CATDIR/$category.txt")
    echo "  → $count unique suggestions for $category"
}

# Category 1: Core construction materials
run_category "core-materials" \
    "concrete calculator" \
    "lumber calculator" \
    "roofing calculator" \
    "drywall calculator" \
    "paint calculator" \
    "gravel calculator" \
    "mulch calculator" \
    "fence calculator" \
    "deck calculator" \
    "flooring calculator" \
    "tile calculator" \
    "brick calculator" \
    "insulation calculator" \
    "siding calculator" \
    "stucco calculator"

# Category 2: Specific construction tasks
run_category "construction-tasks" \
    "how many bags of concrete" \
    "how much gravel do i need" \
    "how much paint do i need" \
    "how many shingles do i need" \
    "how much flooring do i need" \
    "how many deck boards do i need" \
    "how much mulch do i need" \
    "how many bricks do i need" \
    "how much concrete do i need" \
    "how much lumber do i need"

# Category 3: Cost calculators
run_category "cost-calculators" \
    "concrete cost calculator" \
    "roofing cost calculator" \
    "deck cost calculator" \
    "fence cost calculator" \
    "flooring cost calculator" \
    "drywall cost calculator" \
    "siding cost calculator" \
    "patio cost calculator"

# Category 4: Unit conversions
run_category "unit-conversions" \
    "cubic yards to bags of concrete" \
    "square feet to squares roofing" \
    "board feet calculator" \
    "cubic yards calculator" \
    "square footage calculator"

# Category 5: Electrical/plumbing
run_category "electrical-plumbing" \
    "wire gauge calculator" \
    "voltage drop calculator" \
    "electrical load calculator" \
    "pipe sizing calculator"

# Category 6: Landscaping
run_category "landscaping" \
    "paver calculator" \
    "retaining wall calculator" \
    "topsoil calculator" \
    "sod calculator" \
    "landscape rock calculator"

echo ""
echo "=== Merging all categories ==="

# Merge all category files into one deduplicated file
cat "$CATDIR"/*.txt | sort -u > "$OUTDIR/autocomplete-suggestions.txt"
TOTAL=$(wc -l < "$OUTDIR/autocomplete-suggestions.txt")
echo "Total unique suggestions: $TOTAL"

# Print per-category counts
echo ""
echo "=== Per-category counts ==="
for f in "$CATDIR"/*.txt; do
    name=$(basename "$f" .txt)
    count=$(wc -l < "$f")
    echo "  $name: $count"
done

echo ""
echo "Done! Results in $OUTDIR/autocomplete-suggestions.txt"
