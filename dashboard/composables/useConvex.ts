import type { ConvexClient } from 'convex/browser'
import type { FunctionReference, FunctionArgs, FunctionReturnType } from 'convex/server'
import { ref, watch, toValue, onScopeDispose, type MaybeRefOrGetter, type Ref } from 'vue'

export function useConvex(): ConvexClient {
  const { $convex } = useNuxtApp()
  return $convex as ConvexClient
}

// Reactive query — subscribes via WebSocket, auto-updates when backend data changes
export function useConvexQuery<F extends FunctionReference<'query'>>(
  fn: F,
  args: MaybeRefOrGetter<FunctionArgs<F> | 'skip'>,
): { data: Ref<FunctionReturnType<F> | undefined>; loading: Ref<boolean>; error: Ref<Error | null> } {
  const client = useConvex()
  const data = ref<FunctionReturnType<F>>() as Ref<FunctionReturnType<F> | undefined>
  const loading = ref(true)
  const error = ref<Error | null>(null)
  let unsub: (() => void) | null = null

  function subscribe() {
    if (unsub) {
      unsub()
      unsub = null
    }
    const resolvedArgs = toValue(args)
    if (resolvedArgs === 'skip') {
      loading.value = false
      return
    }
    loading.value = true
    error.value = null
    unsub = client.onUpdate(
      fn,
      resolvedArgs,
      (result) => {
        data.value = result
        loading.value = false
      },
      (e) => {
        error.value = e
        loading.value = false
      },
    )
  }

  subscribe()

  // Re-subscribe when args change (for filtered queries)
  watch(() => toValue(args), () => subscribe(), { deep: true })

  // Auto-cleanup on component unmount
  onScopeDispose(() => {
    if (unsub) unsub()
  })

  return { data, loading, error }
}

// Mutation wrapper — returns { mutate } function
export function useConvexMutation<F extends FunctionReference<'mutation'>>(fn: F) {
  const client = useConvex()
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function mutate(args: FunctionArgs<F>): Promise<FunctionReturnType<F>> {
    loading.value = true
    error.value = null
    try {
      const result = await client.mutation(fn, args)
      return result
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      loading.value = false
    }
  }

  return { mutate, loading, error }
}

// Action wrapper — returns { execute } function
export function useConvexAction<F extends FunctionReference<'action'>>(fn: F) {
  const client = useConvex()
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(args: FunctionArgs<F>): Promise<FunctionReturnType<F>> {
    loading.value = true
    error.value = null
    try {
      const result = await client.action(fn, args)
      return result
    } catch (e) {
      error.value = e as Error
      throw e
    } finally {
      loading.value = false
    }
  }

  return { execute, loading, error }
}
