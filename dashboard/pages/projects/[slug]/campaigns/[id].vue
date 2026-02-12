<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'
import { ArrowLeft } from 'lucide-vue-next'

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

// Load skills for writing strategy display
const { data: allSkills } = useConvexQuery(api.skills.list, {})

const skillMap = computed(() => {
  const map: Record<string, any> = {}
  if (allSkills.value) {
    for (const s of allSkills.value) map[s._id] = s
  }
  return map
})

const writingStrategySummary = computed(() => {
  const sc = campaign.value?.skillConfig
  if (!sc) return null
  const items: { layer: string; name: string; subs?: string[] }[] = []
  if (sc.offerFramework?.skillId) {
    const s = skillMap.value[sc.offerFramework.skillId]
    if (s) items.push({ layer: 'L2', name: s.displayName })
  }
  if (sc.persuasionSkills?.length) {
    for (const ps of sc.persuasionSkills) {
      const s = skillMap.value[ps.skillId]
      if (s) items.push({ layer: 'L3', name: s.displayName, subs: ps.subSelections })
    }
  }
  if (sc.primaryCopyStyle?.skillId) {
    const s = skillMap.value[sc.primaryCopyStyle.skillId]
    if (s) items.push({ layer: 'L4', name: s.displayName })
  }
  return items.length > 0 ? items : null
})

const { mutate: activateCampaign } = useConvexMutation(api.campaigns.activate)
const { mutate: pauseCampaign } = useConvexMutation(api.campaigns.pause)
const { mutate: resumeCampaign } = useConvexMutation(api.campaigns.resume)
const { mutate: completeCampaign } = useConvexMutation(api.campaigns.complete)
const toast = useToast()

const showEdit = ref(false)
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

async function resume() {
  try {
    await resumeCampaign({ id: campaignId.value as any })
    toast.success('Campaign resumed!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to resume campaign')
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
  if (!tasks.value) return { total: 0, completed: 0, inProgress: 0, backlog: 0, blocked: 0 }
  return {
    total: tasks.value.length,
    completed: tasks.value.filter((t: any) => t.status === 'completed').length,
    inProgress: tasks.value.filter((t: any) => !['completed', 'cancelled', 'blocked', 'backlog'].includes(t.status)).length,
    backlog: tasks.value.filter((t: any) => t.status === 'backlog').length,
    blocked: tasks.value.filter((t: any) => t.status === 'blocked').length,
  }
})

const progressPercent = computed(() => {
  if (!taskStats.value.total) return 0
  return Math.round((taskStats.value.completed / taskStats.value.total) * 100)
})
</script>

<template>
  <div>
    <div v-if="loading" class="text-muted-foreground">Loading campaign...</div>

    <div v-else-if="!campaign" class="text-muted-foreground">Campaign not found.</div>

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <div class="flex items-center gap-3">
            <NuxtLink
              :to="`/projects/${$route.params.slug}/campaigns`"
              class="text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft :size="18" />
            </NuxtLink>
            <h1 class="text-2xl font-bold text-foreground">{{ campaign.name }}</h1>
          </div>
          <div class="flex items-center gap-2 mt-1 ml-9">
            <VStatusBadge :status="campaign.status" />
            <p v-if="campaign.description" class="text-sm text-muted-foreground">
              {{ campaign.description }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="px-3 py-2 text-sm border border-border rounded-md text-muted-foreground hover:bg-muted transition-colors"
            @click="showEdit = true"
          >
            Edit
          </button>
          <button
            v-if="campaign.status === 'planning'"
            class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            @click="showConfirmActivate = true"
          >
            Activate
          </button>
          <button
            v-if="campaign.status === 'paused'"
            class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            @click="resume"
          >
            Resume
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
            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
            @click="showConfirmComplete = true"
          >
            Complete
          </button>
        </div>
      </div>

      <!-- Info cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Tasks overview -->
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Tasks</h3>
          <div class="text-2xl font-bold text-foreground">{{ taskStats.total }}</div>
          <div class="flex gap-3 text-xs text-muted-foreground mt-1">
            <span class="text-green-600">{{ taskStats.completed }} done</span>
            <span class="text-blue-600">{{ taskStats.inProgress }} active</span>
          </div>
        </div>

        <!-- Focus groups -->
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Focus Groups</h3>
          <div v-if="focusGroups?.length" class="space-y-1">
            <span
              v-for="fg in focusGroups"
              :key="fg._id"
              class="inline-block bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full mr-1 mb-1"
            >
              {{ fg.name }}
            </span>
          </div>
          <p v-else class="text-sm text-muted-foreground/70">None selected</p>
        </div>

        <!-- Keywords -->
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Keywords</h3>
          <div v-if="campaign.seedKeywords?.length" class="flex flex-wrap gap-1">
            <span
              v-for="kw in campaign.seedKeywords"
              :key="kw"
              class="inline-block bg-muted text-muted-foreground text-xs px-2 py-0.5 rounded-full"
            >
              {{ kw }}
            </span>
          </div>
          <p v-else class="text-sm text-muted-foreground/70">None</p>
        </div>

        <!-- Pipeline info -->
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Pipeline</h3>
          <div v-if="campaign.pipelineSnapshot">
            <p class="text-sm font-medium text-foreground">{{ campaign.pipelineSnapshot.name }}</p>
            <p class="text-xs text-muted-foreground">
              {{ campaign.pipelineSnapshot.mainSteps?.length || 0 }} steps
            </p>
          </div>
          <p v-else class="text-sm text-muted-foreground/70">Unknown</p>
        </div>
      </div>

      <!-- Writing Strategy -->
      <div v-if="writingStrategySummary" class="mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-sm font-medium text-foreground mb-3">Writing Strategy</h3>
          <div class="flex flex-wrap gap-2 mb-2">
            <span class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-medium">
              L1: Schwartz Awareness
              <span class="text-blue-400 font-normal">(auto)</span>
            </span>
            <span
              v-for="item in writingStrategySummary"
              :key="item.name"
              class="inline-flex items-center gap-1 bg-primary/10 text-primary text-xs px-2.5 py-1 rounded-full font-medium"
            >
              {{ item.layer }}: {{ item.name }}
              <template v-if="item.subs?.length">
                <span class="text-primary/60 font-normal">[{{ item.subs.join(', ') }}]</span>
              </template>
            </span>
            <span class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2.5 py-1 rounded-full font-medium">
              L5: Quality
              <span class="text-blue-400 font-normal">(auto)</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Pipeline Progress -->
      <div v-if="taskStats.total > 0" class="mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-foreground">Pipeline Progress</h3>
            <span class="text-sm font-medium text-foreground">{{ progressPercent }}%</span>
          </div>
          <div class="w-full bg-muted rounded-full h-2.5 mb-3">
            <div
              class="h-2.5 rounded-full transition-all duration-500"
              :class="progressPercent === 100 ? 'bg-green-500' : 'bg-primary'"
              :style="{ width: `${progressPercent}%` }"
            />
          </div>
          <div class="flex gap-3 text-xs">
            <span v-if="taskStats.completed" class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-green-500" />
              {{ taskStats.completed }} completed
            </span>
            <span v-if="taskStats.inProgress" class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              {{ taskStats.inProgress }} in progress
            </span>
            <span v-if="taskStats.backlog" class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-muted-foreground/40" />
              {{ taskStats.backlog }} queued
            </span>
            <span v-if="taskStats.blocked" class="flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-red-500" />
              {{ taskStats.blocked }} blocked
            </span>
          </div>
        </div>
      </div>

      <!-- Tasks table -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Tasks</h2>
        <VDataTable
          :columns="taskColumns"
          :rows="tasks || []"
          :loading="!tasks"
          empty-message="No tasks created for this campaign yet."
        >
          <template #cell-title="{ row }">
            <button
              class="text-left font-medium text-primary hover:text-primary/80"
              @click="selectedTaskId = row._id"
            >
              {{ row.title }}
            </button>
          </template>
          <template #cell-contentType="{ row }">
            <span class="text-muted-foreground text-xs bg-muted px-2 py-0.5 rounded">
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
                'bg-muted text-muted-foreground': row.priority === 'low',
              }"
            >
              {{ row.priority }}
            </span>
          </template>
          <template #cell-lockedBy="{ row }">
            <span v-if="row.lockedBy" class="text-sm text-foreground">{{ row.lockedBy }}</span>
            <span v-else class="text-xs text-muted-foreground/70">Unassigned</span>
          </template>
          <template #cell-qualityScore="{ row }">
            <span v-if="row.qualityScore" class="font-medium">{{ row.qualityScore }}/10</span>
            <span v-else class="text-xs text-muted-foreground/70">--</span>
          </template>
        </VDataTable>
      </div>

      <!-- Edit Modal -->
      <VModal v-model="showEdit" title="Edit Campaign" size="xl" persistent>
        <CampaignForm
          v-if="campaign"
          :project-id="campaign.projectId"
          :campaign="campaign"
          @saved="showEdit = false"
        />
      </VModal>

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
