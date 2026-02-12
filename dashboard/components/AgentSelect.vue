<script setup lang="ts">
import {
  Users, Search, Microscope, Sparkles, FileSearch,
  PenTool, ShieldCheck, UserCheck, Repeat, Share2,
  Mail, Megaphone, Layout, Image, ImagePlus,
  Video, BookOpen, Bot, ChevronDown, X, Check,
} from 'lucide-vue-next'
import { api } from '../../convex/_generated/api'

const model = defineModel<string>({ default: '' })

const props = defineProps<{
  placeholder?: string
}>()

const { data: agents } = useConvexQuery(api.agents.list, {})

const iconMap: Record<string, any> = {
  'vibe-audience-parser': Users,
  'vibe-audience-researcher': Search,
  'vibe-audience-enricher': Sparkles,
  'vibe-keyword-researcher': FileSearch,
  'vibe-serp-analyzer': Microscope,
  'vibe-content-writer': PenTool,
  'vibe-content-reviewer': ShieldCheck,
  'vibe-humanizer': UserCheck,
  'vibe-content-repurposer': Repeat,
  'vibe-social-writer': Share2,
  'vibe-email-writer': Mail,
  'vibe-ad-writer': Megaphone,
  'vibe-landing-page-writer': Layout,
  'vibe-image-director': Image,
  'vibe-image-generator': ImagePlus,
  'vibe-script-writer': Video,
  'vibe-ebook-writer': BookOpen,
  'vibe-orchestrator': Bot,
}

const open = ref(false)
const searchQuery = ref('')
const dropdownRef = ref<HTMLElement | null>(null)
const searchRef = ref<HTMLInputElement | null>(null)

const filteredAgents = computed(() => {
  const list = agents.value || []
  if (!searchQuery.value) return list
  const q = searchQuery.value.toLowerCase()
  return list.filter((a: any) =>
    a.name.toLowerCase().includes(q) ||
    a.displayName?.toLowerCase().includes(q) ||
    a.role?.toLowerCase().includes(q)
  )
})

const selectedAgent = computed(() => {
  if (!model.value || !agents.value) return null
  return agents.value.find((a: any) => a.name === model.value)
})

function select(agentName: string) {
  model.value = agentName
  open.value = false
  searchQuery.value = ''
}

function clear() {
  model.value = ''
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    nextTick(() => searchRef.value?.focus())
  }
}

function onClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    open.value = false
    searchQuery.value = ''
  }
}

onMounted(() => document.addEventListener('click', onClickOutside, true))
onUnmounted(() => document.removeEventListener('click', onClickOutside, true))
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- Trigger button -->
    <button
      type="button"
      class="w-full border border-input rounded-md px-3 py-2 text-sm bg-background ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 flex items-center gap-2 text-left"
      @click="toggle"
    >
      <template v-if="selectedAgent">
        <component
          :is="iconMap[selectedAgent.name] || Bot"
          :size="16"
          class="text-primary shrink-0"
        />
        <span class="flex-1 truncate text-foreground">{{ selectedAgent.displayName || selectedAgent.name }}</span>
        <button
          type="button"
          class="text-muted-foreground hover:text-foreground shrink-0"
          @click.stop="clear"
        >
          <X :size="14" />
        </button>
      </template>
      <template v-else>
        <Bot :size="16" class="text-muted-foreground shrink-0" />
        <span class="flex-1 text-muted-foreground">{{ placeholder || 'Select agent...' }}</span>
        <ChevronDown :size="14" class="text-muted-foreground shrink-0" />
      </template>
    </button>

    <!-- Dropdown -->
    <div
      v-if="open"
      class="absolute left-0 top-full mt-1 w-full min-w-[340px] rounded-lg border bg-popover text-popover-foreground shadow-lg z-50"
    >
      <!-- Search -->
      <div class="p-2 border-b">
        <div class="flex items-center gap-2 px-2 py-1.5 rounded-md bg-muted/50">
          <Search :size="14" class="text-muted-foreground shrink-0" />
          <input
            ref="searchRef"
            v-model="searchQuery"
            type="text"
            placeholder="Search agents..."
            class="flex-1 bg-transparent text-sm focus:outline-none placeholder:text-muted-foreground/70"
          />
        </div>
      </div>

      <!-- Agent list -->
      <div class="max-h-64 overflow-y-auto p-1">
        <div
          v-if="filteredAgents.length === 0"
          class="px-3 py-4 text-center text-sm text-muted-foreground"
        >
          No agents found
        </div>
        <button
          v-for="agent in filteredAgents"
          :key="agent.name"
          type="button"
          class="w-full flex items-start gap-3 px-3 py-2.5 rounded-md text-left transition-colors"
          :class="model === agent.name ? 'bg-primary/10' : 'hover:bg-muted'"
          @click="select(agent.name)"
        >
          <div
            class="w-8 h-8 rounded-md flex items-center justify-center shrink-0 mt-0.5"
            :class="model === agent.name ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'"
          >
            <component :is="iconMap[agent.name] || Bot" :size="16" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-foreground">{{ agent.displayName || agent.name }}</span>
              <Check v-if="model === agent.name" :size="14" class="text-primary shrink-0" />
            </div>
            <p v-if="agent.role" class="text-xs text-muted-foreground line-clamp-2 mt-0.5">
              {{ agent.role }}
            </p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
