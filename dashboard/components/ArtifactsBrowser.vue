<script setup lang="ts">
import { ref, watch, computed, onUnmounted, nextTick } from 'vue'
import {
  X,
  Folder,
  FolderOpen,
  FileText,
  FileImage,
  FileVideo,
  FileCode,
  File,
  ChevronRight,
  ChevronDown,
  Save,
  Download,
  Loader2,
} from 'lucide-vue-next'

const { isOpen, initialPath, close } = useArtifactsBrowser()

// --- Types ---

interface FileEntry {
  name: string
  isDirectory: boolean
  path: string
  size?: number
  modified?: string
}

interface TreeNode extends FileEntry {
  children?: TreeNode[]
  expanded?: boolean
  loading?: boolean
}

// --- State ---

const treeRoots = ref<TreeNode[]>([])
const selectedFile = ref<FileEntry | null>(null)
const fileContent = ref('')
const fileLoading = ref(false)
const fileSaving = ref(false)
const fileDirty = ref(false)
const treeLoading = ref(false)
const errorMessage = ref('')

// --- File type detection ---

const TEXT_EXTENSIONS = new Set([
  '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css',
  '.js', '.ts', '.vue', '.jsx', '.tsx', '.xml', '.csv',
  '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
  '.py', '.rb', '.go', '.rs', '.java', '.c', '.cpp', '.h',
  '.env', '.gitignore', '.dockerfile', '.sql',
])

const IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'])
const VIDEO_EXTENSIONS = new Set(['.mp4', '.webm'])
const PDF_EXTENSIONS = new Set(['.pdf'])

function getExtension(name: string): string {
  const dotIndex = name.lastIndexOf('.')
  return dotIndex >= 0 ? name.slice(dotIndex).toLowerCase() : ''
}

type FileType = 'text' | 'image' | 'video' | 'pdf' | 'unknown'

function getFileType(name: string): FileType {
  const ext = getExtension(name)
  if (TEXT_EXTENSIONS.has(ext)) return 'text'
  if (IMAGE_EXTENSIONS.has(ext)) return 'image'
  if (VIDEO_EXTENSIONS.has(ext)) return 'video'
  if (PDF_EXTENSIONS.has(ext)) return 'pdf'
  return 'unknown'
}

function getMonacoLanguage(name: string): string {
  const ext = getExtension(name)
  const map: Record<string, string> = {
    '.md': 'markdown',
    '.txt': 'plaintext',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.html': 'html',
    '.css': 'css',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.vue': 'html',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.xml': 'xml',
    '.py': 'python',
    '.sh': 'shell',
    '.bash': 'shell',
    '.sql': 'sql',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.csv': 'plaintext',
    '.toml': 'plaintext',
    '.ini': 'ini',
  }
  return map[ext] || 'plaintext'
}

// --- Tree operations ---

async function fetchDirectory(path: string): Promise<FileEntry[]> {
  try {
    const data = await $fetch<{ entries: FileEntry[] }>('/api/files', {
      query: { path },
    })
    return data.entries
  } catch (err) {
    console.error('Failed to fetch directory:', err)
    return []
  }
}

async function loadRootTree() {
  treeLoading.value = true
  const entries = await fetchDirectory('/')
  treeRoots.value = entries.map((e) => ({
    ...e,
    children: e.isDirectory ? undefined : undefined,
    expanded: false,
    loading: false,
  }))
  treeLoading.value = false
}

async function toggleDirectory(node: TreeNode) {
  if (!node.isDirectory) return

  if (node.expanded) {
    node.expanded = false
    return
  }

  node.loading = true
  const entries = await fetchDirectory(node.path)
  node.children = entries.map((e) => ({
    ...e,
    children: e.isDirectory ? undefined : undefined,
    expanded: false,
    loading: false,
  }))
  node.expanded = true
  node.loading = false
}

async function selectFile(entry: FileEntry) {
  if (entry.isDirectory) return

  // Check for unsaved changes
  if (fileDirty.value && selectedFile.value) {
    const discard = confirm('You have unsaved changes. Discard them?')
    if (!discard) return
  }

  selectedFile.value = entry
  fileDirty.value = false
  errorMessage.value = ''

  const fileType = getFileType(entry.name)

  if (fileType === 'text') {
    fileLoading.value = true
    try {
      const data = await $fetch<{ content: string }>('/api/file-content', {
        query: { path: entry.path },
      })
      fileContent.value = data.content
    } catch (err) {
      errorMessage.value = 'Failed to load file content'
      fileContent.value = ''
    }
    fileLoading.value = false
  }
}

async function saveFile() {
  if (!selectedFile.value || fileSaving.value) return

  fileSaving.value = true
  errorMessage.value = ''

  try {
    await $fetch('/api/file-content', {
      method: 'POST',
      body: {
        path: selectedFile.value.path,
        content: fileContent.value,
      },
    })
    fileDirty.value = false
  } catch (err) {
    errorMessage.value = 'Failed to save file'
  }

  fileSaving.value = false
}

function onEditorChange(value: string | undefined) {
  if (value !== undefined) {
    fileContent.value = value
    fileDirty.value = true
  }
}

function formatFileSize(bytes?: number): string {
  if (bytes === undefined) return '--'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso?: string): string {
  if (!iso) return '--'
  return new Date(iso).toLocaleString()
}

// --- Selected file computed ---

const selectedFileType = computed<FileType>(() => {
  if (!selectedFile.value) return 'unknown'
  return getFileType(selectedFile.value.name)
})

const selectedFileLanguage = computed(() => {
  if (!selectedFile.value) return 'plaintext'
  return getMonacoLanguage(selectedFile.value.name)
})

const selectedFileServeUrl = computed(() => {
  if (!selectedFile.value) return ''
  return `/api/file-serve?path=${encodeURIComponent(selectedFile.value.path)}`
})

// --- Keyboard ---

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    close()
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    if (selectedFileType.value === 'text' && fileDirty.value) {
      saveFile()
    }
  }
}

// --- Watchers ---

watch(isOpen, async (open) => {
  if (open) {
    document.addEventListener('keydown', onKeydown)
    document.body.style.overflow = 'hidden'
    await loadRootTree()

    // If opened with a specific path, navigate to it
    if (initialPath.value) {
      // Expand path segments to navigate to the file
      const segments = initialPath.value.replace(/^\//, '').split('/').filter(Boolean)
      let currentNodes = treeRoots.value
      for (let i = 0; i < segments.length; i++) {
        const segment = segments[i]
        const node = currentNodes.find((n) => n.name === segment)
        if (!node) break

        if (node.isDirectory && i < segments.length - 1) {
          await toggleDirectory(node)
          currentNodes = node.children || []
        } else if (!node.isDirectory) {
          await selectFile(node)
        }
      }
    }
  } else {
    document.removeEventListener('keydown', onKeydown)
    document.body.style.overflow = ''
    selectedFile.value = null
    fileContent.value = ''
    fileDirty.value = false
    errorMessage.value = ''
  }
}, { immediate: true })

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-200"
      leave-active-class="transition-all duration-200"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        data-testid="artifacts-browser"
        class="fixed inset-0 z-50 bg-black/80 p-5 flex items-stretch justify-center"
      >
        <div
          class="bg-background rounded-lg shadow-2xl w-full h-full border border-border flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-4 py-3 border-b border-border bg-card shrink-0">
            <div class="flex items-center gap-2">
              <FolderOpen :size="18" class="text-primary" />
              <h2 class="text-sm font-semibold text-foreground">Artifacts Browser</h2>
              <span v-if="selectedFile" class="text-xs text-muted-foreground ml-2">
                {{ selectedFile.path }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <!-- Save button (text files only) -->
              <button
                v-if="selectedFileType === 'text' && selectedFile"
                data-testid="save-button"
                class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
                :class="fileDirty
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'"
                :disabled="!fileDirty || fileSaving"
                @click="saveFile"
              >
                <Loader2 v-if="fileSaving" :size="14" class="animate-spin" />
                <Save v-else :size="14" />
                {{ fileSaving ? 'Saving...' : fileDirty ? 'Save' : 'Saved' }}
              </button>
              <!-- Close button -->
              <button
                data-testid="close-button"
                class="text-muted-foreground hover:text-foreground transition-colors rounded-sm p-1 hover:bg-muted"
                @click="close"
              >
                <X :size="18" />
              </button>
            </div>
          </div>

          <!-- Body: split panels -->
          <div class="flex flex-1 min-h-0">
            <!-- Left panel: File tree -->
            <div
              data-testid="file-tree-panel"
              class="w-72 border-r border-border bg-card/50 flex flex-col shrink-0 overflow-hidden"
            >
              <div class="px-3 py-2 border-b border-border/50">
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Files</p>
              </div>
              <div class="flex-1 overflow-y-auto py-1">
                <div v-if="treeLoading" class="flex items-center justify-center py-8">
                  <Loader2 :size="20" class="animate-spin text-muted-foreground" />
                </div>
                <template v-else>
                  <TreeNodeItem
                    v-for="node in treeRoots"
                    :key="node.path"
                    :node="node"
                    :depth="0"
                    :selected-path="selectedFile?.path || ''"
                    @toggle="toggleDirectory"
                    @select="selectFile"
                  />
                </template>
              </div>
            </div>

            <!-- Right panel: File viewer -->
            <div
              data-testid="file-viewer-panel"
              class="flex-1 flex flex-col min-w-0 overflow-hidden"
            >
              <!-- No file selected -->
              <div v-if="!selectedFile" class="flex-1 flex items-center justify-center">
                <div class="text-center">
                  <File :size="48" class="text-muted-foreground/30 mx-auto mb-3" />
                  <p class="text-sm text-muted-foreground">Select a file to view</p>
                </div>
              </div>

              <!-- Error message -->
              <div v-else-if="errorMessage" class="flex-1 flex items-center justify-center">
                <div class="text-center">
                  <p class="text-sm text-destructive">{{ errorMessage }}</p>
                </div>
              </div>

              <!-- Loading -->
              <div v-else-if="fileLoading" class="flex-1 flex items-center justify-center">
                <Loader2 :size="24" class="animate-spin text-muted-foreground" />
              </div>

              <!-- Text file: Monaco Editor -->
              <template v-else-if="selectedFileType === 'text'">
                <div class="flex-1 min-h-0">
                  <ClientOnly>
                    <VMonacoEditor
                      :value="fileContent"
                      :language="selectedFileLanguage"
                      theme="vs-dark"
                      :options="{
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineNumbers: 'on',
                        wordWrap: 'on',
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        readOnly: false,
                        tabSize: 2,
                      }"
                      @change="onEditorChange"
                    />
                    <template #fallback>
                      <div class="flex items-center justify-center h-full">
                        <Loader2 :size="24" class="animate-spin text-muted-foreground" />
                      </div>
                    </template>
                  </ClientOnly>
                </div>
              </template>

              <!-- Image file -->
              <template v-else-if="selectedFileType === 'image'">
                <div class="flex-1 flex items-center justify-center p-4 bg-muted/20 overflow-auto">
                  <img
                    :src="selectedFileServeUrl"
                    :alt="selectedFile.name"
                    class="max-w-full max-h-full object-contain rounded shadow-sm"
                  />
                </div>
                <div class="px-4 py-2 border-t border-border bg-card/50 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{{ selectedFile.name }} - {{ formatFileSize(selectedFile.size) }}</span>
                  <a
                    :href="selectedFileServeUrl"
                    download
                    class="flex items-center gap-1 text-primary hover:underline"
                  >
                    <Download :size="12" />
                    Download
                  </a>
                </div>
              </template>

              <!-- Video file -->
              <template v-else-if="selectedFileType === 'video'">
                <div class="flex-1 flex items-center justify-center p-4 bg-black">
                  <video
                    :src="selectedFileServeUrl"
                    controls
                    class="max-w-full max-h-full"
                  >
                    Your browser does not support the video element.
                  </video>
                </div>
                <div class="px-4 py-2 border-t border-border bg-card/50 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{{ selectedFile.name }} - {{ formatFileSize(selectedFile.size) }}</span>
                  <a
                    :href="selectedFileServeUrl"
                    download
                    class="flex items-center gap-1 text-primary hover:underline"
                  >
                    <Download :size="12" />
                    Download
                  </a>
                </div>
              </template>

              <!-- PDF file -->
              <template v-else-if="selectedFileType === 'pdf'">
                <div class="flex-1">
                  <iframe
                    :src="selectedFileServeUrl"
                    class="w-full h-full border-0"
                    :title="selectedFile.name"
                  />
                </div>
              </template>

              <!-- Unknown file type -->
              <template v-else>
                <div class="flex-1 flex items-center justify-center">
                  <div class="text-center space-y-3">
                    <File :size="48" class="text-muted-foreground/30 mx-auto" />
                    <div>
                      <p class="text-sm font-medium text-foreground">{{ selectedFile.name }}</p>
                      <p class="text-xs text-muted-foreground mt-1">
                        Size: {{ formatFileSize(selectedFile.size) }}
                      </p>
                      <p class="text-xs text-muted-foreground">
                        Modified: {{ formatDate(selectedFile.modified) }}
                      </p>
                    </div>
                    <a
                      :href="selectedFileServeUrl"
                      download
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                    >
                      <Download :size="14" />
                      Download File
                    </a>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
