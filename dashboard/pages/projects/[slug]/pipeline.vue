<script setup lang="ts">
import { api } from '../../../../convex/_generated/api'
import { Cpu } from 'lucide-vue-next'

const { project } = useCurrentProject()
const projectId = computed(() => project.value?._id)

const { data: tasks, loading } = useConvexQuery(
  api.tasks.listByProject,
  computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
)

const columns = [
  { key: 'backlog', label: 'Backlog', color: 'bg-muted/50', headerColor: 'bg-muted-foreground/40', textColor: 'text-muted-foreground' },
  { key: 'researched', label: 'Researched', color: 'bg-blue-50', headerColor: 'bg-blue-500', textColor: 'text-blue-700' },
  { key: 'briefed', label: 'Briefed', color: 'bg-indigo-50', headerColor: 'bg-indigo-500', textColor: 'text-indigo-700' },
  { key: 'drafted', label: 'Drafted', color: 'bg-purple-50', headerColor: 'bg-purple-500', textColor: 'text-purple-700' },
  { key: 'reviewed', label: 'Reviewed', color: 'bg-amber-50', headerColor: 'bg-amber-500', textColor: 'text-amber-700' },
  { key: 'humanized', label: 'Humanized', color: 'bg-teal-50', headerColor: 'bg-teal-500', textColor: 'text-teal-700' },
  { key: 'completed', label: 'Completed', color: 'bg-green-50', headerColor: 'bg-green-500', textColor: 'text-green-700' },
]

const tasksByStatus = computed(() => {
  const map: Record<string, any[]> = {}
  for (const col of columns) map[col.key] = []
  if (!tasks.value) return map

  for (const task of tasks.value) {
    if (map[task.status]) {
      map[task.status].push(task)
    }
    // revision_needed, blocked, cancelled get their own row below the board
  }
  return map
})

const specialTasks = computed(() => {
  if (!tasks.value) return []
  return tasks.value.filter((t: any) =>
    ['revision_needed', 'blocked', 'cancelled'].includes(t.status),
  )
})

const totalTaskCount = computed(() => tasks.value?.length || 0)

const selectedTaskId = ref<string | null>(null)
const showTaskDetail = ref(false)

function openTask(taskId: string) {
  selectedTaskId.value = taskId
  showTaskDetail.value = true
}

function closeTaskDetail(val: boolean) {
  if (!val) {
    showTaskDetail.value = false
    selectedTaskId.value = null
  }
}

function priorityColor(priority: string) {
  switch (priority) {
    case 'urgent': return 'border-l-red-500'
    case 'high': return 'border-l-orange-500'
    case 'medium': return 'border-l-blue-400'
    default: return 'border-l-border'
  }
}
</script>

<template>
  <div>
    <VPageHeader title="Pipeline Board" :description="`${totalTaskCount} tasks across all stages`" />

    <div v-if="loading" class="text-muted-foreground">Loading pipeline...</div>

    <VEmptyState
      v-else-if="totalTaskCount === 0"
      title="No tasks yet"
      description="Create a campaign and activate it to start generating tasks."
    />

    <template v-else>
      <!-- Kanban board -->
      <div class="overflow-x-auto pb-4 -mx-6 px-6">
        <div class="flex gap-4 min-w-max">
          <div
            v-for="col in columns"
            :key="col.key"
            class="w-72 flex-shrink-0 rounded-lg overflow-hidden"
            :class="col.color"
          >
            <!-- Column header -->
            <div class="px-3 py-2.5 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full" :class="col.headerColor" />
                <span class="text-sm font-semibold" :class="col.textColor">{{ col.label }}</span>
              </div>
              <span
                class="text-xs font-medium px-2 py-0.5 rounded-full"
                :class="col.textColor"
                :style="{ opacity: 0.7 }"
              >
                {{ tasksByStatus[col.key]?.length || 0 }}
              </span>
            </div>

            <!-- Task cards -->
            <div class="px-2 pb-2 space-y-2 min-h-[200px]">
              <button
                v-for="task in tasksByStatus[col.key]"
                :key="task._id"
                class="w-full text-left rounded-lg border bg-card shadow-sm hover:shadow-md transition-shadow p-3 border-l-3 cursor-pointer"
                :class="priorityColor(task.priority)"
                @click="openTask(task._id)"
              >
                <div class="flex items-start justify-between gap-2 mb-1.5">
                  <h4 class="text-sm font-medium text-foreground line-clamp-2 flex-1">
                    {{ task.title }}
                  </h4>
                </div>

                <div v-if="task.contentType" class="mb-2">
                  <span class="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded">
                    {{ task.contentType }}
                  </span>
                </div>

                <div class="flex items-center justify-between">
                  <div v-if="task.lockedBy" class="flex items-center gap-1">
                    <svg class="w-3 h-3 text-muted-foreground/70" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6.75A2.25 2.25 0 0 0 4.5 6.75v10.5a2.25 2.25 0 0 0 2.25 2.25Z" />
                    </svg>
                    <span class="text-xs text-muted-foreground">{{ task.lockedBy }}</span>
                  </div>
                  <div v-else />

                  <div class="flex items-center gap-2">
                    <span
                      v-if="task.qualityScore"
                      class="text-xs font-medium"
                      :class="task.qualityScore >= 7 ? 'text-green-600' : task.qualityScore >= 5 ? 'text-amber-600' : 'text-red-600'"
                    >
                      {{ task.qualityScore }}/10
                    </span>
                    <span
                      class="text-xs font-medium px-1.5 py-0.5 rounded"
                      :class="{
                        'bg-red-100 text-red-700': task.priority === 'urgent',
                        'bg-orange-100 text-orange-600': task.priority === 'high',
                        'bg-blue-50 text-blue-600': task.priority === 'medium',
                        'bg-muted/50 text-muted-foreground': task.priority === 'low',
                      }"
                    >
                      {{ task.priority }}
                    </span>
                  </div>
                </div>
              </button>

              <!-- Empty column state -->
              <div
                v-if="!tasksByStatus[col.key]?.length"
                class="flex items-center justify-center h-24 text-xs text-muted-foreground/70"
              >
                No tasks
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Special statuses (revision, blocked, cancelled) -->
      <div v-if="specialTasks.length" class="mt-6">
        <h3 class="text-sm font-semibold text-muted-foreground mb-3">
          Needs Attention ({{ specialTasks.length }})
        </h3>
        <div class="rounded-lg border bg-card shadow-sm divide-y divide-border">
          <button
            v-for="task in specialTasks"
            :key="task._id"
            class="w-full text-left px-4 py-3 flex items-center justify-between hover:bg-muted/50 transition-colors cursor-pointer"
            @click="openTask(task._id)"
          >
            <div class="flex items-center gap-3">
              <VStatusBadge :status="task.status" size="sm" />
              <span class="text-sm font-medium">{{ task.title }}</span>
            </div>
            <div class="flex items-center gap-3 text-xs text-muted-foreground">
              <span v-if="task.rejectionNotes" class="max-w-xs truncate">
                {{ task.rejectionNotes }}
              </span>
              <span v-if="task.lockedBy">{{ task.lockedBy }}</span>
            </div>
          </button>
        </div>
      </div>
    </template>

    <!-- Task detail modal -->
    <TaskDetailModal
      :model-value="showTaskDetail"
      :task-id="selectedTaskId"
      @update:model-value="closeTaskDetail"
    />
  </div>
</template>
