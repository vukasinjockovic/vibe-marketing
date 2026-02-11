# Implementation Report: Rewrite Dashboard Pages for Real-time Convex Subscriptions
Generated: 2026-02-11

## Task
Rewrote all existing dashboard pages and layouts to use WebSocket-based reactive Convex subscriptions instead of manual `onMounted` + `client.query()` patterns. Added shared component usage (VPageHeader, VDataTable, VEmptyState, VStatusBadge, VToast) throughout.

## Changes Made

### 1. `dashboard/app.vue` - Added VToast globally
- Added `<VToast />` after `<NuxtLayout>` so toast notifications render on every page

### 2. `dashboard/layouts/default.vue` - Updated navigation + active link logic
- Added 2 new nav items: Pipelines (`/pipelines`) and Settings (`/settings`)
- Changed active link detection from exact match (`route.path === item.path`) to `startsWith` for non-root paths, so sub-pages highlight correctly

### 3. `dashboard/pages/index.vue` - Dashboard rewrite
- FROM: `onMounted` + `useConvex()` + `client.query()` + dynamic `import()`
- TO: Static `import { api }` + `useConvexQuery()` reactive subscriptions
- Added `VPageHeader` with user greeting
- Added reactive `stats` computed from projects subscription
- Added `recentActivities` section showing last 10 activities with type coloring

### 4. `dashboard/pages/projects/index.vue` - Projects list rewrite
- FROM: Manual `ref<Project[]>`, `onMounted`, `loading` management
- TO: Single `useConvexQuery(api.projects.list, {})` call
- Uses `VPageHeader` with #actions slot for "New Project" button
- Uses `VEmptyState` for zero-project state
- Project cards with appearance colors, descriptions, and stats

### 5. `dashboard/pages/agents.vue` - Agents rewrite
- FROM: Manual table, `onMounted`, `statusColor` function
- TO: `useConvexQuery` + `VDataTable` + `VStatusBadge` + search + status filter
- Added search input and status dropdown filter in `VPageHeader` actions
- Clickable agent names link to `/agents/{name}`
- Uses `VDataTable` with scoped slots for custom cell rendering

### 6. `dashboard/pages/services.vue` - Services rewrite
- FROM: `onMounted` + sequential per-category queries
- TO: Reactive `useConvexQuery` for categories, watch-based per-category service loading
- Added toggle button using `useConvexMutation(api.services.toggleActive)`
- Uses `VStatusBadge` for API key status, `VPageHeader`, toast notifications
- Note: No `services.list` exists in Convex -- used `listByCategory` per category with a watcher

### 7. `dashboard/pages/activity.vue` - Activity log rewrite
- FROM: `onMounted` + manual loading state
- TO: Single `useConvexQuery(api.activities.list, {})`
- Uses `VPageHeader` and `VEmptyState`

### 8. `dashboard/pages/login.vue` - No changes needed
- Already uses `useAuth()` which internally handles Convex action calls
- Does not import `useConvex` or `api` directly

## Convex Services API Analysis
Verified available functions in `/var/www/vibe-marketing/convex/services.ts`:
- `listCategories` - returns all categories sorted by sortOrder
- `listByCategory({ categoryId })` - returns services for a category
- `listActive` - returns all active services only
- `get({ id })` - single service
- `resolve({ categoryName })` - find highest-priority active service
- `create(...)` - create service
- `update({ id, isActive?, ... })` - partial update
- `toggleActive({ id })` - toggle isActive boolean

Used `toggleActive` for the toggle button (cleaner than `update`).

## Typecheck Results
- All dashboard page/layout errors: 0
- Pre-existing backend errors (convex/admin.ts, convex/auth.ts): 7 (not in scope)
- Command: `npx nuxi typecheck`

## Key Patterns Applied
1. Static `import { api }` instead of dynamic `await import()` in onMounted
2. `useConvexQuery()` for reactive WebSocket subscriptions (auto-update on backend changes)
3. `useConvexMutation()` for write operations
4. Shared components: VPageHeader, VDataTable, VEmptyState, VStatusBadge, VToast
5. `useToast()` for user feedback on mutations
6. Correct relative import paths based on file depth:
   - `pages/*.vue` -> `../../convex/_generated/api`
   - `pages/projects/*.vue` -> `../../../convex/_generated/api`

## Files Modified
1. `/var/www/vibe-marketing/dashboard/app.vue`
2. `/var/www/vibe-marketing/dashboard/layouts/default.vue`
3. `/var/www/vibe-marketing/dashboard/pages/index.vue`
4. `/var/www/vibe-marketing/dashboard/pages/projects/index.vue`
5. `/var/www/vibe-marketing/dashboard/pages/agents.vue`
6. `/var/www/vibe-marketing/dashboard/pages/services.vue`
7. `/var/www/vibe-marketing/dashboard/pages/activity.vue`
