<script setup lang="ts">
defineProps<{
  label: string
  value: any
  filled: boolean
  confidence?: string
}>()
</script>

<template>
  <div class="flex items-start gap-2">
    <span
      data-testid="field-status-indicator"
      class="mt-1 w-2 h-2 rounded-full flex-shrink-0"
      :class="filled ? 'bg-green-500' : 'bg-muted-foreground/30'"
    />
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2">
        <span class="text-xs font-medium text-muted-foreground">{{ label }}</span>
        <span
          v-if="confidence"
          data-testid="confidence-badge"
          class="text-xs px-1.5 py-0.5 rounded-full"
          :class="{
            'bg-green-100 text-green-700': confidence === 'high',
            'bg-yellow-100 text-yellow-700': confidence === 'medium',
            'bg-red-100 text-red-700': confidence === 'low',
          }"
        >
          {{ confidence }}
        </span>
      </div>
      <p v-if="filled" class="text-sm text-foreground mt-0.5 truncate">
        {{ typeof value === 'object' ? JSON.stringify(value) : value }}
      </p>
      <p v-else class="text-sm text-muted-foreground/60 italic mt-0.5">Not yet enriched</p>
    </div>
  </div>
</template>
