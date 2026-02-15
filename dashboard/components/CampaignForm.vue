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
const totalSteps = 6
const stepLabels = ['Basic\nInformation', 'Products\n& Audiences', 'Pipeline\nSelection', 'Skill\nSelection', 'Agent\nOverrides', 'Configuration']

// Product role types
type ProductRole = 'main' | 'upsell' | 'addon' | 'downsell'

interface CampaignProduct {
  productId: string
  role: ProductRole
}

interface SkillSelectionEntry {
  categoryKey: string
  skillId: string
  subSelections?: string[]
}

interface AgentOverride {
  agentName: string
  selections: SkillSelectionEntry[]
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
  // Per-article deliverables
  perArticle: {
    heroImage: true,
    socialPosts: {
      facebook: 0,
      instagram: 0,
      x: 1,
      linkedin: 1,
      tiktok: 0,
      pinterest: 0,
      vk: 0,
    },
    emailExcerpt: false,
    videoScript: false,
    redditVersion: false,
  },
  // Standalone deliverables (not per-article)
  standalone: {
    emailSequence: 0,
    landingPage: 0,
    leadMagnet: 0,
    adCopySet: 0,
    pressRelease: 0,
    ebookFull: 0,
  },
  // Skill config (new generic format)
  skillSelections: [] as SkillSelectionEntry[],
  agentOverrides: [] as AgentOverride[],
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

// Load sales pipeline presets
const { data: pipelinePresets } = useConvexQuery(
  api.pipelines.listByCategory,
  { category: 'sales' },
)

// Selected pipeline details
const { data: selectedPipeline } = useConvexQuery(
  api.pipelines.get,
  computed(() => form.pipelineId ? { id: form.pipelineId as any } : 'skip'),
)

// Extract agent names from the selected pipeline
const pipelineAgentNames = computed(() => {
  if (!selectedPipeline.value) return []
  const names = new Set<string>()
  for (const s of selectedPipeline.value.mainSteps || []) {
    if (s.agent) names.add(s.agent)
  }
  for (const branch of selectedPipeline.value.parallelBranches || []) {
    for (const s of branch.steps || []) {
      if (s.agent) names.add(s.agent)
    }
  }
  return [...names]
})

// Load skill categories relevant to the selected pipeline's agents
const { data: relevantCategories } = useConvexQuery(
  api.skillCategories.listForPipeline,
  computed(() => pipelineAgentNames.value.length > 0
    ? { agentNames: pipelineAgentNames.value }
    : 'skip'
  ),
)

// Category keys for loading skills
const relevantCategoryKeys = computed(() =>
  (relevantCategories.value || []).map((c: any) => c.key)
)

// Load selectable skills for the relevant categories
const { data: categorySkills } = useConvexQuery(
  api.skills.listSelectableByCategories,
  computed(() => relevantCategoryKeys.value.length > 0
    ? { categoryKeys: relevantCategoryKeys.value }
    : 'skip'
  ),
)

// Group skills by category key
const skillsByCategory = computed(() => {
  if (!categorySkills.value) return {} as Record<string, any[]>
  const grouped: Record<string, any[]> = {}
  for (const s of categorySkills.value) {
    if (!grouped[s.category]) grouped[s.category] = []
    grouped[s.category].push(s)
  }
  return grouped
})

// Categories that actually have selectable skills (for display)
const selectableCategories = computed(() => {
  if (!relevantCategories.value) return []
  return relevantCategories.value.filter((c: any) =>
    (skillsByCategory.value[c.key]?.length ?? 0) > 0
  )
})

// Auto-active categories (for info banner)
const autoActiveCategories = computed(() => {
  if (!relevantCategories.value) return []
  return relevantCategories.value.filter((c: any) =>
    (skillsByCategory.value[c.key]?.length ?? 0) === 0
  )
})

const { mutate: createCampaign } = useConvexMutation(api.campaigns.create)
const { mutate: updateCampaign } = useConvexMutation(api.campaigns.update)
const saving = ref(false)
const toast = useToast()
const isEdit = computed(() => !!props.campaign)

// ═══ Skill Selection helpers ═══
function getSelectionsForCategory(categoryKey: string): SkillSelectionEntry[] {
  return form.skillSelections.filter(s => s.categoryKey === categoryKey)
}

function isSkillSelected(skillId: string): boolean {
  return form.skillSelections.some(s => s.skillId === skillId)
}

function selectSingleSkill(categoryKey: string, skillId: string | null) {
  // Remove all existing selections for this category
  form.skillSelections = form.skillSelections.filter(s => s.categoryKey !== categoryKey)
  if (skillId) {
    form.skillSelections.push({ categoryKey, skillId })
  }
}

function toggleMultiSkill(categoryKey: string, skillId: string) {
  const idx = form.skillSelections.findIndex(s => s.categoryKey === categoryKey && s.skillId === skillId)
  if (idx >= 0) {
    form.skillSelections.splice(idx, 1)
  } else {
    form.skillSelections.push({ categoryKey, skillId })
  }
}

function toggleSubSelection(skillId: string, key: string) {
  const sel = form.skillSelections.find(s => s.skillId === skillId)
  if (!sel) return
  if (!sel.subSelections) sel.subSelections = []
  const idx = sel.subSelections.indexOf(key)
  if (idx >= 0) {
    sel.subSelections.splice(idx, 1)
  } else {
    sel.subSelections.push(key)
  }
}

function getSkillById(skillId: string) {
  return categorySkills.value?.find((s: any) => s._id === skillId)
}

// ═══ Agent Override helpers ═══
const overrideableAgents = computed(() => {
  if (!selectedPipeline.value || !relevantCategories.value) return []
  const agents: { name: string; label: string; categories: any[] }[] = []
  const seen = new Set<string>()
  const allSteps = [
    ...(selectedPipeline.value.mainSteps || []),
    ...(selectedPipeline.value.parallelBranches || []).flatMap((b: any) => b.steps || []),
  ]
  for (const s of allSteps) {
    if (!s.agent || seen.has(s.agent)) continue
    seen.add(s.agent)
    // Find categories relevant to this agent
    const agentCats = (relevantCategories.value || []).filter((c: any) =>
      c.pipelineAgentNames?.includes(s.agent) && (skillsByCategory.value[c.key]?.length ?? 0) > 0
    )
    if (agentCats.length > 0) {
      agents.push({ name: s.agent, label: s.label || s.agent, categories: agentCats })
    }
  }
  return agents
})

function hasAgentOverride(agentName: string): boolean {
  return form.agentOverrides.some(o => o.agentName === agentName)
}

function enableAgentOverride(agentName: string) {
  if (hasAgentOverride(agentName)) return
  // Pre-fill with campaign defaults
  form.agentOverrides.push({
    agentName,
    selections: [...form.skillSelections.map(s => ({ ...s }))],
  })
}

function disableAgentOverride(agentName: string) {
  const idx = form.agentOverrides.findIndex(o => o.agentName === agentName)
  if (idx >= 0) form.agentOverrides.splice(idx, 1)
}

function toggleAgentOverride(agentName: string) {
  if (hasAgentOverride(agentName)) {
    disableAgentOverride(agentName)
  } else {
    enableAgentOverride(agentName)
  }
}

function overrideSelectSingle(agentName: string, categoryKey: string, skillId: string | null) {
  const override = form.agentOverrides.find(o => o.agentName === agentName)
  if (!override) return
  override.selections = override.selections.filter(s => s.categoryKey !== categoryKey)
  if (skillId) {
    override.selections.push({ categoryKey, skillId })
  }
}

function overrideToggleMulti(agentName: string, categoryKey: string, skillId: string) {
  const override = form.agentOverrides.find(o => o.agentName === agentName)
  if (!override) return
  const idx = override.selections.findIndex(s => s.categoryKey === categoryKey && s.skillId === skillId)
  if (idx >= 0) {
    override.selections.splice(idx, 1)
  } else {
    override.selections.push({ categoryKey, skillId })
  }
}

function overrideToggleSub(agentName: string, skillId: string, key: string) {
  const override = form.agentOverrides.find(o => o.agentName === agentName)
  if (!override) return
  const sel = override.selections.find(s => s.skillId === skillId)
  if (!sel) return
  if (!sel.subSelections) sel.subSelections = []
  const idx = sel.subSelections.indexOf(key)
  if (idx >= 0) {
    sel.subSelections.splice(idx, 1)
  } else {
    sel.subSelections.push(key)
  }
}

function overrideHasSkill(agentName: string, skillId: string): boolean {
  const override = form.agentOverrides.find(o => o.agentName === agentName)
  return override?.selections.some(s => s.skillId === skillId) ?? false
}

function overrideGetSingleSkill(agentName: string, categoryKey: string): string | null {
  const override = form.agentOverrides.find(o => o.agentName === agentName)
  const sel = override?.selections.find(s => s.categoryKey === categoryKey)
  return sel?.skillId ?? null
}

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
  // Load from productionManifest (new) or deliverableConfig (legacy)
  if (c.productionManifest) {
    const m = c.productionManifest
    form.targetArticleCount = m.articles?.count || 5
    if (m.articles?.perArticle) {
      const pa = m.articles.perArticle
      form.perArticle.heroImage = pa.heroImage ?? false
      form.perArticle.emailExcerpt = pa.emailExcerpt ?? false
      form.perArticle.videoScript = pa.videoScript ?? false
      form.perArticle.redditVersion = pa.redditVersion ?? false
      if (pa.socialPosts) Object.assign(form.perArticle.socialPosts, pa.socialPosts)
    }
    if (m.standalone) Object.assign(form.standalone, m.standalone)
  } else {
    form.targetArticleCount = c.targetArticleCount || 5
    if (c.deliverableConfig) {
      const dc = c.deliverableConfig
      form.perArticle.heroImage = dc.heroImage ?? false
      form.perArticle.emailExcerpt = dc.emailExcerpt ?? false
      form.perArticle.videoScript = dc.videoScript ?? false
      form.perArticle.redditVersion = dc.redditVersion ?? false
      if (dc.socialX) form.perArticle.socialPosts.x = 1
      if (dc.socialLinkedIn) form.perArticle.socialPosts.linkedin = 1
      if (dc.socialInstagram) form.perArticle.socialPosts.instagram = 1
      if (dc.socialFacebook) form.perArticle.socialPosts.facebook = 1
      if (dc.socialTikTok) form.perArticle.socialPosts.tiktok = 1
      if (dc.socialPinterest) form.perArticle.socialPosts.pinterest = 1
      if (dc.socialVK) form.perArticle.socialPosts.vk = 1
      if (dc.emailSequence) form.standalone.emailSequence = 1
      if (dc.landingPage) form.standalone.landingPage = 1
      if (dc.leadMagnet) form.standalone.leadMagnet = 1
      if (dc.adCopySet) form.standalone.adCopySet = 1
      if (dc.pressRelease) form.standalone.pressRelease = 1
      if (dc.ebookFull) form.standalone.ebookFull = 1
    }
  }
  if (c.skillConfig) {
    const sc = c.skillConfig
    // New format
    if (sc.selections?.length) {
      form.skillSelections = sc.selections.map((s: any) => ({
        categoryKey: s.categoryKey,
        skillId: s.skillId,
        subSelections: s.subSelections,
      }))
    }
    // Legacy format → convert to new
    else {
      if (sc.offerFramework?.skillId) {
        form.skillSelections.push({ categoryKey: 'L2_offer', skillId: sc.offerFramework.skillId })
      }
      if (sc.persuasionSkills?.length) {
        for (const ps of sc.persuasionSkills) {
          form.skillSelections.push({
            categoryKey: 'L3_persuasion',
            skillId: ps.skillId,
            subSelections: ps.subSelections,
          })
        }
      }
      if (sc.primaryCopyStyle?.skillId) {
        form.skillSelections.push({ categoryKey: 'L4_craft', skillId: sc.primaryCopyStyle.skillId })
      }
    }
    // Agent overrides (new format)
    if (sc.agentOverrides?.length) {
      for (const ao of sc.agentOverrides) {
        if (ao.selections?.length) {
          form.agentOverrides.push({
            agentName: ao.agentName,
            selections: ao.selections.map((s: any) => ({
              categoryKey: s.categoryKey,
              skillId: s.skillId,
              subSelections: s.subSelections,
            })),
          })
        }
      }
    }
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
    case 4: return true // Skill selection is optional
    case 5: return true // Agent overrides are optional
    case 6: return true
    default: return false
  }
})

const perArticleToggles = [
  { key: 'heroImage', label: 'Hero Image' },
  { key: 'emailExcerpt', label: 'Email Excerpt' },
  { key: 'videoScript', label: 'Video Script' },
  { key: 'redditVersion', label: 'Reddit Version' },
] as const

const socialPlatforms = [
  { key: 'x', label: 'X / Twitter' },
  { key: 'linkedin', label: 'LinkedIn' },
  { key: 'facebook', label: 'Facebook' },
  { key: 'instagram', label: 'Instagram' },
  { key: 'tiktok', label: 'TikTok' },
  { key: 'pinterest', label: 'Pinterest' },
  { key: 'vk', label: 'VK' },
] as const

const standaloneOptions = [
  { key: 'emailSequence', label: 'Email Sequence' },
  { key: 'landingPage', label: 'Landing Page' },
  { key: 'leadMagnet', label: 'Lead Magnet' },
  { key: 'adCopySet', label: 'Ad Copy Set' },
  { key: 'pressRelease', label: 'Press Release' },
  { key: 'ebookFull', label: 'Full eBook' },
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

function removeProduct(productId: string) {
  const idx = form.products.findIndex(p => p.productId === productId)
  if (idx >= 0) form.products.splice(idx, 1)
}

function addProduct(productId: string) {
  const hasMain = form.products.some(p => p.role === 'main')
  form.products.push({ productId, role: hasMain ? 'upsell' : 'main' })
  productSearch.value = ''
  productDropdownOpen.value = false
}

function getProduct(productId: string) {
  return products.value?.find((p: any) => p._id === productId)
}

// Product search
const productSearch = ref('')
const productDropdownOpen = ref(false)

const selectedProducts = computed(() => {
  if (!products.value) return []
  return form.products
    .map(fp => {
      const p = products.value!.find((pr: any) => pr._id === fp.productId)
      return p ? { ...p, role: fp.role } : null
    })
    .filter(Boolean) as any[]
})

const filteredUnselectedProducts = computed(() => {
  if (!products.value) return []
  const selectedIds = new Set(form.products.map(p => p.productId))
  let list = products.value.filter((p: any) => !selectedIds.has(p._id))
  if (productSearch.value.trim()) {
    const q = productSearch.value.toLowerCase()
    list = list.filter((p: any) => p.name.toLowerCase().includes(q) || p.description?.toLowerCase().includes(q))
  }
  return list
})

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
  for (const sel of form.skillSelections) {
    const s = getSkillById(sel.skillId)
    if (s) {
      const cat = relevantCategories.value?.find((c: any) => c.key === sel.categoryKey)
      const prefix = cat?.displayName?.split(':')[0] || sel.categoryKey
      const subs = sel.subSelections?.length ? ` [${sel.subSelections.join(', ')}]` : ''
      parts.push(`${prefix}: ${s.displayName}${subs}`)
    }
  }
  return parts
})

// Build skillConfig for submission
function buildSkillConfig() {
  const config: any = {}
  if (form.skillSelections.length) {
    config.selections = form.skillSelections.map(s => ({
      categoryKey: s.categoryKey,
      skillId: s.skillId,
      subSelections: s.subSelections?.length ? s.subSelections : undefined,
    }))
  }
  if (form.agentOverrides.length) {
    config.agentOverrides = form.agentOverrides.map(o => ({
      agentName: o.agentName,
      selections: o.selections.map(s => ({
        categoryKey: s.categoryKey,
        skillId: s.skillId,
        subSelections: s.subSelections?.length ? s.subSelections : undefined,
      })),
    }))
  }
  return Object.keys(config).length > 0 ? config : undefined
}

function buildProductionManifest() {
  // Build socialPosts object (only non-zero values)
  const sp = form.perArticle.socialPosts
  const socialPosts: Record<string, number> = {}
  let hasSocial = false
  for (const [k, v] of Object.entries(sp)) {
    if (v > 0) { socialPosts[k] = v; hasSocial = true }
  }

  // Build standalone object (only non-zero values)
  const standalone: Record<string, number> = {}
  let hasStandalone = false
  for (const [k, v] of Object.entries(form.standalone)) {
    if (v > 0) { standalone[k] = v; hasStandalone = true }
  }

  return {
    articles: {
      count: form.targetArticleCount,
      perArticle: {
        heroImage: form.perArticle.heroImage || undefined,
        socialPosts: hasSocial ? socialPosts : undefined,
        emailExcerpt: form.perArticle.emailExcerpt || undefined,
        videoScript: form.perArticle.videoScript || undefined,
        redditVersion: form.perArticle.redditVersion || undefined,
      },
    },
    standalone: hasStandalone ? standalone : undefined,
  }
}

async function submit() {
  if (!stepValid.value) return
  saving.value = true
  try {
    const skillConfig = buildSkillConfig()
    const productionManifest = buildProductionManifest()
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
        productionManifest,
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
        productionManifest,
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
    <div class="flex items-center justify-between mb-8 overflow-x-auto scrollbar-hide">
      <template v-for="s in totalSteps" :key="s">
        <div class="flex flex-col items-center min-w-[3rem] sm:min-w-[4.5rem]">
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
        <!-- Selected products -->
        <div v-if="selectedProducts.length" class="space-y-2 mb-3">
          <div
            v-for="sp in selectedProducts"
            :key="'sel-' + sp._id"
            class="flex items-center gap-3 p-3 border border-primary/20 bg-primary/5 rounded-md"
          >
            <div class="flex-1 min-w-0">
              <span class="font-medium text-sm">{{ sp.name }}</span>
              <p v-if="sp.description" class="text-xs text-muted-foreground mt-0.5 truncate">{{ sp.description }}</p>
            </div>
            <select
              :value="sp.role"
              class="shrink-0 border border-input rounded px-2 py-1 text-xs bg-background"
              @change="setProductRole(sp._id, ($event.target as HTMLSelectElement).value as ProductRole)"
            >
              <option v-for="r in productRoles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
            <button
              type="button"
              class="shrink-0 w-5 h-5 flex items-center justify-center rounded-full text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
              @click="removeProduct(sp._id)"
            >
              <span class="text-xs leading-none">&times;</span>
            </button>
          </div>
        </div>

        <!-- Product search dropdown -->
        <div v-if="products?.length" class="relative">
          <input
            v-model="productSearch"
            type="text"
            placeholder="Search and add products..."
            class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            @focus="productDropdownOpen = true"
            @blur="setTimeout(() => productDropdownOpen = false, 150)"
          />
          <div
            v-if="productDropdownOpen && filteredUnselectedProducts.length"
            class="absolute z-10 mt-1 w-full bg-popover border border-border rounded-md shadow-md max-h-48 overflow-y-auto"
          >
            <button
              v-for="p in filteredUnselectedProducts"
              :key="p._id"
              type="button"
              class="w-full flex items-start gap-3 px-3 py-2.5 text-left hover:bg-muted/50 transition-colors border-b border-border last:border-b-0"
              @mousedown.prevent="addProduct(p._id)"
            >
              <div class="flex-1 min-w-0">
                <span class="font-medium text-sm">{{ p.name }}</span>
                <p v-if="p.description" class="text-xs text-muted-foreground mt-0.5 truncate">{{ p.description }}</p>
              </div>
            </button>
          </div>
          <p v-if="productDropdownOpen && productSearch && !filteredUnselectedProducts.length" class="absolute z-10 mt-1 w-full bg-popover border border-border rounded-md shadow-md px-3 py-2 text-sm text-muted-foreground">
            No matching products found.
          </p>
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
        <hr v-if="selectedFocusGroups.length" class="border-border" />
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

    <!-- Step 4: Skill Selection (dynamic by pipeline agents) -->
    <div v-if="step === 4" class="space-y-6">
      <!-- Auto-active notice -->
      <div class="rounded-lg border border-blue-200 bg-blue-50 p-3">
        <p class="text-sm text-blue-800">
          <strong>L1: Awareness</strong> (Schwartz) is auto-applied based on your selected focus groups.
          <br />
          <strong>L5: Quality</strong> (humanizer + writing-clearly) is auto-applied as post-processing.
        </p>
      </div>

      <!-- No pipeline selected -->
      <div v-if="!form.pipelineId" class="text-sm text-muted-foreground text-center py-4">
        Select a pipeline in Step 3 to see available skill categories.
      </div>

      <!-- Dynamic skill categories -->
      <template v-for="cat in selectableCategories" :key="cat.key">
        <!-- Single-select category -->
        <div v-if="cat.selectionMode === 'single'">
          <h4 class="text-sm font-semibold text-foreground mb-1">{{ cat.displayName }}</h4>
          <p class="text-xs text-muted-foreground mb-3">{{ cat.description }}</p>
          <div class="space-y-2">
            <!-- "None" option for allowNone categories -->
            <label
              v-if="cat.allowNone"
              class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
              :class="getSelectionsForCategory(cat.key).length === 0 ? 'border-primary bg-primary/5' : ''"
            >
              <input
                type="radio"
                :name="'cat-' + cat.key"
                :checked="getSelectionsForCategory(cat.key).length === 0"
                class="mt-1.5"
                @change="selectSingleSkill(cat.key, null)"
              />
              <div>
                <span class="font-medium text-sm">None</span>
                <p class="text-xs text-muted-foreground">No {{ cat.displayName.toLowerCase() }} applied</p>
              </div>
            </label>
            <label
              v-for="skill in skillsByCategory[cat.key]"
              :key="skill._id"
              class="flex items-start gap-3 p-3 border border-border rounded-md cursor-pointer hover:bg-muted/50 transition-colors"
              :class="isSkillSelected(skill._id) ? 'border-primary bg-primary/5' : ''"
            >
              <input
                type="radio"
                :name="'cat-' + cat.key"
                :checked="isSkillSelected(skill._id)"
                class="mt-1.5"
                @change="selectSingleSkill(cat.key, skill._id)"
              />
              <div>
                <span class="font-medium text-sm">{{ skill.displayName }}</span>
                <span v-if="skill.tagline" class="text-xs text-muted-foreground ml-2 italic">{{ skill.tagline }}</span>
                <p class="text-xs text-muted-foreground mt-0.5">{{ skill.dashboardDescription || skill.description }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Multi-select category -->
        <div v-else-if="cat.selectionMode === 'multiple'">
          <h4 class="text-sm font-semibold text-foreground mb-1">{{ cat.displayName }}</h4>
          <p class="text-xs text-muted-foreground mb-3">{{ cat.description }}</p>
          <div class="space-y-2">
            <div
              v-for="skill in skillsByCategory[cat.key]"
              :key="skill._id"
              class="border border-border rounded-md transition-colors"
              :class="isSkillSelected(skill._id) ? 'border-primary bg-primary/5' : ''"
            >
              <label class="flex items-start gap-3 p-3 cursor-pointer hover:bg-muted/50">
                <input
                  type="checkbox"
                  :checked="isSkillSelected(skill._id)"
                  class="mt-1.5"
                  @change="toggleMultiSkill(cat.key, skill._id)"
                />
                <div class="flex-1">
                  <span class="font-medium text-sm">{{ skill.displayName }}</span>
                  <span v-if="skill.tagline" class="text-xs text-muted-foreground ml-2 italic">{{ skill.tagline }}</span>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ skill.dashboardDescription || skill.description }}</p>
                </div>
              </label>
              <!-- Sub-selections -->
              <div
                v-if="isSkillSelected(skill._id) && skill.subSelections?.length"
                class="px-3 pb-3 ml-8"
              >
                <p class="text-xs text-muted-foreground mb-1.5">Select specific principles to apply:</p>
                <div class="flex flex-wrap gap-1.5">
                  <label
                    v-for="sub in skill.subSelections"
                    :key="sub.key"
                    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs cursor-pointer transition-colors"
                    :class="form.skillSelections.find(s => s.skillId === skill._id)?.subSelections?.includes(sub.key)
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'"
                  >
                    <input
                      type="checkbox"
                      :checked="form.skillSelections.find(s => s.skillId === skill._id)?.subSelections?.includes(sub.key)"
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
      </template>

      <!-- Selection Summary -->
      <div v-if="selectedSkillSummary.length" class="rounded-lg border bg-card p-4">
        <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Selected Skills</h4>
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

      <div v-else-if="form.pipelineId" class="text-sm text-muted-foreground text-center py-4">
        No skills selected. The pipeline will use default writing without specialized frameworks.
      </div>
    </div>

    <!-- Step 5: Agent Overrides -->
    <div v-if="step === 5" class="space-y-6">
      <div class="rounded-lg border border-amber-200 bg-amber-50 p-3">
        <p class="text-sm text-amber-800">
          <strong>Optional:</strong> Override skill selections per agent. By default, all agents use the campaign-level selections from Step 4.
        </p>
      </div>

      <div v-if="!overrideableAgents.length" class="text-sm text-muted-foreground text-center py-4">
        No agents with configurable skills in this pipeline.
      </div>

      <div v-for="agent in overrideableAgents" :key="agent.name" class="border border-border rounded-lg">
        <div class="flex items-center justify-between p-4">
          <div>
            <span class="font-medium text-sm">{{ agent.label }}</span>
            <span class="text-xs text-muted-foreground ml-2">{{ agent.name }}</span>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <span class="text-xs text-muted-foreground">Custom skills</span>
            <input
              type="checkbox"
              :checked="hasAgentOverride(agent.name)"
              class="rounded"
              @change="toggleAgentOverride(agent.name)"
            />
          </label>
        </div>

        <!-- Override is OFF -->
        <div v-if="!hasAgentOverride(agent.name)" class="px-4 pb-3">
          <p class="text-xs text-muted-foreground">Using campaign defaults from Step 4</p>
        </div>

        <!-- Override is ON — compact selectors -->
        <div v-else class="px-4 pb-4 space-y-3 border-t border-border pt-3">
          <div v-for="cat in agent.categories" :key="cat.key">
            <h5 class="text-xs font-medium text-foreground mb-1.5">{{ cat.displayName }}</h5>

            <!-- Single-select override -->
            <div v-if="cat.selectionMode === 'single'" class="space-y-1">
              <label
                v-if="cat.allowNone"
                class="flex items-center gap-2 text-xs cursor-pointer p-1.5 rounded hover:bg-muted/50"
                :class="!overrideGetSingleSkill(agent.name, cat.key) ? 'text-primary font-medium' : 'text-muted-foreground'"
              >
                <input
                  type="radio"
                  :name="'override-' + agent.name + '-' + cat.key"
                  :checked="!overrideGetSingleSkill(agent.name, cat.key)"
                  @change="overrideSelectSingle(agent.name, cat.key, null)"
                />
                None
              </label>
              <label
                v-for="skill in skillsByCategory[cat.key]"
                :key="skill._id"
                class="flex items-center gap-2 text-xs cursor-pointer p-1.5 rounded hover:bg-muted/50"
                :class="overrideHasSkill(agent.name, skill._id) ? 'text-primary font-medium' : 'text-muted-foreground'"
              >
                <input
                  type="radio"
                  :name="'override-' + agent.name + '-' + cat.key"
                  :checked="overrideHasSkill(agent.name, skill._id)"
                  @change="overrideSelectSingle(agent.name, cat.key, skill._id)"
                />
                {{ skill.displayName }}
              </label>
            </div>

            <!-- Multi-select override -->
            <div v-else-if="cat.selectionMode === 'multiple'" class="space-y-1">
              <div v-for="skill in skillsByCategory[cat.key]" :key="skill._id">
                <label
                  class="flex items-center gap-2 text-xs cursor-pointer p-1.5 rounded hover:bg-muted/50"
                  :class="overrideHasSkill(agent.name, skill._id) ? 'text-primary font-medium' : 'text-muted-foreground'"
                >
                  <input
                    type="checkbox"
                    :checked="overrideHasSkill(agent.name, skill._id)"
                    @change="overrideToggleMulti(agent.name, cat.key, skill._id)"
                  />
                  {{ skill.displayName }}
                </label>
                <!-- Sub-selections for override -->
                <div
                  v-if="overrideHasSkill(agent.name, skill._id) && skill.subSelections?.length"
                  class="ml-6 mt-1 flex flex-wrap gap-1"
                >
                  <label
                    v-for="sub in skill.subSelections"
                    :key="sub.key"
                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] cursor-pointer transition-colors"
                    :class="form.agentOverrides.find(o => o.agentName === agent.name)?.selections.find(s => s.skillId === skill._id)?.subSelections?.includes(sub.key)
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'"
                  >
                    <input
                      type="checkbox"
                      :checked="form.agentOverrides.find(o => o.agentName === agent.name)?.selections.find(s => s.skillId === skill._id)?.subSelections?.includes(sub.key)"
                      class="sr-only"
                      @change="overrideToggleSub(agent.name, skill._id, sub.key)"
                    />
                    {{ sub.label }}
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 6: Configuration -->
    <div v-if="step === 6" class="space-y-6">
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

      <!-- Per-Article Deliverables -->
      <VFormField label="Per-Article Deliverables" hint="These are produced for each article.">
        <div class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <label
              v-for="opt in perArticleToggles"
              :key="opt.key"
              class="flex items-center gap-2 text-sm cursor-pointer"
            >
              <input
                v-model="(form.perArticle as any)[opt.key]"
                type="checkbox"
              />
              {{ opt.label }}
            </label>
          </div>

          <!-- Social Posts per platform -->
          <div class="mt-3">
            <h5 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Social Posts per Article</h5>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              <div
                v-for="platform in socialPlatforms"
                :key="platform.key"
                class="flex items-center gap-2"
              >
                <input
                  v-model.number="(form.perArticle.socialPosts as any)[platform.key]"
                  type="number"
                  min="0"
                  max="10"
                  class="w-16 border border-input rounded-md px-2 py-1 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                />
                <span class="text-sm text-foreground">{{ platform.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </VFormField>

      <!-- Standalone Deliverables -->
      <VFormField label="Standalone Deliverables" hint="Produced once for the entire campaign, not per article.">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="opt in standaloneOptions"
            :key="opt.key"
            class="flex items-center gap-2"
          >
            <input
              v-model.number="(form.standalone as any)[opt.key]"
              type="number"
              min="0"
              max="20"
              class="w-16 border border-input rounded-md px-2 py-1 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            />
            <span class="text-sm text-foreground">{{ opt.label }}</span>
          </div>
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
    <div class="flex flex-col-reverse sm:flex-row justify-between gap-3 mt-8 pt-4 border-t border-border">
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
