<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../../../convex/_generated/api'
import { useAudienceJobs } from '../../../../composables/useAudienceJobs'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

// Get taskId from query param or from latest audience job
const queryTaskId = computed(() => route.query.taskId as string | undefined)
const { latestTaskId: autoTaskId } = useAudienceJobs(undefined)
const taskId = computed(() => queryTaskId.value || autoTaskId.value)

// Fetch staging records for the task
const { data: stagingRecords, loading } = useConvexQuery(
  api.focusGroupStaging.listByTask,
  computed(() => taskId.value ? { taskId: taskId.value as any } : 'skip'),
)

const { data: stagingSummary } = useConvexQuery(
  api.focusGroupStaging.getSummary,
  computed(() => taskId.value ? { taskId: taskId.value as any } : 'skip'),
)

const { mutate: updateReviewStatus } = useConvexMutation(api.focusGroupStaging.updateReviewStatus)
const { mutate: bulkApprove } = useConvexMutation(api.focusGroupStaging.bulkApprove)
const { mutate: bulkReject } = useConvexMutation(api.focusGroupStaging.bulkReject)
const { mutate: importApproved } = useConvexMutation(api.focusGroups.importFromStaging)

// Group records by matchStatus
const newGroups = computed(() =>
  (stagingRecords.value || []).filter((r: any) => r.matchStatus === 'create_new'),
)
const enrichmentMatches = computed(() =>
  (stagingRecords.value || []).filter((r: any) => r.matchStatus === 'enrich_existing'),
)
const possibleMatches = computed(() =>
  (stagingRecords.value || []).filter((r: any) => r.matchStatus === 'possible_match'),
)

// Preview expansion
const expandedPreviews = ref(new Set<string>())

function togglePreview(id: string) {
  if (expandedPreviews.value.has(id)) {
    expandedPreviews.value.delete(id)
  } else {
    expandedPreviews.value.add(id)
  }
}

function isPreviewExpanded(id: string) {
  return expandedPreviews.value.has(id)
}

// Actions
async function approve(id: string) {
  try {
    await updateReviewStatus({ id: id as any, reviewStatus: 'approved' })
    toast.success('Approved')
  } catch (e: any) {
    toast.error(e.message || 'Failed to approve')
  }
}

async function reject(id: string) {
  try {
    await updateReviewStatus({ id: id as any, reviewStatus: 'rejected' })
    toast.info('Rejected')
  } catch (e: any) {
    toast.error(e.message || 'Failed to reject')
  }
}

async function approveAllNew() {
  const ids = newGroups.value
    .filter((r: any) => r.reviewStatus === 'pending_review')
    .map((r: any) => r._id)
  if (!ids.length) return
  try {
    await bulkApprove({ ids: ids as any })
    toast.success(`Approved ${ids.length} new groups`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to bulk approve')
  }
}

async function approveAll() {
  const ids = (stagingRecords.value || [])
    .filter((r: any) => r.reviewStatus === 'pending_review')
    .map((r: any) => r._id)
  if (!ids.length) return
  try {
    await bulkApprove({ ids: ids as any })
    toast.success(`Approved ${ids.length} records`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to bulk approve')
  }
}

async function rejectRemaining() {
  const ids = (stagingRecords.value || [])
    .filter((r: any) => r.reviewStatus === 'pending_review')
    .map((r: any) => r._id)
  if (!ids.length) return
  try {
    await bulkReject({ ids: ids as any })
    toast.info(`Rejected ${ids.length} remaining records`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to bulk reject')
  }
}

const importing = ref(false)

async function importAllApproved() {
  const approvedIds = (stagingRecords.value || [])
    .filter((r: any) => r.reviewStatus === 'approved' || r.reviewStatus === 'edited')
    .map((r: any) => r._id)
  if (!approvedIds.length) {
    toast.warning('No approved records to import')
    return
  }
  importing.value = true
  try {
    await importApproved({ stagingIds: approvedIds as any })
    toast.success(`Imported ${approvedIds.length} focus groups!`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to import')
  } finally {
    importing.value = false
  }
}

function reviewStatusColor(status: string) {
  switch (status) {
    case 'approved': return 'bg-green-100 text-green-700'
    case 'rejected': return 'bg-red-100 text-red-700'
    case 'edited': return 'bg-blue-100 text-blue-700'
    case 'imported': return 'bg-purple-100 text-purple-700'
    default: return 'bg-muted text-muted-foreground'
  }
}

function completenessColor(score: number) {
  if (score >= 80) return 'text-green-600'
  if (score >= 50) return 'text-yellow-600'
  return 'text-red-600'
}

function hasEnrichmentData(record: any): boolean {
  return !!(record.awarenessStage || record.sophisticationLevel ||
    record.purchaseBehavior || record.contentPreferences ||
    record.influenceSources || record.competitorContext ||
    record.communicationStyle || record.seasonalContext || record.negativeTriggers)
}

function awarenessLabel(stage: string): string {
  const labels: Record<string, string> = {
    unaware: 'Unaware',
    problem_aware: 'Problem Aware',
    solution_aware: 'Solution Aware',
    product_aware: 'Product Aware',
    most_aware: 'Most Aware',
  }
  return labels[stage] || stage
}

function sophLabel(stage: string): string {
  const labels: Record<string, string> = {
    stage1: '1 — First to Market',
    stage2: '2 — Enlarged Claims',
    stage3: '3 — Mechanism',
    stage4: '4 — Specific Mechanism',
    stage5: '5 — Proof & Identification',
  }
  return labels[stage] || stage
}

const backUrl = computed(() => {
  if (!project.value?.slug) return '#'
  return `/projects/${project.value.slug}/audiences`
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

    <VPageHeader title="Review Staged Audiences" description="Review and approve parsed focus groups before importing">
      <template #actions>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors"
          @click="approveAllNew"
        >
          Approve All New
        </button>
        <button
          class="border border-border text-muted-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-muted/50 transition-colors"
          @click="approveAll"
        >
          Approve All
        </button>
        <button
          v-if="stagingSummary?.approved"
          class="bg-primary text-primary-foreground px-3 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="importing"
          @click="importAllApproved"
        >
          {{ importing ? 'Importing...' : `Import (${stagingSummary.approved})` }}
        </button>
        <button
          class="border border-red-200 text-red-600 px-3 py-2 rounded-md text-sm font-medium hover:bg-red-50 transition-colors"
          @click="rejectRemaining"
        >
          Reject Remaining
        </button>
      </template>
    </VPageHeader>

    <!-- Summary Bar -->
    <div v-if="stagingSummary" class="mb-6 rounded-lg border bg-card shadow-sm p-4">
      <div class="grid grid-cols-5 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-foreground">{{ stagingSummary.total }}</p>
          <p class="text-xs text-muted-foreground">Total</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-muted-foreground">{{ stagingSummary.pending }}</p>
          <p class="text-xs text-muted-foreground">Pending</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-green-600">{{ stagingSummary.approved }}</p>
          <p class="text-xs text-muted-foreground">Approved</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-red-600">{{ stagingSummary.rejected }}</p>
          <p class="text-xs text-muted-foreground">Rejected</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-amber-600">{{ stagingSummary.needsEnrichment }}</p>
          <p class="text-xs text-muted-foreground">Needs Enrichment</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-muted-foreground">Loading staging records...</div>

    <VEmptyState
      v-else-if="!taskId"
      title="No staging task found"
      description="Start a research or import task to populate staging records."
    />

    <VEmptyState
      v-else-if="!stagingRecords?.length"
      title="No staged records"
      description="The task has not produced any staging records yet."
    />

    <template v-else>
      <!-- New Groups Section -->
      <div v-if="newGroups.length" class="mb-8">
        <h3 class="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          New Groups
          <span class="text-sm font-normal text-muted-foreground">({{ newGroups.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in newGroups"
            :key="record._id"
            class="rounded-lg border bg-card shadow-sm overflow-hidden"
          >
            <div class="p-4 cursor-pointer hover:bg-muted/30 transition-colors" @click="togglePreview(record._id)">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-foreground">{{ record.name }}</h4>
                  <span class="text-xs text-muted-foreground/60">{{ record.nickname || '' }}</span>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :class="reviewStatusColor(record.reviewStatus)"
                  >
                    {{ record.reviewStatus.replace(/_/g, ' ') }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <span :class="completenessColor(record.completenessScore)" class="text-sm font-medium">
                    {{ record.completenessScore }}%
                  </span>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    @click.stop="approve(record._id)"
                  >
                    Approve
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    @click.stop="reject(record._id)"
                  >
                    Reject
                  </button>
                  <span class="text-xs text-muted-foreground/60">
                    {{ isPreviewExpanded(record._id) ? '▲' : '▼' }}
                  </span>
                </div>
              </div>
              <p v-if="record.overview" class="text-sm text-muted-foreground mt-1 line-clamp-2">{{ record.overview }}</p>
              <div v-if="record.missingFields?.length" class="mt-2">
                <span class="text-xs text-muted-foreground">Missing:</span>
                <span
                  v-for="f in record.missingFields"
                  :key="f"
                  class="text-xs text-red-500 ml-1"
                >
                  {{ f }},
                </span>
              </div>
            </div>

            <!-- Preview Expansion -->
            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-muted/50 space-y-3 text-sm">
              <div v-if="record.demographics" class="grid grid-cols-4 gap-2">
                <div><span class="text-muted-foreground">Age:</span> {{ record.demographics.ageRange }}</div>
                <div><span class="text-muted-foreground">Gender:</span> {{ record.demographics.gender }}</div>
                <div><span class="text-muted-foreground">Income:</span> {{ record.demographics.income }}</div>
                <div><span class="text-muted-foreground">Lifestyle:</span> {{ record.demographics.lifestyle }}</div>
              </div>
              <div v-if="record.coreDesires?.length">
                <span class="text-xs text-muted-foreground">Core Desires:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="d in record.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">{{ d }}</span>
                </div>
              </div>
              <div v-if="record.painPoints?.length">
                <span class="text-xs text-muted-foreground">Pain Points:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="p in record.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">{{ p }}</span>
                </div>
              </div>
              <div v-if="record.marketingHooks?.length">
                <span class="text-xs text-muted-foreground">Marketing Hooks:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="h in record.marketingHooks" :key="h" class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full">{{ h }}</span>
                </div>
              </div>
              <div v-if="record.transformationPromise">
                <span class="text-xs text-muted-foreground">Transformation:</span>
                <p class="italic text-foreground">"{{ record.transformationPromise }}"</p>
              </div>

              <!-- Parser-only fields -->
              <div v-if="record.fears?.length">
                <span class="text-xs text-muted-foreground">Fears:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="f in record.fears" :key="f" class="bg-orange-50 text-orange-700 text-xs px-2 py-0.5 rounded-full">{{ f }}</span>
                </div>
              </div>
              <div v-if="record.objections?.length">
                <span class="text-xs text-muted-foreground">Objections:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="o in record.objections" :key="o" class="bg-amber-50 text-amber-700 text-xs px-2 py-0.5 rounded-full">{{ o }}</span>
                </div>
              </div>
              <div v-if="record.emotionalTriggers?.length">
                <span class="text-xs text-muted-foreground">Emotional Triggers:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="t in record.emotionalTriggers" :key="t" class="bg-pink-50 text-pink-700 text-xs px-2 py-0.5 rounded-full">{{ t }}</span>
                </div>
              </div>
              <div v-if="record.languagePatterns?.length">
                <span class="text-xs text-muted-foreground">Language Patterns:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="l in record.languagePatterns" :key="l" class="bg-violet-50 text-violet-700 text-xs px-2 py-0.5 rounded-full">{{ l }}</span>
                </div>
              </div>
              <div v-if="record.psychographics">
                <span class="text-xs text-muted-foreground">Psychographics:</span>
                <div class="grid grid-cols-2 gap-2 mt-1">
                  <div v-if="record.psychographics.identity"><span class="text-muted-foreground">Identity:</span> {{ record.psychographics.identity }}</div>
                  <div v-if="record.psychographics.lifestyle"><span class="text-muted-foreground">Lifestyle:</span> {{ record.psychographics.lifestyle }}</div>
                  <div v-if="record.psychographics.values?.length" class="col-span-2">
                    <span class="text-muted-foreground">Values:</span>
                    <span v-for="val in record.psychographics.values" :key="val" class="ml-1 bg-cyan-50 text-cyan-700 text-xs px-2 py-0.5 rounded-full">{{ val }}</span>
                  </div>
                </div>
              </div>

              <!-- Enrichment Data -->
              <template v-if="hasEnrichmentData(record)">
                <div class="border-t border-border pt-3 mt-3">
                  <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Enrichment Data</span>
                </div>

                <div v-if="record.awarenessStage || record.sophisticationLevel" class="grid grid-cols-2 gap-4">
                  <div v-if="record.awarenessStage">
                    <span class="text-xs text-muted-foreground">Awareness Stage:</span>
                    <div class="flex items-center gap-1.5 mt-0.5">
                      <span class="font-medium text-foreground">{{ awarenessLabel(record.awarenessStage) }}</span>
                      <span v-if="record.awarenessConfidence" class="text-xs px-1.5 py-0.5 rounded-full"
                        :class="{ 'bg-green-100 text-green-700': record.awarenessConfidence === 'high', 'bg-yellow-100 text-yellow-700': record.awarenessConfidence === 'medium', 'bg-red-100 text-red-700': record.awarenessConfidence === 'low' }"
                      >{{ record.awarenessConfidence }}</span>
                    </div>
                  </div>
                  <div v-if="record.sophisticationLevel">
                    <span class="text-xs text-muted-foreground">Market Sophistication:</span>
                    <p class="font-medium text-foreground mt-0.5">{{ sophLabel(record.sophisticationLevel) }}</p>
                  </div>
                </div>

                <div v-if="record.awarenessSignals" class="text-xs text-muted-foreground/80">
                  <span class="text-muted-foreground">Signals:</span>
                  <span v-if="record.awarenessSignals.beliefsSignal" class="ml-1">Beliefs: {{ record.awarenessSignals.beliefsSignal }}</span>
                  <span v-if="record.awarenessSignals.languageSignal" class="ml-2">Language: {{ record.awarenessSignals.languageSignal }}</span>
                </div>

                <div v-if="record.purchaseBehavior" class="grid grid-cols-3 gap-2">
                  <div v-if="record.purchaseBehavior.priceRange">
                    <span class="text-xs text-muted-foreground">Price Range:</span>
                    <p class="text-foreground">{{ record.purchaseBehavior.priceRange }}</p>
                  </div>
                  <div v-if="record.purchaseBehavior.decisionProcess">
                    <span class="text-xs text-muted-foreground">Decision Process:</span>
                    <p class="text-foreground">{{ record.purchaseBehavior.decisionProcess }}</p>
                  </div>
                  <div v-if="record.purchaseBehavior.buyingTriggers?.length">
                    <span class="text-xs text-muted-foreground">Buying Triggers:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="t in record.purchaseBehavior.buyingTriggers" :key="t" class="bg-emerald-50 text-emerald-700 text-xs px-1.5 py-0.5 rounded-full">{{ t }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="record.contentPreferences" class="grid grid-cols-3 gap-2">
                  <div v-if="record.contentPreferences.attentionSpan">
                    <span class="text-xs text-muted-foreground">Attention Span:</span>
                    <p class="text-foreground">{{ record.contentPreferences.attentionSpan }}</p>
                  </div>
                  <div v-if="record.contentPreferences.tonePreference">
                    <span class="text-xs text-muted-foreground">Tone Preference:</span>
                    <p class="text-foreground">{{ record.contentPreferences.tonePreference }}</p>
                  </div>
                  <div v-if="record.contentPreferences.preferredFormats?.length">
                    <span class="text-xs text-muted-foreground">Preferred Formats:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="f in record.contentPreferences.preferredFormats" :key="f" class="bg-sky-50 text-sky-700 text-xs px-1.5 py-0.5 rounded-full">{{ f }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="record.influenceSources">
                  <div v-if="record.influenceSources.trustedVoices?.length">
                    <span class="text-xs text-muted-foreground">Trusted Voices:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="v in record.influenceSources.trustedVoices" :key="v" class="bg-purple-50 text-purple-700 text-xs px-1.5 py-0.5 rounded-full">{{ v }}</span>
                    </div>
                  </div>
                  <div v-if="record.influenceSources.socialPlatforms?.length" class="mt-1">
                    <span class="text-xs text-muted-foreground">Social Platforms:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="s in record.influenceSources.socialPlatforms" :key="s" class="bg-blue-50 text-blue-700 text-xs px-1.5 py-0.5 rounded-full">{{ s }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="record.competitorContext">
                  <div v-if="record.competitorContext.currentSolutions?.length">
                    <span class="text-xs text-muted-foreground">Current Solutions:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="c in record.competitorContext.currentSolutions" :key="c" class="bg-slate-100 text-slate-700 text-xs px-1.5 py-0.5 rounded-full">{{ c }}</span>
                    </div>
                  </div>
                  <div v-if="record.competitorContext.switchMotivators?.length" class="mt-1">
                    <span class="text-xs text-muted-foreground">Switch Motivators:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="m in record.competitorContext.switchMotivators" :key="m" class="bg-teal-50 text-teal-700 text-xs px-1.5 py-0.5 rounded-full">{{ m }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="record.communicationStyle" class="grid grid-cols-4 gap-2">
                  <div v-if="record.communicationStyle.formalityLevel">
                    <span class="text-xs text-muted-foreground">Formality:</span>
                    <p class="text-foreground">{{ record.communicationStyle.formalityLevel }}</p>
                  </div>
                  <div v-if="record.communicationStyle.humorReceptivity">
                    <span class="text-xs text-muted-foreground">Humor:</span>
                    <p class="text-foreground">{{ record.communicationStyle.humorReceptivity }}</p>
                  </div>
                  <div v-if="record.communicationStyle.storyPreference">
                    <span class="text-xs text-muted-foreground">Stories:</span>
                    <p class="text-foreground">{{ record.communicationStyle.storyPreference }}</p>
                  </div>
                  <div v-if="record.communicationStyle.dataPreference">
                    <span class="text-xs text-muted-foreground">Data:</span>
                    <p class="text-foreground">{{ record.communicationStyle.dataPreference }}</p>
                  </div>
                </div>

                <div v-if="record.negativeTriggers">
                  <div v-if="record.negativeTriggers.dealBreakers?.length">
                    <span class="text-xs text-muted-foreground">Deal Breakers:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="d in record.negativeTriggers.dealBreakers" :key="d" class="bg-red-50 text-red-600 text-xs px-1.5 py-0.5 rounded-full">{{ d }}</span>
                    </div>
                  </div>
                  <div v-if="record.negativeTriggers.toneAversions?.length" class="mt-1">
                    <span class="text-xs text-muted-foreground">Tone Aversions:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="a in record.negativeTriggers.toneAversions" :key="a" class="bg-rose-50 text-rose-600 text-xs px-1.5 py-0.5 rounded-full">{{ a }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="record.seasonalContext">
                  <div v-if="record.seasonalContext.peakInterestPeriods?.length">
                    <span class="text-xs text-muted-foreground">Peak Periods:</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <span v-for="p in record.seasonalContext.peakInterestPeriods" :key="p" class="bg-amber-50 text-amber-700 text-xs px-1.5 py-0.5 rounded-full">{{ p }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Enrichment Matches Section -->
      <div v-if="enrichmentMatches.length" class="mb-8">
        <h3 class="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          Enrichment Matches
          <span class="text-sm font-normal text-muted-foreground">({{ enrichmentMatches.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in enrichmentMatches"
            :key="record._id"
            class="rounded-lg border bg-card shadow-sm overflow-hidden"
          >
            <div class="p-4 cursor-pointer hover:bg-muted/30 transition-colors" @click="togglePreview(record._id)">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-foreground">{{ record.name }}</h4>
                  <span class="text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                    Match: {{ Math.round((record.matchConfidence || 0) * 100) }}%
                  </span>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :class="reviewStatusColor(record.reviewStatus)"
                  >
                    {{ record.reviewStatus.replace(/_/g, ' ') }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    @click.stop="approve(record._id)"
                  >
                    Approve Merge
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    @click.stop="reject(record._id)"
                  >
                    Reject
                  </button>
                  <span class="text-xs text-muted-foreground/60">
                    {{ isPreviewExpanded(record._id) ? '▲' : '▼' }}
                  </span>
                </div>
              </div>
              <p v-if="record.matchReason" class="text-sm text-muted-foreground mt-1">{{ record.matchReason }}</p>
            </div>

            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-muted/50 space-y-2 text-sm">
              <p v-if="record.overview" class="text-muted-foreground">{{ record.overview }}</p>
              <div v-if="record.coreDesires?.length">
                <span class="text-xs text-muted-foreground">New Core Desires:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="d in record.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">{{ d }}</span>
                </div>
              </div>
              <div v-if="record.painPoints?.length">
                <span class="text-xs text-muted-foreground">New Pain Points:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="p in record.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">{{ p }}</span>
                </div>
              </div>
              <!-- Enrichment summary for merge candidates -->
              <template v-if="hasEnrichmentData(record)">
                <div class="border-t border-border pt-2 mt-2">
                  <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Enrichment</span>
                </div>
                <div v-if="record.awarenessStage || record.sophisticationLevel" class="grid grid-cols-2 gap-2">
                  <div v-if="record.awarenessStage">
                    <span class="text-xs text-muted-foreground">Awareness:</span>
                    <span class="font-medium text-foreground ml-1">{{ awarenessLabel(record.awarenessStage) }}</span>
                  </div>
                  <div v-if="record.sophisticationLevel">
                    <span class="text-xs text-muted-foreground">Sophistication:</span>
                    <span class="font-medium text-foreground ml-1">{{ sophLabel(record.sophisticationLevel) }}</span>
                  </div>
                </div>
                <div v-if="record.purchaseBehavior?.priceRange">
                  <span class="text-xs text-muted-foreground">Price Range:</span>
                  <span class="text-foreground ml-1">{{ record.purchaseBehavior.priceRange }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Possible Matches Section -->
      <div v-if="possibleMatches.length" class="mb-8">
        <h3 class="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
          Possible Matches
          <span class="text-sm font-normal text-muted-foreground">({{ possibleMatches.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in possibleMatches"
            :key="record._id"
            class="rounded-lg border bg-card shadow-sm overflow-hidden"
          >
            <div class="p-4 cursor-pointer hover:bg-muted/30 transition-colors" @click="togglePreview(record._id)">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-foreground">{{ record.name }}</h4>
                  <span class="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                    Similarity: {{ Math.round((record.matchConfidence || 0) * 100) }}%
                  </span>
                  <span
                    class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :class="reviewStatusColor(record.reviewStatus)"
                  >
                    {{ record.reviewStatus.replace(/_/g, ' ') }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                    @click.stop="approve(record._id)"
                  >
                    Create as New
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs text-muted-foreground border rounded-md hover:bg-muted/50 transition-colors"
                    @click.stop="reject(record._id)"
                  >
                    Skip
                  </button>
                  <span class="text-xs text-muted-foreground/60">
                    {{ isPreviewExpanded(record._id) ? '▲' : '▼' }}
                  </span>
                </div>
              </div>
              <p v-if="record.matchReason" class="text-sm text-muted-foreground mt-1">{{ record.matchReason }}</p>
            </div>

            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-muted/50 space-y-2 text-sm">
              <p v-if="record.overview" class="text-muted-foreground">{{ record.overview }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Import Button -->
      <div class="mt-8 flex justify-center">
        <button
          class="bg-primary text-primary-foreground px-6 py-3 rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
          :disabled="importing || !stagingSummary?.approved"
          @click="importAllApproved"
        >
          {{ importing ? 'Importing...' : `Import All Approved (${stagingSummary?.approved || 0})` }}
        </button>
      </div>
    </template>
  </div>
</template>
