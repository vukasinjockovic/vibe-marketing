import { ref, readonly } from 'vue'

// Shared state across all components (module-level singleton)
const isOpen = ref(false)
const initialPath = ref<string | null>(null)
const projectSlug = ref<string | null>(null)

export function useArtifactsBrowser() {
  function open(path?: string, slug?: string) {
    if (!slug) return // Only open when a project slug is provided
    projectSlug.value = slug
    isOpen.value = true
    initialPath.value = path || null
  }

  function close() {
    isOpen.value = false
    initialPath.value = null
    projectSlug.value = null
  }

  return {
    isOpen: readonly(isOpen),
    initialPath: readonly(initialPath),
    projectSlug: readonly(projectSlug),
    open,
    close,
  }
}
