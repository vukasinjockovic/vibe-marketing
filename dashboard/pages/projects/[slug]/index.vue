<script setup lang="ts">
import { api } from '../../../../convex/_generated/api'

const { project } = useCurrentProject()
const projectId = computed(() => project.value?._id)

const { data: campaigns } = useConvexQuery(
  api.campaigns.list,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)
const { data: activities } = useConvexQuery(
  api.activities.listByProject,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const stats = computed(() => project.value?.stats || {
  productCount: 0,
  campaignCount: 0,
  taskCount: 0,
  completedTaskCount: 0,
})

const statCards = computed(() => [
  { label: 'Products', value: stats.value.productCount || 0, icon: 'i-heroicons-cube', color: 'text-blue-600 bg-blue-50' },
  { label: 'Campaigns', value: stats.value.campaignCount || 0, icon: 'i-heroicons-megaphone', color: 'text-purple-600 bg-purple-50' },
  { label: 'Tasks', value: stats.value.taskCount || 0, icon: 'i-heroicons-clipboard-document-list', color: 'text-amber-600 bg-amber-50' },
  { label: 'Completed', value: stats.value.completedTaskCount || 0, icon: 'i-heroicons-check-circle', color: 'text-green-600 bg-green-50' },
])

const recentCampaigns = computed(() => (campaigns.value || []).slice(0, 5))
const recentActivities = computed(() => (activities.value || []).slice(0, 10))

function formatTime(ts: number) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}
</script>

<template>
  <div class="space-y-6">
    <!-- Stats Grid -->
    <div class="grid grid-cols-4 gap-4">
      <div
        v-for="stat in statCards"
        :key="stat.label"
        class="bg-white rounded-lg shadow p-4"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="stat.color">
            <span :class="stat.icon" class="text-xl" />
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
            <p class="text-sm text-gray-500">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-6">
      <!-- Recent Campaigns -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-4 py-3 border-b flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Recent Campaigns</h3>
          <NuxtLink
            v-if="project"
            :to="`/projects/${project.slug}/campaigns`"
            class="text-sm text-primary-600 hover:underline"
          >
            View all
          </NuxtLink>
        </div>
        <div v-if="!recentCampaigns.length" class="p-6 text-center text-sm text-gray-500">
          No campaigns yet
        </div>
        <div v-else class="divide-y">
          <div
            v-for="campaign in recentCampaigns"
            :key="campaign._id"
            class="px-4 py-3 flex items-center justify-between"
          >
            <div>
              <p class="text-sm font-medium text-gray-900">{{ campaign.name }}</p>
              <p v-if="campaign.description" class="text-xs text-gray-500 mt-0.5">{{ campaign.description }}</p>
            </div>
            <VStatusBadge :status="campaign.status" size="sm" />
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-4 py-3 border-b">
          <h3 class="font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div v-if="!recentActivities.length" class="p-6 text-center text-sm text-gray-500">
          No activity yet
        </div>
        <div v-else class="divide-y">
          <div
            v-for="activity in recentActivities"
            :key="activity._id"
            class="px-4 py-3"
          >
            <div class="flex items-start gap-2">
              <span class="inline-block w-6 h-6 rounded-full bg-gray-100 text-xs flex items-center justify-center text-gray-600 font-medium flex-shrink-0 mt-0.5">
                {{ (activity.agentName || '?')[0].toUpperCase() }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-sm text-gray-900">
                  <span class="font-medium">{{ activity.agentName }}</span>
                  {{ activity.message }}
                </p>
                <p v-if="activity._creationTime" class="text-xs text-gray-400 mt-0.5">
                  {{ formatTime(activity._creationTime) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
