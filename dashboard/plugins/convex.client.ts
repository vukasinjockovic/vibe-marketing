import { ConvexClient } from 'convex/browser'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const client = new ConvexClient(config.public.convexUrl as string, {
    skipConvexDeploymentUrlCheck: true, // Required for self-hosted Convex
  })

  return {
    provide: {
      convex: client,
    },
  }
})
