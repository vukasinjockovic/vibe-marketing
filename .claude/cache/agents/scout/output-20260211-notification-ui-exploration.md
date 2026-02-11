# Codebase Report: Dashboard Notification System & UI Structure
Generated: 2026-02-11

## Summary
Explored the vibe-marketing dashboard codebase to understand the current layout structure, notification system (backend and frontend), breadcrumb patterns, and authentication/user tracking. The dashboard uses Vue 3/Nuxt 3 with a sidebar layout, has a full backend notification system in Convex, but NO frontend notification UI components yet. No breadcrumb system exists.

---

## 1. Current Layout Structure

### Primary Layout: `dashboard/layouts/default.vue`
**Location:** `/var/www/vibe-marketing/dashboard/layouts/default.vue`

**Structure:**
- **Fixed sidebar** (left, collapsible)
  - Width: `w-60` (expanded) / `w-16` (collapsed)
  - Collapse state stored in `collapsed` ref
  - Background: `bg-sidebar` with `text-sidebar-foreground`
  
- **Main content area**
  - Margin adjusts based on sidebar: `ml-60` / `ml-16`
  - Max width: `max-w-[1400px]`
  - Padding: `p-6`

**Sidebar Components:**
```vue
<!-- Logo Section (h-14) -->
<div class="flex items-center gap-3 px-4 h-14 border-b">
  <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
    V
  </div>
  <p v-if="!collapsed" class="text-sm font-semibold">Vibe Marketing</p>
  <button @click="collapsed = !collapsed">
    <ChevronLeft :class="collapsed ? 'rotate-180' : ''" />
  </button>
</div>

<!-- Navigation (flex-1, scrollable) -->
<nav class="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
  <NuxtLink v-for="item in navigation" :to="item.path">
    <!-- navigation items -->
  </NuxtLink>
</nav>

<!-- User Section (bottom, h-auto) -->
<div class="px-2 py-3 border-t border-white/10">
  <div class="flex items-center gap-3">
    <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/10">
      {{ (user?.name || 'U')[0].toUpperCase() }}
    </div>
    <div v-if="!collapsed">
      <p class="text-sm font-medium">{{ user?.name }}</p>
      <p class="text-xs text-sidebar-foreground/40">{{ user?.role }}</p>
    </div>
    <button v-if="!collapsed" @click="logout">
      <LogOut :size="16" />
    </button>
  </div>
</div>
```

**Navigation Items:**
```typescript
const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Projects', path: '/projects', icon: FolderKanban },
  { name: 'Pipelines', path: '/pipelines', icon: Workflow },
  { name: 'Agents', path: '/agents', icon: Bot },
  { name: 'Services', path: '/services', icon: Server },
  { name: 'Activity', path: '/activity', icon: Activity },
  { name: 'Settings', path: '/settings', icon: Settings },
]
```

---

## 2. Notification System

### Backend (Convex) - FULLY IMPLEMENTED

**Location:** `/var/www/vibe-marketing/convex/notifications.ts`

**Schema:**
```typescript
notifications: defineTable({
  mentionedAgent: v.string(),
  fromAgent: v.string(),
  taskId: v.optional(v.id("tasks")),
  content: v.string(),
  delivered: v.boolean(),
  deliveredAt: v.optional(v.number()),
}).index("by_undelivered", ["mentionedAgent", "delivered"])
```

**Available Functions:**
1. `listUndelivered(mentionedAgent)` - Query undelivered notifications
2. `create(mentionedAgent, fromAgent, taskId?, content)` - Create notification
3. `markDelivered(id)` - Mark single as delivered
4. `markAllDelivered(mentionedAgent)` - Mark all as delivered

### Frontend - NO NOTIFICATION UI YET

**Missing Components:**
- No notification bell component
- No notification dropdown
- No notification panel
- No notification badge counter
- No notification list component

**Existing Toast System (transient only):**
`dashboard/composables/useToast.ts` + `dashboard/components/VToast.vue`
- Bottom-right fixed position
- Auto-dismiss (4s default)
- Types: success, error, warning, info

---

## 3. Breadcrumb Patterns

**Search Result:** NO BREADCRUMB SYSTEM EXISTS

**Current Pattern:** `VPageHeader.vue` component with title + description
```vue
<VPageHeader title="Audiences" description="Target focus groups">
  <template #actions>
    <button>Action 1</button>
  </template>
</VPageHeader>
```

Deep routes exist (e.g., `/projects/[slug]/products/[id]/audiences/[fgId]`) but no breadcrumb trail shown.

---

## 4. Auth/User System

### Backend (`convex/auth.ts`)

**Flow:**
1. `signIn(email, password)` - Action with bcrypt validation
2. `createSession(userId)` - Creates 30-day UUID token
3. `validateSession(token)` - Checks token validity
4. `me(token)` - Returns current user
5. `signOut(token)` - Deletes session

**Schema:**
```typescript
users: {
  email, name, passwordHash,
  role: "admin" | "editor" | "viewer",
  status: "active" | "disabled"
}

sessions: {
  userId, token, expiresAt,
  userAgent?, ip?
}
```

### Frontend (`dashboard/composables/useAuth.ts`)

**Storage:**
- Cookie: `vibe_session` (30 days, sameSite: lax)
- State: `useState('user')` (reactive, in-memory)

**API:**
```typescript
const { user, token, isAuthenticated, login, logout, fetchUser } = useAuth()
```

---

## 5. Convex Integration (`dashboard/composables/useConvex.ts`)

**Patterns:**
```typescript
// Reactive query (WebSocket subscription)
const { data, loading, error } = useConvexQuery(
  api.campaigns.list,
  computed(() => projectId.value ? { projectId } : 'skip')
)

// Mutation
const { mutate, loading, error } = useConvexMutation(api.campaigns.create)
await mutate({ name: 'New Campaign' })

// Action
const { execute, loading, error } = useConvexAction(api.auth.signIn)
await execute({ email, password })
```

---

## 6. Existing UI Components

**Component Library:**
- VPageHeader, VToast, VModal, VConfirmDialog
- VFormField, VStatusBadge, VEmptyState, VChipInput, VDataTable
- AudienceImportDialog, AudienceResearchDialog, CampaignForm
- EnrichmentFieldStatus, EnrichmentProgressBar, EnrichmentTimeline
- FocusGroupForm, ProductForm, TaskDetailModal

**Composables:**
- useAuth, useConvex, useToast, useCurrentProject, useAudienceJobs

---

## 7. Recommendations

### Notification UI Implementation

**Placement:** Sidebar top (between logo and navigation)

**Components Needed:**
1. `NotificationBell.vue` - Bell icon with badge counter
2. `NotificationDropdown.vue` - Notification list panel
3. `useNotifications.ts` - Composable for data/actions

**Composable Pattern:**
```typescript
export function useNotifications() {
  const { user } = useAuth()
  
  const { data: notifications } = useConvexQuery(
    api.notifications.listUndelivered,
    computed(() => user.value?.name 
      ? { mentionedAgent: user.value.name } 
      : 'skip'
    )
  )
  
  const unreadCount = computed(() => notifications.value?.length || 0)
  
  const { mutate: markRead } = useConvexMutation(api.notifications.markDelivered)
  const { mutate: markAllRead } = useConvexMutation(api.notifications.markAllDelivered)
  
  return { notifications, unreadCount, markRead, markAllRead }
}
```

### Breadcrumb Implementation

**Option A:** Manual via VPageHeader slot
```vue
<VPageHeader title="Audiences">
  <template #breadcrumb>
    <Breadcrumb :items="breadcrumbItems" />
  </template>
</VPageHeader>
```

**Option B:** Auto-generate from route
```typescript
// composables/useBreadcrumbs.ts
export function useBreadcrumbs() {
  const route = useRoute()
  const breadcrumbs = computed(() => {
    // Parse route.path and build breadcrumb items
  })
  return { breadcrumbs }
}
```

---

## Files Explored

| File | Purpose |
|------|---------|
| `/var/www/vibe-marketing/dashboard/layouts/default.vue` | Main layout |
| `/var/www/vibe-marketing/dashboard/layouts/auth.vue` | Auth layout |
| `/var/www/vibe-marketing/convex/schema.ts` | Database schema |
| `/var/www/vibe-marketing/convex/notifications.ts` | Notification functions |
| `/var/www/vibe-marketing/convex/auth.ts` | Auth functions |
| `/var/www/vibe-marketing/dashboard/composables/useAuth.ts` | Auth composable |
| `/var/www/vibe-marketing/dashboard/composables/useConvex.ts` | Convex helpers |
| `/var/www/vibe-marketing/dashboard/composables/useToast.ts` | Toast system |
| `/var/www/vibe-marketing/dashboard/components/VPageHeader.vue` | Page header |
| `/var/www/vibe-marketing/dashboard/components/VToast.vue` | Toast UI |
| `/var/www/vibe-marketing/dashboard/pages/projects/[slug]/index.vue` | Project page |
| `/var/www/vibe-marketing/dashboard/pages/projects/[slug]/products/[id]/audiences.vue` | Nested route example |
