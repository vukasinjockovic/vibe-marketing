# Implementation Report: vibe-audience-researcher Agent Skill
Generated: 2026-02-11T20:05:00Z

## Task
Build the vibe-audience-researcher agent skill -- a comprehensive audience intelligence agent that researches markets, identifies audience segments, builds detailed focus group profiles with real language patterns, and stages structured data for human review.

## Files Created

### Skill Core
- `.claude/skills/audience-research-procedures/SKILL.md` -- Comprehensive agent instructions (340+ lines). Covers 8-step execution protocol: lock acquisition, context loading, service resolution, 4-phase research workflow, segmentation, profile generation, output/staging. Includes graceful degradation matrix, error handling, memory protocol, timing guidelines, and anti-patterns.
- `.claude/skills/audience-research-procedures/vibe-audience-researcher.md` -- Agent identity file. Defines opus model, pipeline position (Step 1 of audience-discovery), service dependencies with degradation behavior, input/output contracts, and cost justification.

### Scripts
- `.claude/skills/audience-research-procedures/scripts/scrape_reddit.py` -- Reddit API wrapper. Accepts subreddits + queries, returns JSON posts with title/body/comments/upvotes. Supports OAuth Reddit API and generic scraping services. Includes language pattern extraction (identity markers, frustrations, problem descriptions). Gracefully returns empty results when service unavailable.
- `.claude/skills/audience-research-procedures/scripts/scrape_reviews.py` -- Review site scraper. Accepts product name + competitor URLs. Supports Crawl4AI (self-hosted) and Firecrawl (cloud). Extracts themes: satisfaction, pain points, emotional expressions, objection patterns, demographic signals, competitor mentions. Graceful degradation.
- `.claude/skills/audience-research-procedures/scripts/analyze_competitors.py` -- Competitor site analysis. Accepts competitor URLs. Extracts: headlines, value props, testimonials, audience signals, pricing signals, FAQ topics, CTA text, messaging angles. Generates cross-competitor summary with recurring themes.
- `.claude/skills/audience-research-procedures/scripts/compile_audience_doc.py` -- Document compiler. Takes research JSON, generates comprehensive markdown document following the focus-group-template format. Produces table of contents, all profiles, and outputs JSON summary.

### References
- `.claude/skills/audience-research-procedures/references/research-methodology.md` -- 8-phase step-by-step protocol with timing estimates (45-75 min total).
- `.claude/skills/audience-research-procedures/references/focus-group-template.md` -- Complete template with all fields, minimums, and quality checklist.
- `.claude/skills/audience-research-procedures/references/focus-group-schema.json` -- JSON Schema matching Convex focusGroups table (all fields: required core + optional enrichment).
- `.claude/skills/audience-research-procedures/references/psychographic-frameworks.md` -- Schwartz Awareness (5 stages), Market Sophistication (5 stages), VALS Framework (8 types), Maslow's Hierarchy (5 levels) with application guidance.
- `.claude/skills/audience-research-procedures/references/data-sources.md` -- 7 source categories: Reddit, competitor websites, review sites, forums, social media, industry reports, customer support data. Each with access methods and extraction guidance.
- `.claude/skills/audience-research-procedures/references/example-output.md` -- Excerpt of 3 focus groups from the GymZilla fitness doc showing expected depth and format.

## Validation Results

### Script Compilation
- `scrape_reddit.py`: Compiles successfully
- `scrape_reviews.py`: Compiles successfully
- `analyze_competitors.py`: Compiles successfully
- `compile_audience_doc.py`: Compiles successfully

### Functional Tests
- `compile_audience_doc.py`: Tested with sample data, produced valid markdown output (2570 chars, 1 group, 1 category)
- `scrape_reddit.py`: Tested graceful degradation -- returns `{"status": "unavailable"}` when service not configured
- All scripts use only stdlib dependencies (json, subprocess, sys, argparse, os, re, datetime) + optional `requests`

### File Permissions
- All 4 scripts: chmod +x (executable)

### Schema Validation
- `focus-group-schema.json`: Valid JSON, matches Convex focusGroups table structure

## Design Decisions

1. **Scripts use resolve_service.py, not direct API calls**: All external service access goes through the service registry at `/var/www/vibe-marketing/scripts/resolve_service.py`. This ensures the agent respects configured services and degrades gracefully.

2. **Graceful degradation at script level**: Each script exits with code 0 and returns `{"status": "unavailable"}` when its required service is not configured. This lets the agent check the status field and skip that research phase without error handling in the SKILL.md.

3. **Scripts do extraction, agent does synthesis**: The Python scripts extract and structure raw data. The opus agent (following SKILL.md) does the deep synthesis, segmentation, and profile writing. This division keeps scripts simple and leverages the model's strength for creative research synthesis.

4. **Language pattern extraction in scrape_reddit.py**: The script pre-extracts identity markers, frustrations, and problem descriptions from Reddit posts. This gives the agent a head start but the agent should still read raw posts for nuance.

5. **Staging with completeness tracking**: Every focus group goes through focusGroupStaging with completenessScore and missingFields, enabling the dashboard to show humans which profiles need more work.

6. **Multiple scraping service support**: Each scraping script supports Crawl4AI (self-hosted), Firecrawl (cloud), and generic scraping services, matching the platform's capability-first service architecture.

## Directory Structure

```
.claude/skills/audience-research-procedures/
├── SKILL.md                              (340+ lines, comprehensive agent SOP)
├── vibe-audience-researcher.md           (agent identity, pipeline position)
├── scripts/
│   ├── scrape_reddit.py                  (Reddit API wrapper, 280 lines)
│   ├── scrape_reviews.py                 (Review scraper, 260 lines)
│   ├── analyze_competitors.py            (Competitor analyzer, 270 lines)
│   └── compile_audience_doc.py           (Document compiler, 245 lines)
└── references/
    ├── research-methodology.md           (8-phase protocol)
    ├── focus-group-template.md           (profile template + checklist)
    ├── focus-group-schema.json           (JSON schema for Convex)
    ├── psychographic-frameworks.md       (4 frameworks)
    ├── data-sources.md                   (7 source categories)
    └── example-output.md                 (3 GymZilla examples)
```

## Notes
- The SKILL.md is intentionally verbose (340+ lines) because this is an opus-model agent where thoroughness is worth the context cost
- All scripts use no exotic dependencies -- just requests (commonly available) plus stdlib
- The focus-group-schema.json was generated directly from reading convex/schema.ts lines 92-192
- The staging table integration uses focusGroupStaging:createBatch for efficient batch writes
