# NY Dataset Ingestion Analysis: Schema Compatibility Report
Created: 2026-03-11
Author: architect-agent

## Overview

Analysis of 26 NY datasets (Tiers 1-4) against the existing `master.*` PostgreSQL schema (localhost:5433, us_contractors). The schema currently holds WA (145K contractors) and OR (76K contractors) data across 8 tables. NY introduces fundamentally new data patterns -- fragmented licensing (no statewide license), massive violation/enforcement data (21M+ OATH records), insurance details with carrier/policy info, and M/WBE certification data -- that require targeted schema extensions.

## Current Schema Summary

| Table | Rows | Key Sources |
|-------|------|-------------|
| contractors | 236,670 | WA (L&I), OR (CCB, BCD) |
| licenses | 264,456 | WA (L&I), OR (CCB) |
| insurance_records | 139,187 | WA (L&I), OR (CCB, WC, self-insured) |
| bond_records | 221,941 | WA (L&I) |
| officers | 295,916 | OR (CCB) |
| projects | 2,407,738 | WA (intent, affidavit), OR (ODOT) |
| violations | 18,281 | OR (AG complaints) |
| tradespersons | — | WA (prevailing wage) |
| categories | — | — |

---

## 1. GREEN -- Maps Perfectly to Existing Schema

These NY fields slot directly into existing columns with no modifications.

### Dataset #1: Contractor Registry (i4jv-zkey) -> 12,604 rows

| NY Field | Target | Notes |
|----------|--------|-------|
| Business Name | contractors.business_name | Direct |
| DBA Name | contractors.business_name (alt) | Store in raw_data or use business_name; no dba_name column exists |
| Business Type | contractors.entity_type | Values: Corporation, LLC, etc. |
| Address, City, State, Zip Code | contractors.street/city/state/zip | Direct |
| Phone | contractors.phone | Direct |
| Certificate Number | licenses.license_number | Maps as license |
| Issued Date | licenses.issue_date | Direct |
| Expiration Date | licenses.expiration_date | Direct |
| Status | licenses.status | Direct |
| Business Officers | officers.name + officers.title | Must parse multi-value field |

### Dataset #2: DOB License Info (t8hj-ruu2) -> 102,752 rows

| NY Field | Target | Notes |
|----------|--------|-------|
| License Number | licenses.license_number | Direct |
| License Type | licenses.license_type | GC, Plumber, Welder, etc. (20+ types) |
| License Status | licenses.status | Direct |
| First/Last Name | contractors.owner_name | Individual licensees |
| Business Name | contractors.business_name | Direct |
| Number + Street, City, State, Postcode | contractors.street/city/state/zip | Direct |
| Business Email | contractors.email | Direct |
| Business Phone Number | contractors.phone | Direct |

**Note**: `License SL No` is a system ID distinct from `License Number`. Store SL No in raw_data.

### Dataset #3: Active HIC Licenses (acd4-wkax) -> 69,231 rows

| NY Field | Target | Notes |
|----------|--------|-------|
| License Number | licenses.license_number | Direct |
| License Type | licenses.license_type | "Home Improvement Contractor" |
| Expiration Date | licenses.expiration_date | Direct |
| License Status | licenses.status | Direct |
| Initial Issuance Date | licenses.issue_date | Direct |
| Business Name | contractors.business_name | Direct |
| Building Number + Street, City, State, ZIP | contractors.street/city/state/zip | Direct |
| Contact Phone | contractors.phone | Direct |

### Dataset #6: SBS Certified Business (ci93-uc8s) -> 11,294 rows

| NY Field | Target | Notes |
|----------|--------|-------|
| Vendor Formal Name | contractors.business_name | Direct |
| NAICS Code | contractors.naics_code | Direct (column already exists from OR) |

### Datasets #7-10: DOB Permits -> 8.4M+ rows combined

| NY Field | Target | Notes |
|----------|--------|-------|
| Applicant Business Name | projects -> contractor match | Via contractor_id |
| Applicant License # | projects.contract_number (or raw_data) | Cross-ref to licenses |
| Job Description | projects.contract_name | Direct |
| Approved/Issued Date | projects.award_date/start_date | Direct |
| Applicant Business Address | raw_data | Not directly on projects |

### Dataset #11: Electrical Permits (dm9a-ab7w) -> 549,983 rows

| NY Field | Target | Notes |
|----------|--------|-------|
| Firm Name | contractors.business_name | Direct |
| License Number | licenses.license_number | Direct |
| License Type | licenses.license_type | Direct |
| GL Company, GL Policy, GL Expiration | insurance_records.insurance_company/policy_number/expiration_date | Direct |
| WC Company, WC Policy, WC Expiration | insurance_records (separate row) | Direct |

### Datasets #16-26: Violations -> 25M+ rows combined

| NY Field | Target | Notes |
|----------|--------|-------|
| Respondent Name | violations -> contractor match | Via contractor_id |
| Violation Date | violations.violation_date | Direct |
| Penalty Imposed | violations.penalty_amount | Direct |
| Violation Description | violations.description | Direct |
| Hearing Result | violations.resolution | Direct |

### Datasets #27-30: Specialty Licenses -> 13K rows

| NY Field | Target | Notes |
|----------|--------|-------|
| License Number | licenses.license_number | Direct |
| License Type | licenses.license_type | Elevator, Crane, Mold |
| Licensee Name | contractors.business_name or owner_name | Direct |
| Status | licenses.status | Direct |
| Issue/Expiration Date | licenses.issue_date/expiration_date | Direct |

---

## 2. YELLOW -- Fits with raw_data JSONB Overflow

These fields CAN be stored in the `raw_data` jsonb column of their respective tables but lose queryability.

### contractors.raw_data candidates

| NY Field | Source Dataset | Why JSONB for now |
|----------|---------------|-------------------|
| DBA Name | i4jv-zkey, ci93-uc8s | No dba_name column; infrequent query target |
| BIN (Building Identification Number) | acd4-wkax, permits | NYC-specific property identifier |
| BBL (Borough-Block-Lot) | acd4-wkax | NYC-specific property identifier |
| Borough, NTA, Community Board, Council District | acd4-wkax | NYC geo subdivisions |
| Business Description | ci93-uc8s | Free-text, variable length |
| Types of Construction Projects Performed | ci93-uc8s | Semi-structured list |
| Job Experience entries | ci93-uc8s | Complex nested: client/value/pct/description x3 |

### licenses.raw_data candidates

| NY Field | Source Dataset | Why JSONB for now |
|----------|---------------|-------------------|
| License SL No (system ID) | t8hj-ruu2 | Internal DOB system number; not a license number |

### violations.raw_data candidates

| NY Field | Source Dataset | Why JSONB for now |
|----------|---------------|-------------------|
| Charge Codes 1-10 | jz4z-kudi | Up to 10 parallel charge fields per ticket |
| Charge Sections 1-10 | jz4z-kudi | Parallel to charge codes |
| Charge Descriptions 1-10 | jz4z-kudi | Parallel to charge codes |
| Certification Status | 6bgk-3dad | ECB-specific workflow status |
| Hearing Status details | jz4z-kudi | Intermediate hearing statuses |
| Issuing Agency | jz4z-kudi | DOB, FDNY, DEP, etc. |

### projects.raw_data candidates

| NY Field | Source Dataset | Why JSONB for now |
|----------|---------------|-------------------|
| BIN | rbx6-tga4, ipu4-2q9a | NYC property identifier |
| Work Type sub-categories | w9ak-ipjd | Plumbing, sprinkler, boiler, etc. |
| Owner Name / Owner Business | rbx6-tga4 | Property owner, not contractor |
| Permit Type | rbx6-tga4, ipu4-2q9a | NB, A1, A2, DM, etc. |

---

## 3. RED -- Needs Schema Changes

### 3A. MUST-HAVE: New Columns on Existing Tables

#### master.contractors -- 5 new columns

```sql
-- DBA name (NY Contractor Registry, SBS list both provide this)
ALTER TABLE master.contractors ADD COLUMN dba_name text;

-- M/WBE certification status (SBS Certified list, Contractor Registry)
-- Values: MBE, WBE, DBE, LBE, EBE, or NULL
ALTER TABLE master.contractors ADD COLUMN mwbe_status text;

-- Ethnicity detail for M/WBE (SBS list: Black American, Hispanic American, etc.)
ALTER TABLE master.contractors ADD COLUMN mwbe_ethnicity text;

-- Debarment status (Contractor Registry, Non-Responsible Entities)
ALTER TABLE master.contractors ADD COLUMN is_debarred boolean DEFAULT false;

-- Source tracking (contractors table uniquely lacks a source column)
ALTER TABLE master.contractors ADD COLUMN source text;
```

**Rationale**: `dba_name` appears in 2 NY datasets and is a standard business identifier. `mwbe_status` and `is_debarred` are critical compliance/search fields used in government contracting. `source` is present on every other table but missing from contractors.

#### master.insurance_records -- 1 new column

```sql
-- Insurance type discriminator (GL, WC, Disability, Bond)
-- NY Electrical Permits provide GL, WC, and Disability as separate records
ALTER TABLE master.insurance_records ADD COLUMN insurance_type text;
CREATE INDEX idx_insurance_type ON master.insurance_records(insurance_type);
```

**Rationale**: The current schema assumes one insurance record = one relationship. NY's Electrical Permit data provides 3 distinct insurance types per contractor (General Liability, Workers Comp, Disability) with separate carriers and policies. Without a type discriminator, these become indistinguishable rows. Backfill existing WA/OR data: WA records are mostly WC, OR has WC and self-insured. Set `insurance_type = 'WC'` for existing or_wc_employer rows, `'GL'` for or_ccb rows, etc.

#### master.violations -- 3 new columns

```sql
-- Balance due / amount still owed (ECB Violations, OATH Hearings)
ALTER TABLE master.violations ADD COLUMN balance_due numeric;

-- Amount already paid (OATH Hearings)
ALTER TABLE master.violations ADD COLUMN amount_paid numeric;

-- Severity level (ECB Violations: Unknown, Non-Hazardous, Hazardous, Immediately Hazardous)
ALTER TABLE master.violations ADD COLUMN severity text;
```

**Rationale**: NY enforcement data is far richer than OR/WA. `balance_due` is the single most actionable field -- it tells you whether a contractor has outstanding unpaid penalties. `severity` enables filtering hazardous vs. minor violations. These are not niche fields; they apply to 23M+ records.

#### master.projects -- 2 new columns

```sql
-- Estimated job cost (DOB NOW Permits have this; WA/OR project data didn't)
ALTER TABLE master.projects ADD COLUMN estimated_cost numeric;

-- Permit number (distinct from contract_number; NY permits have their own numbering)
ALTER TABLE master.projects ADD COLUMN permit_number text;
CREATE INDEX idx_projects_permit ON master.projects(permit_number);
```

**Rationale**: `estimated_cost` is a high-value field for understanding contractor project scale. `permit_number` is the primary identifier for NY permit data (distinct from contract numbers used in WA/OR public works).

### 3B. NICE-TO-HAVE: Columns That Can Use raw_data Initially

These are valuable but can live in raw_data JSONB until query patterns justify promotion.

#### master.contractors (deferred)

```sql
-- Bonding limit (SBS Certified list only, 11K records)
-- ALTER TABLE master.contractors ADD COLUMN aggregate_bonding_limit numeric;

-- Union signatory flag (SBS Certified list only)
-- ALTER TABLE master.contractors ADD COLUMN is_union_signatory boolean DEFAULT false;

-- DOL Employer Registration Number (Contractor Registry only)
-- ALTER TABLE master.contractors ADD COLUMN dol_employer_reg text;

-- WCB Employer Number (Contractor Registry only)
-- ALTER TABLE master.contractors ADD COLUMN wcb_employer_number text;
```

**Recommendation**: Store in raw_data. Promote to columns only if search/filter queries need them.

#### master.violations (deferred)

```sql
-- Hearing status (OATH: Hearing Complete, Default, etc.)
-- ALTER TABLE master.violations ADD COLUMN hearing_status text;

-- Disposition type (DOB Disciplinary: license_revoked, license_suspended, etc.)
-- ALTER TABLE master.violations ADD COLUMN disposition text;
```

**Recommendation**: `resolution` column can hold disposition. Hearing status goes to raw_data.

### 3C. NEW TABLE: master.debarments

```sql
CREATE TABLE master.debarments (
    id bigserial PRIMARY KEY,
    contractor_id bigint REFERENCES master.contractors(id),
    state char(2),
    entity_name text NOT NULL,
    debarment_start_date date,
    debarment_end_date date,
    reason text,
    source text,
    raw_data jsonb,
    ingested_at timestamptz DEFAULT now()
);

CREATE INDEX idx_debarments_contractor ON master.debarments(contractor_id);
CREATE INDEX idx_debarments_state ON master.debarments(state);
CREATE INDEX idx_debarments_dates ON master.debarments(debarment_start_date, debarment_end_date);
```

**Rationale**: NY has two debarment sources: the Contractor Registry flags (debarment_start/end dates) and the Non-Responsible Entities list (18 records, but authoritative state-level debarment). WA and OR will eventually have their own debarment lists. This is a distinct concept from violations -- debarment is an *outcome* that prevents a contractor from bidding on public work. It deserves its own table with date ranges.

**Row estimate**: ~200 rows initially (NY debarred contractors + Non-Responsible Entities). Will grow as more states added.

### 3D. NEW TABLE: master.certifications

```sql
CREATE TABLE master.certifications (
    id bigserial PRIMARY KEY,
    contractor_id bigint REFERENCES master.contractors(id),
    state char(2),
    certification_type text NOT NULL,  -- 'MBE', 'WBE', 'DBE', 'LBE', 'EBE', 'SDVOB'
    certifying_agency text,            -- 'NYC SBS', 'NY ESD', 'NY DOT'
    ethnicity text,                    -- 'Black American', 'Hispanic American', etc.
    effective_date date,
    expiration_date date,
    naics_codes text[],                -- Array: multiple NAICS per cert
    construction_types text[],         -- Array: types of construction performed
    aggregate_bonding_limit numeric,
    is_union_signatory boolean,
    source text,
    raw_data jsonb,
    ingested_at timestamptz DEFAULT now()
);

CREATE INDEX idx_certifications_contractor ON master.certifications(contractor_id);
CREATE INDEX idx_certifications_type ON master.certifications(certification_type);
CREATE INDEX idx_certifications_state ON master.certifications(state);
```

**Rationale**: M/WBE certification is a first-class concept in NY (11K records from SBS alone) and will be present in other states. It does not fit cleanly into contractors (one contractor can hold multiple certifications) or licenses (it is not a license). This table also accommodates the SBS list's unique fields: bonding limits, union status, construction types performed.

**Alternative**: If a new table feels premature, add `mwbe_status` to contractors and dump the rest in raw_data. The table becomes necessary once we ingest M/WBE data from additional states.

### 3E. CONSIDERATION: master.violation_charges (NOT recommended yet)

The OATH dataset has up to 10 charge codes per ticket. A normalized design would be:

```sql
-- NOT RECOMMENDED YET -- use raw_data jsonb instead
CREATE TABLE master.violation_charges (
    id bigserial PRIMARY KEY,
    violation_id bigint REFERENCES master.violations(id),
    charge_number int,          -- 1-10
    charge_code text,
    charge_section text,
    charge_description text
);
```

**Recommendation**: Do NOT create this table yet. Store charge arrays in violations.raw_data. At 21M OATH rows x up to 10 charges, this table would be 100M+ rows. Only create if we need to search by specific charge code, which is unlikely for contractor profiling.

---

## 4. Dataset-by-Dataset Mapping Summary

### TIER 1: Core Contractor Profiles

#### #1: Contractor Registry (i4jv-zkey) -- 12,604 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Business Name | GREEN | contractors.business_name | Direct |
| DBA Name | RED | contractors.dba_name | **Add column** |
| Business Type | GREEN | contractors.entity_type | Direct |
| Business is MWBE Owned | RED | contractors.mwbe_status | **Add column** |
| Business Officers | GREEN | officers (parse multi-value) | Split + insert |
| Address/City/State/Zip | GREEN | contractors.* | Direct |
| Phone | GREEN | contractors.phone | Direct |
| Certificate Number | GREEN | licenses.license_number | Direct |
| Issued/Expiration Date | GREEN | licenses.issue_date/expiration_date | Direct |
| Status | GREEN | licenses.status | Direct |
| DOL Employer Reg# | YELLOW | contractors.raw_data | JSONB |
| WCB Employer# | YELLOW | contractors.raw_data | JSONB |
| Outstanding Wage Assessments | RED | violations (boolean->row) | Create violation row |
| Has Been Debarred | RED | debarments table | **New table** |
| Debarment Start/End Date | RED | debarments.debarment_start/end_date | **New table** |
| Labor/Tax Law Violations | RED | violations (boolean->row) | Create violation row |
| Safety Violations | RED | violations (boolean->row) | Create violation row |
| Apprenticeship Program | YELLOW | contractors.raw_data | JSONB |
| Has WC Insurance | GREEN | insurance_records (status row) | Direct |
| WC Insurance Exempt | YELLOW | contractors.raw_data | JSONB |

#### #2: DOB License Info (t8hj-ruu2) -- 102,752 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| License Number | GREEN | licenses.license_number | Direct |
| License Type | GREEN | licenses.license_type | Direct (20+ types) |
| License SL No | YELLOW | licenses.raw_data | System ID |
| First/Last Name | GREEN | contractors.owner_name | Direct |
| Business Name | GREEN | contractors.business_name | Direct |
| Address fields | GREEN | contractors.* | Direct |
| Business Email | GREEN | contractors.email | Direct |
| Business Phone | GREEN | contractors.phone | Direct |
| License Status | GREEN | licenses.status | Direct |

#### #3: Active HIC Licenses (acd4-wkax) -- 69,231 rows
All fields GREEN. Standard license + contractor mapping.

#### #5: Active Corporations (n9v6-gdp6) -- 4.1M rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Current Entity Name | GREEN | contractors.business_name | Entity match |
| DOS ID | GREEN | contractors.business_id | Direct |
| Jurisdiction | YELLOW | contractors.raw_data | State of incorporation |
| Entity Formation Date | GREEN | contractors.year_established | Extract year |
| Entity Type Description | GREEN | contractors.entity_type_desc | Direct |
| County | GREEN | contractors.county | Direct |
| Process Address | GREEN | contractors.street/city/state/zip | Registered agent addr |

**WARNING**: 4.1M rows includes ALL NY corporations, not just contractors. Must cross-reference with other datasets to identify construction entities. Do NOT bulk-ingest -- use for entity matching/enrichment only.

#### #6: SBS Certified Business (ci93-uc8s) -- 11,294 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Vendor Formal Name | GREEN | contractors.business_name | Direct |
| DBA | RED | contractors.dba_name | **Add column** |
| Certification | RED | certifications table | **New table** |
| Ethnicity | RED | certifications.ethnicity | **New table** |
| NAICS Code/Title | GREEN | contractors.naics_code | Direct |
| Aggregate Bonding Limit | RED | certifications.aggregate_bonding_limit | **New table** |
| Signatory To Union Contracts | RED | certifications.is_union_signatory | **New table** |
| Types of Construction | RED | certifications.construction_types | **New table** |
| Job Experience (3 entries) | YELLOW | certifications.raw_data | Complex nested |
| Business Description | YELLOW | contractors.raw_data | Free text |

### TIER 2: Projects & Permits

#### #7: DOB NOW Approved Permits (rbx6-tga4) -- 904,760 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Applicant Business Name | GREEN | projects -> contractor match | Via FK |
| Applicant License # | GREEN | projects.raw_data (cross-ref) | JSONB |
| Estimated Job Costs | RED | projects.estimated_cost | **Add column** |
| Job Description | GREEN | projects.contract_name | Direct |
| Work Type | YELLOW | projects.raw_data | JSONB |
| Approved/Issued/Expired Date | GREEN | projects.award_date/start_date | Direct |
| Permit Status | GREEN | projects.raw_data | JSONB |
| Permit Number/Sequence | RED | projects.permit_number | **Add column** |
| BIN | YELLOW | projects.raw_data | NYC-specific |
| Owner Name/Business | YELLOW | projects.raw_data | Property owner |

#### #8: DOB Permit Issuance Legacy (ipu4-2q9a) -- 3.98M rows
Same pattern as #7. Key additions: Permit Type (NB/A1/A2/DM), Filing Status.

#### #9: DOB NOW Build Applications (w9ak-ipjd) -- 871,887 rows
Same pattern. Additional: Work types (plumbing, sprinkler, boiler sub-flags).

#### #11: Electrical Permits (dm9a-ab7w) -- 549,983 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| GL Company/Policy/Expiration | GREEN | insurance_records (type='GL') | Direct + **add insurance_type** |
| WC Company/Policy/Expiration | GREEN | insurance_records (type='WC') | Direct + **add insurance_type** |
| Disability Company/Policy/Exp | GREEN | insurance_records (type='DI') | Direct + **add insurance_type** |
| Firm Name/Number/Address | GREEN | contractors.* | Direct |
| License Number/Type | GREEN | licenses.* | Direct |

This dataset is uniquely valuable -- it provides actual insurance carrier names and policy numbers for GL, WC, and Disability insurance. No WA/OR dataset has this level of insurance detail.

#### #13: Certified Payroll (w2zp-sf2x) -- 4,706 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Contractor Name | GREEN | contractors.business_name | Direct |
| Project Address/City/State | GREEN | projects.project_location/city/state | Direct |
| Contract Amount | GREEN | projects.contract_amount | Direct |
| Job Title / Wage Rate | GREEN | tradespersons.trade/hourly_rate | Direct |

### TIER 3: Violations & Enforcement

#### #16: OATH Hearings (jz4z-kudi) -- 21.4M rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Ticket Number | GREEN | violations.inspection_number | Direct |
| Respondent Name | GREEN | violations -> contractor match | Via FK |
| Violation Date | GREEN | violations.violation_date | Direct |
| Penalty Imposed | GREEN | violations.penalty_amount | Direct |
| Violation Description | GREEN | violations.description | Direct |
| Hearing Result | GREEN | violations.resolution | Direct |
| Balance Due | RED | violations.balance_due | **Add column** |
| Amount Paid | RED | violations.amount_paid | **Add column** |
| Charge Codes 1-10 | YELLOW | violations.raw_data | JSONB (up to 10 per row) |
| Hearing Status | YELLOW | violations.raw_data | JSONB |
| Issuing Agency | YELLOW | violations.raw_data | JSONB (filter DOB) |

**CRITICAL NOTE**: 21.4M rows includes ALL NYC agency violations (DOB, FDNY, DEP, DOT, etc.). For contractor profiling, filter to `Issuing Agency IN ('DOB', 'FDNY')`. Even filtered, this will be millions of rows.

#### #17: DOB ECB Violations (6bgk-3dad) -- 1.8M rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| ECB Violation Number | GREEN | violations.inspection_number | Direct |
| Respondent Name | GREEN | violations -> contractor match | Via FK |
| Violation Description | GREEN | violations.description | Direct |
| Penalty Imposed | GREEN | violations.penalty_amount | Direct |
| Balance Due | RED | violations.balance_due | **Add column** |
| Amount Paid | RED | violations.amount_paid | **Add column** |
| Severity | RED | violations.severity | **Add column** |
| ECB Violation Status | GREEN | violations.resolution | Direct |
| Certification Status | YELLOW | violations.raw_data | JSONB |

#### #21: DOB Disciplinary Actions (ndq3-kuef) -- 2,794 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| License # | GREEN | violations -> license cross-ref | Via raw_data |
| Respondent Name | GREEN | violations -> contractor match | Via FK |
| Company Name | GREEN | violations -> contractor match | Via FK |
| Disposition | GREEN | violations.resolution | Direct |
| Disposition Date | GREEN | violations.resolution_date | Direct |
| Violation Description | GREEN | violations.description | Direct |

#### #25: Non-Responsible Entities (jhxt-dfv6) -- 18 rows
| Field | Color | Target | Action |
|-------|-------|--------|--------|
| Entity Name | RED | debarments.entity_name | **New table** |
| Debarment Start/End | RED | debarments.debarment_start/end_date | **New table** |
| Reason | RED | debarments.reason | **New table** |

### TIER 4: Specialty

#### #27-30: Elevator/Crane/Mold Licenses -- 13K rows
All GREEN. Standard license mapping with license_type = 'Elevator Contractor', 'Crane Operator', 'Mold Contractor', 'Mold Individual'.

---

## 5. Consolidated Schema Changes

### Priority 1: MUST-HAVE (required for core ingestion)

```sql
-- ============================================
-- PRIORITY 1: Must-have columns
-- ============================================

-- 1a. contractors: source tracking (every other table has this)
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS source text;

-- 1b. contractors: DBA name (2 datasets provide it)
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS dba_name text;

-- 1c. contractors: debarment flag (quick boolean check)
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS is_debarred boolean DEFAULT false;

-- 1d. contractors: M/WBE status
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS mwbe_status text;

-- 1e. insurance_records: type discriminator (GL vs WC vs Disability)
ALTER TABLE master.insurance_records ADD COLUMN IF NOT EXISTS insurance_type text;
CREATE INDEX IF NOT EXISTS idx_insurance_type ON master.insurance_records(insurance_type);

-- 1f. violations: financial tracking
ALTER TABLE master.violations ADD COLUMN IF NOT EXISTS balance_due numeric;
ALTER TABLE master.violations ADD COLUMN IF NOT EXISTS amount_paid numeric;
ALTER TABLE master.violations ADD COLUMN IF NOT EXISTS severity text;

-- 1g. projects: permit and cost data
ALTER TABLE master.projects ADD COLUMN IF NOT EXISTS estimated_cost numeric;
ALTER TABLE master.projects ADD COLUMN IF NOT EXISTS permit_number text;
CREATE INDEX IF NOT EXISTS idx_projects_permit ON master.projects(permit_number);
```

**Total: 9 new columns + 2 indexes across 4 tables.**

### Priority 2: NICE-TO-HAVE (enrichment; can defer)

```sql
-- ============================================
-- PRIORITY 2: Nice-to-have columns (defer OK)
-- ============================================

-- 2a. contractors: M/WBE ethnicity detail
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS mwbe_ethnicity text;

-- 2b. violations: hearing status for OATH data
-- (can use resolution column or raw_data instead)
-- ALTER TABLE master.violations ADD COLUMN IF NOT EXISTS hearing_status text;
```

### Priority 3: NEW TABLES

```sql
-- ============================================
-- PRIORITY 3: New tables
-- ============================================

-- 3a. Debarments (cross-state debarment tracking)
CREATE TABLE IF NOT EXISTS master.debarments (
    id bigserial PRIMARY KEY,
    contractor_id bigint REFERENCES master.contractors(id),
    state char(2),
    entity_name text NOT NULL,
    debarment_start_date date,
    debarment_end_date date,
    reason text,
    source text,
    raw_data jsonb,
    ingested_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_debarments_contractor ON master.debarments(contractor_id);
CREATE INDEX IF NOT EXISTS idx_debarments_state ON master.debarments(state);
CREATE INDEX IF NOT EXISTS idx_debarments_active ON master.debarments(debarment_end_date)
    WHERE debarment_end_date IS NULL OR debarment_end_date > CURRENT_DATE;

-- 3b. Certifications (M/WBE, DBE, SDVOB, etc.)
CREATE TABLE IF NOT EXISTS master.certifications (
    id bigserial PRIMARY KEY,
    contractor_id bigint REFERENCES master.contractors(id),
    state char(2),
    certification_type text NOT NULL,
    certifying_agency text,
    ethnicity text,
    effective_date date,
    expiration_date date,
    naics_codes text[],
    construction_types text[],
    aggregate_bonding_limit numeric,
    is_union_signatory boolean,
    source text,
    raw_data jsonb,
    ingested_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_certifications_contractor ON master.certifications(contractor_id);
CREATE INDEX IF NOT EXISTS idx_certifications_type ON master.certifications(certification_type);
CREATE INDEX IF NOT EXISTS idx_certifications_state ON master.certifications(state);
```

---

## 6. What Is Unique to NY (Not Encountered in WA/OR)

| Concept | NY Source | Why It Matters | Schema Impact |
|---------|----------|----------------|---------------|
| **No statewide license** | Structural | Cannot use a single license_number as universal ID | Must support multiple license authorities per contractor |
| **20+ trade license types** | t8hj-ruu2 | GC, Plumber, Welder, Rigger, Fire Suppression, etc. | licenses.license_type values expand massively |
| **Insurance carrier + policy details** | dm9a-ab7w | Actual GL/WC/Disability carrier names | insurance_records.insurance_type column needed |
| **Balance due on violations** | jz4z-kudi, 6bgk-3dad | Outstanding unpaid penalties | violations.balance_due column |
| **Severity levels** | 6bgk-3dad | Hazardous vs non-hazardous | violations.severity column |
| **Debarment with date ranges** | i4jv-zkey, jhxt-dfv6 | Time-bounded prohibition from public work | New debarments table |
| **M/WBE certification** | ci93-uc8s | Minority/Women-owned business status | New certifications table or contractors column |
| **Bonding limits** | ci93-uc8s | Aggregate bonding capacity | certifications.aggregate_bonding_limit |
| **Union signatory status** | ci93-uc8s | Organized labor relationship | certifications.is_union_signatory |
| **Apprenticeship program** | i4jv-zkey | Training program association | contractors.raw_data |
| **Multiple charge codes per violation** | jz4z-kudi | Up to 10 charges per OATH ticket | violations.raw_data (not worth normalizing) |
| **Estimated job cost on permits** | rbx6-tga4 | Dollar value of permitted work | projects.estimated_cost |
| **Disability insurance** | dm9a-ab7w | NY-specific insurance requirement | insurance_records with type='DI' |
| **21M+ violation records** | jz4z-kudi | Scale: 1000x larger than WA/OR combined | Ingestion filtering essential |

---

## 7. Ingestion Risks & Recommendations

### Risk 1: OATH Hearings Scale (21.4M rows)
**Impact**: High. Would dominate the violations table (currently 18K rows).
**Mitigation**: Filter to `Issuing Agency IN ('DOB', 'FDNY', 'DOT')` for construction-related only. Even so, expect 2-5M rows. Consider ingesting DOB ECB Violations (1.8M, pre-filtered) first and deferring full OATH ingest.

### Risk 2: Active Corporations (4.1M rows)
**Impact**: High. Bulk insert would overwhelm contractors table.
**Mitigation**: Do NOT bulk-ingest. Use as enrichment/matching source only. Query on-demand to resolve entity_type, DOS ID, formation date for contractors already identified from other datasets.

### Risk 3: Contractor Identity Resolution
**Impact**: Medium. NY has no UBI equivalent. Same contractor may appear in DOB licenses, HIC licenses, Contractor Registry, and SBS list under slightly different names.
**Mitigation**: Use `business_name_normalized` + trigram matching (idx_contractors_name_trgm already exists). Match on phone/email/address as secondary signals. Store source-specific IDs in raw_data for cross-referencing.

### Risk 4: Permit Data Volume (8.4M rows across 4 datasets)
**Impact**: Medium. Projects table already has 2.4M rows; would triple.
**Mitigation**: Consider ingesting DOB NOW data (905K, cleaner) before legacy BIS data (4M, older). Legacy data may have less structured contractor names.

### Risk 5: Missing contractor_id on Violations
**Impact**: Medium. OATH/ECB violations identify respondents by name + address, not by license number. Many violations will have NULL contractor_id.
**Mitigation**: Accept NULL contractor_id for initial ingest. Run batch matching job post-ingest using name + address fuzzy matching.

---

## 8. Recommended Execution Order

1. **Run Priority 1 ALTER TABLE statements** (9 columns + 2 indexes)
2. **Backfill existing data**: Set `insurance_type` on existing WA/OR insurance_records; set `source` on existing contractors
3. **Ingest Tier 1**: Contractor Registry, DOB Licenses, HIC Licenses, SBS Certified (small datasets, establish contractor base)
4. **Ingest Tier 2**: DOB NOW Permits first (905K, has contractor details), then Electrical Permits (549K, has insurance data)
5. **Create Priority 3 tables** (debarments, certifications) when ingesting SBS and debarment data
6. **Ingest Tier 3**: ECB Violations first (1.8M, pre-filtered to DOB), then OATH if needed
7. **Ingest Tier 4**: Specialty licenses (small, straightforward)
8. **Defer**: Active Corporations (use for enrichment only), full OATH Hearings (filter first)
