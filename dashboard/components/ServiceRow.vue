<script setup lang="ts">
import { GripVertical } from 'lucide-vue-next'

const props = defineProps<{
  service: any
  rank?: number
  draggable?: boolean
}>()

const emit = defineEmits<{
  toggle: [service: any]
  configure: [service: any]
}>()

const typeBadge = computed(() => {
  switch (props.service.integrationType) {
    case 'mcp': return { label: 'MCP', class: 'bg-blue-100 text-blue-700' }
    case 'script': return { label: 'API', class: 'bg-purple-100 text-purple-700' }
    case 'both': return { label: 'MCP+API', class: 'bg-indigo-100 text-indigo-700' }
    case 'local': return { label: 'Local', class: 'bg-green-100 text-green-700' }
    default: return { label: 'API', class: 'bg-gray-100 text-gray-700' }
  }
})
</script>

<template>
  <div class="flex items-center gap-3 px-4 py-2.5 group">
    <!-- Drag handle -->
    <GripVertical
      v-if="draggable"
      class="h-4 w-4 text-muted-foreground/50 cursor-grab active:cursor-grabbing shrink-0"
    />
    <div v-else class="w-4 shrink-0" />

    <!-- Rank -->
    <span v-if="rank" class="text-xs text-muted-foreground w-5 text-right shrink-0">{{ rank }}.</span>

    <!-- Name (clickable) -->
    <button
      class="font-medium text-sm text-foreground hover:text-primary truncate text-left"
      @click="emit('configure', service)"
    >
      {{ service.displayName }}
    </button>

    <!-- Type badge -->
    <span class="px-1.5 py-0.5 text-xs rounded-full font-medium shrink-0" :class="typeBadge.class">
      {{ typeBadge.label }}
    </span>

    <!-- Free tier badge -->
    <span v-if="service.freeTier" class="px-1.5 py-0.5 text-xs rounded-full bg-emerald-100 text-emerald-700 font-medium shrink-0">
      Free
    </span>

    <!-- Cost -->
    <span class="text-xs text-muted-foreground ml-auto shrink-0">{{ service.costInfo }}</span>

    <!-- Health dot -->
    <ServiceHealthDot :status="service.lastHealthStatus" />

    <!-- Toggle -->
    <button
      role="switch"
      :aria-checked="service.isActive"
      class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      :class="service.isActive ? 'bg-primary' : 'bg-input'"
      @click="emit('toggle', service)"
    >
      <span
        class="pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform"
        :class="service.isActive ? 'translate-x-4' : 'translate-x-0'"
      />
    </button>
  </div>
</template>
