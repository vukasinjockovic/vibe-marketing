<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../../../../convex/_generated/api'
import { useAudienceJobs } from '../../../../../composables/useAudienceJobs'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

const productId = computed(() => route.params.id as string)

const { data: product } = useConvexQuery(
  api.products.get,
  computed(() => productId.value ? { id: productId.value as any } : 'skip'),
)

const { data: focusGroups, loading } = useConvexQuery(
  api.focusGroups.listByProduct,
  computed(() => productId.value ? { productId: productId.value as any } : 'skip'),
)

const { mutate: removeFocusGroup } = useConvexMutation(api.focusGroups.remove)

// Audience jobs tracking
const { hasActiveJob, activeTasks, hasPendingReview, stagingSummary, latestTaskId } = useAudienceJobs(productId)

// Enrichment progress for each focus group
const enrichmentProgressMap = ref<Record<string, { score: number; missingFields: string[] }>>({})

// Watch focus groups and fetch enrichment progress for each
const focusGroupIds = computed(() => focusGroups.value?.map((fg: any) => fg._id) || [])

// We query enrichment progress individually per FG -- for performance, we batch in a computed
// Since useConvexQuery cannot be called in a loop reactively, we approximate by computing from FG data
const overallEnrichmentScore = computed(() => {
  if (!focusGroups.value?.length) return 0
  const enrichmentFields = [
    'awarenessStage', 'sophisticationLevel', 'contentPreferences',
    'influenceSources', 'purchaseBehavior', 'competitorContext',
    'communicationStyle', 'seasonalContext', 'negativeTriggers', 'awarenessSignals',
  ]
  const weights: Record<string, number> = {
    awarenessStage: 15, sophisticationLevel: 10, contentPreferences: 10,
    influenceSources: 10, purchaseBehavior: 15, competitorContext: 10,
    communicationStyle: 10, seasonalContext: 5, negativeTriggers: 10, awarenessSignals: 5,
  }

  let totalScore = 0
  for (const fg of focusGroups.value) {
    let fgScore = 0
    for (const field of enrichmentFields) {
      if ((fg as any)[field] !== undefined && (fg as any)[field] !== null) {
        fgScore += weights[field] || 0
      }
    }
    totalScore += fgScore
  }
  return Math.round(totalScore / focusGroups.value.length)
})

function getFgEnrichmentScore(fg: any): number {
  const enrichmentFields = [
    'awarenessStage', 'sophisticationLevel', 'contentPreferences',
    'influenceSources', 'purchaseBehavior', 'competitorContext',
    'communicationStyle', 'seasonalContext', 'negativeTriggers', 'awarenessSignals',
  ]
  const weights: Record<string, number> = {
    awarenessStage: 15, sophisticationLevel: 10, contentPreferences: 10,
    influenceSources: 10, purchaseBehavior: 15, competitorContext: 10,
    communicationStyle: 10, seasonalContext: 5, negativeTriggers: 10, awarenessSignals: 5,
  }
  let score = 0
  for (const field of enrichmentFields) {
    if (fg[field] !== undefined && fg[field] !== null) {
      score += weights[field] || 0
    }
  }
  return score
}

// UI state
const showCreate = ref(false)
const showResearch = ref(false)
const showImport = ref(false)
const expandedCards = ref(new Set<string>())
const deleteTarget = ref<string | null>(null)
const showDeleteConfirm = ref(false)

function toggleExpand(id: string) {
  if (expandedCards.value.has(id)) {
    expandedCards.value.delete(id)
  } else {
    expandedCards.value.add(id)
  }
}

function isExpanded(id: string) {
  return expandedCards.value.has(id)
}

function onCreated() {
  showCreate.value = false
  toast.success('Focus group created!')
}

function onResearchCreated() {
  showResearch.value = false
}

function onImportCreated() {
  showImport.value = false
}

function promptDelete(id: string) {
  deleteTarget.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await removeFocusGroup({ id: deleteTarget.value as any })
    toast.success('Focus group deleted')
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (e: any) {
    toast.error(e.message || 'Failed to delete')
  }
}

const reviewUrl = computed(() => {
  if (!project.value?.slug || !productId.value) return '#'
  const base = `/projects/${project.value.slug}/products/${productId.value}/audiences/review`
  return latestTaskId.value ? `${base}?taskId=${latestTaskId.value}` : base
})
</script>

<template>
  <div>
    <VPageHeader title="Audiences" description="Target focus groups for this product">
      <template #actions>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors inline-flex items-center gap-1.5"
          @click="showResearch = true"
        >
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          Research Audiences
        </button>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors inline-flex items-center gap-1.5"
          @click="showImport = true"
        >
          <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
          Import Document
        </button>
        <button
          class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreate = true"
        >
          + Manual
        </button>
      </template>
    </VPageHeader>

    <!-- Active Jobs Banner -->
    <div v-if="hasActiveJob" class="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 animate-spin text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="text-sm text-blue-800">
          {{ activeTasks.length }} audience {{ activeTasks.length === 1 ? 'task' : 'tasks' }} running...
        </span>
      </div>
      <span class="text-xs text-blue-600">
        {{ activeTasks[0]?.title }}
      </span>
    </div>

    <!-- Pending Review Banner -->
    <div v-if="hasPendingReview && stagingSummary" class="mb-4 bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
        </svg>
        <span class="text-sm text-amber-800">
          {{ stagingSummary.pending }} focus group{{ stagingSummary.pending === 1 ? '' : 's' }} pending review
        </span>
      </div>
      <NuxtLink
        :to="reviewUrl"
        class="text-sm font-medium text-amber-700 hover:text-amber-900 underline"
      >
        Review &amp; Import
      </NuxtLink>
    </div>

    <!-- Overall Enrichment Progress -->
    <div v-if="focusGroups?.length" class="mb-4 rounded-lg border bg-card shadow-sm p-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-semibold text-foreground">Overall Enrichment Progress</h3>
        <span class="text-xs text-muted-foreground">{{ focusGroups.length }} focus group{{ focusGroups.length === 1 ? '' : 's' }}</span>
      </div>
      <EnrichmentProgressBar :score="overallEnrichmentScore" label="Enrichment Completeness" />
    </div>

    <div v-if="loading" class="text-muted-foreground">Loading...</div>

    <VEmptyState
      v-else-if="!focusGroups?.length"
      title="No focus groups yet"
      description="Define target audiences for better marketing."
    >
      <template #icon>
        <svg class="w-6 h-6 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
        </svg>
      </template>
      <button
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        @click="showCreate = true"
      >
        Add Focus Group
      </button>
    </VEmptyState>

    <div v-else class="space-y-4">
      <div
        v-for="fg in focusGroups"
        :key="fg._id"
        class="rounded-lg border bg-card shadow-sm overflow-hidden"
      >
        <!-- Card Header (always visible) -->
        <div
          class="p-4 cursor-pointer hover:bg-muted/50 transition-colors"
          @click="toggleExpand(fg._id)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary text-sm font-bold">
                {{ fg.number || '#' }}
              </span>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <NuxtLink
                    :to="`/projects/${project?.slug}/products/${productId}/audiences/${fg._id}`"
                    class="font-medium text-foreground hover:text-primary"
                    @click.stop
                  >
                    {{ fg.name }}
                  </NuxtLink>
                  <span class="text-xs text-muted-foreground/70">{{ fg.nickname }}</span>
                </div>
                <div class="flex items-center gap-2 mt-0.5">
                  <VStatusBadge :status="fg.category" size="sm" />
                  <span class="text-xs text-muted-foreground">{{ fg.source }}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <!-- Enrichment mini-bar -->
              <div class="w-20">
                <EnrichmentProgressBar :score="getFgEnrichmentScore(fg)" :show-percentage="false" />
              </div>
              <button
                class="p-1 text-red-400 hover:text-red-600 transition-colors"
                title="Delete"
                @click.stop="promptDelete(fg._id)"
              >
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
              </button>
              <svg
                class="w-4 h-4 text-muted-foreground/70 transition-transform"
                :class="{ 'rotate-180': isExpanded(fg._id) }"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </div>
          </div>
          <p class="text-sm text-muted-foreground mt-2 line-clamp-2">{{ fg.overview }}</p>
        </div>

        <!-- Expanded Details -->
        <div v-if="isExpanded(fg._id)" class="border-t px-4 py-4 space-y-4 bg-muted/50">
          <!-- Demographics -->
          <div v-if="fg.demographics">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Demographics</h5>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-muted-foreground">Age:</span>
                <span class="ml-1 text-foreground">{{ fg.demographics.ageRange }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Gender:</span>
                <span class="ml-1 text-foreground">{{ fg.demographics.gender }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Income:</span>
                <span class="ml-1 text-foreground">{{ fg.demographics.income }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Lifestyle:</span>
                <span class="ml-1 text-foreground">{{ fg.demographics.lifestyle }}</span>
              </div>
            </div>
            <div v-if="fg.demographics.triggers?.length" class="mt-2">
              <span class="text-xs text-muted-foreground">Triggers:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="t in fg.demographics.triggers" :key="t" class="bg-amber-50 text-amber-700 text-xs px-2 py-0.5 rounded-full">
                  {{ t }}
                </span>
              </div>
            </div>
          </div>

          <!-- Psychographics -->
          <div v-if="fg.psychographics">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Psychographics</h5>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-muted-foreground">Lifestyle:</span>
                <span class="ml-1 text-foreground">{{ fg.psychographics.lifestyle }}</span>
              </div>
              <div>
                <span class="text-muted-foreground">Identity:</span>
                <span class="ml-1 text-foreground">{{ fg.psychographics.identity }}</span>
              </div>
            </div>
            <div v-if="fg.psychographics.values?.length" class="mt-2">
              <span class="text-xs text-muted-foreground">Values:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="v in fg.psychographics.values" :key="v" class="bg-purple-50 text-purple-700 text-xs px-2 py-0.5 rounded-full">
                  {{ v }}
                </span>
              </div>
            </div>
          </div>

          <!-- Core Desires & Pain Points -->
          <div class="grid grid-cols-2 gap-4">
            <div v-if="fg.coreDesires?.length">
              <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Core Desires</h5>
              <div class="flex flex-wrap gap-1">
                <span v-for="d in fg.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">
                  {{ d }}
                </span>
              </div>
            </div>
            <div v-if="fg.painPoints?.length">
              <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Pain Points</h5>
              <div class="flex flex-wrap gap-1">
                <span v-for="p in fg.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">
                  {{ p }}
                </span>
              </div>
            </div>
          </div>

          <!-- Marketing Hooks -->
          <div v-if="fg.marketingHooks?.length">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Marketing Hooks</h5>
            <div class="flex flex-wrap gap-1">
              <span v-for="h in fg.marketingHooks" :key="h" class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full">
                {{ h }}
              </span>
            </div>
          </div>

          <!-- Language Patterns -->
          <div v-if="fg.languagePatterns?.length">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Language Patterns</h5>
            <div class="flex flex-wrap gap-1">
              <span v-for="l in fg.languagePatterns" :key="l" class="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                {{ l }}
              </span>
            </div>
          </div>

          <!-- Transformation Promise -->
          <div v-if="fg.transformationPromise">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Transformation Promise</h5>
            <p class="text-sm text-foreground italic">"{{ fg.transformationPromise }}"</p>
          </div>

          <!-- Enrichment Notes (read-only) -->
          <div v-if="fg.enrichmentNotes" class="pt-3 border-t">
            <h5 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Enrichment Notes</h5>
            <p class="text-xs text-muted-foreground">{{ fg.enrichmentNotes }}</p>
          </div>

          <!-- View Full Detail link -->
          <div class="pt-3 border-t">
            <NuxtLink
              :to="`/projects/${project?.slug}/products/${productId}/audiences/${fg._id}`"
              class="text-sm text-primary hover:text-primary font-medium"
            >
              View Full Details &amp; Enrichment History
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <VModal v-model="showCreate" title="New Focus Group" size="xl">
      <FocusGroupForm
        v-if="project"
        :project-id="project._id"
        :product-id="productId"
        @saved="onCreated"
      />
    </VModal>

    <!-- Research Dialog -->
    <AudienceResearchDialog
      v-if="project"
      v-model="showResearch"
      :project-id="project._id"
      :product-id="productId"
      :product="product"
      @created="onResearchCreated"
    />

    <!-- Import Dialog -->
    <AudienceImportDialog
      v-if="project"
      v-model="showImport"
      :project-id="project._id"
      :product-id="productId"
      @created="onImportCreated"
    />

    <!-- Delete Confirm -->
    <VConfirmDialog
      v-model="showDeleteConfirm"
      title="Delete Focus Group"
      message="Are you sure you want to delete this focus group? This action cannot be undone."
      confirm-label="Delete"
      confirm-class="bg-red-600 hover:bg-red-700"
      @confirm="confirmDelete"
    />
  </div>
</template>
