# Idaho DOPL Scraper & Ingestion - Kraken Handoff

## Task
Build scraper and ingestion script for Idaho (ID) contractor data from DOPL.

## Checkpoints
**Task:** Idaho DOPL scraper + ingestion
**Started:** 2026-03-13T18:00:00Z
**Last Updated:** 2026-03-13T20:10:00Z

### Phase Status
- Phase 1 (Portal Probing): VALIDATED - DOPL portal is GL Solutions FAST framework (JS SPA), requires Playwright
- Phase 2 (Scraper Written): VALIDATED - scrape_id_dopl.py works with Playwright bulk list search
- Phase 3 (Ingestion Written): VALIDATED - ingest_id.py handles all 8 construction boards
- Phase 4 (Test Scrape): VALIDATED - 75 records scraped and ingested successfully (0 errors)
- Phase 5 (Full Scrape): IN_PROGRESS - Running for all 8 boards, Active status

### Validation State
```json
{
  "test_count": 75,
  "tests_passing": 75,
  "files_modified": [
    "/var/www/fatstud.businesspress.dev/data/gov/ID/scrape_id_dopl.py",
    "/var/www/fatstud.businesspress.dev/data/gov/ID/ingest_id.py"
  ],
  "last_test_command": "python3 ingest_id.py --sample 75",
  "last_test_exit_code": 0
}
```

### Resume Context
- Full scrape running as PID (check: ps aux | grep scrape_id_dopl)
- After scrape completes, run: python3 ingest_id.py
- Then verify: python3 ingest_id.py --status

## Key Findings

### DOPL Portal Architecture
- NOT the old ASP.NET WebForms described in README
- Completely rebuilt on GL Solutions "FAST" framework (JavaScript SPA)
- Both apps.dopl.idaho.gov and edopl.idaho.gov serve same SPA
- All content loaded via AJAX, requires Playwright headless browser
- eTRAKiT at web.dbs.idaho.gov is DOWN/unreachable (connection timeout)

### Board Codes (from jQuery autocomplete source)
| Code | Label | Est. Active Pages |
|------|-------|-------------------|
| BOCNTR | Contractors Board | 965 |
| BOPWLC | Public Works Contractors License Board | ~138 |
| BOELEC | Electrical Board | 841 |
| BOPLMB | Plumbing Board | ~400 |
| BOHVAC | HVAC Board | ~300 |
| BOELEV | Elevator Program | ~50 |
| BOFBS | Factory Built Structures Board | ~20 |
| BOBCFB | Idaho Building Code Board | ~100 |

### Data Quality
- Contractors Board: 100% fill rate for city, zip, street, county
- Trade boards (ELE, PLU, HVA): Only contractor licenses have addresses
- Individual tradespersons have no address in bulk list
- No email or phone in bulk list (may be in Excel export)
- DBA field present for ~80% of contractor registrations
- State shown as full name (e.g., "IDAHO"), normalized to 2-letter code in ingestion

### Export Button
- Does NOT trigger traditional download
- May generate client-side Excel (blocked in headless)
- Pagination scraping is reliable alternative (25 rows/page, 7 pages/min)
