<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Check, FileText } from 'lucide-vue-next'

const props = defineProps<{
  modelValue: boolean
  taskId: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const { data: task } = useConvexQuery(
  api.tasks.get,
  computed(() => props.taskId ? { id: props.taskId as any } : 'skip'),
)

const { data: pipelineStatus } = useConvexQuery(
  api.pipeline.getTaskPipelineStatus,
  computed(() => props.taskId ? { taskId: props.taskId as any } : 'skip'),
)

const { data: messages } = useConvexQuery(
  api.messages.listByTask,
  computed(() => props.taskId ? { taskId: props.taskId as any } : 'skip'),
)

const { data: documents } = useConvexQuery(
  api.documents.listByTask,
  computed(() => props.taskId ? { taskId: props.taskId as any } : 'skip'),
)

const activeTab = ref<'overview' | 'messages' | 'documents'>('overview')

function stepStatusClass(status: string) {
  switch (status) {
    case 'completed': return 'bg-green-500 text-white'
    case 'in_progress': return 'bg-blue-500 text-white animate-pulse'
    case 'pending': return 'bg-muted text-muted-foreground'
    default: return 'bg-muted text-muted-foreground'
  }
}

function stepLineClass(status: string) {
  switch (status) {
    case 'completed': return 'bg-green-500'
    default: return 'bg-muted'
  }
}

function formatTimestamp(ts: number) {
  return new Date(ts).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>

<template>
  <VModal
    :model-value="modelValue"
    :title="task?.title || 'Task Detail'"
    size="xl"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div v-if="!task" class="text-muted-foreground py-8 text-center">
      Loading task...
    </div>

    <div v-else class="space-y-6">
      <!-- Pipeline progress bar -->
      <div v-if="pipelineStatus?.pipeline?.length" class="bg-muted/50 rounded-lg p-4">
        <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">Pipeline Progress</h3>
        <div class="flex items-center">
          <div
            v-for="(pStep, idx) in pipelineStatus.pipeline"
            :key="idx"
            class="flex items-center"
            :class="idx < pipelineStatus.pipeline.length - 1 ? 'flex-1' : ''"
          >
            <!-- Step circle -->
            <div class="flex flex-col items-center">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
                :class="stepStatusClass(pStep.status)"
              >
                <Check v-if="pStep.status === 'completed'" class="w-4 h-4" />
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <span class="text-xs text-muted-foreground mt-1 max-w-16 text-center truncate">
                {{ pStep.description || `Step ${idx + 1}` }}
              </span>
              <span v-if="pStep.agent" class="text-xs text-muted-foreground/60 truncate max-w-16">
                {{ pStep.agent }}
              </span>
            </div>

            <!-- Connecting line -->
            <div
              v-if="idx < pipelineStatus.pipeline.length - 1"
              class="flex-1 h-0.5 mx-1"
              :class="stepLineClass(pStep.status)"
            />
          </div>
        </div>
      </div>

      <!-- Task info -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-3">
          <div>
            <span class="text-xs text-muted-foreground block">Status</span>
            <VStatusBadge :status="task.status" />
          </div>
          <div>
            <span class="text-xs text-muted-foreground block">Priority</span>
            <span
              class="text-sm font-medium px-2 py-0.5 rounded-full"
              :class="{
                'bg-red-100 text-red-700': task.priority === 'urgent',
                'bg-orange-100 text-orange-700': task.priority === 'high',
                'bg-blue-100 text-blue-700': task.priority === 'medium',
                'bg-muted text-muted-foreground': task.priority === 'low',
              }"
            >
              {{ task.priority }}
            </span>
          </div>
          <div v-if="task.contentType">
            <span class="text-xs text-muted-foreground block">Content Type</span>
            <span class="text-sm text-muted-foreground">{{ task.contentType }}</span>
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <span class="text-xs text-muted-foreground block">Assigned Agent</span>
            <span v-if="task.lockedBy" class="text-sm font-medium text-muted-foreground">{{ task.lockedBy }}</span>
            <span v-else class="text-sm text-muted-foreground/60">Unassigned</span>
          </div>
          <div v-if="pipelineStatus?.qualityScore">
            <span class="text-xs text-muted-foreground block">Quality Score</span>
            <span
              class="text-lg font-bold"
              :class="pipelineStatus.qualityScore >= 7 ? 'text-green-600' : pipelineStatus.qualityScore >= 5 ? 'text-amber-600' : 'text-red-600'"
            >
              {{ pipelineStatus.qualityScore }}/10
            </span>
          </div>
          <div v-if="pipelineStatus?.revisionCount">
            <span class="text-xs text-muted-foreground block">Revisions</span>
            <span class="text-sm text-muted-foreground">{{ pipelineStatus.revisionCount }}</span>
          </div>
        </div>
      </div>

      <!-- Rejection notes -->
      <div
        v-if="pipelineStatus?.rejectionNotes"
        class="bg-red-50 border border-red-200 rounded-lg p-3"
      >
        <h4 class="text-xs font-medium text-red-800 uppercase tracking-wide mb-1">Revision Notes</h4>
        <p class="text-sm text-red-700">{{ pipelineStatus.rejectionNotes }}</p>
      </div>

      <!-- Tabs: Messages & Documents -->
      <div class="border-t border-border pt-4">
        <div class="flex gap-4 mb-4">
          <button
            v-for="tab in (['overview', 'messages', 'documents'] as const)"
            :key="tab"
            class="text-sm font-medium pb-2 border-b-2 transition-colors capitalize"
            :class="activeTab === tab
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'"
            @click="activeTab = tab"
          >
            {{ tab }}
            <span v-if="tab === 'messages' && messages?.length" class="ml-1 text-xs">
              ({{ messages.length }})
            </span>
            <span v-if="tab === 'documents' && documents?.length" class="ml-1 text-xs">
              ({{ documents.length }})
            </span>
          </button>
        </div>

        <!-- Overview tab -->
        <div v-if="activeTab === 'overview'">
          <div v-if="task.description" class="text-sm text-muted-foreground whitespace-pre-wrap">
            {{ task.description }}
          </div>
          <p v-else class="text-sm text-muted-foreground/60">No description.</p>
        </div>

        <!-- Messages tab -->
        <div v-if="activeTab === 'messages'">
          <div v-if="messages?.length" class="space-y-3 max-h-64 overflow-y-auto">
            <div
              v-for="msg in messages"
              :key="msg._id"
              class="bg-muted/50 rounded-lg p-3"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-medium text-primary">{{ msg.fromAgent }}</span>
                <span class="text-xs text-muted-foreground/60">{{ formatTimestamp(msg._creationTime) }}</span>
              </div>
              <p class="text-sm text-muted-foreground whitespace-pre-wrap">{{ msg.content }}</p>
              <div v-if="msg.mentions?.length" class="flex gap-1 mt-1">
                <span
                  v-for="m in msg.mentions"
                  :key="m"
                  class="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded"
                >
                  @{{ m }}
                </span>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground/60">No messages yet.</p>
        </div>

        <!-- Documents tab -->
        <div v-if="activeTab === 'documents'">
          <div v-if="documents?.length" class="space-y-2">
            <div
              v-for="doc in documents"
              :key="doc._id"
              class="flex items-center gap-3 p-3 bg-muted/50 rounded-lg"
            >
              <FileText class="w-5 h-5 text-muted-foreground/60" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-muted-foreground truncate">{{ doc.title || doc.path }}</p>
                <p class="text-xs text-muted-foreground">{{ doc.type || 'Document' }}</p>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground/60">No documents attached.</p>
        </div>
      </div>
    </div>
  </VModal>
</template>
