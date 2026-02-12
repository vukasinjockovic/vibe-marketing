<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../../../convex/_generated/api'
import { useAudienceJobs } from '../../../../composables/useAudienceJobs'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

const projectId = computed(() => project.value?._id)

const { data: focusGroups, loading } = useConvexQuery(
  api.focusGroups.listByProject,
  computed(() => projectId.value ? { projectId: projectId.value as any } : 'skip'),
)

const { mutate: removeFocusGroup } = useConvexMutation(api.focusGroups.remove)

// Audience jobs tracking (pass undefined for productId since project-level)
const { hasActiveJob, activeTasks, hasPendingReview, stagingSummary, latestTaskId } = useAudienceJobs(undefined)

// Enrichment progress for each focus group
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

// Search
const search = ref('')

const filteredFocusGroups = computed(() => {
  if (!focusGroups.value) return []
  const q = search.value.toLowerCase().trim()
  if (!q) return focusGroups.value
  return focusGroups.value.filter((fg: any) =>
    fg.name?.toLowerCase().includes(q)
    || fg.nickname?.toLowerCase().includes(q)
    || fg.category?.toLowerCase().includes(q)
    || fg.overview?.toLowerCase().includes(q)
    || fg.coreDesires?.some((d: string) => d.toLowerCase().includes(q))
    || fg.painPoints?.some((p: string) => p.toLowerCase().includes(q)),
  )
})

// UI state
const showCreate = ref(false)
const showResearch = ref(false)
const showImport = ref(false)
const expandedCards = ref(new Set<string>())
const deleteTarget = ref<string | null>(null)
const showDeleteConfirm = ref(false)
const showAuditTrail = ref(false)
const auditTrailFg = ref<any>(null)

function openAuditTrail(fg: any) {
  auditTrailFg.value = fg
  showAuditTrail.value = true
}

function formatAuditDate(ts: number) {
  return new Date(ts).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
  })
}

function confidenceColor(c: string) {
  if (c === 'high') return 'bg-green-100 text-green-700'
  if (c === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

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
  if (!project.value?.slug) return '#'
  const base = `/projects/${project.value.slug}/audiences/review`
  return latestTaskId.value ? `${base}?taskId=${latestTaskId.value}` : base
})
</script>

<template>
  <div>
    <VPageHeader title="Audiences" description="Target focus groups for this project">
      <template #actions>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors inline-flex items-center gap-1.5"
          @click="showResearch = true"
        >
          Research Audiences
        </button>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors inline-flex items-center gap-1.5"
          @click="showImport = true"
        >
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

    <!-- Search (visible when audiences exist) -->
    <div v-if="focusGroups?.length && !loading" class="mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Search audiences..."
        class="flex h-9 w-full max-w-sm rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      />
    </div>

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

    <!-- Staging Review Banner -->
    <div v-if="stagingSummary && stagingSummary.total > 0" class="mb-4 rounded-lg p-3 flex items-center justify-between"
      :class="stagingSummary.pending > 0 ? 'bg-amber-50 border border-amber-200' : stagingSummary.approved > 0 ? 'bg-green-50 border border-green-200' : 'bg-muted border border-border'"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm" :class="stagingSummary.pending > 0 ? 'text-amber-800' : 'text-foreground'">
          {{ stagingSummary.total }} staged
          <template v-if="stagingSummary.pending > 0"> — {{ stagingSummary.pending }} pending review</template>
          <template v-else-if="stagingSummary.approved > 0"> — {{ stagingSummary.approved }} approved, ready to import</template>
        </span>
      </div>
      <NuxtLink
        :to="reviewUrl"
        class="text-sm font-medium underline"
        :class="stagingSummary.pending > 0 ? 'text-amber-700 hover:text-amber-900' : 'text-primary hover:text-primary/80'"
      >
        {{ stagingSummary.pending > 0 ? 'Review & Import' : 'View Staging & Import' }}
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
      description="Define target audiences for better marketing. Research from scratch, import an existing document, or create manually."
    >
      <button
        class="inline-block bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
        @click="showCreate = true"
      >
        Add Focus Group
      </button>
    </VEmptyState>

    <template v-else>
      <div v-if="search && !filteredFocusGroups.length" class="text-sm text-muted-foreground py-8 text-center">
        No audiences matching "{{ search }}"
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="fg in filteredFocusGroups"
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
                    :to="`/projects/${project?.slug}/audiences/${fg._id}`"
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
                v-if="fg.enrichments?.length"
                class="p-1 text-muted-foreground/70 hover:text-foreground transition-colors"
                title="Audit Trail"
                @click.stop="openAuditTrail(fg)"
              >
                <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                </svg>
              </button>
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
            <div class="grid grid-cols-4 gap-3 text-sm">
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

          <!-- View Full Detail link -->
          <div class="pt-3 border-t">
            <NuxtLink
              :to="`/projects/${project?.slug}/audiences/${fg._id}`"
              class="text-sm text-primary hover:text-primary font-medium"
            >
              View Full Details &amp; Enrichment History
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
    </template>

    <!-- Create Modal -->
    <VModal v-model="showCreate" title="New Focus Group" size="xl">
      <FocusGroupForm
        v-if="project"
        :project-id="project._id"
        @saved="onCreated"
      />
    </VModal>

    <!-- Research Dialog -->
    <AudienceResearchDialog
      v-if="project"
      v-model="showResearch"
      :project-id="project._id"
      @created="onResearchCreated"
    />

    <!-- Import Dialog -->
    <AudienceImportDialog
      v-if="project"
      v-model="showImport"
      :project-id="project._id"
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

    <!-- Audit Trail Modal -->
    <VModal v-model="showAuditTrail" :title="`Enrichment History — ${auditTrailFg?.name || ''}`" size="lg">
      <div v-if="auditTrailFg?.enrichments?.length" class="space-y-0">
        <div class="text-xs text-muted-foreground mb-3">
          {{ auditTrailFg.enrichments.length }} enrichment{{ auditTrailFg.enrichments.length === 1 ? '' : 's' }}
          <span v-if="auditTrailFg.lastEnriched" class="ml-2">
            — last enriched {{ formatAuditDate(auditTrailFg.lastEnriched) }}
          </span>
        </div>

        <!-- Timeline -->
        <div class="relative pl-6 border-l-2 border-border space-y-4">
          <div
            v-for="(entry, idx) in [...auditTrailFg.enrichments].reverse()"
            :key="idx"
            class="relative"
          >
            <!-- Timeline dot -->
            <div class="absolute -left-[1.6rem] top-1 w-3 h-3 rounded-full border-2 border-background"
              :class="entry.confidence === 'high' ? 'bg-green-500' : entry.confidence === 'medium' ? 'bg-yellow-500' : 'bg-red-500'"
            />

            <div class="bg-muted/50 rounded-lg p-3 text-sm">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-foreground">{{ entry.field }}</span>
                  <span class="text-xs px-1.5 py-0.5 rounded-full" :class="confidenceColor(entry.confidence)">
                    {{ entry.confidence }}
                  </span>
                </div>
                <span class="text-xs text-muted-foreground/70">{{ formatAuditDate(entry.timestamp) }}</span>
              </div>

              <div class="flex items-center gap-2 text-xs text-muted-foreground mb-1.5">
                <span>by {{ entry.agentName }}</span>
                <span class="text-muted-foreground/40">via {{ entry.source }}</span>
              </div>

              <!-- Value change -->
              <div v-if="entry.previousValue" class="flex items-start gap-2 text-xs mt-1">
                <span class="bg-red-50 text-red-600 px-1.5 py-0.5 rounded line-through shrink-0">{{ entry.previousValue.slice(0, 80) }}</span>
                <span class="text-muted-foreground/40">-></span>
                <span class="bg-green-50 text-green-600 px-1.5 py-0.5 rounded shrink-0">{{ entry.newValue.slice(0, 80) }}</span>
              </div>
              <div v-else class="text-xs mt-1">
                <span class="bg-green-50 text-green-600 px-1.5 py-0.5 rounded">{{ entry.newValue.slice(0, 120) }}</span>
              </div>

              <!-- Reasoning -->
              <p v-if="entry.reasoning" class="text-xs text-muted-foreground/80 mt-1.5 italic">
                {{ entry.reasoning }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-muted-foreground/70 text-center py-8 text-sm">
        No enrichment history available.
      </div>
    </VModal>
  </div>
</template>
