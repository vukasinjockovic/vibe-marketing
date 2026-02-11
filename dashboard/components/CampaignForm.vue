<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Check } from 'lucide-vue-next'

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  created: []
}>()

const step = ref(1)
const totalSteps = 4

// Product role types
type ProductRole = 'main' | 'upsell' | 'addon' | 'downsell'

interface CampaignProduct {
  productId: string
  role: ProductRole
}

// Form state
const form = reactive({
  name: '',
  slug: '',
  description: '',
  products: [] as CampaignProduct[],
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

// Load focus groups at project level
const { data: focusGroups } = useConvexQuery(
  api.focusGroups.listByProject,
  { projectId: props.projectId as any },
)

const productRoles: { value: ProductRole; label: string }[] = [
  { value: 'main', label: 'Main' },
  { value: 'upsell', label: 'Upsell' },
  { value: 'addon', label: 'Add-on' },
  { value: 'downsell', label: 'Downsell' },
]

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

// Step validation
const stepValid = computed(() => {
  switch (step.value) {
    case 1: return form.name.trim().length > 0 && form.slug.trim().length > 0
    case 2: return form.products.some(p => p.role === 'main') && form.targetFocusGroupIds.length > 0
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

function toggleProduct(productId: string) {
  const idx = form.products.findIndex(p => p.productId === productId)
  if (idx >= 0) {
    form.products.splice(idx, 1)
  } else {
    // Default to 'main' if no main yet, otherwise 'upsell'
    const hasMain = form.products.some(p => p.role === 'main')
    form.products.push({ productId, role: hasMain ? 'upsell' : 'main' })
  }
}

function getProductRole(productId: string): ProductRole | undefined {
  return form.products.find(p => p.productId === productId)?.role
}

function setProductRole(productId: string, role: ProductRole) {
  const entry = form.products.find(p => p.productId === productId)
  if (entry) entry.role = role
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
      products: form.products.map(p => ({ productId: p.productId as any, role: p.role })),
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
            ? 'bg-primary text-primary-foreground'
            : s === step
              ? 'bg-primary text-primary-foreground ring-4 ring-primary/20'
              : 'bg-muted text-muted-foreground'"
        >
          <Check v-if="s < step" class="w-4 h-4" />
          <span v-else>{{ s }}</span>
        </div>
        <div
          v-if="s < totalSteps"
          class="w-12 h-0.5 mx-1"
          :class="s < step ? 'bg-primary' : 'bg-muted'"
        />
      </div>
    </div>

    <div class="text-center mb-6">
      <h3 class="text-sm font-medium text-muted-foreground uppercase tracking-wide">
        Step {{ step }} of {{ totalSteps }}
      </h3>
      <p class="text-lg font-semibold text-foreground mt-1">
        <span v-if="step === 1">Basic Information</span>
        <span v-else-if="step === 2">Products &amp; Audiences</span>
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
          class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </VFormField>

      <VFormField label="Slug" hint="Auto-generated from name. Used in URLs and file paths.">
        <input
          v-model="form.slug"
          type="text"
          placeholder="campaign-slug"
          class="w-full border border-input rounded-md px-3 py-2 text-sm bg-muted/50 ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </VFormField>

      <VFormField label="Description">
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Brief description of the campaign goals and scope..."
          class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </VFormField>
    </div>

    <!-- Step 2: Products & Focus Groups -->
    <div v-if="step === 2" class="space-y-6">
      <VFormField label="Products" hint="Select products and assign roles. At least one 'Main' product required." required>
        <div v-if="products?.length" class="space-y-2 max-h-48 overflow-y-auto">
          <div
            v-for="p in products"
            :key="p._id"
            class="flex items-center gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="getProductRole(p._id) ? 'border-primary bg-primary/5' : ''"
            @click="toggleProduct(p._id)"
          >
            <input
              type="checkbox"
              :checked="!!getProductRole(p._id)"
              class="shrink-0"
              @click.stop
              @change="toggleProduct(p._id)"
            />
            <div class="flex-1 min-w-0">
              <span class="font-medium text-sm">{{ p.name }}</span>
              <p v-if="p.description" class="text-xs text-muted-foreground mt-0.5 truncate">{{ p.description }}</p>
            </div>
            <select
              v-if="getProductRole(p._id)"
              :value="getProductRole(p._id)"
              class="shrink-0 border border-input rounded px-2 py-1 text-xs bg-background"
              @click.stop
              @change="setProductRole(p._id, ($event.target as HTMLSelectElement).value as ProductRole)"
            >
              <option v-for="r in productRoles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>
        </div>
        <p v-else class="text-sm text-muted-foreground">No products found. Create a product first.</p>
      </VFormField>

      <VFormField label="Target Audiences" hint="Select focus groups to target with this campaign." required>
        <div v-if="focusGroups?.length" class="space-y-2 max-h-48 overflow-y-auto">
          <label
            v-for="fg in focusGroups"
            :key="fg._id"
            class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="form.targetFocusGroupIds.includes(fg._id) ? 'border-primary bg-primary/5' : ''"
          >
            <input
              type="checkbox"
              :checked="form.targetFocusGroupIds.includes(fg._id)"
              class="mt-0.5"
              @change="toggleFocusGroup(fg._id)"
            />
            <div>
              <span class="font-medium text-sm">{{ fg.name }}</span>
              <span v-if="fg.nickname" class="text-xs text-muted-foreground ml-1">({{ fg.nickname }})</span>
              <p v-if="fg.overview" class="text-xs text-muted-foreground mt-0.5 line-clamp-2">{{ fg.overview }}</p>
            </div>
          </label>
        </div>
        <p v-else class="text-sm text-muted-foreground">No audiences found. Create or import audiences first.</p>
      </VFormField>
    </div>

    <!-- Step 3: Pipeline -->
    <div v-if="step === 3" class="space-y-4">
      <VFormField label="Pipeline Template" required>
        <div v-if="pipelinePresets?.length" class="space-y-2">
          <label
            v-for="p in pipelinePresets"
            :key="p._id"
            class="flex items-start gap-3 p-4 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="form.pipelineId === p._id ? 'border-primary bg-primary/5' : ''"
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
                <span class="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded">
                  {{ p.mainSteps?.length || 0 }} steps
                </span>
              </div>
              <p v-if="p.description" class="text-xs text-muted-foreground mt-1">{{ p.description }}</p>
            </div>
          </label>
        </div>
        <p v-else class="text-sm text-muted-foreground">No pipeline presets available.</p>
      </VFormField>

      <!-- Show selected pipeline steps -->
      <div v-if="selectedPipeline" class="mt-4">
        <h4 class="text-sm font-medium text-muted-foreground mb-2">Pipeline Steps</h4>
        <div class="space-y-1">
          <div
            v-for="(s, i) in selectedPipeline.mainSteps"
            :key="i"
            class="flex items-center gap-2 text-sm"
          >
            <span class="w-6 h-6 rounded-full bg-muted text-muted-foreground flex items-center justify-center text-xs font-medium">
              {{ i + 1 }}
            </span>
            <span class="font-medium">{{ s.label }}</span>
            <span v-if="s.agent" class="text-xs text-muted-foreground">{{ s.agent }}</span>
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
          class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </VFormField>
    </div>

    <!-- Navigation buttons -->
    <div class="flex justify-between mt-8 pt-4 border-t border-border">
      <button
        v-if="step > 1"
        class="px-4 py-2 text-sm text-muted-foreground hover:bg-muted transition-colors rounded-md"
        @click="step--"
      >
        Back
      </button>
      <div v-else />

      <button
        v-if="step < totalSteps"
        :disabled="!stepValid"
        class="px-4 py-2 text-sm text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="step++"
      >
        Next
      </button>
      <button
        v-else
        :disabled="!stepValid || saving"
        class="px-4 py-2 text-sm text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        @click="submit"
      >
        {{ saving ? 'Creating...' : 'Create Campaign' }}
      </button>
    </div>
  </div>
</template>
