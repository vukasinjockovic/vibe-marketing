<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  campaignId: any
}>()

const { data: progress, loading } = useConvexQuery(
  api.resources.campaignProgress,
  computed(() => props.campaignId ? { campaignId: props.campaignId } : 'skip'),
)

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

const progressEntries = computed(() => {
  if (!progress.value) return []
  return Object.entries(progress.value)
    .map(([type, counts]: [string, any]) => ({
      type,
      label: typeLabels[type] || type.replace(/_/g, ' '),
      total: counts.total,
      draft: counts.draft,
      reviewed: counts.reviewed,
      published: counts.published,
      percent: counts.total > 0 ? Math.round(((counts.reviewed + counts.published) / counts.total) * 100) : 0,
    }))
    .sort((a, b) => b.total - a.total)
})

const overallStats = computed(() => {
  if (!progressEntries.value.length) return { total: 0, completed: 0, percent: 0 }
  const total = progressEntries.value.reduce((sum, e) => sum + e.total, 0)
  const completed = progressEntries.value.reduce((sum, e) => sum + e.reviewed + e.published, 0)
  return {
    total,
    completed,
    percent: total > 0 ? Math.round((completed / total) * 100) : 0,
  }
})
</script>

<template>
  <div class="rounded-lg border bg-card shadow-sm p-4">
    <div v-if="loading" class="text-sm text-muted-foreground text-center py-4">Loading progress...</div>

    <div v-else-if="!progressEntries.length" class="text-sm text-muted-foreground text-center py-4">
      No resources produced yet.
    </div>

    <template v-else>
      <!-- Overall progress -->
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-foreground">Resource Progress</h3>
        <span class="text-sm font-medium text-foreground">{{ overallStats.percent }}%</span>
      </div>
      <div class="w-full bg-muted rounded-full h-2.5 mb-4">
        <div
          class="h-2.5 rounded-full transition-all duration-500"
          :class="overallStats.percent === 100 ? 'bg-green-500' : 'bg-primary'"
          :style="{ width: `${overallStats.percent}%` }"
        />
      </div>
      <p class="text-xs text-muted-foreground mb-4">
        {{ overallStats.completed }} of {{ overallStats.total }} resources reviewed or published
      </p>

      <!-- Per-type breakdown -->
      <div class="space-y-3">
        <div
          v-for="entry in progressEntries"
          :key="entry.type"
          class="flex items-center gap-3"
        >
          <ResourceTypeIcon :type="entry.type" :size="16" class="shrink-0 text-muted-foreground" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-0.5">
              <span class="text-xs font-medium text-foreground truncate">{{ entry.label }}</span>
              <span class="text-xs text-muted-foreground shrink-0 ml-2">
                {{ entry.reviewed + entry.published }}/{{ entry.total }}
              </span>
            </div>
            <div class="w-full bg-muted rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full transition-all duration-300"
                :class="entry.percent === 100 ? 'bg-green-500' : 'bg-primary/70'"
                :style="{ width: `${entry.percent}%` }"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
