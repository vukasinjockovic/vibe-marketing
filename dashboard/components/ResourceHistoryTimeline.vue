<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import {
  Plus, Pencil, ArrowRightLeft, FileText,
  Settings, Trash2, Clock,
} from 'lucide-vue-next'

const props = defineProps<{
  resourceId: any
}>()

const { data: history, loading } = useConvexQuery(
  api.resources.getHistory,
  computed(() => props.resourceId ? { resourceId: props.resourceId } : 'skip'),
)

const changeTypeConfig: Record<string, { icon: any; color: string; label: string }> = {
  created: { icon: Plus, color: 'text-green-500 bg-green-50', label: 'Created' },
  updated: { icon: Pencil, color: 'text-blue-500 bg-blue-50', label: 'Updated' },
  status_changed: { icon: ArrowRightLeft, color: 'text-purple-500 bg-purple-50', label: 'Status Changed' },
  content_changed: { icon: FileText, color: 'text-amber-500 bg-amber-50', label: 'Content Changed' },
  metadata_changed: { icon: Settings, color: 'text-cyan-500 bg-cyan-50', label: 'Metadata Changed' },
  deleted: { icon: Trash2, color: 'text-red-500 bg-red-50', label: 'Deleted' },
}

function formatDate(ts: number) {
  return new Date(ts).toLocaleString()
}
</script>

<template>
  <div>
    <div v-if="loading" class="p-4 text-center text-muted-foreground text-sm">Loading history...</div>
    <div v-else-if="!history?.length" class="p-4 text-center text-muted-foreground text-sm">No history records</div>

    <div v-else class="space-y-0">
      <div
        v-for="(entry, i) in history"
        :key="entry._id"
        class="flex gap-3 px-4 py-3 border-b last:border-0"
      >
        <!-- Icon -->
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
          :class="(changeTypeConfig[entry.changeType]?.color || 'text-muted-foreground bg-muted')"
        >
          <component
            :is="changeTypeConfig[entry.changeType]?.icon || Clock"
            :size="14"
          />
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium text-foreground">
              {{ changeTypeConfig[entry.changeType]?.label || entry.changeType }}
            </span>
            <span class="text-xs text-muted-foreground">by {{ entry.changedBy }}</span>
          </div>

          <!-- Changed fields -->
          <div v-if="entry.changedFields?.length" class="mt-1">
            <span class="text-xs text-muted-foreground">
              Fields: {{ entry.changedFields.join(', ') }}
            </span>
          </div>

          <!-- Previous values -->
          <div v-if="entry.previousValues && Object.keys(entry.previousValues).length" class="mt-1">
            <details class="text-xs">
              <summary class="text-muted-foreground cursor-pointer hover:text-foreground">Previous values</summary>
              <pre class="mt-1 p-2 rounded bg-muted text-xs overflow-auto max-h-32">{{ JSON.stringify(entry.previousValues, null, 2) }}</pre>
            </details>
          </div>

          <!-- Note -->
          <p v-if="entry.note" class="text-xs text-muted-foreground mt-1 italic">{{ entry.note }}</p>

          <!-- Timestamp -->
          <p class="text-xs text-muted-foreground/60 mt-1">{{ formatDate(entry.createdAt) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
