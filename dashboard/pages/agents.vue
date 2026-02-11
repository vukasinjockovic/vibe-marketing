<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const { data: agents, loading } = useConvexQuery(api.agents.list, {})

const searchQuery = ref('')
const statusFilter = ref<string>('all')

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

function timeAgo(ts: number) {
  const diff = Date.now() - ts
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const columns = [
  { key: 'displayName', label: 'Agent' },
  { key: 'role', label: 'Role' },
  { key: 'status', label: 'Status' },
  { key: 'defaultModel', label: 'Model' },
  { key: 'tasksCompleted', label: 'Tasks' },
  { key: 'lastActive', label: 'Last Active' },
]
</script>

<template>
  <div>
    <VPageHeader title="Agents" description="Monitor your AI agents">
      <template #actions>
        <input
          v-model="searchQuery"
          placeholder="Search agents..."
          class="border rounded-md px-3 py-1.5 text-sm w-48"
        />
        <select v-model="statusFilter" class="border rounded-md px-3 py-1.5 text-sm">
          <option v-for="s in statusOptions" :key="s" :value="s">
            {{ s === 'all' ? 'All statuses' : s }}
          </option>
        </select>
      </template>
    </VPageHeader>

    <VDataTable :columns="columns" :rows="filteredAgents" :loading="loading" empty-message="No agents registered yet.">
      <template #cell-displayName="{ row }">
        <NuxtLink :to="`/agents/${row.name}`" class="hover:text-primary-600">
          <div class="font-medium">{{ row.displayName }}</div>
          <div class="text-xs text-gray-500">{{ row.name }}</div>
        </NuxtLink>
      </template>
      <template #cell-status="{ row }">
        <VStatusBadge :status="row.status" />
      </template>
      <template #cell-defaultModel="{ row }">
        <span class="text-gray-600">{{ row.defaultModel }}</span>
      </template>
      <template #cell-tasksCompleted="{ row }">
        {{ row.stats?.tasksCompleted || 0 }}
      </template>
      <template #cell-lastActive="{ row }">
        <span class="text-gray-500">{{ timeAgo(row.stats?.lastActive || 0) }}</span>
      </template>
    </VDataTable>
  </div>
</template>
