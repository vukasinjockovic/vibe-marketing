<script setup lang="ts">
const props = defineProps<{
  status?: string | null
}>()

const colorClass = computed(() => {
  switch (props.status) {
    case 'healthy': return 'bg-green-500'
    case 'degraded': return 'bg-yellow-500'
    case 'unreachable': return 'bg-red-500'
    case 'unknown': return 'bg-gray-400'
    default: return 'bg-gray-300'
  }
})

const label = computed(() => {
  if (!props.status) return 'No data'
  return props.status.charAt(0).toUpperCase() + props.status.slice(1)
})
</script>

<template>
  <span class="relative flex h-2.5 w-2.5" :title="label">
    <span
      v-if="status === 'healthy'"
      class="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"
    />
    <span class="relative inline-flex h-2.5 w-2.5 rounded-full" :class="colorClass" />
  </span>
</template>
