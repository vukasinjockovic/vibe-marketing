// Global test setup - provides Nuxt auto-import globals for test environment
// This file is loaded before any test via vitest.config.ts setupFiles

import {
  ref,
  reactive,
  computed,
  watch,
  readonly,
  onMounted,
  onUnmounted,
  nextTick,
  toRef,
  toRefs,
  watchEffect,
} from 'vue'

// Provide Vue composition API as globals (Nuxt auto-imports these)
Object.assign(globalThis, {
  ref,
  reactive,
  computed,
  watch,
  readonly,
  onMounted,
  onUnmounted,
  nextTick,
  toRef,
  toRefs,
  watchEffect,
})

// VToast uses useToast() as a Nuxt auto-imported global.
// We provide a mock implementation here that individual tests can override.
if (!(globalThis as any).__useToastMock) {
  const mockToasts = ref<Array<{ id: number; type: string; message: string }>>([])
  const mockDismiss = () => {};
  (globalThis as any).__useToastMock = { toasts: mockToasts, dismiss: mockDismiss };
  (globalThis as any).useToast = () => (globalThis as any).__useToastMock
}

// Provide Nuxt auto-import stubs that individual tests can override via vi.stubGlobal
if (!(globalThis as any).navigateTo) {
  (globalThis as any).navigateTo = () => {}
}
if (!(globalThis as any).useRoute) {
  (globalThis as any).useRoute = () => ({ params: {}, path: '/', query: {} })
}
if (!(globalThis as any).useState) {
  (globalThis as any).useState = (key: string, init: () => any) => ref(init ? init() : undefined)
}
if (!(globalThis as any).useConvexQuery) {
  (globalThis as any).useConvexQuery = () => ({ data: ref(undefined), loading: ref(false), error: ref(null) })
}
if (!(globalThis as any).useConvexMutation) {
  (globalThis as any).useConvexMutation = () => ({ mutate: async () => {}, loading: ref(false), error: ref(null) })
}
if (!(globalThis as any).useCurrentProject) {
  (globalThis as any).useCurrentProject = () => ({
    project: ref(null), loading: ref(false), error: ref(null), slug: computed(() => ''),
  })
}
