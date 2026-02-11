# Implementation Report: Convex WebSocket Plugin + Composables
Generated: 2026-02-11T18:50:00Z

## Task
Rewrite Convex plugin and composables from HTTP one-shot calls (ConvexHttpClient) to real-time WebSocket subscriptions (ConvexClient). Create two new composables (useToast, useCurrentProject).

## Files Modified (3)

### `dashboard/plugins/convex.client.ts`
- Changed `ConvexHttpClient` to `ConvexClient` (WebSocket-based)
- Added `skipConvexDeploymentUrlCheck: true` for self-hosted Convex compatibility

### `dashboard/composables/useConvex.ts`
- `useConvex()` now returns `ConvexClient` instead of `ConvexHttpClient`
- `useConvexQuery()` rewritten from async one-shot to reactive subscription pattern:
  - Uses `client.onUpdate()` for WebSocket subscriptions
  - Returns `{ data, loading, error }` refs (not a Promise)
  - Supports `MaybeRefOrGetter` args for reactive re-subscription
  - Supports `'skip'` sentinel to conditionally disable subscription
  - Uses `onScopeDispose()` for automatic cleanup on component unmount
  - Passes `onError` callback to `client.onUpdate()` to capture errors
  - Watches args with `deep: true` to re-subscribe on arg changes
- `useConvexMutation()` rewritten: returns `{ mutate, loading, error }` instead of taking args directly
- `useConvexAction()` rewritten: returns `{ execute, loading, error }` instead of taking args directly

### `dashboard/composables/useAuth.ts`
- Changed `api` import from dynamic `await import()` to top-level static import
- Auth calls remain one-shot (action/mutation/query) -- not reactive subscriptions
- Added try/catch in `logout()` and `fetchUser()` for resilience
- `useConvex()` now returns `ConvexClient` transparently (same `.action()`, `.mutation()`, `.query()` API)

## Files Created (2)

### `dashboard/composables/useToast.ts`
- Global toast notification system using Nuxt's `useState`
- Methods: `show()`, `dismiss()`, `success()`, `error()`, `warning()`, `info()`
- Auto-dismiss with configurable duration (default 4s, errors 6s)
- Returns readonly `toasts` ref for rendering

### `dashboard/composables/useCurrentProject.ts`
- Loads current project from route `slug` param via `api.projects.getBySlug`
- Uses reactive `useConvexQuery` with computed args
- Supports `'skip'` when slug is not available
- Returns `{ project, loading, error, slug }`

## Verification
- `npx nuxi typecheck` reports zero errors in any of the 5 modified/created files
- All pre-existing errors (convex backend implicit anys, missing component references in test stubs) are unrelated

## API Changes Summary

| Composable | Before (HTTP) | After (WebSocket) |
|---|---|---|
| `useConvexQuery` | `await useConvexQuery(fn, args)` returns `Promise<T>` | `useConvexQuery(fn, args)` returns `{ data, loading, error }` refs |
| `useConvexMutation` | `await useConvexMutation(fn, args)` returns `Promise<T>` | `const { mutate } = useConvexMutation(fn)` then `await mutate(args)` |
| `useConvexAction` | `await useConvexAction(fn, args)` returns `Promise<T>` | `const { execute } = useConvexAction(fn)` then `await execute(args)` |

## Notes
- ConvexClient's `onUpdate()` returns an `Unsubscribe` object that is callable as a function -- we use `unsub()` for cleanup
- The `onUpdate` 4th parameter `onError` is used to capture subscription errors into the `error` ref
- All Vue imports (ref, watch, toValue, etc.) are explicit in composable files for clarity, even though Nuxt auto-imports them in .vue files
- The `api` import path from composables is `../../convex/_generated/api` (two levels up from dashboard/composables/)
