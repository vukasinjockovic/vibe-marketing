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
  FilePlus,
  FolderPlus,
  Trash2,
  Pencil,
  Eye,
  ChevronRight,
  ChevronDown,
  Save,
  Download,
  Upload,
  Loader2,
} from 'lucide-vue-next'

const { isOpen, initialPath, projectSlug, close } = useArtifactsBrowser()

// The root directory for the current project
const projectRoot = computed(() =>
  projectSlug.value ? `/projects/${projectSlug.value}` : '/projects',
)

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
const AUDIO_EXTENSIONS = new Set(['.mp3', '.wav', '.ogg', '.flac'])
const EPUB_EXTENSIONS = new Set(['.epub'])
const PDF_EXTENSIONS = new Set(['.pdf'])

function getExtension(name: string): string {
  const dotIndex = name.lastIndexOf('.')
  return dotIndex >= 0 ? name.slice(dotIndex).toLowerCase() : ''
}

type FileType = 'text' | 'image' | 'video' | 'audio' | 'epub' | 'pdf' | 'unknown'

function getFileType(name: string): FileType {
  const ext = getExtension(name)
  if (TEXT_EXTENSIONS.has(ext)) return 'text'
  if (IMAGE_EXTENSIONS.has(ext)) return 'image'
  if (VIDEO_EXTENSIONS.has(ext)) return 'video'
  if (AUDIO_EXTENSIONS.has(ext)) return 'audio'
  if (EPUB_EXTENSIONS.has(ext)) return 'epub'
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
  const entries = await fetchDirectory(projectRoot.value)
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

  // Clean up previous epub if switching away
  destroyEpub()

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
  } else if (fileType === 'epub') {
    const url = `/api/file-serve?path=${encodeURIComponent(entry.path)}`
    openEpub(url)
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

// --- Context menu ---

interface ContextMenu {
  x: number
  y: number
  node: TreeNode | null // null = background click
}

const contextMenu = ref<ContextMenu | null>(null)

function showContextMenu(e: MouseEvent, node: TreeNode | null) {
  contextMenu.value = { x: e.clientX, y: e.clientY, node }
}

function hideContextMenu() {
  contextMenu.value = null
}

// Determine the parent directory path for the context menu target
function getContextDir(): string {
  if (!contextMenu.value) return projectRoot.value
  const node = contextMenu.value.node
  if (!node) return projectRoot.value
  if (node.isDirectory) return node.path
  // For files, get parent directory from path
  const lastSlash = node.path.lastIndexOf('/')
  return lastSlash > 0 ? node.path.slice(0, lastSlash) : projectRoot.value
}

// Find the TreeNode that matches the parent directory so we can refresh it
function findNodeByPath(path: string, nodes: TreeNode[]): TreeNode | null {
  for (const node of nodes) {
    if (node.path === path) return node
    if (node.children) {
      const found = findNodeByPath(path, node.children)
      if (found) return found
    }
  }
  return null
}

async function refreshDirectory(dirPath: string) {
  if (dirPath === projectRoot.value) {
    await loadRootTree()
    return
  }
  const parentNode = findNodeByPath(dirPath, treeRoots.value)
  if (parentNode && parentNode.isDirectory) {
    parentNode.loading = true
    const entries = await fetchDirectory(parentNode.path)
    parentNode.children = entries.map((e) => ({
      ...e,
      children: e.isDirectory ? undefined : undefined,
      expanded: false,
      loading: false,
    }))
    parentNode.expanded = true
    parentNode.loading = false
  }
}

async function createItem(type: 'file' | 'folder') {
  const dirPath = getContextDir()
  const label = type === 'file' ? 'file name (e.g. notes.md)' : 'folder name'
  const name = prompt(`Enter ${label}:`)
  if (!name || !name.trim()) return

  const itemPath = `${dirPath}/${name.trim()}`
  try {
    await $fetch('/api/files', {
      method: 'POST',
      body: { path: itemPath, type },
    })
    await refreshDirectory(dirPath)
  } catch (err: any) {
    const msg = err?.data?.statusMessage || `Failed to create ${type}`
    alert(msg)
  }
  hideContextMenu()
}

async function deleteItem() {
  if (!contextMenu.value?.node) return
  const node = contextMenu.value.node
  const label = node.isDirectory ? 'folder' : 'file'
  if (!confirm(`Delete ${label} "${node.name}"? This cannot be undone.`)) {
    hideContextMenu()
    return
  }

  try {
    await $fetch('/api/files', {
      method: 'DELETE',
      body: { path: node.path },
    })
    // If the deleted file was selected, clear the viewer
    if (selectedFile.value?.path === node.path) {
      selectedFile.value = null
      fileContent.value = ''
      fileDirty.value = false
    }
    // Refresh parent
    const lastSlash = node.path.lastIndexOf('/')
    const parentPath = lastSlash > 0 ? node.path.slice(0, lastSlash) : projectRoot.value
    await refreshDirectory(parentPath)
  } catch (err: any) {
    const msg = err?.data?.statusMessage || 'Failed to delete'
    alert(msg)
  }
  hideContextMenu()
}

function viewItem() {
  if (!contextMenu.value?.node) return
  const node = contextMenu.value.node
  if (node.isDirectory) {
    toggleDirectory(node)
  } else {
    selectFile(node)
  }
  hideContextMenu()
}

async function renameItem() {
  if (!contextMenu.value?.node) return
  const node = contextMenu.value.node
  const newName = prompt(`Rename "${node.name}" to:`, node.name)
  if (!newName || !newName.trim() || newName.trim() === node.name) {
    hideContextMenu()
    return
  }

  try {
    await $fetch('/api/files', {
      method: 'PATCH',
      body: { path: node.path, newName: newName.trim() },
    })
    // If the renamed file was selected, clear viewer
    if (selectedFile.value?.path === node.path) {
      selectedFile.value = null
      fileContent.value = ''
      fileDirty.value = false
    }
    // Refresh parent
    const lastSlash = node.path.lastIndexOf('/')
    const parentPath = lastSlash > 0 ? node.path.slice(0, lastSlash) : projectRoot.value
    await refreshDirectory(parentPath)
  } catch (err: any) {
    const msg = err?.data?.statusMessage || 'Failed to rename'
    alert(msg)
  }
  hideContextMenu()
}

// --- File upload ---

const fileInputRef = ref<HTMLInputElement | null>(null)
let uploadTargetDir = ''

function triggerUpload() {
  uploadTargetDir = getContextDir()
  hideContextMenu()
  nextTick(() => {
    fileInputRef.value?.click()
  })
}

async function handleFileUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return

  for (const file of Array.from(files)) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('destDir', uploadTargetDir)

    try {
      await $fetch('/api/file-upload', {
        method: 'POST',
        body: formData,
      })
    } catch (err: any) {
      const msg = err?.data?.statusMessage || `Failed to upload ${file.name}`
      alert(msg)
    }
  }

  await refreshDirectory(uploadTargetDir)
  // Reset input so the same file can be re-uploaded
  input.value = ''
}

// --- Drag & drop move ---

const treeBgDragOver = ref(false)

function onTreeBgDragOver(e: DragEvent) {
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
  treeBgDragOver.value = true
}

function onTreeBgDragLeave() {
  treeBgDragOver.value = false
}

function onTreeBgDrop(e: DragEvent) {
  treeBgDragOver.value = false
  if (!e.dataTransfer) return
  const sourcePath = e.dataTransfer.getData('text/plain')
  if (!sourcePath) return
  // Drop on background = move to project root
  const sourceParent = sourcePath.slice(0, sourcePath.lastIndexOf('/'))
  if (sourceParent === projectRoot.value) return // already there
  moveItem(sourcePath, projectRoot.value)
}

async function moveItem(sourcePath: string, destDirPath: string) {
  try {
    await $fetch('/api/files', {
      method: 'PUT',
      body: { sourcePath, destDir: destDirPath },
    })
    // If the moved file was selected, clear viewer
    if (selectedFile.value?.path === sourcePath) {
      selectedFile.value = null
      fileContent.value = ''
      fileDirty.value = false
    }
    // Refresh source parent
    const sourceParent = sourcePath.slice(0, sourcePath.lastIndexOf('/')) || projectRoot.value
    await refreshDirectory(sourceParent)
    // Refresh destination (if different)
    if (destDirPath !== sourceParent) {
      await refreshDirectory(destDirPath)
    }
  } catch (err: any) {
    const msg = err?.data?.statusMessage || 'Failed to move'
    alert(msg)
  }
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

// --- EPUB reader ---

const epubContainerRef = ref<HTMLDivElement | null>(null)
let epubBook: any = null
let epubRendition: any = null
const epubLoading = ref(false)
const epubCurrentPage = ref('')

let epubJsPromise: Promise<void> | null = null

function loadEpubJs(): Promise<void> {
  if (epubJsPromise) return epubJsPromise
  if ((window as any).ePub) return Promise.resolve()

  epubJsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/epub.js/0.3.93/epub.min.js'
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load epub.js'))
    document.head.appendChild(script)
  })
  return epubJsPromise
}

async function openEpub(url: string) {
  epubLoading.value = true
  try {
    await loadEpubJs()
    destroyEpub()

    await nextTick()
    if (!epubContainerRef.value) return

    const ePub = (window as any).ePub
    epubBook = ePub(url)
    epubRendition = epubBook.renderTo(epubContainerRef.value, {
      width: '100%',
      height: '100%',
      spread: 'none',
      flow: 'paginated',
    })

    epubRendition.themes.default({
      body: { background: '#1a1b26', color: '#c0caf5', 'font-family': 'Georgia, serif', 'line-height': '1.7', padding: '0 20px' },
      a: { color: '#7aa2f7' },
    })

    epubRendition.on('relocated', (location: any) => {
      if (location?.start?.cfi) {
        const displayed = location.start.displayed
        if (displayed) {
          epubCurrentPage.value = `Page ${displayed.page} of ${displayed.total}`
        }
      }
    })

    await epubRendition.display()
  } catch (err) {
    console.error('Failed to load EPUB:', err)
    errorMessage.value = 'Failed to load EPUB file'
  }
  epubLoading.value = false
}

function epubNext() {
  epubRendition?.next()
}

function epubPrev() {
  epubRendition?.prev()
}

function destroyEpub() {
  if (epubRendition) {
    epubRendition.destroy()
    epubRendition = null
  }
  if (epubBook) {
    epubBook.destroy()
    epubBook = null
  }
  epubCurrentPage.value = ''
}

// --- Keyboard ---

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    if (contextMenu.value) {
      hideContextMenu()
      return
    }
    close()
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    if (selectedFileType.value === 'text' && fileDirty.value) {
      saveFile()
    }
  }
  if (selectedFileType.value === 'epub') {
    if (e.key === 'ArrowLeft') epubPrev()
    if (e.key === 'ArrowRight') epubNext()
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
    destroyEpub()
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
  <!-- Hidden file input for uploads -->
  <input
    ref="fileInputRef"
    type="file"
    multiple
    class="hidden"
    @change="handleFileUpload"
  />

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
              <h2 class="text-sm font-semibold text-foreground">Project Files</h2>
              <span class="text-xs text-muted-foreground ml-2">
                {{ selectedFile ? selectedFile.path : projectRoot }}
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
          <div class="flex flex-1 min-h-0" @click="hideContextMenu">
            <!-- Left panel: File tree -->
            <div
              data-testid="file-tree-panel"
              class="w-72 border-r border-border bg-card/50 flex flex-col shrink-0 overflow-hidden"
            >
              <div class="px-3 py-2 border-b border-border/50">
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Files</p>
              </div>
              <div
                class="flex-1 overflow-y-auto py-1"
                @contextmenu.prevent="showContextMenu($event, null)"
                @dragover.prevent="onTreeBgDragOver"
                @dragleave="onTreeBgDragLeave"
                @drop.prevent="onTreeBgDrop"
                :class="treeBgDragOver ? 'bg-primary/10' : ''"
              >
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
                    @contextmenu="showContextMenu"
                    @drop="moveItem"
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
                      :options="{
                        fontSize: 13,
                        readOnly: false,
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

              <!-- Audio file -->
              <template v-else-if="selectedFileType === 'audio'">
                <div class="flex-1 flex items-center justify-center p-8 bg-muted/20">
                  <div class="w-full max-w-lg space-y-4 text-center">
                    <File :size="48" class="text-muted-foreground/40 mx-auto" />
                    <p class="text-sm font-medium text-foreground">{{ selectedFile.name }}</p>
                    <audio
                      :src="selectedFileServeUrl"
                      controls
                      class="w-full"
                    >
                      Your browser does not support the audio element.
                    </audio>
                    <p class="text-xs text-muted-foreground">{{ formatFileSize(selectedFile.size) }}</p>
                  </div>
                </div>
              </template>

              <!-- EPUB file -->
              <template v-else-if="selectedFileType === 'epub'">
                <div v-if="epubLoading" class="flex-1 flex items-center justify-center">
                  <Loader2 :size="24" class="animate-spin text-muted-foreground" />
                </div>
                <template v-else>
                  <div ref="epubContainerRef" class="flex-1 min-h-0 bg-[#1a1b26]" />
                  <div class="flex items-center justify-between px-4 py-2 border-t border-border bg-card/50 shrink-0">
                    <button
                      class="px-3 py-1 text-xs font-medium rounded-md bg-muted text-muted-foreground hover:bg-muted/80 transition-colors"
                      @click="epubPrev"
                    >
                      Previous
                    </button>
                    <span class="text-xs text-muted-foreground">{{ epubCurrentPage }}</span>
                    <button
                      class="px-3 py-1 text-xs font-medium rounded-md bg-muted text-muted-foreground hover:bg-muted/80 transition-colors"
                      @click="epubNext"
                    >
                      Next
                    </button>
                  </div>
                </template>
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

    <!-- Context menu -->
    <Transition
      enter-active-class="transition-all duration-100"
      leave-active-class="transition-all duration-75"
      enter-from-class="opacity-0 scale-95"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="contextMenu"
        data-testid="context-menu"
        class="fixed z-[60] min-w-[180px] rounded-md border border-border bg-popover text-popover-foreground shadow-lg py-1"
        :style="{ left: `${contextMenu.x}px`, top: `${contextMenu.y}px` }"
        @click.stop
        @contextmenu.prevent
      >
        <!-- View (only for files/folders, not background) -->
        <button
          v-if="contextMenu.node"
          class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
          @click="viewItem"
        >
          <Eye :size="14" class="text-muted-foreground" />
          {{ contextMenu.node.isDirectory ? 'Open' : 'View' }}
        </button>

        <div v-if="contextMenu.node" class="my-1 border-t border-border/50" />

        <!-- New file -->
        <button
          class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
          @click="createItem('file')"
        >
          <FilePlus :size="14" class="text-muted-foreground" />
          New File
        </button>

        <!-- New folder -->
        <button
          class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
          @click="createItem('folder')"
        >
          <FolderPlus :size="14" class="text-muted-foreground" />
          New Folder
        </button>

        <!-- Upload file -->
        <button
          class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
          @click="triggerUpload"
        >
          <Upload :size="14" class="text-muted-foreground" />
          Upload File
        </button>

        <!-- Rename / Delete (only for files/folders, not background) -->
        <template v-if="contextMenu.node">
          <div class="my-1 border-t border-border/50" />
          <button
            class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
            @click="renameItem"
          >
            <Pencil :size="14" class="text-muted-foreground" />
            Rename
          </button>
          <button
            class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-destructive/10 text-destructive transition-colors text-left"
            @click="deleteItem"
          >
            <Trash2 :size="14" />
            Delete
          </button>
        </template>
      </div>
    </Transition>
  </Teleport>
</template>
