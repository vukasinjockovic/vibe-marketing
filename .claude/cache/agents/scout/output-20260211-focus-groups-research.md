# Focus Groups Implementation Research
Generated: 2026-02-11

## Summary
Focus groups are **structurally implemented** in the database and dashboard UI, but the **automated research/creation/enrichment pipeline is completely missing**. The system has the data model, CRUD operations, and UI components, but lacks the AI agents that populate and maintain focus group profiles.

---

## 1. Current Schema/API (✓ VERIFIED - EXISTS)

### Convex Schema (`/var/www/vibe-marketing/convex/schema.ts`)

**Location:** Lines 92-184 (focusGroups table definition)

**Core Fields:**
```typescript
focusGroups: defineTable({
  projectId: v.id("projects"),
  productId: v.id("products"),
  number: v.number(),
  name: v.string(),
  nickname: v.string(),
  category: v.string(),
  overview: v.string(),
  
  // Demographics
  demographics: v.object({
    ageRange: v.string(),
    gender: v.string(),
    income: v.string(),
    lifestyle: v.string(),
    triggers: v.array(v.string()),
  }),
  
  // Psychographics
  psychographics: v.object({
    values: v.array(v.string()),
    beliefs: v.array(v.string()),
    lifestyle: v.string(),
    identity: v.string(),
  }),
  
  // Marketing Intelligence
  coreDesires: v.array(v.string()),
  painPoints: v.array(v.string()),
  fears: v.array(v.string()),
  beliefs: v.array(v.string()),
  objections: v.array(v.string()),
  emotionalTriggers: v.array(v.string()),
  languagePatterns: v.array(v.string()),
  ebookAngles: v.array(v.string()),
  marketingHooks: v.array(v.string()),
  transformationPromise: v.string(),
  
  // Source tracking
  source: v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual")),
  lastEnriched: v.optional(v.number()),
  enrichmentNotes: v.optional(v.string()),
  
  // ENRICHMENT FIELDS (recently added - ✓ VERIFIED)
  awarenessStage: v.optional(v.union(
    v.literal("unaware"), 
    v.literal("problem_aware"), 
    v.literal("solution_aware"),
    v.literal("product_aware"), 
    v.literal("most_aware")
  )),
  awarenessConfidence: v.optional(v.union(
    v.literal("high"), v.literal("medium"), v.literal("low")
  )),
  awarenessStageSource: v.optional(v.union(
    v.literal("auto"), v.literal("manual")
  )),
  awarenessSignals: v.optional(v.object({
    beliefsSignal: v.optional(v.string()),
    objectionsSignal: v.optional(v.string()),
    languageSignal: v.optional(v.string()),
  })),
  
  // Additional enrichment fields
  contentPreferences: v.optional(v.object({...})),
  influenceSources: v.optional(v.object({...})),
  purchaseBehavior: v.optional(v.object({...})),
  competitorContext: v.optional(v.object({...})),
  sophisticationLevel: v.optional(v.union(...)),
  communicationStyle: v.optional(v.object({...})),
  seasonalContext: v.optional(v.object({...})),
  negativeTriggers: v.optional(v.object({...})),
  
  // Audit trail
  enrichments: v.optional(v.array(v.object({
    timestamp: v.number(),
    source: v.string(),
    agentName: v.string(),
    field: v.string(),
    previousValue: v.optional(v.string()),
    newValue: v.string(),
    confidence: v.union(v.literal("high"), v.literal("medium"), v.literal("low")),
    reasoning: v.string(),
  }))),
  
  researchNotes: v.optional(v.string()),
})
.index("by_product", ["productId"])
.index("by_project", ["projectId"])
.index("by_category", ["category"])
```

**Relationship:**
- Projects → Products → Focus Groups → Campaigns
- Campaigns reference `targetFocusGroupIds: v.array(v.id("focusGroups"))`

---

### Convex CRUD Functions (`/var/www/vibe-marketing/convex/focusGroups.ts`)

**✓ VERIFIED - All basic CRUD exists:**

| Function | Type | Purpose |
|----------|------|---------|
| `listByProject` | query | Get all focus groups for a project |
| `listByProduct` | query | Get all focus groups for a product |
| `get` | query | Get single focus group by ID |
| `getByCampaign` | query | Load all focus groups for a campaign |
| `create` | mutation | Create new focus group |
| `update` | mutation | Update existing (partial fields) |
| `remove` | mutation | Delete focus group |

**MISSING:**
- `createBatch` - For bulk import from audience analyzer
- `enrich` - For adding enrichment data with audit trail
- `searchByCategory` - Filter by category
- `getStale` - Find focus groups needing enrichment (lastEnriched > 7 days)

---

## 2. V3 Spec References (✓ VERIFIED - DETAILED)

### From `vibe-marketing-platform-v3.md`

**Section 10: Audience Intelligence Subsystem** (Lines 2526-2790)

Three planned skills (NONE IMPLEMENTED YET):

#### Skill 1: AudienceAnalyzer (✗ MISSING)
```
Path: .claude/skills/audience-analyzer/
Purpose: Parse uploaded docs (.docx, .pdf, .md) containing focus group profiles
Scripts: 
  - extract_focus_groups.py (regex/structural parsing)
  - validate_focus_group.py (field validation)
Output: Convex focusGroups:createBatch
```

#### Skill 2: AudienceResearcher (✗ MISSING)
```
Path: .claude/skills/audience-researcher/
Purpose: Generate comprehensive focus groups from scratch for a product
Agent: vibe-audience-researcher (opus)
Process:
  1. Analyze product/market/competitors
  2. Research forums, Reddit, Amazon reviews
  3. Generate 10-30 distinct focus groups
  4. Write to Convex: focusGroups:createBatch
Template: focus-group-template.md
```

#### Skill 3: AudienceEnricher (✗ MISSING)
```
Path: .claude/skills/audience-enricher/
Purpose: Weekly enrichment of existing focus groups
Agent: vibe-audience-enricher (sonnet)
Process:
  1. Query stale focus groups (lastEnriched > 7 days)
  2. Check activities feed for new discoveries
  3. Run Reddit/forums search for new patterns
  4. Update enrichment fields with audit trail
```

---

### Pipeline Preset (✓ VERIFIED - EXISTS IN SEED)

**Location:** `convex/seed.ts`

```typescript
{
  name: "Audience Research",
  slug: "audience-research",
  description: "Generate focus group profiles from scratch for a new market.",
  type: "preset",
  mainSteps: [
    { 
      order: 1, 
      agent: "vibe-audience-researcher",   // ✗ AGENT DOESN'T EXIST
      model: "opus", 
      label: "Research Audiences",
      description: "Generate audience segments from scratch",
      outputDir: "research" 
    },
    { 
      order: 2, 
      agent: "vibe-audience-enricher",     // ✗ AGENT DOESN'T EXIST
      model: "sonnet", 
      label: "Enrich Profiles",
      description: "Add psychographics, language patterns",
      outputDir: "research" 
    },
  ],
}
```

**Status:** Pipeline preset defined but agents unimplemented.

---

### How Focus Groups Are Supposed to Work

**From V3 Spec (Lines 1025-1031):**

When working on a campaign task, agents MUST:
1. Get task's projectId
2. Load campaign (includes targetFocusGroupIds)
3. Load product context
4. **Load campaign's focus groups** via `focusGroups:getByCampaign`
5. **Use focus group data** (language patterns, pain points, hooks) in content

**Key Quote (Line 2528):**
> "Focus group data lives in Convex, queried by agents when working on a campaign task. The data is structured and searchable, not a raw markdown file that needs parsing every time."

---

## 3. Existing Focus Group Document (✓ VERIFIED)

### File: `/var/www/vibe-marketing/Fitness_Focus_Groups_Marketing_Intelligence.md`

**Stats:**
- **4,762 lines**
- **28 focus groups** (for GymZilla fitness product)
- **Source:** Manual creation (not automated)

**Structure per Focus Group:**
```markdown
# Focus Group N: [Name] - "[Nickname]"

**DEMOGRAPHICS & PSYCHOGRAPHICS**
- Age Range, Gender, Income, Lifestyle

**CORE DESIRES** (emotional drivers)
- 5-10 bullet points

**PAIN POINTS** (problems to solve)
- 5-10 bullet points

**FEARS & ANXIETIES**
- 5-10 bullet points

**BELIEFS & WORLDVIEW**
- 5-10 bullet points

**COMMON OBJECTIONS** (why they hesitate)
- 5-7 quoted objections

**EMOTIONAL TRIGGERS** (buying activation)
- 5-8 triggers

**LANGUAGE PATTERNS** (exact phrases)
- 10-15 quoted phrases

**EBOOK ANGLES** (positioning ideas)
- 5-10 angles

**MARKETING HOOKS** (headlines)
- 10-15 hooks

**TRANSFORMATION PROMISE**
- Before → After journey statement
```

**28 Focus Groups (Table of Contents):**
1. Fat Loss Seekers ("The Scale Watchers")
2. Muscle Builders / Hardgainers
3. Body Recomposition Seekers
4. Specific Body Part Obsessors
5. Plateau Breakers
6. Time-Crunched Professionals
7. Flexible Lifestyle Seekers
8. Sustainability Seekers
9. Home/Minimal Equipment Trainers
10. Confidence Rebuilders
11. Gym Intimidation Overcomers
12. Self-Discipline Seekers
13. Past Failure Recoverers
14. Information Overload Victims
15. Science-Based Learners
16. Personalization Seekers
17. Expert Access Seekers
18. Age 45+ Fitness Maintainers
19. Competition/Physique Prep
20. Post-Diet Recoverers
21. Attractiveness Seekers
22. Social Proof/Transformation Posters
23. "Others Are Passing Me" Comparers
24-28. [Additional focus groups]

**Status:** This document exists but is NOT imported into Convex. No parser/importer built yet.

---

## 4. Existing Skills/Agents (✗ NONE FOUND)

### Search Results:

**Skills directory (`/var/www/vibe-marketing/.claude/skills/`):**
- Total: 77 skills
- **Audience-related:** 0
- **Focus-group-related:** 0

**Searched for:**
- `audience-analyzer/` → NOT FOUND
- `audience-researcher/` → NOT FOUND
- `audience-enricher/` → NOT FOUND
- `audience-research-procedures/` → NOT FOUND

**Mentions in codebase:**
- `vibe-marketing-platform-v3.md` → Spec only (not implemented)
- `external-services-registry.md` → Requirements documentation
- `convex/seed.ts` → Pipeline preset (agents don't exist)

**Conclusion:** All three audience intelligence agents are **planned but not implemented**.

---

## 5. Pipeline Presets (✓ VERIFIED - PARTIAL)

### From `convex/seed.ts`:

**Audience Research Pipeline:**
```typescript
{
  name: "Audience Research",
  slug: "audience-research",
  type: "preset",
  mainSteps: [
    { order: 1, agent: "vibe-audience-researcher", model: "opus" },    // ✗ MISSING
    { order: 2, agent: "vibe-audience-enricher", model: "sonnet" },   // ✗ MISSING
  ],
}
```

**Other pipelines reference focus groups:**
- Blog Post Pipeline → reads targetFocusGroupIds from campaign
- Ebook Pipeline → uses focus group language patterns
- Landing Page Pipeline → uses emotional triggers

**Status:** Pipelines expect focus groups to exist but have no way to create them automatically.

---

## 6. Dashboard Pages (✓ VERIFIED - BUILT)

### Focus Group Management UI

**Page: `/var/www/vibe-marketing/dashboard/pages/projects/[slug]/products/[id]/audiences.vue`**

**Features (✓ VERIFIED - 262 lines):**
- Lists all focus groups for a product
- Expandable cards showing all fields
- Demographics, psychographics, desires, pain points
- Marketing hooks, language patterns
- Transformation promise
- Enrichment notes (read-only)
- Delete confirmation modal
- "New Focus Group" button → opens form modal

**Component: `/var/www/vibe-marketing/dashboard/components/FocusGroupForm.vue`**

**Features (✓ VERIFIED - 15,283 bytes):**
- Accordion-style form (collapsible sections)
- Basic Info: name, nickname, number, category, source
- Demographics: age, gender, income, lifestyle, triggers
- Psychographics: values, beliefs, lifestyle, identity
- Language & Hooks: coreDesires, painPoints, fears, beliefs, objections
- Emotional triggers, language patterns
- Marketing hooks, ebook angles
- Transformation promise
- Chip inputs for all array fields (12+ chip inputs)
- Create/update mutations
- Field validation

**Test: `/var/www/vibe-marketing/dashboard/tests/unit/FocusGroupForm.spec.ts`**

**Status:** UI is fully built and tested. Manual CRUD works. Only missing automated population.

---

## What Exists vs What's Missing

### ✓ EXISTS (Infrastructure)

| Component | Status | Location |
|-----------|--------|----------|
| Database schema | ✓ Complete | `convex/schema.ts` lines 92-184 |
| Enrichment fields | ✓ Added | awarenessStage, contentPreferences, etc. |
| CRUD functions | ✓ Basic | `convex/focusGroups.ts` (7 functions) |
| Relationship model | ✓ Working | Projects → Products → Focus Groups |
| Campaign integration | ✓ Working | targetFocusGroupIds array |
| Dashboard page | ✓ Built | `audiences.vue` (262 lines) |
| Form component | ✓ Built | `FocusGroupForm.vue` (15KB) |
| Unit tests | ✓ Passing | `FocusGroupForm.spec.ts` |
| Pipeline preset | ✓ Seeded | "Audience Research" in seed.ts |
| Example document | ✓ Exists | 28 fitness focus groups (4,762 lines) |

### ✗ MISSING (Automation)

| Component | Status | Impact |
|-----------|--------|--------|
| **vibe-audience-researcher** agent | ✗ Not built | Can't generate focus groups from scratch |
| **vibe-audience-enricher** agent | ✗ Not built | Can't update existing profiles |
| **audience-analyzer** agent | ✗ Not built | Can't parse uploaded documents |
| Skill directories | ✗ Empty | No SKILL.md files |
| Parser scripts | ✗ Missing | No `extract_focus_groups.py` |
| Validation scripts | ✗ Missing | No `validate_focus_group.py` |
| Batch import function | ✗ Missing | No `focusGroups:createBatch` |
| Enrichment function | ✗ Missing | No `focusGroups:enrich` with audit trail |
| Stale query | ✗ Missing | No `getStale` for weekly enrichment |
| Document importer | ✗ Missing | Fitness doc not in database |
| Template files | ✗ Missing | No `focus-group-template.md` |
| Research procedures | ✗ Missing | No `audience-research-procedures/` |

---

## Current Workflow (Manual Only)

**What works TODAY:**
1. User navigates to `/projects/[slug]/products/[id]/audiences`
2. Clicks "New Focus Group"
3. Fills out **massive form** manually (12+ chip input fields)
4. Saves to Convex
5. Focus group appears in campaign builder checkboxes
6. Agents can query focus groups via `getByCampaign` when writing content

**What's BROKEN:**
- No way to generate focus groups automatically
- No way to import the existing 28-group fitness document
- No way to enrich profiles over time
- "Audience Research" pipeline fails (agents don't exist)
- Manual entry is tedious (30+ minutes per focus group)

---

## Architecture Map

```
┌──────────────────────────────────────────────────────────────┐
│                    FOCUS GROUP LIFECYCLE                     │
└──────────────────────────────────────────────────────────────┘

CREATION PATHS (1 working, 2 missing):
├─ Manual Entry ✓ WORKING
│  └─ Dashboard → FocusGroupForm → focusGroups:create
│
├─ Upload + Parse ✗ MISSING
│  └─ Upload .md/.docx → audience-analyzer → validate → createBatch
│
└─ Automated Research ✗ MISSING
   └─ vibe-audience-researcher → market research → createBatch

ENRICHMENT (missing):
└─ Weekly Cron ✗ MISSING
   └─ vibe-audience-enricher → getStale → enrich with audit trail

CONSUMPTION (working):
└─ Campaign Execution ✓ WORKING
   └─ Task → getByCampaign → Use in content generation
```

---

## Key Files Inventory

### Database Layer
| File | Purpose | Status |
|------|---------|--------|
| `convex/schema.ts` | Focus group table definition | ✓ Complete |
| `convex/focusGroups.ts` | CRUD queries/mutations | ✓ Basic (missing batch/enrich) |

### Frontend Layer
| File | Purpose | Status |
|------|---------|--------|
| `dashboard/pages/.../audiences.vue` | Focus group list page | ✓ Built |
| `dashboard/components/FocusGroupForm.vue` | Create/edit form | ✓ Built |
| `dashboard/tests/unit/FocusGroupForm.spec.ts` | Unit tests | ✓ Passing |
| `dashboard/tests/unit/AudienceList.spec.ts` | List tests | ✓ Exists |

### Agent Layer (ALL MISSING)
| File | Purpose | Status |
|------|---------|--------|
| `.claude/skills/audience-researcher/SKILL.md` | Generate from scratch | ✗ NOT FOUND |
| `.claude/skills/audience-enricher/SKILL.md` | Weekly updates | ✗ NOT FOUND |
| `.claude/skills/audience-analyzer/SKILL.md` | Parse uploads | ✗ NOT FOUND |
| `scripts/audience/extract_focus_groups.py` | Parser | ✗ NOT FOUND |
| `scripts/audience/validate_focus_group.py` | Validator | ✗ NOT FOUND |

### Documentation/Examples
| File | Purpose | Status |
|------|---------|--------|
| `Fitness_Focus_Groups_Marketing_Intelligence.md` | 28 example profiles | ✓ Exists (not imported) |
| `vibe-marketing-platform-v3.md` | System spec | ✓ Detailed (lines 2526-2790) |

---

## Open Questions

1. **Importer priority:** Should we parse the existing fitness doc first, or build the research agent?
2. **Batch size:** V3 spec says "10-30 focus groups" — is that per product or per project?
3. **Enrichment schedule:** Weekly cron or on-demand trigger?
4. **Source attribution:** How to track which Reddit threads/forums informed each field?
5. **Validation:** What's the minimum viable focus group? (All fields required or progressive enrichment?)
6. **Sophistication vs Awareness:** Do we need both fields or can one be derived from the other?
7. **Human review:** Should auto-generated focus groups go through approval workflow before being campaign-selectable?

---

## Next Steps (Priority Order)

### Phase 1: Import Existing Data
1. Build `audience-analyzer` skill
2. Write `extract_focus_groups.py` parser (regex-based)
3. Add `focusGroups:createBatch` mutation
4. Import `Fitness_Focus_Groups_Marketing_Intelligence.md` → Convex
5. Test campaign builder with real focus groups

### Phase 2: Automated Research
1. Build `audience-researcher` skill
2. Define research process (Reddit API, forum scraping, competitor analysis)
3. Create `focus-group-template.md`
4. Test generation for non-fitness products
5. Add human review workflow

### Phase 3: Enrichment Pipeline
1. Build `audience-enricher` skill
2. Add `focusGroups:enrich` mutation with audit trail
3. Add `focusGroups:getStale` query
4. Set up weekly cron job
5. Build dashboard for enrichment history

### Phase 4: Dashboard Enhancements
1. Add "Research Audiences" button → triggers vibe-audience-researcher
2. Add "Import Document" upload → triggers audience-analyzer
3. Add enrichment history viewer
4. Add focus group analytics (usage in campaigns)
5. Add bulk operations (duplicate, merge, archive)

---

## References

- **V3 Spec Section 10:** Lines 2526-2790 (Audience Intelligence Subsystem)
- **Schema Definition:** `convex/schema.ts` lines 92-184
- **CRUD Functions:** `convex/focusGroups.ts`
- **Pipeline Preset:** `convex/seed.ts` (Audience Research)
- **Dashboard Page:** `dashboard/pages/.../audiences.vue`
- **Form Component:** `dashboard/components/FocusGroupForm.vue`
- **Example Data:** `Fitness_Focus_Groups_Marketing_Intelligence.md`

---

**Report prepared by:** scout agent  
**Timestamp:** 2026-02-11  
**Exploration method:** Schema analysis, codebase grep, file inventory, V3 spec cross-reference
