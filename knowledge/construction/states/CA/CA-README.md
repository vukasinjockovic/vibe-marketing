# California — Contractor Data Sources

Last updated: 2026-03-11

## Ingested Sources

### 1. CSLB License Master (ca_cslb_master)
- **Source:** https://www.cslb.ca.gov/onlineservices/dataportal/ContractorList.aspx
- **Format:** CSV download (74 MB)
- **Records:** 242,794
- **Cost:** Free
- **Updated:** ~daily on CSLB portal
- **Tables populated:**
  - `master.contractors` — 241,960 new contractors (business name, phone, address, county, entity type)
  - `master.licenses` — 242,794 (license number, type CSLB, classifications, status, issue/expiration/reissue dates)
  - `master.bond_records` — 247,274 (3 bond types per license: contractor, worker_llc, disciplinary)
  - `master.insurance_records` — 115,886 (WC company, policy number, effective/expiration dates from master)
  - `master.categories` — 309,416 (all classification codes mapped to trade descriptions)
- **Coverage:** All renewed or expired-but-renewable licenses. Cancelled/revoked/expired-non-renewable excluded.
- **Classifications:** 5,122 unique combos across 60+ CSLB codes (A, B, C-2 through C-61, D-series, ASB, HAZ)

### 2. CSLB Workers' Compensation (ca_cslb_wc)
- **Source:** Same portal as above
- **Format:** CSV (31 MB)
- **Records:** 240,381
- **Cost:** Free
- **Tables populated:**
  - `master.insurance_records` — 223 additional unique records (deduped against master file)
- **Note:** Most WC data overlaps with master file. This file adds historical WC records not in the current master snapshot.

### 3. CSLB Personnel (ca_cslb_personnel)
- **Source:** Same portal as above
- **Format:** CSV (82 MB)
- **Records:** 402,661
- **Cost:** Free
- **Tables populated:**
  - `master.officers` — 401,067 (name, title, association/disassociation dates)
- **Titles:** Officer, CEO/President, Sole Owner, RMO, RME, General Partner, LLC Manager/Member/Director, Qualifying Partner
- **Name format:** Fixed-width LAST(35) FIRST(15) MIDDLE parsed to "First Middle Last"

## Not Ingested

### CSLB Complaints & Citations
- **Source:** https://www.cslb.ca.gov/onlineservices/dataportal/
- **Cost:** $245 (paid data request)
- **Content:** Complaint records, citation details, enforcement actions
- **Status:** SKIPPED — not worth the cost for MVP

### Cal/OSHA Inspections
- **Source:** Federal OSHA bulk data already covers Cal/OSHA
- **How:** Cal/OSHA records have RID codes starting with "5" in osha.inspections table
- **Status:** ALREADY COVERED via federal OSHA ingestion (schema `osha`)

### CA Secretary of State Business Entities
- **Source:** https://www.sos.ca.gov/business-programs/business-entities/statements-of-information
- **Cost:** $100 for master unload (17M entities)
- **Content:** Business registration, agent of service, entity status
- **Status:** SKIPPED — useful for entity cross-referencing but not core contractor data

### DCA Open Data Portal
- **Source:** https://www.dca.ca.gov/data/index.shtml
- **Content:** Aggregate licensing stats for CSLB (not individual records)
- **Status:** SKIPPED — we already have individual records from CSLB

## Database Summary

| Table | CA Records | Source |
|-------|-----------|--------|
| master.contractors | 243,935 | ca_cslb_master |
| master.licenses | 242,794 | ca_cslb_master |
| master.bond_records | 247,274 | ca_cslb_master |
| master.insurance_records | 116,109 | ca_cslb_master + ca_cslb_wc |
| master.officers | 401,067 | ca_cslb_personnel |
| master.categories | 309,416 | ca_cslb_master |

## Ingestion Script

```bash
cd /var/www/fatstud.businesspress.dev/data/gov/CA

# Full ingest (all 3 sources)
python3 ingest_ca.py

# Individual sources
python3 ingest_ca.py --master-only
python3 ingest_ca.py --wc-only
python3 ingest_ca.py --personnel-only

# Check status
python3 ingest_ca.py --status

# Purge and re-ingest
python3 ingest_ca.py --purge

# Test with sample
python3 ingest_ca.py --sample 100
```

## Raw Data Files

Located at: `/var/www/vibe-marketing/knowledge/construction/states/CA/raw/`

| File | Size | Rows |
|------|------|------|
| MasterLicenseData.csv | 74 MB | 242,794 |
| WorkersCompData.csv | 31 MB | 240,381 |
| PersonnelData.csv | 82 MB | 402,661 |

Downloaded via Playwright from CSLB data portal (ASP.NET postback, WAF blocks direct curl).

## Field Mapping

See: `states/CA/mappings/ca_field_mapping.yaml`

## Key Differences from WA

| Feature | WA | CA |
|---------|----|----|
| Source format | Socrata API (CSV) | ASP.NET portal download |
| Bond types | Single (no type distinction) | 3 types: contractor, worker_llc, disciplinary |
| Classifications | 2 specialty codes per license | Up to 10+ per license (pipe-delimited) |
| Personnel | 248K principals | 401K officers with titles and dates |
| UBI equivalent | WA UBI | None (license number is the key) |
| Status values | ACTIVE/INACTIVE/etc | CLEAR + 19 suspension types |
