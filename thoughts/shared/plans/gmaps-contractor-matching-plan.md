# Matching Strategy: Government Contractor Licenses <-> Google Maps Business Profiles

**Created**: 2026-03-14
**Author**: architect-agent
**Status**: Design Complete — Ready for Implementation

---

## Overview

This document defines a comprehensive strategy for matching 3.6M government contractor license records (PostgreSQL `master.contractors`) against 2.2M Google Maps business profiles (SQLite `google_maps_places`). The goal is to enrich licensed contractors with commercial presence data (ratings, reviews, website, hours, categories) and to identify which Google Maps businesses hold valid trade licenses.

The strategy uses a multi-stage pipeline: deterministic matching first (phone, normalized name+location), then embedding-based fuzzy matching, then optional LLM verification for ambiguous cases. Each match produces a composite confidence score from 0.0 to 1.0.

---

## 1. Data Landscape

### 1.1 Government Contractor Licenses (`master.contractors`)

| Field | Coverage | Notes |
|-------|----------|-------|
| `business_name` | 3,653,100 (100%) | Required field, UPPER CASE in many states |
| `city` | 3,141,724 (86%) | |
| `state` | All rows | 2-char code |
| `zip` | 3,092,821 (85%) | Variable quality (some 9-digit) |
| `phone` | 983,722 (27%) | 10+ digit normalized |
| `email` | 245,777 (7%) | |
| `street` | 2,169,614 (59%) | Mailing address (may be PO Box) |
| `dba_name` | 144,631 (4%) | Critical for sole proprietor matching |
| `website` | 0 (0%) | Not captured from gov sources |
| `entity_type` | 3,052,463 (84%) | Individual, LLC, Corporation, etc. |

**Key challenge**: Only 27% have phone numbers. Phone is our strongest signal but covers barely a quarter of records.

**Entity type distribution** (matching implications):
- Individual: 1,639,895 (45%) -- Personal name, may have no GMaps listing
- Business: 567,166 (16%) -- Generic entity, GMaps name may differ
- LLC: 363,399 (10%) -- Legal name often includes "LLC" suffix
- Corporation: 287,959 (8%) -- Legal name often includes "Inc"/"Corp"
- SoleProprietor: 182,248 (5%) -- DBA name is the matching target
- NULL: 600,637 (16%) -- Unknown entity type

### 1.2 Google Maps Business Profiles (`google_maps_places`)

| Field | Coverage | Notes |
|-------|----------|-------|
| `title` | 2,215,021 (100%) | Trade/DBA name (what customers see) |
| `address` | 2,215,021 (100%) | Full formatted address string |
| `complete_address` | 2,215,021 (100%) | JSON: street, city, postal_code, state, country |
| `phone` | 2,133,072 (96%) | Formatted: "+1 832-768-9994" |
| `website` | 2,196,722 (99%) | |
| `category` | 2,215,021 (100%) | Google category (Electrician, Plumber, etc.) |
| `review_rating` | Most | 1.0-5.0 |
| `review_count` | Most | Integer |
| `latitude/longitude` | Most | Geocoded |
| `place_id` | 2,215,021 (100%) | Google's unique ID |
| `owner` | Partial | Enriched field |

**Key advantage**: 96% have phone numbers. Phone-based matching is feasible for GMaps->Gov direction.

**Geographic coverage** (from address parsing):
- Covers most US states but unevenly. TX, CA, FL, NY, OH, PA, IL, NC, MI, NJ are well-represented.
- 648K records have NULL address (likely service-area businesses with no physical location shown).
- 734K in "OTHER" states not in the top-15 check.

### 1.3 Overlap Analysis

| Dimension | Gov | GMaps | Overlap Potential |
|-----------|-----|-------|-------------------|
| Total Records | 3.6M | 2.2M | |
| With Phone | 984K (27%) | 2.13M (96%) | Phone match feasible for 984K gov records |
| With City | 3.14M (86%) | ~1.57M (parseable) | Good for blocking |
| With State | 3.65M (100%) | ~1.57M (parseable) | Excellent for blocking |
| With Zip | 3.09M (85%) | ~1.57M (parseable) | Good secondary signal |

**Estimated true overlap**: 400K-800K businesses exist in both datasets. Many gov records are individuals without a GMaps presence. Many GMaps businesses don't hold state licenses (handyman services, unlicensed trades).

---

## 2. Data Preparation & Normalization

### 2.1 Phone Normalization

Phone is the single most reliable matching signal. Normalize both sides to 10-digit US format.

```python
import re

def normalize_phone(raw: str) -> str | None:
    """Extract 10-digit US phone number. Returns None if invalid."""
    if not raw:
        return None
    digits = re.sub(r'[^0-9]', '', raw)
    # Strip leading 1 (country code)
    if len(digits) == 11 and digits[0] == '1':
        digits = digits[1:]
    if len(digits) != 10:
        return None
    # Filter out known junk patterns
    if digits[:3] in ('000', '111', '555', '800', '888', '877', '866'):
        return None  # Toll-free or invalid area codes
    return digits
```

**Warning**: Some businesses share phone numbers (franchise main line, answering service). Phone match alone does NOT guarantee same entity. Must confirm with at least one additional signal (name similarity OR address proximity).

### 2.2 Business Name Normalization

Name normalization is critical. Use a multi-level approach.

```python
import re

# Level 1: Basic normalization (for exact matching)
SUFFIX_RE = re.compile(
    r'\b('
    r'INCORPORATED|CORPORATION|COMPANY|LIMITED\s+LIABILITY\s+COMPANY|'
    r'L\.?L\.?C\.?|INC\.?|CORP\.?|CO\.?|LTD\.?|LLC|'
    r'D/?B/?A|P\.?C\.?|PLLC|LLP|LP'
    r')\s*\.?\s*$',
    re.IGNORECASE,
)
TRAILING_PUNCT_RE = re.compile(r'[,.\s\-&]+$')
MULTI_SPACE_RE = re.compile(r'\s{2,}')
LEADING_THE_RE = re.compile(r'^THE\s+', re.IGNORECASE)

# Level 2: Token normalization (for token-based matching)
ABBREVIATIONS = {
    'ASSOC': 'ASSOCIATES', 'ASSOCS': 'ASSOCIATES',
    'BROS': 'BROTHERS', 'BRO': 'BROTHER',
    'CONSTR': 'CONSTRUCTION', 'CONST': 'CONSTRUCTION',
    'CONTRS': 'CONTRACTORS', 'CONTR': 'CONTRACTOR',
    'CTR': 'CENTER',
    'ELEC': 'ELECTRIC', 'ELECTR': 'ELECTRIC',
    'ENTR': 'ENTERPRISES', 'ENTS': 'ENTERPRISES', 'ENT': 'ENTERPRISE',
    'GRP': 'GROUP', 'GP': 'GROUP',
    'INTL': 'INTERNATIONAL', 'INTERNATL': 'INTERNATIONAL',
    'MGMT': 'MANAGEMENT', 'MGT': 'MANAGEMENT',
    'MECH': 'MECHANICAL',
    'MTN': 'MOUNTAIN',
    'NATL': 'NATIONAL',
    'PLBG': 'PLUMBING', 'PLMB': 'PLUMBING', 'PLUMB': 'PLUMBING',
    'SVC': 'SERVICE', 'SVCS': 'SERVICES', 'SERV': 'SERVICE',
    'ST': 'SAINT',  # Context-dependent: street vs saint
    'SYS': 'SYSTEMS',
    'TECH': 'TECHNOLOGY',
    '&': 'AND',
}

def normalize_name_l1(raw: str) -> str:
    """Level 1: Upper, strip suffixes, strip punctuation, collapse whitespace."""
    if not raw:
        return ""
    s = raw.strip().upper()
    for _ in range(3):
        prev = s
        s = SUFFIX_RE.sub('', s)
        s = TRAILING_PUNCT_RE.sub('', s)
        if s == prev:
            break
    s = MULTI_SPACE_RE.sub(' ', s)
    return s.strip()

def normalize_name_l2(raw: str) -> str:
    """Level 2: L1 + expand abbreviations + strip 'THE'."""
    s = normalize_name_l1(raw)
    s = LEADING_THE_RE.sub('', s)
    tokens = s.split()
    expanded = [ABBREVIATIONS.get(t, t) for t in tokens]
    return ' '.join(expanded).strip()

def name_tokens(name: str) -> set:
    """Extract meaningful tokens from a normalized name."""
    stop_words = {'AND', 'OF', 'THE', 'A', 'AN', 'IN', 'AT', 'BY', 'FOR', 'ON'}
    tokens = set(normalize_name_l2(name).split())
    return tokens - stop_words
```

### 2.3 DBA Name Extraction

Government records often contain DBA information embedded in the business name:

```python
DBA_PATTERNS = [
    re.compile(r'\bD/?B/?A\s+(.+)$', re.IGNORECASE),
    re.compile(r'\bT/?A\s+(.+)$', re.IGNORECASE),      # "Trading As"
    re.compile(r'\bAKA\s+(.+)$', re.IGNORECASE),
    re.compile(r'^(.+?)\s*[-/]\s*(.+)$'),                # "JOHN SMITH / SMITH PLUMBING"
]

def extract_dba(business_name: str, dba_field: str | None) -> list[str]:
    """Return list of all name variants to try matching against."""
    names = [business_name]
    if dba_field:
        names.append(dba_field)
    for pat in DBA_PATTERNS:
        m = pat.search(business_name)
        if m:
            names.append(m.group(1).strip())
            # Also add the part before DBA
            pre_dba = business_name[:m.start()].strip().rstrip('-/')
            if pre_dba:
                names.append(pre_dba)
    return [normalize_name_l1(n) for n in names if n.strip()]
```

### 2.4 Address Normalization

```python
def parse_gmaps_address(complete_address_json: str) -> dict:
    """Parse GMaps complete_address JSON into components."""
    import json
    try:
        d = json.loads(complete_address_json)
        state = d.get('state', '')
        # GMaps uses both full name and abbreviation
        state = STATE_ABBREVS.get(state.title(), state.upper()[:2])
        return {
            'street': d.get('street', ''),
            'city': d.get('city', '').upper().strip(),
            'state': state,
            'zip': d.get('postal_code', '').strip()[:5],
        }
    except (json.JSONDecodeError, TypeError):
        return {}

def normalize_zip(raw: str) -> str | None:
    """Extract 5-digit ZIP code."""
    if not raw:
        return None
    digits = re.sub(r'[^0-9]', '', raw.strip())
    return digits[:5] if len(digits) >= 5 else None
```

### 2.5 Pre-Processing Pipeline (One-Time)

Before matching, materialize normalized data into PostgreSQL staging tables:

```sql
-- 1. Import GMaps data from SQLite into PostgreSQL
CREATE SCHEMA IF NOT EXISTS gmaps;

CREATE TABLE gmaps.places (
    place_id        TEXT PRIMARY KEY,
    cid             TEXT,
    title           TEXT NOT NULL,
    title_norm      TEXT,          -- normalize_name_l1(title)
    title_tokens    TEXT[],        -- name_tokens(title)
    category        TEXT,
    street          TEXT,
    city            TEXT,          -- UPPER, parsed from complete_address
    state           CHAR(2),      -- Mapped to 2-char
    zip             CHAR(5),      -- 5-digit only
    phone_norm      CHAR(10),     -- 10-digit normalized
    phone_raw       TEXT,
    website         TEXT,
    review_rating   REAL,
    review_count    INTEGER,
    latitude        REAL,
    longitude       REAL,
    owner           TEXT,
    raw_address     TEXT,         -- Original address string
    complete_address TEXT         -- Original JSON
);

-- Indexes for blocking
CREATE INDEX idx_gp_phone ON gmaps.places(phone_norm) WHERE phone_norm IS NOT NULL;
CREATE INDEX idx_gp_state ON gmaps.places(state);
CREATE INDEX idx_gp_city_state ON gmaps.places(city, state);
CREATE INDEX idx_gp_zip ON gmaps.places(zip) WHERE zip IS NOT NULL;
CREATE INDEX idx_gp_title_trgm ON gmaps.places USING gin(title_norm gin_trgm_ops);

-- 2. Add normalized columns to contractors (or use existing)
ALTER TABLE master.contractors ADD COLUMN IF NOT EXISTS phone_norm CHAR(10);
UPDATE master.contractors SET phone_norm = ... ; -- Python-side normalization

CREATE INDEX idx_mc_phone_norm ON master.contractors(phone_norm) WHERE phone_norm IS NOT NULL;
```

---

## 3. Matching Pipeline

The pipeline runs in 6 stages, each producing matches with decreasing confidence. Later stages only process records not matched in earlier stages.

```
                    ┌─────────────────────────┐
                    │  Stage 0: Phone Match    │  ~200K-400K matches
                    │  (Highest confidence)    │  Phone + name confirm
                    └──────────┬──────────────┘
                               │ unmatched
                    ┌──────────▼──────────────┐
                    │  Stage 1: Exact Name     │  ~50K-100K matches
                    │  Name_L1 + City + State  │
                    └──────────┬──────────────┘
                               │ unmatched
                    ┌──────────▼──────────────┐
                    │  Stage 2: DBA / Alt Name │  ~20K-50K matches
                    │  DBA variants + location │
                    └──────────┬──────────────┘
                               │ unmatched
                    ┌──────────▼──────────────┐
                    │  Stage 3: Embedding      │  ~50K-150K matches
                    │  Name embeddings + city  │
                    └──────────┬──────────────┘
                               │ unmatched
                    ┌──────────▼──────────────┐
                    │  Stage 4: Fuzzy (pg_trgm)│  ~30K-80K matches
                    │  Trigram sim + location   │
                    └──────────┬──────────────┘
                               │ unmatched / ambiguous
                    ┌──────────▼──────────────┐
                    │  Stage 5: LLM Verify     │  Review borderline
                    │  Haiku batch API         │  matches from 3-4
                    └──────────────────────────┘
```

### 3.0 Stage 0: Phone Number Match

**The strongest signal.** A matching 10-digit phone number between a contractor and a GMaps business in the same state is a near-certain match.

```sql
-- Direct phone match, same state
INSERT INTO match_results (contractor_id, place_id, confidence, method, signals)
SELECT c.id, g.place_id,
    CASE
        -- Phone + name similarity > 0.6 = near certain
        WHEN similarity(c.business_name_normalized, g.title_norm) > 0.6 THEN 0.98
        -- Phone + same city = very high
        WHEN c.city = g.city THEN 0.95
        -- Phone match only, same state = high
        ELSE 0.90
    END,
    'phone',
    jsonb_build_object(
        'phone_match', true,
        'name_sim', similarity(c.business_name_normalized, g.title_norm),
        'same_city', c.city = g.city,
        'same_zip', LEFT(c.zip,5) = g.zip
    )
FROM master.contractors c
JOIN gmaps.places g ON c.phone_norm = g.phone_norm AND c.state = g.state
WHERE c.phone_norm IS NOT NULL
  AND g.phone_norm IS NOT NULL;
```

**Edge cases**:
- **Shared phone numbers**: Answering services, franchise main lines. Mitigated by requiring same state AND boosting confidence when name similarity is also high.
- **Ported numbers**: Business changes number, old number goes to new business. Rare but possible. Name similarity check catches this.
- **Multiple GMaps listings, same phone**: Pick the one with highest name similarity. If tie, pick highest review count (most established).

**Expected yield**: 200K-400K matches (27% of contractors have phones, 96% of GMaps have phones, overlap in same state ~25-40% of phone-bearing contractors).

### 3.1 Stage 1: Exact Normalized Name + Location

After phone matching, try exact normalized name match anchored by city+state.

```sql
-- Exact L1-normalized name + same city + same state
INSERT INTO match_results (contractor_id, place_id, confidence, method, signals)
SELECT DISTINCT ON (c.id)
    c.id, g.place_id, 0.92, 'exact_name_city',
    jsonb_build_object(
        'name_norm_match', true,
        'same_city', true,
        'same_zip', LEFT(c.zip,5) = g.zip
    )
FROM master.contractors c
JOIN gmaps.places g
    ON normalize_name_l1(c.business_name) = g.title_norm
    AND UPPER(TRIM(c.city)) = g.city
    AND c.state = g.state
WHERE c.id NOT IN (SELECT contractor_id FROM match_results)
ORDER BY c.id, g.review_count DESC NULLS LAST;
```

**Confidence adjustments**:
- Same ZIP too: +0.03 (0.95)
- Name includes entity suffix match (both LLC, or both Inc): +0.02
- Multiple GMaps matches for same contractor: pick highest review_count, flag for review

### 3.2 Stage 2: DBA / Alternate Name Matching

Critical for sole proprietors where gov has "JOHN A SMITH" but GMaps has "Smith's Handyman Service".

```python
# For each unmatched contractor with a dba_name:
for contractor in unmatched_with_dba:
    name_variants = extract_dba(contractor.business_name, contractor.dba_name)
    for variant in name_variants:
        # Try exact match of variant against GMaps in same city/state
        # If match found, confidence = 0.88
        pass
```

Also try matching the `owner` field from GMaps enrichment against the contractor's personal name (for Individual/SoleProprietor entities):

```sql
-- GMaps owner name matches contractor (for individuals)
SELECT c.id, g.place_id
FROM master.contractors c
JOIN gmaps.places g
    ON UPPER(TRIM(g.owner)) LIKE '%' || UPPER(TRIM(c.business_name)) || '%'
    AND c.state = g.state
    AND UPPER(TRIM(c.city)) = g.city
WHERE c.entity_type IN ('Individual', 'SoleProprietor')
  AND g.owner IS NOT NULL AND g.owner != ''
  AND c.id NOT IN (SELECT contractor_id FROM match_results);
```

### 3.3 Stage 3: Embedding-Based Matching

Use the proven `all-MiniLM-L6-v2` approach from OSHA/NY DOS matching. This handles abbreviations, word order differences, and semantic similarity.

**Blocking strategy**: Match only within same city+state. This reduces the search space from N*M to sum(Ni*Mi) per city, which is orders of magnitude smaller.

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import defaultdict

model = SentenceTransformer('all-MiniLM-L6-v2')

def embedding_match_by_city(contractors, gmaps_places, threshold=0.82):
    """
    Match contractors to GMaps places using embedding similarity,
    grouped by (city, state) for efficiency.
    """
    # Group by (city, state)
    contr_by_loc = defaultdict(list)  # (city, state) -> [(idx, name)]
    gmaps_by_loc = defaultdict(list)  # (city, state) -> [(idx, name)]

    for i, c in enumerate(contractors):
        key = (c.city.upper().strip(), c.state) if c.city else None
        if key:
            contr_by_loc[key].append((i, clean_name_for_embedding(c.business_name)))

    for i, g in enumerate(gmaps_places):
        key = (g.city, g.state) if g.city else None
        if key:
            gmaps_by_loc[key].append((i, clean_name_for_embedding(g.title)))

    matches = []
    for loc_key in contr_by_loc:
        if loc_key not in gmaps_by_loc:
            continue

        c_items = contr_by_loc[loc_key]
        g_items = gmaps_by_loc[loc_key]

        c_names = [item[1] for item in c_items]
        g_names = [item[1] for item in g_items]

        c_embs = model.encode(c_names, normalize_embeddings=True)
        g_embs = model.encode(g_names, normalize_embeddings=True)

        # Cosine similarity (already normalized -> dot product)
        sim_matrix = c_embs @ g_embs.T

        # Best match for each contractor
        best_g_idx = sim_matrix.argmax(axis=1)
        best_sims = sim_matrix[np.arange(len(c_items)), best_g_idx]

        for j, (ci, gi_local, sim) in enumerate(zip(
            range(len(c_items)), best_g_idx, best_sims
        )):
            if sim >= threshold:
                matches.append({
                    'contractor_idx': c_items[ci][0],
                    'gmaps_idx': g_items[gi_local][0],
                    'similarity': float(sim),
                    'method': 'emb+city',
                })

    return matches
```

**Tier structure**:
| Tier | Blocking | Threshold | Confidence Multiplier |
|------|----------|-----------|----------------------|
| 3a | Same city + state | 0.85 | 1.0 |
| 3b | Same zip (5-digit) | 0.82 | 0.95 |
| 3c | Same state only | 0.92 | 0.85 |

**Scale considerations at full dataset**:
- Embedding generation: ~3.6M contractor names + ~2.2M GMaps names = ~5.8M embeddings
- At 512 batch size on CPU: ~45 minutes (one-time cost)
- On GPU (if available): ~5 minutes
- Per-city matrix multiplication: fast (largest cities have ~50K contractors x ~30K GMaps)
- Total matching time: ~10-20 minutes
- Memory: Store embeddings as float16 on disk, memory-map as proven in NY DOS script

### 3.4 Stage 4: Fuzzy Matching (pg_trgm)

For records that didn't match via embeddings (perhaps because the name is very different but shares character patterns), use pg_trgm as a sweep.

```sql
-- Only for records not yet matched
-- Use LATERAL + LIMIT 1 pattern (proven performant)
INSERT INTO match_results (contractor_id, place_id, confidence, method, signals)
SELECT c.id, m.place_id, m.sim * 0.85, 'trgm+city',
    jsonb_build_object('trgm_sim', m.sim, 'anchor', 'city')
FROM (
    SELECT id, business_name_normalized, city, state
    FROM master.contractors
    WHERE id NOT IN (SELECT contractor_id FROM match_results)
      AND city IS NOT NULL
) c,
LATERAL (
    SELECT g.place_id, similarity(c.business_name_normalized, g.title_norm) AS sim
    FROM gmaps.places g
    WHERE g.title_norm OPERATOR(public.%) c.business_name_normalized
      AND g.city = UPPER(TRIM(c.city))
      AND g.state = c.state
    ORDER BY similarity(g.title_norm, c.business_name_normalized) DESC
    LIMIT 1
) m
WHERE m.sim >= 0.55;
```

**Warning**: At full scale (millions of unmatched on each side), pg_trgm LATERAL queries can be slow even with GIN indexes. Run per-state to keep working sets manageable.

### 3.5 Stage 5: LLM Verification (Optional)

For matches in the 0.55-0.80 confidence range ("maybe" zone), use Claude Haiku batch API for verification.

```python
VERIFY_PROMPT = """Are these the same business?

Business A (Government License):
  Name: "{gov_name}"
  DBA: "{gov_dba}"
  Address: "{gov_street}, {gov_city}, {gov_state} {gov_zip}"
  Phone: {gov_phone}
  Type: {gov_entity_type}

Business B (Google Maps):
  Name: "{gmaps_title}"
  Address: "{gmaps_address}"
  Phone: {gmaps_phone}
  Category: {gmaps_category}
  Reviews: {gmaps_review_count} ({gmaps_rating} stars)

Answer YES, NO, or MAYBE with brief reasoning (1 sentence)."""
```

**Cost estimate**:
- Expect 50K-100K ambiguous pairs
- Haiku batch API: ~$0.25/1M input tokens, ~$1.25/1M output tokens (50% batch discount)
- ~200 tokens per pair input, ~30 tokens output
- 100K pairs: ~$7 total (very affordable)

**LLM confidence mapping**:
- YES -> confidence = max(existing_score, 0.85)
- MAYBE -> confidence = existing_score (no change, flag for human)
- NO -> confidence = 0.0 (discard match)

---

## 4. Composite Confidence Scoring Model

Each match gets a confidence score from 0.0 to 1.0 based on multiple signals:

### 4.1 Signal Weights

| Signal | Weight | Range | Notes |
|--------|--------|-------|-------|
| Phone match (10-digit) | 0.40 | 0 or 1 | Strongest single signal |
| Name similarity (embedding) | 0.25 | 0.0-1.0 | Handles abbreviations |
| Name similarity (trigram) | 0.20 | 0.0-1.0 | Character-level fallback |
| City match | 0.10 | 0 or 1 | Required for most stages |
| ZIP match | 0.05 | 0 or 1 | Secondary location signal |
| Entity type compatible | 0.05 | 0 or 1 | LLC->business GMaps |
| Street address match | 0.10 | 0.0-1.0 | When available |
| DBA name match | 0.10 | 0 or 1 | When DBA in gov record |

*Note: Weights are used for multi-signal scoring when no single stage is definitive. Stage-based confidence (above) takes precedence when a stage makes the match.*

### 4.2 Composite Score Formula

For matches that combine signals from multiple stages:

```python
def composite_confidence(signals: dict) -> float:
    """
    Compute composite confidence from matched signals.
    Uses a Bayesian-inspired approach: each signal multiplicatively
    increases confidence.
    """
    base = 0.10  # Prior: 10% chance any two businesses are the same

    # Phone match is extremely strong evidence
    if signals.get('phone_match'):
        base = 0.85  # Jump to 85% with phone alone

    # Name similarity (take best of embedding and trigram)
    name_sim = max(
        signals.get('embedding_sim', 0),
        signals.get('trigram_sim', 0)
    )
    if name_sim >= 0.95:
        base = max(base, base + (1 - base) * 0.6)
    elif name_sim >= 0.85:
        base = max(base, base + (1 - base) * 0.4)
    elif name_sim >= 0.70:
        base = max(base, base + (1 - base) * 0.2)

    # Location signals
    if signals.get('same_city') and signals.get('same_state'):
        base = base + (1 - base) * 0.15
    if signals.get('same_zip'):
        base = base + (1 - base) * 0.10
    if signals.get('street_sim', 0) > 0.7:
        base = base + (1 - base) * 0.15

    # DBA match bonus
    if signals.get('dba_match'):
        base = base + (1 - base) * 0.20

    # Entity type compatibility bonus (small)
    if signals.get('entity_compatible'):
        base = base + (1 - base) * 0.05

    return min(base, 0.99)
```

### 4.3 Confidence Tiers & Actions

| Tier | Score Range | Action | Label |
|------|------------|--------|-------|
| **Auto-accept** | >= 0.90 | Write to match table, link records | HIGH |
| **Likely match** | 0.75 - 0.89 | Accept with review flag | MEDIUM |
| **Ambiguous** | 0.55 - 0.74 | Send to LLM verification (Stage 5) | LOW |
| **Unlikely** | 0.35 - 0.54 | Store as candidate, do not link | CANDIDATE |
| **Reject** | < 0.35 | Discard | REJECT |

---

## 5. Blocking Strategies (Avoiding N-Squared)

The naive approach (compare every contractor to every GMaps business) is 3.6M x 2.2M = 7.9 trillion comparisons. This is obviously infeasible. Blocking reduces the search space dramatically.

### 5.1 Blocking Hierarchy

```
Level 1: Phone number (exact 10-digit match)
    → Only compares records sharing a phone number
    → Reduction: 7.9T → ~2M comparisons

Level 2: State
    → All stages after phone use state as minimum block
    → Reduction: 7.9T → ~160M comparisons (varies by state)

Level 3: City + State
    → Primary blocking key for name matching
    → Reduction: 7.9T → ~5M comparisons total

Level 4: ZIP code (5-digit)
    → Secondary blocking key for name matching
    → Reduction: 7.9T → ~3M comparisons total
```

### 5.2 Processing Order

Process states sequentially to manage memory:

```python
STATES_BY_SIZE = [
    'TX', 'CA', 'FL', 'NY', 'CT', 'MI', 'CO', 'NC', 'IL',
    'NJ', 'WA', 'MN', 'TN', 'KY', 'OR', 'VA', 'MD', 'ID',
    'PA', 'DE', 'VT', ...
]

for state in STATES_BY_SIZE:
    # 1. Load contractors for this state
    # 2. Load GMaps places for this state
    # 3. Run stages 0-4
    # 4. Write results
    # 5. Free memory
```

### 5.3 Index Strategy

```sql
-- On gmaps.places:
CREATE INDEX idx_gp_phone ON gmaps.places(phone_norm) WHERE phone_norm IS NOT NULL;
CREATE INDEX idx_gp_city_state ON gmaps.places(city, state);
CREATE INDEX idx_gp_zip ON gmaps.places(zip) WHERE zip IS NOT NULL;
CREATE INDEX idx_gp_title_trgm ON gmaps.places USING gin(title_norm gin_trgm_ops);

-- On master.contractors (some already exist):
CREATE INDEX idx_mc_phone_norm ON master.contractors(phone_norm) WHERE phone_norm IS NOT NULL;
-- idx_contractors_city_state already exists
-- idx_contractors_zip already exists
-- idx_contractors_name_trgm already exists (on business_name_normalized -- BEWARE bug, see below)
```

**IMPORTANT**: The existing `business_name_normalized` column has a known bug that strips "CO" from "CONSTRUCTION" (documented in MATCHING-APPROACHES.md). Do NOT rely on this column. Use Python-side normalization or create a new `business_name_clean` column.

---

## 6. Results Schema

### 6.1 Match Table

```sql
CREATE TABLE master.gmaps_matches (
    id              SERIAL PRIMARY KEY,
    contractor_id   BIGINT NOT NULL REFERENCES master.contractors(id),
    place_id        TEXT NOT NULL,    -- GMaps place_id
    confidence      REAL NOT NULL,    -- 0.0-1.0
    confidence_tier TEXT NOT NULL,    -- 'HIGH', 'MEDIUM', 'LOW', 'CANDIDATE'
    method          TEXT NOT NULL,    -- 'phone', 'exact_name_city', 'dba', 'emb+city', 'trgm+city', etc.
    signals         JSONB,           -- Detailed signal breakdown
    verified        BOOLEAN DEFAULT NULL, -- NULL=unreviewed, TRUE=confirmed, FALSE=rejected
    verified_by     TEXT,            -- 'auto', 'llm', 'human'
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_gmaps_match UNIQUE (contractor_id, place_id)
);

CREATE INDEX idx_gm_contractor ON master.gmaps_matches(contractor_id);
CREATE INDEX idx_gm_place ON master.gmaps_matches(place_id);
CREATE INDEX idx_gm_confidence ON master.gmaps_matches(confidence DESC);
CREATE INDEX idx_gm_tier ON master.gmaps_matches(confidence_tier);
CREATE INDEX idx_gm_unverified ON master.gmaps_matches(verified) WHERE verified IS NULL;
```

### 6.2 Enrichment View

Once matches are confirmed, create a denormalized view:

```sql
CREATE VIEW master.contractor_profiles AS
SELECT
    c.*,
    g.title AS gmaps_name,
    g.review_rating AS gmaps_rating,
    g.review_count AS gmaps_reviews,
    g.website AS gmaps_website,
    g.category AS gmaps_category,
    g.latitude AS gmaps_lat,
    g.longitude AS gmaps_lng,
    g.phone_raw AS gmaps_phone,
    m.confidence AS match_confidence,
    m.method AS match_method
FROM master.contractors c
JOIN master.gmaps_matches m ON m.contractor_id = c.id AND m.verified != false
JOIN gmaps.places g ON g.place_id = m.place_id;
```

---

## 7. Implementation Plan

### Phase 1: Data Staging (Day 1)

**Files to create:**
- `scripts/matching/import_gmaps_to_pg.py` — Import SQLite GMaps data into PostgreSQL `gmaps.places`
- `scripts/matching/normalize_phones.py` — Add `phone_norm` column to contractors, populate
- `scripts/matching/create_match_schema.sql` — DDL for `gmaps` schema and match tables

**Steps:**
1. Create `gmaps` schema in PostgreSQL
2. Import 2.2M Google Maps records from SQLite to PostgreSQL
3. Parse `complete_address` JSON into normalized columns during import
4. Normalize phone numbers on both sides
5. Create all indexes
6. Validate data quality (spot-check 100 random records)

**Acceptance criteria:**
- [ ] `gmaps.places` has 2.2M rows with parsed city/state/zip
- [ ] Phone normalization applied to both tables
- [ ] All indexes created and ANALYZEd
- [ ] Spot-check passes (10 random phone numbers manually verified)

**Estimated effort:** 3-4 hours

### Phase 2: Phone Matching (Day 1-2)

**Files to create:**
- `scripts/matching/match_stage0_phone.py` — Phone number matching

**Steps:**
1. Join on `phone_norm` + `state`
2. For each phone match, compute name similarity as confirmation signal
3. Handle one-to-many (one phone, multiple GMaps listings): pick best
4. Handle many-to-one (multiple contractors, one GMaps listing): match all if names are similar
5. Write results to `master.gmaps_matches`
6. Report match rate and confidence distribution

**Acceptance criteria:**
- [ ] 200K+ phone matches found
- [ ] False positive rate < 2% on 100-record sample review
- [ ] One-to-many and many-to-one cases handled

**Estimated effort:** 2-3 hours

### Phase 3: Exact Name Matching (Day 2)

**Files to create:**
- `scripts/matching/match_stage1_exact.py` — Normalized exact name + location matching

**Steps:**
1. For unmatched contractors, try L1-normalized name + city + state
2. Try L2-normalized name (with abbreviation expansion) + city + state
3. For records with DBA names, try DBA variants
4. Write results

**Acceptance criteria:**
- [ ] Additional 50K+ matches beyond phone
- [ ] DBA matching catches sole proprietor cases

**Estimated effort:** 2-3 hours

### Phase 4: Embedding Matching (Day 2-3)

**Files to create:**
- `scripts/matching/match_stage3_embeddings.py` — Embedding-based fuzzy matching
- `scripts/matching/generate_embeddings.py` — One-time embedding generation script

**Steps:**
1. Generate embeddings for all contractor names (batch, save to disk as .npy)
2. Generate embeddings for all GMaps titles (batch, save to disk as .npy)
3. Group by (city, state), compute cosine similarity matrices
4. Match at threshold 0.85 (city-blocked), 0.82 (zip-blocked), 0.92 (state-blocked)
5. Write results

**Acceptance criteria:**
- [ ] Embeddings generated and saved (reusable)
- [ ] 50K+ additional matches
- [ ] Runtime under 30 minutes total

**Estimated effort:** 4-5 hours

### Phase 5: pg_trgm Sweep (Day 3)

**Files to create:**
- `scripts/matching/match_stage4_trgm.py` — Trigram fuzzy matching sweep

**Steps:**
1. For still-unmatched contractors with city, run pg_trgm LATERAL against GMaps
2. Process per-state to manage performance
3. Write results

**Acceptance criteria:**
- [ ] Additional 30K+ matches
- [ ] Runtime manageable (under 2 hours)

**Estimated effort:** 2-3 hours

### Phase 6: LLM Verification (Day 3-4)

**Files to create:**
- `scripts/matching/verify_llm_batch.py` — Batch LLM verification of ambiguous matches

**Steps:**
1. Extract matches in 0.55-0.75 confidence range
2. Format into verification prompts
3. Send to Claude Haiku batch API
4. Parse responses, update confidence scores
5. Report acceptance/rejection rates

**Acceptance criteria:**
- [ ] All ambiguous matches reviewed
- [ ] Cost under $20
- [ ] LLM agrees with high-confidence matches (sanity check)

**Estimated effort:** 3-4 hours

### Phase 7: Analysis & Reporting (Day 4)

**Files to create:**
- `scripts/matching/match_report.py` — Generate match statistics and quality report
- `scripts/matching/export_enriched.py` — Export enriched contractor profiles

**Steps:**
1. Generate match rate report by state, entity type, category
2. Sample-based precision audit (random 500 matches across tiers)
3. Create the enrichment view
4. Export enriched data for downstream use

**Acceptance criteria:**
- [ ] Overall match rate documented
- [ ] Precision validated at each tier
- [ ] Enrichment view working

**Estimated effort:** 2-3 hours

---

## 8. Expected Results

### 8.1 Match Rate Projections

| Stage | Expected Matches | Cumulative | Confidence Range |
|-------|-----------------|------------|-----------------|
| 0: Phone | 250,000-400,000 | 250K-400K | 0.85-0.98 |
| 1: Exact name+city | 50,000-100,000 | 300K-500K | 0.88-0.95 |
| 2: DBA variants | 20,000-50,000 | 320K-550K | 0.82-0.92 |
| 3: Embeddings | 50,000-150,000 | 370K-700K | 0.70-0.90 |
| 4: pg_trgm | 30,000-80,000 | 400K-780K | 0.55-0.80 |
| 5: LLM verify | Reclassify ~50K | 400K-780K | Adjusted |
| **Total** | **400K-780K** | | |

**Overall match rate**: 11-21% of contractors, 18-35% of GMaps businesses.

This is realistic because:
- 45% of contractors are Individuals (many have no GMaps listing)
- Many contractors are in states with limited GMaps coverage
- Not all construction businesses are on Google Maps
- Not all Google Maps businesses hold government licenses

### 8.2 Error Rate Projections

| Confidence Tier | Expected Precision | Expected Volume |
|-----------------|-------------------|-----------------|
| HIGH (>= 0.90) | > 99% | 300K-500K |
| MEDIUM (0.75-0.89) | 95-98% | 50K-150K |
| LOW (0.55-0.74) | 80-90% (pre-LLM) | 50K-130K |
| CANDIDATE (0.35-0.54) | 50-70% | Store but don't link |

---

## 9. Edge Cases & Mitigations

### 9.1 Common Name Problem

**Problem**: "Smith Electric" or "ABC Construction" exists in every major city. Name alone is worthless.

**Mitigation**: NEVER match on name alone. Always require at least one location signal (city, zip, or phone area code). The blocking strategy inherently prevents cross-city false positives.

**Additional safeguard**: For names with high frequency (appearing in 50+ cities), require TWO location signals (city + zip, or city + phone match).

```python
# Detect high-frequency names
HIGH_FREQ_NAMES = set()  # Names appearing in 50+ cities
# For these: require city + zip match, or city + phone match
```

### 9.2 Multi-Location Businesses

**Problem**: A company like "Comfort Systems USA" has one license but 50 GMaps locations.

**Mitigation**: Allow many-to-one matching (multiple GMaps -> one contractor). Store all matches. For enrichment, use the GMaps listing closest to the contractor's registered address (by lat/lng distance).

### 9.3 Franchise vs Independent

**Problem**: "ServiceMaster" franchises are independently licensed but share a brand name on GMaps.

**Mitigation**: Require city-level match for franchise-like names. Phone match resolves ambiguity (each franchise has its own phone).

### 9.4 Individual Name Mismatches

**Problem**: Gov has "JOHN ALBERT SMITH" (Individual), GMaps has "Smith's Plumbing Service".

**Mitigation**:
1. Check DBA name field first
2. Check if contractor last name appears in GMaps title
3. Check if the `owner` field in GMaps matches the contractor name
4. For Individual/SoleProprietor entities, apply a special matching function:

```python
def individual_name_in_business(person_name: str, business_name: str) -> float:
    """Check if parts of a person's name appear in a business name."""
    parts = person_name.upper().split()
    if len(parts) < 2:
        return 0.0
    last_name = parts[-1]
    # "SMITH" in "SMITH'S PLUMBING SERVICE"
    if last_name in business_name.upper().replace("'S", "").replace("'", ""):
        return 0.5  # Partial signal, combine with location
    return 0.0
```

### 9.5 Address: PO Box vs Physical Location

**Problem**: Gov records often have PO Box or home address. GMaps has storefront address.

**Mitigation**: Don't rely on street address matching as a primary signal. Use it only as a confidence booster when it matches. City + ZIP matching works even when street addresses differ.

### 9.6 Stale Data

**Problem**: Contractor may have moved, changed name, or closed since the license was issued.

**Mitigation**: Use `year_established` and license dates to detect very old records. Flag matches where the contractor license is expired (if we have expiration dates). The GMaps `review_count` and recency can indicate if a business is still active.

### 9.7 Non-English Names

**Problem**: Some contractor names include non-ASCII characters or are in Spanish.

**Mitigation**: The `all-MiniLM-L6-v2` model handles multilingual text reasonably well. Name normalization should preserve non-ASCII characters. The embedding approach is more robust than character-level trigrams for these cases.

---

## 10. Technology Stack & Libraries

### 10.1 Already Installed (Confirmed)

| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 15+ | Primary database |
| `pg_trgm` | 1.6 | Trigram similarity |
| `fuzzystrmatch` | 1.2 | Levenshtein distance |
| `pgvector` | 0.8.2 | Vector storage/search |
| `btree_gin` | 1.3 | GIN index support |
| Python 3.12 | 3.12 | Script runtime |
| sentence-transformers | Installed in FEDERAL/.venv | Embedding model |

### 10.2 Python Dependencies

```
# Core (already available)
psycopg2-binary
numpy
sentence-transformers  # all-MiniLM-L6-v2

# Additional recommended
tqdm                   # Progress bars
pandas                 # Data analysis/reporting (optional)
```

### 10.3 Database Extensions Usage

| Extension | Use In This Pipeline |
|-----------|---------------------|
| `pg_trgm` | Stage 4 (fuzzy trigram matching), GIN indexes on name columns |
| `fuzzystrmatch` | `levenshtein()` for address comparison, `soundex()` for phonetic name matching |
| `pgvector` | Optional: store embeddings in DB for reuse. Current approach uses NumPy (faster) |

---

## 11. Performance Benchmarks (Projected)

Based on our proven OSHA and NY DOS matching performance:

| Operation | Scale | Expected Time |
|-----------|-------|--------------|
| Import GMaps to PG | 2.2M rows | 5-10 min |
| Phone normalization | 3.6M + 2.2M | 2-3 min |
| Phone matching (Stage 0) | ~2M join | < 1 min |
| Exact name matching (Stage 1) | ~3M join | 2-5 min |
| DBA matching (Stage 2) | ~500K candidates | 5-10 min |
| Embedding generation | 5.8M names | 30-60 min (CPU) |
| Embedding matching (Stage 3) | Per city groups | 15-30 min |
| pg_trgm sweep (Stage 4) | Per state | 30-60 min |
| LLM verification (Stage 5) | ~50-100K pairs | 20-40 min (API latency) |
| **Total** | | **~2-4 hours** |

Memory requirements:
- Embeddings: 5.8M x 384 dims x 2 bytes (float16) = ~4.5 GB on disk
- Per-city matching: well within RAM (largest city groups < 100K records)
- Memory-mapped embeddings (proven in NY DOS script) keep RAM usage manageable

---

## 12. Monitoring & Quality Assurance

### 12.1 Match Quality Metrics

Track these metrics per run:

```python
QUALITY_METRICS = {
    'total_contractors': 0,
    'total_gmaps': 0,
    'matched_contractors': 0,
    'matched_gmaps': 0,
    'match_rate_contractors': 0.0,
    'match_rate_gmaps': 0.0,
    'confidence_distribution': {
        'high': 0,      # >= 0.90
        'medium': 0,    # 0.75-0.89
        'low': 0,       # 0.55-0.74
        'candidate': 0, # 0.35-0.54
    },
    'method_distribution': {
        'phone': 0,
        'exact_name': 0,
        'dba': 0,
        'embedding': 0,
        'trgm': 0,
    },
    'one_to_many_cases': 0,  # One contractor, multiple GMaps
    'many_to_one_cases': 0,  # Multiple contractors, one GMaps
}
```

### 12.2 Precision Audit Protocol

After each run, sample and manually verify:

| Tier | Sample Size | Expected Precision |
|------|-------------|-------------------|
| HIGH (>= 0.90) | 100 random | > 98% |
| MEDIUM (0.75-0.89) | 100 random | > 93% |
| LOW (0.55-0.74) | 200 random | > 80% |
| CANDIDATE (0.35-0.54) | 100 random | > 50% |

Audit script should present pairs in a simple format for quick human review:

```
Match #1 (confidence=0.92, method=phone)
  GOV:  ABC CONSTRUCTION LLC | 123 Main St, Houston, TX 77001 | (832) 555-1234
  GMAP: ABC Construction     | 125 Main St, Houston, TX 77001 | (832) 555-1234
  [CORRECT / INCORRECT / UNSURE]
```

### 12.3 Ongoing Monitoring

As new contractors are ingested or new GMaps data is scraped:

1. Run incremental matching on new records only (track `created_at`)
2. Compare match rates to baseline (flag if significantly different)
3. Re-verify a sample of existing matches periodically (businesses close/change names)

---

## 13. File Structure

```
scripts/matching/
    README.md                     # This strategy summary
    import_gmaps_to_pg.py         # Phase 1: Import GMaps to PostgreSQL
    normalize_phones.py           # Phase 1: Phone normalization
    create_match_schema.sql       # Phase 1: DDL
    match_stage0_phone.py         # Phase 2: Phone matching
    match_stage1_exact.py         # Phase 3: Exact name matching
    match_stage2_dba.py           # Phase 3: DBA/alternate name matching
    generate_embeddings.py        # Phase 4: One-time embedding generation
    match_stage3_embeddings.py    # Phase 4: Embedding matching
    match_stage4_trgm.py          # Phase 5: pg_trgm sweep
    verify_llm_batch.py           # Phase 6: LLM verification
    match_report.py               # Phase 7: Analysis and reporting
    utils/
        normalize.py              # Shared normalization functions
        scoring.py                # Confidence scoring functions
        blocking.py               # Blocking key generation
```

---

## 14. Open Questions

- [ ] **GMaps geographic completeness**: The current GMaps scrape appears concentrated in specific metro areas. What is the actual state-by-state coverage? Should we expand the scrape before matching?
- [ ] **Website matching**: Contractors have 0% website coverage in gov data, but 99% in GMaps. Could we reverse-lookup contractor names on their GMaps websites to boost matching? (Expensive but high signal.)
- [ ] **One contractor, multiple licenses**: Some contractors appear multiple times in `master.contractors` (different license types, different states). Should we dedup contractors first?
- [ ] **GMaps category -> trade license mapping**: Could we filter GMaps candidates by category (e.g., only match "Electrician" GMaps listings against electrical license holders)? Requires mapping Google categories to license types.
- [ ] **Incremental matching strategy**: How often will we re-run? Daily (as new data arrives) or batch (monthly)?
- [ ] **Privacy considerations**: Are there any restrictions on storing matched PII (linking gov records to commercial profiles)?

---

## 15. Lessons Learned from Prior Matching Work

From `MATCHING-APPROACHES.md` and the existing OSHA/NY DOS scripts:

1. **Embeddings are 170x faster than pg_trgm** for matching at scale. Use embeddings as the primary fuzzy approach, pg_trgm as a sweep.
2. **NumPy grouped cosine similarity beats pgvector LATERAL queries**. HNSW indexes don't work well with WHERE clause filtering. Do matching in Python.
3. **Memory-map embeddings to disk** (`np.save` + `mmap_mode='r'`). This is essential at scale (proven in NY DOS with 4.1M records).
4. **Don't use `business_name_normalized`** column — it has a bug that strips "CO" from "CONSTRUCTION".
5. **Dedup names before matching** to avoid redundant computation (OSHA: 88K unique vs 101K total).
6. **3-tier cascade** (exact -> fuzzy+city -> fuzzy+zip) is proven and effective.
7. **`OPERATOR(public.%)` syntax** is required for pg_trgm with psycopg2 (escaping issue with `%`).
8. **Create indexes AFTER populating temp tables** for speed.
9. **float16 embeddings** are sufficient for cosine similarity and save 50% memory.
10. **LLM verification at $5-15** for 50-100K pairs is cost-effective and catches false positives that automated methods miss.

---

## Appendix A: State Name to Abbreviation Mapping

The GMaps `complete_address` JSON uses full state names ("Texas") in some records and abbreviations ("TX") in others. Normalize to 2-char during import.

## Appendix B: Google Maps Category to Trade Mapping (Partial)

| Google Maps Category | Likely License Types |
|---------------------|---------------------|
| Electrician | Electrical |
| Plumber | Plumbing |
| HVAC Contractor | HVAC, Mechanical |
| Roofing Contractor | Roofing, General |
| General Contractor | General, Building |
| Painter | Painting (often unlicensed) |
| Landscaper | Landscaping (often unlicensed) |
| Home Builder | General, Residential Building |

This mapping could be used to reduce false positives (don't match an electrician to a plumbing license) but requires careful handling of multi-trade businesses.
