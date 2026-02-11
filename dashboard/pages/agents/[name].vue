<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../convex/_generated/api'

const route = useRoute()
const agentName = computed(() => route.params.name as string)

const { data: agent, loading } = useConvexQuery(
  api.agents.getByName,
  computed(() => agentName.value ? { name: agentName.value } : 'skip')
)

const { data: runs } = useConvexQuery(
  api.analytics.listRunsByAgent,
  computed(() => agentName.value ? { agentName: agentName.value } : 'skip')
)

const { data: activities } = useConvexQuery(
  api.activities.listByAgent,
  computed(() => agentName.value ? { agentName: agentName.value } : 'skip')
)

function timeAgo(ts: number) {
  const diff = Date.now() - ts
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

function formatDuration(seconds: number) {
  if (seconds < 60) return `${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

function typeColor(type: string) {
  switch (type) {
    case 'error': return 'text-red-600 bg-red-50'
    case 'warning': return 'text-yellow-600 bg-yellow-50'
    case 'complete': return 'text-green-600 bg-green-50'
    default: return 'text-gray-600 bg-gray-50'
  }
}

const runColumns = [
  { key: 'startedAt', label: 'Started' },
  { key: 'duration', label: 'Duration' },
  { key: 'model', label: 'Model' },
  { key: 'status', label: 'Status' },
  { key: 'itemsProcessed', label: 'Items' },
]

const sortedRuns = computed(() => {
  if (!runs.value) return []
  return [...runs.value].sort((a: any, b: any) => b.startedAt - a.startedAt)
})

const recentActivities = computed(() => {
  if (!activities.value) return []
  return activities.value.slice(0, 20)
})
</script>

<template>
  <div>
    <!-- Back link -->
    <NuxtLink to="/agents" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
      <span class="i-heroicons-arrow-left w-4 h-4" />
      Back to Agents
    </NuxtLink>

    <!-- Loading state -->
    <div v-if="loading" class="text-gray-500">
      <span class="i-heroicons-arrow-path animate-spin text-2xl mb-2 block" />
      Loading agent...
    </div>

    <!-- Agent not found -->
    <VEmptyState
      v-else-if="!agent"
      icon="i-heroicons-exclamation-triangle"
      title="Agent Not Found"
      :description="`No agent found with name '${agentName}'.`"
    >
      <NuxtLink to="/agents" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
        View all agents
      </NuxtLink>
    </VEmptyState>

    <!-- Agent detail -->
    <template v-else>
      <VPageHeader :title="agent.displayName">
        <template #actions>
          <VStatusBadge :status="agent.status" />
        </template>
      </VPageHeader>

      <!-- Info Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Role</p>
          <p class="text-sm font-medium mt-1">{{ agent.role }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Model</p>
          <p class="text-sm font-medium mt-1">{{ agent.defaultModel }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Level</p>
          <p class="text-sm font-medium mt-1 capitalize">{{ agent.level }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Skill Path</p>
          <p class="text-sm font-medium mt-1 font-mono text-xs">{{ agent.skillPath }}</p>
        </div>
      </div>

      <!-- Stats Row -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <p class="text-2xl font-bold">{{ agent.stats?.tasksCompleted || 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Tasks Completed</p>
        </div>
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <p class="text-2xl font-bold">{{ agent.stats?.avgQualityScore?.toFixed(1) || 'N/A' }}</p>
          <p class="text-xs text-gray-500 mt-1">Avg Quality Score</p>
        </div>
        <div class="bg-white rounded-lg shadow p-4 text-center">
          <p class="text-2xl font-bold">{{ timeAgo(agent.lastHeartbeat || 0) }}</p>
          <p class="text-xs text-gray-500 mt-1">Last Heartbeat</p>
        </div>
      </div>

      <!-- Current Task -->
      <div v-if="agent.currentTaskId" class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs text-blue-600 uppercase tracking-wide font-medium">Current Task</p>
            <p class="text-sm font-medium mt-1">{{ agent.currentTaskId }}</p>
          </div>
          <VStatusBadge status="in_progress" size="sm" />
        </div>
      </div>

      <!-- Recent Runs -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold mb-3">Recent Runs</h2>
        <VDataTable
          :columns="runColumns"
          :rows="sortedRuns"
          :loading="false"
          empty-message="No runs recorded yet."
        >
          <template #cell-startedAt="{ row }">
            <span class="text-gray-600">{{ timeAgo(row.startedAt) }}</span>
          </template>
          <template #cell-duration="{ row }">
            <span v-if="row.durationSeconds" class="text-gray-600">{{ formatDuration(row.durationSeconds) }}</span>
            <span v-else class="text-gray-400">--</span>
          </template>
          <template #cell-status="{ row }">
            <VStatusBadge :status="row.status" size="sm" />
          </template>
          <template #cell-itemsProcessed="{ row }">
            {{ row.itemsProcessed ?? '--' }}
          </template>
        </VDataTable>
      </div>

      <!-- Activity Log -->
      <div>
        <h2 class="text-lg font-semibold mb-3">Activity Log</h2>
        <VEmptyState
          v-if="recentActivities.length === 0"
          title="No activity recorded"
          description="Activities will appear here as the agent runs."
        />
        <div v-else class="bg-white rounded-lg shadow divide-y">
          <div
            v-for="activity in recentActivities"
            :key="activity._id"
            class="px-4 py-3 flex items-center gap-3"
          >
            <span
              class="text-xs font-mono px-2 py-0.5 rounded"
              :class="typeColor(activity.type)"
            >
              {{ activity.type }}
            </span>
            <span class="text-sm text-gray-700 flex-1">{{ activity.message }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
