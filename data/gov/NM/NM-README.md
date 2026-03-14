# New Mexico (NM) Contractor License Data

## Source

**Agency:** New Mexico Regulation & Licensing Department - Construction Industries Division (CID)
**Portal:** PSI Exams Public License Lookup
**URL:** https://public.psiexams.com/search.jsp?cid=445
**Format:** HTML scrape (search + detail pages)

## Estimated Records

~55,000-60,000 contractor licenses based on prefix survey.

## Scraping Strategy

### Portal Behavior

- **Search endpoint:** POST `https://public.psiexams.com/searchLicensee.do`
- **Detail endpoint:** POST `https://public.psiexams.com/licensee/showBusinessLicensee.do`
- **CAPTCHA:** Simple 5-character text CAPTCHA (grayscale image with strikethrough line)
- **Session:** JSESSIONID cookie; CAPTCHA answer must be included in every search POST
- **Result cap:** Server returns max 300 results per search prefix

### License Number Prefix Enumeration

License numbers range from 4-digit to 6-digit (e.g., 9930 to 948xxx).

**Prefix tree (adaptive depth):**
- 2-digit prefixes where result count < 300 (e.g., 10, 11, 62-79, 95-99)
- 3-digit prefixes where 2-digit parent is capped (e.g., 140-149, 200-299, 500-619, 800-949)
- 4-digit prefixes where 3-digit parent is capped (e.g., 3500-3599, 3600-3679, 3760-3929, etc.)
- Total: ~905 prefix searches

### CAPTCHA Handling

1. Create HTTP session, hit search page to get JSESSIONID
2. Download CAPTCHA from `/simplecaptcha.jpg`
3. Solve manually (OCR unreliable due to strikethrough line)
4. Include answer in every search POST for the session lifetime
5. Support multiple parallel sessions for faster scraping

## Data Fields

| Field | Source | Description |
|-------|--------|-------------|
| company_name | Detail page | Business/company name |
| license_number | Search/Detail | NM CID license number |
| phone | Detail page | Business phone number |
| license_status | Detail page | Active, Cancelled, etc. |
| issue_date | Detail page | License issue date |
| expiry_date | Detail page | License expiry date |
| volume | Detail page | Revenue tier (e.g., "$1000000.00 +") |
| street | Detail page | Business street address |
| city | Detail page | City |
| state | Detail page | Always "NM" |
| zip_code | Detail page | ZIP code |
| qp_name | Detail page | Qualifying Party name |
| qp_certificate_no | Detail page | QP certificate number |
| qp_classification | Detail page | Trade classification code (e.g., EE-98, GB98, MM04) |
| qp_attach_date | Detail page | Date QP was attached to this license |
| qp_status | Detail page | QP status (Attached, Detached, etc.) |

### Classification Code Mapping

| Prefix | Trade |
|--------|-------|
| EE, EL | Electrical |
| MM, MH, MC | HVAC/Mechanical |
| GB, GS, GA | General Contracting |
| PB | Plumbing |
| RG | Roofing |
| LN | Landscaping |
| EW, ER | Earthwork |
| FS, FL | Fire Protection |
| WW | Water Well Drilling |
| LP | LP Gas |
| BL | Blasting |
| PI | Pipeline |
| SE | Solar/Energy |

## Scripts

### Scraper: `scrape_nm_psi.py`

```bash
# Step 1: Create sessions and download CAPTCHAs
python3 scrape_nm_psi.py --prepare-sessions 5

# Step 2: Solve CAPTCHAs manually, then run
python3 scrape_nm_psi.py --captcha-answers "ans1,ans2,ans3,ans4,ans5"

# Resume from checkpoint
python3 scrape_nm_psi.py --captcha-answers "ans1" --resume

# Check progress
python3 scrape_nm_psi.py --status
```

### Ingester: `ingest_nm.py`

```bash
# Full ingest
python3 ingest_nm.py

# Test with sample
python3 ingest_nm.py --sample 500

# Show status
python3 ingest_nm.py --status

# Purge and re-ingest
python3 ingest_nm.py --purge
python3 ingest_nm.py
```

## Database Mapping

| CSV Field | DB Table | DB Column |
|-----------|----------|-----------|
| company_name | master.contractors | business_name |
| phone | master.contractors | phone |
| street/city/state/zip | master.contractors | street/city/state/zip |
| license_number | master.licenses | license_number |
| license_status | master.licenses | status |
| issue_date | master.licenses | issue_date |
| expiry_date | master.licenses | expiration_date |
| volume | master.licenses | raw_data->volume |
| qp_name | master.tradespersons | name |
| qp_classification | master.tradespersons | classification |
| qp_certificate_no | master.tradespersons | certification_number |

**Source identifier:** `NM_CID_PSI`
**Board name:** NM Construction Industries Division
**Dedup key:** (UPPER(business_name), UPPER(city))

## Verification

```sql
-- Count NM records
SELECT 'contractors' as type, COUNT(*)
FROM master.contractors WHERE state='NM' AND source='NM_CID_PSI'
UNION ALL
SELECT 'licenses', COUNT(*)
FROM master.licenses WHERE state='NM' AND source='NM_CID_PSI'
UNION ALL
SELECT 'tradespersons', COUNT(*)
FROM master.tradespersons WHERE state='NM' AND source='NM_CID_PSI';
```
