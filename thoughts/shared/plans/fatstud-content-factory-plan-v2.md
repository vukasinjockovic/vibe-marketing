# FatStud Content Factory -- Plan v2

**Created:** 2026-03-07
**Updated:** 2026-03-07
**Author:** architect-agent (Opus) + human input
**Purpose:** Comprehensive plan for building a construction content factory that produces 20,000+ pages for fatstud.businesspress.dev. Incorporates web archive mining, Yelp review scraping, programmatic city/brand pages, and Q&A page generation.

---

## Table of Contents

1. [Situation Summary](#1-situation-summary)
2. [Keyword Groups Inventory](#2-keyword-groups-inventory)
3. [Content Scraping Strategy](#3-content-scraping-strategy)
4. [Yelp Review Mining Strategy](#4-yelp-review-mining-strategy)
5. [Web Archive Mining Strategy](#5-web-archive-mining-strategy)
6. [Vibe-Marketing Platform Capabilities](#6-vibe-marketing-platform-capabilities)
7. [Audience Research Plan](#7-audience-research-plan)
8. [Content Cross-Referencing Strategy](#8-content-cross-referencing-strategy)
9. [Page Types & Templates](#9-page-types--templates)
10. [Category Taxonomy](#10-category-taxonomy)
11. [Programmatic City Pages](#11-programmatic-city-pages)
12. [Blog Post Generation Pipeline](#12-blog-post-generation-pipeline)
13. [Q&A Page Generation Pipeline](#13-qa-page-generation-pipeline)
14. [Technical Implementation](#14-technical-implementation)
15. [Scale Estimates](#15-scale-estimates)
16. [Phase Ordering & Rollout](#16-phase-ordering--rollout)
17. [Resolved Decision Points](#17-resolved-decision-points)
18. [Risk Register](#18-risk-register)

---

## 1. Situation Summary

### What Exists

- **Site:** fatstud.businesspress.dev (Laravel 12 + BusinessPress)
- **Infrastructure:** Homepage, calculator CPT (custom post type), provider CPT, taxonomy/categories
- **Keyword research:** 17,967 keywords from Google Keyword Planner across 15 categories (40.6M monthly searches/mo)
- **Autocomplete research:** 5,976 additional unique suggestions from Google Autocomplete API
- **Competitor analysis:** 104 unique calculators identified across OmniCalculator, InchCalculator, and Blocklayer
- **Calculator comparison file:** `/var/www/vibe-marketing/rust/construction-calculators/calculator-comparison-analysis.md`

### What We're Building (v2 Scope)

A **content factory** that produces 20,000+ pages:

| Page Type | Target Count | Source |
|-----------|------------:|--------|
| Topic blog posts | 3,000-5,000 | Expanded keyword targeting + long-tail variations |
| Q&A pages | 3,000-5,000 | Mined from Reddit, Quora, Yelp, YouTube comments |
| City/location pages | 5,000-10,000 | `[service] in [city]` × 500+ US cities |
| Brand pages | 500-1,000 | `[brand] [product]`, `[brand] vs [brand]`, `[brand] in [city]` |
| **Total** | **11,500-21,000** | |

### Revenue Opportunity (Updated for 20K+ pages)

| Scenario | Monthly Traffic | Monthly Revenue | Annual Revenue |
|----------|---------------:|----------------:|---------------:|
| Conservative (0.5% capture, $25 RPM) | 203,236 | $5,080 | $60,969 |
| Moderate (3% capture, $35 RPM) | 1,219,418 | $42,679 | $512,154 |
| Optimistic (8% capture, $50 RPM) | 3,251,780 | $162,589 | $1,951,069 |
| Aggressive (15% capture, $50 RPM) | 6,097,087 | $304,854 | $3,658,254 |

With 20K+ pages, even a conservative capture rate generates meaningful revenue.

---

## 2. Keyword Groups Inventory

### All 15 Category Groups

| # | Category | Unique KWs | Monthly Vol | Top Keywords (50K+) | Blog Post Potential |
|:-:|----------|----------:|------------:|--------------------:|--------------------:|
| 1 | **Square Footage & Conversions** | 4,158 | 25,861,350 | sq ft calculator, acre to sq ft, how to calculate square footage | 200-400 |
| 2 | **Paint & Flooring** | 3,370 | 1,502,700 | paint calculator, tile calculator, carpet installation cost | 250-500 |
| 3 | **Concrete** | 2,834 | 6,702,400 | concrete calculator, concrete slab, concrete block, concrete cost | 200-400 |
| 4 | **Landscaping** | 2,562 | 1,020,750 | gravel calculator, mulch calculator, topsoil calculator | 200-350 |
| 5 | **Roofing** | 1,922 | 1,640,300 | roofing calculator, roof pitch calculator | 150-300 |
| 6 | **Electrical** | 1,753 | 731,650 | conduit fill calculator, voltage drop calculator | 120-250 |
| 7 | **Deck & Fence** | 1,333 | 747,350 | deck calculator, fence calculator | 100-200 |
| 8 | **Misc Construction** | 1,009 | 575,050 | stair calculator | 80-150 |
| 9 | **Brick & Masonry** | 988 | 626,650 | retaining wall | 80-150 |
| 10 | **Lumber & Board Feet** | 638 | 592,800 | board feet calculator, linear feet | 60-120 |
| 11 | **Drywall & Insulation** | 527 | 567,650 | drywall calculator, drywall installation cost | 50-100 |
| 12 | **Patio & Outdoor** | 459 | 89,850 | - | 40-80 |
| 13 | **Roofing Cost Extended** | 410 | 136,350 | cost-specific roofing | 30-60 |
| 14 | **Flooring Extended** | 209 | 106,100 | cost-specific flooring | 20-40 |
| 15 | **Concrete Cost Extended** | 125 | 69,250 | concrete pad cost | 15-30 |
| | **TOTALS** | **~17,967** | **~40.6M** | | **1,395-3,130** |

### Key Files

All in `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/`:

- `MASTER-SUMMARY.md` — master keyword summary
- `autocomplete-suggestions.txt` — 5,976 unique suggestions
- `category-data.json` — structured autocomplete data
- `*-latest-analysis.md` — per-category analysis files
- `categories/` — raw CSVs per category

### Blog-Mappable Keyword Patterns

| Pattern | Example Keywords | Template | Est. Posts |
|---------|-----------------|----------|----------:|
| "how to calculate [X]" | how to calculate square footage | How-To Guide | 300+ |
| "how much [X] do I need" | how much concrete do I need | Material Guide | 200+ |
| "[X] cost per [unit]" | concrete cost per yard | Cost Breakdown | 150+ |
| "[X] vs [Y]" | concrete vs asphalt driveway | Comparison | 100+ |
| "[brand] [calculator]" | quikrete calculator | Brand Guide | 50+ |
| "[project] calculator" | driveway calculator | Project Planning | 150+ |
| "[X] installation guide" | tile installation | Step-by-Step | 100+ |
| "best [X] for [Y]" | best mulch for flower beds | Recommendation | 80+ |
| "[X] problems/issues" | concrete cracking | Troubleshooting | 60+ |
| "[code/standard] [topic]" | NEC conduit fill | Code Reference | 50+ |
| "[X] in [city]" | concrete contractors in Austin | City Page | 5,000+ |
| "[brand] vs [brand]" | Quikrete vs Sakrete | Brand Comparison | 100+ |
| "[question word] [topic]" | why does concrete crack | Q&A Page | 3,000+ |

---

## 3. Content Scraping Strategy

### 3.1 Available Scraping Infrastructure

| Tool | Status | Use For |
|------|--------|---------|
| **Crawl4AI** | Running at `localhost:11235` v0.5.1-d1 | Bulk blog article scraping |
| **Firecrawl MCP** | Available in `.mcp.json` | Single-page structured extraction |
| **YouTube MCP** | Available + `youtube_research.py` script | Video transcript extraction |
| **Playwright MCP** | Available in `.mcp.json` | JS-heavy sites |
| **Scrapling** | v0.4.1 at `/home/vuk/.local/bin/scrapling` | Yelp scraping (anti-detection) |
| **DataImpulse Proxy** | `gw.dataimpulse.com:823` ($9 credit) | Residential proxy for Yelp |
| **Reddit MCP** | Available in `.mcp.json` | Subreddit scraping |
| **Brave Search MCP** | Available in `.mcp.json` | URL discovery |

### 3.2 Sources to Scrape

**Full source inventory:** See [CONTENT-SOURCES-MASTER.md](/var/www/vibe-marketing/knowledge/construction/CONTENT-SOURCES-MASTER.md) for the complete list of 172 sources with priority ratings (★★★/★★/★), scrapability assessments, and estimated article counts.

**Summary:**

| Category | ★★★ Sources | Total Sources | Est. Articles |
|----------|:----------:|:------------:|:-------------:|
| Construction/DIY Blogs | 20 | 55 | 85,000+ |
| Cost Guide Sites | 6 | 11 | 8,000+ |
| YouTube Channels | 15 | 45 | 8,000+ videos |
| Forums / Q&A Sites | 6 | 17 | 2M+ threads |
| Trade Publications | 5 | 15 | 25,000+ |
| Manufacturer Blogs | 4 | 12 | 2,000+ |
| Building Code / Reference | 2 | 5 | 15,000+ |
| Yelp Reviews | 1 | 1 | 200K+ reviews |
| Reddit | 6 | 12 | Massive |
| Retail How-To | 2 | 3 | 5,500+ |
| **TOTALS** | **67** | **176** | **350,000+** |

**Key additions over v1:**
- inspectapedia.com (10K+ free reference articles — single richest source)
- diy.stackexchange.com (200K+ structured Q&A with API)
- 6 cost guide sites (fixr, homeguide, costhelper, homewyse, inchcalculator, remodelingcalculator)
- 6 major forums (ContractorTalk, Mike Holt, Terry Love, HVAC-Talk, DIY Chatroom, DoItYourself.com)
- 35 additional YouTube channels
- Yelp review mining via archives + Scrapling

### 3.3 Data Storage Plan

```
/var/www/vibe-marketing/knowledge/construction/
├── blogs/
│   ├── this-old-house/
│   │   ├── _index.json
│   │   └── articles/
│   │       └── {slug}.md
│   ├── family-handyman/
│   ├── bob-vila/
│   └── ...
├── youtube/
│   ├── essential-craftsman/
│   │   ├── _index.json
│   │   └── transcripts/
│   │       └── {video_id}-{slug}.md
│   └── ...
├── reddit/
│   ├── home-improvement/
│   │   ├── _index.json
│   │   └── threads/
│   │       └── {post_id}-{slug}.md
│   └── ...
├── yelp/
│   ├── _index.json
│   ├── reviews/
│   │   └── {category}/
│   │       └── {business_slug}.json
│   └── voice-data/
│       └── construction-voice.json
├── quora/
│   ├── topics/
│   └── voice-data/
├── manufacturer-guides/
│   ├── quikrete/
│   ├── gaf/
│   └── ...
├── web-archives/
│   ├── url-inventory.db          # SQLite: all discovered URLs
│   └── domain-inventories/
│       ├── thisoldhouse.txt
│       └── ...
└── _scraped-index.json
```

### 3.4 Scrape Data Format

Each scraped article stored as markdown with YAML frontmatter:

```yaml
---
source: "this-old-house"
sourceUrl: "https://www.thisoldhouse.com/..."
title: "How to Pour a Concrete Slab"
author: "Tom Silva"
datePublished: "2025-06-15"
dateScraped: "2026-03-08"
contentHash: "sha256:abc123..."
categories: ["concrete", "diy", "slab"]
keywords: ["concrete slab", "pour concrete"]
wordCount: 2500
matchedKeywordGroups: ["concrete", "concrete-cost-extended"]
---

[Extracted article text in markdown format]
```

---

## 4. Yelp Review Mining Strategy

### 4.1 Overview

Yelp reviews contain invaluable data for construction content:

| Data Type | Use in Content Factory |
|-----------|----------------------|
| **Customer language** | Real phrases people use when describing projects |
| **Pricing mentions** | Regional pricing data ("paid $4,500 for 600 sqft patio in Austin") |
| **Pain points** | What went wrong, complaints, warnings |
| **Satisfaction signals** | What customers value most in contractors |
| **Question patterns** | "Is this normal?" type questions → Q&A pages |
| **Local context** | City-specific construction challenges (weather, soil, permits) |

### 4.2 Two-Phase Approach

#### Phase A: Web Archive Mining (FREE)

Use the web archive mining script (Section 5) to discover all `yelp.com/biz/*` URLs related to construction.

**Filter criteria:**
- Year >= 2020 (recent data only)
- URL contains construction-related categories:
  - `/biz/` paths with: contractor, roofing, concrete, electrician, plumber, landscaping, carpenter, mason, drywall, flooring, painter, fencing, deck, handyman
- Extract: business names, categories, cities, review counts

**Expected output:** 50,000-200,000 unique business URLs across US cities.

#### Phase B: Scrapling + DataImpulse (TARGETED)

For high-value business pages discovered in Phase A:

**Tool:** Scrapling v0.4.1 (anti-detection Python scraper)
**Proxy:** DataImpulse residential rotating proxy (`gw.dataimpulse.com:823`)
**Budget:** $9 remaining (~1,800 page loads at ~$0.005/request with media disabled)

**Configuration:**

```python
from scrapling import Fetcher

fetcher = Fetcher(
    proxy="http://638dd3cd818880913596:39651982daaac3de@gw.dataimpulse.com:823",
    disable_resources=True,  # No images/CSS/JS = cheaper + faster
    timeout=15
)
```

**Scraping targets (prioritized by value):**
1. **Business category pages** — `/search?find_desc=concrete+contractor&find_loc=[city]`
2. **Top-reviewed businesses** — sort by review count, scrape top 5 per city per category
3. **Review text** — extract review text, rating, date, response text

**Rate limiting:**
- 1 request per 5 seconds
- Rotate user agents
- No more than 50 pages per sitting
- Spread across multiple days to conserve budget

**Data extraction per review:**

```json
{
  "businessName": "Mike's Concrete Works",
  "city": "Austin",
  "state": "TX",
  "category": "concrete",
  "rating": 5,
  "reviewText": "Mike repoured our entire 800 sqft driveway for $6,200. He used 4-inch slabs with rebar...",
  "reviewDate": "2025-08-15",
  "responseText": "Thanks! We always recommend 4-inch for driveways...",
  "extractedPricing": { "project": "driveway", "sqft": 800, "cost": 6200, "perSqft": 7.75 },
  "extractedKeywords": ["driveway", "concrete", "rebar", "4-inch slab"]
}
```

### 4.3 Yelp Data Usage

| Content Type | How Yelp Data Is Used |
|-------------|----------------------|
| **Blog posts** | Real pricing data, customer quotes (anonymized), regional cost variations |
| **Q&A pages** | Questions extracted from reviews ("Is it normal for concrete to crack?") |
| **City pages** | Local contractor density, average ratings, price ranges per city |
| **Cost guides** | Real-world pricing data aggregated by region |

---

## 5. Web Archive Mining Strategy

### 5.1 Architecture

Based on the proven OnlyFans username scraper at `/var/www/onlyfansapi/scripts/discover-onlyfans-usernames.sh`, adapted for construction content discovery.

**Script location:** `/var/www/vibe-marketing/scripts/scraping/discover-construction-urls.sh`

**Data sources:**
1. **GAU** (go tool) — queries Wayback Machine, Common Crawl, OTX, URLScan simultaneously
2. **Wayback CDX API** — paginated, parallel, resumable
3. **Common Crawl Index API** — 121+ crawl snapshots

**Output:** SQLite database of all construction-related URLs discovered.

### 5.2 Target Domains

```bash
# Tier 1: Construction blogs (HIGH priority)
DOMAINS_BLOGS=(
    "thisoldhouse.com"
    "familyhandyman.com"
    "bobvila.com"
    "finehomebuilding.com"
    "concretenetwork.com"
    "thespruce.com"
    "jlconline.com"
    "protoolreviews.com"
    "builderonline.com"
    "hunker.com"
)

# Tier 2: Manufacturer sites
DOMAINS_MANUFACTURERS=(
    "quikrete.com"
    "sakrete.com"
    "gaf.com"
    "owenscorning.com"
    "certainteed.com"
    "trex.com"
    "jameshardie.com"
    "strongtie.com"
)

# Tier 3: Yelp (for review mining)
DOMAINS_YELP=(
    "yelp.com"
)

# Tier 4: Q&A / Forum sites
DOMAINS_QA=(
    "diy.stackexchange.com"
    "forums.finehomebuilding.com"
    "contractortalk.com"
    "electriciantalk.com"
)
```

### 5.3 SQLite Schema

```sql
CREATE TABLE urls (
    url TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    path TEXT NOT NULL,
    category TEXT,              -- matched construction category
    content_type TEXT,          -- article, review, qa, guide, calculator
    year_archived INTEGER,     -- year from archive timestamp
    scrape_status TEXT DEFAULT 'pending', -- pending, scraped, failed, skipped
    scraped_at TEXT,
    content_hash TEXT
);

CREATE INDEX idx_domain ON urls(domain);
CREATE INDEX idx_category ON urls(category);
CREATE INDEX idx_scrape_status ON urls(scrape_status);
CREATE INDEX idx_year ON urls(year_archived);
```

### 5.4 URL Classification Rules

The bash script classifies URLs into categories during extraction:

```bash
# URL path patterns → category mapping
classify_url() {
    local url="$1"
    case "$url" in
        *concrete*|*cement*|*mortar*)       echo "concrete" ;;
        *roof*|*shingle*|*gutter*)          echo "roofing" ;;
        *electri*|*wiring*|*conduit*)       echo "electrical" ;;
        *paint*|*flooring*|*tile*|*carpet*)  echo "paint-flooring" ;;
        *landscape*|*mulch*|*gravel*)       echo "landscaping" ;;
        *deck*|*fence*|*patio*)             echo "deck-fence-patio" ;;
        *drywall*|*insulation*)             echo "drywall-insulation" ;;
        *lumber*|*wood*|*board*)            echo "lumber" ;;
        *brick*|*masonry*|*retaining*)      echo "brick-masonry" ;;
        *stair*|*ramp*|*foundation*)        echo "misc-construction" ;;
        *plumb*|*pipe*|*drain*)             echo "plumbing" ;;
        *calculator*|*calc*|*estimat*)      echo "calculator" ;;
        *cost*|*price*|*budget*)            echo "cost-guide" ;;
        *)                                  echo "uncategorized" ;;
    esac
}
```

### 5.5 Year Filtering

Only collect URLs archived from 2020 onwards to ensure content relevance:

```bash
# Wayback CDX: filter by timestamp
curl "http://web.archive.org/cdx/search/cdx?url=${domain}/*&output=text&fl=original,timestamp&from=20200101"

# GAU: --from flag
gau "${domain}" --from 202001

# Common Crawl: filter by crawl year (CC-MAIN-2020-* onwards)
```

### 5.6 Expected Yield

| Domain | Est. URLs (2020+) | Article URLs | Useful for |
|--------|------------------:|:------------:|------------|
| thisoldhouse.com | 50,000-100,000 | 5,000-10,000 | How-to guides |
| familyhandyman.com | 40,000-80,000 | 4,000-8,000 | DIY tutorials |
| bobvila.com | 30,000-60,000 | 3,000-6,000 | Home improvement |
| concretenetwork.com | 10,000-20,000 | 2,000-4,000 | Concrete deep-dives |
| thespruce.com | 50,000-100,000 | 5,000-10,000 | Consumer guides |
| yelp.com/biz/* | 1,000,000+ | 50,000-200,000 | Construction businesses |
| diy.stackexchange.com | 100,000+ | 30,000-50,000 | Q&A content |
| **Total** | **~1.3M+** | **~100K+** | Massive URL inventory |

We won't scrape all 100K+ URLs. The URL inventory is used to:
1. Identify the most valuable pages (by category + keyword matching)
2. Prioritize scraping order
3. Discover content we didn't know existed

---

## 6. Vibe-Marketing Platform Capabilities

### 6.1 Relevant Agent Skills

| Skill | Purpose in Content Factory |
|-------|---------------------------|
| **audience-research-procedures** | Generate focus group profiles for construction audiences |
| **content-writing-procedures** | Generate blog posts using L1-L5 skill layer model |
| **content-review-procedures** | Quality-score articles (8 dimensions, auto-approve at 7+) |
| **humanizer** | Remove AI writing patterns (24 pattern categories) |
| **youtube-research** | Extract transcripts and comments |
| **quora-research** | Mine Quora for audience voice data |
| **google-suggest-research** | Expand seed keywords via Google Autocomplete |
| **programmatic-seo** | Template-based page generation at scale |
| **schema-markup** | JSON-LD structured data for rich results |
| **content-strategy** | Plan content topics, clusters, calendar |
| **seo-audit** | Audit SEO on published pages |
| **copywriting** | Direct-response copy for CTAs |
| **writing-clearly-and-concisely** | Strunk's rules, applied DURING generation |
| **mbook-schwarz-awareness** | L1: Match content to reader awareness stage |
| **mbook-ogilvy-advertising** | L4: Factual, research-heavy writing style |

### 6.2 Content Pipeline

```
backlog → researched → briefed → drafted → reviewed → humanized → completed
```

### 6.3 MCP Servers

| Server | Tools | Use |
|--------|-------|-----|
| `crawl4ai` | All crawl/scrape | Bulk blog scraping |
| `firecrawl` | crawl, scrape, search, map, extract | Structured extraction |
| `playwright` | All browser automation | JS-heavy sites |
| `brave-search` | Web search | URL discovery |
| `perplexity` | AI search | Research |
| `youtube` | Video download/transcript | YouTube extraction |
| `reddit` | Reddit API | Subreddit scraping |
| `dataforseo` | SEO data | SERP analysis |

---

## 7. Audience Research Plan

### 7.1 Audience Segments

| ID | Segment | Primary Keyword Groups | Awareness Stage |
|:--:|---------|----------------------|:---------------:|
| A1 | DIY Homeowner -- First Project | Sq footage, paint, tile, mulch | Problem Aware |
| A2 | DIY Homeowner -- Experienced | Concrete, deck, fence, drywall | Solution Aware |
| A3 | Licensed Electrician | Electrical (all) | Most Aware |
| A4 | General Contractor / Estimator | All cost calcs | Most Aware |
| A5 | Roofing Contractor | Roofing (all) | Most Aware |
| A6 | Landscaper / Hardscaper | Landscaping, brick/masonry, patio | Solution Aware |
| A7 | Carpenter / Framer | Lumber, deck, stairs | Most Aware |
| A8 | Real Estate Investor / Flipper | All cost calculators | Product Aware |
| A9 | Property Manager | Drywall, paint, flooring | Solution Aware |
| A10 | Architecture / Engineering Student | Sq footage, conversions | Problem Aware |
| A11 | Concrete Professional | Concrete (all) | Most Aware |
| A12 | DIY Homeowner -- Bathroom/Kitchen | Tile, flooring, paint, drywall | Solution Aware |

### 7.2 Focus Group Generation

- Target: 12-15 focus groups in Convex
- Use Reddit + Quora + Yelp scraped data as input for voice patterns
- Run `vibe-audience-researcher` for each segment

---

## 8. Content Cross-Referencing Strategy

### 8.1 Cross-Reference Matrix

```
Scraped Content    Keyword Groups     Audience Segments    Calculators
      │                 │                    │                  │
      └─── Match ───────┤                    │                  │
                        ├── Assign priority  │                  │
                        ├── Match audience ──┘                  │
                        └── Link to calc ───────────────────────┘
```

### 8.2 Prioritization Formula

```
Priority Score = (Monthly Search Volume / 1000)
               × (Average CPC / $1.00)
               × Content Availability Factor  (1.5 rich / 1.0 some / 0.5 none)
               × Audience Match Factor         (1.5 top / 1.0 mid / 0.7 niche)
```

### 8.3 Internal Linking Strategy

Every blog post links to:
1. Its matching calculator
2. 2-3 related blog posts (same category)
3. 1-2 blog posts from adjacent categories
4. Provider directory (where relevant)
5. City page for the topic (if applicable)

Every city page links to:
1. Parent topic blog post
2. Other city pages in same state
3. Relevant calculators
4. Provider directory for that city

---

## 9. Page Types & Templates

### 9.1 Page Type Summary

| Type | Template | Count Target | Word Count | Schema |
|------|----------|:------------:|:----------:|--------|
| How-To Guide | A | 800-1,200 | 1,500-2,500 | Article, HowTo, FAQ |
| Cost Breakdown | B | 500-800 | 1,500-2,000 | Article, FAQ |
| Comparison | C | 300-500 | 1,200-1,800 | Article, FAQ |
| FAQ/Tips | D | 600-1,000 | 1,000-1,500 | Article, FAQ |
| Q&A Page | E | 3,000-5,000 | 300-800 | QAPage |
| City Page | F | 5,000-10,000 | 500-1,000 | LocalBusiness, FAQ |
| Brand Guide | G | 300-500 | 800-1,500 | Article, Product |
| Brand Comparison | H | 100-200 | 1,000-1,500 | Article, FAQ |

### 9.2 Template A: How-To Guide

```markdown
---
title: "How to [Action] [Topic]: Step-by-Step Guide [Year]"
targetKeyword: "[primary keyword]"
categories: ["[parent]", "[child]"]
wordCount: 1500-2500
---

## Quick Answer
[1-2 sentence direct answer]

## What You'll Need
- [Materials with quantities]
- [Tools]

## Step-by-Step Instructions
### Step 1: [Action]
[Detailed instructions]

## Common Mistakes to Avoid
1. [Mistake] -- [Why] -- [Fix]

## Calculator
[Link to matching calculator]

## FAQ
### [Long-tail keyword question 1]
[Answer]
```

### 9.3 Template B: Cost Breakdown

```markdown
---
title: "[Project] Cost Calculator & Price Guide [Year]"
targetKeyword: "[cost keyword]"
---

## Average Cost
| Level | Cost |
|-------|-----:|
| Low | $X |
| Average | $Y |
| High | $Z |

## Cost Factors
### Materials | ### Labor | ### Project Size

## Cost Calculator
[Link to calculator]

## How to Save Money
## When to Hire a Pro vs DIY
## FAQ
```

### 9.4 Template E: Q&A Page (NEW)

```markdown
---
title: "[Question]?"
targetKeyword: "[question keyword]"
categories: ["[parent]", "[child]"]
wordCount: 300-800
sourceType: "qa"
---

## [Question]?

[Direct, authoritative answer in 2-3 paragraphs]

## Key Points
- [Point 1]
- [Point 2]
- [Point 3]

## Related Questions
- [Link to related Q&A 1]
- [Link to related Q&A 2]
- [Link to related Q&A 3]

## Calculator
[Link to relevant calculator if applicable]
```

### 9.5 Template F: City Page (NEW)

```markdown
---
title: "[Service] in [City], [State] -- Cost, Contractors & Guide [Year]"
targetKeyword: "[service] in [city]"
categories: ["[parent]", "[child]"]
city: "[City]"
state: "[State]"
stateCode: "[ST]"
population: [N]
wordCount: 500-1000
sourceType: "city"
---

## [Service] in [City], [State]

[1-2 paragraph overview of this service in this city, mentioning local factors]

## Average Cost in [City]
| Level | Cost |
|-------|-----:|
| Low | $X |
| Average | $Y |
| High | $Z |

[Regional cost note based on Yelp/scraped pricing data]

## Local Considerations
- [Climate/weather factor]
- [Soil/terrain factor if relevant]
- [Local building code notes]
- [Seasonal timing recommendations]

## Calculator
[Link to relevant calculator]

## Related Guides
- [How-to blog post link]
- [Cost guide link]

## Other Cities in [State]
- [City page link 1]
- [City page link 2]
```

### 9.6 Template G: Brand Guide (NEW)

```markdown
---
title: "[Brand] [Product] Guide: Features, Calculator & Reviews [Year]"
targetKeyword: "[brand] [product]"
---

## [Brand] [Product] Overview
[Brand-specific product details]

## Key Specifications
| Spec | Value |
|------|-------|

## How to Use [Brand] [Product]
## Calculator
[Brand-specific calculator or general calculator with brand presets]

## [Brand] vs Alternatives
## FAQ
```

---

## 10. Category Taxonomy

### 10.1 Two-Level Hierarchy

```
Parent Category → Child Categories (create as taxonomy terms in BusinessPress)
```

| Parent | Children |
|--------|----------|
| **Concrete & Masonry** | Concrete Slabs, Concrete Driveways, Stamped Concrete, Concrete Blocks, Concrete Footings, Concrete Repair, Mortar & Grout, Retaining Walls, Brick Work |
| **Roofing** | Shingle Roofing, Metal Roofing, Flat Roofing, Roof Repair, Roof Cost, Gutters & Drainage, Roof Pitch & Measurement |
| **Flooring** | Tile Flooring, Hardwood Flooring, Laminate & Vinyl, Carpet, Flooring Cost, Floor Prep & Leveling |
| **Paint & Finishing** | Interior Paint, Exterior Paint, Staining, Paint Calculator, Color Selection |
| **Electrical** | Wiring & Circuits, Conduit & Raceways, Electrical Panels, Lighting, NEC Code Reference, Voltage & Amperage |
| **Plumbing** | Pipe Sizing, Drain Systems, Water Heaters, Fixtures, Plumbing Code |
| **Landscaping** | Mulch & Soil, Gravel & Stone, Lawn & Turf, Irrigation, Retaining Walls, Landscape Design |
| **Deck & Outdoor** | Wood Decks, Composite Decks, Patios, Pergolas & Gazebos, Outdoor Kitchens |
| **Fencing** | Wood Fencing, Vinyl Fencing, Chain Link, Metal Fencing, Fence Cost |
| **Drywall & Insulation** | Drywall Installation, Drywall Repair, Insulation Types, R-Value Guide, Soundproofing |
| **Lumber & Framing** | Board Feet, Dimensional Lumber, Framing, Structural Design, Span Tables |
| **Stairs & Railings** | Stair Calculation, Building Code Stairs, Railing Types, Spiral Stairs |
| **Measurements & Conversions** | Square Footage, Cubic Yards, Linear Feet, Area Conversions, Volume Conversions |
| **Cost Guides** | Material Costs, Labor Costs, Project Budgeting, Contractor Pricing, DIY vs Pro |
| **Tools & Equipment** | Power Tools, Hand Tools, Safety Equipment, Tool Reviews |

### 10.2 Implementation

Create taxonomy terms in BusinessPress:

```bash
# Example: create via BusinessPress API or direct DB
# Parent term
INSERT INTO categories (name, slug, parent_id) VALUES ('Concrete & Masonry', 'concrete-masonry', NULL);

# Child terms
INSERT INTO categories (name, slug, parent_id) VALUES ('Concrete Slabs', 'concrete-slabs', {parent_id});
INSERT INTO categories (name, slug, parent_id) VALUES ('Concrete Driveways', 'concrete-driveways', {parent_id});
```

Posts can belong to multiple categories (many-to-many via `post_categories` pivot table).

---

## 11. Programmatic City Pages

### 11.1 City Data Source

Use a comprehensive US cities list (500+ cities with population 50K+).

**Data needed per city:**
- City name
- State name and code
- Population
- Latitude/longitude (for "near me" SEO)
- Metro area name
- Climate zone (affects construction advice)

### 11.2 Service Types for City Pages

Each city gets pages for these service types (where keyword volume exists):

| Service Type | Est. Monthly Searches | Pages per City |
|-------------|----------------------:|:--------------:|
| Concrete contractors | 500-5,000 | 1 |
| Roofing contractors | 1,000-10,000 | 1 |
| Electricians | 500-5,000 | 1 |
| Plumbers | 500-5,000 | 1 |
| Landscaping | 500-5,000 | 1 |
| Fencing contractors | 200-2,000 | 1 |
| Deck builders | 200-2,000 | 1 |
| Painters | 500-5,000 | 1 |
| Drywall contractors | 100-1,000 | 1 |
| Flooring installers | 200-2,000 | 1 |
| Handyman services | 500-5,000 | 1 |
| General contractors | 500-5,000 | 1 |
| **Total per city** | | **12** |

### 11.3 Scale Calculation

| Cities | Pages per City | Total City Pages |
|:------:|:--------------:|:----------------:|
| 500 | 12 | 6,000 |
| 600 | 12 | 7,200 |
| 750 | 12 | 9,000 |
| 1,000 | 12 | 12,000 |

**Decision: All US cities with 50K+ population (~500-600 cities) = ~6,000-7,200 city pages.**

### 11.4 City Page Content Generation

City pages are **programmatic** — template-driven with city-specific variables:

```
Variables per city page:
- {city}: "Austin"
- {state}: "Texas"
- {stateCode}: "TX"
- {service}: "Concrete Contractors"
- {avgCost}: from Yelp data or national average adjusted by regional multiplier
- {climate}: "Hot and humid summers, mild winters"
- {localNote}: generated based on climate zone + soil type
- {relatedCities}: 3-5 other cities in same state
```

Content is NOT purely formulaic — each page gets a 1-2 paragraph unique intro generated by the content writer, plus programmatic data sections.

---

## 12. Blog Post Generation Pipeline

### 12.1 Workflow per Blog Post

```
1. SELECT keyword + template
   └── From prioritized keyword list

2. GATHER source material
   └── Scraped blog content from knowledge/construction/
   └── YouTube transcripts
   └── Reddit/Quora/Yelp voice data
   └── Focus group data for matched audience segment

3. GENERATE content brief
   └── Title, target keyword, word count
   └── Source materials (NOT to copy)
   └── Awareness stage
   └── Calculator + related post links

4. WRITE draft
   └── vibe-content-writer
   └── L1 Schwartz awareness matching
   └── L4 Ogilvy factual style
   └── L5 clear/concise rules
   └── Include specific measurements, code refs, brand names

5. REVIEW
   └── vibe-content-reviewer
   └── 8-dimension scoring (target 7+)
   └── Auto-approve at 7+

6. HUMANIZE
   └── vibe-humanizer
   └── Remove AI patterns
   └── Add specificity, personality

7. SEO OPTIMIZE
   └── Schema markup
   └── Meta description
   └── Internal links
   └── Category assignment

8. STORE
   └── Markdown files in projects/fatstud/campaigns/
```

### 12.2 How Scraped Content Gets Used

**CRITICAL: We do NOT copy scraped content.** It serves as a knowledge base:

| Data Type | Usage |
|-----------|-------|
| Blog articles | Extract facts, measurements, techniques. Rewrite in our voice. |
| YouTube transcripts | Extract step-by-step procedures, expert tips, real measurements. |
| Reddit threads | Extract audience language, common questions, real problems. |
| Yelp reviews | Extract pricing data, customer language, regional variations. |
| Quora answers | Extract expert perspectives, question framing. |
| Manufacturer guides | Extract specs, coverage rates. Cite as source. |

### 12.3 Quality Standards

Each article scored on 8 dimensions (from content-review-procedures):

1. Awareness Match (20%)
2. CTA Clarity (15%)
3. Proof Density (15%)
4. Persuasion Application (10%)
5. Voice Consistency (10%)
6. AI Pattern Detection (15%)
7. SEO & Readability (10%)
8. Focus Group Alignment (5%)

Target: 7.0+ for auto-approval.

---

## 13. Q&A Page Generation Pipeline

### 13.1 Question Sources

| Source | Question Extraction Method | Est. Questions |
|--------|---------------------------|:--------------:|
| Reddit threads | Titles + top-level comments that are questions | 2,000-3,000 |
| Quora | Direct question titles | 500-1,000 |
| Yelp reviews | "Is this normal?" patterns, questions in reviews | 500-1,000 |
| YouTube comments | Question comments on construction videos | 500-1,000 |
| Google Autocomplete | "how", "what", "why", "when", "can" patterns | 2,000-3,000 |
| Keyword research | Question-pattern keywords from Planner data | 1,000-2,000 |
| **Total candidates** | | **6,500-11,000** |

### 13.2 Deduplication

Questions are deduplicated by semantic similarity:
- "How much concrete for a 10x10 slab" ≈ "How many bags of concrete for 10x10"
- Keep the version with higher search volume
- Target: 3,000-5,000 unique Q&A pages after dedup

### 13.3 Q&A Generation Workflow

```
1. EXTRACT questions from all sources
2. DEDUPLICATE by semantic similarity
3. MATCH to keyword groups + categories
4. PRIORITIZE by search volume
5. GENERATE answer (300-800 words)
   └── Factual, authoritative tone
   └── Include specific numbers
   └── Link to calculator
   └── Link to related Q&A
6. ADD schema markup (QAPage)
7. STORE in projects/fatstud/campaigns/qa-content/
```

---

## 14. Technical Implementation

### 14.1 Script Architecture

```
/var/www/vibe-marketing/scripts/scraping/
├── discover-construction-urls.sh    # Bash: web archive URL discovery (SQLite)
├── discover-yelp-urls.sh            # Bash: web archive Yelp URL discovery
├── scrape-construction-content.py   # Python: Crawl4AI bulk scraping
├── scrape-yelp-reviews.py           # Python: Scrapling + DataImpulse
├── scrape-youtube.py                # Python: youtube_research.py wrapper
├── scrape-reddit.py                 # Python: Reddit MCP wrapper
├── scrape-quora.py                  # Python: quora_research.py wrapper
├── extract-questions.py             # Python: question extraction from all sources
├── classify-content.py              # Python: keyword matching + categorization
├── generate-city-data.py            # Python: US cities seed data
└── config/
    ├── domains.txt                  # Target domains for archive mining
    ├── categories.json              # Category definitions
    └── cities.json                  # US cities data
```

### 14.2 Crawl4AI Configuration

```python
# Rate limiting
RATE_LIMITS = {
    "default": 3,          # seconds between requests per domain
    "yelp.com": 10,        # extra cautious with Yelp
    "*.gov": 5,            # government sites
}

# CSS selectors for article extraction
SELECTORS = {
    "thisoldhouse.com": "article .article-body",
    "familyhandyman.com": ".article-body",
    "bobvila.com": ".article-content",
    "concretenetwork.com": ".entry-content",
    "thespruce.com": ".article-body",
    "default": "article, .article-body, .entry-content, main"
}
```

### 14.3 Convex Tracking

```
# Existing tables
tasks:*, content:*, campaigns:*, projects:*, pipeline:*

# Content tracking (use existing tables)
- Each blog post = a task in the campaign
- Each scraped document = a resource
- Pipeline handles: backlog → researched → briefed → drafted → reviewed → humanized → completed
```

### 14.4 Publishing to BusinessPress

**Approach: Laravel API endpoint**

```
POST /api/posts
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
  "title": "...",
  "slug": "...",
  "content": "...(markdown)...",
  "categories": ["concrete-masonry", "concrete-slabs"],
  "tags": ["calculator", "diy"],
  "meta_description": "...",
  "schema_markup": "...(JSON-LD)...",
  "status": "publish"     ← all at once, no drip
}
```

**Decision: All content published at once** (maximizes SEO surface area immediately).

**Decision: No images initially** (can add programmatically later via BusinessPress thumbnail/cover/gallery fields).

---

## 15. Scale Estimates

### 15.1 Page Count by Type

| Page Type | Count | Avg Monthly Vol/Page | Total Monthly Vol |
|-----------|------:|---------------------:|------------------:|
| Topic blog posts | 4,000 | 200-2,000 | 800K-8M |
| Q&A pages | 4,000 | 50-500 | 200K-2M |
| City pages | 7,000 | 50-500 | 350K-3.5M |
| Brand pages | 500 | 100-1,000 | 50K-500K |
| **TOTAL** | **15,500** | | **1.4M-14M** |

### 15.2 Scraped Content Volume

| Source | Count | Avg Size | Total |
|--------|------:|--------:|------:|
| Blog articles | 3,000 | 15 KB | 45 MB |
| YouTube transcripts | 500 | 30 KB | 15 MB |
| Reddit threads | 1,000 | 5 KB | 5 MB |
| Yelp reviews | 2,000 | 3 KB | 6 MB |
| Quora Q&A | 300 | 8 KB | 2.4 MB |
| Manufacturer guides | 50 | 50 KB | 2.5 MB |
| Generated pages | 15,500 | 5 KB | 78 MB |
| **Total** | | | **~154 MB** |

### 15.3 Cost Estimates

| Resource | Unit Cost | Quantity | Total |
|----------|----------|---------|------:|
| Claude API (blog posts) | ~$0.04/article | 4,000 | $160 |
| Claude API (Q&A pages) | ~$0.01/page | 4,000 | $40 |
| Claude API (city page intros) | ~$0.005/page | 7,000 | $35 |
| Claude API (review + humanize) | ~$0.02/article | 4,000 | $80 |
| Claude API (audience research) | ~$0.15/segment | 12 | $1.80 |
| DataImpulse proxy (Yelp) | ~$0.005/req | ~1,800 | $9 |
| Crawl4AI / yt-dlp / GAU | Self-hosted (free) | -- | $0 |
| **Total** | | | **~$325** |

### 15.4 Timeline

| Phase | Activity | Duration | Output |
|:-----:|----------|:--------:|--------|
| 0 | Setup: project, Convex, scripts, categories | 2-3 days | Infrastructure |
| 1a | Web archive mining: all domains | 2-3 days | URL inventory (SQLite) |
| 1b | Content scraping: blogs via Crawl4AI | 5-7 days | ~3,000 articles |
| 1c | Content scraping: YouTube, Reddit, Quora | 3-5 days | ~1,800 documents |
| 1d | Yelp scraping: Scrapling + DataImpulse | 3-5 days | ~2,000 review records |
| 2 | Audience research: 12 focus groups | 3-5 days | 12 profiles |
| 3 | Question extraction + dedup | 2-3 days | 4,000 Q&A candidates |
| 4 | Blog post generation (batched by category) | 20-30 days | 4,000 posts |
| 5 | Q&A page generation | 5-7 days | 4,000 Q&A pages |
| 6 | City page generation | 5-7 days | 7,000 city pages |
| 7 | Brand page generation | 3-5 days | 500 brand pages |
| 8 | SEO: schema, linking, categories | 3-5 days | All pages optimized |
| 9 | Publish to BusinessPress | 2-3 days | All live |
| | **Total** | **~55-85 days** | **~15,500 pages** |

---

## 16. Phase Ordering & Rollout

### Phase 0: Foundation (Days 1-3)

**Tasks:**
1. Create FatStud project in Convex
2. Create product record
3. Create category taxonomy in BusinessPress (Section 10)
4. Build web archive mining script (Section 5)
5. Build Yelp scraping scripts (Section 4)
6. Create directory structure
7. Build/verify BusinessPress API endpoint for post import
8. Generate US cities data file (500+ cities)

**Acceptance criteria:**
- [ ] FatStud project in Convex
- [ ] 15 parent + ~60 child categories created in BusinessPress
- [ ] Archive mining script runs and produces SQLite output
- [ ] Cities data file with 500+ US cities
- [ ] Directory structure created

### Phase 1: Data Collection (Days 4-15)

**1a: Web Archive Mining (Days 4-6)**
- Run `discover-construction-urls.sh` for all Tier 1-4 domains
- Run `discover-yelp-urls.sh` for yelp.com construction categories
- Filter URLs: year >= 2020, deduplicate
- Expected: 100K+ URLs in SQLite

**1b: Blog Scraping (Days 6-12)**
- Prioritize URLs by domain + keyword match
- Crawl4AI bulk scraping: ~3,000 articles
- Store in `knowledge/construction/blogs/`

**1c: YouTube + Reddit + Quora (Days 8-12)**
- YouTube: 500+ transcripts from 12 channels
- Reddit: 1,000+ thread extracts from 10 subreddits
- Quora: 300+ Q&A from 8 topics

**1d: Yelp Mining (Days 10-15)**
- Web archive: extract Yelp business URLs (construction categories)
- Scrapling: scrape top-reviewed businesses per city per category
- Budget: ~1,800 requests via DataImpulse ($9)
- Extract: review text, pricing mentions, questions

### Phase 2: Audience Research (Days 16-20)

- Generate 12-15 focus groups
- Use scraped voice data from Reddit, Yelp, Quora
- Store in Convex
- Human review and approval

### Phase 3: Question Extraction (Days 21-23)

- Extract questions from all scraped sources
- Deduplicate by semantic similarity
- Match to keyword groups + categories
- Produce prioritized Q&A candidate list (target: 4,000)

### Phase 4: Blog Post Generation (Days 24-53)

Batched by category, 3 parallel agents:

| Batch | Category | Posts | Days |
|:-----:|----------|------:|:----:|
| 1 | Concrete & Masonry | 500 | 24-30 |
| 2 | Roofing | 400 | 27-33 |
| 3 | Electrical + Plumbing | 350 | 30-36 |
| 4 | Paint & Flooring | 400 | 33-39 |
| 5 | Landscaping | 350 | 36-42 |
| 6 | Deck, Fence, Outdoor | 350 | 39-45 |
| 7 | Drywall, Insulation, Lumber | 350 | 42-48 |
| 8 | Measurements, Stairs, Misc | 350 | 45-51 |
| 9 | Cost Guides, Tools | 350 | 48-53 |
| | **Total** | **3,400** | |

Remaining 600 posts filled from long-tail keyword expansion during generation.

### Phase 5: Q&A Page Generation (Days 45-51)

- Template-driven, faster than blog posts
- 4,000 Q&A pages
- Batch by category
- Can run in parallel with Phase 4 tail end

### Phase 6: City Page Generation (Days 50-56)

- Programmatic with unique intros
- 7,000 city pages (500+ cities × 12 service types)
- Template sections + generated intro paragraphs
- Inject Yelp pricing data where available

### Phase 7: Brand Page Generation (Days 55-59)

- 500 brand pages
- Brand guides + brand comparisons
- Match to manufacturer scraped data

### Phase 8: SEO & Linking (Days 58-62)

- Generate schema markup for all 15,500 pages
- Build internal linking graph
- Assign categories (multi-category where appropriate)
- Generate XML sitemap

### Phase 9: Publish (Days 63-65)

- Bulk publish all pages to BusinessPress via API
- All at once (no drip)
- Submit sitemap to Google Search Console
- QA spot-check 5% of pages

---

## 17. Resolved Decision Points

| DP | Question | Decision |
|:--:|----------|----------|
| DP-1 | Publishing API | Laravel API endpoint (POST /api/posts) |
| DP-2 | Publication cadence | **All at once** |
| DP-3 | Author attribution | "FatStud Team" (no individual authors) |
| DP-4 | Images | **No images initially** — add programmatically later via BusinessPress thumbnail/cover/gallery fields |
| DP-5 | Calculator integration | Pre-filled calculator links with example values |
| DP-6 | Provider directory | Category-specific links when directory is populated |
| DP-7 | Convex project | Check/create via `npx convex run projects:list` |
| DP-8 | Yelp approach | Web archive mining (2020+) + Scrapling with DataImpulse proxy |
| DP-9 | Scraper architecture | Bash URL discovery (SQLite) + Python/Crawl4AI content scraping |
| DP-10 | Q&A pages | Yes, 3,000-5,000 programmatic Q&A pages |
| DP-11 | City scope | All US cities with 50K+ population (500+) |
| DP-12 | Category structure | 2-level hierarchy: 15 parents, ~60 children |
| DP-13 | Page count target | 20,000+ (topic + city + brand + Q&A) |

---

## 18. Risk Register

| # | Risk | Prob | Impact | Mitigation |
|:-:|------|:----:|:------:|------------|
| R1 | Google penalizes for rapid bulk publish | Medium | High | Ensure unique value per page, no thin content, proper schema |
| R2 | AI content detected by Google | Medium | High | Humanizer pass, specific measurements, real data from Yelp/Reddit |
| R3 | Yelp blocks scraping / DataImpulse budget runs out | Medium | Low | Web archives are free fallback, $9 covers ~1,800 pages |
| R4 | City pages too thin / templatic | Medium | Medium | Generate unique intros, inject local Yelp data, local climate info |
| R5 | Duplicate content across similar keywords | Medium | High | Dedup keywords before generating, canonical tags, consolidation |
| R6 | Rate limiting during blog scraping | Medium | Low | Respect robots.txt, delays, domain rotation, Crawl4AI caching |
| R7 | Quality drops below 7.0 at scale | Medium | Medium | Review first 50 manually, tune prompts, adjust templates |
| R8 | BusinessPress API not ready | Medium | Medium | Store all as markdown, bulk import later |
| R9 | Q&A pages cannibalize blog post rankings | Low | Medium | Different intent targeting, canonical tags, internal linking strategy |
| R10 | 20K pages overwhelm sitemap / crawl budget | Low | Medium | Priority sitemap, category-based sitemap index |

---

## Appendix A: File Path Reference

| Resource | Path |
|----------|------|
| This plan (v2) | `/var/www/vibe-marketing/thoughts/shared/plans/fatstud-content-factory-plan-v2.md` |
| Original plan (v1) | `/var/www/vibe-marketing/thoughts/shared/plans/fatstud-content-factory-plan.md` |
| Master keyword summary | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/MASTER-SUMMARY.md` |
| Autocomplete data | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/autocomplete-suggestions.txt` |
| Calculator comparison | `/var/www/vibe-marketing/rust/construction-calculators/calculator-comparison-analysis.md` |
| Scrapling binary | `/home/vuk/.local/bin/scrapling` |
| DataImpulse proxy | Configured in `/var/www/onlyfansapi/.env` as `SCRAPER_PROXY` |
| OF scraper (reference) | `/var/www/onlyfansapi/scripts/discover-onlyfans-usernames.sh` |
| Skills directory | `/var/www/vibe-marketing/.claude/skills/` |
| MCP config | `/var/www/vibe-marketing/.mcp.json` |
| Knowledge base (target) | `/var/www/vibe-marketing/knowledge/construction/` |
| Content output (target) | `/var/www/vibe-marketing/projects/fatstud/` |
| Scraping scripts (target) | `/var/www/vibe-marketing/scripts/scraping/` |

## Appendix B: Quick-Start Commands

```bash
# 1. Verify infrastructure
curl -s http://localhost:11235/health                                    # Crawl4AI
npx convex run projects:list --url http://localhost:3210                 # Convex
scrapling --version                                                      # Scrapling

# 2. Read this plan
cat /var/www/vibe-marketing/thoughts/shared/plans/fatstud-content-factory-plan-v2.md

# 3. Read keyword research
cat /var/www/vibe-marketing/rust/construction-calculators/keyword-research/MASTER-SUMMARY.md

# 4. Start Phase 0
# ... (see Phase 0 tasks in Section 16)
```
