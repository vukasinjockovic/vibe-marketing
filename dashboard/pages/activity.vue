<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const { data: activities, loading } = useConvexQuery(api.activities.list, {})

function typeColor(type: string) {
  switch (type) {
    case 'error': return 'text-red-600'
    case 'warning': return 'text-yellow-600'
    case 'complete': return 'text-green-600'
    default: return 'text-muted-foreground'
  }
}
</script>

<template>
  <div>
    <VPageHeader title="Activity Log" description="All agent activity across projects" />

    <VEmptyState
      v-if="!loading && (!activities || activities.length === 0)"
      title="No activity recorded yet"
      description="Activities will appear here once agents start running."
    />

    <div v-else-if="!loading" class="rounded-lg border bg-card shadow-sm divide-y divide-border">
      <div v-for="activity in activities" :key="activity._id" class="px-4 sm:px-6 py-3 flex flex-wrap items-start gap-2 sm:items-center sm:gap-4">
        <span class="text-xs font-mono px-2 py-1 bg-muted rounded" :class="typeColor(activity.type)">
          {{ activity.type }}
        </span>
        <span class="text-sm font-medium text-primary">{{ activity.agentName }}</span>
        <span class="text-sm text-muted-foreground flex-1">{{ activity.message }}</span>
      </div>
    </div>

    <div v-else class="text-muted-foreground">Loading...</div>
  </div>
</template>
