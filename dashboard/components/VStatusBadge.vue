<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
  size?: 'sm' | 'md'
}>()

const colorMap: Record<string, string> = {
  // Pipeline statuses
  backlog: 'bg-gray-100 text-gray-700',
  researched: 'bg-blue-100 text-blue-700',
  briefed: 'bg-indigo-100 text-indigo-700',
  drafted: 'bg-purple-100 text-purple-700',
  reviewed: 'bg-amber-100 text-amber-700',
  revision_needed: 'bg-red-100 text-red-700',
  humanized: 'bg-teal-100 text-teal-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-gray-100 text-gray-500',
  blocked: 'bg-red-100 text-red-700',
  // Campaign statuses
  planning: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  in_revision: 'bg-orange-100 text-orange-700',
  // Agent statuses
  idle: 'bg-gray-100 text-gray-600',
  offline: 'bg-gray-100 text-gray-400',
  // Service statuses
  configured: 'bg-green-100 text-green-700',
  needs_key: 'bg-yellow-100 text-yellow-700',
  // Generic
  pending: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-700',
  running: 'bg-blue-100 text-blue-700',
  failed: 'bg-red-100 text-red-700',
  success: 'bg-green-100 text-green-700',
}

const classes = computed(() => colorMap[props.status] || 'bg-gray-100 text-gray-600')
const sizeClasses = computed(() => props.size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-xs')
const label = computed(() => props.status.replace(/_/g, ' '))
</script>

<template>
  <span class="rounded-full font-medium capitalize" :class="[classes, sizeClasses]">
    {{ label }}
  </span>
</template>
