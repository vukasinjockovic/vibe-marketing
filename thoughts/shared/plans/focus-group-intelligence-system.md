# Feature Plan: Focus Group Intelligence System
Created: 2026-02-11
Author: architect-agent

## Overview

The Focus Group Intelligence System transforms audience research from a one-time manual process into an automated, living intelligence pipeline. It provides two primary flows: **Flow A (0-to-1)** researches and generates focus groups from scratch for a new product using web scraping, competitor analysis, and social listening; **Flow B (0.5-to-1)** parses an existing audience research document into structured Convex records and enriches them. Both flows converge into a review-and-approve dashboard experience, after which the system continuously enriches focus groups through a weekly heartbeat and agent-triggered updates.

## Requirements

- [ ] Flow A: Generate 10-30 focus groups from scratch given product context
- [ ] Flow B: Parse uploaded .md/.docx/.pdf/.txt into structured focus groups
- [ ] Fuzzy matching: detect existing focus groups to enrich vs. create new
- [ ] Enrichment tracking: audit trail per field (who changed what, when, confidence)
- [ ] Dashboard: review/approve extracted groups before import
- [ ] Dashboard: enrichment progress visualization per focus group
- [ ] Dashboard: trigger research or import from the product audiences page
- [ ] Pipeline integration: focus group pipeline works through existing task/pipeline system
- [ ] Batch Convex operations: createBatch, enrichBatch, findByName
- [ ] Three new agent skills: audience-parser, audience-researcher, audience-enricher
- [ ] Weekly enrichment heartbeat via vibe-audience-enricher

---

## 1. System Design

### Architecture

```
                    Dashboard (Nuxt 3)
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
     [Import Doc]  [Research]    [Manual Create]
           │             │             │
           ▼             ▼             │
    audience-parser  audience-        │
           │         researcher       │
           ▼             │            │
     ┌─────┴─────┐      │            │
     │ Parse to   │      ▼            │
     │ staging    │  Generate doc     │
     │ (preview)  │  + parse to       │
     └─────┬─────┘  staging           │
           │             │            │
           └──────┬──────┘            │
                  ▼                   │
         Review & Approve             │
         (Dashboard UI)               │
                  │                   │
                  ▼                   ▼
          focusGroups:createBatch  focusGroups:create
          focusGroups:enrichBatch
                  │
                  ▼
         audience-enricher
         (weekly heartbeat +
          triggered enrichment)
                  │
                  ▼
          focusGroups:enrich
          (with audit trail)
```

### Data Flow: Flow A (0 to 1)

1. User navigates to Product -> Audiences -> clicks "Research Audiences"
2. Dashboard creates a task using the "Audience Discovery" pipeline (already seeded)
3. **Step 1 - vibe-audience-researcher** (opus):
   a. Reads product context from Convex (whatItIs, features, targetMarket, competitors, USPs)
   b. Uses web_search (Brave) to research the market
   c. Optionally uses web_scraping (Firecrawl/Crawl4AI) for competitor sites
   d. Optionally uses social_scraping_reddit (Reddit API) for audience language
   e. Generates a comprehensive markdown audience intelligence document
   f. Saves document to filesystem: `projects/{slug}/research/audience-intelligence.md`
   g. Saves document to Convex documents table (type: "audience_doc")
   h. Parses the document into structured JSON focus groups
   i. Writes each group to `focusGroupStaging` table (status: "pending_review")
   j. Completes pipeline step
4. **Step 2 - vibe-audience-enricher** (sonnet):
   a. Reads all staged groups from focusGroupStaging for this task
   b. For each group, fills enrichment fields (awarenessStage, purchaseBehavior, etc.)
   c. Updates staging records with enrichment data
   d. Completes pipeline step
5. Dashboard shows notification: "18 focus groups ready for review"
6. User reviews in dashboard -> approve/edit/reject each group
7. "Import Approved" -> `focusGroups:importFromStaging` moves approved groups to focusGroups table

### Data Flow: Flow B (0.5 to 1)

1. User navigates to Product -> Audiences -> clicks "Import from Document"
2. User uploads file (.md, .docx, .pdf, .txt) via dashboard file input
3. File is saved to: `projects/{slug}/uploads/audience-{timestamp}.{ext}`
4. Dashboard creates a task using the "Document Import" pipeline (new preset)
5. **Step 1 - vibe-audience-parser** (sonnet):
   a. Reads the uploaded file
   b. If .docx: converts to markdown via pandoc
   c. If .pdf: extracts text via Python pdf library
   d. Identifies distinct audience segments using structural parsing
   e. For each segment, extracts all fields matching focusGroups schema
   f. Runs fuzzy matching against existing focus groups (by product):
      - Exact name match -> mark as "enrich_existing"
      - Nickname match -> mark as "enrich_existing"
      - Similarity > 0.8 (normalized Levenshtein on name+nickname) -> mark as "possible_match"
      - No match -> mark as "create_new"
   g. Writes each group to focusGroupStaging with match status
   h. Flags groups with missing required fields as "needs_enrichment"
   i. Completes pipeline step
6. **Step 2 - vibe-audience-enricher** (sonnet):
   a. Same as Flow A step 2
7. Dashboard review flow (same as Flow A steps 5-7)
8. For "enrich_existing" groups: `focusGroups:enrichFromStaging` merges new data into existing records

---

## 2. Convex Changes

### 2a. New Table: focusGroupStaging

This is the staging area where parsed/generated focus groups wait for human review before being committed to the production focusGroups table.

```typescript
// Add to schema.ts after focusGroups table

focusGroupStaging: defineTable({
  // Context
  taskId: v.id("tasks"),
  productId: v.id("products"),
  projectId: v.id("projects"),
  sourceDocumentId: v.optional(v.id("documents")),

  // Match resolution
  matchStatus: v.union(
    v.literal("create_new"),         // No existing match found
    v.literal("enrich_existing"),    // Exact match on name/nickname
    v.literal("possible_match"),     // Fuzzy match, needs human decision
    v.literal("skip")               // User decided to skip
  ),
  matchedFocusGroupId: v.optional(v.id("focusGroups")),
  matchConfidence: v.optional(v.number()),  // 0.0-1.0
  matchReason: v.optional(v.string()),      // "exact_name", "nickname_match", "fuzzy_0.85"

  // Review status
  reviewStatus: v.union(
    v.literal("pending_review"),
    v.literal("approved"),
    v.literal("rejected"),
    v.literal("edited"),       // Approved after human edits
    v.literal("imported")      // Successfully written to focusGroups
  ),
  reviewNotes: v.optional(v.string()),
  reviewedAt: v.optional(v.number()),

  // Completeness tracking
  completenessScore: v.number(),         // 0.0-1.0, percentage of fields filled
  missingFields: v.array(v.string()),    // ["contentPreferences", "purchaseBehavior"]
  needsEnrichment: v.boolean(),

  // All focusGroup fields (same as focusGroups table but all optional except name)
  number: v.optional(v.number()),
  name: v.string(),
  nickname: v.optional(v.string()),
  category: v.optional(v.string()),
  overview: v.optional(v.string()),
  demographics: v.optional(v.object({
    ageRange: v.string(),
    gender: v.string(),
    income: v.string(),
    lifestyle: v.string(),
    triggers: v.array(v.string()),
  })),
  psychographics: v.optional(v.object({
    values: v.array(v.string()),
    beliefs: v.array(v.string()),
    lifestyle: v.string(),
    identity: v.string(),
  })),
  coreDesires: v.optional(v.array(v.string())),
  painPoints: v.optional(v.array(v.string())),
  fears: v.optional(v.array(v.string())),
  beliefs: v.optional(v.array(v.string())),
  objections: v.optional(v.array(v.string())),
  emotionalTriggers: v.optional(v.array(v.string())),
  languagePatterns: v.optional(v.array(v.string())),
  ebookAngles: v.optional(v.array(v.string())),
  marketingHooks: v.optional(v.array(v.string())),
  transformationPromise: v.optional(v.string()),
  source: v.optional(v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual"))),

  // Enrichment fields (same optionals as focusGroups)
  awarenessStage: v.optional(v.union(
    v.literal("unaware"), v.literal("problem_aware"), v.literal("solution_aware"),
    v.literal("product_aware"), v.literal("most_aware")
  )),
  awarenessConfidence: v.optional(v.union(v.literal("high"), v.literal("medium"), v.literal("low"))),
  awarenessStageSource: v.optional(v.union(v.literal("auto"), v.literal("manual"))),
  awarenessSignals: v.optional(v.object({
    beliefsSignal: v.optional(v.string()),
    objectionsSignal: v.optional(v.string()),
    languageSignal: v.optional(v.string()),
  })),
  contentPreferences: v.optional(v.object({
    preferredFormats: v.optional(v.array(v.string())),
    attentionSpan: v.optional(v.string()),
    tonePreference: v.optional(v.string()),
  })),
  influenceSources: v.optional(v.object({
    trustedVoices: v.optional(v.array(v.string())),
    mediaConsumption: v.optional(v.array(v.string())),
    socialPlatforms: v.optional(v.array(v.string())),
  })),
  purchaseBehavior: v.optional(v.object({
    buyingTriggers: v.optional(v.array(v.string())),
    priceRange: v.optional(v.string()),
    decisionProcess: v.optional(v.string()),
    objectionHistory: v.optional(v.array(v.string())),
  })),
  competitorContext: v.optional(v.object({
    currentSolutions: v.optional(v.array(v.string())),
    switchMotivators: v.optional(v.array(v.string())),
  })),
  sophisticationLevel: v.optional(v.union(
    v.literal("stage1"), v.literal("stage2"), v.literal("stage3"),
    v.literal("stage4"), v.literal("stage5")
  )),
  communicationStyle: v.optional(v.object({
    formalityLevel: v.optional(v.string()),
    humorReceptivity: v.optional(v.string()),
    storyPreference: v.optional(v.string()),
    dataPreference: v.optional(v.string()),
  })),
  seasonalContext: v.optional(v.object({
    peakInterestPeriods: v.optional(v.array(v.string())),
    lifeEvents: v.optional(v.array(v.string())),
    cyclicalBehaviors: v.optional(v.array(v.string())),
  })),
  negativeTriggers: v.optional(v.object({
    dealBreakers: v.optional(v.array(v.string())),
    offensiveTopics: v.optional(v.array(v.string())),
    toneAversions: v.optional(v.array(v.string())),
  })),
  researchNotes: v.optional(v.string()),
}).index("by_task", ["taskId"])
  .index("by_product", ["productId"])
  .index("by_project", ["projectId"])
  .index("by_review_status", ["reviewStatus"]),
```

### 2b. New Convex Module: convex/focusGroupStaging.ts

```
Functions to implement:

// Queries
listByTask(taskId)           -> All staging records for a task
listByProduct(productId)     -> All staging records for a product
listPendingReview(taskId)    -> Only pending_review records
get(id)                      -> Single staging record
getSummary(taskId)           -> { total, pending, approved, rejected, needsEnrichment }

// Mutations
createFromParsed(data)       -> Insert a single parsed focus group
createBatch(groups[])        -> Insert multiple parsed focus groups at once
updateReviewStatus(id, status, notes?)  -> Approve/reject/edit
updateFields(id, fields)     -> Update any focus group fields (for human edits in review)
bulkApprove(ids[])           -> Approve multiple at once
bulkReject(ids[])            -> Reject multiple at once
```

### 2c. New Functions in convex/focusGroups.ts

```
// New queries
findByName(productId, name)  -> Find by exact name match within product
findByNickname(productId, nickname) -> Find by exact nickname match within product
searchByName(productId, query) -> Fuzzy search (collect all for product, filter client-side)
listNeedingEnrichment(projectId) -> Focus groups where lastEnriched is null or >7 days ago
getEnrichmentProgress(id)    -> Returns filled vs total enrichment fields

// New mutations
createBatch(groups[])        -> Insert multiple focus groups, return array of IDs
enrich(id, fields, agentName, reasoning) -> Update enrichment fields + append to enrichments[] audit log
enrichBatch(updates[])       -> Batch enrich multiple focus groups
importFromStaging(stagingIds[]) -> Move approved staging records to focusGroups
                                  For "create_new": insert new focusGroup
                                  For "enrich_existing": merge into matched focusGroup
updateEnrichmentFields(id, enrichmentFields) -> Update only the enrichment-specific fields
                                                (awareness, contentPreferences, purchaseBehavior, etc.)
```

### 2d. Schema Changes to Existing focusGroups Table

No structural changes needed -- the existing schema already has all 40+ fields including the enrichments[] audit log array. However, add one new index:

```typescript
// Add to focusGroups table in schema.ts
.index("by_name", ["productId", "name"])  // For exact-match lookups during import
```

### 2e. New Pipeline Preset in seed.ts

Add a second audience-focused pipeline for document import:

```typescript
{
  name: "Document Import",
  slug: "document-import",
  type: "preset" as const,
  description: "Parse an uploaded audience document into structured focus groups.",
  mainSteps: [
    { order: 0, label: "Created", description: "Task created", outputDir: "" },
    { order: 1, agent: "vibe-audience-parser", model: "sonnet", label: "Parse Document", description: "Extract focus groups from uploaded document", outputDir: "research" },
    { order: 2, agent: "vibe-audience-enricher", model: "sonnet", label: "Enrich Profiles", description: "Fill missing enrichment fields", outputDir: "research" },
  ],
  parallelBranches: [],
  onComplete: { telegram: true, summary: true, generateManifest: false },
}
```

The existing "Audience Discovery" pipeline (slug: `audience-discovery`) already covers Flow A with vibe-audience-researcher and vibe-audience-enricher. No change needed.

### 2f. Task Status Extension

The existing task status enum does not need changes. The pipeline maps `outputDir: "research"` to status `"researched"`, which is fine. Focus group pipeline tasks will use:
- `backlog` -> `researched` (after parse/research completes) -> `completed` (after enrichment)

---

## 3. Agent Design

### Agent 1: vibe-audience-researcher

| Property | Value |
|----------|-------|
| **Skill path** | `.claude/skills/audience-research-procedures/` |
| **Agent file** | `.claude/skills/audience-research-procedures/vibe-audience-researcher.md` |
| **Model** | opus |
| **Schedule** | on-demand |
| **Pipeline step** | "Audience Discovery" step 1 |
| **Service dependencies** | web_search (REQUIRED), web_scraping (OPTIONAL), social_scraping_reddit (OPTIONAL) |

**Inputs:**
- Product context from Convex: `products:get` (whatItIs, features, targetMarket, competitors, USPs, website)
- Task metadata with projectId, productId

**Process:**
1. Read product context from Convex
2. Phase 1 - Market Research:
   - Use Brave Search (web_search) to find competitor sites, forums, review sites
   - If web_scraping available: scrape 3-5 competitor sites for messaging/testimonials
   - If social_scraping_reddit available: scrape relevant subreddits for language patterns
3. Phase 2 - Segmentation:
   - Identify natural groupings by goal, life stage, pain point, identity
   - Target 10-30 groups depending on market breadth
   - Apply psychographic frameworks (Schwartz awareness levels, lifestyle segmentation)
4. Phase 3 - Profile Generation:
   - For each group, generate full profile matching focusGroups schema
   - Critical: language patterns must be REAL phrases from research, not invented
   - Each group must have 5+ core desires, 5+ pain points, 5+ language patterns, 3+ hooks
5. Phase 4 - Output:
   - Generate comprehensive markdown document
   - Save to filesystem: `projects/{slug}/research/audience-intelligence-{timestamp}.md`
   - Save to Convex documents table (type: "audience_doc")
   - Parse into structured JSON and write to `focusGroupStaging` via `focusGroupStaging:createBatch`
   - Complete pipeline step

**Outputs:**
- Markdown document (filesystem + Convex documents)
- N records in focusGroupStaging table (status: pending_review)

**Skills needed:**
```
.claude/skills/audience-research-procedures/
├── SKILL.md                          <- Main skill instructions
├── scripts/
│   ├── scrape_reddit.py              <- Reddit API wrapper (uses resolve_service.py)
│   ├── scrape_reviews.py             <- Review site scraper
│   ├── analyze_competitors.py        <- Competitor site analysis
│   └── compile_audience_doc.py       <- Generate final markdown
└── references/
    ├── research-methodology.md       <- Step-by-step protocol
    ├── focus-group-template.md       <- Template for each profile
    ├── focus-group-schema.json       <- JSON schema matching Convex fields
    ├── psychographic-frameworks.md   <- Maslow, VALS, Schwartz
    └── example-output.md            <- The fitness doc as example
```

### Agent 2: vibe-audience-parser

| Property | Value |
|----------|-------|
| **Skill path** | `.claude/skills/audience-analysis-procedures/` |
| **Agent file** | `.claude/skills/audience-analysis-procedures/vibe-audience-parser.md` |
| **Model** | sonnet |
| **Schedule** | on-demand |
| **Pipeline step** | "Document Import" step 1 |
| **Service dependencies** | none (local file processing only) |

**Inputs:**
- Uploaded file path (from task metadata)
- Product context (productId, projectId)
- Existing focus groups for the product (for matching)

**Process:**
1. Read the uploaded file
2. Format detection and conversion:
   - `.md` / `.txt`: read directly
   - `.docx`: convert via `pandoc -f docx -t markdown`
   - `.pdf`: extract text via `pymupdf` or `pdfplumber`
3. Structural parsing:
   - Identify document structure (headers, numbered sections, tables)
   - Detect individual audience segment boundaries
   - For each segment, extract fields using pattern matching + LLM reasoning
4. Field extraction per segment:
   - Name, nickname (from headers)
   - Category (infer from grouping headers or content)
   - Demographics, psychographics (from labeled sections/tables)
   - Core desires, pain points, fears, beliefs, objections (from bullet lists)
   - Language patterns, marketing hooks, ebook angles (from bullet lists)
   - Transformation promise (from labeled section)
5. Completeness scoring:
   - Count filled vs total required fields
   - Generate completenessScore (0.0-1.0)
   - List missingFields array
6. Fuzzy matching against existing focus groups:
   - Query `focusGroups:listByProduct` for existing groups
   - For each parsed group, compare:
     a. Exact name match (case-insensitive) -> "enrich_existing" (confidence: 1.0)
     b. Exact nickname match (case-insensitive) -> "enrich_existing" (confidence: 0.95)
     c. Normalized Levenshtein distance on name < 0.2 -> "possible_match" (confidence: 1.0 - distance)
     d. No match -> "create_new"
7. Write to staging: `focusGroupStaging:createBatch`
8. Complete pipeline step

**Outputs:**
- N records in focusGroupStaging with matchStatus and completeness data

**Skills needed:**
```
.claude/skills/audience-analysis-procedures/
├── SKILL.md                          <- Main skill instructions
├── scripts/
│   ├── convert_docx.sh              <- pandoc wrapper
│   ├── extract_pdf_text.py          <- PDF text extraction
│   ├── parse_audience_doc.py        <- Structural parsing (regex + heuristics)
│   └── fuzzy_match.py               <- Name matching logic
└── references/
    ├── focus-group-schema.json       <- Required fields and types
    ├── parsing-patterns.md           <- Common document structures to recognize
    ├── example-input-output.md       <- Example: raw text -> structured JSON
    └── known-formats.md              <- Formats we've seen (fitness doc format, etc.)
```

### Agent 3: vibe-audience-enricher

| Property | Value |
|----------|-------|
| **Skill path** | `.claude/skills/audience-enrichment-procedures/` |
| **Agent file** | `.claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md` |
| **Model** | sonnet |
| **Schedule** | weekly + on-demand (triggered by pipeline or @mention) |
| **Pipeline step** | "Audience Discovery" step 2 / "Document Import" step 2 |
| **Service dependencies** | web_search (OPTIONAL), social_scraping_reddit (OPTIONAL) |

**Inputs (pipeline mode):**
- Task ID -> reads all staging records via `focusGroupStaging:listByTask`
- Product context

**Inputs (weekly heartbeat mode):**
- Queries `focusGroups:listNeedingEnrichment` across all projects
- Activity feed for agent discoveries

**Process (pipeline mode - enriching staging records):**
1. For each staging record with `needsEnrichment: true`:
   a. Analyze existing fields to infer missing ones:
      - If pain points + beliefs present but awarenessStage missing:
        Apply Schwartz awareness framework to infer stage
      - If demographics present but purchaseBehavior missing:
        Infer buying triggers from income + lifestyle + pain points
      - If language patterns present but communicationStyle missing:
        Analyze formality, humor, story/data preferences from language
   b. For each inferred field:
      - Set confidence level (high/medium/low)
      - Record reasoning
   c. Update staging record: `focusGroupStaging:updateFields`
   d. Update completenessScore and missingFields

**Process (weekly heartbeat mode - enriching production records):**
1. Query `focusGroups:listNeedingEnrichment` (lastEnriched null or > 7 days)
2. Check activities feed for agent discoveries tagged with focus group IDs
3. For each new discovery:
   a. Validate it's genuinely new (not duplicate of existing data)
   b. Categorize: new pain point? language pattern? objection?
   c. Call `focusGroups:enrich` which:
      - Appends to relevant array field
      - Appends audit entry to enrichments[] array
      - Updates lastEnriched timestamp
4. Log enrichment summary to activities

**Outputs:**
- Updated staging records (pipeline mode)
- Updated focusGroup records with enrichments audit trail (heartbeat mode)

**Enrichment audit trail format (already in schema):**
```json
{
  "timestamp": 1739300000000,
  "source": "weekly_heartbeat",
  "agentName": "vibe-audience-enricher",
  "field": "awarenessStage",
  "previousValue": null,
  "newValue": "solution_aware",
  "confidence": "high",
  "reasoning": "Beliefs include 'I know what works but can't stick to it' + objections mention specific product categories -> solution_aware"
}
```

**Skills needed:**
```
.claude/skills/audience-enrichment-procedures/
├── SKILL.md                           <- Main skill instructions
├── scripts/
│   ├── infer_awareness.py            <- Schwartz awareness inference from fields
│   ├── infer_sophistication.py       <- Market sophistication from language patterns
│   ├── infer_purchase_behavior.py    <- Purchase behavior from demographics + pain points
│   ├── scan_recent_mentions.py       <- Check activities for new discoveries
│   └── update_focus_group.sh         <- Convex CLI wrapper for enrich
└── references/
    ├── enrichment-protocol.md        <- Validation rules and confidence criteria
    ├── awareness-classification.md   <- How to classify awareness stages
    ├── sophistication-classification.md <- How to classify market sophistication
    └── enrichment-sources.md         <- Where to find new data
```

---

## 4. Pipeline Templates

### Pipeline 1: Audience Discovery (already exists in seed.ts)

```
Slug: audience-discovery
Steps:
  0. Created (task created)
  1. vibe-audience-researcher (opus) - "Research Audiences"
     - Inputs: product context
     - Outputs: audience doc + staging records
     - outputDir: "research"
  2. vibe-audience-enricher (sonnet) - "Enrich Profiles"
     - Inputs: staging records from step 1
     - Outputs: enriched staging records
     - outputDir: "research"
On complete: telegram notification, summary
```

### Pipeline 2: Document Import (new, add to seed.ts)

```
Slug: document-import
Steps:
  0. Created (task created)
  1. vibe-audience-parser (sonnet) - "Parse Document"
     - Inputs: uploaded file path
     - Outputs: staging records with match status
     - outputDir: "research"
  2. vibe-audience-enricher (sonnet) - "Enrich Profiles"
     - Inputs: staging records from step 1
     - Outputs: enriched staging records
     - outputDir: "research"
On complete: telegram notification, summary
```

### How Focus Group Pipelines Differ from Content Pipelines

They use the **same** task/pipeline infrastructure. The differences are:
1. **Output type**: Focus group pipelines produce focusGroupStaging records, not files in campaign folders
2. **No campaignId**: These tasks have productId but no campaignId (campaigns don't exist yet -- you need audiences first)
3. **Review gate**: After pipeline completion, there's a manual review step in the dashboard before data goes live. Content pipelines go straight to the campaign folder.
4. **Task metadata**: The task.metadata field stores `{ type: "audience_research", productId, uploadedFilePath? }`

To support this, the task creation for focus group pipelines should set:
- `contentType: "audience_research"` or `contentType: "audience_import"`
- `metadata: { productId, uploadedFilePath?, sourceDocumentId? }`
- `campaignId: undefined` (no campaign)

---

## 5. Dashboard Pages

### 5a. Enhanced Audiences Page (modify existing)

**File:** `dashboard/pages/projects/[slug]/products/[id]/audiences.vue`

**Current state:** List of expandable cards with "New Focus Group" button.

**Enhanced layout:**

```
┌──────────────────────────────────────────────────────┐
│  Audiences                                           │
│  Target focus groups for this product                │
│                                                      │
│  [Research Audiences] [Import Document] [+ Manual]   │
│                                                      │
│  ┌─ Active Jobs ──────────────────────────────────┐  │
│  │ ⟳ Audience Research - Step 2/2 (Enriching)    │  │
│  │   14/18 groups enriched  [View Progress]       │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Pending Review ───────────────────────────────┐  │
│  │ 18 focus groups from "Audience Research" task   │  │
│  │ [Review & Import]                              │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ── Existing Focus Groups (12) ──                    │
│                                                      │
│  [Enrichment Progress: ████████░░ 78%]               │
│                                                      │
│  ┌─ #1 Fat Loss Seekers "The Scale Watchers"  ──┐   │
│  │ Category: Physical Transformation | Source: up │   │
│  │ Enrichment: ████████░░ 80% | Last: 3 days ago │   │
│  │ [▼ expand]                                     │   │
│  └────────────────────────────────────────────────┘  │
│  ┌─ #2 Muscle Builders "The Ectomorph Strugg..."─┐   │
│  │ ...                                            │   │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

**New UI elements on this page:**
1. **Three action buttons** at top: "Research Audiences", "Import Document", "+ Manual"
2. **Active Jobs banner** (if there are audience-related tasks in progress for this product)
3. **Pending Review banner** (if there are staging records in pending_review status)
4. **Enrichment progress bar** per focus group card (filled enrichment fields / total)
5. **Overall enrichment progress** across all groups

### 5b. New Page: Staging Review

**File:** `dashboard/pages/projects/[slug]/products/[id]/audiences/review.vue`

**Purpose:** Review and approve/reject staging records before import.

```
┌──────────────────────────────────────────────────────┐
│  Review Imported Audiences                           │
│  Source: "Audience Research" task #abc123             │
│                                                      │
│  Summary: 18 total | 15 new | 2 enrich | 1 possible │
│  Completeness: avg 85%                               │
│                                                      │
│  [Approve All New] [Approve All] [Reject Remaining]  │
│                                                      │
│  ─── New Groups (15) ────────────────────────────    │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☐ Fat Loss Seekers "The Scale Watchers"        │  │
│  │    Status: create_new | Completeness: 92%      │  │
│  │    Missing: contentPreferences, seasonalContext │  │
│  │    [Preview] [Edit] [Approve] [Reject]         │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ─── Enrichment Matches (2) ─────────────────────    │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☐ Plateau Breakers "The Stuck Sufferers"       │  │
│  │    Status: enrich_existing                     │  │
│  │    Matches: existing group #5 (name: exact)    │  │
│  │    New data: +3 pain points, +2 hooks          │  │
│  │    [View Diff] [Approve Merge] [Reject]        │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ─── Possible Matches (1) ───────────────────────    │
│  ┌────────────────────────────────────────────────┐  │
│  │ ☐ Weight Plateau Victims (similarity: 0.82)    │  │
│  │    Possible match: #5 "Plateau Breakers"       │  │
│  │    [Create as New] [Merge with #5] [Skip]      │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  [Import All Approved (16)]                          │
└──────────────────────────────────────────────────────┘
```

### 5c. New Page: Enrichment Detail

**File:** `dashboard/pages/projects/[slug]/products/[id]/audiences/[fgId].vue`

**Purpose:** Deep view of a single focus group with enrichment history.

```
┌──────────────────────────────────────────────────────┐
│  ← Back to Audiences                                 │
│                                                      │
│  #1 Fat Loss Seekers "The Scale Watchers"            │
│  Category: Physical Transformation | Source: uploaded │
│  Enrichment: ████████░░ 80%                          │
│                                                      │
│  [Edit] [Re-enrich Now] [Delete]                     │
│                                                      │
│  ── Core Data ────────────────────────────────────   │
│  (Same expandable sections as current audiences.vue)  │
│  Demographics | Psychographics | Core Desires |       │
│  Pain Points | Fears | Beliefs | Objections |         │
│  Emotional Triggers | Language Patterns |             │
│  Marketing Hooks | Ebook Angles |                     │
│  Transformation Promise                               │
│                                                      │
│  ── Enrichment Fields ────────────────────────────   │
│  ┌────────────────────────────────────────────────┐  │
│  │ Awareness Stage: solution_aware (high conf.)   │  │
│  │   Signals: beliefs="I know what works..."      │  │
│  │   Source: auto | Last: 2026-02-10              │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Sophistication Level: stage3                   │  │
│  │   Source: auto | Last: 2026-02-10              │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Content Preferences: ░░░ NOT YET ENRICHED      │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Purchase Behavior: ✓ enriched                  │  │
│  │   Buying triggers: Photos, doctor visits...    │  │
│  │   Price range: $30-$100/month                  │  │
│  │   Decision process: Research-heavy, 2-4 weeks  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ── Enrichment History ───────────────────────────   │
│  │ 2026-02-10 14:32 | vibe-audience-enricher      │  │
│  │   Field: awarenessStage                         │  │
│  │   null → "solution_aware" (high confidence)     │  │
│  │   Reason: "Beliefs include 'I know what...'     │  │
│  │           + objections mention specific..."      │  │
│  │                                                 │  │
│  │ 2026-02-10 14:32 | vibe-audience-enricher      │  │
│  │   Field: purchaseBehavior                       │  │
│  │   null → {buyingTriggers: [...], ...}           │  │
│  │   Reason: "Demographics indicate middle..."     │  │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 5d. Upload Dialog Component

**File:** `dashboard/components/AudienceImportDialog.vue`

**Purpose:** Modal for uploading an audience document and triggering the import pipeline.

```
┌──────────────────────────────────────────────────────┐
│  Import Audience Document                       [X]  │
│                                                      │
│  Upload a document containing audience research,     │
│  personas, or focus group profiles.                  │
│                                                      │
│  Supported formats: .md, .txt, .docx, .pdf           │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │                                                │  │
│  │     Drag & drop file here or click to browse   │  │
│  │                                                │  │
│  │     ┌──────────────┐                          │  │
│  │     │ Browse Files │                          │  │
│  │     └──────────────┘                          │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Selected: Fitness_Focus_Groups.md (4.2 KB)          │
│                                                      │
│  ☐ Auto-enrich after parsing (recommended)           │
│                                                      │
│  [Cancel]                          [Start Import]    │
└──────────────────────────────────────────────────────┘
```

### 5e. Research Trigger Dialog Component

**File:** `dashboard/components/AudienceResearchDialog.vue`

**Purpose:** Confirm product context and launch the research pipeline.

```
┌──────────────────────────────────────────────────────┐
│  Research Audiences                             [X]  │
│                                                      │
│  Generate focus group profiles from market research  │
│  for: GymZilla Tribe                                 │
│                                                      │
│  ── Product Context (pre-filled) ─────────────────   │
│  What it is: Online fitness community and supplements │
│  Target market: Men and women 25-55 into fitness     │
│  Competitors: Athlean-X, Jeff Nippard, MuscleBlaze   │
│  Website: gymzillatribe.com                          │
│                                                      │
│  ☐ Include Reddit research (requires Reddit API)     │
│  ☐ Include competitor scraping (requires Firecrawl)   │
│  ☐ Auto-enrich after research (recommended)          │
│                                                      │
│  Estimated time: 15-30 minutes                       │
│  Model: opus (high-quality research)                 │
│                                                      │
│  [Cancel]                      [Start Research]      │
└──────────────────────────────────────────────────────┘
```

---

## 6. Matching Logic (Enrich vs. Create)

When the parser encounters a focus group from an uploaded document and needs to decide whether to create a new record or enrich an existing one:

### Matching Algorithm

```python
def match_focus_group(parsed_name, parsed_nickname, existing_groups):
    """
    Returns: (match_status, matched_id, confidence, reason)
    """
    parsed_name_lower = parsed_name.strip().lower()
    parsed_nickname_lower = (parsed_nickname or "").strip().lower()

    for existing in existing_groups:
        existing_name_lower = existing.name.strip().lower()
        existing_nickname_lower = (existing.nickname or "").strip().lower()

        # Priority 1: Exact name match
        if parsed_name_lower == existing_name_lower:
            return ("enrich_existing", existing._id, 1.0, "exact_name")

        # Priority 2: Exact nickname match
        if parsed_nickname_lower and parsed_nickname_lower == existing_nickname_lower:
            return ("enrich_existing", existing._id, 0.95, "exact_nickname")

        # Priority 3: Name contained in other (handles "Fat Loss Seekers" vs "Fat Loss")
        if parsed_name_lower in existing_name_lower or existing_name_lower in parsed_name_lower:
            return ("possible_match", existing._id, 0.85, "name_substring")

        # Priority 4: Levenshtein similarity on name
        similarity = 1.0 - (levenshtein(parsed_name_lower, existing_name_lower) /
                           max(len(parsed_name_lower), len(existing_name_lower)))
        if similarity >= 0.8:
            return ("possible_match", existing._id, similarity, f"fuzzy_{similarity:.2f}")

        # Priority 5: Nickname-to-name cross-match
        if parsed_nickname_lower:
            nick_to_name_sim = 1.0 - (levenshtein(parsed_nickname_lower, existing_name_lower) /
                                      max(len(parsed_nickname_lower), len(existing_name_lower)))
            if nick_to_name_sim >= 0.8:
                return ("possible_match", existing._id, nick_to_name_sim, f"nick_to_name_{nick_to_name_sim:.2f}")

    return ("create_new", None, 0.0, "no_match")
```

### Merge Strategy for "enrich_existing"

When merging new data into an existing focus group:

1. **Array fields** (painPoints, coreDesires, languagePatterns, etc.): **Union** -- add new items that don't already exist (case-insensitive dedup)
2. **String fields** (overview, transformationPromise): **Keep existing** unless existing is empty
3. **Object fields** (demographics, psychographics): **Deep merge** -- fill in missing sub-fields, keep existing values
4. **Enrichment fields** (awarenessStage, etc.): **Only overwrite if existing is null** -- never downgrade existing enrichment
5. **Always**: Append entry to enrichments[] audit trail

---

## 7. Document Handling

### Upload Flow

1. User clicks "Import Document" on audiences page
2. AudienceImportDialog.vue opens
3. User selects file via file input (accepts: .md, .txt, .docx, .pdf)
4. On "Start Import":
   a. Read file content client-side (for .md/.txt) or prepare for server-side processing
   b. For .md/.txt: content is stored directly in Convex documents table
   c. For .docx/.pdf: file path is stored; agent converts later
   d. Call API to create a task with:
      - Pipeline: "document-import"
      - contentType: "audience_import"
      - metadata: { productId, uploadedFilePath, sourceFormat }
   e. Save uploaded file to: `projects/{slug}/uploads/audience-{timestamp}.{ext}`
   f. Create document record in Convex
5. Dashboard shows "Active Job" banner on audiences page
6. Orchestrator picks up the task and dispatches agents

### Format Detection

The vibe-audience-parser agent handles format conversion:

| Format | Detection | Conversion |
|--------|-----------|------------|
| `.md` | File extension | Read directly |
| `.txt` | File extension | Read directly |
| `.docx` | File extension | `pandoc -f docx -t markdown -o output.md input.docx` |
| `.pdf` | File extension | Python: `pymupdf` or `pdfplumber` to extract text |

### Storage

- **Raw file**: `projects/{project-slug}/uploads/audience-{timestamp}.{ext}`
- **Converted markdown**: `projects/{project-slug}/research/audience-{timestamp}.md`
- **Convex record**: documents table with type "audience_doc", productId set, filePath pointing to filesystem

---

## 8. Enrichment Tracking

### Completeness Score Calculation

Each focus group has a calculated enrichment completeness score. The enrichable fields and their weights:

| Field | Weight | Category |
|-------|--------|----------|
| awarenessStage | 15 | Core enrichment |
| sophisticationLevel | 10 | Core enrichment |
| contentPreferences | 10 | Behavioral |
| influenceSources | 10 | Behavioral |
| purchaseBehavior | 15 | Behavioral |
| competitorContext | 10 | Market |
| communicationStyle | 10 | Behavioral |
| seasonalContext | 5 | Contextual |
| negativeTriggers | 10 | Safety |
| awarenessSignals | 5 | Diagnostic |

**Total weight: 100**

A field is "filled" if it's not null/undefined. Score = sum of weights for filled fields.

### Dashboard Visualization

- Per-group: colored progress bar (red < 30%, yellow 30-70%, green > 70%)
- Per-product: average enrichment score across all groups
- Enrichment history: timeline view of all enrichments[] entries

### Enrichments Audit Log

Already exists in the schema as `enrichments: v.optional(v.array(v.object({...})))`. The `focusGroups:enrich` function MUST:
1. Read existing enrichments array (or initialize empty)
2. Append new entry with timestamp, source, agentName, field, previousValue, newValue, confidence, reasoning
3. Update the target field
4. Update lastEnriched timestamp

---

## 9. Implementation Phases

### Phase 1: Convex Foundation
**Estimated effort:** Small (1 session)
**Dependencies:** None

**Files to create:**
- `convex/focusGroupStaging.ts` -- Full CRUD for staging table

**Files to modify:**
- `convex/schema.ts` -- Add focusGroupStaging table, add by_name index to focusGroups
- `convex/focusGroups.ts` -- Add findByName, findByNickname, searchByName, listNeedingEnrichment, getEnrichmentProgress, createBatch, enrich, enrichBatch, importFromStaging, updateEnrichmentFields
- `convex/seed.ts` -- Add "Document Import" pipeline preset

**Acceptance criteria:**
- [ ] `npx convex dev` compiles without errors
- [ ] All new functions callable via CLI
- [ ] `focusGroupStaging:createBatch` inserts multiple records
- [ ] `focusGroups:createBatch` inserts multiple records and returns IDs
- [ ] `focusGroups:enrich` updates field + appends to enrichments[] audit log
- [ ] `focusGroups:importFromStaging` moves approved staging records to production
- [ ] `focusGroups:findByName` returns exact match or null

### Phase 2: Agent Skills -- Audience Parser
**Estimated effort:** Medium (1-2 sessions)
**Dependencies:** Phase 1

**Files to create:**
- `.claude/skills/audience-analysis-procedures/SKILL.md`
- `.claude/skills/audience-analysis-procedures/scripts/convert_docx.sh`
- `.claude/skills/audience-analysis-procedures/scripts/extract_pdf_text.py`
- `.claude/skills/audience-analysis-procedures/scripts/parse_audience_doc.py`
- `.claude/skills/audience-analysis-procedures/scripts/fuzzy_match.py`
- `.claude/skills/audience-analysis-procedures/references/focus-group-schema.json`
- `.claude/skills/audience-analysis-procedures/references/parsing-patterns.md`
- `.claude/skills/audience-analysis-procedures/references/example-input-output.md`
- `.claude/skills/audience-analysis-procedures/references/known-formats.md`
- `.claude/skills/audience-analysis-procedures/vibe-audience-parser.md` (agent file)

**Acceptance criteria:**
- [ ] Parser can extract 28 focus groups from the fitness intelligence doc
- [ ] Each extracted group has all required fields or flagged missing fields
- [ ] Completeness scoring works (count filled fields)
- [ ] Fuzzy matching correctly identifies exact name matches
- [ ] .docx conversion works via pandoc
- [ ] .pdf text extraction works
- [ ] Output writes to focusGroupStaging via Convex CLI

### Phase 3: Agent Skills -- Audience Researcher
**Estimated effort:** Medium-Large (2 sessions)
**Dependencies:** Phase 1

**Files to create:**
- `.claude/skills/audience-research-procedures/SKILL.md`
- `.claude/skills/audience-research-procedures/scripts/scrape_reddit.py`
- `.claude/skills/audience-research-procedures/scripts/scrape_reviews.py`
- `.claude/skills/audience-research-procedures/scripts/analyze_competitors.py`
- `.claude/skills/audience-research-procedures/scripts/compile_audience_doc.py`
- `.claude/skills/audience-research-procedures/references/research-methodology.md`
- `.claude/skills/audience-research-procedures/references/focus-group-template.md`
- `.claude/skills/audience-research-procedures/references/focus-group-schema.json` (shared with parser)
- `.claude/skills/audience-research-procedures/references/psychographic-frameworks.md`
- `.claude/skills/audience-research-procedures/references/data-sources.md`
- `.claude/skills/audience-research-procedures/references/example-output.md`
- `.claude/skills/audience-research-procedures/vibe-audience-researcher.md` (agent file)

**Acceptance criteria:**
- [ ] Given a product context, generates 10-30 focus group profiles
- [ ] Each group has 5+ core desires, 5+ pain points, 5+ language patterns, 3+ hooks
- [ ] Language patterns are sourced from web research (not invented)
- [ ] Output saved as markdown document to filesystem and Convex
- [ ] Output parsed and written to focusGroupStaging
- [ ] Works with web_search only (REQUIRED); degrades gracefully without web_scraping/reddit

### Phase 4: Agent Skills -- Audience Enricher
**Estimated effort:** Medium (1-2 sessions)
**Dependencies:** Phase 1

**Files to create:**
- `.claude/skills/audience-enrichment-procedures/SKILL.md`
- `.claude/skills/audience-enrichment-procedures/scripts/infer_awareness.py`
- `.claude/skills/audience-enrichment-procedures/scripts/infer_sophistication.py`
- `.claude/skills/audience-enrichment-procedures/scripts/infer_purchase_behavior.py`
- `.claude/skills/audience-enrichment-procedures/scripts/scan_recent_mentions.py`
- `.claude/skills/audience-enrichment-procedures/scripts/update_focus_group.sh`
- `.claude/skills/audience-enrichment-procedures/references/enrichment-protocol.md`
- `.claude/skills/audience-enrichment-procedures/references/awareness-classification.md`
- `.claude/skills/audience-enrichment-procedures/references/sophistication-classification.md`
- `.claude/skills/audience-enrichment-procedures/references/enrichment-sources.md`
- `.claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md` (agent file)

**Acceptance criteria:**
- [ ] Pipeline mode: reads staging records, fills enrichment fields, updates completeness
- [ ] Heartbeat mode: finds groups needing enrichment, processes them
- [ ] Awareness stage inference matches expected results for known test cases
- [ ] All enrichments logged to enrichments[] audit trail
- [ ] lastEnriched timestamp updated after each run

### Phase 5: Dashboard -- Enhanced Audiences Page
**Estimated effort:** Medium (1-2 sessions)
**Dependencies:** Phase 1

**Files to modify:**
- `dashboard/pages/projects/[slug]/products/[id]/audiences.vue` -- Add three action buttons, active jobs banner, pending review banner, enrichment progress bars

**Files to create:**
- `dashboard/components/AudienceImportDialog.vue` -- Upload dialog
- `dashboard/components/AudienceResearchDialog.vue` -- Research trigger dialog
- `dashboard/components/EnrichmentProgressBar.vue` -- Reusable progress bar component
- `dashboard/composables/useAudienceJobs.ts` -- Composable for tracking audience task status

**Acceptance criteria:**
- [ ] Three buttons visible on audiences page header
- [ ] Import dialog opens, accepts file upload, creates task
- [ ] Research dialog shows product context, creates task
- [ ] Active job banner appears when audience task is in progress
- [ ] Pending review banner appears when staging records exist
- [ ] Enrichment progress bar shows per-group and overall enrichment %

### Phase 6: Dashboard -- Staging Review Page
**Estimated effort:** Medium (1-2 sessions)
**Dependencies:** Phase 5

**Files to create:**
- `dashboard/pages/projects/[slug]/products/[id]/audiences/review.vue` -- Full review interface
- `dashboard/components/StagingGroupCard.vue` -- Individual staging record card with approve/reject/edit
- `dashboard/components/StagingDiffView.vue` -- Side-by-side diff for enrich_existing matches
- `dashboard/components/StagingBulkActions.vue` -- Bulk approve/reject toolbar

**Acceptance criteria:**
- [ ] Review page lists all staging records grouped by matchStatus
- [ ] "create_new" groups can be approved/rejected/edited
- [ ] "enrich_existing" groups show diff between new and existing data
- [ ] "possible_match" groups let user choose: create new, merge, or skip
- [ ] Bulk approve/reject works
- [ ] "Import All Approved" calls focusGroups:importFromStaging and clears staging

### Phase 7: Dashboard -- Focus Group Detail & Enrichment History
**Estimated effort:** Small-Medium (1 session)
**Dependencies:** Phase 5

**Files to create:**
- `dashboard/pages/projects/[slug]/products/[id]/audiences/[fgId].vue` -- Detail page

**Files to create:**
- `dashboard/components/EnrichmentTimeline.vue` -- Timeline visualization of enrichment history
- `dashboard/components/EnrichmentFieldStatus.vue` -- Shows enrichment field with filled/empty state

**Acceptance criteria:**
- [ ] Detail page shows all focus group data (core + enrichment fields)
- [ ] Enrichment fields show filled/empty status with confidence badges
- [ ] Enrichment history timeline shows all entries from enrichments[] array
- [ ] "Re-enrich Now" button triggers manual enrichment
- [ ] "Edit" mode allows updating any field (including enrichment overrides)

### Phase 8: Agent Registration & Orchestrator Integration
**Estimated effort:** Small (1 session)
**Dependencies:** Phases 2, 3, 4

**Files to modify:**
- `convex/seed.ts` -- Add agent records for vibe-audience-parser, vibe-audience-researcher, vibe-audience-enricher
- Agent service dependency records in Convex (agentServiceDeps)

**Files to create:**
- Pipeline orchestrator awareness of audience tasks (if vibe-orchestrator needs updates)

**Acceptance criteria:**
- [ ] All 3 agents registered in Convex agents table
- [ ] Service dependencies recorded (web_search, web_scraping, social_scraping_reddit)
- [ ] Orchestrator can dispatch audience pipeline tasks to the correct agents
- [ ] `scripts/invoke-agent.sh` can invoke each agent by name

### Phase 9: End-to-End Testing
**Estimated effort:** Medium (1-2 sessions)
**Dependencies:** All previous phases

**Test scenarios:**
1. **Flow A full cycle**: Create product -> Research Audiences -> wait for pipeline -> review -> import -> verify in Convex
2. **Flow B full cycle**: Create product -> Upload fitness doc -> wait for parse -> review -> import -> verify
3. **Enrichment**: Import groups without enrichment fields -> run enricher -> verify fields populated with audit trail
4. **Matching**: Upload doc with some existing group names -> verify match detection -> approve merge -> verify data merged
5. **Edge cases**: Empty document, document with 1 group, document with 50+ groups, .docx, .pdf

---

## 10. Complete File Inventory

### New Files (31 total)

**Convex (2):**
1. `convex/focusGroupStaging.ts` -- Staging CRUD module

**Agent Skills -- Parser (10):**
2. `.claude/skills/audience-analysis-procedures/SKILL.md`
3. `.claude/skills/audience-analysis-procedures/vibe-audience-parser.md`
4. `.claude/skills/audience-analysis-procedures/scripts/convert_docx.sh`
5. `.claude/skills/audience-analysis-procedures/scripts/extract_pdf_text.py`
6. `.claude/skills/audience-analysis-procedures/scripts/parse_audience_doc.py`
7. `.claude/skills/audience-analysis-procedures/scripts/fuzzy_match.py`
8. `.claude/skills/audience-analysis-procedures/references/focus-group-schema.json`
9. `.claude/skills/audience-analysis-procedures/references/parsing-patterns.md`
10. `.claude/skills/audience-analysis-procedures/references/example-input-output.md`
11. `.claude/skills/audience-analysis-procedures/references/known-formats.md`

**Agent Skills -- Researcher (12):**
12. `.claude/skills/audience-research-procedures/SKILL.md`
13. `.claude/skills/audience-research-procedures/vibe-audience-researcher.md`
14. `.claude/skills/audience-research-procedures/scripts/scrape_reddit.py`
15. `.claude/skills/audience-research-procedures/scripts/scrape_reviews.py`
16. `.claude/skills/audience-research-procedures/scripts/analyze_competitors.py`
17. `.claude/skills/audience-research-procedures/scripts/compile_audience_doc.py`
18. `.claude/skills/audience-research-procedures/references/research-methodology.md`
19. `.claude/skills/audience-research-procedures/references/focus-group-template.md`
20. `.claude/skills/audience-research-procedures/references/focus-group-schema.json`
21. `.claude/skills/audience-research-procedures/references/psychographic-frameworks.md`
22. `.claude/skills/audience-research-procedures/references/data-sources.md`
23. `.claude/skills/audience-research-procedures/references/example-output.md`

**Agent Skills -- Enricher (11):**
24. `.claude/skills/audience-enrichment-procedures/SKILL.md`
25. `.claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md`
26. `.claude/skills/audience-enrichment-procedures/scripts/infer_awareness.py`
27. `.claude/skills/audience-enrichment-procedures/scripts/infer_sophistication.py`
28. `.claude/skills/audience-enrichment-procedures/scripts/infer_purchase_behavior.py`
29. `.claude/skills/audience-enrichment-procedures/scripts/scan_recent_mentions.py`
30. `.claude/skills/audience-enrichment-procedures/scripts/update_focus_group.sh`
31. `.claude/skills/audience-enrichment-procedures/references/enrichment-protocol.md`
32. `.claude/skills/audience-enrichment-procedures/references/awareness-classification.md`
33. `.claude/skills/audience-enrichment-procedures/references/sophistication-classification.md`
34. `.claude/skills/audience-enrichment-procedures/references/enrichment-sources.md`

**Dashboard Components (8):**
35. `dashboard/components/AudienceImportDialog.vue`
36. `dashboard/components/AudienceResearchDialog.vue`
37. `dashboard/components/EnrichmentProgressBar.vue`
38. `dashboard/components/StagingGroupCard.vue`
39. `dashboard/components/StagingDiffView.vue`
40. `dashboard/components/StagingBulkActions.vue`
41. `dashboard/components/EnrichmentTimeline.vue`
42. `dashboard/components/EnrichmentFieldStatus.vue`

**Dashboard Pages (2):**
43. `dashboard/pages/projects/[slug]/products/[id]/audiences/review.vue`
44. `dashboard/pages/projects/[slug]/products/[id]/audiences/[fgId].vue`

**Dashboard Composables (1):**
45. `dashboard/composables/useAudienceJobs.ts`

### Modified Files (5)

1. `convex/schema.ts` -- Add focusGroupStaging table, add by_name index to focusGroups
2. `convex/focusGroups.ts` -- Add 8 new functions (findByName, findByNickname, searchByName, listNeedingEnrichment, getEnrichmentProgress, createBatch, enrich, enrichBatch, importFromStaging, updateEnrichmentFields)
3. `convex/seed.ts` -- Add "Document Import" pipeline preset + 3 agent registrations
4. `dashboard/pages/projects/[slug]/products/[id]/audiences.vue` -- Enhanced with action buttons, job banners, enrichment progress
5. `dashboard/components/FocusGroupForm.vue` -- Add enrichment fields section (read-only display of enrichment data in edit mode)

---

## 11. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Audience researcher generates low-quality groups (generic, not grounded in real data) | High | Medium | Require web_search as REQUIRED service; include quality checks in SKILL.md; use opus model for research; validate language patterns are from real sources |
| Document parser fails on unusual formats | Medium | Medium | Start with the fitness doc as the reference format; add format detection heuristics; fall back to LLM-based extraction when regex fails |
| Fuzzy matching produces false positives (wrong groups merged) | High | Low | Use conservative threshold (0.8); always show "possible_match" for human decision; never auto-merge below 0.95 confidence |
| Staging table grows unbounded (rejected records never cleaned) | Low | Medium | Add cleanup logic: delete rejected/imported staging records after 30 days |
| Enrichment overwrites good data with worse inference | Medium | Low | Never overwrite non-null enrichment fields in heartbeat mode; always log to audit trail; add human override flag |
| Pipeline task has no campaignId (breaks existing task queries) | Medium | Low | campaignId is already optional in the schema; ensure all task queries handle null campaignId gracefully |
| Large documents (100+ pages) timeout during parsing | Medium | Low | Chunk processing; set reasonable limits (max 50 groups per run); agent can split into multiple batches |

## 12. Open Questions

- [ ] **Staging TTL**: How long should rejected/imported staging records persist before cleanup? Suggested: 30 days.
- [ ] **Maximum focus groups per product**: Should there be a hard limit? The fitness doc has 28; some niches might warrant 50+.
- [ ] **Re-research**: If user runs "Research Audiences" again for the same product, should new results replace or merge with existing? Suggested: create new staging records that go through the match/merge flow, same as document import.
- [ ] **Enricher triggers**: Beyond weekly heartbeat, should content performance data automatically trigger enrichment? This depends on analytics agents (post-MVP).
- [ ] **File storage**: For MVP, files live on the filesystem. Should we add Convex file storage for uploads? Filesystem is fine for single-server; Convex storage needed for multi-server.

## 13. Success Criteria

1. A user with a new product can click "Research Audiences" and receive 15+ structured focus groups within 30 minutes, each with 5+ pain points, 5+ language patterns, and correct awareness stage classification.
2. A user can upload the existing 4,762-line fitness focus groups document and have all 28 groups extracted, validated, and imported in under 5 minutes.
3. Every enrichment change is tracked in the enrichments[] audit trail with agent name, confidence level, and reasoning.
4. The dashboard shows enrichment progress per focus group and allows human override of any field.
5. The system correctly identifies existing focus groups during re-import (name/nickname matching) and merges new data rather than creating duplicates.
6. All three agents (parser, researcher, enricher) work through the existing pipeline infrastructure without modifications to the pipeline engine.
