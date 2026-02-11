<script setup lang="ts">
import { api } from '../../convex/_generated/api'

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  created: []
}>()

const step = ref(1)
const totalSteps = 4

// Form state
const form = reactive({
  name: '',
  slug: '',
  description: '',
  productId: '' as string,
  targetFocusGroupIds: [] as string[],
  pipelineId: '' as string,
  seedKeywords: [] as string[],
  competitorUrls: [] as string[],
  notes: '',
  deliverableConfig: {
    heroImage: true,
    socialX: true,
    socialLinkedIn: true,
    emailExcerpt: false,
    videoScript: false,
    landingPage: false,
    emailSequence: false,
    leadMagnet: false,
    adCopySet: false,
    pressRelease: false,
  },
})

// Load products for this project
const { data: products } = useConvexQuery(
  api.products.list,
  { projectId: props.projectId as any },
)

// Load focus groups when product selected
const { data: focusGroups } = useConvexQuery(
  api.focusGroups.listByProduct,
  computed(() => form.productId ? { productId: form.productId as any } : 'skip'),
)

// Load pipeline presets
const { data: pipelinePresets } = useConvexQuery(api.pipelines.listPresets, {})

// Selected pipeline details
const { data: selectedPipeline } = useConvexQuery(
  api.pipelines.get,
  computed(() => form.pipelineId ? { id: form.pipelineId as any } : 'skip'),
)

const { mutate: createCampaign } = useConvexMutation(api.campaigns.create)
const saving = ref(false)
const toast = useToast()

// Auto-generate slug from name
watch(() => form.name, (name) => {
  form.slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
})

// Reset focus groups when product changes
watch(() => form.productId, () => {
  form.targetFocusGroupIds = []
})

// Step validation
const stepValid = computed(() => {
  switch (step.value) {
    case 1: return form.name.trim().length > 0 && form.slug.trim().length > 0
    case 2: return !!form.productId && form.targetFocusGroupIds.length > 0
    case 3: return !!form.pipelineId
    case 4: return true
    default: return false
  }
})

const deliverableOptions = [
  { key: 'heroImage', label: 'Hero Image' },
  { key: 'socialX', label: 'X / Twitter Post' },
  { key: 'socialLinkedIn', label: 'LinkedIn Post' },
  { key: 'emailExcerpt', label: 'Email Excerpt' },
  { key: 'videoScript', label: 'Video Script' },
  { key: 'landingPage', label: 'Landing Page' },
  { key: 'emailSequence', label: 'Email Sequence' },
  { key: 'leadMagnet', label: 'Lead Magnet' },
  { key: 'adCopySet', label: 'Ad Copy Set' },
  { key: 'pressRelease', label: 'Press Release' },
] as const

function toggleFocusGroup(id: string) {
  const idx = form.targetFocusGroupIds.indexOf(id)
  if (idx >= 0) {
    form.targetFocusGroupIds.splice(idx, 1)
  } else {
    form.targetFocusGroupIds.push(id)
  }
}

async function submit() {
  if (!stepValid.value) return
  saving.value = true
  try {
    await createCampaign({
      projectId: props.projectId as any,
      name: form.name,
      slug: form.slug,
      description: form.description,
      productId: form.productId as any,
      pipelineId: form.pipelineId as any,
      pipelineSnapshot: selectedPipeline.value,
      targetFocusGroupIds: form.targetFocusGroupIds as any[],
      seedKeywords: form.seedKeywords,
      competitorUrls: form.competitorUrls,
      notes: form.notes || undefined,
      deliverableConfig: form.deliverableConfig,
    })
    toast.success('Campaign created!')
    emit('created')
  } catch (e: any) {
    toast.error(e.message || 'Failed to create campaign')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <!-- Step indicator -->
    <div class="flex items-center justify-center mb-8">
      <div v-for="s in totalSteps" :key="s" class="flex items-center">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors"
          :class="s < step
            ? 'bg-primary-600 text-white'
            : s === step
              ? 'bg-primary-600 text-white ring-4 ring-primary-100'
              : 'bg-gray-200 text-gray-500'"
        >
          <span v-if="s < step" class="i-heroicons-check text-sm" />
          <span v-else>{{ s }}</span>
        </div>
        <div
          v-if="s < totalSteps"
          class="w-12 h-0.5 mx-1"
          :class="s < step ? 'bg-primary-600' : 'bg-gray-200'"
        />
      </div>
    </div>

    <div class="text-center mb-6">
      <h3 class="text-sm font-medium text-gray-500 uppercase tracking-wide">
        Step {{ step }} of {{ totalSteps }}
      </h3>
      <p class="text-lg font-semibold text-gray-900 mt-1">
        <span v-if="step === 1">Basic Information</span>
        <span v-else-if="step === 2">Product &amp; Audience</span>
        <span v-else-if="step === 3">Pipeline Selection</span>
        <span v-else>Configuration</span>
      </p>
    </div>

    <!-- Step 1: Basic info -->
    <div v-if="step === 1" class="space-y-4">
      <VFormField label="Campaign Name" required>
        <input
          v-model="form.name"
          type="text"
          placeholder="e.g. Q1 Blog Series - Fat Loss"
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <VFormField label="Slug" hint="Auto-generated from name. Used in URLs and file paths.">
        <input
          v-model="form.slug"
          type="text"
          placeholder="campaign-slug"
          class="w-full border rounded-md px-3 py-2 text-sm bg-gray-50 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>

      <VFormField label="Description">
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Brief description of the campaign goals and scope..."
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>
    </div>

    <!-- Step 2: Product & Focus Groups -->
    <div v-if="step === 2" class="space-y-4">
      <VFormField label="Product" required>
        <select
          v-model="form.productId"
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="" disabled>Select a product...</option>
          <option v-for="p in products" :key="p._id" :value="p._id">
            {{ p.name }}
          </option>
        </select>
      </VFormField>

      <VFormField v-if="form.productId" label="Target Focus Groups" required>
        <div v-if="focusGroups?.length" class="space-y-2 max-h-60 overflow-y-auto">
          <label
            v-for="fg in focusGroups"
            :key="fg._id"
            class="flex items-start gap-3 p-3 border rounded-md cursor-pointer hover:bg-gray-50 transition-colors"
            :class="form.targetFocusGroupIds.includes(fg._id) ? 'border-primary-500 bg-primary-50' : ''"
          >
            <input
              type="checkbox"
              :checked="form.targetFocusGroupIds.includes(fg._id)"
              class="mt-0.5"
              @change="toggleFocusGroup(fg._id)"
            />
            <div>
              <span class="font-medium text-sm">{{ fg.name }}</span>
              <p v-if="fg.description" class="text-xs text-gray-500 mt-0.5">{{ fg.description }}</p>
            </div>
          </label>
        </div>
        <p v-else class="text-sm text-gray-500">No focus groups found for this product.</p>
      </VFormField>
    </div>

    <!-- Step 3: Pipeline -->
    <div v-if="step === 3" class="space-y-4">
      <VFormField label="Pipeline Template" required>
        <div v-if="pipelinePresets?.length" class="space-y-2">
          <label
            v-for="p in pipelinePresets"
            :key="p._id"
            class="flex items-start gap-3 p-4 border rounded-md cursor-pointer hover:bg-gray-50 transition-colors"
            :class="form.pipelineId === p._id ? 'border-primary-500 bg-primary-50' : ''"
          >
            <input
              v-model="form.pipelineId"
              type="radio"
              :value="p._id"
              class="mt-0.5"
            />
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-medium text-sm">{{ p.name }}</span>
                <span class="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                  {{ p.mainSteps?.length || 0 }} steps
                </span>
              </div>
              <p v-if="p.description" class="text-xs text-gray-500 mt-1">{{ p.description }}</p>
            </div>
          </label>
        </div>
        <p v-else class="text-sm text-gray-500">No pipeline presets available.</p>
      </VFormField>

      <!-- Show selected pipeline steps -->
      <div v-if="selectedPipeline" class="mt-4">
        <h4 class="text-sm font-medium text-gray-700 mb-2">Pipeline Steps</h4>
        <div class="space-y-1">
          <div
            v-for="(s, i) in selectedPipeline.mainSteps"
            :key="i"
            class="flex items-center gap-2 text-sm"
          >
            <span class="w-6 h-6 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center text-xs font-medium">
              {{ i + 1 }}
            </span>
            <span class="font-medium">{{ s.label }}</span>
            <span v-if="s.agent" class="text-xs text-gray-500">{{ s.agent }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 4: Config -->
    <div v-if="step === 4" class="space-y-4">
      <VFormField label="Seed Keywords">
        <VChipInput v-model="form.seedKeywords" placeholder="Add keywords..." />
      </VFormField>

      <VFormField label="Competitor URLs">
        <VChipInput v-model="form.competitorUrls" placeholder="Add competitor URLs..." />
      </VFormField>

      <VFormField label="Deliverables">
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="opt in deliverableOptions"
            :key="opt.key"
            class="flex items-center gap-2 text-sm cursor-pointer"
          >
            <input
              v-model="(form.deliverableConfig as any)[opt.key]"
              type="checkbox"
            />
            {{ opt.label }}
          </label>
        </div>
      </VFormField>

      <VFormField label="Notes">
        <textarea
          v-model="form.notes"
          rows="3"
          placeholder="Any additional notes for agents..."
          class="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </VFormField>
    </div>

    <!-- Navigation buttons -->
    <div class="flex justify-between mt-8 pt-4 border-t">
      <button
        v-if="step > 1"
        class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
        @click="step--"
      >
        Back
      </button>
      <div v-else />

      <button
        v-if="step < totalSteps"
        :disabled="!stepValid"
        class="px-4 py-2 text-sm text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="step++"
      >
        Next
      </button>
      <button
        v-else
        :disabled="!stepValid || saving"
        class="px-4 py-2 text-sm text-white bg-primary-600 rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="submit"
      >
        {{ saving ? 'Creating...' : 'Create Campaign' }}
      </button>
    </div>
  </div>
</template>
