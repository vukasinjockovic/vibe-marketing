<script setup lang="ts">
import {
  LayoutDashboard,
  FolderKanban,
  Workflow,
  Bot,
  Server,
  Activity,
  Settings,
  LogOut,
  ChevronLeft,
} from 'lucide-vue-next'

const { user, logout } = useAuth()
const route = useRoute()

const collapsed = ref(false)

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
      class="fixed inset-y-0 left-0 z-30 flex flex-col bg-sidebar text-sidebar-foreground border-r border-border/10 transition-all duration-200"
      :class="collapsed ? 'w-16' : 'w-60'"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 h-14 border-b border-white/10 shrink-0">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white text-sm font-bold shrink-0">
          V
        </div>
        <div v-if="!collapsed" class="overflow-hidden">
          <p class="text-sm font-semibold text-white truncate">Vibe Marketing</p>
        </div>
        <button
          class="ml-auto text-sidebar-foreground/40 hover:text-white transition-colors"
          @click="collapsed = !collapsed"
        >
          <ChevronLeft
            :size="16"
            class="transition-transform duration-200"
            :class="collapsed ? 'rotate-180' : ''"
          />
        </button>
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
          <span v-if="!collapsed" class="truncate">{{ item.name }}</span>
        </NuxtLink>
      </nav>

      <!-- User -->
      <div class="px-2 py-3 border-t border-white/10 shrink-0">
        <div class="flex items-center gap-3 px-3 py-2">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white text-xs font-medium shrink-0">
            {{ (user?.name || 'U')[0].toUpperCase() }}
          </div>
          <div v-if="!collapsed" class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ user?.name }}</p>
            <p class="text-xs text-sidebar-foreground/40 truncate">{{ user?.role }}</p>
          </div>
          <button
            v-if="!collapsed"
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
      class="transition-all duration-200 min-h-screen"
      :class="collapsed ? 'ml-16' : 'ml-60'"
    >
      <div class="p-6 max-w-[1400px]">
        <slot />
      </div>
    </main>
  </div>
</template>
