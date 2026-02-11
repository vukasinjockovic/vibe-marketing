# Implementation Report: Convex Function Modules
Generated: 2026-02-11

## Task
Build 5 Convex function modules (products, focusGroups, campaigns, tasks, pipelines) following existing patterns from convex/projects.ts.

## Validation

### Type Check Results
- `npx tsc --noEmit --project convex/tsconfig.json` -- zero errors in all 5 new files
- `npx convex codegen` -- all 5 modules registered in generated API types
- Pre-existing errors in auth.ts/admin.ts (7 errors) were NOT introduced by this work

## Files Created

### 1. convex/products.ts (6 functions)
- `list` query: by projectId (by_project index)
- `get` query: by id
- `getBySlug` query: by slug (by_slug index)
- `create` mutation: all required fields, status defaults to "active", slug uniqueness check
- `update` mutation: partial updates (name, description, context, brandVoice)
- `archive` mutation: sets status to "archived"

### 2. convex/focusGroups.ts (7 functions)
- `listByProject` query: by projectId (by_project index)
- `listByProduct` query: by productId (by_product index)
- `get` query: by id
- `getByCampaign` query: loads campaign, resolves targetFocusGroupIds via ctx.db.get()
- `create` mutation: all schema fields
- `update` mutation: partial updates on all editable fields
- `remove` mutation: deletes the record

### 3. convex/campaigns.ts (8 functions)
- `list` query: by projectId (by_project index)
- `get` query: by id
- `getBySlug` query: by slug (by_slug index)
- `listActive` query: by status "active" (by_status index)
- `create` mutation: all required fields, status defaults to "planning", slug uniqueness check
- `update` mutation: partial updates (name, description, notes, seedKeywords, competitorUrls, deliverableConfig, skillConfig, publishConfig)
- `activate` mutation: status="active", activatedAt=Date.now()
- `pause` mutation: status="paused", pausedAt=Date.now()
- `complete` mutation: status="completed", completedAt=Date.now()

### 4. convex/tasks.ts (9 functions)
- `listByProject` query: by projectId (by_project index)
- `listByCampaign` query: by campaignId (by_campaign index)
- `listByStatus` query: by projectId+status (by_project_status index)
- `get` query: by id
- `create` mutation: all required fields, status defaults to "backlog", pipelineStep=0, empty arrays for subscribers/assignees
- `update` mutation: partial updates on all mutable fields
- `updateStatus` mutation: status only
- `assignAgent` mutation: adds to assigneeNames (deduped), sets lockedBy/lockedAt
- `unassign` mutation: clears lockedBy/lockedAt
- `subscribe` mutation: adds to subscriberNames (deduped)
- `unsubscribe` mutation: removes from subscriberNames

### 5. convex/pipelines.ts (6 functions)
- `list` query: all pipelines
- `listPresets` query: by type "preset" (by_type index)
- `get` query: by id
- `getBySlug` query: by slug (by_slug index)
- `create` mutation: all fields, slug uniqueness check
- `fork` mutation: loads original, creates copy with type="custom" and forkedFrom set

## Patterns Followed
- Imports: `query`/`mutation` from "./_generated/server", `v` from "convex/values"
- No internal functions (only auth/admin use those)
- Slug uniqueness checks on create (products, campaigns, pipelines)
- Partial update pattern: iterate Object.entries, skip undefined
- Index usage matches schema.ts definitions exactly
- Brief single-line comments on each function
- No _creationTime or _id fields in inserts

## Total Function Count
36 functions across 5 modules (19 queries + 17 mutations)
