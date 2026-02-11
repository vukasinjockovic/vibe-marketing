<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'

const route = useRoute()
const campaignId = computed(() => route.params.id as string)

const { data: campaign, loading } = useConvexQuery(
  api.campaigns.get,
  computed(() => campaignId.value ? { id: campaignId.value as any } : 'skip'),
)

const { data: tasks } = useConvexQuery(
  api.tasks.listByCampaign,
  computed(() => campaignId.value ? { campaignId: campaignId.value as any } : 'skip'),
)

const { data: focusGroups } = useConvexQuery(
  api.focusGroups.getByCampaign,
  computed(() => campaignId.value ? { campaignId: campaignId.value as any } : 'skip'),
)

const { mutate: activateCampaign } = useConvexMutation(api.campaigns.activate)
const { mutate: pauseCampaign } = useConvexMutation(api.campaigns.pause)
const { mutate: completeCampaign } = useConvexMutation(api.campaigns.complete)
const toast = useToast()

const showConfirmActivate = ref(false)
const showConfirmPause = ref(false)
const showConfirmComplete = ref(false)
const selectedTaskId = ref<string | null>(null)
const showTaskDetail = computed({
  get: () => !!selectedTaskId.value,
  set: (v: boolean) => { if (!v) selectedTaskId.value = null },
})

async function activate() {
  try {
    await activateCampaign({ id: campaignId.value as any })
    toast.success('Campaign activated!')
    showConfirmActivate.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to activate campaign')
  }
}

async function pause() {
  try {
    await pauseCampaign({ id: campaignId.value as any })
    toast.success('Campaign paused.')
    showConfirmPause.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to pause campaign')
  }
}

async function complete() {
  try {
    await completeCampaign({ id: campaignId.value as any })
    toast.success('Campaign completed!')
    showConfirmComplete.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to complete campaign')
  }
}

function formatDate(ts: number) {
  return new Date(ts).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const taskColumns = [
  { key: 'title', label: 'Title' },
  { key: 'contentType', label: 'Type' },
  { key: 'status', label: 'Status' },
  { key: 'priority', label: 'Priority' },
  { key: 'lockedBy', label: 'Agent' },
  { key: 'qualityScore', label: 'Quality' },
]

const taskStats = computed(() => {
  if (!tasks.value) return { total: 0, completed: 0, inProgress: 0 }
  return {
    total: tasks.value.length,
    completed: tasks.value.filter((t: any) => t.status === 'completed').length,
    inProgress: tasks.value.filter((t: any) => !['completed', 'cancelled', 'blocked', 'backlog'].includes(t.status)).length,
  }
})
</script>

<template>
  <div>
    <div v-if="loading" class="text-gray-500">Loading campaign...</div>

    <div v-else-if="!campaign" class="text-gray-500">Campaign not found.</div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <div class="flex items-center gap-3">
            <NuxtLink
              :to="`/projects/${$route.params.slug}/campaigns`"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <span class="i-heroicons-arrow-left text-lg" />
            </NuxtLink>
            <h1 class="text-2xl font-bold text-gray-900">{{ campaign.name }}</h1>
            <VStatusBadge :status="campaign.status" />
          </div>
          <p v-if="campaign.description" class="text-sm text-gray-500 mt-1 ml-9">
            {{ campaign.description }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="campaign.status === 'planning' || campaign.status === 'paused'"
            class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            @click="showConfirmActivate = true"
          >
            Activate
          </button>
          <button
            v-if="campaign.status === 'active'"
            class="bg-yellow-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-yellow-700 transition-colors"
            @click="showConfirmPause = true"
          >
            Pause
          </button>
          <button
            v-if="campaign.status === 'active' || campaign.status === 'paused'"
            class="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
            @click="showConfirmComplete = true"
          >
            Complete
          </button>
        </div>
      </div>

      <!-- Info cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Tasks overview -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Tasks</h3>
          <div class="text-2xl font-bold text-gray-900">{{ taskStats.total }}</div>
          <div class="flex gap-3 text-xs text-gray-500 mt-1">
            <span class="text-green-600">{{ taskStats.completed }} done</span>
            <span class="text-blue-600">{{ taskStats.inProgress }} active</span>
          </div>
        </div>

        <!-- Focus groups -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Focus Groups</h3>
          <div v-if="focusGroups?.length" class="space-y-1">
            <span
              v-for="fg in focusGroups"
              :key="fg._id"
              class="inline-block bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full mr-1 mb-1"
            >
              {{ fg.name }}
            </span>
          </div>
          <p v-else class="text-sm text-gray-400">None selected</p>
        </div>

        <!-- Keywords -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Keywords</h3>
          <div v-if="campaign.seedKeywords?.length" class="flex flex-wrap gap-1">
            <span
              v-for="kw in campaign.seedKeywords"
              :key="kw"
              class="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full"
            >
              {{ kw }}
            </span>
          </div>
          <p v-else class="text-sm text-gray-400">None</p>
        </div>

        <!-- Pipeline info -->
        <div class="bg-white rounded-lg shadow p-4">
          <h3 class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Pipeline</h3>
          <div v-if="campaign.pipelineSnapshot">
            <p class="text-sm font-medium">{{ campaign.pipelineSnapshot.name }}</p>
            <p class="text-xs text-gray-500">
              {{ campaign.pipelineSnapshot.mainSteps?.length || 0 }} steps
            </p>
          </div>
          <p v-else class="text-sm text-gray-400">Unknown</p>
        </div>
      </div>

      <!-- Tasks table -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-3">Tasks</h2>
        <VDataTable
          :columns="taskColumns"
          :rows="tasks || []"
          :loading="!tasks"
          empty-message="No tasks created for this campaign yet."
        >
          <template #cell-title="{ row }">
            <button
              class="text-left font-medium text-primary-600 hover:text-primary-700"
              @click="selectedTaskId = row._id"
            >
              {{ row.title }}
            </button>
          </template>
          <template #cell-contentType="{ row }">
            <span class="text-gray-600 text-xs bg-gray-100 px-2 py-0.5 rounded">
              {{ row.contentType || 'article' }}
            </span>
          </template>
          <template #cell-status="{ row }">
            <VStatusBadge :status="row.status" size="sm" />
          </template>
          <template #cell-priority="{ row }">
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              :class="{
                'bg-red-100 text-red-700': row.priority === 'urgent',
                'bg-orange-100 text-orange-700': row.priority === 'high',
                'bg-blue-100 text-blue-700': row.priority === 'medium',
                'bg-gray-100 text-gray-600': row.priority === 'low',
              }"
            >
              {{ row.priority }}
            </span>
          </template>
          <template #cell-lockedBy="{ row }">
            <span v-if="row.lockedBy" class="text-sm text-gray-700">{{ row.lockedBy }}</span>
            <span v-else class="text-xs text-gray-400">Unassigned</span>
          </template>
          <template #cell-qualityScore="{ row }">
            <span v-if="row.qualityScore" class="font-medium">{{ row.qualityScore }}/10</span>
            <span v-else class="text-xs text-gray-400">--</span>
          </template>
        </VDataTable>
      </div>

      <!-- Confirm dialogs -->
      <VConfirmDialog
        v-model="showConfirmActivate"
        title="Activate Campaign"
        message="This will start the campaign and allow agents to begin processing tasks. Continue?"
        confirm-label="Activate"
        confirm-class="bg-green-600 hover:bg-green-700"
        @confirm="activate"
      />
      <VConfirmDialog
        v-model="showConfirmPause"
        title="Pause Campaign"
        message="This will pause the campaign. Active tasks will finish but no new tasks will be started."
        confirm-label="Pause"
        confirm-class="bg-yellow-600 hover:bg-yellow-700"
        @confirm="pause"
      />
      <VConfirmDialog
        v-model="showConfirmComplete"
        title="Complete Campaign"
        message="Mark this campaign as completed? This cannot be undone."
        confirm-label="Complete"
        @confirm="complete"
      />

      <!-- Task detail modal -->
      <TaskDetailModal
        v-model="showTaskDetail"
        :task-id="selectedTaskId"
      />
    </template>
  </div>
</template>
