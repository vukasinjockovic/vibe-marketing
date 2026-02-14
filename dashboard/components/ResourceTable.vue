<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { ChevronRight, AlertTriangle } from 'lucide-vue-next'

const props = defineProps<{
  projectId?: any
  campaignId?: any
  contentBatchId?: any
  resourceType?: string
}>()

const emit = defineEmits<{
  select: [resource: any]
}>()

// Pick the right query based on props
const queryFn = computed(() => {
  if (props.campaignId) return api.resources.listByCampaign
  if (props.contentBatchId) return api.resources.listByContentBatch
  if (props.resourceType && props.projectId) return api.resources.listByType
  if (props.projectId) return api.resources.listByProject
  return null
})

const queryArgs = computed(() => {
  if (!queryFn.value) return 'skip'
  if (props.campaignId) return { campaignId: props.campaignId }
  if (props.contentBatchId) return { contentBatchId: props.contentBatchId }
  if (props.resourceType && props.projectId) return { projectId: props.projectId, resourceType: props.resourceType }
  if (props.projectId) return { projectId: props.projectId }
  return 'skip'
})

const { data: result, loading } = useConvexQuery(
  computed(() => queryFn.value || api.resources.listByProject),
  queryArgs,
)

const resources = computed(() => result.value?.page || [])

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
  <div class="rounded-lg border bg-card shadow-sm">
    <!-- Loading -->
    <div v-if="loading" class="p-8 text-center text-muted-foreground">
      Loading resources...
    </div>

    <!-- Empty state -->
    <div v-else-if="resources.length === 0" class="p-8 text-center text-muted-foreground">
      No resources found
    </div>

    <!-- Table -->
    <table v-else class="w-full">
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
  </div>
</template>
