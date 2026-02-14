<script setup lang="ts">
import { api } from '../../../../../../convex/_generated/api'
import { ArrowLeft } from 'lucide-vue-next'

const route = useRoute()
const batchId = computed(() => route.params.id as string)

const { data: batch, loading } = useConvexQuery(
  api.contentBatches.get,
  computed(() => batchId.value ? { id: batchId.value as any } : 'skip'),
)

const { data: channel } = useConvexQuery(
  api.channels.get,
  computed(() => batch.value?.channelId ? { id: batch.value.channelId as any } : 'skip'),
)

const { data: tasks } = useConvexQuery(
  api.tasks.listByContentBatch,
  computed(() => batchId.value ? { contentBatchId: batchId.value as any } : 'skip'),
)

const { data: activities } = useConvexQuery(
  api.activities.listByContentBatch,
  computed(() => batchId.value ? { contentBatchId: batchId.value as any } : 'skip'),
)

const { data: focusGroups } = useConvexQuery(
  api.focusGroups.getByContentBatch,
  computed(() => batchId.value ? { contentBatchId: batchId.value as any } : 'skip'),
)

const { mutate: activateBatch } = useConvexMutation(api.contentBatches.activate)
const { mutate: pauseBatch } = useConvexMutation(api.contentBatches.pause)
const { mutate: resumeBatch } = useConvexMutation(api.contentBatches.resume)
const { mutate: completeBatch } = useConvexMutation(api.contentBatches.complete)
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
    await activateBatch({ id: batchId.value as any })
    toast.success('Batch activated!')
    showConfirmActivate.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to activate batch')
  }
}

async function pause() {
  try {
    await pauseBatch({ id: batchId.value as any })
    toast.success('Batch paused.')
    showConfirmPause.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to pause batch')
  }
}

async function resume() {
  try {
    await resumeBatch({ id: batchId.value as any })
    toast.success('Batch resumed!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to resume batch')
  }
}

async function complete() {
  try {
    await completeBatch({ id: batchId.value as any })
    toast.success('Batch completed!')
    showConfirmComplete.value = false
  } catch (e: any) {
    toast.error(e.message || 'Failed to complete batch')
  }
}

const taskColumns = [
  { key: 'title', label: 'Title' },
  { key: 'status', label: 'Status' },
  { key: 'lockedBy', label: 'Agent' },
  { key: 'qualityScore', label: 'Quality' },
]

// Single-task model: one task produces all posts
const batchTask = computed(() => tasks.value?.[0] || null)

const pipelineSteps = computed(() => {
  if (!batchTask.value?.pipeline) return []
  return batchTask.value.pipeline as { step: number; status: string; description: string; agent?: string }[]
})

const currentStepIndex = computed(() => batchTask.value?.pipelineStep ?? 0)

const pipelineProgress = computed(() => {
  const steps = pipelineSteps.value
  if (!steps.length) return { completed: 0, total: 0, percent: 0 }
  const completed = steps.filter(s => s.status === 'completed').length
  return {
    completed,
    total: steps.length,
    percent: Math.round((completed / steps.length) * 100),
  }
})

// Activity pagination
const activityPage = ref(1)
const activityPerPage = 10

const sortedActivities = computed(() => {
  if (!activities.value) return []
  return [...activities.value].sort((a, b) => (b._creationTime || 0) - (a._creationTime || 0))
})

const activityTotalPages = computed(() =>
  Math.max(1, Math.ceil(sortedActivities.value.length / activityPerPage))
)

const paginatedActivities = computed(() => {
  const start = (activityPage.value - 1) * activityPerPage
  return sortedActivities.value.slice(start, start + activityPerPage)
})

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
  <div>
    <div v-if="loading" class="text-muted-foreground">Loading batch...</div>

    <div v-else-if="!batch" class="text-muted-foreground">Batch not found.</div>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div class="min-w-0">
          <div class="flex items-center gap-3">
            <NuxtLink
              :to="`/projects/${$route.params.slug}/engagement`"
              class="text-muted-foreground hover:text-foreground transition-colors shrink-0"
            >
              <ArrowLeft :size="18" />
            </NuxtLink>
            <h1 class="text-xl sm:text-2xl font-bold text-foreground truncate">{{ batch.name }}</h1>
          </div>
          <div class="flex items-center gap-2 mt-1 ml-9 flex-wrap">
            <VStatusBadge :status="batch.status" />
            <span v-if="channel" class="text-sm text-muted-foreground capitalize">
              {{ channel.platform }} &middot; {{ channel.name }}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-wrap shrink-0">
          <button
            v-if="batch.status === 'planning'"
            class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            @click="showConfirmActivate = true"
          >
            Activate
          </button>
          <button
            v-if="batch.status === 'paused'"
            class="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
            @click="resume"
          >
            Resume
          </button>
          <button
            v-if="batch.status === 'active'"
            class="bg-yellow-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-yellow-700 transition-colors"
            @click="showConfirmPause = true"
          >
            Pause
          </button>
          <button
            v-if="batch.status === 'active' || batch.status === 'paused'"
            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
            @click="showConfirmComplete = true"
          >
            Complete
          </button>
        </div>
      </div>

      <!-- Info cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Posts</h3>
          <div class="text-2xl font-bold text-foreground">{{ batch.batchSize }}</div>
          <div class="text-xs text-muted-foreground mt-1">
            <template v-if="batchTask">
              <VStatusBadge :status="batchTask.status" size="sm" />
            </template>
            <span v-else>Waiting for activation</span>
          </div>
        </div>

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

        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Themes</h3>
          <div v-if="batch.contentThemes?.length" class="flex flex-wrap gap-1">
            <span
              v-for="theme in batch.contentThemes"
              :key="theme"
              class="inline-block bg-muted text-muted-foreground text-xs px-2 py-0.5 rounded-full"
            >
              {{ theme }}
            </span>
          </div>
          <p v-else class="text-sm text-muted-foreground/70">None</p>
        </div>

        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Pipeline</h3>
          <div v-if="batch.pipelineSnapshot">
            <p class="text-sm font-medium text-foreground">{{ (batch.pipelineSnapshot as any).name }}</p>
            <p class="text-xs text-muted-foreground">
              {{ (batch.pipelineSnapshot as any).mainSteps?.length || 0 }} steps
            </p>
          </div>
          <p v-else class="text-sm text-muted-foreground/70">Not snapshotted yet</p>
        </div>
      </div>

      <!-- Mix Config -->
      <div v-if="batch.mixConfig" class="mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <h3 class="text-sm font-medium text-foreground mb-3">Content Mix</h3>
          <div class="flex flex-wrap gap-3">
            <div v-if="batch.mixConfig.questions" class="text-xs">
              <span class="font-medium">Questions:</span> {{ batch.mixConfig.questions }}%
            </div>
            <div v-if="batch.mixConfig.emotional" class="text-xs">
              <span class="font-medium">Emotional:</span> {{ batch.mixConfig.emotional }}%
            </div>
            <div v-if="batch.mixConfig.interactive" class="text-xs">
              <span class="font-medium">Interactive:</span> {{ batch.mixConfig.interactive }}%
            </div>
            <div v-if="batch.mixConfig.debate" class="text-xs">
              <span class="font-medium">Debate:</span> {{ batch.mixConfig.debate }}%
            </div>
            <div v-if="batch.mixConfig.textOnly" class="text-xs">
              <span class="font-medium">Text Only:</span> {{ batch.mixConfig.textOnly }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Pipeline Progress -->
      <div v-if="batchTask" class="mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-medium text-foreground">Pipeline Progress</h3>
            <span class="text-sm font-medium text-foreground">{{ pipelineProgress.percent }}%</span>
          </div>
          <div class="w-full bg-muted rounded-full h-2.5 mb-4">
            <div
              class="h-2.5 rounded-full transition-all duration-500"
              :class="pipelineProgress.percent === 100 ? 'bg-green-500' : 'bg-primary'"
              :style="{ width: `${pipelineProgress.percent}%` }"
            />
          </div>
          <!-- Step-by-step view -->
          <div class="space-y-2">
            <div
              v-for="(step, idx) in pipelineSteps"
              :key="idx"
              class="flex items-center gap-3 text-sm"
            >
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium shrink-0"
                :class="{
                  'bg-green-100 text-green-700': step.status === 'completed',
                  'bg-blue-100 text-blue-700 animate-pulse': step.status === 'in_progress',
                  'bg-muted text-muted-foreground': step.status === 'pending',
                }"
              >
                <template v-if="step.status === 'completed'">&#10003;</template>
                <template v-else>{{ idx }}</template>
              </span>
              <span
                class="truncate"
                :class="{
                  'text-foreground font-medium': step.status === 'in_progress',
                  'text-foreground': step.status === 'completed',
                  'text-muted-foreground': step.status === 'pending',
                }"
              >
                {{ step.description }}
              </span>
              <span v-if="step.agent && step.status === 'in_progress'" class="text-xs text-blue-600 shrink-0">
                {{ step.agent }}
              </span>
            </div>
          </div>
          <!-- Pending branches -->
          <div v-if="batchTask.pendingBranches?.length" class="mt-3 pt-3 border-t">
            <p class="text-xs text-muted-foreground mb-1">Parallel branches:</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="branch in batchTask.pendingBranches"
                :key="branch"
                class="text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 animate-pulse"
              >
                {{ branch }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Batch Task -->
      <div v-if="batchTask" class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Batch Task</h2>
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <div class="flex items-start sm:items-center justify-between gap-3 flex-col sm:flex-row">
            <div class="min-w-0">
              <button
                class="text-left font-medium text-primary hover:text-primary/80 text-sm"
                @click="selectedTaskId = batchTask._id"
              >
                {{ batchTask.title }}
              </button>
              <div class="flex items-center gap-2 mt-1 flex-wrap">
                <VStatusBadge :status="batchTask.status" size="sm" />
                <span v-if="batchTask.lockedBy" class="text-xs text-muted-foreground">
                  Agent: <span class="font-medium text-foreground">{{ batchTask.lockedBy }}</span>
                </span>
                <span v-if="batchTask.qualityScore" class="text-xs text-muted-foreground">
                  Quality: <span class="font-medium text-foreground">{{ batchTask.qualityScore }}/10</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="batch.status === 'planning'" class="mb-6">
        <div class="rounded-lg border bg-card shadow-sm p-4 text-sm text-muted-foreground">
          Activate the batch to start the pipeline. All {{ batch.batchSize }} posts will be produced in a single pipeline run.
        </div>
      </div>

      <!-- Resources -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Resources</h2>
        <ResourceStatsCards :content-batch-id="batchId" />
        <div class="mt-3">
          <ResourceTable :content-batch-id="batchId" @select="(r) => $router.push(`/projects/${$route.params.slug}/resources/${r._id}`)" />
        </div>
      </div>

      <!-- Services -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Service Health</h2>
        <div class="rounded-lg border bg-card shadow-sm p-4">
          <ServiceOverridePanel :content-batch-id="batchId" />
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Recent Activity</h2>
        <div class="rounded-lg border bg-card shadow-sm">
          <div v-if="!activities" class="p-6 text-center text-sm text-muted-foreground">Loading...</div>
          <div v-else-if="sortedActivities.length === 0" class="p-6 text-center text-sm text-muted-foreground">
            No activity recorded for this batch yet.
          </div>
          <template v-else>
            <div class="divide-y divide-border">
              <div
                v-for="activity in paginatedActivities"
                :key="activity._id"
                class="px-4 py-3"
              >
                <div class="flex items-start gap-2">
                  <span class="inline-flex w-6 h-6 rounded-full bg-muted text-xs items-center justify-center text-muted-foreground font-medium shrink-0 mt-0.5">
                    {{ (activity.agentName || '?')[0].toUpperCase() }}
                  </span>
                  <div class="min-w-0 flex-1">
                    <p class="text-sm text-foreground">
                      <span class="font-medium">{{ activity.agentName }}</span>
                      {{ activity.message }}
                    </p>
                    <div class="flex items-center gap-2 mt-0.5">
                      <span v-if="activity.type" class="text-[10px] bg-muted text-muted-foreground px-1.5 py-0.5 rounded">
                        {{ activity.type }}
                      </span>
                      <span v-if="activity._creationTime" class="text-xs text-muted-foreground/70">
                        {{ formatTime(activity._creationTime) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="activityTotalPages > 1" class="px-4 py-3 border-t flex items-center justify-between">
              <span class="text-xs text-muted-foreground">
                {{ sortedActivities.length }} activities
              </span>
              <div class="flex items-center gap-1">
                <button
                  :disabled="activityPage <= 1"
                  class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  @click="activityPage--"
                >
                  Prev
                </button>
                <button
                  :disabled="activityPage >= activityTotalPages"
                  class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  @click="activityPage++"
                >
                  Next
                </button>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Confirm dialogs -->
      <VConfirmDialog
        v-model="showConfirmActivate"
        title="Activate Batch"
        :message="`This will start the engagement pipeline to produce all ${batch.batchSize} posts in a single run. Continue?`"
        confirm-label="Activate"
        confirm-class="bg-green-600 hover:bg-green-700"
        @confirm="activate"
      />
      <VConfirmDialog
        v-model="showConfirmPause"
        title="Pause Batch"
        message="The current pipeline step will finish but no further steps will be dispatched."
        confirm-label="Pause"
        confirm-class="bg-yellow-600 hover:bg-yellow-700"
        @confirm="pause"
      />
      <VConfirmDialog
        v-model="showConfirmComplete"
        title="Complete Batch"
        message="Mark this batch as completed? This cannot be undone."
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
