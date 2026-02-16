# Plan: Batch Detail Page Enhancements

## Overview
Three features for the content batch detail page:
1. **Edit batch** (when status = planning)
2. **Clickable resource stats** → filtered resource table below
3. **Resource detail modal** → full resource view without leaving the page

---

## Part A: Edit Batch (status = planning)

### A1. `convex/contentBatches.ts` — status guard (line ~142)
Add to `update` handler, before the patch:
```ts
if (batch.status !== 'planning') {
  throw new Error("Cannot edit a batch that is no longer in planning status");
}
```

### A2. `dashboard/components/ContentBatchForm.vue` — edit mode
Follow the ProductForm pattern:
- Add optional `batch?: any` prop
- Add `isEdit = computed(() => !!props.batch)`
- Add `useConvexMutation(api.contentBatches.update)` for edit
- Pre-populate `form` reactive from `props.batch` (name, slug, description, batchSize, pipelineId, targetFocusGroupIds, contentThemes as comma string, notes, mediaConfig)
- Auto-slug watch: only run when `!isEdit.value`
- Auto-select watchers: only run when `!form.channelId` (already do this)
- Disable channel select + slug input in edit mode (`:disabled="isEdit"`)
- In `submit()`: branch on `isEdit` — call update with `{ id: props.batch._id, ...fields }` instead of create
- Button text: `isEdit ? 'Save Changes' : 'Create Batch'`
- Emit `saved` (rename from `created`) on success in both modes

### A3. `dashboard/pages/.../batches/[id].vue` — edit button + modal
- Add `showEditModal = ref(false)`
- Add Edit button next to Activate (only when `batch.status === 'planning'`)
- Add `<VModal v-model="showEditModal" title="Edit Batch" size="xl">` containing `<ContentBatchForm :batch="batch" :project-id="batch.projectId" @saved="showEditModal = false" />`

---

## Part B: Clickable Resource Stats → Filtered Table

### B1. `dashboard/components/ResourceStatsCards.vue` — emit click
- Add emit: `selectType: [type: string | null]`
- Add prop: `activeType?: string | null` (to highlight the active card)
- Make each type card a `<button>` with `@click="emit('selectType', item.type)"`
- Make the "Total" card clickable too: `@click="emit('selectType', null)"` (clears filter)
- Active card styling: ring/border highlight when `activeType === item.type`
- Cursor pointer on all cards

### B2. `dashboard/pages/.../batches/[id].vue` — wire stats → table
- Add `selectedResourceType = ref<string | null>(null)`
- Pass `activeType` to ResourceStatsCards, handle `@selectType`
- Replace the current `<ResourceTable :content-batch-id="batchId">` with a conditional:
  - When `selectedResourceType` is set, pass `:resource-type="selectedResourceType"`
  - ResourceTable already supports `resourceType` prop but only with `projectId`, not `contentBatchId`

### B3. `dashboard/components/ResourceTable.vue` — support contentBatchId + resourceType filtering
ResourceTable currently picks query based on props but doesn't combine `contentBatchId` + `resourceType`. Two options:
- **Option A**: Client-side filter (simplest) — add computed that filters `resources` by type
- **Option B**: New Convex query `listByContentBatchAndType`

Go with **Option A** (client-side): add an internal `filteredResources` computed that applies `resourceType` filter to the fetched results. This works because engagement batches have ≤48 resources (small dataset).

Add to ResourceTable:
```ts
const filteredResources = computed(() => {
  if (!props.resourceType) return resources.value
  return resources.value.filter((r: any) => r.resourceType === props.resourceType)
})
```
Use `filteredResources` instead of `resources` in the template.

---

## Part C: Resource Detail Modal

### C1. `dashboard/components/ResourceDetailModal.vue` — new component
Thin wrapper: `<VModal>` containing `<ResourceDetailPanel>`.
- Props: `modelValue: boolean`, `resourceId: string | null`
- Uses existing `ResourceDetailPanel` (already has content/metadata/relationships/history/file tabs)
- Add "Open Full Page" link in header that navigates to `/projects/{slug}/resources/{id}`
- Size: `xl` or `2xl` for enough room

### C2. `dashboard/pages/.../batches/[id].vue` — wire table → modal
- Add `selectedResourceId = ref<string | null>(null)`
- Add `showResourceModal` computed get/set (like existing `showTaskDetail` pattern)
- Handle `@select` on ResourceTable: set `selectedResourceId`
- Add `<ResourceDetailModal>` at bottom of template

---

## Files Changed
1. `convex/contentBatches.ts` — status guard (1 line)
2. `dashboard/components/ContentBatchForm.vue` — edit mode (~30 lines changed)
3. `dashboard/components/ResourceStatsCards.vue` — clickable + emit (~15 lines)
4. `dashboard/components/ResourceTable.vue` — client-side type filter (~5 lines)
5. `dashboard/components/ResourceDetailModal.vue` — **new** (~30 lines, thin wrapper)
6. `dashboard/pages/.../batches/[id].vue` — edit button, resource type state, resource modal (~40 lines)

## Part D: Resource Table Pagination

### D1. `dashboard/components/ResourceTable.vue` — pagination controls
Currently shows at most 25 items (Convex default) with no pagination.
- Pass `paginationOpts: { numItems: 200 }` in query args to fetch full set
- Add client-side pagination: `currentPage = ref(1)`, `perPage = 25`
- Add `totalPages` computed and `paginatedResources` computed (slice)
- Add Prev/Next bar below table (matching activity pagination pattern in `batches/[id].vue`)
- Show total count: "X resources"
- Reset page to 1 when query args change (watch)

### D2. `dashboard/pages/.../resources/index.vue` — pagination controls
Same pattern as D1 but for the project resources page:
- Pass `paginationOpts: { numItems: 200 }` in both search and list query args
- Add client-side pagination state
- Add Prev/Next bar below the inline table
- Show count: "Showing X-Y of Z resources"
- Reset page to 1 when filters change

---

## Verification
- Create batch → Edit button visible → edit name/size/focus groups → saves
- Activate → Edit button gone
- Click "Social Posts" count → table shows only social posts
- Click "Total" → table shows all
- Click a resource row → modal opens with full detail (content, metadata, relationships)
- Close modal → back to table
- Batch detail: resource table shows pagination when >25 resources
- Project resources: pagination controls appear at bottom, Prev/Next work
- Changing filters on project resources resets to page 1
