<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const { user } = useAuth()

const { data: projects, loading: projectsLoading } = useConvexQuery(api.projects.list, {})
const { data: activities, loading: activitiesLoading } = useConvexQuery(api.activities.list, {})

const stats = computed(() => ({
  projects: projects.value?.length || 0,
  campaigns: 0,
  tasks: 0,
  agents: 0,
}))

const loading = computed(() => projectsLoading.value || activitiesLoading.value)

const recentActivities = computed(() => (activities.value || []).slice(0, 10))

function typeColor(type: string) {
  switch (type) {
    case 'error': return 'text-red-600'
    case 'warning': return 'text-yellow-600'
    case 'complete': return 'text-green-600'
    default: return 'text-gray-600'
  }
}
</script>

<template>
  <div>
    <VPageHeader :title="`Welcome, ${user?.name || 'User'}`" />

    <div class="grid grid-cols-4 gap-6 mb-8">
      <div v-for="(value, key) in stats" :key="key" class="bg-white rounded-lg shadow p-6">
        <p class="text-sm text-gray-500 capitalize">{{ key }}</p>
        <p class="text-3xl font-bold mt-1">{{ value }}</p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold mb-4">Recent Activity</h2>
      <div v-if="loading" class="text-gray-500 text-sm">Loading...</div>
      <div v-else-if="recentActivities.length === 0" class="text-gray-500 text-sm">
        No recent activity. Create a project to get started.
      </div>
      <div v-else class="space-y-2">
        <div v-for="activity in recentActivities" :key="activity._id" class="flex items-center gap-3 text-sm">
          <span class="text-xs font-mono px-2 py-0.5 bg-gray-100 rounded" :class="typeColor(activity.type)">
            {{ activity.type }}
          </span>
          <span class="font-medium text-primary-700">{{ activity.agentName }}</span>
          <span class="text-gray-600 flex-1">{{ activity.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
