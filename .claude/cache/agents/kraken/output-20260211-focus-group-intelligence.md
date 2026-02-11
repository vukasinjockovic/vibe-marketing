# Implementation Report: Phase 1 -- Convex Foundation for Focus Group Intelligence System
Generated: 2026-02-11T19:45:00Z

## Task
Build the Convex backend for the Focus Group Intelligence System: schema changes, new staging module, extended focusGroups module, and seed update.

## Changes Made

### 1. Schema Changes (`convex/schema.ts`)

**A. Added `focusGroupStaging` table** (after existing `focusGroups` table):
- Full staging schema with context fields (taskId, productId, projectId, sourceDocumentId)
- Match resolution fields (matchStatus, matchedFocusGroupId, matchConfidence, matchReason)
- Review workflow fields (reviewStatus, reviewNotes, reviewedAt)
- Completeness tracking (completenessScore, missingFields, needsEnrichment)
- All focus group fields as optional (for partial data from parsing)
- All enrichment fields copied from focusGroups schema
- 4 indexes: by_task, by_product, by_project, by_review_status

**B. Added `by_name` index to existing focusGroups table:**
- `.index("by_name", ["productId", "name"])` for efficient exact-match lookup

### 2. New Module: `convex/focusGroupStaging.ts`

**Queries:**
- `listByTask(taskId)` - All staging records for a task (uses by_task index)
- `listByProduct(productId)` - All staging records for a product (uses by_product index)
- `listPendingReview(taskId)` - Only pending_review records for a task
- `get(id)` - Single staging record
- `getSummary(taskId)` - Returns { total, pending, approved, rejected, needsEnrichment }

**Mutations:**
- `createFromParsed(data)` - Insert a single parsed focus group with all fields
- `createBatch(groups[])` - Insert multiple parsed focus groups, returns array of IDs
- `updateReviewStatus(id, status, notes?)` - Approve/reject/edit with timestamp
- `updateFields(id, fields)` - Update any focus group fields (partial update pattern)
- `bulkApprove(ids[])` - Approve multiple at once
- `bulkReject(ids[])` - Reject multiple at once

### 3. Extended Module: `convex/focusGroups.ts`

**New Queries:**
- `findByName(productId, name)` - Exact match using by_name index
- `findByNickname(productId, nickname)` - Case-insensitive nickname search
- `searchByName(productId, query)` - Partial name match (case-insensitive)
- `listNeedingEnrichment(projectId)` - Focus groups where lastEnriched is null or >7 days ago
- `getEnrichmentProgress(id)` - Weighted scoring (100 points total) with filledCount, totalCount, score, missingFields

**New Mutations:**
- `createBatch(groups[])` - Insert multiple focus groups, return array of IDs
- `enrich(id, fields, agentName, reasoning)` - Update enrichment fields + append to enrichments[] audit trail + update lastEnriched
- `enrichBatch(updates[])` - Batch version of enrich
- `importFromStaging(stagingIds[])` - Imports approved staging records:
  - create_new: inserts new focusGroup with defaults for missing fields
  - enrich_existing: merges into matched focusGroup with smart logic:
    - Array fields: union (add new items, deduplicate case-insensitively)
    - String fields: keep existing unless empty
    - Object fields: deep merge (fill missing sub-fields)
    - Enrichment fields: only overwrite if existing is null
  - All operations append to enrichments[] audit trail
  - Returns { created: number, enriched: number }

### 4. Seed Update (`convex/seed.ts`)

Added "Document Import" pipeline preset:
- Steps: Created -> Parse Document (vibe-audience-parser, sonnet) -> Enrich Profiles (vibe-audience-enricher, sonnet)
- onComplete: telegram + summary, no manifest generation

Ensured "Audience Discovery" preset references correct agents (vibe-audience-researcher opus, vibe-audience-enricher sonnet).

## Verification Results

All tests run against live Convex instance at localhost:3210:

| Test | Result |
|------|--------|
| Deploy schema (new table + index) | PASS - 5 indexes created |
| createFromParsed | PASS - Returns staging ID |
| createBatch (staging) | PASS - Returns array of 2 IDs |
| getSummary | PASS - Correct counts { total:2, pending:2, approved:0, rejected:0, needsEnrichment:2 } |
| listPendingReview | PASS - Returns only pending records |
| updateReviewStatus | PASS - Updates status + timestamp |
| bulkApprove | PASS - Approves multiple records |
| bulkReject | PASS - Rejects multiple records |
| updateFields | PASS - Partial update of name, category, overview |
| importFromStaging (create_new) | PASS - Created 2 focus groups from staging |
| importFromStaging (enrich_existing) | PASS - Merged painPoints (4 items from 2+3 with dedup), filled influenceSources |
| Staging records marked "imported" | PASS |
| findByName (by_name index) | PASS - Exact match returns single result |
| findByNickname (case-insensitive) | PASS - "the bulkers" matches "The Bulkers" |
| searchByName (partial) | PASS - "loss" matches "Fat Loss Seekers" |
| enrich | PASS - Updates fields + appends to enrichments[] audit trail |
| getEnrichmentProgress | PASS - Score 35 (3 fields) -> 45 (4 fields) after merge |
| listNeedingEnrichment | PASS - Returns empty (all recently enriched) |

## Files Modified
1. `/var/www/vibe-marketing/convex/schema.ts` - Added focusGroupStaging table + by_name index on focusGroups
2. `/var/www/vibe-marketing/convex/focusGroupStaging.ts` - NEW: Complete staging CRUD module (5 queries, 6 mutations)
3. `/var/www/vibe-marketing/convex/focusGroups.ts` - Extended with 5 new queries + 4 new mutations
4. `/var/www/vibe-marketing/convex/seed.ts` - Added Document Import pipeline preset

## Notes
- The seed file is idempotent: the Document Import preset will only be seeded on fresh databases. Existing databases need a manual pipeline creation or re-seed.
- The `importFromStaging` function handles both `create_new` and `enrich_existing` merge strategies with full audit trail tracking.
- Array field merging is case-insensitive to prevent near-duplicate entries.
- The enrichment weight system totals 100 points across 10 fields for intuitive scoring.
