<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  agentName: string
}>()

const { data: status } = useConvexQuery(
  api.services.getAgentServiceStatus,
  computed(() => ({ agentName: props.agentName })),
)

const badgeClass = computed(() => {
  switch (status.value?.status) {
    case 'enabled': return 'bg-green-100 text-green-700'
    case 'degraded': return 'bg-yellow-100 text-yellow-700'
    case 'disabled': return 'bg-red-100 text-red-700'
    default: return 'bg-muted text-muted-foreground'
  }
})

const label = computed(() => {
  return status.value?.status?.toUpperCase() || 'UNKNOWN'
})
</script>

<template>
  <span
    class="px-2 py-0.5 text-xs font-semibold rounded-full uppercase tracking-wide"
    :class="badgeClass"
    :title="status?.capabilities?.map((c: any) => `${c.capability}: ${c.activeCount} active`).join(', ')"
  >
    {{ label }}
  </span>
</template>
