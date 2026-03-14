#!/usr/bin/env python3
"""
Ingest New Mexico CID contractor data into PostgreSQL.

Source: CSV from scrape_nm_psi.py (PSI Exams portal scrape)
Target: master.contractors, master.licenses, master.tradespersons, master.categories

NM Construction Industries Division (CID) licenses contractors through
the PSI Exams portal. Each license has a business entity and one or more
Qualifying Party (QP) individuals.

Data fields from scrape:
  - Business: company_name, phone, street, city, state, zip_code
  - License: license_number, license_status, issue_date, expiry_date, volume
  - QP: qp_name, qp_certificate_no, qp_classification, qp_attach_date, qp_status
  - Meta: license_id, license_application_id, company_id

Usage:
  python3 ingest_nm.py                  # full ingest
  python3 ingest_nm.py --sample 500     # limit rows for testing
  python3 ingest_nm.py --status         # show row counts
  python3 ingest_nm.py --purge          # delete all NM CID PSI data
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
from psycopg2.extras import execute_values, Json

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "raw"
INPUT_CSV = RAW_DIR / "nm_psi_all.csv"

STATE = "NM"
SOURCE = "NM_CID_PSI"
SOURCE_URL = "https://public.psiexams.com/search.jsp?cid=445"
PG_DSN = "host=localhost port=5433 dbname=us_contractors user=app password=phevasTAz7d2"

FLUSH_EVERY = 500

# ----- QP Classification -> trade category mapping -----

CLASSIFICATION_TRADE_MAP = {
    # Electrical
    "EE": "Electrical",
    "EL": "Electrical",

    # Mechanical / HVAC
    "MM": "HVAC/Mechanical",
    "MH": "HVAC/Mechanical",
    "MC": "HVAC/Mechanical",

    # General Building
    "GB": "General Contracting",
    "GS": "General Contracting",
    "GA": "General Contracting",

    # Plumbing
    "PB": "Plumbing",

    # Roofing
    "RG": "Roofing",

    # Landscaping / Earthwork
    "LN": "Landscaping",
    "EW": "Earthwork",
    "ER": "Earthwork",

    # Specialty
    "FS": "Fire Protection",
    "FL": "Fire Protection",
    "WW": "Water Well Drilling",
    "LP": "LP Gas",
    "BL": "Blasting",
    "PI": "Pipeline",
    "SE": "Solar/Energy",
}

# ----- Status mapping -----

STATUS_MAP = {
    "Active": ("ACTIVE", "Active"),
    "Cancelled": ("CANCELED", "Cancelled"),
    "Inactive": ("INACTIVE", "Inactive"),
    "Expired": ("EXPIRED", "Expired"),
    "Suspended": ("SUSPENDED", "Suspended"),
    "Revoked": ("REVOKED", "Revoked"),
    "Pending": ("PENDING", "Pending"),
}

# Business name suffixes for entity type detection
_BIZ_SUFFIXES = re.compile(
    r'\b(LLC|L\.L\.C\.?|INC\.?|INCORPORATED|CORP\.?|CORPORATION|LTD\.?|'
    r'CO\.?|COMPANY|ENTERPRISES?|SERVICES?|SOLUTIONS?|GROUP|ASSOCIATES?|'
    r'PARTNERS?|PARTNERSHIP|LLP|LP)\b',
    re.IGNORECASE,
)


# ----- Utility functions -----

def get_pg():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = False
    return conn


def parse_date(s):
    """Parse date strings like '11/06/2006' or '2026-09-04'."""
    if not s or not s.strip():
        return None
    s = s.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def normalize_name(name):
    """Normalize business name for dedup matching."""
    if not name:
        return None
    n = name.upper().strip()
    n = re.sub(r'\b(LLC|L\.L\.C\.|INC|INC\.|INCORPORATED|CORP|CORP\.|CORPORATION|LTD|LTD\.|CO\.|DBA|D/B/A)\b', '', n)
    n = re.sub(r'[,.]', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n or None


def determine_entity_type(name):
    """Determine entity type from business name patterns."""
    if not name:
        return "Business", "Business Entity"
    upper = name.upper()

    # Check for common individual name patterns (no comma in PSI data, but check anyway)
    # PSI data is always company names, so default to business
    if "LLC" in upper or "L.L.C" in upper:
        return "LLC", "Limited Liability Company"
    if "INC" in upper or "INCORPORATED" in upper:
        return "Corporation", "Corporation"
    if "CORP" in upper:
        return "Corporation", "Corporation"
    if "LTD" in upper:
        return "Corporation", "Corporation"
    if "LLP" in upper:
        return "LLP", "Limited Liability Partnership"
    if re.search(r'\bLP\b', upper):
        return "LP", "Limited Partnership"
    if "PARTNERSHIP" in upper or "PARTNERS" in upper:
        return "Partnership", "Partnership"
    if "JOINT VENTURE" in upper:
        return "JointVenture", "Joint Venture"

    # Check if it looks like a person's name (sole proprietor)
    # Pattern: "First Last" or "First M. Last" without business suffixes
    if not _BIZ_SUFFIXES.search(name):
        words = name.strip().split()
        if len(words) == 2 and all(w[0].isupper() for w in words if w):
            return "SoleProprietor", "Sole Proprietor"
        if len(words) == 3 and all(w[0].isupper() for w in words if w):
            return "SoleProprietor", "Sole Proprietor"

    return "Business", "Business Entity"


def classify_trade(qp_classification):
    """Map QP classification code to trade category.

    Classification codes are like 'EE-98', 'GB98', 'MM04', etc.
    The first 2 letters indicate the trade.
    """
    if not qp_classification:
        return "General Contracting"

    code = qp_classification.strip().upper()
    # Extract the 2-letter prefix
    prefix = re.match(r'^([A-Z]{2})', code)
    if prefix:
        return CLASSIFICATION_TRADE_MAP.get(prefix.group(1), "General Contracting")

    return "General Contracting"


def clean_phone(phone):
    """Clean phone number to digits only."""
    if not phone:
        return None
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return digits
    if len(digits) == 11 and digits.startswith('1'):
        return digits[1:]
    return digits if digits else None


def clean_volume(volume_str):
    """Clean volume/revenue tier string."""
    if not volume_str or not volume_str.strip():
        return None
    return volume_str.strip()


# ----- Meta tracking -----

def register_source(cur, records_available):
    cur.execute("""
        INSERT INTO meta.sources (state_code, source_name, source_type, source_url,
                                  format, agency, category, records_available, status)
        VALUES (%s, %s, %s, %s, 'csv', %s, %s, %s, 'ingesting')
        ON CONFLICT (state_code, source_name) DO UPDATE SET
            records_available = EXCLUDED.records_available,
            status = 'ingesting'
        RETURNING id
    """, (STATE, SOURCE, "scrape", SOURCE_URL,
          "Construction Industries Division", "licenses",
          records_available))
    return cur.fetchone()[0]


def start_run(cur, source_id):
    cur.execute("""
        INSERT INTO meta.ingestion_runs (source_id, started_at)
        VALUES (%s, NOW())
        RETURNING id
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


# ----- Batch flush helpers -----

def _flush_contractors(cur, batch):
    if not batch:
        return []
    sql = """
        INSERT INTO master.contractors (
            business_name, business_name_normalized, dba_name,
            phone, email, street, city, state, zip, county,
            entity_type, entity_type_desc,
            owner_name, source
        ) VALUES %s
        RETURNING id
    """
    template = "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    result = execute_values(cur, sql, batch, template=template, fetch=True)
    return [r[0] for r in result]


def _flush_licenses(cur, batch):
    if not batch:
        return
    execute_values(cur, """
        INSERT INTO master.licenses (
            contractor_id, state, license_number,
            license_type, license_type_desc,
            classification, classification_desc,
            status, status_desc,
            issue_date, expiration_date,
            source, source_url, raw_data
        ) VALUES %s
    """, batch, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")


def _flush_tradespersons(cur, batch):
    if not batch:
        return
    execute_values(cur, """
        INSERT INTO master.tradespersons (
            name, trade, classification,
            certification_number, state,
            employer_contractor_id,
            source, raw_data
        ) VALUES %s
    """, batch, template="(%s, %s, %s, %s, %s, %s, %s, %s)")


def _flush_categories(cur, batch):
    if not batch:
        return
    execute_values(cur, """
        INSERT INTO master.categories (contractor_id, trade, raw_classification, source)
        VALUES %s
    """, batch, template="(%s, %s, %s, %s)")


# ----- Contractor cache -----

def build_contractor_cache(cur):
    """Load existing NM contractors into dedup cache.

    Dedup key: (UPPER(business_name), city) for NM data since we have addresses.
    """
    cur.execute("""
        SELECT id, UPPER(COALESCE(business_name, '')), UPPER(COALESCE(city, ''))
        FROM master.contractors
        WHERE state = 'NM'
    """)
    cache = {}
    for row in cur.fetchall():
        key = (row[1].strip(), row[2].strip())
        cache[key] = row[0]
    return cache


# ----- Main ingestion -----

def ingest(pg, limit=None):
    """Ingest NM CID PSI license CSV."""
    if not INPUT_CSV.exists():
        print(f"  ERROR: {INPUT_CSV} not found. Run scrape_nm_psi.py first.")
        return 0

    cur = pg.cursor()

    # Count rows
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        csv_rows = sum(1 for _ in f) - 1
    print(f"  Source: {INPUT_CSV.name} ({csv_rows:,} rows)")

    source_id = register_source(cur, csv_rows)
    run_id = start_run(cur, source_id)
    pg.commit()

    contractor_cache = build_contractor_cache(cur)
    print(f"  Loaded {len(contractor_cache):,} existing NM contractors")

    # Counters
    total = 0
    errors = 0
    contractors_new = 0
    contractors_reused = 0
    licenses_inserted = 0
    tradespersons_inserted = 0
    categories_inserted = 0
    skipped_no_name = 0

    # Batch buffers
    license_batch = []
    tradesperson_batch = []
    category_batch = []

    # Dedup
    category_seen = set()
    license_seen = set()

    t0 = time.time()

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if limit and total > limit:
                break

            try:
                # Parse CSV fields
                company_name = (row.get("company_name") or "").strip()
                license_number = (row.get("license_number") or "").strip()
                phone_raw = (row.get("phone") or "").strip()
                license_status = (row.get("license_status") or "").strip()
                issue_date_str = (row.get("issue_date") or "").strip()
                expiry_date_str = (row.get("expiry_date") or "").strip()
                volume_raw = (row.get("volume") or "").strip()
                street = (row.get("street") or "").strip()
                city = (row.get("city") or "").strip()
                state = (row.get("state") or "NM").strip()
                zip_code = (row.get("zip_code") or "").strip()
                qp_name = (row.get("qp_name") or "").strip()
                qp_cert_no = (row.get("qp_certificate_no") or "").strip()
                qp_class = (row.get("qp_classification") or "").strip()
                qp_attach_date = (row.get("qp_attach_date") or "").strip()
                qp_status = (row.get("qp_status") or "").strip()
                license_id = (row.get("license_id") or "").strip()
                license_app_id = (row.get("license_application_id") or "").strip()
                company_id = (row.get("company_id") or "").strip()

                if not company_name:
                    skipped_no_name += 1
                    continue

                if not license_number:
                    errors += 1
                    continue

                # Skip exact duplicate licenses
                lic_dedup_key = license_number
                if lic_dedup_key in license_seen:
                    continue
                license_seen.add(lic_dedup_key)

                # Parse dates
                issue_date = parse_date(issue_date_str)
                expiration_date = parse_date(expiry_date_str)

                # Clean phone
                phone = clean_phone(phone_raw)

                # Trade classification
                trade = classify_trade(qp_class)

                # Entity type
                entity_type, entity_type_desc = determine_entity_type(company_name)

                # Status mapping
                status, status_desc = STATUS_MAP.get(
                    license_status, (license_status.upper().replace(" ", "_"), license_status)
                )

                # Build normalized name
                contractor_name = company_name.upper().strip()
                normalized = normalize_name(contractor_name)

                # Dedup: (UPPER(name), UPPER(city))
                dedup_key = (contractor_name, city.upper().strip())

                contractor_id = contractor_cache.get(dedup_key)
                if contractor_id is None:
                    ids = _flush_contractors(cur, [(
                        company_name,          # business_name
                        normalized,            # business_name_normalized
                        None,                  # dba_name
                        phone,                 # phone
                        None,                  # email
                        street or None,        # street
                        city or None,          # city
                        STATE,                 # state
                        zip_code or None,      # zip
                        None,                  # county
                        entity_type,           # entity_type
                        entity_type_desc,      # entity_type_desc
                        None,                  # owner_name
                        SOURCE,                # source
                    )])
                    contractor_id = ids[0]
                    contractor_cache[dedup_key] = contractor_id
                    contractors_new += 1
                else:
                    contractors_reused += 1

                # License classification info
                classification = trade
                classification_desc = qp_class if qp_class else "Contractor"

                # Raw data
                raw_data = {
                    "psi_license_id": license_id,
                    "psi_license_app_id": license_app_id,
                    "psi_company_id": company_id,
                }
                if volume_raw:
                    raw_data["volume"] = volume_raw
                if qp_name:
                    raw_data["qp_name"] = qp_name
                    raw_data["qp_cert_no"] = qp_cert_no
                    raw_data["qp_classification"] = qp_class

                license_batch.append((
                    contractor_id,
                    STATE,
                    license_number,
                    "Contractor",          # license_type
                    "CID Contractor License",  # license_type_desc
                    classification,        # classification
                    classification_desc,   # classification_desc
                    status,                # status
                    status_desc,           # status_desc
                    issue_date,            # issue_date
                    expiration_date,       # expiration_date
                    SOURCE,                # source
                    SOURCE_URL,            # source_url
                    Json(raw_data),        # raw_data
                ))
                licenses_inserted += 1

                # Insert QP as tradesperson if available
                if qp_name:
                    tp_raw = {
                        "license_number": license_number,
                        "qp_cert_no": qp_cert_no,
                        "qp_classification": qp_class,
                        "qp_attach_date": qp_attach_date,
                        "qp_status": qp_status,
                    }

                    tradesperson_batch.append((
                        qp_name,              # name
                        trade,                # trade
                        qp_class,             # classification
                        qp_cert_no,           # certification_number
                        STATE,                # state
                        contractor_id,        # employer_contractor_id
                        SOURCE,               # source
                        Json(tp_raw),         # raw_data
                    ))
                    tradespersons_inserted += 1

                # Insert category
                cat_key = (contractor_id, trade)
                if cat_key not in category_seen:
                    category_seen.add(cat_key)
                    category_batch.append((
                        contractor_id,
                        trade,
                        qp_class or "Contractor",
                        SOURCE,
                    ))
                    categories_inserted += 1

                # Flush batches
                if len(license_batch) >= FLUSH_EVERY:
                    _flush_licenses(cur, license_batch)
                    _flush_tradespersons(cur, tradesperson_batch)
                    _flush_categories(cur, category_batch)
                    license_batch, tradesperson_batch, category_batch = [], [], []
                    pg.commit()

            except Exception as e:
                errors += 1
                if errors <= 10:
                    print(f"    ERROR row {total}: {e}")

            # Progress
            if total % 5000 == 0:
                elapsed = time.time() - t0
                rate = total / elapsed if elapsed > 0 else 0
                print(f"    [{total:,}] new_co={contractors_new:,} reused={contractors_reused:,} "
                      f"lic={licenses_inserted:,} tp={tradespersons_inserted:,} "
                      f"cat={categories_inserted:,} err={errors} {rate:.0f}/s")

    # Final flush
    _flush_licenses(cur, license_batch)
    _flush_tradespersons(cur, tradesperson_batch)
    _flush_categories(cur, category_batch)

    finish_run(cur, run_id, total, contractors_new, errors)
    finish_source(cur, source_id, licenses_inserted)
    pg.commit()

    elapsed = time.time() - t0
    print(f"\n  Ingestion complete ({elapsed:.0f}s):")
    print(f"    Rows processed:     {total:,}")
    print(f"    Skipped (no name):  {skipped_no_name:,}")
    print(f"    Contractors new:    {contractors_new:,}")
    print(f"    Contractors reused: {contractors_reused:,}")
    print(f"    Licenses:           {licenses_inserted:,}")
    print(f"    Tradespersons (QP): {tradespersons_inserted:,}")
    print(f"    Categories:         {categories_inserted:,}")
    print(f"    Errors:             {errors}")
    return contractors_new


# ----- Status display -----

def show_status():
    """Show current NM data counts."""
    pg = get_pg()
    cur = pg.cursor()

    print("=" * 60)
    print("  New Mexico (NM) CID PSI Data Status")
    print("=" * 60)

    cur.execute("SELECT COUNT(*) FROM master.contractors WHERE state='NM'")
    print(f"  Contractors:   {cur.fetchone()[0]:>10,}")

    cur.execute("SELECT COUNT(*) FROM master.licenses WHERE state='NM'")
    print(f"  Licenses:      {cur.fetchone()[0]:>10,}")

    cur.execute("SELECT COUNT(*) FROM master.tradespersons WHERE state='NM'")
    print(f"  Tradespersons: {cur.fetchone()[0]:>10,}")

    cur.execute("""
        SELECT COUNT(*) FROM master.categories c
        JOIN master.contractors co ON c.contractor_id = co.id
        WHERE co.state='NM'
    """)
    print(f"  Categories:    {cur.fetchone()[0]:>10,}")

    # By source
    cur.execute("""
        SELECT source, COUNT(*) FROM master.contractors
        WHERE state='NM' GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10
    """)
    rows = cur.fetchall()
    if rows:
        print(f"\n  By source:")
        for row in rows:
            print(f"    {(row[0] or 'unknown'):<40} {row[1]:>8,}")

    # By entity type
    cur.execute("""
        SELECT entity_type, COUNT(*) FROM master.contractors
        WHERE state='NM' AND source=%s
        GROUP BY entity_type ORDER BY COUNT(*) DESC
    """, (SOURCE,))
    rows = cur.fetchall()
    if rows:
        print(f"\n  Entity types:")
        for row in rows:
            print(f"    {(row[0] or 'unknown'):<20} {row[1]:>8,}")

    # By license status
    cur.execute("""
        SELECT status, COUNT(*) FROM master.licenses
        WHERE state='NM' AND source=%s
        GROUP BY status ORDER BY COUNT(*) DESC
    """, (SOURCE,))
    rows = cur.fetchall()
    if rows:
        print(f"\n  License status:")
        for row in rows:
            print(f"    {(row[0] or 'unknown'):<20} {row[1]:>8,}")

    # By trade category
    cur.execute("""
        SELECT c.trade, COUNT(*) FROM master.categories c
        JOIN master.contractors co ON c.contractor_id = co.id
        WHERE co.state='NM' AND c.source=%s
        GROUP BY c.trade ORDER BY COUNT(*) DESC
    """, (SOURCE,))
    rows = cur.fetchall()
    if rows:
        print(f"\n  Trade categories:")
        for row in rows:
            print(f"    {(row[0] or 'unknown'):<30} {row[1]:>8,}")

    # Volume distribution
    cur.execute("""
        SELECT raw_data->>'volume', COUNT(*) FROM master.licenses
        WHERE state='NM' AND source=%s AND raw_data->>'volume' IS NOT NULL
        GROUP BY raw_data->>'volume' ORDER BY COUNT(*) DESC LIMIT 10
    """, (SOURCE,))
    rows = cur.fetchall()
    if rows:
        print(f"\n  Revenue tiers:")
        for row in rows:
            print(f"    {(row[0] or 'unknown'):<30} {row[1]:>8,}")

    pg.close()


# ----- Purge -----

def purge():
    """Delete all NM CID PSI data."""
    pg = get_pg()
    cur = pg.cursor()

    print("  Purging New Mexico CID PSI data...")

    cur.execute("SELECT id FROM master.contractors WHERE state='NM' AND source=%s", (SOURCE,))
    contractor_ids = [r[0] for r in cur.fetchall()]
    print(f"  Found {len(contractor_ids):,} contractors from {SOURCE}")

    if contractor_ids:
        for table in ['licenses', 'categories', 'officers', 'insurance_records',
                       'bond_records', 'certifications', 'violations']:
            cur.execute(f"""
                DELETE FROM master.{table}
                WHERE contractor_id = ANY(%s)
            """, (contractor_ids,))
            if cur.rowcount > 0:
                print(f"    Deleted {cur.rowcount:,} from {table}")

        cur.execute("DELETE FROM master.tradespersons WHERE employer_contractor_id = ANY(%s)",
                    (contractor_ids,))
        if cur.rowcount > 0:
            print(f"    Deleted {cur.rowcount:,} from tradespersons (by employer)")

        cur.execute("DELETE FROM master.contractors WHERE id = ANY(%s)", (contractor_ids,))
        print(f"    Deleted {cur.rowcount:,} contractors")

    # Also delete by source
    cur.execute("DELETE FROM master.licenses WHERE source=%s", (SOURCE,))
    print(f"    Deleted {cur.rowcount:,} additional licenses by source")

    cur.execute("DELETE FROM master.tradespersons WHERE source=%s", (SOURCE,))
    print(f"    Deleted {cur.rowcount:,} additional tradespersons by source")

    # Delete meta records
    cur.execute("""
        DELETE FROM meta.ingestion_runs WHERE source_id IN (
            SELECT id FROM meta.sources WHERE state_code='NM' AND source_name=%s
        )
    """, (SOURCE,))
    cur.execute("DELETE FROM meta.sources WHERE state_code='NM' AND source_name=%s", (SOURCE,))

    pg.commit()
    pg.close()
    print("  Purge complete.")


# ----- Main -----

def main():
    parser = argparse.ArgumentParser(description="Ingest NM CID PSI data into PostgreSQL")
    parser.add_argument("--sample", type=int, help="Limit rows for testing")
    parser.add_argument("--status", action="store_true", help="Show row counts")
    parser.add_argument("--purge", action="store_true", help="Delete all NM CID PSI data")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.purge:
        purge()
        return

    print("=" * 60)
    print("  New Mexico (NM) CID PSI Ingestion")
    print("=" * 60)

    pg = get_pg()
    try:
        new_count = ingest(pg, limit=args.sample)
    except Exception as e:
        print(f"\n  FATAL ERROR: {e}")
        pg.rollback()
        raise
    finally:
        pg.close()

    # Show final status
    show_status()


if __name__ == "__main__":
    main()
