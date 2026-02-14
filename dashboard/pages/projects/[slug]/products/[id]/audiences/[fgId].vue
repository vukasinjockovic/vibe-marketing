<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../../../../../convex/_generated/api'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

const productId = computed(() => route.params.id as string)
const fgId = computed(() => route.params.fgId as string)

const { data: fg, loading } = useConvexQuery(
  api.focusGroups.get,
  computed(() => fgId.value ? { id: fgId.value as any } : 'skip'),
)

const { data: enrichmentProgress } = useConvexQuery(
  api.focusGroups.getEnrichmentProgress,
  computed(() => fgId.value ? { id: fgId.value as any } : 'skip'),
)

const { mutate: createTask } = useConvexMutation(api.tasks.create)

const showEdit = ref(false)
const reEnriching = ref(false)

// Enrichment field definitions
const enrichmentFields = [
  { key: 'awarenessStage', label: 'Awareness Stage', weight: 15 },
  { key: 'sophisticationLevel', label: 'Sophistication Level', weight: 10 },
  { key: 'contentPreferences', label: 'Content Preferences', weight: 10 },
  { key: 'influenceSources', label: 'Influence Sources', weight: 10 },
  { key: 'purchaseBehavior', label: 'Purchase Behavior', weight: 15 },
  { key: 'competitorContext', label: 'Competitor Context', weight: 10 },
  { key: 'communicationStyle', label: 'Communication Style', weight: 10 },
  { key: 'seasonalContext', label: 'Seasonal Context', weight: 5 },
  { key: 'negativeTriggers', label: 'Negative Triggers', weight: 10 },
  { key: 'awarenessSignals', label: 'Awareness Signals', weight: 5 },
]

function isFieldFilled(field: string): boolean {
  if (!fg.value) return false
  const val = (fg.value as any)[field]
  return val !== undefined && val !== null
}

function getFieldValue(field: string): any {
  if (!fg.value) return null
  return (fg.value as any)[field]
}

function getFieldConfidence(field: string): string | undefined {
  if (!fg.value?.enrichments?.length) return undefined
  // Get the latest enrichment entry for this field
  const entries = fg.value.enrichments.filter((e: any) => e.field === field)
  if (!entries.length) return undefined
  return entries[entries.length - 1].confidence
}

async function reEnrichNow() {
  if (!project.value?._id) return
  reEnriching.value = true
  try {
    await createTask({
      projectId: project.value._id as any,
      title: `Re-enrich: ${fg.value?.name || 'Focus Group'}`,
      description: `Re-enrich focus group "${fg.value?.name}" with missing fields: ${enrichmentProgress.value?.missingFields?.join(', ') || 'unknown'}`,
      pipeline: [
        { step: 1, status: 'in_progress', agent: 'vibe-audience-enricher', description: 'Enrich focus group with missing intelligence data' },
      ],
      priority: 'medium',
      createdBy: 'dashboard',
      contentType: 'audience_research',
      metadata: {
        productId: productId.value,
        focusGroupId: fgId.value,
        singleGroupEnrichment: true,
      },
    })
    toast.success('Re-enrichment task created!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to create enrichment task')
  } finally {
    reEnriching.value = false
  }
}

function onSaved() {
  showEdit.value = false
  toast.success('Focus group updated!')
}

function formatValue(val: any): string {
  if (val === null || val === undefined) return ''
  if (typeof val === 'string') return val
  if (typeof val === 'object') return JSON.stringify(val, null, 2)
  return String(val)
}

const backUrl = computed(() => {
  if (!project.value?.slug || !productId.value) return '#'
  return `/projects/${project.value.slug}/products/${productId.value}/audiences`
})
</script>

<template>
  <div>
    <div class="flex items-center gap-2 mb-4">
      <NuxtLink
        :to="backUrl"
        class="text-sm text-muted-foreground hover:text-muted-foreground inline-flex items-center gap-1"
      >
        <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
        </svg>
        Back to Audiences
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <VEmptyState
      v-else-if="!fg"
      title="Focus group not found"
      description="This focus group doesn't exist or has been deleted."
    >
      <template #icon>
        <svg class="w-6 h-6 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
        </svg>
      </template>
      <NuxtLink
        :to="backUrl"
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
      >
        Back to Audiences
      </NuxtLink>
    </VEmptyState>

    <template v-else>
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div class="flex items-center gap-3">
            <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary text-lg font-bold shrink-0">
              {{ fg.number || '#' }}
            </span>
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-foreground">{{ fg.name }}</h1>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-sm text-muted-foreground">{{ fg.nickname }}</span>
                <VStatusBadge :status="fg.category" size="sm" />
                <span class="text-xs text-muted-foreground/70">{{ fg.source }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 text-sm border rounded-md text-muted-foreground hover:bg-muted/50 transition-colors inline-flex items-center gap-1.5"
            @click="showEdit = true"
          >
            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
            </svg>
            Edit
          </button>
          <button
            class="px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
            :disabled="reEnriching"
            @click="reEnrichNow"
          >
            {{ reEnriching ? 'Creating...' : 'Re-enrich Now' }}
          </button>
        </div>
      </div>

      <!-- Enrichment Progress -->
      <div class="rounded-lg border bg-card shadow-sm p-6 mb-6">
        <h3 class="font-semibold text-foreground mb-3">Enrichment Progress</h3>
        <EnrichmentProgressBar
          v-if="enrichmentProgress"
          :score="enrichmentProgress.score"
          :label="`${enrichmentProgress.filledCount} of ${enrichmentProgress.totalCount} fields filled`"
        />
        <div v-if="enrichmentProgress?.missingFields?.length" class="mt-3">
          <span class="text-xs text-muted-foreground">Missing fields:</span>
          <div class="flex flex-wrap gap-1 mt-1">
            <span
              v-for="field in enrichmentProgress.missingFields"
              :key="field"
              class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full"
            >
              {{ field }}
            </span>
          </div>
        </div>
      </div>

      <!-- Core Data -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- Left Column: Basic Info -->
        <div class="rounded-lg border bg-card shadow-sm p-4 sm:p-6 space-y-4">
          <h3 class="font-semibold text-foreground">Core Profile</h3>

          <div>
            <p class="text-xs font-medium text-muted-foreground uppercase">Overview</p>
            <p class="text-sm text-foreground mt-1">{{ fg.overview }}</p>
          </div>

          <div>
            <p class="text-xs font-medium text-muted-foreground uppercase">Transformation Promise</p>
            <p class="text-sm text-foreground italic mt-1">"{{ fg.transformationPromise }}"</p>
          </div>

          <div v-if="fg.demographics">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-2">Demographics</p>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-muted-foreground">Age:</span> {{ fg.demographics.ageRange }}</div>
              <div><span class="text-muted-foreground">Gender:</span> {{ fg.demographics.gender }}</div>
              <div><span class="text-muted-foreground">Income:</span> {{ fg.demographics.income }}</div>
              <div><span class="text-muted-foreground">Lifestyle:</span> {{ fg.demographics.lifestyle }}</div>
            </div>
          </div>

          <div v-if="fg.psychographics">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-2">Psychographics</p>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-muted-foreground">Lifestyle:</span> {{ fg.psychographics.lifestyle }}</div>
              <div><span class="text-muted-foreground">Identity:</span> {{ fg.psychographics.identity }}</div>
            </div>
            <div v-if="fg.psychographics.values?.length" class="mt-2">
              <span class="text-xs text-muted-foreground">Values:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="v in fg.psychographics.values" :key="v" class="bg-purple-50 text-purple-700 text-xs px-2 py-0.5 rounded-full">{{ v }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Marketing Data -->
        <div class="rounded-lg border bg-card shadow-sm p-4 sm:p-6 space-y-4">
          <h3 class="font-semibold text-foreground">Marketing Intelligence</h3>

          <div v-if="fg.coreDesires?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Core Desires</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="d in fg.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">{{ d }}</span>
            </div>
          </div>

          <div v-if="fg.painPoints?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Pain Points</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="p in fg.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">{{ p }}</span>
            </div>
          </div>

          <div v-if="fg.fears?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Fears</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="f in fg.fears" :key="f" class="bg-orange-50 text-orange-700 text-xs px-2 py-0.5 rounded-full">{{ f }}</span>
            </div>
          </div>

          <div v-if="fg.objections?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Objections</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="o in fg.objections" :key="o" class="bg-amber-50 text-amber-700 text-xs px-2 py-0.5 rounded-full">{{ o }}</span>
            </div>
          </div>

          <div v-if="fg.marketingHooks?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Marketing Hooks</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="h in fg.marketingHooks" :key="h" class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full">{{ h }}</span>
            </div>
          </div>

          <div v-if="fg.languagePatterns?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Language Patterns</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="l in fg.languagePatterns" :key="l" class="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">{{ l }}</span>
            </div>
          </div>

          <div v-if="fg.emotionalTriggers?.length">
            <p class="text-xs font-medium text-muted-foreground uppercase mb-1">Emotional Triggers</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="t in fg.emotionalTriggers" :key="t" class="bg-pink-50 text-pink-700 text-xs px-2 py-0.5 rounded-full">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Enrichment Field Status -->
      <div class="rounded-lg border bg-card shadow-sm p-6 mb-6">
        <h3 class="font-semibold text-foreground mb-4">Enrichment Field Status</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <EnrichmentFieldStatus
            v-for="field in enrichmentFields"
            :key="field.key"
            :label="field.label"
            :value="getFieldValue(field.key)"
            :filled="isFieldFilled(field.key)"
            :confidence="getFieldConfidence(field.key)"
          />
        </div>
      </div>

      <!-- Enrichment History Timeline -->
      <div class="rounded-lg border bg-card shadow-sm p-6">
        <h3 class="font-semibold text-foreground mb-4">Enrichment History</h3>
        <EnrichmentTimeline :enrichments="fg.enrichments || []" />
      </div>

      <!-- Edit Modal -->
      <VModal v-model="showEdit" title="Edit Focus Group" size="xl">
        <FocusGroupForm
          v-if="project"
          :project-id="project._id"
          :product-id="productId"
          :focus-group="fg"
          @saved="onSaved"
        />
      </VModal>
    </template>
  </div>
</template>
