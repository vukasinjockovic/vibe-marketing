# FatStud Content Factory -- Pre-Plan

**Created:** 2026-03-07
**Author:** architect-agent (Opus)
**Purpose:** Comprehensive pre-plan for building a construction content factory that produces thousands of blog posts for fatstud.businesspress.dev. A fresh Claude Code session should be able to read this document and immediately create a task-by-task implementation plan.

---

## Table of Contents

1. [Situation Summary](#1-situation-summary)
2. [Keyword Groups Inventory](#2-keyword-groups-inventory)
3. [Content Scraping Strategy](#3-content-scraping-strategy)
4. [Vibe-Marketing Platform Capabilities](#4-vibe-marketing-platform-capabilities)
5. [Audience Research Plan](#5-audience-research-plan)
6. [Content Cross-Referencing Strategy](#6-content-cross-referencing-strategy)
7. [Blog Post Generation Pipeline](#7-blog-post-generation-pipeline)
8. [Technical Implementation](#8-technical-implementation)
9. [Scale Estimates](#9-scale-estimates)
10. [Phase Ordering & Rollout](#10-phase-ordering--rollout)
11. [Decision Points Requiring Human Input](#11-decision-points-requiring-human-input)
12. [Risk Register](#12-risk-register)

---

## 1. Situation Summary

### What Exists

- **Site:** fatstud.businesspress.dev (Laravel 12 + BusinessPress)
- **Infrastructure:** Homepage, calculator CPT (custom post type), provider CPT
- **Keyword research:** 17,967 keywords from Google Keyword Planner across 15 categories (40.6M monthly searches/mo)
- **Autocomplete research:** 5,976 additional unique suggestions from Google Autocomplete API
- **Competitor analysis:** 104 unique calculators identified across OmniCalculator, InchCalculator, and Blocklayer
- **Calculator comparison file:** `/var/www/vibe-marketing/rust/construction-calculators/calculator-comparison-analysis.md` (63KB, detailed feature-by-feature)

### What We Need to Build

A **content factory** that:
1. Scrapes construction knowledge from the web (blogs, YouTube, Reddit, Quora, manufacturer guides)
2. Researches target audiences via vibe-marketing agents
3. Cross-references scraped content with keyword data and audience segments
4. Generates thousands of unique, high-quality blog posts
5. Publishes to BusinessPress via the existing Laravel infrastructure

### Revenue Opportunity

| Scenario | Monthly Traffic | Monthly Revenue | Annual Revenue |
|----------|---------------:|----------------:|---------------:|
| Conservative (1% capture, $25 RPM) | 406,472 | $10,161 | $121,939 |
| Moderate (5% capture, $35 RPM) | 2,032,362 | $71,132 | $853,590 |
| Optimistic (10% capture, $50 RPM) | 4,064,725 | $203,236 | $2,438,836 |

---

## 2. Keyword Groups Inventory

### All 15 Category Groups

| # | Category | Unique KWs | Monthly Vol | Top Keywords (50K+) | Blog Post Potential |
|:-:|----------|----------:|------------:|--------------------:|--------------------:|
| 1 | **Square Footage & Conversions** | 4,158 | 25,861,350 | sq ft calculator, acre to sq ft, how to calculate square footage, cubic footage, cubic yard | 200-300 |
| 2 | **Paint & Flooring** | 3,370 | 1,502,700 | paint calculator, tile calculator, carpet installation cost | 250-350 |
| 3 | **Concrete** | 2,834 | 6,702,400 | concrete calculator, concrete slab, concrete block, concrete cost, concrete yards, concrete volume, concrete bags, concrete floor | 200-300 |
| 4 | **Landscaping** | 2,562 | 1,020,750 | gravel calculator, mulch calculator, topsoil calculator | 200-280 |
| 5 | **Roofing** | 1,922 | 1,640,300 | roofing calculator, roof pitch calculator | 150-200 |
| 6 | **Electrical** | 1,753 | 731,650 | conduit fill calculator, voltage drop calculator, wire gauge chart | 120-180 |
| 7 | **Deck & Fence** | 1,333 | 747,350 | deck calculator, fence calculator | 100-150 |
| 8 | **Misc Construction** | 1,009 | 575,050 | stair calculator | 80-120 |
| 9 | **Brick & Masonry** | 988 | 626,650 | (no 50K+ keywords; retaining wall at 5K is top) | 80-120 |
| 10 | **Lumber & Board Feet** | 638 | 592,800 | board feet calculator, linear feet | 60-90 |
| 11 | **Drywall & Insulation** | 527 | 567,650 | drywall calculator, drywall installation cost | 50-80 |
| 12 | **Patio & Outdoor** | 459 | 89,850 | (no 50K+ keywords) | 40-60 |
| 13 | **Roofing Cost Extended** | 410 | 136,350 | (cost-specific roofing keywords) | 30-50 |
| 14 | **Flooring Extended** | 209 | 106,100 | (cost-specific flooring keywords) | 20-35 |
| 15 | **Concrete Cost Extended** | 125 | 69,250 | concrete pad cost calculator at 50K | 15-25 |
| | **TOTALS** | **~17,967** | **~40.6M** | | **1,395-2,340** |

### Key Files for Each Category

All files are in `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/`:

| Category | Analysis File | Raw CSV (in categories/) |
|----------|---------------|--------------------------|
| Square Footage | `square-footage-latest-analysis.md` | `square-footage-Keyword Stats 2026-03-07 at 03_56_16.csv` |
| Paint & Flooring | `paint-flooring-latest-analysis.md` | (multiple CSVs) |
| Concrete | `concrete-latest-analysis.md` | `g1-concrete-volume/` |
| Landscaping | `landscaping-latest-analysis.md` | `landscaping.txt` |
| Roofing | `roofing-latest-analysis.md` | `g2-roofing/` |
| Electrical | `electrical-latest-analysis.md` | `electrical-Keyword Stats 2026-03-07 at 03_52_24.csv` |
| Deck & Fence | `deck-fence-latest-analysis.md` | `g3-deck-and-fence/` |
| Misc Construction | `misc-construction-latest-analysis.md` | `other-Keyword Stats 2026-03-07 at 04_03_20.csv` |
| Brick & Masonry | `brick-masonry-latest-analysis.md` | `brick-Keyword Stats 2026-03-07 at 03_54_39.csv` |
| Lumber | `lumber-latest-analysis.md` | `lumber-Keyword Stats 2026-03-07 at 03_51_44.csv` |
| Drywall & Insulation | `drywall-insulation-latest-analysis.md` | `drywall-Keyword Stats 2026-03-07 at 03_50_54.csv` |
| Patio & Outdoor | `patio-outdoor-latest-analysis.md` | `patio-Keyword Stats 2026-03-07 at 03_55_07.csv` |
| Roofing Cost Ext | `roofing-cost-extended-latest-analysis.md` | `roofing-extended-Keyword Stats 2026-03-07 at 04_01_28.csv` |
| Flooring Extended | `flooring-extended-latest-analysis.md` | `flooring-Keyword Stats 2026-03-07 at 04_02_28.csv` |
| Concrete Cost Ext | `concrete-cost-extended-latest-analysis.md` | `concrete-extend-Keyword Stats 2026-03-07 at 04_00_01.csv` |

### Autocomplete Data

- **File:** `autocomplete-suggestions.txt` (5,976 unique suggestions)
- **Structured data:** `category-data.json`
- **Per-category files** in `categories/`:
  - `core-materials.txt` (2,625 keywords)
  - `construction-tasks.txt` (1,261 keywords)
  - `cost-calculators.txt` (670 keywords)
  - `electrical-plumbing.txt` (553 keywords)
  - `landscaping.txt` (511 keywords)
  - `unit-conversions.txt` (403 keywords)

### Blog-Mappable Keyword Patterns

The following keyword patterns from the research directly map to blog post templates:

| Pattern | Example Keywords | Blog Template | Est. Posts |
|---------|-----------------|---------------|----------:|
| "how to calculate [X]" | how to calculate square footage, how to figure concrete | How-To Guide | 200+ |
| "how much [X] do I need" | how much concrete do I need, how much mulch do I need | Material Calculator Guide | 150+ |
| "[X] cost per [unit]" | concrete cost per yard, roofing cost per square | Cost Breakdown | 100+ |
| "[X] vs [Y]" | concrete vs asphalt driveway, composite vs wood decking | Comparison Guide | 80+ |
| "[brand] [calculator]" | quikrete calculator, trex deck calculator, laticrete grout | Brand-Specific Guide | 40+ |
| "[project] calculator" | driveway calculator, patio calculator, shed calculator | Project Planning Guide | 100+ |
| "[X] installation guide" | tile installation, drywall installation, fence installation | Step-by-Step Guide | 80+ |
| "best [X] for [Y]" | best mulch for flower beds, best concrete mix for posts | Product Recommendation | 60+ |
| "[X] problems/issues" | concrete cracking, roof leak, voltage drop issues | Troubleshooting Guide | 50+ |
| "[code/standard] [topic]" | NEC conduit fill, building code stairs, R-value requirements | Code Reference Guide | 40+ |

---

## 3. Content Scraping Strategy

### 3.1 Available Scraping Infrastructure

#### Crawl4AI (CONFIRMED RUNNING)
- **Status:** Running and healthy at `http://localhost:11235`
- **Version:** 0.5.1-d1
- **Configuration:** Defined in `docker-compose.yml` at `/var/www/vibe-marketing/docker-compose.yml`
- **Container name:** `crawl4ai`
- **Use for:** Bulk article scraping, structured content extraction
- **MCP server:** `crawl4ai` available in `.mcp.json` (all tools exposed)

#### Firecrawl MCP
- **Status:** Available as MCP server `firecrawl` in `.mcp.json`
- **Use for:** Single-page structured scraping, JS-rendered pages
- **Tools:** All tools exposed (crawl, scrape, search, map, extract)

#### YouTube Transcript Tool
- **MCP server:** `youtube` available in `.mcp.json`
- **Skill script:** `/var/www/vibe-marketing/.claude/skills/youtube-research/scripts/youtube_research.py`
- **Use for:** Video transcript extraction, comment mining
- **Dependencies:** `yt-dlp` (free, no API key)

#### Playwright MCP
- **Status:** Available as MCP server `playwright` in `.mcp.json`
- **Use for:** JS-heavy sites that need browser rendering

#### Brave Search MCP
- **Status:** Available as MCP server `brave-search` in `.mcp.json`
- **Use for:** Discovering URLs to scrape, finding content sources

### 3.2 Sources to Scrape

#### Tier 1: Construction Blogs (High Authority, Long-Form Content)

| Source | URL | Content Type | Est. Articles to Scrape | Priority |
|--------|-----|-------------|------------------------:|:--------:|
| This Old House | thisoldhouse.com | How-to guides, project walkthroughs | 500-800 | HIGH |
| Family Handyman | familyhandyman.com | DIY tutorials, tips & tricks | 400-600 | HIGH |
| Bob Vila | bobvila.com | Home improvement guides | 300-500 | HIGH |
| Fine Homebuilding | finehomebuilding.com | Professional-grade techniques | 200-400 | HIGH |
| JLC Online | jlconline.com | Trade-specific articles | 150-300 | MEDIUM |
| Pro Tool Reviews | protoolreviews.com | Tool & material reviews | 100-200 | MEDIUM |
| Builder Online | builderonline.com | Builder industry insights | 100-200 | MEDIUM |
| Concrete Network | concretenetwork.com | Concrete-specific deep dives | 200-300 | HIGH |
| The Spruce | thespruce.com | Consumer-friendly home guides | 300-500 | MEDIUM |
| Hunker | hunker.com | Home improvement basics | 200-300 | MEDIUM |

**Scraping approach:** Use Crawl4AI to crawl site maps, extract article URLs, then bulk-scrape article content (title, body text, images, categories, publish date).

#### Tier 2: YouTube Channels (Video Transcripts)

| Channel | Focus | Est. Videos | Priority |
|---------|-------|------------:|:--------:|
| Essential Craftsman | General construction, concrete, framing | 300+ | HIGH |
| This Old House (YT) | Full project walkthroughs | 1,500+ | HIGH |
| Home RenoVision DIY | DIY renovation tutorials | 400+ | HIGH |
| Vancouver Carpenter | Carpentry, framing, finishing | 200+ | MEDIUM |
| Larry Haun | Framing masterclass | 100+ | MEDIUM |
| Matt Risinger | Building science, materials | 500+ | HIGH |
| Stumpy Nubs | Woodworking, workshop | 300+ | LOW |
| RR Buildings | Pole barns, metal buildings | 200+ | MEDIUM |
| Build Show Network | Building techniques | 150+ | MEDIUM |
| Sparky Channel | Electrical tutorials | 200+ | HIGH |
| Roger Wakefield | Plumbing tutorials | 300+ | HIGH |
| Roof It Right | Roofing tutorials | 100+ | HIGH |

**Scraping approach:** Use `youtube_research.py` script with `--search` to find relevant videos, `--extract transcripts` to get full transcripts. Store in `/tmp/yt_transcripts/` initially, then move to knowledge base.

#### Tier 3: Reddit Communities (Audience Voice + Technical Q&A)

| Subreddit | Members | Content Value | Priority |
|-----------|---------|--------------|:--------:|
| r/HomeImprovement | 5M+ | DIY questions, project results, material recommendations | HIGH |
| r/DIY | 22M+ | Broad DIY including construction | HIGH |
| r/Construction | 200K+ | Pro trade discussions, techniques | HIGH |
| r/Carpentry | 200K+ | Framing, finishing, woodwork | MEDIUM |
| r/Electricians | 300K+ | Code questions, wiring help | HIGH |
| r/Plumbing | 200K+ | Pipe sizing, drain issues | MEDIUM |
| r/Roofing | 50K+ | Material comparisons, estimates | HIGH |
| r/Concrete | 30K+ | Mix ratios, finishing techniques | HIGH |
| r/Landscaping | 300K+ | Material calculations, design | MEDIUM |
| r/Drywall | 10K+ | Finishing, mud, tape techniques | MEDIUM |

**Scraping approach:** Use the `reddit` MCP server and/or the audience research skill's `scrape_reddit.py` script. Focus on extracting:
- Top posts per subreddit (last year, top 100)
- Comment threads with detailed technical answers
- Questions that match our keyword groups

#### Tier 4: Quora Topics (Question-Based Content Ideas)

Target Quora topics:
- "Home Improvement"
- "Construction"
- "DIY Home Projects"
- "Roofing"
- "Electrical Wiring"
- "Concrete Work"
- "Landscaping"
- "Carpentry"

**Scraping approach:** Use `/var/www/vibe-marketing/.claude/skills/quora-research/scripts/quora_questions.py` to discover high-engagement questions, then `quora_answers.py` for expert answers. Max 10-20 questions per topic to stay polite.

#### Tier 5: Manufacturer Guides & Technical Resources (Free PDFs and Guides)

| Manufacturer | Products | Content Type | Priority |
|-------------|----------|-------------|:--------:|
| Quikrete | Concrete, mortar, stucco | Product guides, calculators, how-tos | HIGH |
| Sakrete | Concrete, mortar | Application guides, mix ratios | HIGH |
| GAF | Roofing shingles | Installation guides, specs | HIGH |
| Owens Corning | Roofing, insulation | Installation guides, R-value charts | HIGH |
| CertainTeed | Roofing, siding, insulation | Product specs, installation | MEDIUM |
| Trex | Composite decking | Installation guides, span tables | MEDIUM |
| Behr/PPG/S-W | Paint | Coverage calculators, color guides | MEDIUM |
| James Hardie | Fiber cement siding | Installation guides | MEDIUM |
| NEC (NFPA 70) | Electrical code | Code tables (conduit fill, wire gauge) | HIGH |
| Simpson Strong-Tie | Connectors, fasteners | Span tables, load charts | HIGH |

**Scraping approach:** Use Firecrawl or Crawl4AI for web-based guides. For PDFs, download directly and extract text. Store in knowledge base with source attribution.

### 3.3 Data Storage Plan

```
/var/www/vibe-marketing/knowledge/construction/
├── blogs/
│   ├── this-old-house/
│   │   ├── _index.json          # Source metadata
│   │   └── articles/
│   │       ├── how-to-pour-concrete-slab.md
│   │       └── ...
│   ├── family-handyman/
│   ├── bob-vila/
│   ├── fine-homebuilding/
│   ├── concrete-network/
│   └── ...
├── youtube/
│   ├── essential-craftsman/
│   │   ├── _index.json          # Channel metadata
│   │   └── transcripts/
│   │       ├── {video_id}-{slug}.md
│   │       └── ...
│   ├── matt-risinger/
│   ├── sparky-channel/
│   └── ...
├── reddit/
│   ├── home-improvement/
│   │   ├── _index.json          # Subreddit metadata
│   │   └── threads/
│   │       ├── top-2025-concrete-slab.md
│   │       └── ...
│   ├── construction/
│   ├── electricians/
│   └── ...
├── quora/
│   ├── topics/
│   │   ├── concrete-work.json
│   │   └── ...
│   └── voice-data/
│       ├── construction-voice.json
│       └── ...
├── manufacturer-guides/
│   ├── quikrete/
│   ├── gaf/
│   ├── owens-corning/
│   └── ...
└── _scraped-index.json          # Master index: what's been scraped, when, hash
```

### 3.4 Scrape Data Format

Each scraped article should be stored as markdown with YAML frontmatter:

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
keywords: ["concrete slab", "pour concrete", "slab foundation"]
wordCount: 2500
matchedKeywordGroups: ["concrete", "concrete-cost-extended"]
---

[Extracted article text in markdown format]
```

---

## 4. Vibe-Marketing Platform Capabilities

### 4.1 Available Agent Skills (Relevant to Content Factory)

| Skill | Location | Purpose in Content Factory |
|-------|----------|---------------------------|
| **audience-research-procedures** | `.claude/skills/audience-research-procedures/SKILL.md` | Generate focus group profiles for construction audiences |
| **content-writing-procedures** | `.claude/skills/content-writing-procedures/SKILL.md` | Generate blog posts using the L1-L5 skill layer model |
| **content-review-procedures** | `.claude/skills/content-review-procedures/SKILL.md` | Quality-score articles (8 dimensions, 1-10 scale, auto-approve at 7+) |
| **humanizer** | `.claude/skills/humanizer/SKILL.md` | Remove AI writing patterns (24 pattern categories) |
| **youtube-research** | `.claude/skills/youtube-research/SKILL.md` | Extract transcripts and comments from YouTube |
| **quora-research** | `.claude/skills/quora-research/SKILL.md` | Mine Quora for audience voice data |
| **google-suggest-research** | `.claude/skills/google-suggest-research/SKILL.md` | Expand seed keywords via Google Autocomplete |
| **programmatic-seo** | `.claude/skills/programmatic-seo/SKILL.md` | Template-based page generation at scale |
| **schema-markup** | `.claude/skills/schema-markup/SKILL.md` | JSON-LD structured data for rich results |
| **content-strategy** | `.claude/skills/content-strategy/SKILL.md` | Plan content topics, clusters, calendar |
| **seo-audit** | `.claude/skills/seo-audit/SKILL.md` | Audit SEO on published pages |
| **copywriting** | `.claude/skills/copywriting/SKILL.md` | Direct-response copy for CTAs |
| **writing-clearly-and-concisely** | `.claude/skills/writing-clearly-and-concisely/SKILL.md` | Strunk's rules, applied DURING generation |

### 4.2 Marketing Book Skills (L1-L5 Layer Model)

These skills provide frameworks for writing. For construction content, the most relevant are:

| Layer | Skill | Use in Construction Content |
|:-----:|-------|----------------------------|
| L1 | `mbook-schwarz-awareness` | Match content angle to reader awareness stage (DIYer who has never done concrete vs licensed contractor) |
| L2 | `mbook-hormozi-offers` | Frame calculator/tool value propositions |
| L4 | `mbook-ogilvy-advertising` | Factual, research-heavy writing style appropriate for technical construction content |
| L5 | `writing-clearly-and-concisely` | Clean, direct technical writing |
| L5 | `humanizer` | Remove AI patterns post-generation |

### 4.3 MCP Servers Available

All MCP servers are configured in `/var/www/vibe-marketing/.mcp.json`:

| Server | Available Tools | Use in Content Factory |
|--------|-----------------|------------------------|
| `crawl4ai` | All crawl/scrape tools | Bulk blog scraping |
| `firecrawl` | crawl, scrape, search, map, extract | Single-page structured extraction |
| `playwright` | All browser automation | JS-heavy sites |
| `brave-search` | Web search | URL discovery, fact-checking |
| `perplexity` | AI search | Research questions |
| `youtube` | Video download/transcript | YouTube content extraction |
| `reddit` | Reddit API access | Subreddit scraping |
| `dataforseo` | SEO data | SERP analysis, keyword difficulty |

### 4.4 Convex Database (Self-Hosted at localhost:3210)

The vibe-marketing platform uses Convex for all data. Relevant tables/functions:

| Entity | Convex Function | Purpose |
|--------|----------------|---------|
| Projects | `projects:*` | FatStud project record |
| Campaigns | `campaigns:*` | Content campaigns |
| Tasks | `tasks:*` | Individual task tracking |
| Content | `content:*` | Content records |
| Focus Groups | `focusGroups:*` | Audience segments |
| Resources | `resources:*` | Content artifacts (files, articles) |
| Pipeline | `pipeline:*` | Pipeline step management |
| Activities | `activities:*` | Activity logging |

### 4.5 Content Pipeline Flow

The existing vibe-marketing pipeline follows this flow:

```
backlog → researched → briefed → drafted → reviewed → humanized → completed
```

Each step is handled by a specific agent:
1. **vibe-audience-researcher** → produces focus group profiles (researched)
2. **vibe-brief-writer** (or human) → creates content briefs (briefed)
3. **vibe-content-writer** → writes the article (drafted)
4. **vibe-content-reviewer** → scores on 8 dimensions (reviewed, auto-approve at 7+)
5. **vibe-humanizer** → removes AI patterns (humanized)
6. **human** → final approval and publish (completed)

### 4.6 Focus Group Data Format

Focus groups in vibe-marketing follow this schema (from audience-research-procedures SKILL.md):

```json
{
  "name": "DIY Weekend Warriors",
  "nickname": "The Home Depot Regulars",
  "category": "Homeowner DIYers",
  "overview": "...",
  "demographics": {
    "ageRange": "30-55",
    "gender": "70% male, 30% female",
    "income": "Middle class, $50K-$100K household",
    "lifestyle": "Homeowners, suburban, hands-on",
    "triggers": ["YouTube video inspiration", "Home purchase", "Broken item needing repair"]
  },
  "psychographics": {
    "values": ["Self-reliance", "Saving money", "Pride in craftsmanship"],
    "beliefs": ["I can do it myself", "Contractors overcharge", "YouTube has all the answers"],
    "lifestyle": "Weekend project warriors",
    "identity": "Handy homeowner"
  },
  "coreDesires": ["Save money on home projects", "..."],
  "painPoints": ["Not knowing how much material to buy", "..."],
  "fears": ["Buying too much and wasting money", "..."],
  "objections": ["These calculators are probably inaccurate", "..."],
  "languagePatterns": ["how many bags of concrete do I need", "..."],
  "awarenessStage": "solution_aware",
  "awarenessConfidence": "high"
}
```

---

## 5. Audience Research Plan

### 5.1 Audience Segment Mapping

Construction calculator users fall into distinct groups that map to our keyword categories:

| Segment ID | Audience Segment | Primary Keyword Groups | Awareness Stage | Content Tone |
|:----------:|-----------------|----------------------|:---------------:|:------------:|
| A1 | **DIY Homeowner -- First Project** | Sq footage, paint, tile, mulch | Problem Aware | Encouraging, step-by-step |
| A2 | **DIY Homeowner -- Experienced** | Concrete, deck, fence, drywall | Solution Aware | Efficient, detail-oriented |
| A3 | **Licensed Electrician** | Electrical (all) | Most Aware | Code-reference, NEC tables |
| A4 | **General Contractor / Estimator** | Concrete cost, roofing cost, all cost calcs | Most Aware | Precise, professional, fast |
| A5 | **Roofing Contractor** | Roofing (all) | Most Aware | Industry-specific, estimation |
| A6 | **Landscaper / Hardscaper** | Landscaping, brick/masonry, patio | Solution Aware | Material-focused, seasonal |
| A7 | **Carpenter / Framer** | Lumber, deck, stairs, misc construction | Most Aware | Trade jargon, span tables |
| A8 | **Real Estate Investor / Flipper** | All cost calculators | Product Aware | ROI-focused, time-is-money |
| A9 | **Property Manager** | Drywall repair, paint, flooring cost | Solution Aware | Budget-conscious, vendor comparison |
| A10 | **Architecture / Engineering Student** | Sq footage, conversions, structural | Problem Aware | Educational, formula-oriented |
| A11 | **Concrete Professional** | Concrete (all) | Most Aware | Mix design, pour techniques |
| A12 | **DIY Homeowner -- Bathroom/Kitchen Reno** | Tile, flooring, paint, drywall | Solution Aware | Project-specific, visual |

### 5.2 Reddit / Quora / YouTube Communities per Segment

| Segment | Reddit Communities | Quora Topics | YouTube Channels |
|---------|-------------------|-------------|-----------------|
| A1 (DIY First) | r/HomeImprovement, r/DIY | "Home Improvement", "DIY Projects" | Home RenoVision DIY, This Old House |
| A2 (DIY Experienced) | r/HomeImprovement, r/DIY, r/Concrete | "Home Renovation" | Essential Craftsman, Matt Risinger |
| A3 (Electrician) | r/Electricians, r/AskElectricians | "Electrical Wiring", "NEC Code" | Sparky Channel, ElectricianU |
| A4 (GC/Estimator) | r/Construction, r/Contractors | "Construction Management" | Builder Show, RR Buildings |
| A5 (Roofer) | r/Roofing | "Roofing" | Roof It Right, Dmitry Lipinskiy |
| A6 (Landscaper) | r/Landscaping, r/Hardscaping | "Landscaping", "Patio" | Yard Mastery, Myatt Landscaping |
| A7 (Carpenter) | r/Carpentry, r/Framing | "Carpentry" | Essential Craftsman, Larry Haun |
| A8 (Investor) | r/realestateinvesting, r/FlippingHouses | "Real Estate Investing" | BiggerPockets |
| A11 (Concrete Pro) | r/Concrete, r/Construction | "Concrete Work" | Mike Day Concrete, Essential Craftsman |
| A12 (Bathroom DIY) | r/BathroomDIY, r/HomeImprovement | "Bathroom Renovation" | Home RenoVision DIY |

### 5.3 Focus Group Generation Plan

**Tool:** `vibe-audience-researcher` agent using `audience-research-procedures` skill.

**Process:**
1. Create a FatStud project in Convex (if not exists)
2. Create a product record for "FatStud Construction Calculators"
3. Run audience researcher with web search + Reddit scraping for each segment
4. Target: 12-15 focus groups covering the segments above
5. Store focus groups in Convex via `focusGroupStaging:createBatch`

**Key research queries for construction audiences:**
- "DIY homeowner construction calculator frustrations"
- "reddit how much concrete do I need"
- "contractor estimating software complaints"
- "first time homeowner renovation mistakes"
- "electrician NEC code calculator"
- "landscaping material calculator accuracy"

---

## 6. Content Cross-Referencing Strategy

### 6.1 Topic-to-Keyword Mapping

For each scraped article:
1. Extract the main topic and sub-topics
2. Match against our 17,967 keywords using text similarity
3. Assign to one or more of the 15 keyword groups
4. Tag with matching audience segments (A1-A12)

### 6.2 Cross-Reference Matrix

```
Scraped Content Topics
       │
       ├── Match to Keyword Groups (15 categories)
       │     └── Identify search volume potential
       │
       ├── Match to Audience Segments (A1-A12)
       │     └── Determine awareness stage → writing approach
       │
       ├── Match to Calculator Pages (104 calculators)
       │     └── Create internal linking opportunities
       │
       └── Gap Analysis
              └── Keywords with NO matching scraped content = content to create from scratch
```

### 6.3 Content Gap Identification

Compare:
- **Keyword list** (17,967 keywords) vs **scraped content topics**
- Find keywords with search volume >= 500/mo that have NO matching scraped content
- These gaps represent original content opportunities
- Prioritize by: `(search volume) x (CPC) x (1 / competition_score)`

### 6.4 Prioritization Formula

For each potential blog post:

```
Priority Score = (Monthly Search Volume / 1000)
               × (Average CPC / $1.00)
               × Content Availability Factor
               × Audience Match Factor

Where:
  Content Availability Factor:
    - Rich scraped content available: 1.5 (easy to write, lots of source material)
    - Some scraped content: 1.0
    - No scraped content (pure research): 0.5

  Audience Match Factor:
    - Targets top 3 segments (A1, A2, A4): 1.5
    - Targets mid segments: 1.0
    - Niche segment only: 0.7
```

### 6.5 Internal Cross-Linking Strategy

Every blog post should link to:
1. **Its matching calculator** (e.g., "How Much Concrete for a Driveway" links to `/concrete-driveway-calculator`)
2. **2-3 related blog posts** in the same category
3. **1-2 blog posts** from adjacent categories (e.g., concrete post links to fence calculator post)
4. **Provider directory** where relevant (e.g., "Find a concrete contractor near you")

Every calculator page should link to:
1. **3-5 related blog posts** that answer common questions
2. **Related calculators** (e.g., concrete slab links to concrete cost, concrete bags)
3. **Brand variant pages** if they exist

### 6.6 Estimated Posts Per Keyword Group

| Keyword Group | Blog Posts (How-To) | Blog Posts (Cost Guide) | Blog Posts (Comparison) | Blog Posts (FAQ/Tips) | Total |
|---------------|--------------------:|------------------------:|------------------------:|----------------------:|------:|
| Square Footage & Conversions | 30 | 10 | 15 | 50 | 105 |
| Concrete | 60 | 30 | 20 | 40 | 150 |
| Paint & Flooring | 50 | 25 | 25 | 40 | 140 |
| Roofing | 40 | 30 | 15 | 30 | 115 |
| Landscaping | 40 | 20 | 15 | 30 | 105 |
| Electrical | 30 | 10 | 10 | 40 | 90 |
| Deck & Fence | 30 | 15 | 15 | 25 | 85 |
| Brick & Masonry | 25 | 15 | 10 | 20 | 70 |
| Drywall & Insulation | 20 | 15 | 10 | 15 | 60 |
| Lumber | 20 | 10 | 10 | 15 | 55 |
| Misc Construction | 20 | 10 | 10 | 15 | 55 |
| Patio & Outdoor | 15 | 10 | 10 | 10 | 45 |
| Roofing Cost Extended | 5 | 20 | 5 | 5 | 35 |
| Flooring Extended | 5 | 15 | 5 | 5 | 30 |
| Concrete Cost Extended | 5 | 10 | 5 | 5 | 25 |
| **TOTALS** | **395** | **245** | **180** | **345** | **1,165** |

---

## 7. Blog Post Generation Pipeline

### 7.1 Blog Post Templates

#### Template A: How-To Guide (395 posts)

```markdown
---
title: "How to [Action] [Topic]: Step-by-Step Guide [Year]"
targetKeyword: "[primary keyword]"
wordCount: 1500-2500
---

## Quick Answer
[1-2 sentence direct answer to the keyword query]

## What You'll Need
- [Materials list with quantities]
- [Tools list]

## Step-by-Step Instructions
### Step 1: [Action]
[Detailed instructions with measurements]

### Step 2: [Action]
...

## Common Mistakes to Avoid
1. [Mistake] -- [Why it matters] -- [What to do instead]

## Calculator
[Embed or link to matching calculator]

## FAQ
### [Question matching long-tail keyword 1]
[Answer]

### [Question matching long-tail keyword 2]
[Answer]
```

#### Template B: Cost Breakdown Guide (245 posts)

```markdown
---
title: "[Project] Cost Calculator & Price Guide [Year]"
targetKeyword: "[cost keyword]"
wordCount: 1500-2000
---

## Average Cost
[Table: Low / Average / High costs per unit]

## Cost Factors
### 1. Materials
[Breakdown by material type]

### 2. Labor
[Regional labor rate ranges]

### 3. Project Size
[How scale affects cost per unit]

## Cost Calculator
[Embed or link to matching cost calculator]

## How to Save Money
1. [Tip]
2. [Tip]

## When to Hire a Pro vs DIY
[Decision matrix]

## FAQ
[Cost-related questions from keyword research]
```

#### Template C: Comparison Guide (180 posts)

```markdown
---
title: "[X] vs [Y]: Which Is Better for [Project]?"
targetKeyword: "[vs keyword]"
wordCount: 1200-1800
---

## Quick Comparison
[Table: Feature, X, Y, Winner]

## [X] Overview
[Pros, cons, best for]

## [Y] Overview
[Pros, cons, best for]

## Head-to-Head Comparison
### Cost
### Durability
### Installation Difficulty
### Appearance

## Our Recommendation
[Specific recommendation based on use case]

## Calculator
[Link to relevant calculator for both options]
```

#### Template D: FAQ / Tips Guide (345 posts)

```markdown
---
title: "[N] [Topic] Tips Every [Audience] Should Know"
targetKeyword: "[tip/faq keyword]"
wordCount: 1000-1500
---

## [Tip/FAQ 1]
[Answer with specifics]

## [Tip/FAQ 2]
[Answer with specifics]

...

## Tools & Calculators
[Links to relevant calculators]

## Related Reading
[Links to related how-to and cost guides]
```

### 7.2 Content Generation Workflow

For each blog post:

```
1. SELECT keyword + template
   └── From prioritized keyword list
   └── Match template type (how-to, cost, comparison, FAQ)

2. GATHER source material
   └── Pull matching scraped content from knowledge/construction/
   └── Pull matching YouTube transcripts
   └── Pull matching Reddit/Quora voice data
   └── Load focus group data for matched audience segment

3. GENERATE content brief
   └── Title, target keyword, word count target
   └── Source materials to reference (NOT copy)
   └── Awareness stage (from focus group)
   └── Calculators to link to
   └── Related posts to link to

4. WRITE draft
   └── vibe-content-writer agent
   └── Apply L1 (Schwartz awareness matching)
   └── Apply L4 (Ogilvy: factual, authoritative)
   └── Apply L5 (clear/concise writing rules)
   └── Use scraped content as KNOWLEDGE BASE, not source to copy
   └── Include specific measurements, code references, brand names

5. REVIEW
   └── vibe-content-reviewer agent
   └── Score on 8 dimensions (target: 7+ overall)
   └── Auto-approve at 7+, revision at <7

6. HUMANIZE
   └── vibe-humanizer agent
   └── Remove AI patterns (24 pattern categories)
   └── Add specificity, personality, opinions

7. SEO OPTIMIZE
   └── Add schema markup (Article, HowTo, FAQPage, BreadcrumbList)
   └── Optimize meta description
   └── Ensure internal links present
   └── Add image alt text

8. PUBLISH
   └── Push to BusinessPress via Laravel API
   └── Add to XML sitemap
   └── Submit to Google Search Console
```

### 7.3 How Scraped Content Gets Used

**CRITICAL: We do NOT copy scraped content.** It serves as a knowledge base:

| Scraped Data | How It's Used |
|-------------|---------------|
| Blog article text | Extract facts, measurements, techniques, code references. Rewrite in our voice. |
| YouTube transcripts | Extract step-by-step procedures, expert tips, real-world measurements. Attribute if quoting. |
| Reddit threads | Extract audience language patterns, common questions, real problems. Use for FAQ sections. |
| Quora answers | Extract expert perspectives, persuasion patterns, question framing. Use for outline structure. |
| Manufacturer guides | Extract product specs, coverage rates, application instructions. Cite as source. |

### 7.4 Quality Standards

From the content-review-procedures skill, each article is scored on:

1. **Awareness Match** (20%): Does content match reader's awareness stage?
2. **CTA Clarity** (15%): Clear link to calculator?
3. **Proof Density** (15%): Specific numbers, measurements, code references?
4. **Persuasion Application** (10%): Natural, not forced?
5. **Voice Consistency** (10%): Single expert voice throughout?
6. **AI Pattern Detection** (15%): Zero detectable AI patterns?
7. **SEO & Readability** (10%): Keyword placement, short paragraphs, scannable?
8. **Focus Group Alignment** (5%): Uses real audience language?

**Target:** 7.0+ overall score for auto-approval.

### 7.5 Schema Markup per Post Type

| Post Type | Schema Types | Rich Result Potential |
|-----------|-------------|---------------------|
| How-To Guide | `Article`, `HowTo`, `FAQPage`, `BreadcrumbList` | How-To steps in search results |
| Cost Guide | `Article`, `FAQPage`, `BreadcrumbList` | FAQ rich results |
| Comparison | `Article`, `FAQPage`, `BreadcrumbList` | FAQ rich results |
| FAQ/Tips | `Article`, `FAQPage`, `BreadcrumbList` | FAQ rich results |
| Calculator Page | `WebApplication`, `FAQPage`, `BreadcrumbList` | Software App rich result |

---

## 8. Technical Implementation

### 8.1 Crawl4AI Configuration for Bulk Scraping

Crawl4AI is running at `localhost:11235`. For bulk scraping:

```python
# Example API call to Crawl4AI
import requests

response = requests.post("http://localhost:11235/crawl", json={
    "urls": ["https://www.thisoldhouse.com/concrete/how-to-pour-concrete-slab"],
    "word_count_threshold": 100,
    "excluded_tags": ["nav", "footer", "header", "aside"],
    "css_selector": "article, .article-body, .entry-content, main",
    "bypass_cache": False
})
```

**Rate limiting plan:**
- 1 request per 3 seconds per domain
- Respect robots.txt (check before scraping)
- Maximum 50 pages per domain per hour
- Rotate between domains (scrape 10 from site A, then 10 from site B, etc.)
- Use cached responses where available

**Robots.txt compliance:**
Before scraping any domain, check `robots.txt`:
```bash
curl -s https://www.thisoldhouse.com/robots.txt | head -20
```

### 8.2 Storage Estimates

| Content Type | Count | Avg Size | Total |
|-------------|------:|--------:|------:|
| Scraped blog articles | 3,000 | 15 KB | 45 MB |
| YouTube transcripts | 500 | 30 KB | 15 MB |
| Reddit threads | 1,000 | 5 KB | 5 MB |
| Quora questions/answers | 300 | 8 KB | 2.4 MB |
| Manufacturer guides | 50 | 50 KB | 2.5 MB |
| Generated blog posts | 1,200 | 10 KB | 12 MB |
| **Total** | | | **~82 MB** |

Storage is trivially small. No concerns about disk space.

### 8.3 Convex Tracking Schema

Track scraping and content generation in Convex:

```
# Scrape tracking
scrapeJobs:create   → { source, url, status, scrapedAt, contentHash }
scrapeJobs:list     → { filter by source, status }
scrapeJobs:update   → { status: scraped|failed|skipped }

# Content pipeline tracking (already exists)
tasks:create        → { title, status, projectId, assignedTo, notes }
resources:create    → { projectId, resourceType, filePath, status, pipelineStage }
pipeline:acquireLock → { taskId, agent }
pipeline:completeStep → { taskId, agentName, qualityScore, resourceIds }
```

### 8.4 Parallelization Strategy

```
PHASE 1: SCRAPING (can run fully parallel by domain)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Agent 1:         │  │ Agent 2:         │  │ Agent 3:         │
│ This Old House   │  │ Family Handyman  │  │ YouTube          │
│ Bob Vila         │  │ Fine Homebuilding│  │ transcripts      │
│ Concrete Network │  │ The Spruce       │  │                  │
└─────────────────┘  └─────────────────┘  └─────────────────┘

PHASE 2: AUDIENCE RESEARCH (sequential per segment, but segments can run parallel)
┌─────────────────┐  ┌─────────────────┐
│ Agent 1:         │  │ Agent 2:         │
│ Segments A1-A6   │  │ Segments A7-A12  │
└─────────────────┘  └─────────────────┘

PHASE 3: CONTENT GENERATION (parallel by category)
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Agent 1:         │  │ Agent 2:         │  │ Agent 3:         │
│ Concrete posts   │  │ Roofing posts    │  │ Electrical posts │
│ (150 articles)   │  │ (115 articles)   │  │ (90 articles)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

Each agent runs independently with its own task queue in Convex. No file conflicts because each category writes to separate directories.

### 8.5 Publishing to BusinessPress

**[DECISION POINT]** How to publish to BusinessPress:
- Option A: Laravel API endpoint that accepts markdown + frontmatter → creates post
- Option B: Direct database insertion (less safe)
- Option C: File-based import (write to a watched directory)
- Option D: WordPress-compatible XML import

Recommendation: **Option A** -- build a simple authenticated API endpoint in the Laravel app:
```
POST /api/posts
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
  "title": "...",
  "slug": "...",
  "content": "...(markdown)...",
  "category": "concrete",
  "tags": ["calculator", "diy"],
  "meta_description": "...",
  "schema_markup": "...(JSON-LD)...",
  "status": "draft"
}
```

---

## 9. Scale Estimates

### 9.1 Blog Posts Per Keyword Group

| Keyword Group | Blog Posts | Avg Monthly Vol/Post | Total Monthly Vol |
|---------------|----------:|---------------------:|------------------:|
| Square Footage & Conversions | 105 | 500-5,000 | 250K-500K |
| Concrete (all) | 175 | 500-5,000 | 300K-800K |
| Paint & Flooring (all) | 170 | 200-2,000 | 100K-300K |
| Roofing (all) | 150 | 200-5,000 | 200K-500K |
| Landscaping | 105 | 200-2,000 | 80K-200K |
| Electrical | 90 | 100-2,000 | 50K-150K |
| Deck & Fence | 85 | 200-2,000 | 60K-150K |
| Brick & Masonry | 70 | 100-1,000 | 30K-70K |
| Drywall & Insulation | 60 | 200-2,000 | 40K-100K |
| Lumber | 55 | 200-2,000 | 30K-100K |
| Misc Construction | 55 | 100-1,000 | 20K-50K |
| Patio & Outdoor | 45 | 50-500 | 10K-25K |
| **TOTAL** | **~1,165** | | **~1.2M-2.9M/mo** |

### 9.2 Timeline Estimates

| Phase | Activity | Duration | Output |
|:-----:|----------|:--------:|--------|
| 0 | Setup: project, Convex records, scraping scripts | 2-3 days | Infrastructure ready |
| 1 | Scraping: blogs, YouTube, Reddit, Quora | 5-7 days | ~4,500 source documents |
| 2 | Audience research: focus groups for all segments | 3-5 days | 12-15 focus group profiles |
| 3 | Content generation: Batch 1 (concrete, 175 posts) | 7-10 days | 175 blog posts |
| 4 | Content generation: Batch 2 (roofing, 150 posts) | 7-10 days | 150 blog posts |
| 5 | Content generation: Batch 3 (paint/flooring, 170 posts) | 7-10 days | 170 blog posts |
| 6 | Content generation: Batch 4 (sq footage, landscaping, 210 posts) | 7-10 days | 210 blog posts |
| 7 | Content generation: Batch 5 (remaining 460 posts) | 14-20 days | 460 blog posts |
| 8 | SEO optimization: schema, linking, sitemap | 3-5 days | All posts optimized |
| | **Total** | **~50-80 days** | **~1,165 blog posts** |

### 9.3 Cost Estimates

| Resource | Unit Cost | Quantity | Total |
|----------|----------|---------|------:|
| Claude API (content generation) | ~$0.03-0.05 per article | 1,165 articles | $35-60 |
| Claude API (review + humanize) | ~$0.02-0.03 per article | 1,165 articles | $23-35 |
| Claude API (audience research) | ~$0.10-0.20 per segment | 12 segments | $1.20-2.40 |
| Crawl4AI | Self-hosted (free) | -- | $0 |
| yt-dlp | Free | -- | $0 |
| Brave Search API | Free tier (2,000/mo) or $3/mo | ~500 queries | $0-3 |
| **Total API cost** | | | **~$60-100** |

---

## 10. Phase Ordering & Rollout

### Phase 0: Foundation (Days 1-3)

**Tasks:**
1. Create FatStud project in Convex (`projects:create`)
2. Create product record for FatStud calculators (`products:create`)
3. Build scraping scripts:
   - `scrape_blogs.py` -- Crawl4AI wrapper for construction blogs
   - `scrape_youtube.py` -- youtube_research.py wrapper for bulk channel scraping
   - `scrape_reddit.py` -- Reddit MCP wrapper for subreddit extraction
   - `scrape_quora.py` -- quora_research.py wrapper for construction topics
4. Create directory structure: `knowledge/construction/` (see section 3.3)
5. Create scrape tracking index: `knowledge/construction/_scraped-index.json`
6. **[DECISION POINT]** Create BusinessPress API endpoint for post import

**Acceptance criteria:**
- [ ] FatStud project exists in Convex
- [ ] All scraping scripts run and produce output
- [ ] Directory structure created
- [ ] At least 1 test scrape from each source type completes

### Phase 1: Scraping (Days 4-10)

**Priority order by value density:**

| Day | Source | Target | Est. Articles |
|:---:|--------|--------|:-------------:|
| 4-5 | This Old House | Construction how-tos | 500 |
| 5-6 | Concrete Network | Concrete-specific content | 200 |
| 6-7 | Family Handyman, Bob Vila | DIY guides | 500 |
| 7-8 | YouTube (Essential Craftsman, Matt Risinger, Sparky Channel) | Transcripts | 200 |
| 8-9 | Reddit (r/HomeImprovement, r/Construction, r/Electricians, r/Concrete, r/Roofing) | Thread extracts | 500 |
| 9-10 | Fine Homebuilding, JLC, manufacturer guides | Pro-grade content | 300 |
| 10 | Quora construction topics | Q&A voice data | 200 |

**Acceptance criteria:**
- [ ] 2,000+ source documents scraped and stored
- [ ] All 10 blog sources attempted
- [ ] All 12 YouTube channels attempted
- [ ] All 10 Reddit subreddits attempted
- [ ] Scraped index updated with status for each source
- [ ] No robots.txt violations

### Phase 2: Audience Research (Days 11-15)

**Tasks:**
1. Run `vibe-audience-researcher` for construction audiences
2. Use Reddit and Quora scraped data as input
3. Generate 12-15 focus group profiles (see section 5.1)
4. Store in Convex via `focusGroupStaging:createBatch`
5. Human review and approval of focus groups

**Acceptance criteria:**
- [ ] 12+ focus groups created and stored in Convex
- [ ] Each focus group has all required fields (see section 4.6)
- [ ] Language patterns sourced from actual Reddit/Quora/YouTube data
- [ ] All 12 audience segments (A1-A12) covered
- [ ] Human has reviewed and approved focus groups

### Phase 3: Content Generation -- Batch 1: Concrete (Days 16-25)

**Why concrete first:**
- Highest total search volume: 6.7M/mo
- Second-highest CPC
- Most scraped content available (Concrete Network alone has 200+ articles)
- Maps to 8 hero calculators (all at 50K+ monthly searches)

**Tasks per blog post:**
1. Select keyword and template type
2. Pull matching source material from `knowledge/construction/`
3. Generate content brief
4. Write article (vibe-content-writer)
5. Review (vibe-content-reviewer)
6. Humanize (vibe-humanizer)
7. Add schema markup
8. Store in `projects/fatstud/campaigns/concrete-content/drafts/`

**Sub-batches:**
- Batch 1a: How-To guides (60 posts) -- "how to pour concrete slab", "how to mix concrete", etc.
- Batch 1b: Cost guides (30 posts) -- "concrete cost per yard", "stamped concrete cost", etc.
- Batch 1c: Comparisons (20 posts) -- "concrete vs asphalt", "concrete vs pavers", etc.
- Batch 1d: FAQ/Tips (40 posts) -- "concrete curing time", "concrete mix ratios", etc.
- Batch 1e: Brand guides (15 posts) -- "Quikrete calculator guide", "Sakrete vs Quikrete", etc.

### Phase 4: Content Generation -- Batch 2: Roofing (Days 26-35)

**Why roofing second:**
- Highest CPC of any category ($4.60-$122.89)
- 8 of top 20 highest-CPC keywords are roofing
- Even low-traffic roofing pages are revenue goldmines
- Roofing contractor lead gen potential

**Sub-batches:**
- Batch 2a: How-To guides (40 posts) -- "how to measure roof", "how to calculate shingles", etc.
- Batch 2b: Cost guides (50 posts) -- "roof replacement cost", "metal roofing cost", etc.
- Batch 2c: Comparisons (15 posts) -- "metal vs shingle roof", "TPO vs EPDM", etc.
- Batch 2d: FAQ/Tips (30 posts) -- "roof pitch explained", "when to replace roof", etc.
- Batch 2e: Estimate guides (15 posts) -- "how to read a roofing estimate", "roofing estimate checklist", etc.

### Phase 5: Content Generation -- Batch 3: Paint & Flooring (Days 36-45)

### Phase 6: Content Generation -- Batch 4: Sq Footage + Landscaping (Days 46-55)

### Phase 7: Content Generation -- Batch 5: All Remaining (Days 56-75)

Covers: Electrical, Deck & Fence, Brick & Masonry, Drywall & Insulation, Lumber, Misc Construction, Patio & Outdoor.

### Phase 8: SEO Optimization & Publishing (Days 76-80)

**Tasks:**
1. Generate schema markup for all 1,165 posts
2. Build internal linking graph (each post links to 3-5 other posts + 1-2 calculators)
3. Generate XML sitemap
4. Publish to BusinessPress (draft status initially)
5. Submit sitemap to Google Search Console
6. QA review of published pages (spot-check 10% for rendering issues)

---

## 11. Decision Points Requiring Human Input

These items cannot be resolved by an automated agent. A human must decide:

### DP-1: BusinessPress Publishing API
**Question:** How should blog posts be pushed to BusinessPress?
**Options:** Laravel API endpoint, database insertion, file import, or XML import
**Recommendation:** Laravel API endpoint (see section 8.5)
**Impact:** Blocks Phase 0 completion
**Owner:** Vuk

### DP-2: Content Publication Cadence
**Question:** Should all 1,165 posts go live at once, or be dripped over time?
**Options:**
- A) All at once (maximum SEO surface area immediately)
- B) Drip 10-20 posts/day over 2-3 months (more natural to Google)
- C) Batch by category (all concrete at once, then all roofing, etc.)
**Recommendation:** Option C -- publish one full category at a time, one category per week
**Impact:** Affects Phase 8 timeline
**Owner:** Vuk

### DP-3: Author Attribution
**Question:** Should blog posts have author names? If so, what names?
**Options:**
- A) No author (just "FatStud Team")
- B) Fictional expert authors per category (e.g., "Mike Rivera, Licensed Electrician")
- C) Real expert names (requires hiring/partnering)
**Recommendation:** Option A for now, upgrade to C later when revenue justifies it
**Impact:** Affects blog post template and schema markup
**Owner:** Vuk

### DP-4: Image Strategy
**Question:** Should blog posts include images? If so, where from?
**Options:**
- A) No images initially (text-only, fastest to generate)
- B) Stock photos from free sources (Unsplash, Pexels)
- C) AI-generated images per post (adds cost and time)
- D) Diagrams/illustrations from scraped content (attribution required)
**Recommendation:** Option A for initial launch, add Option B in second pass
**Impact:** Affects content generation time and quality score
**Owner:** Vuk

### DP-5: Calculator Integration Depth
**Question:** How deeply should blog posts integrate with calculators?
**Options:**
- A) Simple text link to calculator page
- B) Embedded calculator widget within blog post
- C) Pre-filled calculator link (e.g., `/concrete-calculator?length=20&width=20&depth=4`)
**Recommendation:** Option C -- pre-filled links based on the blog post's example values
**Impact:** Requires calculator URL parameter support
**Owner:** Vuk

### DP-6: Provider Directory Integration
**Question:** Should blog posts link to the provider directory?
**Options:**
- A) No provider links (pure information)
- B) Generic "Find a contractor" CTA
- C) Category-specific provider links (e.g., concrete posts link to concrete contractors)
**Recommendation:** Option C when provider directory is populated
**Impact:** Affects CTA strategy and potential lead gen revenue
**Owner:** Vuk

### DP-7: Convex Project Setup
**Question:** Does a FatStud project already exist in Convex, or does one need to be created?
**Action:** Check via `npx convex run projects:list --url http://localhost:3210`
**Impact:** Blocks Phase 0
**Owner:** Vuk

---

## 12. Risk Register

| # | Risk | Probability | Impact | Mitigation |
|:-:|------|:----------:|:------:|------------|
| R1 | Google penalizes site for rapid content publication | Medium | High | Drip content over time (DP-2), ensure unique value per page, avoid thin content |
| R2 | Scraped content is too thin to base articles on | Low | Medium | Use multiple sources per topic, flag topics with insufficient source material for manual writing |
| R3 | AI-generated content detected by Google | Medium | High | Humanizer pass on every article, add specific measurements/code references, inject expert opinions |
| R4 | Rate limiting during scraping blocks progress | Medium | Low | Respect robots.txt, use delays, rotate domains, cache responses |
| R5 | Content quality drops below 7.0 threshold at scale | Medium | Medium | Review first 50 articles manually, tune prompts, adjust templates |
| R6 | Duplicate content across similar keyword variations | Medium | High | Deduplicate keywords before generating, canonical tags, topic consolidation |
| R7 | Calculator pages not ready when blog posts reference them | Low | Medium | Build calculators in parallel, use placeholder links initially |
| R8 | Focus group research produces inaccurate audience profiles | Low | Medium | Validate against actual Reddit/forum data, human review required |
| R9 | BusinessPress API not ready when content is generated | Medium | Medium | Store all content as markdown files, bulk import later |
| R10 | Crawl4AI goes down during scraping phase | Low | Low | Docker auto-restarts, manual restart if needed, can also use Firecrawl as backup |

---

## Appendix A: File Path Reference

| Resource | Absolute Path |
|----------|---------------|
| This pre-plan | `/var/www/vibe-marketing/rust/construction-calculators/content-factory-preplan.md` |
| Master keyword summary | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/MASTER-SUMMARY.md` |
| Autocomplete summary | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/keyword-summary.md` |
| Calculator comparison | `/var/www/vibe-marketing/rust/construction-calculators/calculator-comparison-analysis.md` |
| Category analysis files | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/*-latest-analysis.md` |
| Autocomplete data | `/var/www/vibe-marketing/rust/construction-calculators/keyword-research/autocomplete-suggestions.txt` |
| Audience research skill | `/var/www/vibe-marketing/.claude/skills/audience-research-procedures/SKILL.md` |
| Content writing skill | `/var/www/vibe-marketing/.claude/skills/content-writing-procedures/SKILL.md` |
| Content review skill | `/var/www/vibe-marketing/.claude/skills/content-review-procedures/SKILL.md` |
| Humanizer skill | `/var/www/vibe-marketing/.claude/skills/humanizer/SKILL.md` |
| YouTube research skill | `/var/www/vibe-marketing/.claude/skills/youtube-research/SKILL.md` |
| Quora research skill | `/var/www/vibe-marketing/.claude/skills/quora-research/SKILL.md` |
| Google suggest skill | `/var/www/vibe-marketing/.claude/skills/google-suggest-research/SKILL.md` |
| Programmatic SEO skill | `/var/www/vibe-marketing/.claude/skills/programmatic-seo/SKILL.md` |
| Schema markup skill | `/var/www/vibe-marketing/.claude/skills/schema-markup/SKILL.md` |
| Content strategy skill | `/var/www/vibe-marketing/.claude/skills/content-strategy/SKILL.md` |
| MCP configuration | `/var/www/vibe-marketing/.mcp.json` |
| Docker compose | `/var/www/vibe-marketing/docker-compose.yml` |
| Platform docs | `/var/www/vibe-marketing/CLAUDE.md` |
| Existing projects | `/var/www/vibe-marketing/projects/` |
| Knowledge base (target) | `/var/www/vibe-marketing/knowledge/construction/` |
| Content output (target) | `/var/www/vibe-marketing/projects/fatstud/` |

## Appendix B: Quick-Start Commands for a Fresh Session

```bash
# 1. Verify infrastructure
curl -s http://localhost:11235/health  # Crawl4AI
npx convex run projects:list --url http://localhost:3210  # Convex

# 2. Read this pre-plan
cat /var/www/vibe-marketing/rust/construction-calculators/content-factory-preplan.md

# 3. Read keyword research
cat /var/www/vibe-marketing/rust/construction-calculators/keyword-research/MASTER-SUMMARY.md

# 4. Check existing project
npx convex run projects:list --url http://localhost:3210 | grep -i fatstud

# 5. Read relevant skills
cat /var/www/vibe-marketing/.claude/skills/audience-research-procedures/SKILL.md
cat /var/www/vibe-marketing/.claude/skills/content-writing-procedures/SKILL.md

# 6. Test scraping
python /var/www/vibe-marketing/.claude/skills/youtube-research/scripts/youtube_research.py \
    --search "how to pour concrete slab" --max-videos 2 --extract metadata --output json

python /var/www/vibe-marketing/.claude/skills/quora-research/scripts/quora_questions.py \
    --topic "concrete calculator" --max-questions 5 --output json

python /var/www/vibe-marketing/.claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "concrete calculator" --expand-questions --output json
```

## Appendix C: Category-Specific Scraping Targets

### Concrete Category (Priority 1)

**Blog sources:**
- concretenetwork.com (200+ articles on concrete techniques)
- thisoldhouse.com/concrete
- familyhandyman.com/project/concrete/
- quikrete.com/diy (manufacturer guides)

**YouTube:**
- Essential Craftsman: "concrete" playlist
- Mike Day Concrete: mixing, finishing, stamping
- This Old House: concrete projects

**Reddit:**
- r/Concrete (30K members, highly technical)
- r/HomeImprovement (concrete-tagged posts)

**Keywords to match:** 2,834 concrete keywords + 125 concrete cost keywords = 2,959

### Roofing Category (Priority 2)

**Blog sources:**
- finehomebuilding.com/roofing
- thisoldhouse.com/roofing
- gaf.com/en-us/for-professionals (manufacturer)
- owenscorning.com/roofing

**YouTube:**
- Roof It Right (100+ tutorials)
- Dmitry Lipinskiy (Roofing Insights)
- This Old House roofing projects

**Reddit:**
- r/Roofing (50K members)
- r/HomeImprovement (roofing-tagged)

**Keywords to match:** 1,922 roofing keywords + 410 roofing cost keywords = 2,332

### Electrical Category (Priority 3)

**Blog sources:**
- electriciantalk.com (forum, but scrape public threads)
- ecmweb.com (trade publication)
- nfpa.org/nec (code reference -- limited scraping)
- southwire.com/calculator-hub (voltage drop reference)

**YouTube:**
- Sparky Channel (200+ tutorials)
- ElectricianU (apprenticeship content)
- Roger Wakefield (some electrical content)

**Reddit:**
- r/Electricians (300K members, very active)
- r/AskElectricians (Q&A format)

**Keywords to match:** 1,753 electrical keywords

---

*End of pre-plan. This document is 1,100+ lines and contains all information needed for a fresh Claude Code session to create a detailed task-by-task implementation plan.*
