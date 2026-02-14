<script setup lang="ts">
import { Plus, Search, GitBranch, Layers, Users, MessageSquare, ArrowRight, Copy, Bot } from 'lucide-vue-next'
import { api } from '../../../convex/_generated/api'

const { data: pipelines, loading } = useConvexQuery(api.pipelines.list, {})
const { mutate: forkPipeline } = useConvexMutation(api.pipelines.fork)
const toast = useToast()

const forking = ref<string | null>(null)
const showCreate = ref(false)
const searchQuery = ref('')
const filterCategory = ref<'all' | 'sales' | 'engagement' | 'audience'>('all')
const filterType = ref<'all' | 'preset' | 'custom'>('all')

const categories = [
  { value: 'all', label: 'All', icon: Layers },
  { value: 'sales', label: 'Sales', icon: ArrowRight },
  { value: 'engagement', label: 'Engagement', icon: MessageSquare },
  { value: 'audience', label: 'Audience', icon: Users },
] as const

const categoryMeta: Record<string, { color: string; bg: string; icon: string; label: string }> = {
  sales: { color: 'text-blue-700', bg: 'bg-blue-100', icon: '💰', label: 'Sales' },
  engagement: { color: 'text-purple-700', bg: 'bg-purple-100', icon: '💬', label: 'Engagement' },
  audience: { color: 'text-emerald-700', bg: 'bg-emerald-100', icon: '👥', label: 'Audience' },
}

const filteredPipelines = computed(() => {
  if (!pipelines.value) return []

  return pipelines.value.filter((p: any) => {
    if (filterCategory.value !== 'all' && p.category !== filterCategory.value) return false
    if (filterType.value !== 'all' && p.type !== filterType.value) return false
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      if (!p.name.toLowerCase().includes(q) && !p.description?.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const stats = computed(() => {
  if (!pipelines.value) return { total: 0, sales: 0, engagement: 0, audience: 0, preset: 0, custom: 0 }
  return {
    total: pipelines.value.length,
    sales: pipelines.value.filter((p: any) => p.category === 'sales').length,
    engagement: pipelines.value.filter((p: any) => p.category === 'engagement').length,
    audience: pipelines.value.filter((p: any) => p.category === 'audience').length,
    preset: pipelines.value.filter((p: any) => p.type === 'preset').length,
    custom: pipelines.value.filter((p: any) => p.type === 'custom').length,
  }
})

function totalAgents(p: any) {
  const mainAgents = new Set((p.mainSteps || []).filter((s: any) => s.agent).map((s: any) => s.agent))
  const branchAgents = (p.parallelBranches || []).filter((b: any) => b.agent).map((b: any) => b.agent)
  branchAgents.forEach((a: string) => mainAgents.add(a))
  return mainAgents.size
}

async function fork(p: any) {
  forking.value = p._id
  try {
    const newSlug = `${p.slug}-copy-${Date.now().toString(36)}`
    await forkPipeline({
      pipelineId: p._id,
      newName: `${p.name} (Copy)`,
      newSlug: newSlug,
    })
    toast.success('Pipeline forked successfully!')
  } catch (e: any) {
    toast.error(e.message || 'Failed to fork pipeline')
  } finally {
    forking.value = null
  }
}

function onCreated(slug: string) {
  showCreate.value = false
  navigateTo(`/pipelines/${slug}`)
}
</script>

<template>
  <div>
    <VPageHeader title="Pipelines" description="Content production pipeline templates and custom forks">
      <template #actions>
        <button
          class="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="showCreate = true"
        >
          <Plus :size="16" />
          Create Pipeline
        </button>
      </template>
    </VPageHeader>

    <!-- Stats -->
    <div v-if="!loading && pipelines?.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-foreground">{{ stats.total }}</div>
        <div class="text-xs text-muted-foreground">Total</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-blue-600">{{ stats.sales }}</div>
        <div class="text-xs text-muted-foreground">Sales</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-purple-600">{{ stats.engagement }}</div>
        <div class="text-xs text-muted-foreground">Engagement</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-emerald-600">{{ stats.audience }}</div>
        <div class="text-xs text-muted-foreground">Audience</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-muted-foreground">{{ stats.preset }}</div>
        <div class="text-xs text-muted-foreground">Preset</div>
      </div>
      <div class="rounded-lg border bg-card px-4 py-3">
        <div class="text-2xl font-bold text-muted-foreground">{{ stats.custom }}</div>
        <div class="text-xs text-muted-foreground">Custom</div>
      </div>
    </div>

    <!-- Search + Filters -->
    <div v-if="!loading && pipelines?.length" class="flex flex-col sm:flex-row gap-3 mb-6">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search pipelines..."
          class="w-full pl-9 pr-3 py-2 rounded-md border bg-background text-sm"
        />
      </div>

      <!-- Category filter -->
      <div class="flex gap-1 rounded-md border p-0.5">
        <button
          v-for="cat in categories"
          :key="cat.value"
          class="px-3 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1.5"
          :class="filterCategory === cat.value
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground'"
          @click="filterCategory = cat.value"
        >
          {{ cat.label }}
        </button>
      </div>

      <!-- Type filter -->
      <div class="flex gap-1 rounded-md border p-0.5">
        <button
          v-for="t in ['all', 'preset', 'custom']"
          :key="t"
          class="px-3 py-1.5 text-xs font-medium rounded capitalize transition-colors"
          :class="filterType === t
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground'"
          @click="filterType = t as any"
        >
          {{ t }}
        </button>
      </div>
    </div>

    <!-- Create modal -->
    <VModal v-model="showCreate" title="Create Pipeline" size="xl">
      <PipelineForm
        @saved="onCreated"
        @cancelled="showCreate = false"
      />
    </VModal>

    <div v-if="loading" class="text-muted-foreground py-8 text-center">Loading pipelines...</div>

    <VEmptyState
      v-else-if="!pipelines?.length"
      title="No pipelines"
      description="Pipeline templates will appear here once created."
    >
      <button
        class="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
        @click="showCreate = true"
      >
        <Plus :size="16" />
        Create Pipeline
      </button>
    </VEmptyState>

    <div v-else-if="filteredPipelines.length === 0" class="text-center py-12 text-muted-foreground">
      No pipelines match your filters.
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <NuxtLink
        v-for="p in filteredPipelines"
        :key="p._id"
        :to="`/pipelines/${p.slug}`"
        class="group rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md hover:border-primary/30 transition-all flex flex-col"
      >
        <div class="p-5 flex flex-col flex-1">
          <!-- Top row: category badge + type badge -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span
                v-if="p.category && categoryMeta[p.category]"
                class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full"
                :class="[categoryMeta[p.category].bg, categoryMeta[p.category].color]"
              >
                {{ categoryMeta[p.category].icon }} {{ categoryMeta[p.category].label }}
              </span>
              <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-muted text-muted-foreground">
                Uncategorized
              </span>
            </div>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              :class="p.type === 'preset'
                ? 'bg-sky-100 text-sky-700'
                : 'bg-amber-100 text-amber-700'"
            >
              {{ p.type }}
            </span>
          </div>

          <!-- Name -->
          <h3 class="font-semibold text-foreground group-hover:text-primary transition-colors mb-1 line-clamp-1">
            {{ p.name }}
          </h3>

          <!-- Description -->
          <p v-if="p.description" class="text-sm text-muted-foreground mb-4 line-clamp-2">
            {{ p.description }}
          </p>

          <!-- Step flow visualization -->
          <div class="flex flex-wrap items-center gap-y-1.5 mb-4">
            <template v-for="(s, i) in (p.mainSteps || [])" :key="i">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap"
                :class="p.category === 'engagement'
                  ? 'bg-purple-50 text-purple-700 border border-purple-200'
                  : p.category === 'audience'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-blue-50 text-blue-700 border border-blue-200'"
              >
                {{ s.label }}
              </span>
              <svg
                v-if="i < (p.mainSteps || []).length - 1"
                class="w-4 h-4 text-muted-foreground/40 shrink-0 mx-0.5"
                viewBox="0 0 16 16"
                fill="none"
              >
                <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
          </div>

          <!-- Bottom stats row -->
          <div class="flex items-center justify-between pt-3 border-t border-border/50 mt-auto">
            <div class="flex items-center gap-4 text-xs text-muted-foreground">
              <span class="flex items-center gap-1" :title="'Main steps'">
                <Layers :size="12" />
                {{ (p.mainSteps || []).length }} steps
              </span>
              <span v-if="p.parallelBranches?.length" class="flex items-center gap-1" :title="'Parallel branches'">
                <GitBranch :size="12" />
                {{ p.parallelBranches.length }}
              </span>
              <span class="flex items-center gap-1" :title="'Unique agents'">
                <Bot :size="12" />
                {{ totalAgents(p) }}
              </span>
            </div>
            <button
              class="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground font-medium px-2 py-1 rounded hover:bg-muted transition-colors"
              :disabled="forking === p._id"
              @click.prevent="fork(p)"
            >
              <Copy :size="12" />
              {{ forking === p._id ? 'Forking...' : 'Fork' }}
            </button>
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
