#!/usr/bin/env python3
"""
Washington State Contractor License Data Ingestion

Reads 4 WA L&I CSV datasets and loads them into contractors.sqlite
with proper field mapping. Links records via ContractorLicenseNumber + UBI.

Sources:
  - wa_contractors_general.csv   (159K records — core license data)
  - wa_contractors_insurance.csv (75K records — insurance policies)
  - wa_contractors_bond.csv      (171K records — surety bonds)
  - wa_contractors_principal.csv (248K records — owners/officers)

Usage:
  python3 ingest_wa.py                    # full ingest
  python3 ingest_wa.py --status           # show ingestion stats
  python3 ingest_wa.py --sample 10        # ingest 10 records only (test)
"""

import argparse
import csv
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "contractors.sqlite"
RAW_DIR = SCRIPT_DIR / "states" / "WA" / "raw"

SOURCE = "wa_lni"
STATE = "WA"


def parse_date(s):
    """Parse MM/DD/YYYY to YYYY-MM-DD."""
    if not s or s.strip() == "":
        return None
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def normalize_name(name):
    """Normalize business name for matching."""
    if not name:
        return None
    n = name.upper().strip()
    for suffix in [" LLC", " INC", " CORP", " CO", " LTD", " L.L.C.", " L.L.C",
                   " INC.", " CORP.", " CO.", " LTD.", ",", "."]:
        n = n.replace(suffix, "")
    return n.strip()


def init_db(conn):
    """Create all tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS contractors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            business_name_normalized TEXT,
            phone TEXT,
            phone_alt TEXT,
            email TEXT,
            website TEXT,
            street TEXT,
            street2 TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            county TEXT,
            entity_type TEXT,
            entity_type_desc TEXT,
            year_established INTEGER,
            owner_name TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contractor_id INTEGER REFERENCES contractors(id),
            state TEXT NOT NULL,
            license_number TEXT,
            license_type TEXT,
            license_type_desc TEXT,
            classification TEXT,
            classification_desc TEXT,
            classification2 TEXT,
            classification2_desc TEXT,
            status TEXT,
            status_desc TEXT,
            issue_date TEXT,
            expiration_date TEXT,
            suspend_date TEXT,
            ubi TEXT,
            source TEXT,
            source_url TEXT,
            raw_data JSON,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS insurance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contractor_id INTEGER REFERENCES contractors(id),
            license_number TEXT,
            state TEXT,
            insurance_company TEXT,
            insurance_agency TEXT,
            policy_number TEXT,
            coverage_amount REAL,
            effective_date TEXT,
            expiration_date TEXT,
            cancel_date TEXT,
            source TEXT,
            raw_data JSON,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS bond_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contractor_id INTEGER REFERENCES contractors(id),
            license_number TEXT,
            state TEXT,
            bond_company TEXT,
            bond_account_id TEXT,
            bond_amount REAL,
            effective_date TEXT,
            expiration_date TEXT,
            cancel_date TEXT,
            is_impaired INTEGER DEFAULT 0,
            impaired_date TEXT,
            source TEXT,
            raw_data JSON,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS officers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contractor_id INTEGER REFERENCES contractors(id),
            name TEXT,
            title TEXT,
            start_date TEXT,
            end_date TEXT,
            source TEXT,
            raw_data JSON,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contractor_id INTEGER REFERENCES contractors(id),
            trade TEXT,
            raw_classification TEXT,
            source TEXT
        );

        CREATE TABLE IF NOT EXISTS source_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_state TEXT,
            source_id TEXT,
            source_url TEXT,
            business_name TEXT,
            phone TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            raw_data JSON,
            contractor_id INTEGER REFERENCES contractors(id),
            match_confidence REAL,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS ingestion_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            source_state TEXT,
            file_name TEXT,
            file_url TEXT,
            records_total INTEGER DEFAULT 0,
            records_new INTEGER DEFAULT 0,
            records_updated INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT
        );

        -- Indexes for fast lookups
        CREATE INDEX IF NOT EXISTS idx_contractors_name_norm ON contractors(business_name_normalized);
        CREATE INDEX IF NOT EXISTS idx_contractors_state ON contractors(state);
        CREATE INDEX IF NOT EXISTS idx_contractors_phone ON contractors(phone);
        CREATE INDEX IF NOT EXISTS idx_licenses_number ON licenses(license_number);
        CREATE INDEX IF NOT EXISTS idx_licenses_ubi ON licenses(ubi);
        CREATE INDEX IF NOT EXISTS idx_licenses_expiration ON licenses(expiration_date);
        CREATE INDEX IF NOT EXISTS idx_licenses_state ON licenses(state);
        CREATE INDEX IF NOT EXISTS idx_insurance_expiration ON insurance_records(expiration_date);
        CREATE INDEX IF NOT EXISTS idx_insurance_license ON insurance_records(license_number);
        CREATE INDEX IF NOT EXISTS idx_bond_expiration ON bond_records(expiration_date);
        CREATE INDEX IF NOT EXISTS idx_bond_license ON bond_records(license_number);
        CREATE INDEX IF NOT EXISTS idx_officers_contractor ON officers(contractor_id);
        CREATE INDEX IF NOT EXISTS idx_source_records_source ON source_records(source, source_id);
        CREATE INDEX IF NOT EXISTS idx_source_records_contractor ON source_records(contractor_id);
    """)
    conn.commit()


def ingest_general(conn, limit=None):
    """Ingest WA general contractor license data."""
    csv_path = RAW_DIR / "wa_contractors_general.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return

    run_id = conn.execute("""
        INSERT INTO ingestion_runs (source, source_state, file_name, file_url, started_at)
        VALUES (?, ?, ?, ?, ?)
    """, (SOURCE, STATE, csv_path.name,
          "https://data.wa.gov/api/views/m8qx-ubtq/rows.csv",
          datetime.now(timezone.utc).isoformat())).lastrowid
    conn.commit()

    # Build lookup of existing license numbers
    existing = {}
    for row in conn.execute("SELECT id, license_number FROM licenses WHERE state = 'WA' AND source = ?", (SOURCE,)):
        existing[row[1]] = row[0]

    new_count = 0
    updated_count = 0
    total = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        batch_contractors = []
        batch_licenses = []
        batch_categories = []
        batch_source_records = []

        for row in reader:
            total += 1
            if limit and total > limit:
                break

            lic_num = row.get("ContractorLicenseNumber", "").strip()
            if not lic_num:
                continue

            biz_name = row.get("BusinessName", "").strip()
            phone = row.get("PhoneNumber", "").strip() or None
            if phone and len(phone) == 10:
                phone = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

            # Skip if already ingested
            if lic_num in existing:
                updated_count += 1
                continue

            new_count += 1

            # Insert contractor
            cid = conn.execute("""
                INSERT INTO contractors (
                    business_name, business_name_normalized, phone,
                    street, street2, city, state, zip,
                    entity_type, entity_type_desc, owner_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                biz_name,
                normalize_name(biz_name),
                phone,
                row.get("Address1", "").strip() or None,
                row.get("Address2", "").strip() or None,
                row.get("City", "").strip() or None,
                row.get("State", "").strip() or None,
                row.get("Zip", "").strip() or None,
                row.get("BusinessTypeCode", "").strip() or None,
                row.get("BusinessTypeCodeDesc", "").strip() or None,
                row.get("PrimaryPrincipalName", "").strip() or None,
            )).lastrowid

            # Insert license
            conn.execute("""
                INSERT INTO licenses (
                    contractor_id, state, license_number,
                    license_type, license_type_desc,
                    classification, classification_desc,
                    classification2, classification2_desc,
                    status, status_desc,
                    issue_date, expiration_date, suspend_date,
                    ubi, source, source_url, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, STATE, lic_num,
                row.get("ContractorLicenseTypeCode", "").strip() or None,
                row.get("ContractorLicenseTypeCodeDesc", "").strip() or None,
                row.get("SpecialtyCode1", "").strip() or None,
                row.get("SpecialtyCode1Desc", "").strip() or None,
                row.get("SpecialtyCode2", "").strip() or None,
                row.get("SpecialtyCode2Desc", "").strip() or None,
                row.get("StatusCode", "").strip() or None,
                row.get("ContractorLicenseStatus", "").strip() or None,
                parse_date(row.get("LicenseEffectiveDate", "")),
                parse_date(row.get("LicenseExpirationDate", "")),
                parse_date(row.get("ContractorLicenseSuspendDate", "")),
                row.get("UBI", "").strip() or None,
                SOURCE,
                f"https://data.wa.gov/Labor/L-I-Contractor-License-Data-General/m8qx-ubtq",
                json.dumps(dict(row)),
            ))

            existing[lic_num] = cid

            # Insert categories from specialty codes
            for code_key, desc_key in [("SpecialtyCode1", "SpecialtyCode1Desc"),
                                        ("SpecialtyCode2", "SpecialtyCode2Desc")]:
                desc = row.get(desc_key, "").strip()
                if desc:
                    conn.execute("""
                        INSERT INTO categories (contractor_id, trade, raw_classification, source)
                        VALUES (?, ?, ?, ?)
                    """, (cid, desc, row.get(code_key, "").strip(), SOURCE))

            # Insert source record
            conn.execute("""
                INSERT INTO source_records (
                    source, source_state, source_id, source_url,
                    business_name, phone, street, city, state, zip,
                    raw_data, contractor_id, match_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                SOURCE, STATE, lic_num,
                f"https://secure.lni.wa.gov/verify/Detail.aspx?UBI={row.get('UBI', '')}",
                biz_name, phone,
                row.get("Address1", "").strip() or None,
                row.get("City", "").strip() or None,
                STATE,
                row.get("Zip", "").strip() or None,
                json.dumps(dict(row)),
                cid, 1.0,
            ))

            if new_count % 5000 == 0:
                conn.commit()
                print(f"    General: {new_count:,} new / {total:,} total")

    conn.commit()

    conn.execute("""
        UPDATE ingestion_runs SET records_total=?, records_new=?, records_updated=?, completed_at=?
        WHERE id=?
    """, (total, new_count, updated_count, datetime.now(timezone.utc).isoformat(), run_id))
    conn.commit()

    print(f"  General: {new_count:,} new, {updated_count:,} existing, {total:,} total")
    return existing  # license_number -> contractor_id


def ingest_insurance(conn, license_map, limit=None):
    """Ingest WA insurance data, linking to contractors by license number."""
    csv_path = RAW_DIR / "wa_contractors_insurance.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return

    run_id = conn.execute("""
        INSERT INTO ingestion_runs (source, source_state, file_name, file_url, started_at)
        VALUES (?, ?, ?, ?, ?)
    """, (f"{SOURCE}_insurance", STATE, csv_path.name,
          "https://data.wa.gov/api/views/ciwg-agsx/rows.csv",
          datetime.now(timezone.utc).isoformat())).lastrowid
    conn.commit()

    total = 0
    linked = 0
    unlinked = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if limit and total > limit:
                break

            lic_num = row.get("ContractorLicenseNumber", "").strip()
            cid = license_map.get(lic_num)

            if cid:
                linked += 1
            else:
                unlinked += 1
                continue  # skip unmatched for now

            conn.execute("""
                INSERT INTO insurance_records (
                    contractor_id, license_number, state,
                    insurance_company, insurance_agency,
                    policy_number, coverage_amount,
                    effective_date, expiration_date, cancel_date,
                    source, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, lic_num, STATE,
                row.get("InsuranceCompany", "").strip() or None,
                row.get("InsuranceAgencyName", "").strip() or None,
                row.get("InsurancePolicyNo", "").strip() or None,
                float(row["InsuranceAmt"]) if row.get("InsuranceAmt", "").strip() else None,
                parse_date(row.get("EffectiveDate", "")),
                parse_date(row.get("ExpirationDate", "")),
                parse_date(row.get("CancelDate", "")),
                SOURCE,
                json.dumps(dict(row)),
            ))

            if linked % 5000 == 0:
                conn.commit()

    conn.commit()
    conn.execute("""
        UPDATE ingestion_runs SET records_total=?, records_new=?, completed_at=?
        WHERE id=?
    """, (total, linked, datetime.now(timezone.utc).isoformat(), run_id))
    conn.commit()

    print(f"  Insurance: {linked:,} linked, {unlinked:,} unmatched, {total:,} total")


def ingest_bonds(conn, license_map, limit=None):
    """Ingest WA bond data."""
    csv_path = RAW_DIR / "wa_contractors_bond.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return

    run_id = conn.execute("""
        INSERT INTO ingestion_runs (source, source_state, file_name, file_url, started_at)
        VALUES (?, ?, ?, ?, ?)
    """, (f"{SOURCE}_bond", STATE, csv_path.name,
          "https://data.wa.gov/api/views/bzff-4fmt/rows.csv",
          datetime.now(timezone.utc).isoformat())).lastrowid
    conn.commit()

    total = 0
    linked = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if limit and total > limit:
                break

            lic_num = row.get("ContractorLicenseNumber", "").strip()
            cid = license_map.get(lic_num)
            if not cid:
                continue

            linked += 1

            exp_date = row.get("BondExpirationDate", "").strip()
            if exp_date == "Until Canceled":
                exp_date = None
            else:
                exp_date = parse_date(exp_date)

            conn.execute("""
                INSERT INTO bond_records (
                    contractor_id, license_number, state,
                    bond_company, bond_account_id, bond_amount,
                    effective_date, expiration_date, cancel_date,
                    is_impaired, impaired_date,
                    source, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, lic_num, STATE,
                row.get("BondFirmName", "").strip() or None,
                row.get("BondAccountID", "").strip() or None,
                float(row["BondAmt"]) if row.get("BondAmt", "").strip() else None,
                parse_date(row.get("BondEffectiveDate", "")),
                exp_date,
                parse_date(row.get("BondCancelDate", "")),
                1 if row.get("BondImpaired", "").strip() else 0,
                parse_date(row.get("BondImpairedDate", "")),
                SOURCE,
                json.dumps(dict(row)),
            ))

            if linked % 5000 == 0:
                conn.commit()

    conn.commit()
    conn.execute("""
        UPDATE ingestion_runs SET records_total=?, records_new=?, completed_at=?
        WHERE id=?
    """, (total, linked, datetime.now(timezone.utc).isoformat(), run_id))
    conn.commit()

    print(f"  Bonds: {linked:,} linked, {total:,} total")


def ingest_principals(conn, license_map, limit=None):
    """Ingest WA principal/officer data."""
    csv_path = RAW_DIR / "wa_contractors_principal.csv"
    if not csv_path.exists():
        print(f"  SKIP: {csv_path} not found")
        return

    run_id = conn.execute("""
        INSERT INTO ingestion_runs (source, source_state, file_name, file_url, started_at)
        VALUES (?, ?, ?, ?, ?)
    """, (f"{SOURCE}_principal", STATE, csv_path.name,
          "https://data.wa.gov/api/views/4xk5-x9j6/rows.csv",
          datetime.now(timezone.utc).isoformat())).lastrowid
    conn.commit()

    total = 0
    linked = 0

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if limit and total > limit:
                break

            lic_num = row.get("ContractorLicenseNumber", "").strip()
            cid = license_map.get(lic_num)
            if not cid:
                continue

            linked += 1
            name = row.get("PrincipalName", "").strip()
            if not name:
                continue

            # Determine title from business type
            btype = row.get("BusinessTypeCodeDesc", "").strip()
            title = "Principal"
            if "Sole" in btype:
                title = "Owner"
            elif "Partner" in btype:
                title = "Partner"
            elif "Corp" in btype:
                title = "Officer"
            elif "LLC" in btype or "Limited" in btype:
                title = "Member"

            conn.execute("""
                INSERT INTO officers (
                    contractor_id, name, title,
                    start_date, end_date,
                    source, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, name, title,
                parse_date(row.get("StartDate", "")),
                parse_date(row.get("EndDate", "")),
                SOURCE,
                json.dumps(dict(row)),
            ))

            if linked % 5000 == 0:
                conn.commit()

    conn.commit()
    conn.execute("""
        UPDATE ingestion_runs SET records_total=?, records_new=?, completed_at=?
        WHERE id=?
    """, (total, linked, datetime.now(timezone.utc).isoformat(), run_id))
    conn.commit()

    print(f"  Principals: {linked:,} linked, {total:,} total")


def show_status(conn):
    """Show ingestion stats."""
    print("=" * 60)
    print("  Contractor License Database — Status")
    print("=" * 60)

    contractors = conn.execute("SELECT COUNT(*) FROM contractors").fetchone()[0]
    licenses = conn.execute("SELECT COUNT(*) FROM licenses").fetchone()[0]
    insurance = conn.execute("SELECT COUNT(*) FROM insurance_records").fetchone()[0]
    bonds = conn.execute("SELECT COUNT(*) FROM bond_records").fetchone()[0]
    officers = conn.execute("SELECT COUNT(*) FROM officers").fetchone()[0]
    categories = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    sources = conn.execute("SELECT COUNT(*) FROM source_records").fetchone()[0]

    print(f"  Contractors:       {contractors:>10,}")
    print(f"  Licenses:          {licenses:>10,}")
    print(f"  Insurance records: {insurance:>10,}")
    print(f"  Bond records:      {bonds:>10,}")
    print(f"  Officers:          {officers:>10,}")
    print(f"  Categories:        {categories:>10,}")
    print(f"  Source records:     {sources:>10,}")
    print()

    # By state
    print("  By state:")
    for row in conn.execute("SELECT state, COUNT(*) FROM contractors GROUP BY state ORDER BY COUNT(*) DESC LIMIT 10"):
        print(f"    {row[0] or '?':>5}: {row[1]:>10,}")
    print()

    # License status breakdown
    print("  License status:")
    for row in conn.execute("SELECT status_desc, COUNT(*) FROM licenses GROUP BY status_desc ORDER BY COUNT(*) DESC"):
        print(f"    {row[0] or '?':>20}: {row[1]:>10,}")
    print()

    # Insurance expiration dates (upcoming)
    upcoming_ins = conn.execute("""
        SELECT COUNT(*) FROM insurance_records
        WHERE expiration_date BETWEEN date('now') AND date('now', '+90 days')
          AND cancel_date IS NULL
    """).fetchone()[0]
    print(f"  Insurance expiring in 90 days: {upcoming_ins:,}")

    upcoming_lic = conn.execute("""
        SELECT COUNT(*) FROM licenses
        WHERE expiration_date BETWEEN date('now') AND date('now', '+90 days')
    """).fetchone()[0]
    print(f"  Licenses expiring in 90 days:  {upcoming_lic:,}")
    print()

    # Ingestion runs
    print("  Ingestion runs:")
    for row in conn.execute("""
        SELECT source, source_state, file_name, records_total, records_new, completed_at
        FROM ingestion_runs ORDER BY id DESC LIMIT 10
    """):
        print(f"    {row[0]:>20} | {row[1]} | {row[3]:>8,} total | {row[4]:>8,} new | {row[5] or 'running'}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Ingest WA contractor license data")
    parser.add_argument("--status", action="store_true", help="Show ingestion stats")
    parser.add_argument("--sample", type=int, default=None, help="Limit records (test)")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")

    init_db(conn)

    if args.status:
        show_status(conn)
        conn.close()
        return

    print(f"Washington State Contractor License Ingestion")
    print(f"  DB: {DB_PATH}")
    print(f"  Raw data: {RAW_DIR}")
    print()

    # Step 1: General (creates contractors + licenses)
    print("Step 1/4: General license data...")
    license_map = ingest_general(conn, limit=args.sample)

    if not license_map:
        print("  No license map returned, skipping linked tables")
        conn.close()
        return

    # Step 2: Insurance
    print("Step 2/4: Insurance records...")
    ingest_insurance(conn, license_map, limit=args.sample)

    # Step 3: Bonds
    print("Step 3/4: Bond records...")
    ingest_bonds(conn, license_map, limit=args.sample)

    # Step 4: Principals/Officers
    print("Step 4/4: Principal/officer records...")
    ingest_principals(conn, license_map, limit=args.sample)

    print()
    show_status(conn)
    conn.close()


if __name__ == "__main__":
    main()
