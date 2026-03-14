# NM PSI Contractor Scrape + Ingest

## Checkpoints
<!-- Resumable state for kraken agent -->
**Task:** Build NM CID contractor scraper for PSI Exams portal + ingest script for PostgreSQL
**Started:** 2026-03-14T01:30:00Z
**Last Updated:** 2026-03-14T03:45:00Z

### Phase Status
- Phase 1 (Scraper Built): VALIDATED (tested with 5 prefixes, 1238 records at 1.4/s)
- Phase 2 (Ingest Built): VALIDATED (tested with 1238 records, 0 errors)
- Phase 3 (Auth Fix): VALIDATED (fixed authenticate() to handle "No Records Found" vs "No record found")
- Phase 4 (Full Scrape): IN_PROGRESS (launched at 03:29 CET, 905 prefixes, ~55K estimated records)
- Phase 5 (Full Ingest): PENDING
- Phase 6 (Verification): PENDING

### Validation State
```json
{
  "test_records": 1238,
  "test_prefixes": 5,
  "scrape_rate": 1.4,
  "estimated_total_records": 55000,
  "estimated_total_time_hours": 11,
  "full_scrape_pid": 2891323,
  "full_scrape_log": "/tmp/nm_scrape_full.log",
  "files_created": [
    "data/gov/NM/scrape_nm_psi.py",
    "data/gov/NM/ingest_nm.py",
    "data/gov/NM/NM-README.md",
    "data/gov/NM/launch_scrape.py",
    "data/gov/NM/go_scrape.py",
    "data/gov/NM/run_scrape.py"
  ]
}
```

### Resume Context
- Current focus: Full scrape running in background (PID 2891323)
- Next action: When scrape completes, run `python3 ingest_nm.py` for full ingest
- Monitor: `tail -20 /tmp/nm_scrape_full.log` and `wc -l data/gov/NM/raw/nm_psi_all.csv`
- Resume scrape if interrupted: `python3 launch_scrape.py --resume` (need new CAPTCHA)
- Blockers: None - scrape is running

### Key Bug Fix
The `authenticate()` method in `scrape_nm_psi.py` was using prefix `9999` for test search, which returns 0 results with text "No Records Found for [9999]". But the check was looking for "No record found" (case/plural mismatch). Fixed by:
1. Changed test prefix to `99` (known to return 24 results)
2. Added check for "No Records Found" (capital R, plural)
3. Added fallback: if captchaAnswer field is NOT in response, CAPTCHA was accepted

### Post-Scrape Checklist
1. `wc -l data/gov/NM/raw/nm_psi_all.csv` (should be ~55,000+)
2. `python3 ingest_nm.py` (full ingest)
3. `python3 ingest_nm.py --status` (verify counts)
4. SQL verification query from NM-README.md
