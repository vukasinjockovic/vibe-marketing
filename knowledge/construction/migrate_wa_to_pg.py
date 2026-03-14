#!/usr/bin/env python3
"""
Migrate WA data from SQLite prototype to PostgreSQL us_contractors database.
Also registers all discovered WA sources in meta.sources.
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = Path(__file__).parent
SQLITE_PATH = SCRIPT_DIR / "contractors.sqlite"

PG_DSN = "host=localhost port=5433 dbname=us_contractors user=app password=phevasTAz7d2"

SOURCE = "wa_lni"
STATE = "WA"


def get_pg():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = False
    return conn


def migrate():
    sq = sqlite3.connect(str(SQLITE_PATH))
    sq.row_factory = sqlite3.Row
    pg = get_pg()
    cur = pg.cursor()

    # ── Register WA sources ────────────────────────────────────────
    sources = [
        ("wa_lni_general", "bulk_csv", "https://data.wa.gov/api/views/m8qx-ubtq/rows.csv",
         "csv", "L&I", "licenses", 159680),
        ("wa_lni_insurance", "bulk_csv", "https://data.wa.gov/api/views/ciwg-agsx/rows.csv",
         "csv", "L&I", "insurance", 75454),
        ("wa_lni_bond", "bulk_csv", "https://data.wa.gov/api/views/bzff-4fmt/rows.csv",
         "csv", "L&I", "bonds", 171688),
        ("wa_lni_principal", "bulk_csv", "https://data.wa.gov/api/views/4xk5-x9j6/rows.csv",
         "csv", "L&I", "officers", 248420),
    ]

    for name, stype, url, fmt, agency, cat, recs in sources:
        cur.execute("""
            INSERT INTO meta.sources (state_code, source_name, source_type, source_url, format, agency, category, records_available, records_ingested, status, ingested_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ingested', NOW())
            ON CONFLICT (state_code, source_name) DO UPDATE SET records_ingested = EXCLUDED.records_ingested, status = 'ingested'
        """, (STATE, name, stype, url, fmt, agency, cat, recs, recs))

    cur.execute("UPDATE meta.states SET status='complete', sources_discovered=4, sources_ingested=4, last_updated=NOW() WHERE code='WA'")
    pg.commit()
    print("Registered WA sources in meta.sources")

    # ── Migrate contractors ────────────────────────────────────────
    print("Migrating contractors...")
    rows = sq.execute("SELECT * FROM contractors").fetchall()
    total = len(rows)

    # Build sqlite_id -> pg_id mapping
    id_map = {}
    batch = []
    for i, row in enumerate(rows):
        batch.append((
            row["business_name"], row["business_name_normalized"],
            row["phone"], row["phone_alt"], row["email"], row["website"],
            row["street"], row["street2"], row["city"], row["state"], row["zip"],
            row["county"], row["entity_type"], row["entity_type_desc"],
            row["year_established"], row["owner_name"],
        ))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.contractors (
                    business_name, business_name_normalized,
                    phone, phone_alt, email, website,
                    street, street2, city, state, zip,
                    county, entity_type, entity_type_desc,
                    year_established, owner_name
                ) VALUES %s RETURNING id
            """, batch)
            new_ids = [r[0] for r in cur.fetchall()]

            start_idx = i - len(batch) + 1
            for j, new_id in enumerate(new_ids):
                old_id = rows[start_idx + j]["id"]
                id_map[old_id] = new_id

            batch = []
            pg.commit()
            print(f"  Contractors: {i+1:,}/{total:,}")

    print(f"  Done: {len(id_map):,} contractors migrated")

    # ── Migrate licenses ───────────────────────────────────────────
    print("Migrating licenses...")
    rows = sq.execute("SELECT * FROM licenses").fetchall()
    total = len(rows)
    batch = []

    for i, row in enumerate(rows):
        cid = id_map.get(row["contractor_id"])
        if not cid:
            continue

        raw = row["raw_data"]
        if raw and isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        batch.append((
            cid, row["state"], row["license_number"],
            row["license_type"], row["license_type_desc"],
            row["classification"], row["classification_desc"],
            row["classification2"], row["classification2_desc"],
            row["status"], row["status_desc"],
            row["issue_date"], row["expiration_date"], row["suspend_date"],
            row["ubi"], row["source"], row["source_url"],
            json.dumps(raw) if raw else None,
        ))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.licenses (
                    contractor_id, state, license_number,
                    license_type, license_type_desc,
                    classification, classification_desc,
                    classification2, classification2_desc,
                    status, status_desc,
                    issue_date, expiration_date, suspend_date,
                    ubi, source, source_url, raw_data
                ) VALUES %s
            """, batch)
            batch = []
            pg.commit()
            if (i + 1) % 50000 == 0 or i == total - 1:
                print(f"  Licenses: {i+1:,}/{total:,}")

    # ── Migrate insurance ──────────────────────────────────────────
    print("Migrating insurance records...")
    rows = sq.execute("SELECT * FROM insurance_records").fetchall()
    total = len(rows)
    batch = []

    for i, row in enumerate(rows):
        cid = id_map.get(row["contractor_id"])
        if not cid:
            continue

        raw = row["raw_data"]
        if raw and isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        batch.append((
            cid, row["license_number"], row["state"],
            row["insurance_company"], row["insurance_agency"],
            row["policy_number"], row["coverage_amount"],
            row["effective_date"], row["expiration_date"], row["cancel_date"],
            row["source"],
            json.dumps(raw) if raw else None,
        ))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.insurance_records (
                    contractor_id, license_number, state,
                    insurance_company, insurance_agency,
                    policy_number, coverage_amount,
                    effective_date, expiration_date, cancel_date,
                    source, raw_data
                ) VALUES %s
            """, batch)
            batch = []
            pg.commit()
            if (i + 1) % 50000 == 0 or i == total - 1:
                print(f"  Insurance: {i+1:,}/{total:,}")

    # ── Migrate bonds ──────────────────────────────────────────────
    print("Migrating bond records...")
    rows = sq.execute("SELECT * FROM bond_records").fetchall()
    total = len(rows)
    batch = []

    for i, row in enumerate(rows):
        cid = id_map.get(row["contractor_id"])
        if not cid:
            continue

        raw = row["raw_data"]
        if raw and isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        batch.append((
            cid, row["license_number"], row["state"],
            row["bond_company"], row["bond_account_id"], row["bond_amount"],
            row["effective_date"], row["expiration_date"], row["cancel_date"],
            bool(row["is_impaired"]), row["impaired_date"],
            row["source"],
            json.dumps(raw) if raw else None,
        ))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.bond_records (
                    contractor_id, license_number, state,
                    bond_company, bond_account_id, bond_amount,
                    effective_date, expiration_date, cancel_date,
                    is_impaired, impaired_date,
                    source, raw_data
                ) VALUES %s
            """, batch)
            batch = []
            pg.commit()
            if (i + 1) % 50000 == 0 or i == total - 1:
                print(f"  Bonds: {i+1:,}/{total:,}")

    # ── Migrate officers ───────────────────────────────────────────
    print("Migrating officers...")
    rows = sq.execute("SELECT * FROM officers").fetchall()
    total = len(rows)
    batch = []

    for i, row in enumerate(rows):
        cid = id_map.get(row["contractor_id"])
        if not cid:
            continue

        raw = row["raw_data"]
        if raw and isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                pass

        batch.append((
            cid, row["name"], row["title"],
            row["start_date"], row["end_date"],
            row["source"],
            json.dumps(raw) if raw else None,
        ))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.officers (
                    contractor_id, name, title,
                    start_date, end_date,
                    source, raw_data
                ) VALUES %s
            """, batch)
            batch = []
            pg.commit()
            if (i + 1) % 50000 == 0 or i == total - 1:
                print(f"  Officers: {i+1:,}/{total:,}")

    # ── Migrate categories ─────────────────────────────────────────
    print("Migrating categories...")
    rows = sq.execute("SELECT * FROM categories").fetchall()
    total = len(rows)
    batch = []

    for i, row in enumerate(rows):
        cid = id_map.get(row["contractor_id"])
        if not cid:
            continue

        batch.append((cid, row["trade"], row["raw_classification"], row["source"]))

        if len(batch) >= 5000 or i == total - 1:
            execute_values(cur, """
                INSERT INTO master.categories (contractor_id, trade, raw_classification, source)
                VALUES %s
            """, batch)
            batch = []
            pg.commit()
            if (i + 1) % 50000 == 0 or i == total - 1:
                print(f"  Categories: {i+1:,}/{total:,}")

    # ── Update state record counts ─────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM master.contractors WHERE state = 'WA'")
    wa_count = cur.fetchone()[0]
    cur.execute("UPDATE meta.states SET total_records = %s WHERE code = 'WA'", (wa_count,))
    pg.commit()

    # ── Summary ────────────────────────────────────────────────────
    print("\n=== Migration Complete ===")
    for table in ["contractors", "licenses", "insurance_records", "bond_records", "officers", "categories"]:
        cur.execute(f"SELECT COUNT(*) FROM master.{table}")
        count = cur.fetchone()[0]
        print(f"  master.{table:>20}: {count:>10,}")

    pg.close()
    sq.close()


if __name__ == "__main__":
    migrate()
