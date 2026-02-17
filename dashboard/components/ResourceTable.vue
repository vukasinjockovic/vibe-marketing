<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { ChevronRight, AlertTriangle } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  projectId?: any
  campaignId?: any
  contentBatchId?: any
  resourceType?: string
  pageSize?: number
}>(), {
  pageSize: 25,
})

const emit = defineEmits<{
  select: [resource: any]
}>()

// Separate queries — useConvexQuery needs a static function reference, not a computed
const paginationOpts = { numItems: 200 }

const { data: campaignResult, loading: loadingCampaign } = useConvexQuery(
  api.resources.listByCampaign,
  computed(() => props.campaignId ? { campaignId: props.campaignId, paginationOpts } : 'skip'),
)

const { data: batchResult, loading: loadingBatch } = useConvexQuery(
  api.resources.listByContentBatch,
  computed(() => !props.campaignId && props.contentBatchId ? { contentBatchId: props.contentBatchId, paginationOpts } : 'skip'),
)

const { data: typeResult, loading: loadingType } = useConvexQuery(
  api.resources.listByType,
  computed(() => !props.campaignId && !props.contentBatchId && props.resourceType && props.projectId ? { projectId: props.projectId, resourceType: props.resourceType, paginationOpts } : 'skip'),
)

const { data: projectResult, loading: loadingProject } = useConvexQuery(
  api.resources.listByProject,
  computed(() => !props.campaignId && !props.contentBatchId && !props.resourceType && props.projectId ? { projectId: props.projectId, paginationOpts } : 'skip'),
)

const result = computed(() => campaignResult.value || batchResult.value || typeResult.value || projectResult.value)
const loading = computed(() => loadingCampaign.value || loadingBatch.value || loadingType.value || loadingProject.value)

const rawResources = computed(() => result.value?.page || [])

// Client-side type filter (when using batch/campaign query but also filtering by type)
const allResources = computed(() => {
  if (!props.resourceType || (!props.campaignId && !props.contentBatchId)) return rawResources.value
  return rawResources.value.filter((r: any) => r.resourceType === props.resourceType)
})

// Client-side pagination
const currentPage = ref(1)
const totalPages = computed(() => Math.max(1, Math.ceil(allResources.value.length / props.pageSize)))
const resources = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return allResources.value.slice(start, start + props.pageSize)
})

// Reset page when filter changes
watch(() => [props.contentBatchId, props.campaignId, props.projectId, props.resourceType], () => { currentPage.value = 1 })

const typeLabels: Record<string, string> = {
  research_material: 'Research',
  brief: 'Brief',
  article: 'Article',
  landing_page: 'Landing Page',
  ad_copy: 'Ad Copy',
  social_post: 'Social Post',
  email_sequence: 'Email Sequence',
  email_excerpt: 'Email Excerpt',
  image_prompt: 'Image Prompt',
  image: 'Image',
  video_script: 'Video Script',
  lead_magnet: 'Lead Magnet',
  report: 'Report',
  brand_asset: 'Brand Asset',
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  in_review: 'bg-blue-100 text-blue-700',
  reviewed: 'bg-amber-100 text-amber-700',
  humanized: 'bg-teal-100 text-teal-700',
  approved: 'bg-emerald-100 text-emerald-700',
  published: 'bg-green-100 text-green-700',
  archived: 'bg-muted text-muted-foreground',
}

function formatTime(ts: number) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}
</script>

<template>
  <div class="rounded-lg border bg-card shadow-sm overflow-x-auto">
    <!-- Loading -->
    <div v-if="loading" class="p-8 text-center text-muted-foreground">
      Loading resources...
    </div>

    <!-- Empty state -->
    <div v-else-if="resources.length === 0" class="p-8 text-center text-muted-foreground">
      No resources found
    </div>

    <!-- Table -->
    <table v-else class="w-full min-w-[600px]">
      <thead>
        <tr class="border-b text-left text-sm text-muted-foreground">
          <th class="px-4 py-3 font-medium">Resource</th>
          <th class="px-4 py-3 font-medium">Type</th>
          <th class="px-4 py-3 font-medium">Status</th>
          <th class="px-4 py-3 font-medium">Created By</th>
          <th class="px-4 py-3 font-medium">Created</th>
          <th class="px-4 py-3 font-medium w-8"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="r in resources"
          :key="r._id"
          class="border-b last:border-0 hover:bg-muted/50 cursor-pointer transition-colors"
          @click="emit('select', r)"
        >
          <td class="px-4 py-3">
            <div class="flex items-center gap-2">
              <ResourceTypeIcon :type="r.resourceType" :size="16" />
              <span class="font-medium text-sm text-foreground">{{ r.title }}</span>
              <AlertTriangle v-if="r.fileOrphaned" :size="14" class="text-amber-500" title="File not found on disk" />
            </div>
            <p v-if="r.slug" class="text-xs text-muted-foreground mt-0.5">{{ r.slug }}</p>
          </td>
          <td class="px-4 py-3">
            <span class="text-xs text-muted-foreground">{{ typeLabels[r.resourceType] || r.resourceType }}</span>
          </td>
          <td class="px-4 py-3">
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              :class="statusColors[r.status] || 'bg-muted text-muted-foreground'"
            >
              {{ r.status.replace('_', ' ') }}
            </span>
          </td>
          <td class="px-4 py-3">
            <span class="text-xs text-muted-foreground">{{ r.createdBy }}</span>
          </td>
          <td class="px-4 py-3">
            <span class="text-xs text-muted-foreground">{{ formatTime(r.createdAt) }}</span>
          </td>
          <td class="px-4 py-3">
            <ChevronRight :size="16" class="text-muted-foreground" />
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="px-4 py-3 border-t flex items-center justify-between">
      <span class="text-xs text-muted-foreground">
        {{ allResources.length }} resource{{ allResources.length !== 1 ? 's' : '' }}
      </span>
      <div class="flex items-center gap-1">
        <button
          :disabled="currentPage <= 1"
          class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="currentPage--"
        >
          Prev
        </button>
        <span class="text-xs text-muted-foreground px-2">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button
          :disabled="currentPage >= totalPages"
          class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="currentPage++"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>
