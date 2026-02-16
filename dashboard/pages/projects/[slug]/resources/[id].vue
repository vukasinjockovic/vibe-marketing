<script setup lang="ts">
import { api } from '../../../../../convex/_generated/api'
import {
  ArrowLeft, Trash2, Download, ExternalLink,
  Clock, User, Hash, FolderOpen, Star,
  ChevronRight, FileText, AlertTriangle,
} from 'lucide-vue-next'
import {
  getFileExtension,
  getContentDisplayMode,
  buildFileUrl,
  formatFileSize,
  resolveContentSource,
  buildBreadcrumbs,
  isTextFile,
  typeLabels,
  statusColors,
} from '../../../../composables/useResourceContent'

const route = useRoute()
const router = useRouter()
const slug = computed(() => route.params.slug as string)
const resourceId = computed(() => route.params.id as string)

// --- Data fetching ---
const { data: resource, loading } = useConvexQuery(
  api.resources.get,
  computed(() => resourceId.value ? { id: resourceId.value as any } : 'skip'),
)

const { data: relationships } = useConvexQuery(
  api.resources.listRelated,
  computed(() => resourceId.value ? { resourceId: resourceId.value as any } : 'skip'),
)

// Load campaign info if resource has one
const { data: campaign } = useConvexQuery(
  api.campaigns.get,
  computed(() => resource.value?.campaignId
    ? { id: resource.value.campaignId as any }
    : 'skip'),
)

// --- Content display ---
const { parse } = useMarkdown()

const contentSource = computed(() => {
  if (!resource.value) return { source: 'none' as const, value: '' }
  return resolveContentSource(resource.value)
})

const displayMode = computed(() => {
  if (!resource.value) return 'empty'
  return getContentDisplayMode(resource.value.filePath, resource.value.content)
})

const fileExt = computed(() => getFileExtension(resource.value?.filePath))

// Rendered markdown content (from DB content)
const parsedMarkdown = computed(() => {
  if (displayMode.value !== 'markdown') return null
  if (contentSource.value.source === 'db') {
    return parse(contentSource.value.value)
  }
  // If from file, we load it separately
  if (fileContent.value) {
    return parse(fileContent.value)
  }
  return null
})

// Monaco language mapping for text content
const monacoLanguage = computed(() => {
  const ext = fileExt.value
  const map: Record<string, string> = {
    md: 'markdown',
    json: 'json',
    js: 'javascript',
    ts: 'typescript',
    py: 'python',
    sh: 'shell',
    yaml: 'yaml',
    yml: 'yaml',
    vue: 'html',
    jsx: 'javascript',
    tsx: 'typescript',
    html: 'html',
    htm: 'html',
    css: 'css',
    csv: 'plaintext',
    txt: 'plaintext',
    log: 'plaintext',
  }
  return map[ext] || 'markdown'
})

// Text content for Monaco (unified from DB or file)
const monacoContent = computed(() => {
  if (contentSource.value.source === 'db') return contentSource.value.value
  if (fileContent.value) return fileContent.value
  return ''
})

// --- File loading for disk-based text content ---
const fileContent = ref<string | null>(null)
const fileLoading = ref(false)
const fileError = ref<string | null>(null)

async function loadFileContent() {
  if (!resource.value?.filePath) return
  if (contentSource.value.source !== 'file') return

  const ext = getFileExtension(resource.value.filePath)
  if (!isTextFile(ext)) return

  fileLoading.value = true
  fileError.value = null

  try {
    const url = buildFileUrl(resource.value.filePath, 'text')
    const response = await $fetch<{ content: string }>(url)
    fileContent.value = response.content
  } catch (e: any) {
    fileError.value = e.message || 'Failed to load file content'
  } finally {
    fileLoading.value = false
  }
}

// Watch for resource changes and load file content
watch(() => resource.value?._id, () => {
  fileContent.value = null
  fileError.value = null
  if (resource.value && contentSource.value.source === 'file') {
    loadFileContent()
  }
}, { immediate: true })

// --- File URL for binary content ---
const binaryFileUrl = computed(() => {
  if (!resource.value?.filePath) return ''
  return buildFileUrl(resource.value.filePath, 'binary')
})

// --- Breadcrumbs ---
const breadcrumbs = computed(() => {
  return buildBreadcrumbs(
    slug.value,
    resource.value ? { title: resource.value.title, campaignId: resource.value.campaignId } : null,
    campaign.value ? { name: campaign.value.name, _id: campaign.value._id } : null,
  )
})

// --- Siblings (other children of the same parent) ---
const { data: siblings } = useConvexQuery(
  api.resources.listChildren,
  computed(() => resource.value?.parentResourceId
    ? { parentResourceId: resource.value.parentResourceId as any }
    : 'skip'),
)

const filteredSiblings = computed(() => {
  if (!siblings.value || !resource.value) return []
  return siblings.value.filter((s: any) => s._id !== resource.value!._id)
})

// --- Tabs ---
const activeTab = ref('content')
const tabs = computed(() => {
  const t = ['content', 'metadata', 'relationships', 'history']
  if (resource.value?.filePath) t.push('file')
  return t
})

// --- Delete ---
const { mutate: deleteResource } = useConvexMutation(api.resources.remove)
const showDeleteConfirm = ref(false)
const deleteError = ref('')

async function handleDelete() {
  if (!resource.value) return
  try {
    await deleteResource({
      id: resource.value._id,
      deletedBy: 'dashboard',
    })
    router.push(`/projects/${slug.value}/resources`)
  } catch (e: any) {
    deleteError.value = e.message || 'Failed to delete'
  }
}

function handleNavigate(id: string) {
  router.push(`/projects/${slug.value}/resources/${id}`)
}

function formatDate(ts: number) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatRelativeTime(ts: number) {
  if (!ts) return ''
  const now = Date.now()
  const diff = now - ts
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

function downloadFile() {
  if (!resource.value?.filePath) return
  const url = buildFileUrl(resource.value.filePath, 'binary')
  const a = document.createElement('a')
  a.href = url
  a.download = resource.value.filePath.split('/').pop() || 'download'
  a.click()
}
</script>

<template>
  <div class="space-y-4">
    <!-- Loading -->
    <div v-if="loading" class="text-muted-foreground p-8 text-center">Loading resource...</div>

    <!-- Not found -->
    <div v-else-if="!resource" class="text-center py-12">
      <FileText :size="48" class="mx-auto text-muted-foreground/40 mb-4" />
      <h2 class="text-lg font-semibold text-foreground mb-1">Resource not found</h2>
      <p class="text-sm text-muted-foreground mb-4">The resource may have been deleted or moved.</p>
      <NuxtLink
        :to="`/projects/${slug}/resources`"
        class="inline-flex items-center gap-1 text-sm text-primary hover:text-primary/80"
      >
        <ArrowLeft :size="14" />
        Back to Resources
      </NuxtLink>
    </div>

    <template v-else>
      <!-- Breadcrumbs -->
      <nav class="flex items-center gap-1 text-sm text-muted-foreground overflow-x-auto">
        <template v-for="(crumb, i) in breadcrumbs" :key="i">
          <ChevronRight v-if="i > 0" :size="14" class="shrink-0" />
          <NuxtLink
            v-if="crumb.to"
            :to="crumb.to"
            class="hover:text-foreground transition-colors whitespace-nowrap"
          >
            {{ crumb.label }}
          </NuxtLink>
          <span v-else class="text-foreground font-medium truncate max-w-[200px]">{{ crumb.label }}</span>
        </template>
      </nav>

      <!-- Header section -->
      <div class="rounded-lg border bg-card shadow-sm p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div class="flex items-start gap-3 min-w-0">
            <ResourceTypeIcon :type="resource.resourceType" :size="28" class="mt-0.5 shrink-0" />
            <div class="min-w-0">
              <h1 class="text-xl sm:text-2xl font-bold text-foreground break-words">{{ resource.title }}</h1>
              <div class="flex items-center gap-2 mt-1.5 flex-wrap">
                <span class="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                  {{ typeLabels[resource.resourceType] || resource.resourceType }}
                </span>
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="statusColors[resource.status] || 'bg-muted text-muted-foreground'"
                >
                  {{ resource.status.replace(/_/g, ' ') }}
                </span>
                <span v-if="resource.qualityScore" class="inline-flex items-center gap-1 text-xs text-amber-600">
                  <Star :size="12" />
                  {{ resource.qualityScore }}/10
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              v-if="resource.filePath"
              class="flex items-center gap-1 px-3 py-1.5 text-sm border border-border rounded-md text-muted-foreground hover:bg-muted transition-colors"
              @click="downloadFile"
            >
              <Download :size="14" />
              Download
            </button>
            <button
              class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
              @click="showDeleteConfirm = true"
            >
              <Trash2 :size="14" />
              Delete
            </button>
          </div>
        </div>

        <!-- Meta row -->
        <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-3 pt-3 border-t text-xs text-muted-foreground">
          <span v-if="resource.createdBy" class="flex items-center gap-1">
            <User :size="12" />
            {{ resource.createdBy }}
          </span>
          <span v-if="resource.createdAt" class="flex items-center gap-1">
            <Clock :size="12" />
            {{ formatDate(resource.createdAt) }}
          </span>
          <span v-if="resource.updatedAt" class="flex items-center gap-1">
            Updated {{ formatRelativeTime(resource.updatedAt) }}
          </span>
          <span v-if="resource.slug" class="flex items-center gap-1">
            <Hash :size="12" />
            {{ resource.slug }}
          </span>
          <span v-if="resource.filePath" class="flex items-center gap-1 font-mono text-[11px]">
            <FolderOpen :size="12" />
            {{ resource.filePath }}
          </span>
          <span v-if="resource.fileSizeBytes" class="flex items-center gap-1">
            {{ formatFileSize(resource.fileSizeBytes) }}
          </span>
          <NuxtLink
            v-if="campaign"
            :to="`/projects/${slug}/campaigns/${campaign._id}`"
            class="flex items-center gap-1 text-primary hover:text-primary/80"
          >
            <ExternalLink :size="12" />
            {{ campaign.name }}
          </NuxtLink>
        </div>

        <!-- Orphan warning -->
        <div v-if="resource.fileOrphaned" class="flex items-center gap-2 mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200">
          <AlertTriangle :size="16" class="text-amber-500 shrink-0" />
          <span class="text-sm text-amber-700">File not found on disk. The file may have been moved or deleted.</span>
        </div>
      </div>

      <!-- Tabs -->
      <div class="rounded-lg border bg-card shadow-sm overflow-hidden">
        <div class="flex border-b px-4 sm:px-6 overflow-x-auto scrollbar-hide">
          <button
            v-for="tab in tabs"
            :key="tab"
            class="px-3 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize -mb-px whitespace-nowrap"
            :class="activeTab === tab
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </div>

        <div class="p-4 sm:p-6">
          <!-- ========== Content Tab ========== -->
          <div v-if="activeTab === 'content'">
            <!-- Frontmatter cards (for markdown with frontmatter) -->
            <div v-if="parsedMarkdown?.frontmatter" class="mb-4 grid grid-cols-2 sm:grid-cols-3 gap-2">
              <div
                v-for="(value, key) in parsedMarkdown.frontmatter"
                :key="key"
                class="rounded-md border p-2"
              >
                <p class="text-xs text-muted-foreground capitalize">
                  {{ String(key).replace(/([A-Z])/g, ' $1').replace(/_/g, ' ') }}
                </p>
                <p class="text-sm font-medium text-foreground mt-0.5">
                  {{ Array.isArray(value) ? value.join(', ') : value }}
                </p>
              </div>
            </div>

            <!-- Loading file content -->
            <div v-if="fileLoading" class="text-center py-8 text-muted-foreground text-sm">
              Loading file content...
            </div>

            <!-- File load error -->
            <div v-else-if="fileError" class="text-center py-8">
              <AlertTriangle :size="24" class="mx-auto text-amber-500 mb-2" />
              <p class="text-sm text-muted-foreground">{{ fileError }}</p>
              <button
                class="mt-2 text-sm text-primary hover:text-primary/80"
                @click="loadFileContent"
              >
                Retry
              </button>
            </div>

            <!-- Text content (markdown, plaintext, code) — Monaco Editor -->
            <div
              v-else-if="(displayMode === 'markdown' || displayMode === 'plaintext' || displayMode === 'code') && monacoContent"
              class="rounded-lg border overflow-hidden h-[600px]"
            >
              <VMonacoEditor
                :value="monacoContent"
                :language="monacoLanguage"
                :options="{ readOnly: true, domReadOnly: true }"
              />
            </div>

            <!-- HTML content -->
            <div v-else-if="displayMode === 'html'" class="rounded-lg border overflow-hidden">
              <iframe
                :srcdoc="contentSource.source === 'db' ? contentSource.value : fileContent || ''"
                class="w-full min-h-[500px] border-0"
                sandbox="allow-same-origin"
              />
            </div>

            <!-- PDF -->
            <div v-else-if="displayMode === 'pdf'" class="rounded-lg border overflow-hidden">
              <iframe
                v-if="resource.fileUrl"
                :src="resource.fileUrl"
                class="w-full min-h-[700px] border-0"
              />
              <iframe
                v-else-if="resource.filePath"
                :src="binaryFileUrl"
                class="w-full min-h-[700px] border-0"
              />
              <p v-else class="p-8 text-center text-muted-foreground text-sm">No PDF source available</p>
            </div>

            <!-- Image -->
            <div v-else-if="displayMode === 'image'" class="text-center">
              <img
                :src="resource.fileUrl || binaryFileUrl"
                :alt="resource.title"
                class="max-w-full max-h-[600px] rounded-lg border mx-auto object-contain"
              />
            </div>

            <!-- Video -->
            <div v-else-if="displayMode === 'video'" class="rounded-lg border overflow-hidden bg-black">
              <video
                :src="resource.fileUrl || binaryFileUrl"
                controls
                class="w-full max-h-[500px]"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            <!-- Audio -->
            <div v-else-if="displayMode === 'audio'" class="py-8">
              <audio
                :src="resource.fileUrl || binaryFileUrl"
                controls
                class="w-full"
              >
                Your browser does not support the audio tag.
              </audio>
            </div>

            <!-- Office documents (docx) -->
            <div v-else-if="displayMode === 'office-doc' || displayMode === 'office-sheet' || displayMode === 'office-pres'">
              <div v-if="resource.fileUrl" class="rounded-lg border overflow-hidden">
                <iframe
                  :src="`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(resource.fileUrl)}`"
                  class="w-full min-h-[600px] border-0"
                />
              </div>
              <div v-else class="text-center py-8">
                <FileText :size="32" class="mx-auto text-muted-foreground/40 mb-3" />
                <p class="text-sm text-muted-foreground mb-3">
                  Office documents require a public URL for online preview.
                </p>
                <button
                  v-if="resource.filePath"
                  class="inline-flex items-center gap-1.5 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                  @click="downloadFile"
                >
                  <Download :size="14" />
                  Download File
                </button>
              </div>
            </div>

            <!-- Unsupported -->
            <div v-else-if="displayMode === 'unsupported'" class="text-center py-8">
              <FileText :size="32" class="mx-auto text-muted-foreground/40 mb-3" />
              <p class="text-sm text-muted-foreground mb-1">
                Preview not available for .{{ fileExt }} files
              </p>
              <button
                v-if="resource.filePath"
                class="mt-3 inline-flex items-center gap-1.5 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                @click="downloadFile"
              >
                <Download :size="14" />
                Download File
              </button>
            </div>

            <!-- Image type resource without file extension detection -->
            <div v-else-if="resource.resourceType === 'image' && resource.fileUrl">
              <img
                :src="resource.fileUrl"
                :alt="resource.title"
                class="max-w-full max-h-[600px] rounded-lg border mx-auto"
              />
            </div>

            <!-- Empty -->
            <div v-else class="text-center py-8">
              <FileText :size="32" class="mx-auto text-muted-foreground/40 mb-3" />
              <p class="text-sm text-muted-foreground">No content available</p>
            </div>
          </div>

          <!-- ========== Metadata Tab ========== -->
          <div v-if="activeTab === 'metadata'">
            <div v-if="resource.metadata && Object.keys(resource.metadata).length">
              <div
                v-for="(value, key) in resource.metadata"
                :key="key"
                class="flex items-start gap-3 py-2.5 border-b last:border-0"
              >
                <span class="text-xs text-muted-foreground font-medium min-w-[140px] capitalize">
                  {{ String(key).replace(/([A-Z])/g, ' $1').replace(/_/g, ' ') }}
                </span>
                <span class="text-sm text-foreground break-all">
                  {{ typeof value === 'object' ? JSON.stringify(value, null, 2) : value }}
                </span>
              </div>
            </div>
            <div v-else class="text-center text-muted-foreground text-sm py-8">No metadata</div>
          </div>

          <!-- ========== Relationships Tab ========== -->
          <div v-if="activeTab === 'relationships'">
            <div v-if="!relationships?.parent && !relationships?.children?.length && !relationships?.related?.length && !filteredSiblings?.length"
                 class="text-center text-muted-foreground text-sm py-8">
              No relationships found
            </div>

            <div v-else class="space-y-6">
              <!-- Parent -->
              <div v-if="relationships?.parent">
                <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Parent</h4>
                <div
                  class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors"
                  @click="handleNavigate(relationships.parent._id)"
                >
                  <ResourceTypeIcon :type="relationships.parent.resourceType" :size="18" />
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-medium text-foreground truncate">{{ relationships.parent.title }}</p>
                    <p class="text-xs text-muted-foreground">{{ typeLabels[relationships.parent.resourceType] || relationships.parent.resourceType }}</p>
                  </div>
                  <span
                    class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
                    :class="statusColors[relationships.parent.status] || 'bg-muted text-muted-foreground'"
                  >
                    {{ relationships.parent.status.replace(/_/g, ' ') }}
                  </span>
                  <ChevronRight :size="14" class="text-muted-foreground shrink-0" />
                </div>
              </div>

              <!-- Children -->
              <div v-if="relationships?.children?.length">
                <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                  Children ({{ relationships.children.length }})
                </h4>
                <div class="space-y-1.5">
                  <div
                    v-for="child in relationships.children"
                    :key="child._id"
                    class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors"
                    @click="handleNavigate(child._id)"
                  >
                    <ResourceTypeIcon :type="child.resourceType" :size="16" />
                    <div class="min-w-0 flex-1">
                      <p class="text-sm font-medium text-foreground truncate">{{ child.title }}</p>
                      <p class="text-xs text-muted-foreground">{{ typeLabels[child.resourceType] || child.resourceType }}</p>
                    </div>
                    <span v-if="child.qualityScore" class="text-xs text-amber-600 shrink-0">
                      {{ child.qualityScore }}/10
                    </span>
                    <span
                      class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
                      :class="statusColors[child.status] || 'bg-muted text-muted-foreground'"
                    >
                      {{ child.status.replace(/_/g, ' ') }}
                    </span>
                    <ChevronRight :size="14" class="text-muted-foreground shrink-0" />
                  </div>
                </div>
              </div>

              <!-- Related -->
              <div v-if="relationships?.related?.length">
                <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                  Related ({{ relationships.related.length }})
                </h4>
                <div class="space-y-1.5">
                  <div
                    v-for="rel in relationships.related"
                    :key="rel._id"
                    class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors"
                    @click="handleNavigate(rel._id)"
                  >
                    <ResourceTypeIcon :type="rel.resourceType" :size="16" />
                    <div class="min-w-0 flex-1">
                      <p class="text-sm font-medium text-foreground truncate">{{ rel.title }}</p>
                      <p class="text-xs text-muted-foreground">{{ typeLabels[rel.resourceType] || rel.resourceType }}</p>
                    </div>
                    <span
                      class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
                      :class="statusColors[rel.status] || 'bg-muted text-muted-foreground'"
                    >
                      {{ rel.status.replace(/_/g, ' ') }}
                    </span>
                    <ChevronRight :size="14" class="text-muted-foreground shrink-0" />
                  </div>
                </div>
              </div>

              <!-- Siblings -->
              <div v-if="filteredSiblings?.length">
                <h4 class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                  Siblings ({{ filteredSiblings.length }})
                </h4>
                <div class="space-y-1.5">
                  <div
                    v-for="sib in filteredSiblings"
                    :key="sib._id"
                    class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted/50 transition-colors"
                    @click="handleNavigate(sib._id)"
                  >
                    <ResourceTypeIcon :type="sib.resourceType" :size="16" />
                    <div class="min-w-0 flex-1">
                      <p class="text-sm font-medium text-foreground truncate">{{ sib.title }}</p>
                      <p class="text-xs text-muted-foreground">{{ typeLabels[sib.resourceType] || sib.resourceType }}</p>
                    </div>
                    <span
                      class="text-[10px] px-1.5 py-0.5 rounded-full font-medium shrink-0"
                      :class="statusColors[sib.status] || 'bg-muted text-muted-foreground'"
                    >
                      {{ sib.status.replace(/_/g, ' ') }}
                    </span>
                    <ChevronRight :size="14" class="text-muted-foreground shrink-0" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ========== History Tab ========== -->
          <div v-if="activeTab === 'history'">
            <ResourceHistoryTimeline :resource-id="resourceId" />
          </div>

          <!-- ========== File Tab ========== -->
          <div v-if="activeTab === 'file'">
            <div class="space-y-3">
              <div v-if="resource.filePath" class="flex items-start gap-3 py-2.5 border-b">
                <FolderOpen :size="16" class="text-muted-foreground mt-0.5" />
                <div>
                  <p class="text-xs text-muted-foreground">File Path</p>
                  <p class="text-sm font-mono text-foreground break-all">{{ resource.filePath }}</p>
                </div>
              </div>

              <div v-if="resource.contentHash" class="flex items-start gap-3 py-2.5 border-b">
                <Hash :size="16" class="text-muted-foreground mt-0.5" />
                <div>
                  <p class="text-xs text-muted-foreground">Content Hash</p>
                  <p class="text-sm font-mono text-foreground">{{ resource.contentHash }}</p>
                </div>
              </div>

              <div v-if="resource.fileUrl" class="flex items-start gap-3 py-2.5 border-b">
                <ExternalLink :size="16" class="text-muted-foreground mt-0.5" />
                <div>
                  <p class="text-xs text-muted-foreground">File URL</p>
                  <a :href="resource.fileUrl" target="_blank" class="text-sm text-primary hover:underline break-all">
                    {{ resource.fileUrl }}
                  </a>
                </div>
              </div>

              <div v-if="resource.mimeType" class="flex items-start gap-3 py-2.5 border-b">
                <FileText :size="16" class="text-muted-foreground mt-0.5" />
                <div>
                  <p class="text-xs text-muted-foreground">MIME Type</p>
                  <p class="text-sm text-foreground">{{ resource.mimeType }}</p>
                </div>
              </div>

              <div v-if="resource.fileSizeBytes" class="flex items-start gap-3 py-2.5 border-b">
                <span class="text-xs text-muted-foreground mt-0.5 w-4 text-center font-mono">B</span>
                <div>
                  <p class="text-xs text-muted-foreground">File Size</p>
                  <p class="text-sm text-foreground">{{ formatFileSize(resource.fileSizeBytes) }}</p>
                </div>
              </div>

              <div v-if="resource.fileOrphaned" class="flex items-center gap-2 p-3 rounded-lg bg-amber-50 border border-amber-200">
                <AlertTriangle :size="16" class="text-amber-500" />
                <span class="text-sm text-amber-700">File not found on disk.</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Delete confirmation -->
    <VConfirmDialog
      v-if="resource"
      v-model="showDeleteConfirm"
      title="Delete Resource"
      :message="`Are you sure you want to delete &quot;${resource.title}&quot;? This action cannot be undone.`"
      confirm-label="Delete"
      confirm-class="bg-red-600 hover:bg-red-700"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
/* Markdown prose styling enhancements */
:deep(.prose h1) { font-size: 1.5rem; margin-top: 1.5rem; margin-bottom: 0.75rem; }
:deep(.prose h2) { font-size: 1.25rem; margin-top: 1.25rem; margin-bottom: 0.625rem; }
:deep(.prose h3) { font-size: 1.125rem; margin-top: 1rem; margin-bottom: 0.5rem; }
:deep(.prose pre) { max-height: 400px; overflow-y: auto; }
:deep(.prose img) { max-width: 100%; border-radius: 0.5rem; }
:deep(.prose table) { width: 100%; border-collapse: collapse; }
:deep(.prose th),
:deep(.prose td) { border: 1px solid hsl(var(--border)); padding: 0.5rem 0.75rem; text-align: left; }
:deep(.prose th) { background: hsl(var(--muted)); font-weight: 600; }

/* Scrollbar hide utility */
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
