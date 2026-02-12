<script setup lang="ts">
const props = defineProps<{
  name: string
  isDirectory: boolean
  expanded?: boolean
  size?: number
}>()

// --- Extension → icon mapping ---

const EXT_ICON_MAP: Record<string, string> = {
  // JavaScript / TypeScript
  '.js': 'javascript',
  '.mjs': 'javascript',
  '.cjs': 'javascript',
  '.ts': 'typescript',
  '.mts': 'typescript',
  '.cts': 'typescript',
  '.jsx': 'jsx',
  '.tsx': 'tsx',
  '.vue': 'vue',

  // Web
  '.html': 'html',
  '.htm': 'html',
  '.css': 'css',
  '.scss': 'css',
  '.less': 'css',
  '.svg': 'svg',

  // Data
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.xml': 'xml',
  '.csv': 'csv',
  '.toml': 'toml',

  // Docs
  '.md': 'markdown',
  '.mdx': 'markdown',
  '.txt': 'text',
  '.pdf': 'pdf',
  '.docx': 'document',
  '.doc': 'document',
  '.epub': 'document',

  // Spreadsheets
  '.xlsx': 'table',
  '.xls': 'table',
  '.ods': 'table',

  // Images
  '.png': 'image',
  '.jpg': 'image',
  '.jpeg': 'image',
  '.gif': 'image',
  '.webp': 'image',
  '.ico': 'image',

  // Video
  '.mp4': 'video',
  '.webm': 'video',
  '.mov': 'video',
  '.avi': 'video',

  // Audio
  '.mp3': 'audio',
  '.wav': 'audio',
  '.ogg': 'audio',
  '.flac': 'audio',

  // Languages
  '.py': 'python',
  '.rb': 'ruby',
  '.go': 'go',
  '.rs': 'rust',
  '.java': 'java',
  '.c': 'c',
  '.cpp': 'cpp',
  '.h': 'c',
  '.hpp': 'cpp',

  // Shell / Config
  '.sh': 'console',
  '.bash': 'console',
  '.zsh': 'console',
  '.fish': 'console',
  '.sql': 'database',
  '.ini': 'config',
  '.cfg': 'config',
  '.conf': 'config',
  '.env': 'env',

  // Archives
  '.zip': 'zip',
  '.tar': 'zip',
  '.gz': 'zip',
  '.rar': 'zip',
  '.7z': 'zip',

  // Git / Docker / Package
  '.gitignore': 'git',
  '.gitmodules': 'git',
  '.dockerfile': 'docker',

  // Lock files
  '.lock': 'lock',
}

// Exact filename → icon mapping
const NAME_ICON_MAP: Record<string, string> = {
  'readme.md': 'readme',
  'readme': 'readme',
  'dockerfile': 'docker',
  'docker-compose.yml': 'docker',
  'docker-compose.yaml': 'docker',
  '.gitignore': 'git',
  '.gitmodules': 'git',
  '.env': 'env',
  '.env.local': 'env',
  '.env.production': 'env',
  '.env.development': 'env',
  'package.json': 'npm',
  'package-lock.json': 'lock',
  'yarn.lock': 'lock',
  'pnpm-lock.yaml': 'lock',
  'tsconfig.json': 'typescript',
  'nuxt.config.ts': 'config',
  'vite.config.ts': 'config',
  'vitest.config.ts': 'config',
}

// Directory name → folder icon mapping
const DIR_ICON_MAP: Record<string, string> = {
  src: 'folder-src',
  source: 'folder-src',
  components: 'folder-components',
  config: 'folder-config',
  configs: 'folder-config',
  configuration: 'folder-config',
  images: 'folder-images',
  img: 'folder-images',
  assets: 'folder-images',
  scripts: 'folder-scripts',
  dist: 'folder-dist',
  build: 'folder-dist',
  output: 'folder-dist',
  node_modules: 'folder-node',
  test: 'folder-test',
  tests: 'folder-test',
  __tests__: 'folder-test',
  spec: 'folder-test',
}

function getExtension(name: string): string {
  const dotIndex = name.lastIndexOf('.')
  return dotIndex >= 0 ? name.slice(dotIndex).toLowerCase() : ''
}

const iconPath = computed(() => {
  const name = props.name.toLowerCase()

  if (props.isDirectory) {
    const dirIcon = DIR_ICON_MAP[name]
    if (dirIcon) {
      // return `/file-icons/${props.expanded ? dirIcon + '-open' : dirIcon}.svg`
      return `/file-icons/${dirIcon}.svg`
    }
    // return `/file-icons/${props.expanded ? 'folder-open' : 'folder'}.svg`
    return `/file-icons/folder.svg`
  }

  // Check exact filename first
  const nameIcon = NAME_ICON_MAP[name]
  if (nameIcon) return `/file-icons/${nameIcon}.svg`

  // Then extension
  const ext = getExtension(name)
  const extIcon = EXT_ICON_MAP[ext]
  if (extIcon) return `/file-icons/${extIcon}.svg`

  return '/file-icons/file.svg'
})
</script>

<template>
  <img
    :src="iconPath"
    :width="size || 16"
    :height="size || 16"
    class="shrink-0"
    draggable="false"
  />
</template>
