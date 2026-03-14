# Government Data Sources for Contractor Intelligence

Last updated: 2026-03-10

## Nationwide Sources

### OSHA Enforcement Data
- **URL:** https://enforcedata.dol.gov/views/data_catalogs.php
- **Format:** CSV bulk download (~3.5 GB), updated daily
- **Content:** Inspections, violations, penalties, severity classifications
- **API:** https://developer.dol.gov/health-and-safety/dol-osha-enforcement/
- **Status:** INGESTED for WA, available nationwide

### OSHA ITA Form 300A (Establishment Injury Data)
- **URL:** https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data
- **Format:** CSV annual bulk download
- **Content:** TRIR and DART rates for establishments with 20+ employees
- **Lag:** Annual (submitted March, published mid-year)
- **Status:** NOT INGESTED

### OSHA Severe Injury Reports
- **URL:** https://www.osha.gov/severe-injury-reports
- **Format:** Dashboard, launched Sept 2024
- **Lag:** ~6 months
- **Status:** NOT INGESTED

---

## AG Consumer Complaints — Open Data (3 states)

### Washington
- **Dataset:** https://data.wa.gov/Consumer-Protection/Attorney-General-Consumer-Complaints/gpri-47xz
- **API:** `https://data.wa.gov/resource/gpri-47xz.json`
- **Records:** 265,941 total; ~10,250 in "Contractors" category
- **Updated:** Daily
- **Fields:** Business name, address, NAICS, complaint date, status, savings
- **Missing:** No complaint narrative, no complaint type, 47% blank business names
- **Status:** NOT INGESTED

### Oregon
- **Dataset:** https://data.oregon.gov/Public-Safety/Oregon-Consumer-Complaints/bstj-mz34
- **API:** `https://data.oregon.gov/resource/bstj-mz34.json`
- **Window:** Rolling 3 years
- **Status:** NOT INGESTED

### Massachusetts
- **URL:** https://www.mass.gov/info-details/list-of-complaints-received-by-the-attorney-generals-consumer-advocacy-and-response-division
- **Format:** Excel/PDF export
- **Window:** 6 years rolling
- **Also publishes:** Debarred contractors list
- **Status:** NOT INGESTED

---

## AG Complaints — Searchable/Scrapeable (4 states)

### Virginia
- **URL:** https://www.oag.state.va.us/consumer-protection/complaint/search/
- **Search by:** Company, industry, topic, geography

### Ohio
- **Complaint summary:** https://complaintsummary.ohioattorneygeneral.gov/
- **Lawsuit search:** https://lawsuitsearch.ohioattorneygeneral.gov/

### California CSLB (contractor-specific)
- **Data portal:** https://www.cslb.ca.gov/onlineservices/dataportal/
- **Coverage:** 285K contractors, complaints, citations, license status

### NYC (city-level)
- **Dataset:** https://nycopendata.socrata.com/Business/Consumer-Services-Mediated-Complaints/nre2-6m2s

---

## AG Complaints — Records Request Required (43 states)

Most state AGs treat complaints as public records but don't publish bulk data.
Use each state's public records act (FOIA equivalent) if needed.
Not worth pursuing for MVP — better data exists via OSHA, BBB, Angi, Google Maps.

---

## State Contractor Licensing Boards

### Washington L&I
- **Dataset:** https://data.wa.gov/Labor/L-I-Contractor-License-Data-General/m8qx-ubtq
- **API:** `https://data.wa.gov/resource/m8qx-ubtq.json`
- **Fields:** License number, type, specialty codes, effective/expiration dates, status, suspend date, UBI
- **Status:** INGESTED

### California CSLB
- **URL:** https://www.cslb.ca.gov/onlineservices/dataportal/
- **Coverage:** 285K contractors
- **Status:** NOT INGESTED

### Oregon CCB
- **URL:** https://www.oregon.gov/ccb/pages/consumer-tools.aspx
- **Separate from AG data:** Contractor-specific disciplinary records
- **Status:** NOT INGESTED

---

## EMR (Experience Modification Rate)

EMR is NOT publicly available. Controlled by NCCI (private org, no FOIA).
Requires employer authorization (FEIN + policy number + signed letter).

**Proxy approach:** Calculate composite safety score from:
1. OSHA violation frequency + severity
2. ITA Form 300A TRIR/DART rates
3. BLS industry benchmarks by NAICS code
4. Workers' comp coverage status (state-by-state)

---

## Safety Certification Platforms (Closed)

- **ISNetworld** — ~70K subscribers, $400-1,200/yr per contractor, no public API
- **Avetta** — Similar model, no public data
- **Veriforce** — Pipeline/energy focused, closed

**Signal detection:** Many contractors display ISNetworld/Avetta badges on websites — scrapeable as binary signal.

**OSHA VPP Participants:** ~2,300 worksites publicly listed at https://www.osha.gov/vpp

---

## Legal Notes

- Publishing government complaint data: Protected by fair report privilege
- Truth is absolute defense against defamation claims
- WA Anti-SLAPP law (2021) provides expedited dismissal + fee recovery
- Include disclaimer: "The existence of a complaint is not evidence of wrongdoing"

---

## Priority Order for Ingestion

1. OSHA enforcement CSVs (nationwide, daily, free) — already have for WA
2. WA AG complaints (Socrata API, free, 10K contractor records)
3. OR AG complaints (Socrata API, free)
4. OSHA ITA Form 300A (nationwide, annual)
5. CA CSLB data portal (285K contractors)
6. MA AG complaints (Excel export)
7. VA/OH complaint scraping (if needed)
