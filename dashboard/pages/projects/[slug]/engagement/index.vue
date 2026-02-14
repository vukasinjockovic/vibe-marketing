<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'

const { project } = useCurrentProject()
const projectId = computed(() => project.value?._id)

const { data: channels, loading: loadingChannels } = useConvexQuery(
  api.channels.list,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const { data: batches, loading: loadingBatches } = useConvexQuery(
  api.contentBatches.list,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const showCreateChannel = ref(false)
const showCreateBatch = ref(false)
const editingChannel = ref<any>(null)
const showEditChannel = ref(false)

function openEditChannel(channel: any) {
  editingChannel.value = channel
  showEditChannel.value = true
}

function onChannelSaved() {
  showEditChannel.value = false
  editingChannel.value = null
}

function platformIcon(platform: string) {
  const icons: Record<string, string> = {
    facebook: 'F',
    x: 'X',
    linkedin: 'in',
    tiktok: 'T',
    instagram: 'I',
  }
  return icons[platform] || '?'
}

function platformColor(platform: string) {
  const colors: Record<string, string> = {
    facebook: '#1877F2',
    x: '#000000',
    linkedin: '#0A66C2',
    tiktok: '#000000',
    instagram: '#E4405F',
  }
  return colors[platform] || '#6366f1'
}

function formatDate(ts: number) {
  return new Date(ts).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function batchesForChannel(channelId: string) {
  if (!batches.value) return []
  return batches.value.filter((b: any) => b.channelId === channelId)
}

const recentBatches = computed(() => {
  if (!batches.value) return []
  return [...batches.value]
    .sort((a, b) => (b._creationTime || 0) - (a._creationTime || 0))
    .slice(0, 6)
})
</script>

<template>
  <div>
    <VPageHeader title="Engagement" description="Social media channels and content batches for organic growth">
      <template #actions>
        <div class="flex gap-2">
          <button
            class="border border-border text-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-muted transition-colors"
            @click="showCreateChannel = true"
          >
            New Channel
          </button>
          <button
            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
            @click="showCreateBatch = true"
          >
            New Batch
          </button>
        </div>
      </template>
    </VPageHeader>

    <!-- Channels -->
    <div class="mb-8">
      <h2 class="text-lg font-semibold text-foreground mb-3">Channels</h2>

      <div v-if="loadingChannels" class="text-muted-foreground text-sm">Loading channels...</div>

      <VEmptyState
        v-else-if="!channels?.length"
        title="No channels yet"
        description="Create a social media channel to start posting engagement content."
      >
        <button
          class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreateChannel = true"
        >
          Create Channel
        </button>
      </VEmptyState>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="channel in channels"
          :key="channel._id"
          class="rounded-lg border bg-card text-card-foreground shadow-sm p-5"
        >
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-9 h-9 rounded-lg flex items-center justify-center text-white text-sm font-bold"
              :style="{ backgroundColor: platformColor(channel.platform) }"
            >
              {{ platformIcon(channel.platform) }}
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="font-semibold text-foreground truncate">{{ channel.name }}</h3>
              <p class="text-xs text-muted-foreground capitalize">{{ channel.platform }}</p>
            </div>
            <VStatusBadge :status="channel.status" size="sm" />
          </div>
          <p v-if="channel.description" class="text-sm text-muted-foreground mb-3 line-clamp-2">
            {{ channel.description }}
          </p>
          <div class="flex items-center justify-between mt-3">
            <div class="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{{ batchesForChannel(channel._id).length }} batches</span>
              <span v-if="channel.platformConfig?.username">@{{ channel.platformConfig.username }}</span>
            </div>
            <button
              class="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded hover:bg-muted"
              @click="openEditChannel(channel)"
            >
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Engagement Resources Summary -->
    <div v-if="projectId && batches?.length">
      <h2 class="text-lg font-semibold text-foreground mb-3">Resources</h2>
      <ResourceStatsCards :project-id="projectId" />
    </div>

    <!-- Recent Batches -->
    <div>
      <h2 class="text-lg font-semibold text-foreground mb-3">Recent Batches</h2>

      <div v-if="loadingBatches" class="text-muted-foreground text-sm">Loading batches...</div>

      <VEmptyState
        v-else-if="!recentBatches.length"
        title="No content batches yet"
        description="Create a batch to generate engagement posts for your channels."
      >
        <button
          v-if="channels?.length"
          class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreateBatch = true"
        >
          Create Batch
        </button>
      </VEmptyState>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <NuxtLink
          v-for="batch in recentBatches"
          :key="batch._id"
          :to="`/projects/${$route.params.slug}/engagement/batches/${batch._id}`"
          class="rounded-lg border bg-card text-card-foreground shadow-sm p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-foreground truncate">{{ batch.name }}</h3>
            <VStatusBadge :status="batch.status" size="sm" />
          </div>
          <p v-if="batch.description" class="text-sm text-muted-foreground mb-3 line-clamp-2">
            {{ batch.description }}
          </p>
          <div class="flex items-center gap-3 text-xs text-muted-foreground">
            <span>{{ batch.batchSize }} posts</span>
            <span v-if="batch.contentThemes?.length">
              {{ batch.contentThemes.slice(0, 2).join(', ') }}
            </span>
            <span v-if="batch._creationTime">{{ formatDate(batch._creationTime) }}</span>
          </div>
        </NuxtLink>
      </div>
    </div>

    <!-- Create Channel Modal -->
    <VModal v-model="showCreateChannel" title="New Channel" size="lg" persistent>
      <ChannelForm
        v-if="projectId"
        :project-id="projectId"
        @created="showCreateChannel = false"
      />
    </VModal>

    <!-- Edit Channel Modal -->
    <VModal v-model="showEditChannel" title="Edit Channel" size="lg" persistent>
      <ChannelForm
        v-if="projectId && editingChannel"
        :project-id="projectId"
        :channel="editingChannel"
        @saved="onChannelSaved"
      />
    </VModal>

    <!-- Create Batch Modal -->
    <VModal v-model="showCreateBatch" title="New Content Batch" size="xl" persistent>
      <ContentBatchForm
        v-if="projectId"
        :project-id="projectId"
        @created="showCreateBatch = false"
      />
    </VModal>
  </div>
</template>
