<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  projectId: string
  batch?: any
}>()

const emit = defineEmits<{
  saved: []
}>()

const isEdit = computed(() => !!props.batch)
const { mutate: createBatch } = useConvexMutation(api.contentBatches.create)
const { mutate: updateBatch } = useConvexMutation(api.contentBatches.update)
const toast = useToast()

// Load channels and pipelines for selectors
const { data: channels } = useConvexQuery(
  api.channels.list,
  computed(() => ({ projectId: props.projectId as any })),
)

const { data: engagementPipelines } = useConvexQuery(
  api.pipelines.listByCategory,
  { category: 'engagement' },
)

const { data: focusGroups } = useConvexQuery(
  api.focusGroups.listByProject,
  computed(() => ({ projectId: props.projectId as any })),
)

const form = reactive({
  channelId: '',
  name: '',
  slug: '',
  description: '',
  batchSize: 12,
  pipelineId: '',
  targetFocusGroupIds: [] as string[],
  contentThemes: '',
  trendSources: '',
  notes: '',
  mediaConfig: {
    imagePrompt: true,
    videoScript: true,
  },
})

// Pre-populate form in edit mode
if (props.batch) {
  form.channelId = props.batch.channelId || ''
  form.name = props.batch.name || ''
  form.slug = props.batch.slug || ''
  form.description = props.batch.description || ''
  form.batchSize = props.batch.batchSize || 12
  form.pipelineId = props.batch.pipelineId || ''
  form.targetFocusGroupIds = props.batch.targetFocusGroupIds ? [...props.batch.targetFocusGroupIds] : []
  form.contentThemes = props.batch.contentThemes?.join(', ') || ''
  form.trendSources = props.batch.trendSources?.join(', ') || ''
  form.notes = props.batch.notes || ''
  form.mediaConfig = props.batch.mediaConfig ? { ...props.batch.mediaConfig } : { imagePrompt: true, videoScript: true }
}

// Auto-generate slug from name (only in create mode)
watch(() => form.name, (name) => {
  if (!isEdit.value) {
    form.slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
  }
})

// Auto-select first channel and pipeline
watch(channels, (chs) => {
  if (chs?.length && !form.channelId) form.channelId = chs[0]._id
}, { immediate: true })

watch(engagementPipelines, (eps) => {
  if (eps?.length && !form.pipelineId) form.pipelineId = eps[0]._id
}, { immediate: true })

const batchSizeOptions = [12, 24, 36, 48]
const submitting = ref(false)

function toggleFocusGroup(id: string) {
  const idx = form.targetFocusGroupIds.indexOf(id)
  if (idx >= 0) form.targetFocusGroupIds.splice(idx, 1)
  else form.targetFocusGroupIds.push(id)
}

async function submit() {
  if (!form.name || !form.channelId || !form.pipelineId) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateBatch({
        id: props.batch._id,
        name: form.name,
        description: form.description || `Content batch: ${form.name}`,
        batchSize: form.batchSize,
        pipelineId: form.pipelineId as any,
        targetFocusGroupIds: form.targetFocusGroupIds as any[],
        contentThemes: form.contentThemes ? form.contentThemes.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        trendSources: form.trendSources ? form.trendSources.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        notes: form.notes || undefined,
      })
      toast.success(`Batch "${form.name}" updated!`)
    } else {
      const pipeline = engagementPipelines.value?.find((p: any) => p._id === form.pipelineId)
      await createBatch({
        projectId: props.projectId as any,
        channelId: form.channelId as any,
        name: form.name,
        slug: form.slug,
        description: form.description || `Content batch: ${form.name}`,
        batchSize: form.batchSize,
        pipelineId: form.pipelineId as any,
        pipelineSnapshot: pipeline || undefined,
        targetFocusGroupIds: form.targetFocusGroupIds as any[],
        contentThemes: form.contentThemes ? form.contentThemes.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        trendSources: form.trendSources ? form.trendSources.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        mediaConfig: form.mediaConfig,
        notes: form.notes || undefined,
      })
      toast.success(`Batch "${form.name}" created!`)
    }
    emit('saved')
  } catch (e: any) {
    toast.error(e.message || (isEdit.value ? 'Failed to update batch' : 'Failed to create batch'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <!-- Channel selector -->
    <VFormField label="Channel" required>
      <select
        v-model="form.channelId"
        :disabled="isEdit"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <option value="" disabled>Select a channel...</option>
        <option v-for="ch in channels" :key="ch._id" :value="ch._id">
          {{ ch.name }} ({{ ch.platform }})
        </option>
      </select>
      <p v-if="!channels?.length" class="text-xs text-muted-foreground mt-1">
        Create a channel first from the Engagement tab.
      </p>
    </VFormField>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <VFormField label="Batch Name" required>
        <input
          v-model="form.name"
          type="text"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          placeholder="Phase 1 - Week 1"
        />
      </VFormField>

      <VFormField label="Slug">
        <input
          v-model="form.slug"
          type="text"
          :disabled="isEdit"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-muted-foreground disabled:opacity-60 disabled:cursor-not-allowed"
        />
      </VFormField>
    </div>

    <VFormField label="Description">
      <textarea
        v-model="form.description"
        rows="2"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        placeholder="What this batch covers..."
      />
    </VFormField>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Batch size -->
      <VFormField label="Batch Size">
        <div class="flex gap-2">
          <button
            v-for="size in batchSizeOptions"
            :key="size"
            type="button"
            class="px-4 py-2 text-sm rounded-md border transition-colors"
            :class="form.batchSize === size
              ? 'bg-primary text-primary-foreground border-primary'
              : 'border-border text-muted-foreground hover:bg-muted'"
            @click="form.batchSize = size"
          >
            {{ size }}
          </button>
        </div>
      </VFormField>

      <!-- Pipeline -->
      <VFormField label="Pipeline" required>
        <select
          v-model="form.pipelineId"
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="" disabled>Select pipeline...</option>
          <option v-for="p in engagementPipelines" :key="p._id" :value="p._id">
            {{ p.name }}
          </option>
        </select>
      </VFormField>
    </div>

    <!-- Media Toggles -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <label class="flex items-center gap-3 cursor-pointer p-3 rounded-md border border-border hover:bg-muted/50 transition-colors">
        <input
          v-model="form.mediaConfig.imagePrompt"
          type="checkbox"
          class="h-4 w-4 rounded border-input text-primary focus:ring-primary"
        />
        <div>
          <span class="text-sm font-medium">Generate Image Prompts</span>
          <p class="text-xs text-muted-foreground">Creates visual prompts for each post</p>
        </div>
      </label>
      <label class="flex items-center gap-3 cursor-pointer p-3 rounded-md border border-border hover:bg-muted/50 transition-colors">
        <input
          v-model="form.mediaConfig.videoScript"
          type="checkbox"
          class="h-4 w-4 rounded border-input text-primary focus:ring-primary"
        />
        <div>
          <span class="text-sm font-medium">Generate Reels Scripts</span>
          <p class="text-xs text-muted-foreground">Creates short-form video scripts for each post</p>
        </div>
      </label>
    </div>

    <!-- Focus Groups -->
    <VFormField label="Target Focus Groups">
      <div v-if="focusGroups?.length" class="flex flex-wrap gap-2">
        <button
          v-for="fg in focusGroups"
          :key="fg._id"
          type="button"
          class="px-3 py-1.5 text-xs rounded-full border transition-colors"
          :class="form.targetFocusGroupIds.includes(fg._id)
            ? 'bg-indigo-100 text-indigo-700 border-indigo-300'
            : 'border-border text-muted-foreground hover:bg-muted'"
          @click="toggleFocusGroup(fg._id)"
        >
          {{ fg.name }}
        </button>
      </div>
      <p v-else class="text-xs text-muted-foreground">No focus groups in this project.</p>
    </VFormField>

    <!-- Content Themes -->
    <VFormField label="Content Themes" hint="Comma-separated topic tags">
      <input
        v-model="form.contentThemes"
        type="text"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        placeholder="nostalgia, wedding moments, family memories"
      />
    </VFormField>

    <!-- Notes -->
    <VFormField label="Notes">
      <textarea
        v-model="form.notes"
        rows="2"
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        placeholder="Any special instructions for this batch..."
      />
    </VFormField>

    <div class="flex justify-end gap-2 pt-2">
      <button
        type="submit"
        :disabled="submitting || !form.name || !form.channelId || !form.pipelineId"
        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {{ submitting ? (isEdit ? 'Saving...' : 'Creating...') : (isEdit ? 'Save Changes' : 'Create Batch') }}
      </button>
    </div>
  </form>
</template>
