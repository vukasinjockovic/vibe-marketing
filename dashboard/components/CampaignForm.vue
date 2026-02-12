<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import { Check } from 'lucide-vue-next'

const props = defineProps<{
  projectId: string
  campaign?: any
}>()

const emit = defineEmits<{
  created: []
  saved: []
}>()

const step = ref(1)
const totalSteps = 5
const stepLabels = ['Basic\nInformation', 'Products\n& Audiences', 'Pipeline\nSelection', 'Writing\nStrategy', 'Configuration']

// Product role types
type ProductRole = 'main' | 'upsell' | 'addon' | 'downsell'

interface CampaignProduct {
  productId: string
  role: ProductRole
}

interface SkillSelection {
  skillId: string
  subSelections?: string[]
}

interface AgentOverride {
  agentName: string
  pipelineStep: number
  skillOverrides: SkillSelection[]
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
  targetArticleCount: 5,
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
  // Writing Strategy (skillConfig)
  skillConfig: {
    offerFramework: null as { skillId: string } | null,
    persuasionSkills: [] as SkillSelection[],
    primaryCopyStyle: null as { skillId: string } | null,
    agentOverrides: [] as AgentOverride[],
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

// Load campaign-selectable skills
const { data: selectableSkills } = useConvexQuery(api.skills.listCampaignSelectable, {})

// Group skills by category (layer)
const skillsByLayer = computed(() => {
  if (!selectableSkills.value) return {}
  const grouped: Record<string, any[]> = {}
  for (const s of selectableSkills.value) {
    if (!grouped[s.category]) grouped[s.category] = []
    grouped[s.category].push(s)
  }
  return grouped
})

const layerLabels: Record<string, string> = {
  L2_offer: 'L2: Offer Framework',
  L3_persuasion: 'L3: Persuasion & Narrative',
  L4_craft: 'L4: Copy Style',
}

const layerOrder = ['L2_offer', 'L3_persuasion', 'L4_craft']

// Pipeline writing steps (steps that have an agent — writing agents)
const writingSteps = computed(() => {
  if (!selectedPipeline.value?.mainSteps) return []
  return selectedPipeline.value.mainSteps.filter((s: any) => s.agent)
})

const { mutate: createCampaign } = useConvexMutation(api.campaigns.create)
const { mutate: updateCampaign } = useConvexMutation(api.campaigns.update)
const saving = ref(false)
const toast = useToast()
const isEdit = computed(() => !!props.campaign)

// Pre-populate form when editing
if (props.campaign) {
  const c = props.campaign
  form.name = c.name || ''
  form.slug = c.slug || ''
  form.description = c.description || ''
  form.products = (c.products || []).map((p: any) => ({ productId: p.productId, role: p.role }))
  form.targetFocusGroupIds = c.targetFocusGroupIds || []
  form.pipelineId = c.pipelineId || ''
  form.seedKeywords = c.seedKeywords || []
  form.competitorUrls = c.competitorUrls || []
  form.notes = c.notes || ''
  form.targetArticleCount = c.targetArticleCount || 5
  if (c.deliverableConfig) {
    Object.assign(form.deliverableConfig, c.deliverableConfig)
  }
  if (c.skillConfig) {
    if (c.skillConfig.offerFramework) form.skillConfig.offerFramework = c.skillConfig.offerFramework
    if (c.skillConfig.persuasionSkills) form.skillConfig.persuasionSkills = c.skillConfig.persuasionSkills
    if (c.skillConfig.primaryCopyStyle) form.skillConfig.primaryCopyStyle = c.skillConfig.primaryCopyStyle
    if (c.skillConfig.agentOverrides) form.skillConfig.agentOverrides = c.skillConfig.agentOverrides
  }
}

// Auto-generate slug from name (only for new campaigns)
watch(() => form.name, (name) => {
  if (!isEdit.value) {
    form.slug = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
  }
})

// Step validation
const stepValid = computed(() => {
  switch (step.value) {
    case 1: return form.name.trim().length > 0 && form.slug.trim().length > 0
    case 2: return form.products.some(p => p.role === 'main') && form.targetFocusGroupIds.length > 0
    case 3: return !!form.pipelineId
    case 4: return true // Writing strategy is optional
    case 5: return true
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

// ═══ Writing Strategy helpers ═══
function setOfferFramework(skillId: string | null) {
  form.skillConfig.offerFramework = skillId ? { skillId } : null
}

function togglePersuasionSkill(skillId: string) {
  const idx = form.skillConfig.persuasionSkills.findIndex(s => s.skillId === skillId)
  if (idx >= 0) {
    form.skillConfig.persuasionSkills.splice(idx, 1)
  } else {
    form.skillConfig.persuasionSkills.push({ skillId })
  }
}

function isPersuasionSelected(skillId: string): boolean {
  return form.skillConfig.persuasionSkills.some(s => s.skillId === skillId)
}

function getPersuasionSelection(skillId: string): SkillSelection | undefined {
  return form.skillConfig.persuasionSkills.find(s => s.skillId === skillId)
}

function toggleSubSelection(skillId: string, key: string) {
  const sel = form.skillConfig.persuasionSkills.find(s => s.skillId === skillId)
  if (!sel) return
  if (!sel.subSelections) sel.subSelections = []
  const idx = sel.subSelections.indexOf(key)
  if (idx >= 0) {
    sel.subSelections.splice(idx, 1)
  } else {
    sel.subSelections.push(key)
  }
}

function setPrimaryCopyStyle(skillId: string | null) {
  form.skillConfig.primaryCopyStyle = skillId ? { skillId } : null
}

function getSkillById(skillId: string) {
  return selectableSkills.value?.find((s: any) => s._id === skillId)
}

// Selected focus groups (resolved objects for display)
const selectedFocusGroups = computed(() => {
  if (!focusGroups.value) return []
  return form.targetFocusGroupIds
    .map(id => focusGroups.value!.find((fg: any) => fg._id === id))
    .filter(Boolean) as any[]
})

// Summary of selected skills for display
const selectedSkillSummary = computed(() => {
  const parts: string[] = []
  if (form.skillConfig.offerFramework) {
    const s = getSkillById(form.skillConfig.offerFramework.skillId)
    if (s) parts.push(`L2: ${s.displayName}`)
  }
  for (const ps of form.skillConfig.persuasionSkills) {
    const s = getSkillById(ps.skillId)
    if (s) {
      const subs = ps.subSelections?.length ? ` [${ps.subSelections.join(', ')}]` : ''
      parts.push(`L3: ${s.displayName}${subs}`)
    }
  }
  if (form.skillConfig.primaryCopyStyle) {
    const s = getSkillById(form.skillConfig.primaryCopyStyle.skillId)
    if (s) parts.push(`L4: ${s.displayName}`)
  }
  return parts
})

// Build skillConfig for submission
function buildSkillConfig() {
  const config: any = {}
  if (form.skillConfig.offerFramework) {
    config.offerFramework = { skillId: form.skillConfig.offerFramework.skillId }
  }
  if (form.skillConfig.persuasionSkills.length) {
    config.persuasionSkills = form.skillConfig.persuasionSkills.map(s => ({
      skillId: s.skillId,
      subSelections: s.subSelections?.length ? s.subSelections : undefined,
    }))
  }
  if (form.skillConfig.primaryCopyStyle) {
    config.primaryCopyStyle = { skillId: form.skillConfig.primaryCopyStyle.skillId }
  }
  if (form.skillConfig.agentOverrides.length) {
    config.agentOverrides = form.skillConfig.agentOverrides
  }
  return Object.keys(config).length > 0 ? config : undefined
}

async function submit() {
  if (!stepValid.value) return
  saving.value = true
  try {
    const skillConfig = buildSkillConfig()
    if (isEdit.value) {
      await updateCampaign({
        id: props.campaign._id as any,
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
        targetArticleCount: form.targetArticleCount,
        deliverableConfig: form.deliverableConfig,
        skillConfig,
      })
      toast.success('Campaign updated!')
      emit('saved')
    } else {
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
        targetArticleCount: form.targetArticleCount,
        deliverableConfig: form.deliverableConfig,
        skillConfig,
      })
      toast.success('Campaign created!')
      emit('created')
    }
  } catch (e: any) {
    toast.error(e.message || (isEdit.value ? 'Failed to update campaign' : 'Failed to create campaign'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <!-- Step indicator -->
    <div class="flex items-center justify-between mb-8">
      <template v-for="s in totalSteps" :key="s">
        <div class="flex flex-col items-center" style="min-width: 4.5rem;">
          <button
            type="button"
            class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium transition-colors"
            :class="[
              s < step
                ? 'bg-primary text-primary-foreground'
                : s === step
                  ? 'bg-primary text-primary-foreground ring-4 ring-primary/20'
                  : 'bg-muted text-muted-foreground',
              isEdit ? 'cursor-pointer hover:ring-2 hover:ring-primary/30' : s < step ? 'cursor-pointer' : 'cursor-default',
            ]"
            @click="isEdit ? (step = s) : s < step ? (step = s) : undefined"
          >
            <Check v-if="s < step" class="w-4 h-4" />
            <span v-else>{{ s }}</span>
          </button>
          <span
            class="text-[10px] leading-tight mt-1.5 text-center whitespace-pre-line"
            :class="s === step ? 'text-foreground font-semibold' : 'text-muted-foreground'"
          >{{ stepLabels[s - 1] }}</span>
        </div>
        <div
          v-if="s < totalSteps"
          class="flex-1 h-0.5 mx-1 mt-[-1.25rem]"
          :class="s < step ? 'bg-primary' : 'bg-muted'"
        />
      </template>
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
        <!-- Selected audiences summary -->
        <div v-if="selectedFocusGroups.length" class="space-y-1 mb-3">
          <div
            v-for="fg in selectedFocusGroups"
            :key="'sel-' + fg._id"
            class="flex items-center gap-2 px-3 py-1.5 bg-primary/5 border border-primary/20 rounded-md text-sm"
          >
            <span class="font-medium truncate flex-1">{{ fg.name }}</span>
            <span v-if="fg.nickname" class="text-xs text-muted-foreground truncate">({{ fg.nickname }})</span>
            <button
              type="button"
              class="shrink-0 w-5 h-5 flex items-center justify-center rounded-full text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              @click="toggleFocusGroup(fg._id)"
            >
              <span class="text-xs leading-none">&times;</span>
            </button>
          </div>
        </div>
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

    <!-- Step 4: Writing Strategy -->
    <div v-if="step === 4" class="space-y-6">
      <!-- Auto-active notice -->
      <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
        <p class="text-sm text-blue-800">
          <strong>L1: Awareness</strong> (Schwartz) is auto-applied based on your selected focus groups.
          <br />
          <strong>L5: Quality</strong> (humanizer + writing-clearly) is auto-applied as post-processing.
        </p>
      </div>

      <!-- L2: Offer Framework (radio — pick one or none) -->
      <div v-if="skillsByLayer['L2_offer']?.length">
        <h4 class="text-sm font-semibold text-foreground mb-1">{{ layerLabels['L2_offer'] }}</h4>
        <p class="text-xs text-muted-foreground mb-3">Choose an offer framework (optional). Best for landing pages, sales pages, and ad copy.</p>
        <div class="space-y-2">
          <label
            class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="!form.skillConfig.offerFramework ? 'border-primary bg-primary/5' : ''"
          >
            <input
              type="radio"
              name="offerFramework"
              :checked="!form.skillConfig.offerFramework"
              class="mt-0.5"
              @change="setOfferFramework(null)"
            />
            <div>
              <span class="font-medium text-sm">None</span>
              <p class="text-xs text-muted-foreground">No offer framework (blog posts, informational content)</p>
            </div>
          </label>
          <label
            v-for="skill in skillsByLayer['L2_offer']"
            :key="skill._id"
            class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="form.skillConfig.offerFramework?.skillId === skill._id ? 'border-primary bg-primary/5' : ''"
          >
            <input
              type="radio"
              name="offerFramework"
              :checked="form.skillConfig.offerFramework?.skillId === skill._id"
              class="mt-0.5"
              @change="setOfferFramework(skill._id)"
            />
            <div>
              <span class="font-medium text-sm">{{ skill.displayName }}</span>
              <span v-if="skill.tagline" class="text-xs text-muted-foreground ml-2 italic">{{ skill.tagline }}</span>
              <p class="text-xs text-muted-foreground mt-0.5">{{ skill.dashboardDescription || skill.description }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- L3: Persuasion (checkbox — multi-select with sub-selections) -->
      <div v-if="skillsByLayer['L3_persuasion']?.length">
        <h4 class="text-sm font-semibold text-foreground mb-1">{{ layerLabels['L3_persuasion'] }}</h4>
        <p class="text-xs text-muted-foreground mb-3">Select one or more persuasion/narrative skills. Sub-select specific principles where available.</p>
        <div class="space-y-2">
          <div
            v-for="skill in skillsByLayer['L3_persuasion']"
            :key="skill._id"
            class="border border-border rounded-md transition-colors"
            :class="isPersuasionSelected(skill._id) ? 'border-primary bg-primary/5' : ''"
          >
            <label class="flex items-start gap-3 p-3 cursor-pointer hover:bg-muted/50">
              <input
                type="checkbox"
                :checked="isPersuasionSelected(skill._id)"
                class="mt-0.5"
                @change="togglePersuasionSkill(skill._id)"
              />
              <div class="flex-1">
                <span class="font-medium text-sm">{{ skill.displayName }}</span>
                <span v-if="skill.tagline" class="text-xs text-muted-foreground ml-2 italic">{{ skill.tagline }}</span>
                <p class="text-xs text-muted-foreground mt-0.5">{{ skill.dashboardDescription || skill.description }}</p>
              </div>
            </label>
            <!-- Sub-selections (e.g., Cialdini principles, Sugarman triggers) -->
            <div
              v-if="isPersuasionSelected(skill._id) && skill.subSelections?.length"
              class="px-3 pb-3 ml-8"
            >
              <p class="text-xs text-muted-foreground mb-1.5">Select specific principles to apply:</p>
              <div class="flex flex-wrap gap-1.5">
                <label
                  v-for="sub in skill.subSelections"
                  :key="sub.key"
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs cursor-pointer transition-colors"
                  :class="getPersuasionSelection(skill._id)?.subSelections?.includes(sub.key)
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'"
                >
                  <input
                    type="checkbox"
                    :checked="getPersuasionSelection(skill._id)?.subSelections?.includes(sub.key)"
                    class="sr-only"
                    @change="toggleSubSelection(skill._id, sub.key)"
                  />
                  {{ sub.label }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- L4: Copy Style (radio — pick one primary) -->
      <div v-if="skillsByLayer['L4_craft']?.length">
        <h4 class="text-sm font-semibold text-foreground mb-1">{{ layerLabels['L4_craft'] }}</h4>
        <p class="text-xs text-muted-foreground mb-3">Choose a primary copy style (optional). Sets the overall writing voice.</p>
        <div class="space-y-2">
          <label
            class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="!form.skillConfig.primaryCopyStyle ? 'border-primary bg-primary/5' : ''"
          >
            <input
              type="radio"
              name="copyStyle"
              :checked="!form.skillConfig.primaryCopyStyle"
              class="mt-0.5"
              @change="setPrimaryCopyStyle(null)"
            />
            <div>
              <span class="font-medium text-sm">None</span>
              <p class="text-xs text-muted-foreground">Use default writing style</p>
            </div>
          </label>
          <label
            v-for="skill in skillsByLayer['L4_craft']"
            :key="skill._id"
            class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
            :class="form.skillConfig.primaryCopyStyle?.skillId === skill._id ? 'border-primary bg-primary/5' : ''"
          >
            <input
              type="radio"
              name="copyStyle"
              :checked="form.skillConfig.primaryCopyStyle?.skillId === skill._id"
              class="mt-0.5"
              @change="setPrimaryCopyStyle(skill._id)"
            />
            <div>
              <span class="font-medium text-sm">{{ skill.displayName }}</span>
              <span v-if="skill.tagline" class="text-xs text-muted-foreground ml-2 italic">{{ skill.tagline }}</span>
              <p class="text-xs text-muted-foreground mt-0.5">{{ skill.dashboardDescription || skill.description }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Selection Summary -->
      <div v-if="selectedSkillSummary.length" class="rounded-lg border bg-card p-4">
        <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Selected Writing Strategy</h4>
        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="label in selectedSkillSummary"
            :key="label"
            class="inline-block bg-primary/10 text-primary text-xs px-2.5 py-1 rounded-full font-medium"
          >
            {{ label }}
          </span>
        </div>
        <p class="text-xs text-muted-foreground mt-2">
          + L1: Schwartz Awareness (auto) + L5: humanizer + writing-clearly (auto)
        </p>
      </div>

      <div v-else class="text-sm text-muted-foreground text-center py-4">
        No writing skills selected. The pipeline will use default writing without specialized frameworks.
      </div>
    </div>

    <!-- Step 5: Config -->
    <div v-if="step === 5" class="space-y-4">
      <VFormField label="Number of Articles" hint="How many content pieces to generate for this campaign.">
        <input
          v-model.number="form.targetArticleCount"
          type="number"
          min="1"
          max="50"
          class="w-32 border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </VFormField>

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
        {{ saving ? (isEdit ? 'Saving...' : 'Creating...') : (isEdit ? 'Save Changes' : 'Create Campaign') }}
      </button>
    </div>
  </div>
</template>
