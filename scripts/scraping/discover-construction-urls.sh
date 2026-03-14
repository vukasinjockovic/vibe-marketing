#!/usr/bin/env bash
#
# Construction URL Discovery Script
# Discovers article/guide/tutorial URLs from construction sites via sitemaps and GAU.
# Stores in SQLite for the content scraper to consume.
#
# Usage:
#   ./scripts/scraping/discover-construction-urls.sh --sitemap                    # All sitemap domains
#   ./scripts/scraping/discover-construction-urls.sh --gau                        # All GAU domains
#   ./scripts/scraping/discover-construction-urls.sh --all                        # Both methods
#   ./scripts/scraping/discover-construction-urls.sh --sitemap --domain fixr.com  # Single domain
#   ./scripts/scraping/discover-construction-urls.sh --stats                      # Show DB stats
#
# Output: knowledge/construction/web-archives/url-inventory.db (SQLite)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/config"
DB_DIR="${PROJECT_DIR}/knowledge/construction/web-archives"
DB_FILE="${DB_DIR}/url-inventory.db"
DOMAINS_JSON="${CONFIG_DIR}/domains.json"
CATEGORIES_JSON="${CONFIG_DIR}/categories.json"

GAU_BIN="${HOME}/go/bin/gau"
TOR_CONFIG="/etc/tor/torrc.instances"

# Counters
SESSION_NEW=0
SESSION_TOTAL=0
SESSION_START=0

# Tor ports (loaded lazily)
TOR_PORTS=()

mkdir -p "$DB_DIR"

# ─── Tor Support ────────────────────────────────────────────────────────────────

load_tor_ports() {
    if [ "${#TOR_PORTS[@]}" -gt 0 ]; then
        return
    fi
    if [ ! -f "$TOR_CONFIG" ]; then
        echo "  ERROR: Tor instances config not found at ${TOR_CONFIG}"
        echo "  Install: /var/www/onlyfansapi/scripts/tor-multi/setup.sh --instances 100"
        return 1
    fi
    while IFS= read -r line; do
        if [[ "$line" =~ ^SocksPort[[:space:]]+([0-9]+) ]]; then
            TOR_PORTS+=("${BASH_REMATCH[1]}")
        fi
    done < "$TOR_CONFIG"
    echo "  Tor: ${#TOR_PORTS[@]} SOCKS ports loaded"
}

get_tor_proxy() {
    local index="$1"
    local port_idx=$((index % ${#TOR_PORTS[@]}))
    echo "socks5://127.0.0.1:${TOR_PORTS[$port_idx]}"
}

# ─── Database ───────────────────────────────────────────────────────────────────

ensure_db() {
    sqlite3 "$DB_FILE" <<'SQL'
CREATE TABLE IF NOT EXISTS urls (
    url TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    path TEXT NOT NULL,
    category TEXT,
    content_type TEXT,
    discovered_via TEXT,
    scrape_status TEXT DEFAULT 'pending',
    scraped_at TEXT,
    content_hash TEXT,
    title TEXT,
    word_count INTEGER
);
CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain);
CREATE INDEX IF NOT EXISTS idx_urls_status ON urls(scrape_status);
CREATE INDEX IF NOT EXISTS idx_urls_category ON urls(category);
CREATE INDEX IF NOT EXISTS idx_urls_domain_status ON urls(domain, scrape_status);
SQL
    SESSION_TOTAL=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls;")
    SESSION_START="$SESSION_TOTAL"
}

# ─── URL Classification ────────────────────────────────────────────────────────

# Build classification regex from categories.json (cached for the session)
CATEGORY_RULES=""
load_category_rules() {
    if [ -z "$CATEGORY_RULES" ] && [ -f "$CATEGORIES_JSON" ]; then
        CATEGORY_RULES=$(python3 -c "
import json, sys
with open('$CATEGORIES_JSON') as f:
    data = json.load(f)
for rule in data['rules']:
    print(rule['pattern'] + '\t' + rule['category'])
" 2>/dev/null || true)
    fi
}

classify_url() {
    local url="$1"
    local path
    path=$(echo "$url" | sed 's|https\?://[^/]*/||' | tr '[:upper:]' '[:lower:]')

    load_category_rules

    if [ -n "$CATEGORY_RULES" ]; then
        while IFS=$'\t' read -r pattern category; do
            if echo "$path" | grep -qiE "$pattern" 2>/dev/null; then
                echo "$category"
                return
            fi
        done <<< "$CATEGORY_RULES"
    fi

    echo "general"
}

# Detect content type from URL path
detect_content_type() {
    local url="$1"
    local lower
    lower=$(echo "$url" | tr '[:upper:]' '[:lower:]')

    if echo "$lower" | grep -qE 'how-to|how_to|diy|tutorial|step-by-step'; then
        echo "how_to"
    elif echo "$lower" | grep -qE 'cost|price|estimat|budget|how-much'; then
        echo "cost_guide"
    elif echo "$lower" | grep -qE 'vs-|versus|compar|difference-between'; then
        echo "comparison"
    elif echo "$lower" | grep -qE 'calculat|convert|formula'; then
        echo "calculator"
    elif echo "$lower" | grep -qE 'review|best-|top-[0-9]'; then
        echo "review"
    elif echo "$lower" | grep -qE 'guide|everything-you-need|complete-guide'; then
        echo "guide"
    else
        echo "article"
    fi
}

# Filter: is this an article URL (not image/css/js/admin)?
is_article_url() {
    local url="$1"
    local lower
    lower=$(echo "$url" | tr '[:upper:]' '[:lower:]')

    # Reject non-article patterns
    if echo "$lower" | grep -qE '\.(jpg|jpeg|png|gif|svg|webp|ico|css|js|xml|pdf|zip|mp4|mp3|woff|woff2|ttf|eot)(\?|$)'; then
        return 1
    fi
    if echo "$lower" | grep -qE '/(wp-admin|wp-content/uploads|wp-includes|wp-json|feed|rss|amp/|/tag/|/author/|/page/[0-9]|/category/$|login|signup|cart|checkout|account|search\?)'; then
        return 1
    fi
    if echo "$lower" | grep -qE '/(ads|privacy|terms|about-us|contact-us|subscribe|newsletter|#)'; then
        return 1
    fi
    # Require a meaningful path (not just domain root)
    local path
    path=$(echo "$url" | sed 's|https\?://[^/]*||')
    if [ -z "$path" ] || [ "$path" = "/" ]; then
        return 1
    fi
    return 0
}

# ─── Batch Insert ───────────────────────────────────────────────────────────────

upsert_urls() {
    local domain="$1"
    local via="$2"
    local tmp_urls
    tmp_urls=$(mktemp /tmp/construction_urls_XXXXXX.txt)

    # Read stdin (URLs, one per line) and filter
    while IFS= read -r url; do
        [ -z "$url" ] && continue
        is_article_url "$url" && echo "$url" >> "$tmp_urls"
    done

    local count
    count=$(wc -l < "$tmp_urls" | tr -d '[:space:]')
    if [ "$count" -eq 0 ]; then
        rm -f "$tmp_urls"
        return 0
    fi

    local sql_file
    sql_file=$(mktemp /tmp/construction_insert_XXXXXX.sql)
    echo "BEGIN TRANSACTION;" > "$sql_file"

    while IFS= read -r url; do
        [ -z "$url" ] && continue
        local escaped="${url//\'/\'\'}"
        local path
        path=$(echo "$url" | sed 's|https\?://[^/]*||')
        local path_escaped="${path//\'/\'\'}"
        local category
        category=$(classify_url "$url")
        local content_type
        content_type=$(detect_content_type "$url")
        echo "INSERT OR IGNORE INTO urls (url, domain, path, category, content_type, discovered_via) VALUES ('${escaped}', '${domain}', '${path_escaped}', '${category}', '${content_type}', '${via}');" >> "$sql_file"
    done < "$tmp_urls"

    echo "COMMIT;" >> "$sql_file"

    local before
    before=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls;")
    sqlite3 "$DB_FILE" < "$sql_file"
    local after
    after=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls;")
    local inserted=$((after - before))

    SESSION_NEW=$((SESSION_NEW + inserted))
    SESSION_TOTAL="$after"

    rm -f "$sql_file" "$tmp_urls"

    if [ "$inserted" -gt 0 ]; then
        echo "    +${inserted} new URLs (${after} total in DB)"
    fi
}

# ─── Sitemap Discovery ─────────────────────────────────────────────────────────

fetch_sitemap_urls() {
    local sitemap_url="$1"
    # Fetch sitemap XML → extract <loc> URLs
    curl -sf --max-time 30 --compressed "$sitemap_url" 2>/dev/null \
        | grep -oP '<loc>\K[^<]+' \
        || true
}

run_sitemap_domain() {
    local domain="$1"
    echo "  [sitemap] ${domain}"

    local sitemap_index sitemap_filter
    sitemap_index=$(python3 -c "
import json
with open('$DOMAINS_JSON') as f:
    d = json.load(f)
cfg = d.get('$domain', {})
print(cfg.get('sitemap_index') or '')
" 2>/dev/null)

    sitemap_filter=$(python3 -c "
import json
with open('$DOMAINS_JSON') as f:
    d = json.load(f)
cfg = d.get('$domain', {})
print(cfg.get('sitemap_filter') or '')
" 2>/dev/null)

    if [ -z "$sitemap_index" ]; then
        echo "    No sitemap_index configured for ${domain}, skipping"
        return
    fi

    echo "    Fetching sitemap index: ${sitemap_index}"

    # Get sub-sitemap URLs from the index
    local sub_sitemaps
    sub_sitemaps=$(fetch_sitemap_urls "$sitemap_index")

    if [ -z "$sub_sitemaps" ]; then
        # Maybe the sitemap_index IS the sitemap (not an index)
        echo "    No sub-sitemaps found, treating as direct sitemap"
        fetch_sitemap_urls "$sitemap_index" | upsert_urls "$domain" "sitemap"
        return
    fi

    # Filter sub-sitemaps if pattern configured
    local filtered_sitemaps
    if [ -n "$sitemap_filter" ]; then
        filtered_sitemaps=$(echo "$sub_sitemaps" | grep -iE "$sitemap_filter" || true)
        # If filter matched nothing, use all (filter might be wrong)
        if [ -z "$filtered_sitemaps" ]; then
            echo "    Filter '${sitemap_filter}' matched nothing, using all sub-sitemaps"
            filtered_sitemaps="$sub_sitemaps"
        fi
    else
        filtered_sitemaps="$sub_sitemaps"
    fi

    local sm_count
    sm_count=$(echo "$filtered_sitemaps" | wc -l | tr -d '[:space:]')
    echo "    Processing ${sm_count} sub-sitemaps..."

    local idx=0
    echo "$filtered_sitemaps" | while IFS= read -r sm_url; do
        [ -z "$sm_url" ] && continue
        idx=$((idx + 1))
        printf "\r    Sub-sitemap %d/%d: %s   " "$idx" "$sm_count" "$(basename "$sm_url")"
        fetch_sitemap_urls "$sm_url" | upsert_urls "$domain" "sitemap"
        sleep 0.5  # Be nice to sitemap servers
    done
    echo ""
}

run_sitemap() {
    echo "=== Sitemap Discovery ==="

    local domains
    if [ -n "${FILTER_DOMAIN:-}" ]; then
        domains="$FILTER_DOMAIN"
    else
        domains=$(python3 -c "
import json
with open('$DOMAINS_JSON') as f:
    d = json.load(f)
for domain, cfg in d.items():
    if 'sitemap' in cfg.get('method', []):
        print(domain)
" 2>/dev/null)
    fi

    if [ -z "$domains" ]; then
        echo "  No sitemap domains configured"
        return
    fi

    while IFS= read -r domain; do
        [ -z "$domain" ] && continue
        run_sitemap_domain "$domain"
    done <<< "$domains"

    echo "  Sitemap discovery complete."
}

# ─── GAU Discovery ─────────────────────────────────────────────────────────────

run_gau_domain() {
    local domain="$1"
    local domain_idx="${2:-0}"

    local proxy_args=""
    if [ "${USE_TOR:-}" = "1" ]; then
        local proxy
        proxy=$(get_tor_proxy "$domain_idx")
        proxy_args="--proxy ${proxy}"
        echo "  [gau+tor] ${domain} (via ${proxy})"
    else
        echo "  [gau] ${domain}"
    fi

    if [ ! -f "$GAU_BIN" ]; then
        echo "    GAU not found at ${GAU_BIN}. Install: go install github.com/lc/gau/v2/cmd/gau@latest"
        return 1
    fi

    local batch_file
    batch_file=$(mktemp /tmp/gau_construction_XXXXXX.txt)

    local url_count=0
    local batch_size=200
    local threads="${GAU_WORKERS:-3}"

    while IFS= read -r url; do
        echo "$url" >> "$batch_file"
        url_count=$((url_count + 1))

        if [ $((url_count % batch_size)) -eq 0 ]; then
            cat "$batch_file" | upsert_urls "$domain" "gau"
            > "$batch_file"
            printf "\r    %d URLs processed..." "$url_count"
        fi
    done < <("$GAU_BIN" "$domain" \
        --threads "$threads" \
        --retries 3 \
        --timeout 60 \
        $proxy_args \
        --providers wayback,commoncrawl,otx,urlscan 2>/dev/null || true)

    # Flush remaining
    if [ -s "$batch_file" ]; then
        cat "$batch_file" | upsert_urls "$domain" "gau"
    fi
    rm -f "$batch_file"

    echo ""
    echo "    GAU done for ${domain}: ${url_count} raw URLs processed"
}

# ─── Wayback CDX Direct (Parallel + Tor) ────────────────────────────────────────

run_wayback_domain() {
    local domain="$1"
    local workers="${WAYBACK_WORKERS:-10}"
    local pages_dir
    pages_dir=$(mktemp -d /tmp/wayback_${domain//\./_}_XXXXXX)

    echo "  [wayback+tor] ${domain} (${workers} workers)"

    # Get total pages
    local proxy_args=""
    if [ "${USE_TOR:-}" = "1" ] && [ "${#TOR_PORTS[@]}" -gt 0 ]; then
        proxy_args="--proxy socks5h://127.0.0.1:${TOR_PORTS[0]}"
    fi

    local num_pages
    num_pages=$(curl -sf --max-time 30 $proxy_args \
        "http://web.archive.org/cdx/search/cdx?url=${domain}/*&output=text&fl=original&collapse=urlkey&showNumPages=true" 2>/dev/null \
        | head -1 | tr -d '[:space:]' || echo "1")

    if ! [[ "$num_pages" =~ ^[0-9]+$ ]] || [ "$num_pages" -eq 0 ]; then
        echo "    Could not determine page count, trying single page..."
        num_pages=1
    fi
    echo "    ${num_pages} pages to fetch"

    # Semaphore for parallel workers
    local sem_fifo
    sem_fifo=$(mktemp -u /tmp/wayback_sem_XXXXXX)
    mkfifo "$sem_fifo"
    exec 7<>"$sem_fifo"
    rm -f "$sem_fifo"
    for (( i=0; i<workers; i++ )); do echo >&7; done

    local completed_file
    completed_file=$(mktemp /tmp/wayback_done_XXXXXX.txt)
    : > "$completed_file"
    local failed_file
    failed_file=$(mktemp /tmp/wayback_fail_XXXXXX.txt)
    : > "$failed_file"

    for (( p=0; p<num_pages; p++ )); do
        read -u 7

        local page_proxy=""
        if [ "${USE_TOR:-}" = "1" ] && [ "${#TOR_PORTS[@]}" -gt 0 ]; then
            local port_idx=$((p % ${#TOR_PORTS[@]}))
            page_proxy="--proxy socks5h://127.0.0.1:${TOR_PORTS[$port_idx]}"
        fi

        (
            local out_file="${pages_dir}/page_${p}.txt"
            local ok=0
            for attempt in 1 2 3; do
                if curl -sf --max-time 30 $page_proxy \
                    "http://web.archive.org/cdx/search/cdx?url=${domain}/*&output=text&fl=original&collapse=urlkey&page=${p}" \
                    -o "$out_file" 2>/dev/null; then
                    ok=1
                    break
                fi
                sleep "$((attempt * 2))"
            done
            if [ "$ok" -eq 1 ] && [ -s "$out_file" ]; then
                echo "1" >> "$completed_file"
            else
                rm -f "$out_file"
                echo "$p" >> "$failed_file"
            fi
            local done_count
            done_count=$(wc -l < "$completed_file" 2>/dev/null | tr -d '[:space:]')
            local fail_count
            fail_count=$(wc -l < "$failed_file" 2>/dev/null | tr -d '[:space:]')
            printf "\r    Pages: %d/%d done (%d failed)   " "$done_count" "$num_pages" "$fail_count"
            echo >&7
        ) &
    done

    wait
    exec 7>&-
    echo ""

    # Process all downloaded pages
    local all_merged
    all_merged=$(mktemp /tmp/wayback_merged_XXXXXX.txt)
    for f in "${pages_dir}"/page_*.txt; do
        [ -f "$f" ] || continue
        cat "$f" >> "$all_merged"
    done

    if [ -s "$all_merged" ]; then
        local total_raw
        total_raw=$(wc -l < "$all_merged" | tr -d '[:space:]')
        echo "    Processing ${total_raw} raw URLs..."
        cat "$all_merged" | upsert_urls "$domain" "wayback"
    fi

    rm -rf "$pages_dir" "$all_merged" "$completed_file" "$failed_file"
}

run_gau() {
    echo "=== GAU Discovery ==="

    if [ "${USE_TOR:-}" = "1" ]; then
        load_tor_ports || return 1
    fi

    local domains
    if [ -n "${FILTER_DOMAIN:-}" ]; then
        domains="$FILTER_DOMAIN"
    else
        domains=$(python3 -c "
import json
with open('$DOMAINS_JSON') as f:
    d = json.load(f)
for domain, cfg in d.items():
    if 'gau' in cfg.get('method', []):
        print(domain)
" 2>/dev/null)
    fi

    if [ -z "$domains" ]; then
        echo "  No GAU domains configured"
        return
    fi

    local idx=0
    while IFS= read -r domain; do
        [ -z "$domain" ] && continue
        run_gau_domain "$domain" "$idx"

        # Also run direct Wayback CDX if Tor is available (catches more than GAU)
        if [ "${USE_TOR:-}" = "1" ]; then
            run_wayback_domain "$domain"
        fi

        idx=$((idx + 1))
    done <<< "$domains"

    echo "  GAU discovery complete."
}

# ─── Stats ──────────────────────────────────────────────────────────────────────

show_stats() {
    echo "=== URL Inventory Stats ==="
    echo ""

    if [ ! -f "$DB_FILE" ]; then
        echo "  No database found at ${DB_FILE}"
        return
    fi

    echo "--- Per Domain ---"
    sqlite3 -header -column "$DB_FILE" "
        SELECT domain,
               COUNT(*) as total,
               SUM(CASE WHEN scrape_status = 'pending' THEN 1 ELSE 0 END) as pending,
               SUM(CASE WHEN scrape_status = 'scraped' THEN 1 ELSE 0 END) as scraped,
               SUM(CASE WHEN scrape_status = 'failed' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN scrape_status = 'skipped' THEN 1 ELSE 0 END) as skipped
        FROM urls
        GROUP BY domain
        ORDER BY total DESC;
    "
    echo ""

    echo "--- Per Category ---"
    sqlite3 -header -column "$DB_FILE" "
        SELECT category, COUNT(*) as total
        FROM urls
        GROUP BY category
        ORDER BY total DESC
        LIMIT 25;
    "
    echo ""

    echo "--- Per Content Type ---"
    sqlite3 -header -column "$DB_FILE" "
        SELECT content_type, COUNT(*) as total
        FROM urls
        GROUP BY content_type
        ORDER BY total DESC;
    "
    echo ""

    echo "--- Per Discovery Method ---"
    sqlite3 -header -column "$DB_FILE" "
        SELECT discovered_via, COUNT(*) as total
        FROM urls
        GROUP BY discovered_via
        ORDER BY total DESC;
    "
    echo ""

    local total
    total=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls;")
    local pending
    pending=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls WHERE scrape_status = 'pending';")
    echo "Total: ${total} URLs (${pending} pending scrape)"
}

# ─── Summary ────────────────────────────────────────────────────────────────────

finalize() {
    echo ""
    echo "=== Summary ==="
    local db_total
    db_total=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls;" 2>/dev/null || echo "0")
    local new_this_run=$((db_total - SESSION_START))
    echo "  SQLite DB: ${db_total} total URLs in ${DB_FILE}"
    echo "  This run:  +${new_this_run} new URLs discovered"
    local pending
    pending=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM urls WHERE scrape_status = 'pending';" 2>/dev/null || echo "0")
    echo "  Pending:   ${pending} URLs ready to scrape"
}

# ─── CLI ────────────────────────────────────────────────────────────────────────

MODE=""
FILTER_DOMAIN=""
USE_TOR=""
GAU_WORKERS=""
WAYBACK_WORKERS=""

while [ $# -gt 0 ]; do
    case "$1" in
        --sitemap|--gau|--all|--stats)
            MODE="$1"
            shift
            ;;
        --domain)
            FILTER_DOMAIN="$2"
            shift 2
            ;;
        --use-tor)
            USE_TOR="1"
            shift
            ;;
        --workers)
            WAYBACK_WORKERS="$2"
            GAU_WORKERS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--sitemap|--gau|--all|--stats] [--domain DOMAIN] [--use-tor] [--workers N]"
            echo ""
            echo "Discovers construction article URLs from sitemaps and web archives."
            echo ""
            echo "Methods:"
            echo "  --sitemap    Fetch URLs from XML sitemaps (configured domains)"
            echo "  --gau        Fetch URLs via GAU (Wayback + Common Crawl + OTX + URLScan)"
            echo "  --all        Run both sitemap + GAU (default)"
            echo "  --stats      Show database statistics"
            echo ""
            echo "Options:"
            echo "  --domain D   Only process domain D (e.g. fixr.com)"
            echo "  --use-tor    Route GAU + Wayback CDX through Tor SOCKS proxies (100 instances)"
            echo "  --workers N  Parallel Wayback CDX workers (default: 10, or 50 with --use-tor)"
            echo ""
            echo "Output:"
            echo "  ${DB_FILE}"
            exit 0
            ;;
        *)
            echo "Unknown option: $1. Use --help for usage."
            exit 1
            ;;
    esac
done

export USE_TOR GAU_WORKERS WAYBACK_WORKERS

MODE="${MODE:---all}"

if [ "$MODE" = "--stats" ]; then
    show_stats
    exit 0
fi

# Initialize DB
ensure_db
echo "SQLite DB: ${SESSION_TOTAL} existing URLs"
echo ""

case "$MODE" in
    --sitemap)
        run_sitemap
        ;;
    --gau)
        run_gau
        ;;
    --all)
        run_sitemap
        echo ""
        run_gau
        ;;
esac

finalize
echo ""
echo "Next: python3 scripts/scraping/scrape-construction-content.py --status"
