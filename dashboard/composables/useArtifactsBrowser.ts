import { ref, readonly } from 'vue'

// Shared state across all components (module-level singleton)
const isOpen = ref(false)
const initialPath = ref<string | null>(null)

export function useArtifactsBrowser() {
  function open(path?: string) {
    isOpen.value = true
    initialPath.value = path || null
  }

  function close() {
    isOpen.value = false
    initialPath.value = null
  }

  return {
    isOpen: readonly(isOpen),
    initialPath: readonly(initialPath),
    open,
    close,
  }
}
