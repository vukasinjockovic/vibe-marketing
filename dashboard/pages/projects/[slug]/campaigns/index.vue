<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'

const { project } = useCurrentProject()
const projectId = computed(() => project.value?._id)

const { data: campaigns, loading } = useConvexQuery(
  api.campaigns.list,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const statusFilter = ref('all')
const statusTabs = ['all', 'planning', 'active', 'paused', 'completed']

const filteredCampaigns = computed(() => {
  if (!campaigns.value) return []
  if (statusFilter.value === 'all') return campaigns.value
  return campaigns.value.filter((c: any) => c.status === statusFilter.value)
})

const showCreateModal = ref(false)

function formatDate(ts: number) {
  return new Date(ts).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<template>
  <div>
    <VPageHeader title="Campaigns" description="Manage content campaigns for this project">
      <template #actions>
        <button
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreateModal = true"
        >
          New Campaign
        </button>
      </template>
    </VPageHeader>

    <!-- Status filter tabs -->
    <div class="flex gap-1 mb-6 bg-muted rounded-lg p-1 w-fit">
      <button
        v-for="tab in statusTabs"
        :key="tab"
        class="px-4 py-1.5 text-sm font-medium rounded-md transition-colors capitalize"
        :class="statusFilter === tab
          ? 'bg-background text-foreground shadow-sm'
          : 'text-muted-foreground hover:text-foreground'"
        @click="statusFilter = tab"
      >
        {{ tab }}
        <span
          v-if="tab !== 'all' && campaigns"
          class="ml-1 text-xs"
        >
          ({{ campaigns.filter((c: any) => c.status === tab).length }})
        </span>
        <span
          v-if="tab === 'all' && campaigns"
          class="ml-1 text-xs"
        >
          ({{ campaigns.length }})
        </span>
      </button>
    </div>

    <div v-if="loading" class="text-muted-foreground">Loading campaigns...</div>

    <VEmptyState
      v-else-if="!filteredCampaigns.length"
      title="No campaigns found"
      :description="statusFilter === 'all'
        ? 'Create your first campaign to start producing content.'
        : `No ${statusFilter} campaigns.`"
    >
      <button
        v-if="statusFilter === 'all'"
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        @click="showCreateModal = true"
      >
        Create Campaign
      </button>
    </VEmptyState>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink
        v-for="campaign in filteredCampaigns"
        :key="campaign._id"
        :to="`/projects/${$route.params.slug}/campaigns/${campaign._id}`"
        class="rounded-lg border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-foreground truncate">{{ campaign.name }}</h3>
          <VStatusBadge :status="campaign.status" size="sm" />
        </div>
        <p v-if="campaign.description" class="text-sm text-muted-foreground mb-4 line-clamp-2">
          {{ campaign.description }}
        </p>
        <div class="flex items-center gap-4 text-xs text-muted-foreground">
          <span v-if="campaign.seedKeywords?.length" class="flex items-center gap-1">
            {{ campaign.seedKeywords.length }} keywords
          </span>
          <span v-if="campaign._creationTime" class="flex items-center gap-1">
            {{ formatDate(campaign._creationTime) }}
          </span>
        </div>
      </NuxtLink>
    </div>

    <!-- Create campaign modal -->
    <VModal v-model="showCreateModal" title="New Campaign" size="xl" persistent>
      <CampaignForm
        v-if="projectId"
        :project-id="projectId"
        @created="showCreateModal = false"
      />
    </VModal>
  </div>
</template>
