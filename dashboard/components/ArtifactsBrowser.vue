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
  Copy,
  Check,
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
  uploading?: boolean
}

// --- Resizable sidebar ---

const SIDEBAR_STORAGE_KEY = 'artifacts-sidebar-width'
const SIDEBAR_MIN_PX = 180
const SIDEBAR_DEFAULT_PX = 288 // 18rem = w-72

const sidebarWidth = ref(
  parseInt(localStorage.getItem(SIDEBAR_STORAGE_KEY) || '', 10) || SIDEBAR_DEFAULT_PX,
)
const isResizing = ref(false)
let resizeContainerEl: HTMLElement | null = null

function onResizeStart(e: MouseEvent) {
  e.preventDefault()
  isResizing.value = true
  resizeContainerEl = (e.target as HTMLElement).closest('[data-testid="artifacts-browser"]')?.querySelector('.flex.flex-1.min-h-0') as HTMLElement | null

  const onMove = (ev: MouseEvent) => {
    if (!resizeContainerEl) return
    const containerRect = resizeContainerEl.getBoundingClientRect()
    const maxWidth = containerRect.width * 0.5
    const newWidth = Math.min(maxWidth, Math.max(SIDEBAR_MIN_PX, ev.clientX - containerRect.left))
    sidebarWidth.value = newWidth
  }

  const onUp = () => {
    isResizing.value = false
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(Math.round(sidebarWidth.value)))
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
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
const pathCopied = ref(false)

async function copyPath() {
  const path = selectedFile.value?.path || projectRoot.value
  await navigator.clipboard.writeText(path)
  pathCopied.value = true
  setTimeout(() => { pathCopied.value = false }, 1500)
}

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
const DOCX_EXTENSIONS = new Set(['.docx', '.doc'])
const SPREADSHEET_EXTENSIONS = new Set(['.xlsx', '.xls', '.ods', '.csv'])
const PDF_EXTENSIONS = new Set(['.pdf'])

function getExtension(name: string): string {
  const dotIndex = name.lastIndexOf('.')
  return dotIndex >= 0 ? name.slice(dotIndex).toLowerCase() : ''
}

type FileType = 'text' | 'image' | 'video' | 'audio' | 'epub' | 'docx' | 'spreadsheet' | 'pdf' | 'unknown'

function getFileType(name: string): FileType {
  const ext = getExtension(name)
  if (TEXT_EXTENSIONS.has(ext)) return 'text'
  if (IMAGE_EXTENSIONS.has(ext)) return 'image'
  if (VIDEO_EXTENSIONS.has(ext)) return 'video'
  if (AUDIO_EXTENSIONS.has(ext)) return 'audio'
  if (EPUB_EXTENSIONS.has(ext)) return 'epub'
  if (DOCX_EXTENSIONS.has(ext)) return 'docx'
  if (SPREADSHEET_EXTENSIONS.has(ext)) return 'spreadsheet'
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
        query: { path: entry.path, ...(entry.modified ? { v: new Date(entry.modified).getTime() } : {}) },
      })
      fileContent.value = data.content
    } catch (err) {
      errorMessage.value = 'Failed to load file content'
      fileContent.value = ''
    }
    fileLoading.value = false
  } else if (fileType === 'epub') {
    openEpub(serveUrl(entry.path, entry.modified))
  } else if (fileType === 'docx') {
    openDocx(serveUrl(entry.path, entry.modified))
  } else if (fileType === 'spreadsheet') {
    openSpreadsheet(serveUrl(entry.path, entry.modified))
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

// --- Download file ---
function downloadItem() {
  if (!contextMenu.value?.node || contextMenu.value.node.isDirectory) {
    hideContextMenu()
    return
  }
  const node = contextMenu.value.node
  const url = serveUrl(node.path, node.modified) + '&download=1'
  const a = document.createElement('a')
  a.href = url
  a.download = node.name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
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

function injectGhostNodes(targetDir: string, fileNames: string[]) {
  const ghosts: TreeNode[] = fileNames.map((name) => ({
    name,
    isDirectory: false,
    path: `${targetDir}/${name}`,
    uploading: true,
  }))

  if (targetDir === projectRoot.value) {
    treeRoots.value = [...treeRoots.value, ...ghosts]
  } else {
    const parentNode = findNodeByPath(targetDir, treeRoots.value)
    if (parentNode && parentNode.isDirectory) {
      parentNode.children = [...(parentNode.children || []), ...ghosts]
      parentNode.expanded = true
    }
  }
}

function removeGhostNodes(targetDir: string) {
  if (targetDir === projectRoot.value) {
    treeRoots.value = treeRoots.value.filter((n) => !n.uploading)
  } else {
    const parentNode = findNodeByPath(targetDir, treeRoots.value)
    if (parentNode?.children) {
      parentNode.children = parentNode.children.filter((n) => !n.uploading)
    }
  }
}

async function handleFileUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return

  const fileList = Array.from(files)
  const targetDir = uploadTargetDir

  // Inject ghost rows immediately
  injectGhostNodes(targetDir, fileList.map((f) => f.name))

  // Upload all files in parallel
  const results = await Promise.allSettled(
    fileList.map(async (file) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('destDir', targetDir)
      await $fetch('/api/file-upload', { method: 'POST', body: formData })
    }),
  )

  // Report any failures
  results.forEach((r, i) => {
    if (r.status === 'rejected') {
      const msg = (r.reason as any)?.data?.statusMessage || `Failed to upload ${fileList[i].name}`
      console.error(msg)
    }
  })

  // Remove ghosts and refresh with real entries
  removeGhostNodes(targetDir)
  await refreshDirectory(targetDir)

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

  // External files/folders from desktop
  if (e.dataTransfer.files?.length) {
    uploadExternalFiles(e.dataTransfer, projectRoot.value)
    return
  }

  const sourcePath = e.dataTransfer.getData('text/plain')
  if (!sourcePath) return
  // Drop on background = move to project root
  const sourceParent = sourcePath.slice(0, sourcePath.lastIndexOf('/'))
  if (sourceParent === projectRoot.value) return // already there
  moveItem(sourcePath, projectRoot.value)
}

// --- Recursive folder upload helpers ---

interface PendingUpload {
  file: File
  destDir: string
}

function readEntries(reader: any): Promise<any[]> {
  return new Promise((resolve, reject) => {
    reader.readEntries((entries: any[]) => resolve(entries), reject)
  })
}

async function traverseEntry(entry: any, baseDest: string): Promise<{ dirs: string[]; files: PendingUpload[] }> {
  const dirs: string[] = []
  const files: PendingUpload[] = []

  if (entry.isFile) {
    const file: File = await new Promise((resolve, reject) => entry.file(resolve, reject))
    files.push({ file, destDir: baseDest })
  } else if (entry.isDirectory) {
    const dirPath = `${baseDest}/${entry.name}`
    dirs.push(dirPath)
    const reader = entry.createReader()
    let batch: any[]
    // readEntries returns in batches of ~100, must loop until empty
    do {
      batch = await readEntries(reader)
      for (const child of batch) {
        const sub = await traverseEntry(child, dirPath)
        dirs.push(...sub.dirs)
        files.push(...sub.files)
      }
    } while (batch.length > 0)
  }

  return { dirs, files }
}

async function uploadExternalFiles(fileListOrTransfer: FileList | DataTransfer, targetDir: string) {
  // Try to get entries for folder support
  const transfer = fileListOrTransfer instanceof DataTransfer ? fileListOrTransfer : null
  const items = transfer?.items
  let allDirs: string[] = []
  let allFiles: PendingUpload[] = []
  let ghostNames: string[] = []

  if (items) {
    // Use webkitGetAsEntry for folder detection
    const entries: any[] = []
    for (let i = 0; i < items.length; i++) {
      const entry = items[i].webkitGetAsEntry?.()
      if (entry) entries.push(entry)
    }

    if (entries.length > 0) {
      // Collect ghost names (top-level entries)
      ghostNames = entries.map((e) => e.name)
      injectGhostNodes(targetDir, ghostNames)

      for (const entry of entries) {
        const result = await traverseEntry(entry, targetDir)
        allDirs.push(...result.dirs)
        allFiles.push(...result.files)
      }
    }
  }

  // Fallback: plain FileList (no folder support)
  if (allFiles.length === 0) {
    const fileList = transfer?.files || (fileListOrTransfer as FileList)
    const files = Array.from(fileList)
    ghostNames = files.map((f) => f.name)
    injectGhostNodes(targetDir, ghostNames)
    allFiles = files.map((f) => ({ file: f, destDir: targetDir }))
  }

  // Create directories first (sorted by depth for correct order)
  allDirs.sort((a, b) => a.split('/').length - b.split('/').length)
  for (const dirPath of allDirs) {
    try {
      await $fetch('/api/files', { method: 'POST', body: { path: dirPath, type: 'folder' } })
    } catch {
      // Directory may already exist, continue
    }
  }

  // Upload files in parallel
  const results = await Promise.allSettled(
    allFiles.map(async ({ file, destDir }) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('destDir', destDir)
      await $fetch('/api/file-upload', { method: 'POST', body: formData })
    }),
  )

  results.forEach((r, i) => {
    if (r.status === 'rejected') {
      console.error(`Failed to upload ${allFiles[i].file.name}`)
    }
  })

  removeGhostNodes(targetDir)
  await refreshDirectory(targetDir)
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

function serveUrl(path: string, modified?: string) {
  let url = `/api/file-serve?path=${encodeURIComponent(path)}`
  if (modified) url += `&v=${new Date(modified).getTime()}`
  return url
}

const selectedFileServeUrl = computed(() => {
  if (!selectedFile.value) return ''
  return serveUrl(selectedFile.value.path, selectedFile.value.modified)
})

// --- DOCX viewer (mammoth.js) ---

const docxHtml = ref('')
const docxLoading = ref(false)
const docxFailed = ref(false)
let mammothPromise: Promise<void> | null = null

function loadMammoth(): Promise<void> {
  if (mammothPromise) return mammothPromise
  if ((window as any).mammoth) return Promise.resolve()
  mammothPromise = loadScript('https://cdn.jsdelivr.net/npm/mammoth@1.8.0/mammoth.browser.min.js')
  return mammothPromise
}

async function openDocx(url: string) {
  docxLoading.value = true
  docxHtml.value = ''
  docxFailed.value = false
  try {
    await loadMammoth()
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const arrayBuffer = await response.arrayBuffer()
    const result = await (window as any).mammoth.convertToHtml({ arrayBuffer })
    docxHtml.value = result.value
  } catch (err) {
    console.warn('DOCX preview unavailable:', err)
    docxFailed.value = true
  }
  docxLoading.value = false
}

// --- Spreadsheet viewer (SheetJS) ---

const sheetHtml = ref('')
const sheetNames = ref<string[]>([])
const activeSheet = ref(0)
const sheetLoading = ref(false)
let sheetWorkbook: any = null
let xlsxPromise: Promise<void> | null = null

function loadXlsx(): Promise<void> {
  if (xlsxPromise) return xlsxPromise
  if ((window as any).XLSX) return Promise.resolve()
  xlsxPromise = loadScript('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js')
  return xlsxPromise
}

async function openSpreadsheet(url: string) {
  sheetLoading.value = true
  sheetHtml.value = ''
  sheetNames.value = []
  activeSheet.value = 0
  sheetWorkbook = null
  try {
    await loadXlsx()
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const arrayBuffer = await response.arrayBuffer()
    const XLSX = (window as any).XLSX
    sheetWorkbook = XLSX.read(arrayBuffer, { type: 'array' })
    sheetNames.value = sheetWorkbook.SheetNames
    renderSheet(0)
  } catch (err) {
    console.error('Failed to load spreadsheet:', err)
    errorMessage.value = 'Failed to load spreadsheet'
  }
  sheetLoading.value = false
}

function renderSheet(index: number) {
  if (!sheetWorkbook) return
  activeSheet.value = index
  const XLSX = (window as any).XLSX
  const ws = sheetWorkbook.Sheets[sheetWorkbook.SheetNames[index]]
  sheetHtml.value = XLSX.utils.sheet_to_html(ws, { editable: false })
}

// --- EPUB reader ---

const epubContainerRef = ref<HTMLDivElement | null>(null)
let epubBook: any = null
let epubRendition: any = null
const epubLoading = ref(false)
const epubCurrentPage = ref('')

let epubJsPromise: Promise<void> | null = null

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    // Temporarily hide AMD define/require so CDN scripts don't conflict with Monaco's AMD loader
    const w = window as any
    const savedDefine = w.define
    const savedRequire = w.require
    try { w.define = undefined } catch {}

    const restore = () => {
      try {
        if (savedDefine) w.define = savedDefine
        if (savedRequire) w.require = savedRequire
      } catch {}
    }

    const script = document.createElement('script')
    script.src = src
    script.onload = () => { restore(); resolve() }
    script.onerror = () => { restore(); reject(new Error(`Failed to load ${src}`)) }
    document.head.appendChild(script)
  })
}

function loadEpubJs(): Promise<void> {
  if (epubJsPromise) return epubJsPromise
  if ((window as any).ePub) return Promise.resolve()

  epubJsPromise = (async () => {
    // epub.js requires JSZip
    if (!(window as any).JSZip) {
      await loadScript('https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js')
    }
    await loadScript('https://cdn.jsdelivr.net/npm/epubjs@0.3.93/dist/epub.min.js')
  })()
  return epubJsPromise
}

async function openEpub(url: string) {
  epubLoading.value = true
  try {
    await loadEpubJs()
    destroyEpub()

    // Wait for the container to render (it's now always in DOM when fileType is epub)
    await nextTick()
    await nextTick()

    if (!epubContainerRef.value) {
      console.error('EPUB container ref not available')
      errorMessage.value = 'Failed to initialize EPUB viewer'
      epubLoading.value = false
      return
    }

    const ePub = (window as any).ePub

    // Fetch as ArrayBuffer for reliable binary handling
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const arrayBuffer = await response.arrayBuffer()

    epubBook = ePub(arrayBuffer)
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
              <button
                class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                title="Copy path"
                @click="copyPath"
              >
                <Check v-if="pathCopied" :size="14" class="text-green-500" />
                <Copy v-else :size="14" />
              </button>
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
              class="border-r border-border bg-card/50 flex flex-col shrink-0 overflow-hidden relative"
              :style="{ width: `${sidebarWidth}px` }"
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
                    @upload="uploadExternalFiles"
                  />
                </template>
              </div>
            </div>

            <!-- Resize handle -->
            <div
              class="w-1 hover:w-1.5 cursor-col-resize bg-transparent hover:bg-primary/30 transition-all shrink-0"
              :class="isResizing ? 'w-1.5 bg-primary/40' : ''"
              @mousedown="onResizeStart"
            />

            <!-- Right panel: File viewer -->
            <div
              data-testid="file-viewer-panel"
              class="flex-1 flex flex-col min-w-0 overflow-hidden"
              :class="isResizing ? 'select-none' : ''"
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
                <div class="flex-1 min-h-0 relative">
                  <div ref="epubContainerRef" class="absolute inset-0 bg-[#1a1b26]" />
                  <div v-if="epubLoading" class="absolute inset-0 flex items-center justify-center bg-[#1a1b26]">
                    <Loader2 :size="24" class="animate-spin text-muted-foreground" />
                  </div>
                </div>
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

              <!-- DOCX file -->
              <template v-else-if="selectedFileType === 'docx'">
                <div v-if="docxLoading" class="flex-1 flex items-center justify-center">
                  <Loader2 :size="24" class="animate-spin text-muted-foreground" />
                </div>
                <div v-else-if="docxFailed" class="flex-1 flex items-center justify-center">
                  <div class="text-center space-y-3">
                    <File :size="48" class="text-muted-foreground/30 mx-auto" />
                    <div>
                      <p class="text-sm font-medium text-foreground">{{ selectedFile!.name }}</p>
                      <p class="text-xs text-muted-foreground mt-1">Preview not available for this file format</p>
                      <p class="text-xs text-muted-foreground">Size: {{ formatFileSize(selectedFile!.size) }}</p>
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
                <div v-else class="flex-1 overflow-auto p-6 bg-white">
                  <div
                    class="max-w-3xl mx-auto prose prose-sm text-gray-900"
                    v-html="docxHtml"
                  />
                </div>
              </template>

              <!-- Spreadsheet file -->
              <template v-else-if="selectedFileType === 'spreadsheet'">
                <div v-if="sheetLoading" class="flex-1 flex items-center justify-center">
                  <Loader2 :size="24" class="animate-spin text-muted-foreground" />
                </div>
                <template v-else>
                  <!-- Sheet tabs -->
                  <div v-if="sheetNames.length > 1" class="flex items-center gap-1 px-3 py-1.5 bg-muted/50 border-b border-border shrink-0 overflow-x-auto">
                    <button
                      v-for="(name, i) in sheetNames"
                      :key="name"
                      class="px-3 py-1 text-xs rounded-md transition-colors whitespace-nowrap"
                      :class="activeSheet === i
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted'"
                      @click="renderSheet(i)"
                    >
                      {{ name }}
                    </button>
                  </div>
                  <div class="flex-1 overflow-auto bg-white">
                    <div class="sheet-viewer" v-html="sheetHtml" />
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

        <!-- Download (only for files, not directories) -->
        <button
          v-if="contextMenu.node && !contextMenu.node.isDirectory"
          class="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted transition-colors text-left"
          @click="downloadItem"
        >
          <Download :size="14" class="text-muted-foreground" />
          Download
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

<style scoped>
.sheet-viewer :deep(table) {
  border-collapse: collapse;
  font-size: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-width: 100%;
}
.sheet-viewer :deep(td),
.sheet-viewer :deep(th) {
  border: 1px solid #e2e8f0;
  padding: 4px 8px;
  white-space: nowrap;
  color: #1a202c;
}
.sheet-viewer :deep(th) {
  background: #f7fafc;
  font-weight: 600;
}
.sheet-viewer :deep(tr:nth-child(even) td) {
  background: #f8fafc;
}
</style>
