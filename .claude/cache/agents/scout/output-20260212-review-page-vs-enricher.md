# Codebase Report: Review Page Fields vs Enricher Agent Analysis
Generated: 2026-02-12

## Summary
Analysis of what data is displayed on the staging review page vs what exists in the schema vs what the enricher agent adds.

---

## 1. Review Page Fields Displayed

### Location
`/var/www/vibe-marketing/dashboard/pages/projects/[slug]/audiences/review.vue`

### Fields Shown Per Staged Focus Group

**Card Header (always visible):**
- `name` (line 251)
- `nickname` (line 252)
- `reviewStatus` (line 257)
- `completenessScore` (line 261-262)
- `overview` (line 286, truncated to 2 lines)
- `missingFields[]` (line 288-295)

**Expanded Preview (click to reveal):**
- `demographics.ageRange` (line 302)
- `demographics.gender` (line 303)
- `demographics.income` (line 304)
- `demographics.lifestyle` (line 305)
- `coreDesires[]` (line 307-312, shown as tags)
- `painPoints[]` (line 313-318, shown as tags)
- `marketingHooks[]` (line 319-324, shown as tags)
- `transformationPromise` (line 325-328, shown as quote)

---

## 2. focusGroupStaging Schema Fields

### Location
`/var/www/vibe-marketing/convex/schema.ts` (lines 199-319)

### All Available Fields

**Context/Metadata:**
- `taskId` (v.id)
- `productId` (optional v.id)
- `projectId` (v.id)
- `sourceDocumentId` (optional v.id)

**Match Resolution:**
- `matchStatus` (union: create_new | enrich_existing | possible_match | skip)
- `matchedFocusGroupId` (optional v.id)
- `matchConfidence` (optional number)
- `matchReason` (optional string)

**Review Status:**
- `reviewStatus` (union: pending_review | approved | rejected | edited | imported)
- `reviewNotes` (optional string)
- `reviewedAt` (optional number)

**Completeness Tracking:**
- `completenessScore` (number)
- `missingFields` (array of strings)
- `needsEnrichment` (boolean)

**Core Focus Group Fields (from parser):**
- `number` (optional number)
- `name` (string, required)
- `nickname` (optional string)
- `category` (optional string)
- `overview` (optional string)
- `demographics` (optional object)
  - `ageRange` (string)
  - `gender` (string)
  - `income` (string)
  - `lifestyle` (string)
  - `triggers` (array of strings)
- `psychographics` (optional object)
  - `values` (array of strings)
  - `beliefs` (array of strings)
  - `lifestyle` (string)
  - `identity` (string)
- `coreDesires` (optional array of strings)
- `painPoints` (optional array of strings)
- `fears` (optional array of strings)
- `beliefs` (optional array of strings)
- `objections` (optional array of strings)
- `emotionalTriggers` (optional array of strings)
- `languagePatterns` (optional array of strings)
- `ebookAngles` (optional array of strings)
- `marketingHooks` (optional array of strings)
- `transformationPromise` (optional string)
- `source` (optional union: uploaded | researched | manual)

**Enrichment Fields (added by enricher agent):**
- `awarenessStage` (optional union: unaware | problem_aware | solution_aware | product_aware | most_aware)
- `awarenessConfidence` (optional union: high | medium | low)
- `awarenessStageSource` (optional union: auto | manual)
- `awarenessSignals` (optional object)
  - `beliefsSignal` (optional string)
  - `objectionsSignal` (optional string)
  - `languageSignal` (optional string)
- `contentPreferences` (optional object)
  - `preferredFormats` (optional array of strings)
  - `attentionSpan` (optional string)
  - `tonePreference` (optional string)
- `influenceSources` (optional object)
  - `trustedVoices` (optional array of strings)
  - `mediaConsumption` (optional array of strings)
  - `socialPlatforms` (optional array of strings)
- `purchaseBehavior` (optional object)
  - `buyingTriggers` (optional array of strings)
  - `priceRange` (optional string)
  - `decisionProcess` (optional string)
  - `objectionHistory` (optional array of strings)
- `competitorContext` (optional object)
  - `currentSolutions` (optional array of strings)
  - `switchMotivators` (optional array of strings)
- `sophisticationLevel` (optional union: stage1 | stage2 | stage3 | stage4 | stage5)
- `communicationStyle` (optional object)
  - `formalityLevel` (optional string)
  - `humorReceptivity` (optional string)
  - `storyPreference` (optional string)
  - `dataPreference` (optional string)
- `seasonalContext` (optional object)
  - `peakInterestPeriods` (optional array of strings)
  - `lifeEvents` (optional array of strings)
  - `cyclicalBehaviors` (optional array of strings)
- `negativeTriggers` (optional object)
  - `dealBreakers` (optional array of strings)
  - `offensiveTopics` (optional array of strings)
  - `toneAversions` (optional array of strings)
- `researchNotes` (optional string)

---

## 3. What The Enricher Agent Adds

### Location
`.claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md`

### Working Memory
`/var/www/vibe-marketing/memory/WORKING/vibe-audience-enricher.md`

### Enrichment Categories

**A. Deterministic Fields (via Python scripts):**

1. **awarenessStage** (via `infer_awareness.py`)
   - Classifies as: unaware | problem_aware | solution_aware | product_aware | most_aware
   - Uses: beliefs, objections, languagePatterns
   
2. **awarenessConfidence** (via `infer_awareness.py`)
   - Classifies as: high | medium | low
   - Based on signal convergence
   
3. **awarenessStageSource** (via `infer_awareness.py`)
   - Always set to: "auto" (vs "manual" for human override)
   
4. **awarenessSignals** (via `infer_awareness.py`)
   - Object with: beliefsSignal, objectionsSignal, languageSignal
   - Explains what indicators were used for classification
   
5. **sophisticationLevel** (via `infer_sophistication.py`)
   - Classifies as: stage1 | stage2 | stage3 | stage4 | stage5
   - Uses: marketingHooks (required) + languagePatterns (optional)
   
6. **purchaseBehavior** (via `infer_purchase_behavior.py`)
   - Object with: buyingTriggers, priceRange, decisionProcess, objectionHistory
   - Uses: demographics (for priceRange), objections (for history)

**B. LLM-Inferred Fields:**

7. **contentPreferences**
   - Object: preferredFormats, attentionSpan, tonePreference
   - Requires: psychographics.identity + psychographics.lifestyle
   
8. **influenceSources**
   - Object: trustedVoices, mediaConsumption, socialPlatforms
   - Requires: psychographics + demographics.lifestyle
   
9. **competitorContext**
   - Object: currentSolutions, switchMotivators
   - Requires: painPoints + objections + beliefs
   
10. **communicationStyle**
    - Object: formalityLevel, humorReceptivity, storyPreference, dataPreference
    - Requires: languagePatterns + psychographics
    
11. **seasonalContext**
    - Object: peakInterestPeriods, lifeEvents, cyclicalBehaviors
    - Requires: demographics.triggers + psychographics.lifestyle
    
12. **negativeTriggers**
    - Object: dealBreakers, offensiveTopics, toneAversions
    - Requires: objections + fears + beliefs

### Recent Run Performance
From `/var/www/vibe-marketing/memory/WORKING/vibe-audience-enricher.md`:

- **Date:** 2026-02-12
- **Records Enriched:** 28/28 (100% success)
- **Deterministic Fields:** 6 fields × 28 records = 168 enrichments
- **LLM Fields:** 6 fields × 28 records = 168 enrichments
- **Total Enrichments:** 336

**Awareness Distribution:**
- problem_aware: 7 groups
- solution_aware: 7 groups
- product_aware: 4 groups
- most_aware: 5 groups
- unaware: 0 groups

**Sophistication Distribution:**
- stage1: 16 groups (most common)
- stage2: 6 groups
- stage3: 2 groups
- stage4: 1 group
- stage5: 0 groups

---

## 4. Fields in Schema NOT Shown on Review Page

The following fields exist in `focusGroupStaging` schema but are NOT displayed on the review page:

### Core Fields (from parser) Not Shown:
- `number` - focus group number
- `category` - group category
- `demographics.triggers[]` - demographic triggers
- `psychographics.values[]` - values
- `psychographics.beliefs[]` - beliefs
- `psychographics.lifestyle` - lifestyle description
- `psychographics.identity` - identity description
- `fears[]` - fears array
- `beliefs[]` - beliefs array
- `objections[]` - objections array
- `emotionalTriggers[]` - emotional triggers
- `languagePatterns[]` - language patterns
- `ebookAngles[]` - ebook angles
- `source` - source type (uploaded/researched/manual)

### Enrichment Fields Not Shown:
- `awarenessStage` - awareness classification
- `awarenessConfidence` - confidence level
- `awarenessStageSource` - auto vs manual
- `awarenessSignals` - what signals indicated this classification
- `contentPreferences` - preferred formats, attention span, tone
- `influenceSources` - trusted voices, media, social platforms
- `purchaseBehavior` - buying triggers, price range, decision process
- `competitorContext` - current solutions, switch motivators
- `sophisticationLevel` - sophistication stage
- `communicationStyle` - formality, humor, story, data preferences
- `seasonalContext` - peak periods, life events, cyclical behaviors
- `negativeTriggers` - deal breakers, offensive topics, tone aversions
- `researchNotes` - research notes

### Metadata Not Shown:
- `reviewNotes` - notes from reviewer
- `reviewedAt` - timestamp of review
- `needsEnrichment` - boolean flag

---

## 5. Gap Analysis

### What's Visible on Review Page
**8 fields shown** out of 50+ available fields (16% visibility)

The review page shows only the most essential fields for quick human review:
- Basic identity (name, nickname, overview)
- Review workflow (status, completeness, missing fields)
- Core marketing data (demographics, desires, pain points, hooks, transformation)

### What's Hidden from Review
**42+ fields** including ALL enrichment data:
- All 12 enrichment fields added by the enricher agent
- Most parser-extracted fields (fears, beliefs, objections, language patterns, etc.)
- Psychographics details
- Demographic triggers

### Implications
1. **Human reviewers cannot see enrichment quality** - They approve/reject based on parser output only
2. **No visibility into awareness/sophistication classification** - Critical marketing strategy fields are invisible
3. **Enrichment happens in "black box"** - Users don't see what the enricher added until after import
4. **Preview is minimal** - Even expanded view shows <20% of available data

### Recommended Action
Consider adding an "Enrichment Details" collapsible section showing:
- Awareness stage + confidence + signals
- Sophistication level
- Purchase behavior insights
- Content/communication preferences
- Competitor context

This would let reviewers validate enrichment quality before approving import.

---

## Key Files Referenced

| File | Purpose | Lines |
|------|---------|-------|
| `/var/www/vibe-marketing/dashboard/pages/projects/[slug]/audiences/review.vue` | Review page UI | 477 |
| `/var/www/vibe-marketing/convex/schema.ts` | focusGroupStaging schema definition | 199-319 |
| `/var/www/vibe-marketing/.claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md` | Enricher agent skill definition | 42 |
| `/var/www/vibe-marketing/.claude/skills/audience-enrichment-procedures/references/enrichment-protocol.md` | Enrichment rules and confidence thresholds | 73 |
| `/var/www/vibe-marketing/memory/WORKING/vibe-audience-enricher.md` | Last run results | 53 |

---

## Enrichment Scripts

Located in `.claude/skills/audience-enrichment-procedures/scripts/`:

1. `infer_awareness.py` - Classifies awareness stage using beliefs/objections/language
2. `infer_sophistication.py` - Classifies sophistication level using marketing hooks
3. `infer_purchase_behavior.py` - Infers buying behavior from demographics/objections
4. `scan_recent_mentions.py` - Scans Convex activities for agent discoveries
5. `update_focus_group.sh` - Shell wrapper for Convex updates

All scripts are deterministic (no LLM calls) for speed and consistency.

---

## Enrichment Input Requirements

From `.claude/skills/audience-enrichment-procedures/references/enrichment-protocol.md`:

| Enrichment Field | Required Input Fields |
|-----------------|----------------------|
| awarenessStage | beliefs OR objections (ideally both + languagePatterns) |
| sophisticationLevel | marketingHooks (required) + languagePatterns (optional) |
| purchaseBehavior | demographics (for priceRange) + objections (for history) |
| contentPreferences | psychographics.identity + psychographics.lifestyle |
| communicationStyle | languagePatterns + psychographics |
| competitorContext | painPoints + objections + beliefs |
| influenceSources | psychographics + demographics.lifestyle |
| seasonalContext | demographics.triggers + psychographics.lifestyle |
| negativeTriggers | objections + fears + beliefs |

**Key Insight:** Enricher cannot run without parser first extracting these base fields.
