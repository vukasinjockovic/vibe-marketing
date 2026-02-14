<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { FileStack } from 'lucide-vue-next'

const props = defineProps<{
  projectId?: any
  campaignId?: any
  contentBatchId?: any
}>()

const queryArgs = computed(() => {
  if (props.campaignId) return { campaignId: props.campaignId }
  if (props.contentBatchId) return { contentBatchId: props.contentBatchId }
  if (props.projectId) return { projectId: props.projectId }
  return 'skip'
})

const { data: stats, loading } = useConvexQuery(api.resources.stats, queryArgs)

const typeLabels: Record<string, string> = {
  research_material: 'Research',
  brief: 'Briefs',
  article: 'Articles',
  landing_page: 'Landing Pages',
  ad_copy: 'Ad Copy',
  social_post: 'Social Posts',
  email_sequence: 'Email Sequences',
  email_excerpt: 'Email Excerpts',
  image_prompt: 'Image Prompts',
  image: 'Images',
  video_script: 'Video Scripts',
  lead_magnet: 'Lead Magnets',
  report: 'Reports',
  brand_asset: 'Brand Assets',
}

const topTypes = computed(() => {
  if (!stats.value?.byType) return []
  return Object.entries(stats.value.byType)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([type, count]) => ({
      type,
      label: typeLabels[type] || type,
      count,
    }))
})
</script>

<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
    <!-- Total card -->
    <div class="rounded-lg border bg-card shadow-sm p-4">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-primary/10 text-primary">
          <FileStack :size="18" />
        </div>
        <div>
          <p class="text-2xl font-bold text-foreground">{{ stats?.total || 0 }}</p>
          <p class="text-xs text-muted-foreground">Total Resources</p>
        </div>
      </div>
    </div>

    <!-- Top type cards -->
    <div
      v-for="item in topTypes"
      :key="item.type"
      class="rounded-lg border bg-card shadow-sm p-4"
    >
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-muted">
          <ResourceTypeIcon :type="item.type" :size="18" />
        </div>
        <div>
          <p class="text-2xl font-bold text-foreground">{{ item.count }}</p>
          <p class="text-xs text-muted-foreground">{{ item.label }}</p>
        </div>
      </div>
    </div>

    <!-- Loading skeleton -->
    <template v-if="loading">
      <div v-for="i in 5" :key="i" class="rounded-lg border bg-card shadow-sm p-4">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-muted animate-pulse" />
          <div class="space-y-1">
            <div class="h-6 w-10 bg-muted rounded animate-pulse" />
            <div class="h-3 w-16 bg-muted/60 rounded animate-pulse" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
