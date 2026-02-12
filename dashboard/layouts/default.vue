<script setup lang="ts">
import {
  LayoutDashboard,
  FolderKanban,
  FolderOpen,
  Workflow,
  Bot,
  Server,
  Activity,
  Settings,
  LogOut,
  ChevronRight,
} from 'lucide-vue-next'

const { user, logout } = useAuth()
const { open: openArtifacts } = useArtifactsBrowser()
const route = useRoute()

// Breadcrumbs
const breadcrumbs = computed(() => {
  const segments = route.path.split('/').filter(Boolean)
  if (segments.length === 0) return [{ label: 'Dashboard', path: '/' }]

  const crumbs: { label: string; path: string }[] = [{ label: 'Home', path: '/' }]

  const labelMap: Record<string, string> = {
    projects: 'Projects',
    pipelines: 'Pipelines',
    agents: 'Agents',
    services: 'Services',
    activity: 'Activity',
    settings: 'Settings',
    campaigns: 'Campaigns',
    audiences: 'Audiences',
    products: 'Products',
    tasks: 'Tasks',
  }

  let pathSoFar = ''
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i]
    pathSoFar += `/${seg}`
    const label = labelMap[seg] || decodeURIComponent(seg)
    crumbs.push({ label, path: pathSoFar })
  }

  return crumbs
})

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Projects', path: '/projects', icon: FolderKanban },
  { name: 'Pipelines', path: '/pipelines', icon: Workflow },
  { name: 'Agents', path: '/agents', icon: Bot },
  { name: 'Services', path: '/services', icon: Server },
  { name: 'Activity', path: '/activity', icon: Activity },
  { name: 'Settings', path: '/settings', icon: Settings },
]

function isActive(path: string) {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-30 flex flex-col bg-sidebar text-sidebar-foreground border-r border-border/10 w-60"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 h-14 border-b border-white/10 shrink-0">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white text-sm font-bold shrink-0">
          V
        </div>
        <div class="overflow-hidden">
          <p class="text-sm font-semibold text-white truncate">Vibe Marketing</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
        <NuxtLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors group"
          :class="isActive(item.path)
            ? 'bg-white/10 text-white font-medium'
            : 'text-sidebar-foreground/40 hover:bg-white/5 hover:text-white'"
        >
          <component
            :is="item.icon"
            :size="18"
            class="shrink-0"
            :class="isActive(item.path) ? 'text-primary' : 'text-sidebar-foreground/50 group-hover:text-sidebar-foreground/70'"
          />
          <span class="truncate">{{ item.name }}</span>
        </NuxtLink>
      </nav>

      <!-- User -->
      <div class="px-2 py-3 border-t border-white/10 shrink-0">
        <div class="flex items-center gap-3 px-3 py-2">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white text-xs font-medium shrink-0">
            {{ (user?.name || 'U')[0].toUpperCase() }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ user?.name }}</p>
            <p class="text-xs text-sidebar-foreground/40 truncate">{{ user?.role }}</p>
          </div>
          <button
            class="text-sidebar-foreground/40 hover:text-white transition-colors shrink-0"
            title="Sign out"
            @click="logout"
          >
            <LogOut :size="16" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main
      class="min-h-screen ml-60"
    >
      <!-- Topbar -->
      <div class="sticky top-0 z-20 h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-6">
        <!-- Breadcrumbs -->
        <nav class="flex items-center gap-1 text-sm">
          <template v-for="(crumb, i) in breadcrumbs" :key="crumb.path">
            <ChevronRight v-if="i > 0" :size="14" class="text-muted-foreground/40" />
            <NuxtLink
              v-if="i < breadcrumbs.length - 1"
              :to="crumb.path"
              class="text-muted-foreground hover:text-foreground transition-colors"
            >
              {{ crumb.label }}
            </NuxtLink>
            <span v-else class="text-foreground font-medium">{{ crumb.label }}</span>
          </template>
        </nav>

        <!-- Right side -->
        <div class="flex items-center gap-2">
          <button
            class="flex items-center justify-center w-8 h-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            title="Artifacts Browser"
            @click="openArtifacts()"
          >
            <FolderOpen :size="18" />
          </button>
          <NotificationDropdown />
        </div>
      </div>

      <div class="p-6 max-w-[1400px]">
        <slot />
      </div>
    </main>

    <ArtifactsBrowser />
  </div>
</template>
