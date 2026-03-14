# SC LLR Scraper + Ingest — Handoff

## Task
Build South Carolina LLR contractor license scraper and ingest script for verify.llronline.com (CLB div=69 and RBC div=46).

## Checkpoints
**Task:** SC LLR scraper + ingest
**Started:** 2026-03-14T04:00:00Z
**Last Updated:** 2026-03-14T05:00:00Z

### Phase Status
- Phase 1 (Probe): VALIDATED — site geo-blocked from EU, form structure analyzed via Wayback Machine
- Phase 2 (Tests Written): VALIDATED (83 tests passing)
- Phase 3 (Scraper Built): VALIDATED — scrape_sc_llr.py with Playwright + requests modes
- Phase 4 (Ingest Built): VALIDATED — ingest_sc.py with CLB + RBC support
- Phase 5 (Run Scraper): BLOCKED — needs US proxy access
- Phase 6 (Run Ingest): PENDING — waiting on scraper data

### Validation State
```json
{
  "test_count": 83,
  "tests_passing": 83,
  "files_modified": [
    "SC/scrape_sc_llr.py",
    "SC/ingest_sc.py",
    "SC/SC-README.md",
    "tests/test_sc_llr.py"
  ],
  "last_test_command": "cd /var/www/fatstud.businesspress.dev/data/gov && python3 -m pytest tests/test_sc_llr.py -v",
  "last_test_exit_code": 0
}
```

### Resume Context
- Current focus: Scraper and ingest are complete and tested. Blocked on network access.
- Next action: Obtain US proxy access, then run `python3 scrape_sc_llr.py --proxy socks5://host:port --test` to verify connectivity, then full scrape.
- Blockers:
  1. verify.llronline.com geo-blocks non-US IPs (167.7.126.249 unreachable from EU)
  2. DataImpulse proxy credits exhausted (TRAFFIC_EXHAUSTED)
  3. SOCKS proxy on :61080 exits via Tor (blocked by site)
  4. Site uses reCAPTCHA v2 invisible (may or may not be server-validated)

## Probe Findings

### CLB (div=69) — Contractor's Licensing Board
- URL: https://verify.llronline.com/LicLookup/Contractors/Contractor.aspx?div=69
- Form fields: txt_lastName, txt_firstName, txt_licNum, txt_city, txt_state, ddl_type (36 license type options)
- reCAPTCHA: v2 invisible, sitekey 6Lc2X-saAAAAAPC6HatgHFOd8rCxCl-2yPTh44PN
- Submit: button.g-recaptcha triggers onSubmit(token) which clicks hidden btn_find
- License types: AC, AP, BL, BT, BR, BD, CT, CP, CCM, EL, GG, GD, HT, HY, HI, LP, MR, MS, MM, NR, PK, PL, PB, MB, 1P, 1U, RR, RG, RF, SF, SP, CLT, WL, WP, WF

### RBC (div=46) — Residential Builders Commission
- URL: https://verify.llronline.com/LicLookup/Resbu/Resbu.aspx?div=46
- Form fields: same as CLB + txt_company
- License types: COA(509), Electrical(518), Heating/Air(505), Home Builders(506,1104), Home Inspector(508), Plumbing(517), RB Exam Waiver(1104), Residential Non Mechanical(1109), Specialty(507), Volunteer(1103)
- Same reCAPTCHA

### Both share
- ASP.NET WebForms with __VIEWSTATE/__VIEWSTATEGENERATOR/__EVENTVALIDATION
- Form action includes AspxAutoDetectCookieSupport=1
- Pagination via __doPostBack with Page$N events
