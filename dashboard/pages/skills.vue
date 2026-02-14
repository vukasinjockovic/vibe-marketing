<script setup lang="ts">
import { RefreshCw, Plus, Search, Pencil, FileText, Bot, Loader2 } from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

// Queries
const { data: groupedSkills, loading: skillsLoading } = useConvexQuery(api.skills.listGroupedByCategory, {})
const { data: categories } = useConvexQuery(api.skillCategories.list, {})
const { data: agentsWithSkills } = useConvexQuery(api.agents.listWithSkills, {})

const toast = useToast()

// State
const searchQuery = ref('')
const activeTab = ref('all')
const syncing = ref(false)
const lastSyncResult = ref<any>(null)
const showEditModal = ref(false)
const showBuildModal = ref(false)
const showViewModal = ref(false)
const selectedSkill = ref<any>(null)
const viewContent = ref('')
const viewLoading = ref(false)

// Sync
async function syncNow() {
  syncing.value = true
  try {
    const result = await $fetch('/api/skills/sync', { method: 'POST' })
    lastSyncResult.value = result
    toast.success(`Synced ${(result as any).synced} skills`)
  } catch (e: any) {
    toast.error(e.message || 'Sync failed')
  } finally {
    syncing.value = false
  }
}

// Filter tabs
const scopeTabs = computed(() => {
  const tabs = [{ key: 'all', label: 'All' }]
  if (categories.value) {
    // Group by scope
    const scopes = new Map<string, string>()
    for (const cat of categories.value) {
      if (cat.scope === 'copy') scopes.set('copy', 'Copy (L1-L5)')
      else if (cat.scope === 'research') scopes.set('research', 'Research')
      else if (cat.scope === 'visual') scopes.set('visual', 'Media')
      else if (cat.scope === 'quality') scopes.set('quality', 'Quality')
      else scopes.set('general', 'General')
    }
    for (const [key, label] of scopes) {
      tabs.push({ key, label })
    }
  }
  return tabs
})

// Filtered groups
const filteredGroups = computed(() => {
  if (!groupedSkills.value) return []
  return groupedSkills.value
    .map((group: any) => {
      // Filter by scope tab
      if (activeTab.value !== 'all') {
        const catScope = group.category.scope || 'general'
        if (catScope !== activeTab.value) return null
      }
      // Filter by search
      let skills = group.skills
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        skills = skills.filter((s: any) =>
          s.displayName.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.slug.toLowerCase().includes(q)
        )
      }
      if (skills.length === 0) return null
      return { ...group, skills }
    })
    .filter(Boolean)
})

// Stats
const totalSkills = computed(() => {
  if (!groupedSkills.value) return 0
  return groupedSkills.value.reduce((sum: number, g: any) => sum + g.skills.length, 0)
})

// Agent count per skill
function agentCount(skillId: string): number {
  if (!agentsWithSkills.value) return 0
  return agentsWithSkills.value.filter((a: any) =>
    a.staticSkillIds?.includes(skillId) || a.dynamicSkillIds?.includes(skillId)
  ).length
}

// Type badge styling
function typeBadge(type: string) {
  switch (type) {
    case 'mbook': return { label: 'Book', class: 'bg-purple-500/10 text-purple-400 border-purple-500/20' }
    case 'procedure': return { label: 'SOP', class: 'bg-blue-500/10 text-blue-400 border-blue-500/20' }
    case 'community': return { label: 'Community', class: 'bg-green-500/10 text-green-400 border-green-500/20' }
    default: return { label: 'Custom', class: 'bg-orange-500/10 text-orange-400 border-orange-500/20' }
  }
}

function syncBadge(status: string) {
  switch (status) {
    case 'synced': return { label: 'Synced', class: 'text-green-400' }
    case 'file_missing': return { label: 'Missing', class: 'text-red-400' }
    case 'pending_sync': return { label: 'Pending', class: 'text-yellow-400' }
    default: return { label: status, class: 'text-muted-foreground' }
  }
}

// Edit
function editSkill(skill: any) {
  selectedSkill.value = skill
  showEditModal.value = true
}

// View SKILL.md
async function viewSkillMd(skill: any) {
  selectedSkill.value = skill
  viewLoading.value = true
  showViewModal.value = true
  try {
    const res = await $fetch('/api/file-content', { params: { path: skill.filePath } })
    viewContent.value = typeof res === 'string' ? res : (res as any).content || ''
  } catch {
    viewContent.value = 'Failed to load SKILL.md'
  } finally {
    viewLoading.value = false
  }
}

function onSkillSaved() {
  showEditModal.value = false
  selectedSkill.value = null
  toast.success('Skill updated')
}
</script>

<template>
  <div>
    <VPageHeader title="Skills" description="Manage writing strategies, procedures, and agent capabilities">
      <template #actions>
        <button
          class="inline-flex items-center gap-2 rounded-md bg-muted px-3 py-2 text-sm font-medium text-foreground hover:bg-muted/80 transition-colors"
          :disabled="syncing"
          @click="syncNow"
        >
          <RefreshCw :size="16" :class="syncing ? 'animate-spin' : ''" />
          {{ syncing ? 'Syncing...' : 'Sync Now' }}
        </button>
        <button
          class="inline-flex items-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          @click="showBuildModal = true"
        >
          <Plus :size="16" />
          Build Skill
        </button>
      </template>
    </VPageHeader>

    <!-- Sync status bar -->
    <div v-if="lastSyncResult" class="mb-4 rounded-lg border bg-card px-4 py-2 text-sm text-muted-foreground flex flex-wrap items-center gap-x-4 gap-y-1">
      <span>{{ lastSyncResult.synced }} synced</span>
      <span>{{ lastSyncResult.unchanged }} unchanged</span>
      <span>{{ lastSyncResult.skipped }} excluded</span>
      <span v-if="lastSyncResult.missing > 0" class="text-destructive">{{ lastSyncResult.missing }} missing</span>
      <span v-if="lastSyncResult.errors?.length" class="text-destructive">{{ lastSyncResult.errors.length }} errors</span>
    </div>

    <!-- Search + tabs -->
    <div class="flex flex-wrap items-center gap-3 sm:gap-4 mb-6">
      <div class="relative flex-1 max-w-sm">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search skills..."
          class="w-full rounded-md border bg-background pl-9 pr-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>
      <div class="flex gap-1 rounded-lg bg-muted p-1 overflow-x-auto scrollbar-hide">
        <button
          v-for="tab in scopeTabs"
          :key="tab.key"
          class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors"
          :class="activeTab === tab.key
            ? 'bg-background text-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground'"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      <span class="text-sm text-muted-foreground">{{ totalSkills }} skills</span>
    </div>

    <!-- Loading -->
    <div v-if="skillsLoading" class="text-muted-foreground">Loading skills...</div>

    <!-- Empty state -->
    <VEmptyState
      v-else-if="filteredGroups.length === 0 && !searchQuery"
      title="No skills synced"
      description="Click 'Sync Now' to import skills from the filesystem."
    />

    <VEmptyState
      v-else-if="filteredGroups.length === 0 && searchQuery"
      title="No matching skills"
      :description="`No skills match '${searchQuery}'`"
    />

    <!-- Skills grouped by category -->
    <div v-else class="space-y-8">
      <div v-for="group in filteredGroups" :key="group.category.key">
        <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1 mb-3">
          <h2 class="text-lg font-semibold text-foreground">{{ group.category.displayName }}</h2>
          <span class="text-xs text-muted-foreground">({{ group.skills.length }})</span>
          <span class="text-sm text-muted-foreground hidden sm:inline">{{ group.category.description }}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="skill in group.skills"
            :key="skill._id"
            class="rounded-lg border bg-card text-card-foreground shadow-sm p-4 flex flex-col gap-2 hover:border-primary/30 transition-colors"
          >
            <!-- Header: name + type badge -->
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <h3 class="font-semibold text-foreground text-sm truncate">{{ skill.displayName }}</h3>
                <p v-if="skill.tagline" class="text-xs text-muted-foreground truncate">{{ skill.tagline }}</p>
              </div>
              <span
                class="shrink-0 inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium"
                :class="typeBadge(skill.type).class"
              >
                {{ typeBadge(skill.type).label }}
              </span>
            </div>

            <!-- Description -->
            <p class="text-xs text-muted-foreground line-clamp-2 flex-1">
              {{ skill.dashboardDescription || skill.description }}
            </p>

            <!-- Status pills -->
            <div class="flex items-center gap-2 flex-wrap">
              <span v-if="skill.isAutoActive" class="inline-flex items-center rounded-full bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 text-[10px] font-medium text-blue-400">
                Auto-active
              </span>
              <span v-if="skill.isCampaignSelectable" class="inline-flex items-center rounded-full bg-green-500/10 border border-green-500/20 px-2 py-0.5 text-[10px] font-medium text-green-400">
                Campaign
              </span>
              <span class="text-[10px]" :class="syncBadge(skill.syncStatus).class">
                {{ syncBadge(skill.syncStatus).label }}
              </span>
              <span v-if="agentCount(skill._id) > 0" class="inline-flex items-center gap-1 text-[10px] text-muted-foreground">
                <Bot :size="10" />
                {{ agentCount(skill._id) }}
              </span>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 pt-1 border-t border-border/50 mt-auto">
              <button
                class="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                @click="editSkill(skill)"
              >
                <Pencil :size="12" /> Edit
              </button>
              <button
                class="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                @click="viewSkillMd(skill)"
              >
                <FileText :size="12" /> SKILL.md
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <VModal v-model="showEditModal" title="Edit Skill" size="lg" persistent>
      <SkillForm
        v-if="selectedSkill"
        :skill="selectedSkill"
        :categories="categories || []"
        :agents="agentsWithSkills || []"
        @saved="onSkillSaved"
        @cancel="showEditModal = false"
      />
    </VModal>

    <!-- Build Wizard Modal -->
    <VModal v-model="showBuildModal" title="Build New Skill" size="xl" persistent>
      <SkillBuilderWizard
        :categories="categories || []"
        @close="showBuildModal = false"
      />
    </VModal>

    <!-- View SKILL.md Modal -->
    <VModal v-model="showViewModal" :title="selectedSkill?.displayName + ' — SKILL.md'" size="xl">
      <div v-if="viewLoading" class="flex items-center gap-2 text-muted-foreground py-8 justify-center">
        <Loader2 :size="16" class="animate-spin" /> Loading...
      </div>
      <pre v-else class="whitespace-pre-wrap text-xs text-foreground font-mono bg-muted/50 rounded-lg p-4 max-h-[60vh] overflow-y-auto">{{ viewContent }}</pre>
    </VModal>
  </div>
</template>
