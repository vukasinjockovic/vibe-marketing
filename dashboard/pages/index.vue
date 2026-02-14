<script setup lang="ts">
import {
  FolderKanban, Megaphone, ListTodo, Bot, Server, FileStack,
  Workflow, Users, ArrowRight, TrendingUp, Clock, CheckCircle2,
  AlertCircle, Loader2, Activity, ChevronRight, Zap, Plus,
} from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

const { user } = useAuth()

const { data: dashData, loading } = useConvexQuery(api.dashboard.globalStats, {})
const { data: activities, loading: activitiesLoading } = useConvexQuery(api.activities.list, {})

// Time-based greeting
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const d = computed(() => dashData.value || null)

// Primary stat cards
const primaryStats = computed(() => {
  if (!d.value) return []
  return [
    { label: 'Projects', value: d.value.projects.total, icon: FolderKanban, color: 'text-blue-600', bg: 'bg-blue-50', link: '/projects' },
    { label: 'Campaigns', value: d.value.campaigns.total, sub: `${d.value.campaigns.active} active`, icon: Megaphone, color: 'text-purple-600', bg: 'bg-purple-50', link: '/projects' },
    { label: 'Tasks', value: d.value.tasks.total, sub: `${d.value.tasks.completed} done`, icon: ListTodo, color: 'text-amber-600', bg: 'bg-amber-50', link: '/activity' },
    { label: 'Focus Groups', value: d.value.focusGroups.total, icon: Users, color: 'text-emerald-600', bg: 'bg-emerald-50', link: '/projects' },
    { label: 'Agents', value: d.value.agents.total, sub: `${d.value.agents.active} online`, icon: Bot, color: 'text-cyan-600', bg: 'bg-cyan-50', link: '/agents' },
    { label: 'Services', value: d.value.services.total, sub: `${d.value.services.active} active`, icon: Server, color: 'text-rose-600', bg: 'bg-rose-50', link: '/services' },
  ]
})

// Task pipeline breakdown
const taskBreakdown = computed(() => {
  if (!d.value) return []
  const t = d.value.tasks
  return [
    { label: 'Backlog', value: t.backlog, color: 'bg-slate-400' },
    { label: 'In Progress', value: t.inProgress, color: 'bg-blue-500' },
    { label: 'Blocked', value: t.blocked, color: 'bg-red-500' },
    { label: 'Completed', value: t.completed, color: 'bg-green-500' },
  ]
})

const taskTotal = computed(() => d.value?.tasks.total || 1)

// Recent activities
const recentActivities = computed(() => (activities.value || []).slice(0, 8))

// Quick links
const quickLinks = [
  { label: 'New Project', icon: Plus, path: '/projects/new', color: 'text-blue-600' },
  { label: 'Pipelines', icon: Workflow, path: '/pipelines', color: 'text-purple-600' },
  { label: 'Skills', icon: Zap, path: '/skills', color: 'text-amber-600' },
  { label: 'Activity Log', icon: Activity, path: '/activity', color: 'text-emerald-600' },
]

function formatTime(ts: number) {
  if (!ts) return ''
  const now = Date.now()
  const diffMs = now - ts
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 30) return `${diffDays}d ago`
  return new Date(ts).toLocaleDateString()
}

function typeIcon(type: string) {
  switch (type) {
    case 'error': return AlertCircle
    case 'complete': return CheckCircle2
    case 'progress': return Loader2
    default: return Activity
  }
}

function typeColor(type: string) {
  switch (type) {
    case 'error': return 'text-red-500'
    case 'warning': return 'text-yellow-500'
    case 'complete': return 'text-green-500'
    default: return 'text-muted-foreground'
  }
}
</script>

<template>
  <div>
    <!-- Greeting Header -->
    <div class="mb-6">
      <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
        {{ greeting }}, {{ user?.name || 'User' }}
      </h1>
      <p class="text-sm text-muted-foreground mt-1">Here's what's happening across your projects.</p>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="h-8 w-8 animate-spin text-muted-foreground" />
    </div>

    <template v-else-if="d">
      <!-- Primary Stats Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        <NuxtLink
          v-for="stat in primaryStats"
          :key="stat.label"
          :to="stat.link"
          class="rounded-lg border bg-card shadow-sm p-3 sm:p-4 hover:shadow-md hover:border-primary/20 transition-all group"
        >
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center shrink-0" :class="[stat.bg, stat.color]">
              <component :is="stat.icon" :size="18" />
            </div>
            <div class="min-w-0">
              <p class="text-xl sm:text-2xl font-bold text-foreground leading-tight">{{ stat.value }}</p>
              <p class="text-xs text-muted-foreground truncate">{{ stat.label }}</p>
            </div>
          </div>
          <p v-if="stat.sub" class="text-xs text-muted-foreground/70 mt-1.5 pl-[46px] sm:pl-[50px] truncate">
            {{ stat.sub }}
          </p>
        </NuxtLink>
      </div>

      <!-- Two-column layout: Projects + Task Pipeline -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <!-- Projects (2/3) -->
        <div class="lg:col-span-2 rounded-lg border bg-card shadow-sm">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="font-semibold text-foreground">Projects</h2>
            <NuxtLink to="/projects" class="text-xs text-primary hover:underline flex items-center gap-0.5">
              View all <ChevronRight :size="12" />
            </NuxtLink>
          </div>

          <div v-if="!d.projects.list.length" class="p-8 text-center">
            <FolderKanban class="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
            <p class="text-sm text-muted-foreground mb-3">No projects yet</p>
            <NuxtLink
              to="/projects/new"
              class="inline-flex items-center gap-1.5 bg-primary text-primary-foreground px-3 py-1.5 rounded-md text-sm font-medium hover:bg-primary/90"
            >
              <Plus :size="14" /> Create Project
            </NuxtLink>
          </div>

          <div v-else class="divide-y divide-border">
            <NuxtLink
              v-for="proj in d.projects.list"
              :key="proj._id"
              :to="`/projects/${proj.slug}`"
              class="flex items-center gap-3 px-4 py-3 hover:bg-muted/50 transition-colors group"
            >
              <div
                class="w-9 h-9 rounded-lg flex items-center justify-center text-white text-sm font-bold shrink-0"
                :style="{ backgroundColor: proj.color }"
              >
                {{ proj.icon || proj.name[0] }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-foreground group-hover:text-primary transition-colors truncate">
                  {{ proj.name }}
                </p>
                <div class="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                  <span>{{ proj.stats?.campaignCount || 0 }} campaigns</span>
                  <span>{{ proj.stats?.taskCount || 0 }} tasks</span>
                  <span>{{ proj.stats?.resourceCount || 0 }} resources</span>
                </div>
              </div>
              <ChevronRight :size="16" class="text-muted-foreground/40 group-hover:text-primary shrink-0 transition-colors" />
            </NuxtLink>
          </div>
        </div>

        <!-- Right Column: Task Pipeline + Quick Links -->
        <div class="space-y-4">
          <!-- Task Pipeline -->
          <div class="rounded-lg border bg-card shadow-sm p-4">
            <h2 class="font-semibold text-foreground mb-3 text-sm">Task Pipeline</h2>

            <div v-if="d.tasks.total === 0" class="text-center py-4">
              <p class="text-sm text-muted-foreground">No tasks yet</p>
            </div>

            <template v-else>
              <!-- Progress bar -->
              <div class="flex rounded-full h-3 overflow-hidden mb-3 bg-muted">
                <div
                  v-for="seg in taskBreakdown.filter(s => s.value > 0)"
                  :key="seg.label"
                  class="transition-all duration-500"
                  :class="seg.color"
                  :style="{ width: `${(seg.value / taskTotal) * 100}%` }"
                />
              </div>

              <!-- Legend -->
              <div class="grid grid-cols-2 gap-2">
                <div
                  v-for="seg in taskBreakdown"
                  :key="seg.label"
                  class="flex items-center gap-2"
                >
                  <div class="w-2.5 h-2.5 rounded-full shrink-0" :class="seg.color" />
                  <span class="text-xs text-muted-foreground">{{ seg.label }}</span>
                  <span class="text-xs font-semibold text-foreground ml-auto">{{ seg.value }}</span>
                </div>
              </div>
            </template>
          </div>

          <!-- Quick Links -->
          <div class="rounded-lg border bg-card shadow-sm p-4">
            <h2 class="font-semibold text-foreground mb-3 text-sm">Quick Links</h2>
            <div class="grid grid-cols-2 gap-2">
              <NuxtLink
                v-for="link in quickLinks"
                :key="link.path"
                :to="link.path"
                class="flex items-center gap-2 px-3 py-2 rounded-md border border-transparent hover:border-border hover:bg-muted/50 transition-all text-sm"
              >
                <component :is="link.icon" :size="14" :class="link.color" />
                <span class="text-foreground text-xs font-medium">{{ link.label }}</span>
              </NuxtLink>
            </div>
          </div>

          <!-- Service Health -->
          <div class="rounded-lg border bg-card shadow-sm p-4">
            <div class="flex items-center justify-between mb-3">
              <h2 class="font-semibold text-foreground text-sm">Service Health</h2>
              <NuxtLink to="/services" class="text-xs text-primary hover:underline">Manage</NuxtLink>
            </div>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-muted-foreground">Active</span>
                <span class="text-xs font-semibold text-green-600">{{ d.services.active }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-muted-foreground">Degraded</span>
                <span class="text-xs font-semibold" :class="d.services.degraded > 0 ? 'text-yellow-600' : 'text-muted-foreground'">{{ d.services.degraded }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-muted-foreground">Total Providers</span>
                <span class="text-xs font-semibold text-foreground">{{ d.services.total }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Row: Active Campaigns + Recent Activity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Active Campaigns -->
        <div class="rounded-lg border bg-card shadow-sm">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="font-semibold text-foreground">Active Campaigns</h2>
            <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
              {{ d.campaigns.active }}
            </span>
          </div>

          <div v-if="!d.campaigns.recent.length" class="p-8 text-center">
            <Megaphone class="h-8 w-8 text-muted-foreground/30 mx-auto mb-2" />
            <p class="text-sm text-muted-foreground">No active campaigns</p>
          </div>

          <div v-else class="divide-y divide-border">
            <div
              v-for="campaign in d.campaigns.recent"
              :key="campaign._id"
              class="px-4 py-3"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-foreground truncate">{{ campaign.name }}</p>
                  <p class="text-xs text-muted-foreground mt-0.5">
                    {{ formatTime(campaign._creationTime) }}
                  </p>
                </div>
                <VStatusBadge :status="campaign.status" size="sm" />
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="rounded-lg border bg-card shadow-sm">
          <div class="px-4 py-3 border-b flex items-center justify-between">
            <h2 class="font-semibold text-foreground">Recent Activity</h2>
            <NuxtLink to="/activity" class="text-xs text-primary hover:underline flex items-center gap-0.5">
              View all <ChevronRight :size="12" />
            </NuxtLink>
          </div>

          <div v-if="activitiesLoading" class="p-6 text-center">
            <Loader2 class="h-5 w-5 animate-spin text-muted-foreground mx-auto" />
          </div>

          <div v-else-if="!recentActivities.length" class="p-8 text-center">
            <Activity class="h-8 w-8 text-muted-foreground/30 mx-auto mb-2" />
            <p class="text-sm text-muted-foreground">No recent activity</p>
          </div>

          <div v-else class="divide-y divide-border">
            <div
              v-for="activity in recentActivities"
              :key="activity._id"
              class="px-4 py-2.5 flex items-start gap-2.5"
            >
              <component
                :is="typeIcon(activity.type)"
                :size="14"
                class="shrink-0 mt-0.5"
                :class="typeColor(activity.type)"
              />
              <div class="min-w-0 flex-1">
                <p class="text-sm text-foreground leading-snug">
                  <span class="font-medium text-primary">{{ activity.agentName }}</span>
                  <span class="text-muted-foreground"> {{ activity.message }}</span>
                </p>
                <p class="text-xs text-muted-foreground/60 mt-0.5">
                  {{ formatTime(activity._creationTime) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom: Resources + Pipelines + Batches summary -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
        <NuxtLink to="/pipelines" class="rounded-lg border bg-card shadow-sm p-3 hover:shadow-md hover:border-primary/20 transition-all">
          <div class="flex items-center gap-2">
            <Workflow :size="16" class="text-purple-600" />
            <span class="text-sm font-medium text-foreground">{{ d.pipelines.total }} Pipelines</span>
          </div>
        </NuxtLink>
        <div class="rounded-lg border bg-card shadow-sm p-3">
          <div class="flex items-center gap-2">
            <FileStack :size="16" class="text-indigo-600" />
            <span class="text-sm font-medium text-foreground">{{ d.resources.total }} Resources</span>
          </div>
        </div>
        <div class="rounded-lg border bg-card shadow-sm p-3">
          <div class="flex items-center gap-2">
            <TrendingUp :size="16" class="text-emerald-600" />
            <span class="text-sm font-medium text-foreground">{{ d.contentBatches.total }} Batches</span>
          </div>
        </div>
        <div class="rounded-lg border bg-card shadow-sm p-3">
          <div class="flex items-center gap-2">
            <CheckCircle2 :size="16" class="text-green-600" />
            <span class="text-sm font-medium text-foreground">{{ d.tasks.completed }} Completed</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
