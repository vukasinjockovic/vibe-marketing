import { ConvexClient } from 'convex/browser'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  // Derive Convex URL: use explicit env var, or auto-detect from current origin + /convex/
  const convexUrl = config.public.convexUrl
    || `${window.location.origin}/convex`

  const client = new ConvexClient(convexUrl as string, {
    skipConvexDeploymentUrlCheck: true, // Required for self-hosted Convex
  })

  return {
    provide: {
      convex: client,
    },
  }
})
