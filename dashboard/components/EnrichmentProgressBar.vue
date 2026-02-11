<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  score: number
  label?: string
  showPercentage?: boolean
}>(), {
  showPercentage: true,
})

const showPct = computed(() => props.showPercentage)

const clampedScore = computed(() => Math.max(0, Math.min(100, props.score)))

const barColorClass = computed(() => {
  if (clampedScore.value < 30) return 'bg-red-500'
  if (clampedScore.value <= 70) return 'bg-yellow-500'
  return 'bg-green-500'
})
</script>

<template>
  <div data-testid="enrichment-bar" class="w-full">
    <div v-if="label || showPct" class="flex items-center justify-between mb-1">
      <span v-if="label" class="text-xs text-gray-600 font-medium">{{ label }}</span>
      <span v-if="showPct" class="text-xs text-gray-500 font-medium">{{ clampedScore }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
      <div
        data-testid="enrichment-bar-fill"
        class="h-2 rounded-full transition-all duration-300"
        :class="barColorClass"
        :style="{ width: `${clampedScore}%` }"
      />
    </div>
  </div>
</template>
