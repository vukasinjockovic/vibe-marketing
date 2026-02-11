# Implementation Report: Batch 2 - Campaign & Pipeline Pages (7 files)
Generated: 2026-02-11

## Task
Build 7 new Vue files for the dashboard: campaign list, campaign form, campaign detail, pipeline kanban board, task detail modal, pipeline template library, and pipeline template viewer.

## Files Created

### 1. `pages/projects/[slug]/campaigns/index.vue` - Campaign List
- Status filter tabs (All, Planning, Active, Paused, Completed) with count badges
- Campaign cards in responsive grid (name, description, status badge, keywords count, date)
- "New Campaign" button opens modal with CampaignForm
- VEmptyState for no campaigns
- Uses `useCurrentProject()` for project context

### 2. `components/CampaignForm.vue` - Multi-step Campaign Creator
- 4-step wizard with visual step indicator (circles with connecting lines)
- Step 1: Name (auto-slugifies), slug, description
- Step 2: Product selector, focus group checkboxes (loads dynamically when product selected)
- Step 3: Pipeline preset selection with radio buttons, shows step preview
- Step 4: Seed keywords (VChipInput), competitor URLs (VChipInput), deliverable checkboxes, notes
- Per-step validation gates (Next button disabled until valid)
- Calls `campaigns.create` mutation with all fields

### 3. `pages/projects/[slug]/campaigns/[id].vue` - Campaign Detail
- Header with back arrow, campaign name, status badge
- Lifecycle controls: Activate (green), Pause (yellow), Complete (blue) with confirm dialogs
- 4 info cards: task stats, focus groups, keywords, pipeline info
- Tasks table with columns: Title, Type, Status, Priority, Agent, Quality
- Clicking task title opens TaskDetailModal

### 4. `pages/projects/[slug]/pipeline.vue` - Kanban Board
- 7-column kanban: Backlog, Researched, Briefed, Drafted, Reviewed, Humanized, Completed
- Each column has colored header dot, label, and count badge
- Task cards show: title, content type, assigned agent, quality score, priority badge
- Left border colored by priority (urgent=red, high=orange, medium=blue, low=gray)
- Cards are clickable, open TaskDetailModal
- Special "Needs Attention" section below for revision_needed, blocked, cancelled tasks
- Horizontal scroll for overflow

### 5. `components/TaskDetailModal.vue` - Task Detail in Modal
- XL-sized VModal with full task info
- Pipeline progress bar: circles connected by lines, colored by step status (green=done, blue+pulse=in progress, gray=pending)
- Task metadata: status, priority, content type, assigned agent, quality score, revision count
- Rejection notes alert box (red bg)
- 3 tabs: Overview (description), Messages (agent thread), Documents (file list)

### 6. `pages/pipelines/index.vue` - Pipeline Template Library
- Grid of pipeline cards with name, type badge (preset/custom), description
- Visual step count preview (numbered circles in a row)
- Fork button creates copy with unique slug (appends timestamp hash)
- View link navigates to detail page

### 7. `pages/pipelines/[slug].vue` - Pipeline Template Viewer
- Back arrow + name + type badge header
- 3 summary cards: main steps count, parallel branches count, on-complete config
- Vertical timeline of main steps with numbered circles, step label, agent/model/outputDir badges
- Parallel branches shown inline as indented purple cards with dashed border
- Convergence point indicator
- Fork button navigates to new pipeline after forking

## Validation
- `npx nuxi typecheck` ran successfully
- Zero type errors from any of the 7 new files
- All pre-existing errors are in Convex backend files and prior test stubs (unrelated)

## Patterns Followed
- `<script setup lang="ts">` + Composition API (matches all existing pages)
- UnoCSS/Tailwind utility classes (matches existing style)
- Shared component reuse: VPageHeader, VStatusBadge, VModal, VDataTable, VEmptyState, VFormField, VChipInput, VConfirmDialog
- Composable usage: useConvexQuery, useConvexMutation, useCurrentProject, useToast
- API import paths adjusted per file depth (verified against existing pattern)
- Convex ID casting with `as any` for TypeScript compatibility
- Skip pattern for conditional queries: `computed(() => id ? { id } : 'skip')`

## Notes
- The fork mutation signature in convex/pipelines.ts uses `pipelineId`, `newName`, `newSlug` (not `id`, `name`, `slug` as originally specified in the task). Implementation matches the actual Convex function signature.
- Campaign detail page's TaskDetailModal binding uses a pattern where closing the modal nullifies selectedTaskId
- The kanban board handles special statuses (revision_needed, blocked, cancelled) separately below the main columns
