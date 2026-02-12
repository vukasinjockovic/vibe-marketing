<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import {
  Folder,
  FolderOpen,
  FileText,
  FileImage,
  FileVideo,
  FileCode,
  File,
  ChevronRight,
  ChevronDown,
  Loader2,
} from 'lucide-vue-next'

interface TreeNode {
  name: string
  isDirectory: boolean
  path: string
  size?: number
  modified?: string
  children?: TreeNode[]
  expanded?: boolean
  loading?: boolean
}

const props = defineProps<{
  node: TreeNode
  depth: number
  selectedPath: string
}>()

const emit = defineEmits<{
  toggle: [node: TreeNode]
  select: [node: TreeNode]
  contextmenu: [event: MouseEvent, node: TreeNode]
  drop: [sourcePath: string, destDirPath: string]
}>()

const IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'])
const VIDEO_EXTENSIONS = new Set(['.mp4', '.webm'])
const CODE_EXTENSIONS = new Set(['.js', '.ts', '.vue', '.jsx', '.tsx', '.py', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.sh'])
const TEXT_EXTENSIONS = new Set(['.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css', '.xml', '.csv', '.toml', '.sql'])

function getExtension(name: string): string {
  const dotIndex = name.lastIndexOf('.')
  return dotIndex >= 0 ? name.slice(dotIndex).toLowerCase() : ''
}

function getFileIcon(node: TreeNode) {
  if (node.isDirectory) {
    return node.expanded ? FolderOpen : Folder
  }
  const ext = getExtension(node.name)
  if (IMAGE_EXTENSIONS.has(ext)) return FileImage
  if (VIDEO_EXTENSIONS.has(ext)) return FileVideo
  if (CODE_EXTENSIONS.has(ext)) return FileCode
  if (TEXT_EXTENSIONS.has(ext)) return FileText
  return File
}

function getFileIconColor(node: TreeNode): string {
  if (node.isDirectory) return 'text-blue-400'
  const ext = getExtension(node.name)
  if (IMAGE_EXTENSIONS.has(ext)) return 'text-green-400'
  if (VIDEO_EXTENSIONS.has(ext)) return 'text-purple-400'
  if (CODE_EXTENSIONS.has(ext)) return 'text-yellow-400'
  if (TEXT_EXTENSIONS.has(ext)) return 'text-muted-foreground'
  return 'text-muted-foreground/50'
}

function handleClick() {
  if (props.node.isDirectory) {
    emit('toggle', props.node)
  } else {
    emit('select', props.node)
  }
}

const isSelected = computed(() => props.node.path === props.selectedPath)

// --- Drag & Drop ---

const isDragOver = ref(false)
let hoverExpandTimer: ReturnType<typeof setTimeout> | null = null

function onDragStart(e: DragEvent) {
  if (!e.dataTransfer) return
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', props.node.path)
}

function onDragOver(e: DragEvent) {
  if (!props.node.isDirectory) return
  e.preventDefault()
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'

  if (!isDragOver.value) {
    isDragOver.value = true
    // Auto-expand closed folders after 600ms hover
    if (!props.node.expanded && !props.node.loading) {
      hoverExpandTimer = setTimeout(() => {
        if (isDragOver.value) {
          emit('toggle', props.node)
        }
      }, 600)
    }
  }
}

function onDragLeave(e: DragEvent) {
  isDragOver.value = false
  if (hoverExpandTimer) {
    clearTimeout(hoverExpandTimer)
    hoverExpandTimer = null
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  e.stopPropagation()
  isDragOver.value = false
  if (hoverExpandTimer) {
    clearTimeout(hoverExpandTimer)
    hoverExpandTimer = null
  }

  if (!props.node.isDirectory || !e.dataTransfer) return
  const sourcePath = e.dataTransfer.getData('text/plain')
  if (!sourcePath || sourcePath === props.node.path) return
  // Don't drop into own parent (same location = noop)
  const sourceParent = sourcePath.slice(0, sourcePath.lastIndexOf('/'))
  if (sourceParent === props.node.path) return

  emit('drop', sourcePath, props.node.path)
}

onUnmounted(() => {
  if (hoverExpandTimer) {
    clearTimeout(hoverExpandTimer)
  }
})
</script>

<template>
  <div>
    <button
      class="w-full flex items-center gap-1 px-2 py-1 text-xs text-left transition-colors group"
      :class="[
        isSelected ? 'bg-primary/10 text-primary' : 'text-foreground hover:bg-muted/60',
        isDragOver && node.isDirectory ? 'bg-primary/20 ring-1 ring-primary/40' : '',
      ]"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      draggable="true"
      @click="handleClick"
      @contextmenu.prevent.stop="emit('contextmenu', $event, node)"
      @dragstart="onDragStart"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <!-- Expand/collapse chevron for directories -->
      <template v-if="node.isDirectory">
        <Loader2 v-if="node.loading" :size="12" class="shrink-0 animate-spin text-muted-foreground" />
        <ChevronDown v-else-if="node.expanded" :size="12" class="shrink-0 text-muted-foreground" />
        <ChevronRight v-else :size="12" class="shrink-0 text-muted-foreground" />
      </template>
      <span v-else class="w-3 shrink-0" />

      <!-- File icon -->
      <component
        :is="getFileIcon(node)"
        :size="14"
        class="shrink-0"
        :class="getFileIconColor(node)"
      />

      <!-- File name -->
      <span class="truncate">{{ node.name }}</span>
    </button>

    <!-- Children (recursive) -->
    <template v-if="node.isDirectory && node.expanded && node.children">
      <TreeNodeItem
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :depth="depth + 1"
        :selected-path="selectedPath"
        @toggle="emit('toggle', $event)"
        @select="emit('select', $event)"
        @contextmenu="(e: MouseEvent, n: any) => emit('contextmenu', e, n)"
        @drop="(s: string, d: string) => emit('drop', s, d)"
      />
    </template>
  </div>
</template>
