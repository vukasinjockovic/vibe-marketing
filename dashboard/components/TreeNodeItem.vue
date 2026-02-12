<script setup lang="ts">
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
</script>

<template>
  <div>
    <button
      class="w-full flex items-center gap-1 px-2 py-1 text-xs text-left hover:bg-muted/60 transition-colors group"
      :class="isSelected ? 'bg-primary/10 text-primary' : 'text-foreground'"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      @click="handleClick"
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
      />
    </template>
  </div>
</template>
