# Kraken: MN WC Insurance Scraper + Ingestion

## Checkpoints
**Task:** Scrape MN DLI Workers' Compensation Insurance portal and ingest into master.insurance_records
**Started:** 2026-03-14T18:00:00Z
**Last Updated:** 2026-03-14T03:35:00Z

### Phase Status
- Phase 1 (Portal Analysis): VALIDATED
- Phase 2 (Build Scraper): VALIDATED (scrape_mn_wc.py with persistent Playwright browser)
- Phase 3 (Test Scraper): VALIDATED (XER: 1342 records, 245 employers from 16 clicks)
- Phase 4 (Full Scrape): -> IN_PROGRESS (~20K records after 42min, running in background)
- Phase 5 (Build Ingestor): VALIDATED (ingest_mn_wc.py built and ready)
- Phase 6 (Ingest): PENDING (run after scrape completes)
- Phase 7 (Verify): PENDING

### Validation State
```json
{
  "portal_url": "http://www.inslookup.doli.state.mn.us/Search.aspx",
  "portal_type": "ASP.NET WebForms",
  "fix_applied": "onclick handler calls ResetError() then WebForm_DoPostBackWithOptions() separately (original return short-circuits)",
  "scraper_architecture": "Single persistent Playwright browser, DB-derived 3-char prefix enumeration with auto-expansion",
  "total_base_prefixes": 3770,
  "excessive_rate": "~50%",
  "scrape_rate": "1.6-1.7 pfx/min",
  "records_at_42min": 19896,
  "estimated_total_time": "8-15 hours",
  "csv_file": "data/gov/MN/raw/mn_wc_insurance.csv",
  "checkpoint_file": "data/gov/MN/raw/mn_wc_checkpoint.json",
  "log_file": "/tmp/mn_wc_scrape.log",
  "test_results": {
    "XER": {"records": 1342, "employers": 245},
    "ABCD": {"records": 127, "employers": 5},
    "sample_5": {"records": 1030, "employers": 311, "time_min": 4.1}
  }
}
```

### Resume Context
- Current focus: Full scrape running in background (PID in ps aux | grep scrape_mn_wc)
- Next action: When scrape completes, run `python3 ingest_mn_wc.py` to load into DB
- Then verify: `python3 ingest_mn_wc.py --status`
- Monitoring: `tail /tmp/mn_wc_scrape.log` or `python3 scrape_mn_wc.py --status`
- Resume after interrupt: `python3 scrape_mn_wc.py --resume`
- Blockers: None (scrape is running autonomously)

### Key Files
- `/var/www/vibe-marketing/data/gov/MN/scrape_mn_wc.py` - Scraper
- `/var/www/vibe-marketing/data/gov/MN/ingest_mn_wc.py` - Ingestor
- `/var/www/vibe-marketing/data/gov/MN/raw/mn_wc_insurance.csv` - Output CSV
- `/var/www/vibe-marketing/data/gov/MN/raw/mn_wc_checkpoint.json` - Checkpoint
