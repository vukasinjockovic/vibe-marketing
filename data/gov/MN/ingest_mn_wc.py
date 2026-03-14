#!/usr/bin/env python3
"""
Ingest MN Workers' Compensation insurance records into master.insurance_records.

Source: MN DLI WC Insurance Verification portal
CSV:    raw/mn_wc_insurance.csv

Matching: match employer_name to master.contractors.business_name WHERE state='MN'
  - Primary: UPPER(employer_name) == UPPER(business_name) AND state='MN'
  - Secondary: normalized name match (strip LLC/INC/etc., collapse whitespace)
  - Unmatched records inserted with contractor_id=NULL

Dedup: (policy_number, effective_date, UPPER(employer_name)) -- same policy not inserted twice

Usage:
  python3 ingest_mn_wc.py                  # full ingest
  python3 ingest_mn_wc.py --sample 100     # test with N rows
  python3 ingest_mn_wc.py --status         # show MN insurance counts
  python3 ingest_mn_wc.py --purge          # delete all MN WC insurance data
"""

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = Path(__file__).parent
CSV_DIR = SCRIPT_DIR / "raw"
WC_CSV = CSV_DIR / "mn_wc_insurance.csv"

PG_DSN = "host=localhost port=5433 dbname=us_contractors user=app password=phevasTAz7d2"
STATE = "MN"
SOURCE = "MN_DLI_WC"
AGENCY = "MN Department of Labor and Industry / MWCIA"
INSURANCE_TYPE = "workers_compensation"

BATCH_SIZE = 1000


# -- Utilities ----------------------------------------------------------------

def get_pg():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = False
    return conn


def parse_date(s):
    """Parse date from MN WC CSV (MM/DD/YYYY format, may have extra text)."""
    if not s or not s.strip():
        return None
    # Clean: may have "06/01/2024 MN Added: 07/09/2024"
    s = s.strip().split()[0]  # Take first token (the date)
    if '/' not in s and '-' not in s:
        return None
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def normalize_name(name):
    """Normalize a business name for matching."""
    if not name:
        return None
    n = name.upper().strip()
    n = re.sub(
        r'\b(LLC|L\.L\.C\.|INC|INC\.|INCORPORATED|CORP|CORP\.|CORPORATION|'
        r'LTD|LTD\.|CO\.|DBA|D/B/A|THE|OF|AND|&)\b',
        '', n,
    )
    n = re.sub(r'[,.]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n or None


# -- Meta tracking ------------------------------------------------------------

def register_source(cur, records_available):
    cur.execute("""
        INSERT INTO meta.sources (source_name, state_code, source_type, category, records_available, agency, status)
        VALUES (%s, %s, 'scraped', 'insurance', %s, %s, 'ingesting')
        ON CONFLICT (state_code, source_name) DO UPDATE SET
            records_available = EXCLUDED.records_available,
            status = 'ingesting'
        RETURNING id
    """, (SOURCE, STATE, records_available, AGENCY))
    return cur.fetchone()[0]


def start_run(cur, source_id):
    cur.execute("""
        INSERT INTO meta.ingestion_runs (source_id, started_at)
        VALUES (%s, NOW()) RETURNING id
    """, (source_id,))
    return cur.fetchone()[0]


def finish_run(cur, run_id, total, new, errors):
    cur.execute("""
        UPDATE meta.ingestion_runs
        SET completed_at = NOW(), records_total = %s, records_new = %s, records_errors = %s
        WHERE id = %s
    """, (total, new, errors, run_id))


def finish_source(cur, source_id, records_ingested):
    cur.execute("""
        UPDATE meta.sources
        SET records_ingested = %s, status = 'ingested', ingested_at = NOW()
        WHERE id = %s
    """, (records_ingested, source_id))


# -- Contractor cache ---------------------------------------------------------

def build_contractor_cache(cur):
    """Build lookup caches for MN contractors.

    Returns:
      name_only_cache:   {UPPER(name): [contractor_id, ...]}
      norm_only_cache:   {normalized_name: set(contractor_id, ...)}
    """
    cur.execute("""
        SELECT id, UPPER(COALESCE(business_name, ''))
        FROM master.contractors WHERE state = %s
    """, (STATE,))

    name_only_cache = {}
    norm_only_cache = {}

    for row in cur:
        cid, bname = row[0], row[1]
        if bname not in name_only_cache:
            name_only_cache[bname] = []
        name_only_cache[bname].append(cid)

        nname = normalize_name(bname)
        if nname:
            if nname not in norm_only_cache:
                norm_only_cache[nname] = set()
            norm_only_cache[nname].add(cid)

    print(f"  Contractor cache: {len(name_only_cache):,} names, "
          f"{len(norm_only_cache):,} normalized names")
    return name_only_cache, norm_only_cache


def match_contractor(employer_name, name_only_cache, norm_only_cache):
    """Try to match an employer to an existing MN contractor.

    Strategy:
      1. Exact match on UPPER(name)
      2. Normalized name match (single result)

    Returns contractor_id or None.
    """
    uname = (employer_name or "").upper().strip()
    if not uname:
        return None

    # 1. Exact name match (single match)
    candidates = name_only_cache.get(uname, [])
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        return candidates[0]  # Take first if multiple

    # 2. Normalized name match
    nname = normalize_name(employer_name)
    if nname:
        norm_candidates = norm_only_cache.get(nname, set())
        if len(norm_candidates) == 1:
            return next(iter(norm_candidates))

    return None


# -- Dedup check --------------------------------------------------------------

def build_existing_dedup_set(cur):
    """Load existing MN WC insurance records for dedup."""
    cur.execute("""
        SELECT policy_number, effective_date, raw_data->>'employer_name'
        FROM master.insurance_records
        WHERE state = %s AND source = %s
    """, (STATE, SOURCE))
    dedup = set()
    for row in cur:
        pn = (row[0] or "").strip()
        ed = row[1]
        en = (row[2] or "").upper().strip()
        dedup.add((pn, ed, en))
    print(f"  Existing dedup set: {len(dedup):,} records")
    return dedup


# -- Batch flush --------------------------------------------------------------

def _flush_insurance(cur, batch):
    """Batch insert insurance records using execute_values."""
    if not batch:
        return
    execute_values(cur, """
        INSERT INTO master.insurance_records (
            contractor_id, state, insurance_company, policy_number,
            effective_date, expiration_date,
            insurance_type, source, raw_data
        ) VALUES %s
    """, batch, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s)")


# -- Main ingestion -----------------------------------------------------------

def ingest_wc(pg, limit=None):
    """Ingest MN WC insurance records."""
    if not WC_CSV.exists():
        print(f"  ERROR: CSV not found: {WC_CSV}")
        return {}

    cur = pg.cursor()

    # Load CSV
    with open(WC_CSV, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if limit:
        rows = rows[:limit]
    total_rows = len(rows)
    print(f"  Loaded {total_rows:,} WC insurance records from CSV")

    # Register source and start run
    source_id = register_source(cur, total_rows)
    run_id = start_run(cur, source_id)
    pg.commit()

    # Build caches
    name_only_cache, norm_only_cache = build_contractor_cache(cur)
    existing_dedup = build_existing_dedup_set(cur)

    # Counters
    inserted = 0
    matched = 0
    unmatched = 0
    skipped_dedup = 0
    errors = 0

    batch = []
    t0 = time.time()

    for i, row in enumerate(rows):
        try:
            employer_name = (row.get("employer_name") or "").strip()
            carrier_name = (row.get("carrier_name") or "").strip()
            policy_number = (row.get("policy_number") or "").strip()
            effective_date = parse_date(row.get("effective_date"))
            expiry_date = parse_date(row.get("expiry_date"))

            if not employer_name:
                errors += 1
                continue

            # Dedup check
            dedup_key = (policy_number, effective_date, employer_name.upper())
            if dedup_key in existing_dedup:
                skipped_dedup += 1
                continue
            existing_dedup.add(dedup_key)

            # Match to contractor
            cid = match_contractor(employer_name, name_only_cache, norm_only_cache)
            if cid:
                matched += 1
            else:
                unmatched += 1

            # Build raw_data JSONB
            raw = {k: v for k, v in row.items() if v}

            batch.append((
                cid,              # contractor_id (may be NULL)
                STATE,            # state
                carrier_name or None,  # insurance_company
                policy_number or None, # policy_number
                effective_date,   # effective_date
                expiry_date,      # expiration_date
                INSURANCE_TYPE,   # insurance_type
                SOURCE,           # source
                json.dumps(raw),  # raw_data
            ))
            inserted += 1

            if len(batch) >= BATCH_SIZE:
                _flush_insurance(cur, batch)
                batch = []
                pg.commit()
                if (i + 1) % 10000 == 0:
                    elapsed = time.time() - t0
                    rate = (i + 1) / elapsed
                    print(f"    ... {i + 1:,}/{total_rows:,} rows ({rate:.0f}/s) "
                          f"matched={matched:,} unmatched={unmatched:,}")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error row {i}: {e}")

    # Flush remaining
    if batch:
        _flush_insurance(cur, batch)
        pg.commit()

    elapsed = time.time() - t0

    # Finalize meta
    finish_run(cur, run_id, total_rows, inserted, errors)
    finish_source(cur, source_id, inserted)
    pg.commit()

    print(f"\n  MN WC Insurance Ingestion Complete ({elapsed:.1f}s)")
    print(f"    Total CSV rows:    {total_rows:,}")
    print(f"    Inserted:          {inserted:,}")
    print(f"    Matched contractor:{matched:,}")
    print(f"    Unmatched:         {unmatched:,}")
    print(f"    Skipped (dedup):   {skipped_dedup:,}")
    print(f"    Errors:            {errors:,}")

    return {
        "total": total_rows,
        "inserted": inserted,
        "matched": matched,
        "unmatched": unmatched,
        "skipped_dedup": skipped_dedup,
        "errors": errors,
    }


# -- Status -------------------------------------------------------------------

def show_status(pg):
    cur = pg.cursor()
    print(f"\n{'=' * 60}")
    print(f"  MN Workers' Compensation Insurance -- Status")
    print(f"{'=' * 60}")

    # Total MN insurance records
    cur.execute("SELECT COUNT(*) FROM master.insurance_records WHERE state = 'MN'")
    total = cur.fetchone()[0]
    print(f"  Total MN insurance records:       {total:>10,}")

    # By source
    cur.execute("""
        SELECT source, COUNT(*) FROM master.insurance_records
        WHERE state = 'MN' GROUP BY source ORDER BY source
    """)
    for r in cur.fetchall():
        print(f"    source={r[0]:40s} {r[1]:>10,}")

    # Matched vs unmatched
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE contractor_id IS NOT NULL) AS matched,
            COUNT(*) FILTER (WHERE contractor_id IS NULL) AS unmatched
        FROM master.insurance_records WHERE state = 'MN' AND source = %s
    """, (SOURCE,))
    r = cur.fetchone()
    if r:
        print(f"  Matched to contractor:            {r[0]:>10,}")
        print(f"  Unmatched (contractor_id=NULL):    {r[1]:>10,}")

    # Top carriers
    cur.execute("""
        SELECT insurance_company, COUNT(*)
        FROM master.insurance_records
        WHERE state = 'MN' AND source = %s AND insurance_company IS NOT NULL
        GROUP BY insurance_company
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """, (SOURCE,))
    rows = cur.fetchall()
    if rows:
        print(f"\n  Top carriers:")
        for r in rows:
            print(f"    {r[1]:>6,}  {r[0]}")

    # Date range
    cur.execute("""
        SELECT MIN(effective_date), MAX(effective_date),
               MIN(expiration_date), MAX(expiration_date)
        FROM master.insurance_records
        WHERE state = 'MN' AND source = %s
    """, (SOURCE,))
    r = cur.fetchone()
    if r and r[0]:
        print(f"\n  Effective date range:  {r[0]} to {r[1]}")
        print(f"  Expiration date range: {r[2]} to {r[3]}")


# -- Purge --------------------------------------------------------------------

def purge(pg):
    cur = pg.cursor()
    cur.execute(
        "DELETE FROM master.insurance_records WHERE state = %s AND source = %s",
        (STATE, SOURCE),
    )
    deleted = cur.rowcount
    pg.commit()
    print(f"  Deleted {deleted:,} MN WC insurance records")


# -- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ingest MN WC insurance data")
    parser.add_argument("--sample", type=int, help="Ingest only N rows")
    parser.add_argument("--status", action="store_true", help="Show MN insurance counts")
    parser.add_argument("--purge", action="store_true", help="Delete all MN WC data")

    args = parser.parse_args()

    pg = get_pg()

    if args.status:
        show_status(pg)
    elif args.purge:
        purge(pg)
    else:
        ingest_wc(pg, limit=args.sample)

    pg.close()


if __name__ == "__main__":
    main()
