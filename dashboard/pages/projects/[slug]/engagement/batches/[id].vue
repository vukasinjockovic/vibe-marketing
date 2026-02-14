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
          <div class="flex gap-3 text-xs text-muted-foreground mt-1">
            <span class="text-green-600">{{ taskStats.completed }} done</span>
            <span class="text-blue-600">{{ taskStats.inProgress }} active</span>
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
          empty-message="No tasks created for this batch yet. Activate the batch to generate tasks."
        >
          <template #cell-title="{ row }">
            <button
              class="text-left font-medium text-primary hover:text-primary/80"
              @click="selectedTaskId = row._id"
            >
              {{ row.title }}
            </button>
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

      <!-- Resources -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-foreground mb-3">Resources</h2>
        <ResourceStatsCards :content-batch-id="batchId" />
        <div class="mt-3">
          <ResourceTable :content-batch-id="batchId" @select="(r) => $router.push(`/projects/${$route.params.slug}/resources/${r._id}`)" />
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
        :message="`This will generate ${batch.batchSize} tasks and start the engagement pipeline. Continue?`"
        confirm-label="Activate"
        confirm-class="bg-green-600 hover:bg-green-700"
        @confirm="activate"
      />
      <VConfirmDialog
        v-model="showConfirmPause"
        title="Pause Batch"
        message="Active tasks will finish but no new tasks will be started."
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
