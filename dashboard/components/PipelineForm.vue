<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Plus, Trash2, GitBranch, ChevronDown, ChevronUp } from 'lucide-vue-next'

const props = defineProps<{
  pipeline?: any // existing pipeline for edit mode
}>()

const emit = defineEmits<{
  saved: [slug: string]
  cancelled: []
}>()

const toast = useToast()
const { mutate: createPipeline } = useConvexMutation(api.pipelines.create)
const { mutate: updatePipeline } = useConvexMutation(api.pipelines.update)
const saving = ref(false)

const isEdit = computed(() => !!props.pipeline)

const models = ['haiku', 'sonnet', 'opus']

const outputDirs = [
  { value: '', label: 'None' },
  { value: 'research', label: 'research/ (→ researched)' },
  { value: 'briefs', label: 'briefs/ (→ briefed)' },
  { value: 'drafts', label: 'drafts/ (→ drafted)' },
  { value: 'reviewed', label: 'reviewed/ (→ reviewed)' },
  { value: 'final', label: 'final/ (→ humanized)' },
]

// Form state
const form = reactive({
  name: '',
  slug: '',
  description: '',
  mainSteps: [] as Array<{
    order: number
    agent: string
    model: string
    label: string
    description: string
    outputDir: string
  }>,
  parallelBranches: [] as Array<{
    triggerAfterStep: number
    agent: string
    model: string
    label: string
    description: string
  }>,
  convergenceStep: null as number | null,
  onComplete: {
    telegram: true,
    summary: true,
    generateManifest: false,
  },
})

// Initialize from existing pipeline
if (props.pipeline) {
  form.name = props.pipeline.name
  form.slug = props.pipeline.slug
  form.description = props.pipeline.description || ''
  form.mainSteps = (props.pipeline.mainSteps || []).map((s: any) => ({
    order: s.order,
    agent: s.agent || '',
    model: s.model || '',
    label: s.label || '',
    description: s.description || '',
    outputDir: s.outputDir || '',
  }))
  form.parallelBranches = (props.pipeline.parallelBranches || []).map((b: any) => ({
    triggerAfterStep: b.triggerAfterStep,
    agent: b.agent || '',
    model: b.model || '',
    label: b.label || '',
    description: b.description || '',
  }))
  form.convergenceStep = props.pipeline.convergenceStep || null
  if (props.pipeline.onComplete) {
    form.onComplete = { ...props.pipeline.onComplete }
  }
}

// Auto-slug from name
const autoSlug = ref(!isEdit.value)
watch(() => form.name, (name) => {
  if (autoSlug.value) {
    form.slug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
  }
})

// Step management
function addStep() {
  const order = form.mainSteps.length + 1
  form.mainSteps.push({
    order,
    agent: '',
    model: 'sonnet',
    label: '',
    description: '',
    outputDir: '',
  })
}

function removeStep(index: number) {
  form.mainSteps.splice(index, 1)
  // Reorder
  form.mainSteps.forEach((s, i) => { s.order = i + 1 })
}

function moveStep(index: number, direction: -1 | 1) {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= form.mainSteps.length) return
  const temp = form.mainSteps[index]
  form.mainSteps[index] = form.mainSteps[newIndex]
  form.mainSteps[newIndex] = temp
  // Reorder
  form.mainSteps.forEach((s, i) => { s.order = i + 1 })
}

// Branch management
function addBranch(afterStep: number) {
  form.parallelBranches.push({
    triggerAfterStep: afterStep,
    agent: '',
    model: 'sonnet',
    label: '',
    description: '',
  })
}

function removeBranch(index: number) {
  form.parallelBranches.splice(index, 1)
}

function branchesForStep(stepOrder: number) {
  return form.parallelBranches
    .map((b, i) => ({ ...b, _index: i }))
    .filter(b => b.triggerAfterStep === stepOrder)
}

// Validation
const errors = reactive<Record<string, string>>({})

function validate(): boolean {
  Object.keys(errors).forEach(k => delete errors[k])

  if (!form.name.trim()) errors.name = 'Name is required'
  if (!form.slug.trim()) errors.slug = 'Slug is required'
  if (!/^[a-z0-9-]+$/.test(form.slug)) errors.slug = 'Slug must be lowercase letters, numbers, and hyphens'
  if (!form.description.trim()) errors.description = 'Description is required'
  if (form.mainSteps.length === 0) errors.steps = 'At least one step is required'

  form.mainSteps.forEach((s, i) => {
    if (!s.label.trim()) errors[`step_${i}_label`] = 'Label required'
    if (!s.agent) errors[`step_${i}_agent`] = 'Agent required'
  })

  return Object.keys(errors).length === 0
}

async function save() {
  if (!validate()) return

  saving.value = true
  try {
    const steps = form.mainSteps.map(s => ({
      order: s.order,
      label: s.label,
      ...(s.agent ? { agent: s.agent } : {}),
      ...(s.model ? { model: s.model } : {}),
      ...(s.description ? { description: s.description } : {}),
      ...(s.outputDir ? { outputDir: s.outputDir } : {}),
    }))

    const branches = form.parallelBranches
      .filter(b => b.label && b.agent)
      .map(b => ({
        triggerAfterStep: b.triggerAfterStep,
        agent: b.agent,
        label: b.label,
        ...(b.model ? { model: b.model } : {}),
        ...(b.description ? { description: b.description } : {}),
      }))

    if (isEdit.value) {
      await updatePipeline({
        id: props.pipeline._id,
        name: form.name,
        slug: form.slug,
        description: form.description,
        mainSteps: steps,
        ...(branches.length ? { parallelBranches: branches } : {}),
        ...(form.convergenceStep ? { convergenceStep: form.convergenceStep } : {}),
        onComplete: form.onComplete,
      })
      toast.success('Pipeline updated!')
    } else {
      const result = await createPipeline({
        name: form.name,
        slug: form.slug,
        description: form.description,
        type: 'custom',
        mainSteps: steps,
        ...(branches.length ? { parallelBranches: branches } : {}),
        ...(form.convergenceStep ? { convergenceStep: form.convergenceStep } : {}),
        onComplete: form.onComplete,
      })
      if ((result as any)?.error) {
        toast.error((result as any).error)
        saving.value = false
        return
      }
      toast.success('Pipeline created!')
    }
    emit('saved', form.slug)
  } catch (e: any) {
    toast.error(e.message || 'Failed to save pipeline')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Basic Info -->
    <div>
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Basic Info</h3>
      <div class="space-y-4">
        <VFormField label="Name" :error="errors.name" required>
          <input
            v-model="form.name"
            type="text"
            placeholder="e.g. Blog Article Pipeline"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>

        <VFormField label="Slug" :error="errors.slug" required>
          <input
            v-model="form.slug"
            type="text"
            placeholder="e.g. blog-article-pipeline"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            @input="autoSlug = false"
          />
        </VFormField>

        <VFormField label="Description" :error="errors.description" required>
          <textarea
            v-model="form.description"
            rows="2"
            placeholder="What does this pipeline produce?"
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          />
        </VFormField>
      </div>
    </div>

    <!-- Pipeline Steps -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide">Pipeline Steps</h3>
        <button
          type="button"
          class="flex items-center gap-1 text-xs text-primary hover:text-primary/80 font-medium"
          @click="addStep"
        >
          <Plus :size="14" />
          Add Step
        </button>
      </div>

      <p v-if="errors.steps" class="text-sm text-destructive mb-3">{{ errors.steps }}</p>

      <div v-if="form.mainSteps.length === 0" class="rounded-lg border border-dashed bg-muted/30 p-8 text-center">
        <p class="text-sm text-muted-foreground mb-3">No steps yet. Add steps to define your pipeline.</p>
        <button
          type="button"
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
          @click="addStep"
        >
          Add First Step
        </button>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="(step, idx) in form.mainSteps"
          :key="idx"
          class="rounded-lg border bg-card p-4"
        >
          <div class="flex items-start gap-3">
            <!-- Order + move -->
            <div class="flex flex-col items-center gap-1 pt-1">
              <button
                type="button"
                class="text-muted-foreground hover:text-foreground disabled:opacity-30"
                :disabled="idx === 0"
                @click="moveStep(idx, -1)"
              >
                <ChevronUp :size="14" />
              </button>
              <span class="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">
                {{ step.order }}
              </span>
              <button
                type="button"
                class="text-muted-foreground hover:text-foreground disabled:opacity-30"
                :disabled="idx === form.mainSteps.length - 1"
                @click="moveStep(idx, 1)"
              >
                <ChevronDown :size="14" />
              </button>
            </div>

            <!-- Step fields -->
            <div class="flex-1 space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <VFormField label="Label" :error="errors[`step_${idx}_label`]" required>
                  <input
                    v-model="step.label"
                    type="text"
                    placeholder="e.g. Research"
                    class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  />
                </VFormField>

                <VFormField label="Agent" :error="errors[`step_${idx}_agent`]" required>
                  <AgentSelect v-model="step.agent" placeholder="Select agent..." />
                </VFormField>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <VFormField label="Model">
                  <select
                    v-model="step.model"
                    class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option value="">Default</option>
                    <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
                  </select>
                </VFormField>

                <VFormField label="Output Directory">
                  <select
                    v-model="step.outputDir"
                    class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  >
                    <option v-for="o in outputDirs" :key="o.value" :value="o.value">{{ o.label }}</option>
                  </select>
                </VFormField>
              </div>

              <VFormField label="Description">
                <input
                  v-model="step.description"
                  type="text"
                  placeholder="What this step does..."
                  class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                />
              </VFormField>
            </div>

            <!-- Remove button -->
            <button
              type="button"
              class="text-muted-foreground hover:text-destructive transition-colors mt-1"
              @click="removeStep(idx)"
            >
              <Trash2 :size="16" />
            </button>
          </div>

          <!-- Parallel branches for this step -->
          <div v-if="branchesForStep(step.order).length > 0" class="mt-3 ml-10 pl-4 border-l-2 border-dashed border-purple-300">
            <p class="text-xs text-purple-600 font-medium mb-2">Parallel branches after this step</p>
            <div
              v-for="branch in branchesForStep(step.order)"
              :key="branch._index"
              class="bg-purple-50 rounded-md p-3 mb-2"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1 space-y-2">
                  <div class="grid grid-cols-3 gap-2">
                    <input
                      v-model="form.parallelBranches[branch._index].label"
                      type="text"
                      placeholder="Branch label"
                      class="w-full border border-purple-200 rounded-md px-2 py-1.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    />
                    <AgentSelect v-model="form.parallelBranches[branch._index].agent" placeholder="Select agent..." />
                    <select
                      v-model="form.parallelBranches[branch._index].model"
                      class="w-full border border-purple-200 rounded-md px-2 py-1.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-purple-400"
                    >
                      <option value="">Default</option>
                      <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
                    </select>
                  </div>
                </div>
                <button
                  type="button"
                  class="text-purple-400 hover:text-destructive transition-colors"
                  @click="removeBranch(branch._index)"
                >
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
          </div>

          <!-- Add branch button -->
          <div class="mt-2 ml-10">
            <button
              type="button"
              class="flex items-center gap-1 text-xs text-purple-600 hover:text-purple-800 font-medium"
              @click="addBranch(step.order)"
            >
              <GitBranch :size="12" />
              Add parallel branch
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Convergence Step -->
    <div v-if="form.parallelBranches.length > 0">
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">Convergence Point</h3>
      <p class="text-xs text-muted-foreground mb-2">Which step should wait for all parallel branches to complete before continuing?</p>
      <select
        v-model.number="form.convergenceStep"
        class="w-48 border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        <option :value="null">None</option>
        <option v-for="step in form.mainSteps" :key="step.order" :value="step.order">
          Step {{ step.order }}: {{ step.label || '(untitled)' }}
        </option>
      </select>
    </div>

    <!-- On Complete Actions -->
    <div>
      <h3 class="text-sm font-semibold text-foreground uppercase tracking-wide mb-4">On Complete</h3>
      <div class="flex flex-wrap gap-4">
        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.onComplete.telegram" type="checkbox" class="rounded border-input" />
          <span>Telegram notification</span>
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.onComplete.summary" type="checkbox" class="rounded border-input" />
          <span>Generate summary</span>
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.onComplete.generateManifest" type="checkbox" class="rounded border-input" />
          <span>Generate manifest</span>
        </label>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-end gap-3 pt-4 border-t">
      <button
        type="button"
        class="px-4 py-2 rounded-md text-sm font-medium border hover:bg-muted transition-colors"
        @click="emit('cancelled')"
      >
        Cancel
      </button>
      <button
        type="button"
        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
        :disabled="saving"
        @click="save"
      >
        {{ saving ? 'Saving...' : (isEdit ? 'Update Pipeline' : 'Create Pipeline') }}
      </button>
    </div>
  </div>
</template>
