<script setup lang="ts">
import { RefreshCw, Search, Filter } from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

// Load all services grouped by category
const { data: grouped, loading, refresh } = useConvexQuery(api.services.listAllGrouped, {})
const { data: serviceStats } = useConvexQuery(api.services.stats, {})

const { mutate: doToggle } = useConvexMutation(api.services.toggleActive)
const toast = useToast()
const client = useConvex()

// Sync state
const syncing = ref(false)

// Filter/search
const searchQuery = ref('')
const filterMode = ref<'all' | 'active' | 'free'>('all')

// Config dialog
const configService = ref<any>(null)
const configOpen = ref(false)

const filteredGroups = computed(() => {
  if (!grouped.value) return []

  return grouped.value
    .map((group: any) => {
      let services = group.services || []

      // Filter by active/free
      if (filterMode.value === 'active') {
        services = services.filter((s: any) => s.isActive)
      } else if (filterMode.value === 'free') {
        services = services.filter((s: any) => s.freeTier)
      }

      // Search
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        services = services.filter((s: any) =>
          s.displayName.toLowerCase().includes(q) ||
          s.name.toLowerCase().includes(q) ||
          s.description?.toLowerCase().includes(q)
        )
      }

      return { ...group, services }
    })
    .filter((group: any) => group.services.length > 0 || (!searchQuery.value && filterMode.value === 'all'))
})

async function toggleActive(svc: any) {
  try {
    await doToggle({ id: svc._id })
    toast.success(`${svc.displayName} ${svc.isActive ? 'deactivated' : 'activated'}`)
  } catch (e: any) {
    toast.error(e.message || 'Failed to update service')
  }
}

function openConfig(svc: any) {
  configService.value = svc
  configOpen.value = true
}

async function syncPlugins() {
  syncing.value = true
  try {
    const res = await $fetch('/api/sync-services', { method: 'POST' })
    if (res.success) {
      toast.success(res.summary || 'Plugins synced successfully')
    } else {
      toast.error(res.error || 'Sync failed')
    }
  } catch (e: any) {
    toast.error(e.message || 'Sync request failed')
  } finally {
    syncing.value = false
  }
}
</script>

<template>
  <div>
    <VPageHeader title="Service Registry" description="Manage external service integrations and fallback chains">
      <template #actions>
        <button
          class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md border hover:bg-muted transition-colors disabled:opacity-50"
          :disabled="syncing"
          @click="syncPlugins"
        >
          <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': syncing }" />
          {{ syncing ? 'Syncing...' : 'Sync Plugins' }}
        </button>
      </template>
    </VPageHeader>

    <!-- Stats bar -->
    <div v-if="serviceStats" class="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-foreground">{{ serviceStats.total }}</div>
        <div class="text-xs text-muted-foreground">Total</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-green-600">{{ serviceStats.active }}</div>
        <div class="text-xs text-muted-foreground">Active</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-yellow-600">{{ serviceStats.degraded }}</div>
        <div class="text-xs text-muted-foreground">Degraded</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-muted-foreground">{{ serviceStats.inactive }}</div>
        <div class="text-xs text-muted-foreground">Inactive</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-emerald-600">{{ serviceStats.freeTier }}</div>
        <div class="text-xs text-muted-foreground">Free Tier</div>
      </div>
    </div>

    <!-- Search + Filter bar -->
    <div class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search services..."
          class="w-full pl-9 pr-3 py-2 rounded-md border bg-background text-sm"
        />
      </div>
      <div class="flex gap-1 rounded-md border p-0.5">
        <button
          v-for="mode in (['all', 'active', 'free'] as const)"
          :key="mode"
          class="px-3 py-1.5 text-xs font-medium rounded capitalize transition-colors"
          :class="filterMode === mode ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'"
          @click="filterMode = mode"
        >
          {{ mode }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-muted-foreground py-8 text-center">Loading services...</div>

    <!-- Category cards -->
    <div v-else class="space-y-4">
      <ServiceCategoryCard
        v-for="group in filteredGroups"
        :key="group._id"
        :category="group"
        :services="group.services"
        @toggle="toggleActive"
        @configure="openConfig"
        @reordered="() => {}"
      />

      <div v-if="filteredGroups.length === 0" class="text-center py-12 text-muted-foreground">
        <p v-if="searchQuery || filterMode !== 'all'">No services match your filters.</p>
        <p v-else>No services found. Click "Sync Plugins" to discover available services.</p>
      </div>
    </div>

    <!-- Config dialog -->
    <ServiceConfigDialog
      :service="configService"
      :open="configOpen"
      @close="configOpen = false"
      @updated="() => {}"
    />
  </div>
</template>
