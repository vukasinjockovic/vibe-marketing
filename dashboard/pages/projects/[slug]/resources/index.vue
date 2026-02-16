<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'
import { Filter } from 'lucide-vue-next'

const { project } = useCurrentProject()
const projectId = computed(() => project.value?._id)
const router = useRouter()
const route = useRoute()
const slug = computed(() => route.params.slug as string)

// Filters synced with URL query
const selectedType = computed({
  get: () => (route.query.resources_type as string) || '',
  set: (v: string) => {
    router.replace({ query: { ...route.query, resources_type: v || undefined, resources_page: undefined } })
  },
})
const selectedStatus = computed({
  get: () => (route.query.resources_status as string) || '',
  set: (v: string) => {
    router.replace({ query: { ...route.query, resources_status: v || undefined, resources_page: undefined } })
  },
})

const resourceTypes = [
  { value: '', label: 'All Types' },
  { value: 'research_material', label: 'Research' },
  { value: 'brief', label: 'Briefs' },
  { value: 'article', label: 'Articles' },
  { value: 'landing_page', label: 'Landing Pages' },
  { value: 'ad_copy', label: 'Ad Copy' },
  { value: 'social_post', label: 'Social Posts' },
  { value: 'email_sequence', label: 'Email Sequences' },
  { value: 'email_excerpt', label: 'Email Excerpts' },
  { value: 'image_prompt', label: 'Image Prompts' },
  { value: 'image', label: 'Images' },
  { value: 'video_script', label: 'Video Scripts' },
  { value: 'lead_magnet', label: 'Lead Magnets' },
  { value: 'report', label: 'Reports' },
  { value: 'brand_asset', label: 'Brand Assets' },
]

const statuses = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'in_review', label: 'In Review' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'humanized', label: 'Humanized' },
  { value: 'approved', label: 'Approved' },
  { value: 'published', label: 'Published' },
  { value: 'archived', label: 'Archived' },
]

// Search query
const searchQuery = ref('')

// Use search query when filters are active, otherwise use list query
const queryArgs = computed(() => {
  if (!projectId.value) return 'skip'
  if (searchQuery.value || selectedType.value || selectedStatus.value) {
    return {
      projectId: projectId.value,
      titleQuery: searchQuery.value || undefined,
      resourceType: selectedType.value || undefined,
      status: selectedStatus.value || undefined,
      paginationOpts: { numItems: 200 },
    }
  }
  return { projectId: projectId.value }
})

const useSearchMode = computed(() => {
  return !!(searchQuery.value || selectedType.value || selectedStatus.value)
})

const { data: searchResults } = useConvexQuery(
  api.resources.search,
  computed(() => useSearchMode.value ? queryArgs.value : 'skip'),
)

const { data: listResults } = useConvexQuery(
  api.resources.listByProject,
  computed(() => !useSearchMode.value && projectId.value ? { projectId: projectId.value, paginationOpts: { numItems: 200 } } : 'skip'),
)

const allResources = computed(() => {
  if (useSearchMode.value) return searchResults.value?.page || []
  return listResults.value?.page || []
})

// Client-side pagination synced with URL query
const perPage = 25
const currentPage = computed({
  get: () => {
    const p = Number(route.query.resources_page)
    return p > 0 ? p : 1
  },
  set: (v: number) => {
    router.replace({ query: { ...route.query, resources_page: v > 1 ? String(v) : undefined } })
  },
})
const totalPages = computed(() => Math.max(1, Math.ceil(allResources.value.length / perPage)))
const resources = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return allResources.value.slice(start, start + perPage)
})

// Reset page when search query changes (type/status setters already reset page)
watch(searchQuery, () => { currentPage.value = 1 })

// Resource detail modal
const selectedResourceId = ref<string | null>(null)
const showResourceModal = computed({
  get: () => !!selectedResourceId.value,
  set: (v: boolean) => { if (!v) selectedResourceId.value = null },
})

function handleSelect(resource: any) {
  selectedResourceId.value = resource._id
}
</script>

<template>
  <div class="space-y-6">
    <!-- Stats -->
    <ResourceStatsCards v-if="projectId" :project-id="projectId" />

    <!-- Filters bar -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3">
      <div class="flex items-center gap-2 text-sm text-muted-foreground shrink-0">
        <Filter :size="14" />
        Filters:
      </div>

      <div class="flex flex-wrap items-center gap-3 flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by title..."
          class="h-9 px-3 text-sm rounded-md border bg-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary w-full sm:w-auto sm:min-w-[180px]"
        />

        <select
          v-model="selectedType"
          class="h-9 px-2 text-sm rounded-md border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option v-for="t in resourceTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>

        <select
          v-model="selectedStatus"
          class="h-9 px-2 text-sm rounded-md border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>

      <span class="text-xs text-muted-foreground sm:ml-auto shrink-0">
        {{ allResources.length }} resource{{ allResources.length !== 1 ? 's' : '' }}
      </span>
    </div>

    <!-- Resource table (inline since we have custom data source) -->
    <div class="rounded-lg border bg-card shadow-sm overflow-x-auto">
      <div v-if="resources.length === 0" class="p-8 text-center text-muted-foreground">
        No resources found
      </div>

      <table v-else class="w-full min-w-[600px]">
        <thead>
          <tr class="border-b text-left text-sm text-muted-foreground">
            <th class="px-4 py-3 font-medium">Resource</th>
            <th class="px-4 py-3 font-medium">Type</th>
            <th class="px-4 py-3 font-medium">Status</th>
            <th class="px-4 py-3 font-medium">Created By</th>
            <th class="px-4 py-3 font-medium">Created</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in resources"
            :key="r._id"
            class="border-b last:border-0 hover:bg-muted/50 cursor-pointer transition-colors"
            @click="handleSelect(r)"
          >
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <ResourceTypeIcon :type="r.resourceType" :size="16" />
                <span class="font-medium text-sm text-foreground">{{ r.title }}</span>
              </div>
              <p v-if="r.slug" class="text-xs text-muted-foreground mt-0.5">{{ r.slug }}</p>
            </td>
            <td class="px-4 py-3">
              <span class="text-xs text-muted-foreground capitalize">{{ r.resourceType.replace(/_/g, ' ') }}</span>
            </td>
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="{
                  'bg-gray-100 text-gray-700': r.status === 'draft',
                  'bg-blue-100 text-blue-700': r.status === 'in_review',
                  'bg-amber-100 text-amber-700': r.status === 'reviewed',
                  'bg-teal-100 text-teal-700': r.status === 'humanized',
                  'bg-emerald-100 text-emerald-700': r.status === 'approved',
                  'bg-green-100 text-green-700': r.status === 'published',
                  'bg-muted text-muted-foreground': r.status === 'archived',
                }"
              >
                {{ r.status.replace('_', ' ') }}
              </span>
            </td>
            <td class="px-4 py-3 text-xs text-muted-foreground">{{ r.createdBy }}</td>
            <td class="px-4 py-3 text-xs text-muted-foreground">{{ new Date(r.createdAt).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t flex items-center justify-between">
        <span class="text-xs text-muted-foreground">
          Showing {{ (currentPage - 1) * perPage + 1 }}–{{ Math.min(currentPage * perPage, allResources.length) }} of {{ allResources.length }}
        </span>
        <div class="flex items-center gap-1">
          <button
            :disabled="currentPage <= 1"
            class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            @click="currentPage--"
          >
            Prev
          </button>
          <span class="text-xs text-muted-foreground px-2">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            :disabled="currentPage >= totalPages"
            class="px-2 py-1 text-xs rounded border border-border text-muted-foreground hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            @click="currentPage++"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Resource detail modal -->
    <VModal v-model="showResourceModal" title="Resource Detail" size="xl">
      <div class="-mx-6 -my-4">
        <ResourceDetailPanel
          v-if="selectedResourceId"
          :resource-id="selectedResourceId"
          @navigate="(id: string) => { selectedResourceId = id }"
        />
      </div>
      <template #footer>
        <div class="flex items-center justify-between w-full">
          <NuxtLink
            v-if="selectedResourceId"
            :to="`/projects/${slug}/resources/${selectedResourceId}`"
            class="text-sm text-primary hover:underline"
          >
            Open Full Page
          </NuxtLink>
          <button
            class="px-3 py-1.5 text-sm rounded-md border border-border text-muted-foreground hover:bg-muted transition-colors"
            @click="showResourceModal = false"
          >
            Close
          </button>
        </div>
      </template>
    </VModal>
  </div>
</template>
