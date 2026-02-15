<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'

const props = defineProps<{
  campaignId?: any
  contentBatchId?: any
  taskId?: any
}>()

const emit = defineEmits<{
  select: [resource: any]
}>()

const queryArgs = computed(() => {
  if (props.taskId) return { taskId: props.taskId }
  if (props.campaignId) return { campaignId: props.campaignId }
  if (props.contentBatchId) return { contentBatchId: props.contentBatchId }
  return 'skip'
})

const { data: tree, loading } = useConvexQuery(
  api.resources.listTree,
  queryArgs,
)

// Track which roots are expanded
const expandedIds = ref(new Set<string>())

function toggleExpand(id: string) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

function isExpanded(id: string) {
  return expandedIds.value.has(id)
}

const statusColors: Record<string, string> = {
  draft: 'bg-muted text-muted-foreground',
  in_review: 'bg-yellow-100 text-yellow-700',
  reviewed: 'bg-blue-100 text-blue-700',
  humanized: 'bg-indigo-100 text-indigo-700',
  approved: 'bg-green-100 text-green-700',
  published: 'bg-green-200 text-green-800',
  archived: 'bg-muted text-muted-foreground/50',
}
</script>

<template>
  <div class="rounded-lg border bg-card shadow-sm">
    <div v-if="loading" class="p-4 text-center text-sm text-muted-foreground">Loading resource tree...</div>

    <div v-else-if="!tree?.length" class="p-4 text-center text-sm text-muted-foreground">
      No resources registered yet.
    </div>

    <div v-else class="divide-y divide-border">
      <div
        v-for="root in tree"
        :key="root._id"
      >
        <!-- Root node -->
        <div
          class="flex items-center gap-2 px-4 py-2.5 hover:bg-muted/50 transition-colors cursor-pointer"
          @click="root.children?.length ? toggleExpand(root._id) : emit('select', root)"
        >
          <!-- Expand toggle -->
          <button
            v-if="root.children?.length"
            class="shrink-0 w-5 h-5 flex items-center justify-center text-muted-foreground"
            @click.stop="toggleExpand(root._id)"
          >
            <ChevronDown v-if="isExpanded(root._id)" :size="14" />
            <ChevronRight v-else :size="14" />
          </button>
          <div v-else class="w-5" />

          <ResourceTypeIcon :type="root.resourceType" :size="16" class="shrink-0" />

          <span
            class="text-sm font-medium text-foreground truncate flex-1 cursor-pointer hover:text-primary"
            @click.stop="emit('select', root)"
          >
            {{ root.title }}
          </span>

          <span
            v-if="root.qualityScore"
            class="text-xs font-medium text-muted-foreground shrink-0"
          >
            {{ root.qualityScore }}/10
          </span>

          <span
            class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
            :class="statusColors[root.status] || 'bg-muted text-muted-foreground'"
          >
            {{ root.status }}
          </span>

          <span
            v-if="root.children?.length"
            class="text-[10px] text-muted-foreground shrink-0"
          >
            {{ root.children.length }} children
          </span>
        </div>

        <!-- Children (expanded) -->
        <template v-if="isExpanded(root._id) && root.children?.length">
          <div
            v-for="child in root.children"
            :key="child._id"
            class="flex items-center gap-2 pl-12 pr-4 py-2 hover:bg-muted/30 transition-colors cursor-pointer border-t border-border/50"
            @click="emit('select', child)"
          >
            <ResourceTypeIcon :type="child.resourceType" :size="14" class="shrink-0 text-muted-foreground" />

            <span class="text-sm text-foreground truncate flex-1">
              {{ child.title }}
            </span>

            <span
              v-if="child.qualityScore"
              class="text-xs font-medium text-muted-foreground shrink-0"
            >
              {{ child.qualityScore }}/10
            </span>

            <span
              class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
              :class="statusColors[child.status] || 'bg-muted text-muted-foreground'"
            >
              {{ child.status }}
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
