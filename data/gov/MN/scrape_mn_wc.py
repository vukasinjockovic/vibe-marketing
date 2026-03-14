#!/usr/bin/env python3
"""
Scrape MN DLI Workers' Compensation Insurance Verification portal.

Source: http://www.inslookup.doli.state.mn.us/Search.aspx
Stack:  ASP.NET WebForms (requires Playwright for form submission + navigation)

Flow:
  1. GET Search.aspx  (Playwright browser)
  2. Fill form with employer name prefix + date range -> submit
  3. Parse employer list from Employer.aspx results
  4. For each employer: click link -> navigate to EmployerDetails.aspx
  5. Parse coverage detail: employer name, address, carrier, policy, dates, status
  6. Go back to employer list -> click next employer -> repeat

Strategy:
  - 3-letter prefix enumeration using DB-derived prefixes (only real word starts)
  - "Starts With" search mode with broad date range
  - If "excessive results" error, expand to 4-letter sub-prefixes (then 5, etc.)
  - Single persistent Playwright browser for entire crawl
  - Checkpoint/resume via JSON file

Usage:
  python3 scrape_mn_wc.py                     # full scrape (all DB-derived prefixes)
  python3 scrape_mn_wc.py --prefix ABC        # single prefix test
  python3 scrape_mn_wc.py --resume            # resume from checkpoint
  python3 scrape_mn_wc.py --status            # show scrape status
  python3 scrape_mn_wc.py --sample 20         # test first N prefixes
"""

import argparse
import csv
import json
import re
import string
import sys
import time
import traceback
from collections import deque
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "raw"
CSV_FILE = RAW_DIR / "mn_wc_insurance.csv"
CHECKPOINT_FILE = RAW_DIR / "mn_wc_checkpoint.json"

BASE_URL = "http://www.inslookup.doli.state.mn.us/Search.aspx"
DATE_START = "01/01/2020"
DATE_END = "03/14/2026"
REQUEST_DELAY = 0.3  # seconds between searches

MAX_EXPAND_DEPTH = 6  # max prefix length before giving up on EXCESSIVE
MAX_EMPLOYERS_PER_PREFIX = 200  # cap employer clicks per prefix (safety)

CSV_COLUMNS = [
    "employer_name", "employer_address",
    "carrier_name", "reported_payroll_zero",
    "effective_date", "expiry_date",
    "policy_number", "status", "status_date",
    "search_prefix", "scraped_at",
]

PG_DSN = "host=localhost port=5433 dbname=us_contractors user=app password=phevasTAz7d2"


# ---------------------------------------------------------------------------
# DB-driven prefix generation
# ---------------------------------------------------------------------------

def generate_db_prefixes(length=3):
    """Generate prefixes from actual MN contractor business names in our DB.

    This avoids wasting time on random 3-char combos that match nothing.
    Returns sorted list of unique letter-only prefixes.
    """
    import psycopg2

    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT UPPER(LEFT(business_name, %s)) as pfx
        FROM master.contractors
        WHERE state = 'MN'
          AND business_name IS NOT NULL
          AND LENGTH(business_name) >= %s
        ORDER BY pfx
    """, (length, length))
    prefixes = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()

    # Filter to letter-only prefixes (digits/spaces rarely match WC employers)
    letter_only = sorted(set(p for p in prefixes if p.isalpha()))
    return letter_only


def expand_prefix(prefix):
    """Expand a prefix by adding one more character (A-Z only)."""
    return [prefix + c for c in string.ascii_uppercase]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_detail_html(html, prefix):
    """Parse the EmployerDetails page HTML for coverage records."""
    records = []
    now = datetime.now().isoformat()

    def extract_field(label, text):
        """Extract all values for a given label."""
        values = []
        pattern = re.escape(label) + r':&nbsp;(?:</b>)?\s*</div>\s*<div[^>]*>(.*?)</div>'
        for m in re.finditer(pattern, text, re.DOTALL):
            val = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
            val = re.sub(r'\s+', ' ', val)
            values.append(val)
        return values

    emp_names = extract_field("Employer", html)
    addresses = extract_field("Address", html)
    effectives = extract_field("Effective", html)
    expires_list = extract_field("Expires", html)
    policies = extract_field("Policy#", html)
    carriers = extract_field("Carrier", html)
    payroll_zeros = extract_field("Reported Payroll Of Zero", html)

    # Status needs special handling to avoid matching "Status Date"
    statuses = []
    for m in re.finditer(
        r'(?<![a-zA-Z])Status:&nbsp;(?:</b>)?\s*</div>\s*<div[^>]*>(.*?)</div>',
        html,
        re.DOTALL,
    ):
        val = re.sub(r'<[^>]+>', ' ', m.group(1)).strip()
        statuses.append(val)

    status_dates = extract_field("Status Date", html)

    n = len(emp_names)
    for i in range(n):
        record = {
            "employer_name": emp_names[i] if i < len(emp_names) else "",
            "employer_address": addresses[i] if i < len(addresses) else "",
            "carrier_name": carriers[i] if i < len(carriers) else "",
            "reported_payroll_zero": payroll_zeros[i] if i < len(payroll_zeros) else "",
            "effective_date": effectives[i] if i < len(effectives) else "",
            "expiry_date": expires_list[i] if i < len(expires_list) else "",
            "policy_number": policies[i] if i < len(policies) else "",
            "status": statuses[i] if i < len(statuses) else "",
            "status_date": status_dates[i] if i < len(status_dates) else "",
            "search_prefix": prefix,
            "scraped_at": now,
        }
        if record["employer_name"]:
            records.append(record)

    return records


# ---------------------------------------------------------------------------
# Checkpoint / CSV helpers
# ---------------------------------------------------------------------------

def load_checkpoint():
    """Load checkpoint state."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {
        "prefixes_done": [],
        "prefixes_excessive": [],
        "prefixes_empty": [],
        "total_records": 0,
        "total_employers_clicked": 0,
        "errors": 0,
    }


def save_checkpoint(state):
    """Save checkpoint state."""
    state["timestamp"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_seen_keys():
    """Load existing dedup keys from CSV."""
    seen = set()
    if CSV_FILE.exists():
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (
                    row.get("employer_name", ""),
                    row.get("policy_number", ""),
                    row.get("effective_date", ""),
                )
                seen.add(key)
    return seen


def append_records(records):
    """Append records to CSV."""
    write_header = not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for rec in records:
            writer.writerow(rec)


# ---------------------------------------------------------------------------
# Playwright browser session
# ---------------------------------------------------------------------------

class MNWCBrowser:
    """Persistent Playwright browser session for MN WC portal."""

    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        self.page = self.context.new_page()
        self._search_count = 0

    def close(self):
        try:
            self.browser.close()
            self._pw.stop()
        except Exception:
            pass

    def _submit_search(self, prefix):
        """Navigate to search page, fill form, submit. Returns (html, employer_count, is_excessive)."""
        page = self.page

        # Go to search page
        page.goto(BASE_URL, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(0.3)

        # Fill form
        page.fill("#i_txtSDate", DATE_START)
        page.fill("#i_txtEDate", DATE_END)
        page.select_option("#i_ddlOption", "Starts")
        page.fill("#i_txtEmployer", prefix)

        # Submit via JS: fix the broken onclick handler that does
        # "return ResetError();WebForm_DoPostBackWithOptions(...)"
        # ResetError() returns undefined, so the return short-circuits.
        # Fix: call both functions separately, then click.
        page.evaluate("""() => {
            var btn = document.getElementById('i_btnSubmit');
            btn.onclick = function() {
                ResetError();
                WebForm_DoPostBackWithOptions(
                    new WebForm_PostBackOptions(
                        'ctl00$i$btnSubmit', '', true, '', '', false, false
                    )
                );
                return false;
            };
            btn.click();
        }""")

        page.wait_for_load_state("domcontentloaded")
        time.sleep(1.0)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        html = page.content()
        self._search_count += 1

        # Check for error/status label
        error_el = page.query_selector("#i_lblNoResult")
        if error_el and error_el.is_visible():
            text = error_el.inner_text().strip().lower()
            if "excessive" in text:
                return html, 0, True
            if "no results" in text:
                return html, 0, False

        # Count employers
        links = page.query_selector_all('a[id*="btnEmployerName"]')
        return html, len(links), False

    def _click_employer(self, index):
        """Click employer at given index. Returns detail HTML or None."""
        page = self.page
        links = page.query_selector_all('a[id*="btnEmployerName"]')
        if index >= len(links):
            return None

        links[index].click()
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1.2)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        html = page.content()

        # Handle pagination on detail page
        all_html = html
        page_m = re.search(r"Page\s+\d+\s+of\s+(\d+)", html)
        total_pages = int(page_m.group(1)) if page_m else 1

        if total_pages > 1:
            for pg_num in range(2, total_pages + 1):
                next_btn = page.query_selector(
                    '[id*="EmployerDetailsList_UCPager_btnNext"]'
                )
                if next_btn and next_btn.is_enabled():
                    next_btn.click()
                    time.sleep(1.2)
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except Exception:
                        pass
                    all_html += page.content()

        return all_html

    def _go_back(self):
        """Go back from detail page to employer list."""
        self.page.go_back()
        time.sleep(0.5)
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

    def search_and_scrape(self, prefix):
        """Search a prefix, click through ALL employers, parse all details.

        Returns (records, status) where status is:
        'ok', 'empty', 'excessive', 'error:<msg>'
        """
        try:
            html, emp_count, excessive = self._submit_search(prefix)
        except Exception as e:
            return [], f"error: search failed: {e}"

        if excessive:
            return [], "excessive"
        if emp_count == 0:
            return [], "empty"

        # Click each employer and collect records
        all_records = []
        click_count = min(emp_count, MAX_EMPLOYERS_PER_PREFIX)
        for i in range(click_count):
            try:
                detail_html = self._click_employer(i)
                if detail_html:
                    records = parse_detail_html(detail_html, prefix)
                    all_records.extend(records)

                # Go back to employer list for next click
                if i < click_count - 1:
                    self._go_back()
                    time.sleep(0.3)

            except Exception as e:
                # If employer click fails, try to recover
                try:
                    self._go_back()
                except Exception:
                    pass
                continue

        return all_records, "ok"

    def restart_if_needed(self):
        """Restart browser every N searches to prevent memory leaks."""
        if self._search_count > 0 and self._search_count % 200 == 0:
            print(f"    [browser restart after {self._search_count} searches]")
            try:
                self.page.close()
                self.context.close()
            except Exception:
                pass
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
            )
            self.page = self.context.new_page()


# ---------------------------------------------------------------------------
# Main crawl logic
# ---------------------------------------------------------------------------

def crawl(resume=False, prefix=None, sample=None):
    """Main crawl loop using persistent Playwright browser."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Load state
    state = load_checkpoint() if resume else {
        "prefixes_done": [],
        "prefixes_excessive": [],
        "prefixes_empty": [],
        "total_records": 0,
        "total_employers_clicked": 0,
        "errors": 0,
    }
    seen_keys = load_seen_keys()
    done_set = set(state["prefixes_done"])
    empty_set = set(state.get("prefixes_empty", []))

    # Single prefix test mode
    if prefix:
        print(f"Testing single prefix: '{prefix}'")
        browser = MNWCBrowser()
        try:
            records, status = browser.search_and_scrape(prefix)
            print(f"  Status: {status}")
            print(f"  Records: {len(records)}")

            # Dedup and save
            new_records = []
            for r in records:
                key = (r["employer_name"], r["policy_number"], r["effective_date"])
                if key not in seen_keys:
                    seen_keys.add(key)
                    new_records.append(r)
            if new_records:
                append_records(new_records)
                print(f"  New (after dedup): {len(new_records)}")

            for r in records[:10]:
                print(f"    {r['employer_name'][:40]:<40} | "
                      f"{r['carrier_name'][:30]:<30} | "
                      f"{r['policy_number']}")
            if len(records) > 10:
                print(f"    ... and {len(records) - 10} more")
        finally:
            browser.close()
        return

    # Generate prefixes from DB
    print("Loading prefixes from DB...")
    all_prefixes = generate_db_prefixes(3)

    if sample:
        all_prefixes = all_prefixes[:sample]

    # Build work queue: undone prefixes
    queue = deque(p for p in all_prefixes if p not in done_set and p not in empty_set)

    total_base = len(all_prefixes)
    done_count = len(done_set)

    print("=" * 70)
    print("  MN WC Insurance Scraper (Playwright)")
    print("=" * 70)
    print(f"  URL: {BASE_URL}")
    print(f"  Date range: {DATE_START} to {DATE_END}")
    print(f"  Total DB-derived 3-char prefixes: {total_base:,}")
    print(f"  Already done: {done_count:,}")
    print(f"  Already empty: {len(empty_set):,}")
    print(f"  Excessive (will expand): {len(state.get('prefixes_excessive', []))}")
    print(f"  Queue: {len(queue):,}")
    print(f"  Dedup keys loaded: {len(seen_keys):,}")
    print(f"  Existing records in CSV: {state.get('total_records', 0):,}")
    print()

    if not queue:
        print("  All prefixes done!")
        return

    # Start browser
    browser = MNWCBrowser()
    t0 = time.time()
    completed = 0
    total_new = state.get("total_records", 0)
    total_emp_clicks = state.get("total_employers_clicked", 0)
    errors = state.get("errors", 0)

    try:
        while queue:
            pfx = queue.popleft()

            if pfx in done_set or pfx in empty_set:
                continue

            try:
                browser.restart_if_needed()
                records, status = browser.search_and_scrape(pfx)

                if status == "excessive":
                    # Expand to longer prefixes
                    if len(pfx) < MAX_EXPAND_DEPTH:
                        sub = expand_prefix(pfx)
                        added = 0
                        for sp in sub:
                            if sp not in done_set and sp not in empty_set:
                                queue.append(sp)
                                added += 1
                        state["prefixes_excessive"].append(pfx)
                        print(f"  {pfx}  EXCESSIVE -> +{added} sub-prefixes (queue={len(queue)})")
                    else:
                        print(f"  {pfx}  EXCESSIVE at depth {len(pfx)} -- skipping")

                elif status == "empty":
                    state["prefixes_empty"].append(pfx)
                    empty_set.add(pfx)

                elif status.startswith("error"):
                    errors += 1
                    state["errors"] = errors
                    print(f"  {pfx}  ERROR: {status}")
                    # Retry once
                    time.sleep(3)
                    try:
                        records, status = browser.search_and_scrape(pfx)
                        if status.startswith("error"):
                            print(f"  {pfx}  RETRY FAILED: {status}")
                    except Exception:
                        pass

                else:
                    # Dedup and save
                    new_records = []
                    for r in records:
                        key = (r["employer_name"], r["policy_number"], r["effective_date"])
                        if key not in seen_keys:
                            seen_keys.add(key)
                            new_records.append(r)

                    if new_records:
                        append_records(new_records)
                        total_new += len(new_records)
                        state["total_records"] = total_new

                    n = len(records)
                    n_new = len(new_records)
                    unique_emps = len(set(r["employer_name"] for r in records)) if records else 0
                    total_emp_clicks += unique_emps
                    state["total_employers_clicked"] = total_emp_clicks

                    elapsed = time.time() - t0
                    rate = (completed + 1) / (elapsed / 60)
                    if n > 0:
                        print(
                            f"  {pfx:<6} +{n_new:<4} new ({n} total, {unique_emps} emps)  "
                            f"cumul={total_new:>7,}  unique={len(seen_keys):>7,}  "
                            f"q={len(queue):<5}  {rate:.1f} pfx/min  "
                            f"{elapsed/60:.1f}min"
                        )

                completed += 1
                state["prefixes_done"].append(pfx)
                done_set.add(pfx)

                # Save checkpoint every 25 prefixes
                if completed % 25 == 0:
                    save_checkpoint(state)

                # Rate limit
                time.sleep(REQUEST_DELAY)

            except KeyboardInterrupt:
                raise
            except Exception as e:
                errors += 1
                state["errors"] = errors
                print(f"  {pfx}  EXCEPTION: {e}")
                time.sleep(3)
                # Re-add to queue for retry if first attempt
                if pfx not in done_set:
                    queue.append(pfx)

    except KeyboardInterrupt:
        print(f"\n  Interrupted! Saving checkpoint...")

    finally:
        save_checkpoint(state)
        browser.close()

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  Completed: {completed:,} prefixes")
    print(f"  Total new records: {total_new:,}")
    print(f"  Unique dedup keys: {len(seen_keys):,}")
    print(f"  Employers clicked: {total_emp_clicks:,}")
    print(f"  Errors: {errors:,}")
    print(f"  Time: {elapsed/60:.1f} min ({elapsed/3600:.1f} hr)")
    print(f"  Output: {CSV_FILE}")
    print(f"{'=' * 70}")


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def show_status():
    """Show scrape status."""
    print("=" * 60)
    print("  MN WC Insurance Scraper -- Status")
    print("=" * 60)

    if CHECKPOINT_FILE.exists():
        cp = load_checkpoint()
        done = len(cp.get("prefixes_done", []))
        empty = len(cp.get("prefixes_empty", []))
        excessive = len(cp.get("prefixes_excessive", []))
        print(f"  Prefixes done:     {done:,}")
        print(f"  Prefixes empty:    {empty:,}")
        print(f"  Prefixes excessive:{excessive:,}")
        print(f"  Total records:     {cp.get('total_records', 0):,}")
        print(f"  Employers clicked: {cp.get('total_employers_clicked', 0):,}")
        print(f"  Errors:            {cp.get('errors', 0):,}")
        print(f"  Last save:         {cp.get('timestamp', 'unknown')}")
    else:
        print("  Checkpoint: none")

    if CSV_FILE.exists():
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            count = sum(1 for _ in f) - 1
        size_mb = CSV_FILE.stat().st_size / (1024 * 1024)

        employers = set()
        carriers = {}
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                employers.add(row.get("employer_name", ""))
                c = row.get("carrier_name", "")
                if c:
                    carriers[c] = carriers.get(c, 0) + 1

        print(f"\n  CSV records:       {count:,}")
        print(f"  CSV file size:     {size_mb:.2f} MB")
        print(f"  Unique employers:  {len(employers):,}")
        print(f"  Unique carriers:   {len(carriers):,}")

        if carriers:
            print(f"\n  Top carriers:")
            for c, n in sorted(carriers.items(), key=lambda x: -x[1])[:15]:
                print(f"    {n:>6,}  {c}")
    else:
        print("  CSV: not yet created")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape MN WC insurance data")
    parser.add_argument("--prefix", help="Test a single prefix")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", action="store_true", help="Show scrape status")
    parser.add_argument("--sample", type=int, help="Process first N prefixes only")

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.prefix:
        crawl(prefix=args.prefix)
    else:
        crawl(resume=args.resume, sample=args.sample)


if __name__ == "__main__":
    main()
