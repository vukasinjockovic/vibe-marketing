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
          class="border border-gray-300 text-gray-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          @click="showResearch = true"
        >
          <span class="i-heroicons-magnifying-glass text-sm mr-1" />
          Research Audiences
        </button>
        <button
          class="border border-gray-300 text-gray-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          @click="showImport = true"
        >
          <span class="i-heroicons-document-arrow-up text-sm mr-1" />
          Import Document
        </button>
        <button
          class="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
          @click="showCreate = true"
        >
          + Manual
        </button>
      </template>
    </VPageHeader>

    <!-- Active Jobs Banner -->
    <div v-if="hasActiveJob" class="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="i-heroicons-arrow-path animate-spin text-blue-600" />
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
        <span class="i-heroicons-exclamation-triangle text-amber-600" />
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
    <div v-if="focusGroups?.length" class="mb-4 bg-white rounded-lg shadow p-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-semibold text-gray-900">Overall Enrichment Progress</h3>
        <span class="text-xs text-gray-500">{{ focusGroups.length }} focus group{{ focusGroups.length === 1 ? '' : 's' }}</span>
      </div>
      <EnrichmentProgressBar :score="overallEnrichmentScore" label="Enrichment Completeness" />
    </div>

    <div v-if="loading" class="text-gray-500">Loading...</div>

    <VEmptyState
      v-else-if="!focusGroups?.length"
      icon="i-heroicons-user-group"
      title="No focus groups yet"
      description="Define target audiences for better marketing."
    >
      <button
        class="inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
        @click="showCreate = true"
      >
        Add Focus Group
      </button>
    </VEmptyState>

    <div v-else class="space-y-4">
      <div
        v-for="fg in focusGroups"
        :key="fg._id"
        class="bg-white rounded-lg shadow overflow-hidden"
      >
        <!-- Card Header (always visible) -->
        <div
          class="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
          @click="toggleExpand(fg._id)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 text-sm font-bold">
                {{ fg.number || '#' }}
              </span>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <NuxtLink
                    :to="`/projects/${project?.slug}/products/${productId}/audiences/${fg._id}`"
                    class="font-medium text-gray-900 hover:text-primary-600"
                    @click.stop
                  >
                    {{ fg.name }}
                  </NuxtLink>
                  <span class="text-xs text-gray-400">{{ fg.nickname }}</span>
                </div>
                <div class="flex items-center gap-2 mt-0.5">
                  <VStatusBadge :status="fg.category" size="sm" />
                  <span class="text-xs text-gray-500">{{ fg.source }}</span>
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
                <span class="i-heroicons-trash text-sm" />
              </button>
              <span
                class="i-heroicons-chevron-down text-gray-400 transition-transform"
                :class="{ 'rotate-180': isExpanded(fg._id) }"
              />
            </div>
          </div>
          <p class="text-sm text-gray-600 mt-2 line-clamp-2">{{ fg.overview }}</p>
        </div>

        <!-- Expanded Details -->
        <div v-if="isExpanded(fg._id)" class="border-t px-4 py-4 space-y-4 bg-gray-50">
          <!-- Demographics -->
          <div v-if="fg.demographics">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Demographics</h5>
            <div class="grid grid-cols-4 gap-3 text-sm">
              <div>
                <span class="text-gray-500">Age:</span>
                <span class="ml-1 text-gray-900">{{ fg.demographics.ageRange }}</span>
              </div>
              <div>
                <span class="text-gray-500">Gender:</span>
                <span class="ml-1 text-gray-900">{{ fg.demographics.gender }}</span>
              </div>
              <div>
                <span class="text-gray-500">Income:</span>
                <span class="ml-1 text-gray-900">{{ fg.demographics.income }}</span>
              </div>
              <div>
                <span class="text-gray-500">Lifestyle:</span>
                <span class="ml-1 text-gray-900">{{ fg.demographics.lifestyle }}</span>
              </div>
            </div>
            <div v-if="fg.demographics.triggers?.length" class="mt-2">
              <span class="text-xs text-gray-500">Triggers:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="t in fg.demographics.triggers" :key="t" class="bg-amber-50 text-amber-700 text-xs px-2 py-0.5 rounded-full">
                  {{ t }}
                </span>
              </div>
            </div>
          </div>

          <!-- Psychographics -->
          <div v-if="fg.psychographics">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Psychographics</h5>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-gray-500">Lifestyle:</span>
                <span class="ml-1 text-gray-900">{{ fg.psychographics.lifestyle }}</span>
              </div>
              <div>
                <span class="text-gray-500">Identity:</span>
                <span class="ml-1 text-gray-900">{{ fg.psychographics.identity }}</span>
              </div>
            </div>
            <div v-if="fg.psychographics.values?.length" class="mt-2">
              <span class="text-xs text-gray-500">Values:</span>
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
              <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Core Desires</h5>
              <div class="flex flex-wrap gap-1">
                <span v-for="d in fg.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">
                  {{ d }}
                </span>
              </div>
            </div>
            <div v-if="fg.painPoints?.length">
              <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Pain Points</h5>
              <div class="flex flex-wrap gap-1">
                <span v-for="p in fg.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">
                  {{ p }}
                </span>
              </div>
            </div>
          </div>

          <!-- Marketing Hooks -->
          <div v-if="fg.marketingHooks?.length">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Marketing Hooks</h5>
            <div class="flex flex-wrap gap-1">
              <span v-for="h in fg.marketingHooks" :key="h" class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full">
                {{ h }}
              </span>
            </div>
          </div>

          <!-- Language Patterns -->
          <div v-if="fg.languagePatterns?.length">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Language Patterns</h5>
            <div class="flex flex-wrap gap-1">
              <span v-for="l in fg.languagePatterns" :key="l" class="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded-full">
                {{ l }}
              </span>
            </div>
          </div>

          <!-- Transformation Promise -->
          <div v-if="fg.transformationPromise">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Transformation Promise</h5>
            <p class="text-sm text-gray-900 italic">"{{ fg.transformationPromise }}"</p>
          </div>

          <!-- Enrichment Notes (read-only) -->
          <div v-if="fg.enrichmentNotes" class="pt-3 border-t">
            <h5 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Enrichment Notes</h5>
            <p class="text-xs text-gray-600">{{ fg.enrichmentNotes }}</p>
          </div>

          <!-- View Full Detail link -->
          <div class="pt-3 border-t">
            <NuxtLink
              :to="`/projects/${project?.slug}/products/${productId}/audiences/${fg._id}`"
              class="text-sm text-primary-600 hover:text-primary-700 font-medium"
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
