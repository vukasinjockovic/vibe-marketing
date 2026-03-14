# Colorado — Contractor Data Sources

Last updated: 2026-03-11

## Important: No General Contractor License

Colorado has **no state-level general contractor license**. Only electricians and plumbers are licensed at the state level through DORA (Division of Regulatory Agencies). HVAC, roofing, and general contracting are regulated at the municipal level only.

## Ingested Sources

### 1. DORA Professional Licenses (co_dora)
- **Source:** https://data.colorado.gov/Regulations/Professional-and-Occupational-Licenses-in-Colorado/7s5z-vewr
- **Format:** Socrata CSV download (441 MB, 1.57M total rows)
- **Construction rows:** 229,809 (filtered from 1.57M total professional licenses)
- **Cost:** Free
- **Updated:** Nightly on data.colorado.gov
- **Tables populated:**
  - `master.contractors` — 181,712 new (16,951 businesses + 164,761 individuals)
  - `master.licenses` — 229,809
  - `master.categories` — 183,636

### License Types Ingested

| Prefix | Description | Records | Active |
|--------|------------|---------|--------|
| APE | Electrical Apprentice | 90,336 | 15,092 |
| AP | Plumbing Apprentice | 40,662 | 9,580 |
| JW | Journeyman Electrician | 32,406 | 11,909 |
| ME | Master Electrician | 13,150 | 7,168 |
| EC | Electrical Contractor | 12,288 | 4,632 |
| JP | Journeyworker Plumber | 11,696 | 2,714 |
| MP | Master Plumber | 9,212 | 4,803 |
| RW | Residential Wireman | 6,342 | 1,860 |
| EL | Electrical (generic) | 5,910 | 2,715 |
| PC | Plumbing Contractor | 5,274 | 2,991 |
| RP | Residential Plumber | 2,533 | 462 |

**Business licenses** (EC, PC): `entityName` → `contractors.business_name`
**Individual licenses** (all others): `firstName middleName lastName` → `contractors.business_name`, `entity_type = "Individual"`

## Not Ingested

### Colorado Workers' Compensation
- **Source:** CDLE (Colorado Dept. of Labor & Employment)
- **Access:** Individual lookup only at https://cdle.colorado.gov/verify-WC
- **Status:** SKIPPED — no bulk data available

### Colorado Bond/Insurance Data
- **Source:** Colorado DOI (Division of Insurance)
- **Status:** SKIPPED — no contractor-specific bulk data published

### CO Secretary of State Business Entities
- **Source:** https://data.colorado.gov/Business/Business-Entities-in-Colorado/4ykn-tg5h
- **Records:** 2,999,591
- **Status:** SKIPPED — useful for cross-referencing but not core contractor data

### CDPHE Asbestos/Lead Certifications
- **Source:** Colorado Dept. of Public Health & Environment
- **Status:** SKIPPED — individual lookup only

## Database Summary

| Table | CO Records | Notes |
|-------|-----------|-------|
| master.contractors | 182,131 | 16,951 businesses + 164,761 individuals |
| master.licenses | 229,809 | 11 license types (electrical + plumbing) |
| master.categories | 183,636 | Electrical or Plumbing trade per contractor |
| master.bond_records | 0 | No bond data available |
| master.insurance_records | 0 | No WC bulk data available |
| master.officers | 0 | No separate personnel file |

## Ingestion Script

```bash
cd /var/www/fatstud.businesspress.dev/data/gov/CO

# Full ingest
python3 ingest_co.py

# Check status
python3 ingest_co.py --status

# Purge and re-ingest
python3 ingest_co.py --purge

# Test with sample
python3 ingest_co.py --sample 100
```

## Key Differences from Other States

| Feature | WA | CA | CO |
|---------|----|----|-----|
| License scope | All contractors | All contractors | Electrical + Plumbing only |
| Bond data | Yes | Yes (3 types) | No |
| Insurance/WC | Yes | Yes | No |
| Personnel | 248K | 401K | N/A (individuals are in main file) |
| Entity types | Businesses | Businesses | Mix (17K businesses + 165K individuals) |
| Data format | Socrata CSV | ASP.NET portal | Socrata CSV |
