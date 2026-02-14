<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const { data: agents, loading } = useConvexQuery(api.agents.list, {})
const { data: skills } = useConvexQuery(api.skills.list, {})

const searchQuery = ref('')
const statusFilter = ref<string>('all')
const expandedCards = ref(new Set<string>())

// Build skill lookup map: id → displayName
const skillMap = computed(() => {
  const map: Record<string, string> = {}
  if (skills.value) {
    for (const s of skills.value) {
      map[s._id] = s.displayName || s.slug || s._id
    }
  }
  return map
})

const filteredAgents = computed(() => {
  let list = agents.value || []
  if (statusFilter.value !== 'all') {
    list = list.filter((a: any) => a.status === statusFilter.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter((a: any) => a.displayName.toLowerCase().includes(q) || a.name.toLowerCase().includes(q) || a.role.toLowerCase().includes(q))
  }
  return list
})

const statusOptions = ['all', 'active', 'idle', 'blocked', 'offline']

function toggleExpand(id: string) {
  if (expandedCards.value.has(id)) {
    expandedCards.value.delete(id)
  } else {
    expandedCards.value.add(id)
  }
}

function isExpanded(id: string) {
  return expandedCards.value.has(id)
}

function timeAgo(ts: number) {
  if (!ts) return 'never'
  const diff = Date.now() - ts
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

function statusColor(status: string) {
  switch (status) {
    case 'active': return 'bg-blue-500'
    case 'idle': return 'bg-green-500'
    case 'blocked': return 'bg-yellow-500'
    case 'offline': return 'bg-gray-400'
    default: return 'bg-gray-400'
  }
}

function resolveSkillNames(ids: string[]): string[] {
  if (!ids?.length) return []
  return ids.map(id => skillMap.value[id] || id).sort()
}
</script>

<template>
  <div>
    <VPageHeader title="Agents" description="Monitor your AI agents">
      <template #actions>
        <input
          v-model="searchQuery"
          placeholder="Search agents..."
          class="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring w-48"
        />
        <select v-model="statusFilter" class="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
          <option v-for="s in statusOptions" :key="s" :value="s">
            {{ s === 'all' ? 'All statuses' : s }}
          </option>
        </select>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <VEmptyState
      v-else-if="!filteredAgents?.length"
      title="No agents found"
      description="No agents match your current filters."
    >
      <template #icon>
        <svg class="w-6 h-6 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128H9m6 0a5.995 5.995 0 0 0-.786-3.07M9 19.128v-.003c0-1.113.285-2.16.786-3.07M9 19.128H3.375a1.125 1.125 0 0 1-1.125-1.125v-.003c0-2.278 1.847-4.125 4.125-4.125h1.5c.321 0 .632.037.932.107M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
        </svg>
      </template>
    </VEmptyState>

    <div v-else class="space-y-3">
      <div
        v-for="agent in filteredAgents"
        :key="agent._id"
        class="rounded-lg border bg-card shadow-sm overflow-hidden"
      >
        <!-- Card Header (always visible) -->
        <div
          class="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
          @click="toggleExpand(agent._id)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <!-- Status dot -->
              <span
                class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                :class="statusColor(agent.status)"
                :title="agent.status"
              />
              <div>
                <div class="flex items-center gap-2">
                  <NuxtLink
                    :to="`/agents/${agent.name}`"
                    class="font-medium text-foreground hover:text-primary"
                    @click.stop
                  >
                    {{ agent.displayName }}
                  </NuxtLink>
                  <span class="text-xs text-muted-foreground font-mono">{{ agent.name }}</span>
                </div>
                <p class="text-xs text-muted-foreground mt-0.5 line-clamp-1 max-w-md">{{ agent.role }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 sm:gap-4">
              <!-- Model badge -->
              <span class="text-xs bg-muted px-2 py-0.5 rounded font-mono text-muted-foreground">{{ agent.defaultModel }}</span>
              <!-- Tasks completed -->
              <span class="text-xs text-muted-foreground hidden sm:inline" :title="`${agent.stats?.tasksCompleted || 0} tasks completed`">
                {{ agent.stats?.tasksCompleted || 0 }} tasks
              </span>
              <!-- Last active -->
              <span class="text-xs text-muted-foreground w-16 text-right hidden sm:inline">{{ timeAgo(agent.stats?.lastActive || 0) }}</span>
              <!-- Chevron -->
              <svg
                class="w-4 h-4 text-muted-foreground/70 transition-transform"
                :class="{ 'rotate-180': isExpanded(agent._id) }"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Expanded Details -->
        <div v-if="isExpanded(agent._id)" class="border-t px-4 py-4 space-y-4 bg-muted/50">
          <!-- Info grid -->
          <div>
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Info</h5>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-muted-foreground">Role:</span>
                <span class="ml-1 text-foreground">{{ agent.role }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Level:</span>
                <span class="ml-1 text-foreground capitalize">{{ agent.level }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Skill Path:</span>
                <span class="ml-1 text-foreground font-mono text-xs">{{ agent.skillPath }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Heartbeat:</span>
                <span class="ml-1 text-foreground font-mono text-xs">{{ agent.heartbeatCron }}</span>
              </div>
            </div>
          </div>

          <!-- Stats grid -->
          <div>
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Stats</h5>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
              <div>
                <span class="text-muted-foreground">Tasks Completed:</span>
                <span class="ml-1 text-foreground font-semibold">{{ agent.stats?.tasksCompleted || 0 }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Avg Quality:</span>
                <span class="ml-1 text-foreground font-semibold">
                  {{ agent.stats?.avgQualityScore ? agent.stats.avgQualityScore.toFixed(1) : 'N/A' }}
                </span>
              </div>
              <div>
                <span class="text-muted-foreground">Last Heartbeat:</span>
                <span class="ml-1 text-foreground">{{ timeAgo(agent.lastHeartbeat) }}</span>
              </div>
            </div>
          </div>

          <!-- Skills -->
          <div>
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Skills</h5>
            <div v-if="resolveSkillNames([...(agent.staticSkillIds || []), ...(agent.dynamicSkillIds || [])]).length" class="flex flex-wrap gap-1.5">
              <span
                v-for="name in resolveSkillNames([...(agent.staticSkillIds || []), ...(agent.dynamicSkillIds || [])])"
                :key="name"
                class="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full"
              >
                {{ name }}
              </span>
            </div>
            <span v-else class="text-xs text-muted-foreground italic">No skills assigned</span>
          </div>

          <!-- Current task banner -->
          <div v-if="agent.currentTaskId" class="rounded-md bg-blue-50 border border-blue-200 px-3 py-2 flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-600 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
            </svg>
            <span class="text-sm text-blue-800">Currently working on a task</span>
          </div>

          <!-- View Details link -->
          <div class="pt-3 border-t">
            <NuxtLink
              :to="`/agents/${agent.name}`"
              class="text-sm text-primary hover:text-primary font-medium"
            >
              View Full Details
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
