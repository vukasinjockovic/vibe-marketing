<script setup lang="ts">
import { api } from '../../convex/_generated/api'
import {
  FileText, Clock, User, Hash, FolderOpen,
  AlertTriangle, ExternalLink,
} from 'lucide-vue-next'
import {
  resolveContentSource,
  getFileExtension,
  isTextFile,
  buildFileUrl,
} from '../composables/useResourceContent'

const props = defineProps<{
  resourceId: any
}>()

const emit = defineEmits<{
  navigate: [resourceId: string]
  close: []
}>()

const { data: resource, loading } = useConvexQuery(
  api.resources.get,
  computed(() => props.resourceId ? { id: props.resourceId } : 'skip'),
)

const activeTab = ref('content')
const tabs = ['content', 'metadata', 'relationships', 'history', 'file']

const { parse } = useMarkdown()

// Monaco language mapping
const monacoLanguage = computed(() => {
  if (!resource.value) return 'markdown'
  const filePath = resource.value.filePath || ''
  const ext = filePath.split('.').pop()?.toLowerCase() || ''
  const map: Record<string, string> = {
    md: 'markdown', json: 'json', js: 'javascript', ts: 'typescript',
    py: 'python', sh: 'shell', yaml: 'yaml', yml: 'yaml',
    vue: 'html', jsx: 'javascript', tsx: 'typescript',
    html: 'html', css: 'css', csv: 'plaintext', txt: 'plaintext',
  }
  return map[ext] || 'markdown'
})

// --- Content resolution: DB content OR load from disk ---
const contentSource = computed(() => {
  if (!resource.value) return { source: 'none' as const, value: '' }
  return resolveContentSource(resource.value)
})

const fileContent = ref<string | null>(null)
const fileLoading = ref(false)

async function loadFileContent() {
  if (!resource.value?.filePath) return
  if (contentSource.value.source !== 'file') return
  const ext = getFileExtension(resource.value.filePath)
  if (!isTextFile(ext)) return

  fileLoading.value = true
  try {
    const url = buildFileUrl(resource.value.filePath, 'text')
    const response = await $fetch<{ content: string }>(url)
    fileContent.value = response.content
  } catch {
    fileContent.value = null
  } finally {
    fileLoading.value = false
  }
}

// Load file content when resource changes
watch(() => resource.value?._id, () => {
  fileContent.value = null
  if (resource.value && contentSource.value.source === 'file') {
    loadFileContent()
  }
}, { immediate: true })

// The actual text to display in Monaco (DB content or file content)
const displayContent = computed(() => {
  if (contentSource.value.source === 'db') return contentSource.value.value
  if (fileContent.value) return fileContent.value
  return null
})

const parsed = computed(() => {
  if (!displayContent.value) return null
  return parse(displayContent.value)
})

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  in_review: 'bg-blue-100 text-blue-700',
  reviewed: 'bg-amber-100 text-amber-700',
  humanized: 'bg-teal-100 text-teal-700',
  approved: 'bg-emerald-100 text-emerald-700',
  published: 'bg-green-100 text-green-700',
  archived: 'bg-muted text-muted-foreground',
}

const typeLabels: Record<string, string> = {
  research_material: 'Research Material',
  brief: 'Brief',
  article: 'Article',
  landing_page: 'Landing Page',
  ad_copy: 'Ad Copy',
  social_post: 'Social Post',
  email_sequence: 'Email Sequence',
  email_excerpt: 'Email Excerpt',
  image_prompt: 'Image Prompt',
  image: 'Image',
  video_script: 'Video Script',
  lead_magnet: 'Lead Magnet',
  report: 'Report',
  brand_asset: 'Brand Asset',
}

function formatDate(ts: number) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString()
}
</script>

<template>
  <div>
    <div v-if="loading" class="p-8 text-center text-muted-foreground">Loading resource...</div>

    <div v-else-if="!resource" class="p-8 text-center text-muted-foreground">Resource not found</div>

    <div v-else>
      <!-- Header -->
      <div class="px-4 sm:px-6 py-4 border-b">
        <div class="flex items-start gap-3">
          <ResourceTypeIcon :type="resource.resourceType" :size="24" />
          <div class="flex-1 min-w-0">
            <h2 class="text-lg font-semibold text-foreground">{{ resource.title }}</h2>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-xs text-muted-foreground">{{ typeLabels[resource.resourceType] || resource.resourceType }}</span>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="statusColors[resource.status] || 'bg-muted text-muted-foreground'"
              >
                {{ resource.status.replace('_', ' ') }}
              </span>
              <span v-if="resource.qualityScore" class="text-xs text-muted-foreground">
                Score: {{ resource.qualityScore }}/10
              </span>
            </div>
          </div>
        </div>

        <!-- Meta row -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-3 text-xs text-muted-foreground">
          <span class="flex items-center gap-1"><User :size="12" /> {{ resource.createdBy }}</span>
          <span class="flex items-center gap-1"><Clock :size="12" /> {{ formatDate(resource.createdAt) }}</span>
          <span v-if="resource.updatedAt" class="flex items-center gap-1">Updated: {{ formatDate(resource.updatedAt) }}</span>
          <span v-if="resource.slug" class="flex items-center gap-1"><Hash :size="12" /> {{ resource.slug }}</span>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b px-4 sm:px-6 overflow-x-auto scrollbar-hide">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="px-3 py-2 text-sm font-medium border-b-2 transition-colors capitalize -mb-px whitespace-nowrap"
          :class="activeTab === tab
            ? 'border-primary text-primary'
            : 'border-transparent text-muted-foreground hover:text-foreground'"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <!-- Tab content -->
      <div class="p-4 sm:p-6">
        <!-- Content tab -->
        <div v-if="activeTab === 'content'">
          <!-- Frontmatter cards -->
          <div v-if="parsed?.frontmatter" class="mb-4 grid grid-cols-2 sm:grid-cols-3 gap-2">
            <div
              v-for="(value, key) in parsed.frontmatter"
              :key="key"
              class="rounded-md border p-2"
            >
              <p class="text-xs text-muted-foreground capitalize">{{ String(key).replace(/([A-Z])/g, ' $1').replace(/_/g, ' ') }}</p>
              <p class="text-sm font-medium text-foreground mt-0.5">
                {{ Array.isArray(value) ? value.join(', ') : value }}
              </p>
            </div>
          </div>

          <!-- Loading file content from disk -->
          <div v-if="fileLoading" class="p-8 text-center text-muted-foreground">
            Loading content...
          </div>

          <!-- Text content — Monaco Editor -->
          <div v-else-if="displayContent" class="rounded-lg border overflow-hidden h-[400px]">
            <VMonacoEditor
              :value="displayContent"
              :language="monacoLanguage"
              :options="{ readOnly: true, domReadOnly: true }"
            />
          </div>

          <!-- Image preview -->
          <div v-else-if="resource.resourceType === 'image' && resource.fileUrl">
            <img :src="resource.fileUrl" :alt="resource.title" class="max-w-full rounded-lg border" />
          </div>

          <!-- No content -->
          <div v-else class="text-center text-muted-foreground text-sm py-8">
            No content to display
          </div>
        </div>

        <!-- Metadata tab -->
        <div v-if="activeTab === 'metadata'">
          <div v-if="resource.metadata && Object.keys(resource.metadata).length">
            <div
              v-for="(value, key) in resource.metadata"
              :key="key"
              class="flex items-start gap-3 py-2 border-b last:border-0"
            >
              <span class="text-xs text-muted-foreground font-medium min-w-[120px] capitalize">
                {{ String(key).replace(/([A-Z])/g, ' $1').replace(/_/g, ' ') }}
              </span>
              <span class="text-sm text-foreground">
                {{ typeof value === 'object' ? JSON.stringify(value) : value }}
              </span>
            </div>
          </div>
          <div v-else class="text-center text-muted-foreground text-sm py-8">No metadata</div>
        </div>

        <!-- Relationships tab -->
        <div v-if="activeTab === 'relationships'">
          <ResourceRelationshipTree
            :resource-id="resourceId"
            @navigate="(id) => emit('navigate', id)"
          />
        </div>

        <!-- History tab -->
        <div v-if="activeTab === 'history'">
          <ResourceHistoryTimeline :resource-id="resourceId" />
        </div>

        <!-- File tab -->
        <div v-if="activeTab === 'file'">
          <div class="space-y-3">
            <div v-if="resource.filePath" class="flex items-start gap-3 py-2 border-b">
              <FolderOpen :size="16" class="text-muted-foreground mt-0.5" />
              <div>
                <p class="text-xs text-muted-foreground">File Path</p>
                <p class="text-sm font-mono text-foreground">{{ resource.filePath }}</p>
              </div>
            </div>

            <div v-if="resource.contentHash" class="flex items-start gap-3 py-2 border-b">
              <Hash :size="16" class="text-muted-foreground mt-0.5" />
              <div>
                <p class="text-xs text-muted-foreground">Content Hash</p>
                <p class="text-sm font-mono text-foreground">{{ resource.contentHash }}</p>
              </div>
            </div>

            <div v-if="resource.fileUrl" class="flex items-start gap-3 py-2 border-b">
              <ExternalLink :size="16" class="text-muted-foreground mt-0.5" />
              <div>
                <p class="text-xs text-muted-foreground">File URL</p>
                <a :href="resource.fileUrl" target="_blank" class="text-sm text-primary hover:underline">
                  {{ resource.fileUrl }}
                </a>
              </div>
            </div>

            <div v-if="resource.mimeType" class="flex items-start gap-3 py-2 border-b">
              <FileText :size="16" class="text-muted-foreground mt-0.5" />
              <div>
                <p class="text-xs text-muted-foreground">MIME Type</p>
                <p class="text-sm text-foreground">{{ resource.mimeType }}</p>
              </div>
            </div>

            <div v-if="resource.fileSizeBytes" class="flex items-start gap-3 py-2 border-b">
              <span class="text-xs text-muted-foreground mt-0.5 w-4 text-center font-mono">B</span>
              <div>
                <p class="text-xs text-muted-foreground">File Size</p>
                <p class="text-sm text-foreground">{{ (resource.fileSizeBytes / 1024).toFixed(1) }} KB</p>
              </div>
            </div>

            <!-- Orphan warning -->
            <div v-if="resource.fileOrphaned" class="flex items-center gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200">
              <AlertTriangle :size="16" class="text-amber-500" />
              <span class="text-sm text-amber-700">File not found on disk. The file may have been moved or deleted.</span>
            </div>

            <div v-if="!resource.filePath && !resource.fileUrl" class="text-center text-muted-foreground text-sm py-8">
              No file information
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
