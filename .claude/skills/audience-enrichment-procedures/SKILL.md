---
name: audience-enrichment-procedures
displayName: Audience Enrichment Procedures
description: SOP for vibe-audience-enricher agent. Fills missing enrichment fields on focus groups using inference from existing data and external research. Works in pipeline mode (staging records) and heartbeat mode (production records weekly).
category: audience
type: procedure
---

# Audience Enrichment Procedures

You are the `vibe-audience-enricher` agent (sonnet model). Your job is to fill missing enrichment fields on focus groups using deterministic inference scripts and, when needed, LLM reasoning. You operate in two modes: pipeline mode (enriching staging records during import) and heartbeat mode (weekly enrichment of production records).

Read `vibe-audience-enricher.md` in this skill directory for your identity, service dependencies, and Convex function reference.

---

## Execution Protocol

### Step 0: Load Context

1. Read this SKILL.md
2. Read `memory/WORKING/vibe-audience-enricher.md` for current state
3. Determine which mode you are in:
   - **Pipeline mode:** You have a `taskId` -- a pipeline step assigned to you
   - **Heartbeat mode:** No taskId -- you are running on schedule
4. Load project context from the task or from your heartbeat config

---

## Mode A: Pipeline Mode

Runs after a document parse or audience research step. You enrich staging records before they go to human review.

### Step A1: Acquire Lock

```bash
npx convex run pipeline:acquireLock '{"taskId":"<taskId>","agentName":"vibe-audience-enricher"}' --url http://localhost:3210
```

If lock not acquired, exit cleanly. Another instance is already running.

### Step A2: Load Staging Records

```bash
npx convex run focusGroupStaging:listByTask '{"taskId":"<taskId>"}' --url http://localhost:3210
```

Filter for records where `needsEnrichment: true`.

### Step A3: Enrich Each Staging Record

For each record with `needsEnrichment: true`:

#### A3a: Run Deterministic Inference Scripts

Run the Python scripts on the record data. Pipe the record JSON to each script.

**Awareness Stage** (if beliefs or objections present):
```bash
echo '<record_json>' | python3 .claude/skills/audience-enrichment-procedures/scripts/infer_awareness.py
```
Output: `{awarenessStage, awarenessConfidence, awarenessStageSource, awarenessSignals, reasoning}`

**Sophistication Level** (if marketingHooks present):
```bash
echo '<record_json>' | python3 .claude/skills/audience-enrichment-procedures/scripts/infer_sophistication.py
```
Output: `{sophisticationLevel, confidence, reasoning}`

**Purchase Behavior** (if demographics present):
```bash
echo '<record_json>' | python3 .claude/skills/audience-enrichment-procedures/scripts/infer_purchase_behavior.py
```
Output: `{purchaseBehavior: {buyingTriggers, priceRange, decisionProcess, objectionHistory}, confidence, reasoning}`

#### A3b: LLM Inference for Complex Fields

For fields that require contextual reasoning (not deterministic keyword matching), use your own LLM capability to infer:

- **contentPreferences** (from psychographics.identity + lifestyle):
  - preferredFormats: what content formats resonate
  - attentionSpan: short/medium/long
  - tonePreference: casual/professional/authoritative/empathetic

- **communicationStyle** (from languagePatterns + psychographics):
  - formalityLevel: casual/semi-formal/formal
  - humorReceptivity: high/medium/low
  - storyPreference: high/medium/low
  - dataPreference: high/medium/low

- **competitorContext** (from painPoints + objections + beliefs):
  - currentSolutions: what they're currently using
  - switchMotivators: what would make them switch

- **negativeTriggers** (from objections + fears + beliefs):
  - dealBreakers: what would stop them from buying
  - offensiveTopics: topics to avoid
  - toneAversions: tones that repel them

Only infer these fields if the required input data exists. See `references/enrichment-protocol.md` for prerequisites.

#### A3c: Update Staging Record

Collect all inferred fields into a single update:

```bash
npx convex run focusGroupStaging:updateFields '{"id":"<stagingId>","awarenessStage":"problem_aware","awarenessConfidence":"high",...}' --url http://localhost:3210
```

### Step A4: Register Resource + Complete Pipeline Step

Register an enrichment report resource, then complete the step:

```bash
# Write enrichment summary to file
# File: projects/{project-slug}/research/enrichment-report-{timestamp}.md

HASH=$(sha256sum "<reportFilePath>" | cut -d' ' -f1)
RESOURCE_ID=$(npx convex run resources:create '{
  "projectId":"<PROJECT_ID>",
  "resourceType":"report",
  "title":"Enrichment Report: <N> staging records",
  "taskId":"<taskId>",
  "filePath":"<reportFilePath>",
  "contentHash":"'$HASH'",
  "status":"draft",
  "pipelineStage":"research",
  "createdBy":"vibe-audience-enricher",
  "metadata":{"enrichedCount":N,"totalCount":M,"fieldsEnriched":["awarenessStage","sophisticationLevel"]}
}' --url http://localhost:3210)

npx convex run pipeline:completeStep '{"taskId":"<taskId>","agentName":"vibe-audience-enricher","qualityScore":7,"resourceIds":["'$RESOURCE_ID'"]}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for full protocol.

### Step A5: Update Memory

Write results to `memory/WORKING/vibe-audience-enricher.md`.

---

## Mode B: Heartbeat Mode

Runs weekly. Enriches production focus group records that are missing fields or stale (>7 days since last enrichment).

### Step B1: Find Groups Needing Enrichment

```bash
npx convex run focusGroups:listNeedingEnrichment '{"projectId":"<projectId>"}' --url http://localhost:3210
```

### Step B2: Check What Is Missing

For each group:
```bash
npx convex run focusGroups:getEnrichmentProgress '{"id":"<focusGroupId>"}' --url http://localhost:3210
```

This returns `{filledCount, totalCount, score, missingFields}`.

### Step B3: Scan for Agent Discoveries

Check if other agents learned anything relevant since last enrichment:
```bash
python3 .claude/skills/audience-enrichment-procedures/scripts/scan_recent_mentions.py <projectId> --days 7
```

### Step B4: Enrich Missing Fields

For each missing field:

1. Check if the required input data exists (see `references/enrichment-protocol.md`)
2. If yes, run the appropriate inference script or LLM inference
3. Collect all updates

**CRITICAL:** In heartbeat mode, NEVER overwrite non-null fields. The `focusGroups:enrich` function handles the audit trail, but you must only send fields that are currently null/undefined on the record.

### Step B5: Update Production Record

Use the enrichment wrapper script:
```bash
.claude/skills/audience-enrichment-procedures/scripts/update_focus_group.sh \
  "<focusGroupId>" \
  '{"awarenessStage":"problem_aware","awarenessConfidence":"high","awarenessStageSource":"auto"}' \
  "vibe-audience-enricher" \
  "Matched 4 indicators for problem_aware: beliefs contain struggling, stuck; objections contain nothing works"
```

Or call Convex directly:
```bash
npx convex run focusGroups:enrich '{"id":"<id>","fields":{...},"agentName":"vibe-audience-enricher","reasoning":"..."}' --url http://localhost:3210
```

### Step B6: Log Activity

```bash
npx convex run activities:log '{"projectId":"<projectId>","type":"enrichment","agentName":"vibe-audience-enricher","content":"Enriched N focus groups. Updated fields: ..."}' --url http://localhost:3210
```

### Step B7: Update Memory

Write results to `memory/WORKING/vibe-audience-enricher.md` and project-scoped memory.

---

## Enrichment Field Reference

All enrichment fields defined in the schema (see `convex/schema.ts` focusGroups table):

| Field | Type | Weight | Script |
|-------|------|--------|--------|
| awarenessStage | enum: unaware, problem_aware, solution_aware, product_aware, most_aware | 15 | infer_awareness.py |
| awarenessConfidence | enum: high, medium, low | -- | infer_awareness.py |
| awarenessStageSource | enum: auto, manual | -- | infer_awareness.py |
| awarenessSignals | {beliefsSignal?, objectionsSignal?, languageSignal?} | 5 | infer_awareness.py |
| sophisticationLevel | enum: stage1-stage5 | 10 | infer_sophistication.py |
| purchaseBehavior | {buyingTriggers?, priceRange?, decisionProcess?, objectionHistory?} | 15 | infer_purchase_behavior.py |
| contentPreferences | {preferredFormats?, attentionSpan?, tonePreference?} | 10 | LLM |
| influenceSources | {trustedVoices?, mediaConsumption?, socialPlatforms?} | 10 | LLM |
| competitorContext | {currentSolutions?, switchMotivators?} | 10 | LLM |
| communicationStyle | {formalityLevel?, humorReceptivity?, storyPreference?, dataPreference?} | 10 | LLM |
| seasonalContext | {peakInterestPeriods?, lifeEvents?, cyclicalBehaviors?} | 5 | LLM |
| negativeTriggers | {dealBreakers?, offensiveTopics?, toneAversions?} | 10 | LLM |

Total enrichment score: 100 points. See `focusGroups:getEnrichmentProgress` for scoring.

---

## Reference Documents

Read these for detailed classification guidance:

- `references/enrichment-protocol.md` -- Validation rules, confidence criteria, operational guardrails
- `references/awareness-classification.md` -- Detailed guide to 5 Schwartz awareness stages
- `references/sophistication-classification.md` -- Market sophistication stages 1-5
- `references/enrichment-sources.md` -- Where enrichment data comes from, priority order

---

## Rules

1. **Pipeline contract:** ALWAYS acquireLock before starting, ALWAYS completeStep as last action
2. **Never overwrite non-null in heartbeat mode** -- only fill empty fields
3. **Always include reasoning** -- every enrichment must explain its basis
4. **Confidence thresholds:** high (3+ indicators), medium (2), low (1)
5. **Skip when no data** -- a null field beats a wrong field
6. **Log everything** -- use activities:log and enrichments[] audit trail
7. **Use scripts for deterministic fields** -- awarenessStage, sophisticationLevel, purchaseBehavior
8. **Use LLM for contextual fields** -- contentPreferences, communicationStyle, competitorContext, etc.
9. **Check SERVICE_REGISTRY.md** before external research -- honor service priority
10. **Update memory** -- always write to WORKING memory after completion
