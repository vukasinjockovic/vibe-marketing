<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  modelValue: boolean
  projectId: string
  productId: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: []
}>()

const toast = useToast()

const { mutate: createDocument } = useConvexMutation(api.documents.create)
const { mutate: createTask } = useConvexMutation(api.tasks.create)
const { data: pipeline } = useConvexQuery(
  api.pipelines.getBySlug,
  { slug: 'document-import' },
)

const selectedFile = ref<File | null>(null)
const fileContent = ref('')
const autoEnrich = ref(true)
const submitting = ref(false)
const isDragOver = ref(false)

const acceptedTypes = '.md,.txt,.docx,.pdf'

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files?.length) {
    handleFile(target.files[0])
  }
}

function handleFile(file: File) {
  selectedFile.value = file
  // Read text content for .md and .txt files
  if (file.name.endsWith('.md') || file.name.endsWith('.txt')) {
    const reader = new FileReader()
    reader.onload = () => {
      fileContent.value = reader.result as string
    }
    reader.readAsText(file)
  } else {
    fileContent.value = `[Uploaded file: ${file.name}]`
  }
}

function onDrop(event: DragEvent) {
  isDragOver.value = false
  const files = event.dataTransfer?.files
  if (files?.length) {
    handleFile(files[0])
  }
}

function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function close() {
  emit('update:modelValue', false)
}

async function submit() {
  if (!selectedFile.value) {
    toast.error('Please select a file')
    return
  }
  submitting.value = true
  try {
    // 1. Create document in Convex
    const docId = await createDocument({
      title: selectedFile.value.name,
      content: fileContent.value,
      type: 'audience_doc' as any,
      productId: props.productId as any,
      projectId: props.projectId as any,
      createdBy: 'dashboard',
    })

    // 2. Build pipeline steps from the pipeline template
    const pipelineSteps = pipeline.value?.mainSteps?.map((s: any) => ({
      step: s.order,
      status: s.order === 1 ? 'in_progress' : 'pending',
      agent: s.agent,
      model: s.model,
      description: s.description || s.label,
      outputDir: s.outputDir,
    })) || [
      { step: 1, status: 'in_progress', agent: 'vibe-audience-researcher', description: 'Parse document and extract focus groups' },
    ]

    // 3. Create a task
    await createTask({
      projectId: props.projectId as any,
      title: `Import audiences from ${selectedFile.value.name}`,
      description: `Parse audience document and extract focus groups. Auto-enrich: ${autoEnrich.value}`,
      pipeline: pipelineSteps,
      priority: 'medium',
      createdBy: 'dashboard',
      contentType: 'audience_import',
      metadata: {
        productId: props.productId,
        documentId: docId,
        autoEnrich: autoEnrich.value,
        uploadedFilePath: selectedFile.value.name,
      },
    })

    toast.success('Audience import task created!')
    emit('created')
    close()
  } catch (e: any) {
    toast.error(e.message || 'Failed to create import task')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <VModal :model-value="modelValue" title="Import Audience Document" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div class="space-y-4">
      <!-- Drag & Drop Zone -->
      <div
        data-testid="drop-zone"
        class="border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer"
        :class="isDragOver ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'"
        @dragover.prevent="onDragOver"
        @dragleave="onDragLeave"
        @drop.prevent="onDrop"
        @click="($refs.fileInput as HTMLInputElement)?.click()"
      >
        <span class="i-heroicons-document-arrow-up text-3xl text-gray-400 mb-2 block" />
        <p v-if="selectedFile" class="text-sm text-gray-900 font-medium">
          {{ selectedFile.name }}
          <span class="text-gray-500">({{ (selectedFile.size / 1024).toFixed(1) }}KB)</span>
        </p>
        <template v-else>
          <p class="text-sm text-gray-600 mb-1">Drop a file here or click to browse</p>
          <p class="text-xs text-gray-400">Accepts .md, .txt, .docx, .pdf</p>
        </template>
      </div>

      <input
        ref="fileInput"
        type="file"
        :accept="acceptedTypes"
        class="hidden"
        @change="onFileChange"
      />

      <!-- Auto-enrich checkbox -->
      <label class="flex items-center gap-2 cursor-pointer">
        <input
          v-model="autoEnrich"
          type="checkbox"
          class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        <span class="text-sm text-gray-700">Auto-enrich after parsing</span>
      </label>
    </div>

    <template #footer>
      <button
        class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        @click="close"
      >
        Cancel
      </button>
      <button
        class="px-4 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors disabled:opacity-50"
        :disabled="!selectedFile || submitting"
        @click="submit"
      >
        {{ submitting ? 'Importing...' : 'Import Document' }}
      </button>
    </template>
  </VModal>
</template>
