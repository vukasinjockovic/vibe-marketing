<script setup lang="ts">
import { computed } from 'vue'

interface EnrichmentEntry {
  timestamp: number
  source: string
  agentName: string
  field: string
  previousValue?: string
  newValue: string
  confidence: string
  reasoning: string
}

const props = defineProps<{
  enrichments: EnrichmentEntry[]
}>()

const sortedEnrichments = computed(() => {
  return [...props.enrichments].sort((a, b) => b.timestamp - a.timestamp)
})

function confidenceClass(confidence: string) {
  switch (confidence) {
    case 'high': return 'bg-green-500'
    case 'medium': return 'bg-yellow-500'
    case 'low': return 'bg-red-500'
    default: return 'bg-muted-foreground/40'
  }
}

function formatTimestamp(ts: number) {
  return new Date(ts).toLocaleString()
}

function formatFieldName(field: string) {
  return field.replace(/([A-Z])/g, ' $1').replace(/^./, (s) => s.toUpperCase())
}
</script>

<template>
  <div>
    <div v-if="!enrichments.length" class="text-sm text-muted-foreground/70 italic py-4 text-center">
      No enrichment history
    </div>

    <div v-else class="relative">
      <!-- Timeline line -->
      <div class="absolute left-3 top-0 bottom-0 w-0.5 bg-border" />

      <div
        v-for="(entry, idx) in sortedEnrichments"
        :key="`${entry.timestamp}-${entry.field}-${idx}`"
        data-testid="timeline-entry"
        class="relative pl-8 pb-6 last:pb-0"
      >
        <!-- Confidence dot -->
        <span
          data-testid="confidence-dot"
          class="absolute left-1.5 top-1 w-3 h-3 rounded-full border-2 border-background"
          :class="confidenceClass(entry.confidence)"
        />

        <div class="rounded-lg border bg-card p-3">
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-foreground">{{ entry.field }}</span>
              <span class="text-xs text-muted-foreground/70">{{ formatFieldName(entry.field) }}</span>
            </div>
            <span class="text-xs text-muted-foreground/70">{{ formatTimestamp(entry.timestamp) }}</span>
          </div>

          <div class="flex items-center gap-1 text-xs text-muted-foreground mb-1">
            <span class="font-medium">{{ entry.agentName }}</span>
            <span class="text-muted-foreground/40">|</span>
            <span>{{ entry.source }}</span>
            <span class="text-muted-foreground/40">|</span>
            <span
              class="px-1.5 py-0.5 rounded-full text-xs"
              :class="{
                'bg-green-100 text-green-700': entry.confidence === 'high',
                'bg-yellow-100 text-yellow-700': entry.confidence === 'medium',
                'bg-red-100 text-red-700': entry.confidence === 'low',
              }"
            >
              {{ entry.confidence }}
            </span>
          </div>

          <!-- Value change -->
          <div v-if="entry.previousValue" class="text-xs text-muted-foreground mb-1">
            <span class="line-through text-red-400">{{ entry.previousValue }}</span>
            <span class="mx-1">-></span>
            <span class="text-green-600">{{ entry.newValue }}</span>
          </div>
          <div v-else class="text-xs text-muted-foreground mb-1">
            <span class="text-green-600">{{ entry.newValue }}</span>
          </div>

          <p class="text-xs text-muted-foreground italic">{{ entry.reasoning }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
