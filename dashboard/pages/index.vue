<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Folder, Megaphone, ClipboardList, Monitor } from 'lucide-vue-next'
import type { Component } from 'vue'

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
    default: return 'text-muted-foreground'
  }
}

const statIcons: Record<string, Component> = {
  projects: Folder,
  campaigns: Megaphone,
  tasks: ClipboardList,
  agents: Monitor,
}
</script>

<template>
  <div>
    <VPageHeader :title="`Welcome, ${user?.name || 'User'}`" />

    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
      <div
        v-for="(value, key) in stats"
        :key="key"
        class="rounded-lg border bg-card text-card-foreground shadow-sm p-6"
      >
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm font-medium text-muted-foreground capitalize">{{ key }}</p>
          <component :is="statIcons[key as string] || statIcons.projects" class="h-4 w-4 text-muted-foreground" />
        </div>
        <p class="text-3xl font-bold text-foreground">{{ value }}</p>
      </div>
    </div>

    <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
      <div class="px-6 py-4 border-b">
        <h2 class="text-lg font-semibold text-foreground">Recent Activity</h2>
      </div>
      <div class="p-6">
        <div v-if="loading" class="text-muted-foreground text-sm">Loading...</div>
        <div v-else-if="recentActivities.length === 0" class="text-muted-foreground text-sm">
          No recent activity. Create a project to get started.
        </div>
        <div v-else class="space-y-3">
          <div v-for="activity in recentActivities" :key="activity._id" class="flex items-center gap-3 text-sm">
            <span class="text-xs font-mono px-2 py-0.5 bg-muted rounded" :class="typeColor(activity.type)">
              {{ activity.type }}
            </span>
            <span class="font-medium text-primary">{{ activity.agentName }}</span>
            <span class="text-muted-foreground flex-1">{{ activity.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
