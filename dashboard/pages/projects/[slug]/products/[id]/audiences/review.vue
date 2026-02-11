<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../../../../../../../convex/_generated/api'
import { useAudienceJobs } from '../../../../../../composables/useAudienceJobs'

const route = useRoute()
const toast = useToast()
const { project } = useCurrentProject()

const productId = computed(() => route.params.id as string)

// Get taskId from query param or from latest audience job
const queryTaskId = computed(() => route.query.taskId as string | undefined)
const { latestTaskId: autoTaskId } = useAudienceJobs(productId)
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
    default: return 'bg-gray-100 text-gray-600'
  }
}

function completenessColor(score: number) {
  if (score >= 80) return 'text-green-600'
  if (score >= 50) return 'text-yellow-600'
  return 'text-red-600'
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
        class="text-sm text-gray-500 hover:text-gray-700"
      >
        <span class="i-heroicons-arrow-left text-sm mr-1" />
        Back to Audiences
      </NuxtLink>
    </div>

    <VPageHeader title="Review Staged Audiences" description="Review and approve parsed focus groups before importing">
      <template #actions>
        <button
          class="border border-gray-300 text-gray-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          @click="approveAllNew"
        >
          Approve All New
        </button>
        <button
          class="border border-gray-300 text-gray-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          @click="approveAll"
        >
          Approve All
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
    <div v-if="stagingSummary" class="mb-6 bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-5 gap-4 text-center">
        <div>
          <p class="text-2xl font-bold text-gray-900">{{ stagingSummary.total }}</p>
          <p class="text-xs text-gray-500">Total</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-600">{{ stagingSummary.pending }}</p>
          <p class="text-xs text-gray-500">Pending</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-green-600">{{ stagingSummary.approved }}</p>
          <p class="text-xs text-gray-500">Approved</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-red-600">{{ stagingSummary.rejected }}</p>
          <p class="text-xs text-gray-500">Rejected</p>
        </div>
        <div>
          <p class="text-2xl font-bold text-amber-600">{{ stagingSummary.needsEnrichment }}</p>
          <p class="text-xs text-gray-500">Needs Enrichment</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-gray-500">Loading staging records...</div>

    <VEmptyState
      v-else-if="!taskId"
      icon="i-heroicons-document-magnifying-glass"
      title="No staging task found"
      description="Start a research or import task to populate staging records."
    />

    <VEmptyState
      v-else-if="!stagingRecords?.length"
      icon="i-heroicons-inbox"
      title="No staged records"
      description="The task has not produced any staging records yet."
    />

    <template v-else>
      <!-- New Groups Section -->
      <div v-if="newGroups.length" class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span class="i-heroicons-plus-circle text-green-500" />
          New Groups
          <span class="text-sm font-normal text-gray-500">({{ newGroups.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in newGroups"
            :key="record._id"
            class="bg-white rounded-lg shadow overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-gray-900">{{ record.name }}</h4>
                  <span class="text-xs text-gray-400">{{ record.nickname || '' }}</span>
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
                    @click="approve(record._id)"
                  >
                    Approve
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    @click="reject(record._id)"
                  >
                    Reject
                  </button>
                  <button
                    class="px-2 py-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
                    @click="togglePreview(record._id)"
                  >
                    {{ isPreviewExpanded(record._id) ? 'Collapse' : 'Preview' }}
                  </button>
                </div>
              </div>
              <p v-if="record.overview" class="text-sm text-gray-600 mt-1 line-clamp-2">{{ record.overview }}</p>
              <div v-if="record.missingFields?.length" class="mt-2">
                <span class="text-xs text-gray-500">Missing:</span>
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
            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-gray-50 space-y-3 text-sm">
              <div v-if="record.demographics" class="grid grid-cols-4 gap-2">
                <div><span class="text-gray-500">Age:</span> {{ record.demographics.ageRange }}</div>
                <div><span class="text-gray-500">Gender:</span> {{ record.demographics.gender }}</div>
                <div><span class="text-gray-500">Income:</span> {{ record.demographics.income }}</div>
                <div><span class="text-gray-500">Lifestyle:</span> {{ record.demographics.lifestyle }}</div>
              </div>
              <div v-if="record.coreDesires?.length">
                <span class="text-xs text-gray-500">Core Desires:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="d in record.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">{{ d }}</span>
                </div>
              </div>
              <div v-if="record.painPoints?.length">
                <span class="text-xs text-gray-500">Pain Points:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="p in record.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">{{ p }}</span>
                </div>
              </div>
              <div v-if="record.marketingHooks?.length">
                <span class="text-xs text-gray-500">Marketing Hooks:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="h in record.marketingHooks" :key="h" class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full">{{ h }}</span>
                </div>
              </div>
              <div v-if="record.transformationPromise">
                <span class="text-xs text-gray-500">Transformation:</span>
                <p class="italic text-gray-900">"{{ record.transformationPromise }}"</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enrichment Matches Section -->
      <div v-if="enrichmentMatches.length" class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span class="i-heroicons-arrow-path text-blue-500" />
          Enrichment Matches
          <span class="text-sm font-normal text-gray-500">({{ enrichmentMatches.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in enrichmentMatches"
            :key="record._id"
            class="bg-white rounded-lg shadow overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-gray-900">{{ record.name }}</h4>
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
                    @click="approve(record._id)"
                  >
                    Approve Merge
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                    @click="reject(record._id)"
                  >
                    Reject
                  </button>
                  <button
                    class="px-2 py-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
                    @click="togglePreview(record._id)"
                  >
                    {{ isPreviewExpanded(record._id) ? 'Collapse' : 'Preview' }}
                  </button>
                </div>
              </div>
              <p v-if="record.matchReason" class="text-sm text-gray-500 mt-1">{{ record.matchReason }}</p>
            </div>

            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-gray-50 space-y-2 text-sm">
              <p v-if="record.overview" class="text-gray-700">{{ record.overview }}</p>
              <div v-if="record.coreDesires?.length">
                <span class="text-xs text-gray-500">New Core Desires:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="d in record.coreDesires" :key="d" class="bg-green-50 text-green-700 text-xs px-2 py-0.5 rounded-full">{{ d }}</span>
                </div>
              </div>
              <div v-if="record.painPoints?.length">
                <span class="text-xs text-gray-500">New Pain Points:</span>
                <div class="flex flex-wrap gap-1 mt-1">
                  <span v-for="p in record.painPoints" :key="p" class="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">{{ p }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Possible Matches Section -->
      <div v-if="possibleMatches.length" class="mb-8">
        <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <span class="i-heroicons-question-mark-circle text-amber-500" />
          Possible Matches
          <span class="text-sm font-normal text-gray-500">({{ possibleMatches.length }})</span>
        </h3>
        <div class="space-y-3">
          <div
            v-for="record in possibleMatches"
            :key="record._id"
            class="bg-white rounded-lg shadow overflow-hidden"
          >
            <div class="p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <h4 class="font-medium text-gray-900">{{ record.name }}</h4>
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
                    @click="approve(record._id)"
                  >
                    Create as New
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    @click="approve(record._id)"
                  >
                    Merge
                  </button>
                  <button
                    v-if="record.reviewStatus === 'pending_review'"
                    class="px-3 py-1 text-xs text-gray-600 border rounded-md hover:bg-gray-50 transition-colors"
                    @click="reject(record._id)"
                  >
                    Skip
                  </button>
                  <button
                    class="px-2 py-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
                    @click="togglePreview(record._id)"
                  >
                    {{ isPreviewExpanded(record._id) ? 'Collapse' : 'Preview' }}
                  </button>
                </div>
              </div>
              <p v-if="record.matchReason" class="text-sm text-gray-500 mt-1">{{ record.matchReason }}</p>
            </div>

            <div v-if="isPreviewExpanded(record._id)" class="border-t p-4 bg-gray-50 space-y-2 text-sm">
              <p v-if="record.overview" class="text-gray-700">{{ record.overview }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Import Button -->
      <div class="mt-8 flex justify-center">
        <button
          class="bg-primary-600 text-white px-6 py-3 rounded-lg text-sm font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50"
          :disabled="importing || !stagingSummary?.approved"
          @click="importAllApproved"
        >
          {{ importing ? 'Importing...' : `Import All Approved (${stagingSummary?.approved || 0})` }}
        </button>
      </div>
    </template>
  </div>
</template>
