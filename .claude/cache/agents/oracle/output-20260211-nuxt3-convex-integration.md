# Research Report: Nuxt 3 + Self-Hosted Convex Integration
Generated: 2026-02-11

## Summary

There is NO official Convex-maintained Nuxt plugin. The community `convex-nuxt` module (by chris-visser) wraps `convex-vue` and provides composables like `useConvexQuery`, `useConvexMutation`, and `useConvexClient`. However, this project's auth model (plain UUID session tokens in cookies, not JWT/OIDC) means we cannot use Convex's built-in `setAuth()` mechanism. Instead, session tokens must be passed as regular arguments to queries/mutations. The recommended approach is: use `convex-nuxt` for real-time subscriptions on the client, use `ConvexHttpClient` in Nitro server routes for SSR, and manage auth cookies via Nuxt's `useCookie` composable.

## Questions Answered

### Q1: Is there an official Convex Nuxt integration, or do we use the plain convex JS client?

**Answer:** No official Convex-maintained Nuxt plugin exists. Two community options:

1. **`convex-nuxt`** (by chris-visser) -- The one referenced in Convex's official docs. Wraps `convex-vue` (@convex-vue/core). Provides auto-imported composables (`useConvexQuery`, `useConvexMutation`, `useConvexAction`, `useConvexClient`). Simple Nuxt module registration.

2. **`better-convex-nuxt`** (by lupinum-dev) -- More opinionated. Adds SSR-first data fetching with automatic WebSocket upgrade, Better Auth integration, optimistic updates with rollback. Newer, less battle-tested.

3. **Roll your own** -- Use `ConvexClient` (WebSocket, reactive) on the client and `ConvexHttpClient` (stateless HTTP) on the server via a Nuxt plugin. Most control, most work.

**Recommendation for this project:** Use `convex-nuxt` for the client-side reactive layer. Add a custom Nitro server utility using `ConvexHttpClient` for server-side queries. Custom auth middleware for cookie-based session tokens.

**Source:** https://docs.convex.dev/client/vue/nuxt, https://github.com/chris-visser/convex-nuxt
**Confidence:** High

### Q2: How to set up the ConvexClient in a Nuxt 3 app (plugin? composable?)

**Answer:** With `convex-nuxt`, it's a Nuxt module -- no manual plugin needed. The module auto-registers composables.

**Setup:**

```bash
# Install
npm install convex convex-nuxt
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['convex-nuxt'],
  convex: {
    // For self-hosted: use the plain HTTP URL
    url: process.env.CONVEX_URL || 'http://localhost:3210',
  },
  runtimeConfig: {
    // Server-only (not exposed to client)
    convexUrl: process.env.CONVEX_URL || 'http://localhost:3210',
    // Public (exposed to client)
    public: {
      convexUrl: process.env.CONVEX_URL || 'http://localhost:3210',
    },
  },
})
```

```
# .env
CONVEX_URL=http://localhost:3210
```

The module internally creates a `ConvexClient` instance and provides it via Vue's `provide/inject`. Composables like `useConvexQuery` are auto-imported.

**Source:** https://docs.convex.dev/quickstart/nuxt, https://github.com/chris-visser/convex-nuxt
**Confidence:** High

### Q3: How to handle auth (session tokens stored in cookies) with Convex queries/mutations

**Answer:** This is the most important architectural question. The project uses **custom session tokens** (UUID strings stored in a `sessions` table), NOT JWT/OIDC tokens. This means:

- **Cannot use** Convex's built-in `client.setAuth()` (expects JWT tokens with OIDC claims)
- **Must pass** the session token as a regular argument to every authenticated query/mutation
- **Store token** in an httpOnly cookie for security

**Pattern: Auth Composable**

```typescript
// composables/useAuth.ts
import { api } from '~/convex/_generated/api'

export const useAuth = () => {
  // useCookie works on both SSR and CSR
  const sessionToken = useCookie('session_token', {
    maxAge: 30 * 24 * 60 * 60, // 30 days (matches Convex session TTL)
    httpOnly: false, // Must be false for client-side JS access
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })

  const user = useState<any>('auth_user', () => null)
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = ref(false)

  // Validate session on app init (SSR + CSR)
  const validateSession = async () => {
    if (!sessionToken.value) {
      user.value = null
      return
    }
    try {
      // Use ConvexHttpClient for one-shot validation
      const { ConvexHttpClient } = await import('convex/browser')
      const httpClient = new ConvexHttpClient(useRuntimeConfig().public.convexUrl)
      const result = await httpClient.query(api.auth.validateSession, {
        token: sessionToken.value,
      })
      user.value = result
      if (!result) {
        sessionToken.value = null // Clear invalid token
      }
    } catch (e) {
      user.value = null
      sessionToken.value = null
    }
  }

  // Sign in
  const signIn = async (email: string, password: string) => {
    isLoading.value = true
    try {
      const { ConvexHttpClient } = await import('convex/browser')
      const httpClient = new ConvexHttpClient(useRuntimeConfig().public.convexUrl)
      const result = await httpClient.action(api.auth.signIn, { email, password })
      sessionToken.value = result.token
      user.value = result.user
      return result
    } finally {
      isLoading.value = false
    }
  }

  // Sign out
  const signOut = async () => {
    if (sessionToken.value) {
      try {
        const { ConvexHttpClient } = await import('convex/browser')
        const httpClient = new ConvexHttpClient(useRuntimeConfig().public.convexUrl)
        await httpClient.mutation(api.auth.signOut, { token: sessionToken.value })
      } catch (e) {
        // Ignore -- token may already be expired
      }
    }
    sessionToken.value = null
    user.value = null
    navigateTo('/login')
  }

  return {
    sessionToken: readonly(sessionToken),
    user: readonly(user),
    isAuthenticated,
    isLoading,
    signIn,
    signOut,
    validateSession,
  }
}
```

**Pattern: Passing token to every query/mutation**

Since Convex's built-in auth doesn't apply here, every authenticated query/mutation in the Convex backend already expects `{ token: string }` as an argument. On the frontend:

```typescript
// In a component
const { sessionToken } = useAuth()

// Reactive query -- will re-run when token changes
const { data: tasks } = useConvexQuery(
  api.tasks.listByProject,
  computed(() =>
    sessionToken.value
      ? { token: sessionToken.value, projectId: someProjectId }
      : 'skip' // convex-vue skips query when args are 'skip'
  )
)
```

**Source:** Custom analysis of `/var/www/vibe-marketing/convex/auth.ts`
**Confidence:** High

### Q4: Best practices for SSR with Convex (should queries run server-side or client-side only?)

**Answer:** This depends on the query type:

**Client-side only (recommended for most cases):**
- Real-time data (tasks, messages, notifications) -- use `useConvexQuery` which subscribes via WebSocket
- Data that changes frequently
- User-specific data after auth

**Server-side (Nitro routes/middleware):**
- Auth validation in middleware (read cookie, validate session)
- SEO-critical pages (if any -- marketing dashboard is typically not public)
- Initial page load optimization

**SSR Pattern with ConvexHttpClient:**

```typescript
// server/utils/convex.ts
import { ConvexHttpClient } from 'convex/browser'

let _client: ConvexHttpClient | null = null

export function getConvexHttpClient(): ConvexHttpClient {
  if (!_client) {
    const config = useRuntimeConfig()
    _client = new ConvexHttpClient(config.convexUrl)
  }
  return _client
}

// Helper for authenticated server-side queries
export async function serverConvexQuery<T>(
  query: any,
  args: Record<string, any>
): Promise<T> {
  const client = getConvexHttpClient()
  return await client.query(query, args) as T
}
```

```typescript
// server/middleware/auth.ts
import { api } from '~/convex/_generated/api'
import { getConvexHttpClient } from '~/server/utils/convex'

export default defineEventHandler(async (event) => {
  // Only protect /api/ routes and dashboard pages
  const path = getRequestURL(event).pathname
  if (path.startsWith('/api/') || path.startsWith('/dashboard')) {
    const token = getCookie(event, 'session_token')
    if (!token) {
      event.context.user = null
      return
    }
    try {
      const client = getConvexHttpClient()
      const user = await client.query(api.auth.validateSession, { token })
      event.context.user = user
      event.context.sessionToken = token
    } catch {
      event.context.user = null
    }
  }
})
```

**Important caveat:** `ConvexHttpClient` is stateless -- it makes one-shot HTTP requests, NOT WebSocket subscriptions. It's appropriate for server-side use but does NOT provide reactivity. For reactive data, always use the client-side `useConvexQuery`.

**Source:** https://docs.convex.dev/api/classes/browser.ConvexHttpClient, https://docs.convex.dev/client/nextjs/app-router/server-rendering
**Confidence:** High

### Q5: Any existing Nuxt 3 + Convex examples or templates?

**Answer:** Limited options:

1. **Convex Nuxt Quickstart** -- Minimal todo app example in official docs
   - Source: https://docs.convex.dev/quickstart/nuxt

2. **better-convex-nuxt demo** -- More complete with auth, SSR, optimistic updates
   - Source: https://better-convex-nuxt.vercel.app/
   - GitHub: https://github.com/lupinum-dev/better-convex-nuxt

3. **convex-vue-vite-template** -- Vue (not Nuxt) template
   - GitHub: https://github.com/loicpennequin/convex-vue-vite-template

4. **No self-hosted Nuxt example exists** -- All examples assume Convex Cloud

**Source:** Multiple GitHub searches
**Confidence:** High

## Detailed Implementation Guide

### 1. nuxt.config.ts

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    'convex-nuxt',
    // Other modules...
  ],

  // convex-nuxt module config
  convex: {
    url: process.env.CONVEX_URL || 'http://localhost:3210',
  },

  // Runtime config for server-side ConvexHttpClient
  runtimeConfig: {
    convexUrl: process.env.CONVEX_URL || 'http://localhost:3210',
    public: {
      convexUrl: process.env.CONVEX_URL || 'http://localhost:3210',
    },
  },

  // Ensure convex client code is not SSR'd (WebSocket doesn't work server-side)
  // convex-nuxt handles this automatically, but just in case:
  build: {
    transpile: ['convex'],
  },
})
```

### 2. Convex Client Plugin (if NOT using convex-nuxt module)

If you choose to skip `convex-nuxt` and wire it manually:

```typescript
// plugins/convex.client.ts
// Note: .client.ts suffix means this only runs in browser
import { ConvexClient } from 'convex/browser'
import { api } from '~/convex/_generated/api'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const client = new ConvexClient(config.public.convexUrl)

  // Make client available throughout the app
  nuxtApp.provide('convex', client)
  nuxtApp.provide('convexApi', api)

  // Cleanup on app unmount
  nuxtApp.hook('app:beforeMount', () => {
    // Client is ready
  })

  // Note: Don't call client.close() on unmount in SPA mode
  // Only close if doing full page navigation away
})
```

```typescript
// composables/useConvex.ts (manual version)
import type { ConvexClient } from 'convex/browser'

export const useConvex = () => {
  const nuxtApp = useNuxtApp()
  return nuxtApp.$convex as ConvexClient
}
```

### 3. useConvex() Composable (with convex-nuxt)

With `convex-nuxt` installed, composables are auto-imported. Here's how to use them:

```typescript
// composables/useConvexAuth.ts
// Wraps convex-nuxt composables with auth token injection
import { api } from '~/convex/_generated/api'

export const useConvexAuth = () => {
  const sessionToken = useCookie('session_token', {
    maxAge: 30 * 24 * 60 * 60,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  })

  // Wrapper that injects token into args
  const useAuthQuery = <T>(
    queryFn: any,
    args: MaybeRefOrGetter<Record<string, any> | 'skip'>
  ) => {
    return useConvexQuery(
      queryFn,
      computed(() => {
        const resolvedArgs = toValue(args)
        if (resolvedArgs === 'skip' || !sessionToken.value) return 'skip'
        return { ...resolvedArgs, token: sessionToken.value }
      })
    )
  }

  const useAuthMutation = (mutationFn: any) => {
    const { mutate: rawMutate, ...rest } = useConvexMutation(mutationFn)
    const mutate = (args: Record<string, any>) => {
      if (!sessionToken.value) throw new Error('Not authenticated')
      return rawMutate({ ...args, token: sessionToken.value })
    }
    return { mutate, ...rest }
  }

  const useAuthAction = (actionFn: any) => {
    const client = useConvexClient()
    const execute = async (args: Record<string, any>) => {
      if (!sessionToken.value) throw new Error('Not authenticated')
      return await client.action(actionFn, { ...args, token: sessionToken.value })
    }
    return { execute }
  }

  return {
    sessionToken,
    useAuthQuery,
    useAuthMutation,
    useAuthAction,
  }
}
```

### 4. Auth Middleware

```typescript
// middleware/auth.ts (Nuxt route middleware, runs on client + SSR)
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, validateSession, isAuthenticated } = useAuth()

  // Skip for public routes
  const publicRoutes = ['/login', '/signup', '/forgot-password']
  if (publicRoutes.includes(to.path)) return

  // Validate session if not already done
  if (!user.value) {
    await validateSession()
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
```

```typescript
// middleware/auth.global.ts (alternative: global middleware)
export default defineNuxtRouteMiddleware(async (to) => {
  // Public routes that don't need auth
  if (to.path === '/login' || to.path === '/signup') return

  const sessionToken = useCookie('session_token')
  if (!sessionToken.value) {
    return navigateTo('/login')
  }
})
```

```typescript
// server/middleware/01.auth.ts (Nitro server middleware)
import { api } from '~/convex/_generated/api'

export default defineEventHandler(async (event) => {
  const path = getRequestURL(event).pathname

  // Skip auth for public paths
  if (path === '/login' || path === '/signup' || path.startsWith('/_nuxt')) {
    return
  }

  const token = getCookie(event, 'session_token')
  if (token) {
    try {
      const { ConvexHttpClient } = await import('convex/browser')
      const config = useRuntimeConfig()
      const client = new ConvexHttpClient(config.convexUrl)
      const user = await client.query(api.auth.validateSession, { token })
      event.context.user = user
      event.context.sessionToken = token
    } catch {
      event.context.user = null
    }
  }
})
```

### 5. Server-Side Convex Utility

```typescript
// server/utils/convex.ts
import { ConvexHttpClient } from 'convex/browser'

let httpClient: ConvexHttpClient | null = null

export function useServerConvex(): ConvexHttpClient {
  if (!httpClient) {
    const config = useRuntimeConfig()
    httpClient = new ConvexHttpClient(config.convexUrl)
  }
  return httpClient
}
```

```typescript
// server/api/projects/index.get.ts (example Nitro API route)
import { api } from '~/convex/_generated/api'

export default defineEventHandler(async (event) => {
  if (!event.context.user) {
    throw createError({ statusCode: 401, message: 'Unauthorized' })
  }

  const client = useServerConvex()
  const projects = await client.query(api.projects.list, {
    token: event.context.sessionToken,
  })

  return projects
})
```

### 6. Example Page Component

```vue
<!-- pages/dashboard/projects/index.vue -->
<script setup lang="ts">
import { api } from '~/convex/_generated/api'

definePageMeta({
  middleware: 'auth',
})

const { useAuthQuery } = useConvexAuth()

// Reactive query -- auto-subscribes via WebSocket, re-renders on changes
const { data: projects, isPending } = useAuthQuery(
  api.projects.list,
  {} // no extra args beyond the token (injected by useAuthQuery)
)
</script>

<template>
  <div>
    <h1>Projects</h1>
    <div v-if="isPending">Loading...</div>
    <div v-else-if="projects">
      <div v-for="project in projects" :key="project._id">
        {{ project.name }}
      </div>
    </div>
  </div>
</template>
```

### 7. Login Page

```vue
<!-- pages/login.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { signIn, isLoading } = useAuth()
const email = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  try {
    await signIn(email.value, password.value)
    navigateTo('/dashboard')
  } catch (e: any) {
    error.value = e.message || 'Login failed'
  }
}
</script>

<template>
  <form @submit.prevent="handleLogin">
    <input v-model="email" type="email" placeholder="Email" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <p v-if="error" class="error">{{ error }}</p>
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? 'Signing in...' : 'Sign In' }}
    </button>
  </form>
</template>
```

## Architecture Decision: Why NOT use convex-nuxt's built-in auth

The `convex-nuxt` module supports `setAuth()` which is designed for JWT/OIDC providers (Clerk, Auth0). This project uses custom session tokens:

| Feature | JWT/OIDC (setAuth) | Custom Session Tokens (this project) |
|---------|-------------------|--------------------------------------|
| Token format | JWT with claims | UUID string |
| Validation | Convex verifies JWT signature | App queries `sessions` table |
| Identity in functions | `ctx.auth.getUserIdentity()` | Manual: query session by token arg |
| Token refresh | Built-in via OIDC | Manual: 30-day expiry, no refresh |
| Client integration | `client.setAuth(getToken)` | Pass token as arg to every call |

Since auth.ts already works with `{ token: string }` args on every function, the right approach is to wrap the composables with a token-injection layer (see `useConvexAuth` above) rather than trying to retrofit JWT auth.

## Self-Hosted URL Considerations

For self-hosted Convex at `http://localhost:3210`:

1. **No TLS/WSS** -- The ConvexClient will connect via `ws://` not `wss://`. This is fine for local dev.
2. **CORS** -- Self-hosted Convex may need CORS headers if the dashboard runs on a different port (e.g., `:3000`). Check Convex self-hosted CORS config.
3. **Environment variable** -- Use `CONVEX_URL=http://localhost:3210` in `.env`. Do NOT use `CONVEX_DEPLOYMENT` (that's for Convex Cloud).
4. **Production** -- In production, use a real domain with TLS: `https://convex.yourdomain.com`.

## Recommended File Structure

```
dashboard/
├── nuxt.config.ts            # Module registration + runtimeConfig
├── .env                      # CONVEX_URL=http://localhost:3210
├── composables/
│   ├── useAuth.ts            # Auth state, signIn, signOut, validateSession
│   └── useConvexAuth.ts      # Token-injecting wrappers for convex-nuxt composables
├── middleware/
│   ├── auth.ts               # Route guard (redirect to /login)
│   └── guest.ts              # Redirect authenticated users away from /login
├── server/
│   ├── middleware/
│   │   └── 01.auth.ts        # Nitro: validate cookie, set event.context.user
│   └── utils/
│       └── convex.ts         # ConvexHttpClient singleton for server-side
├── plugins/
│   └── auth.client.ts        # Auto-validate session on app mount
├── pages/
│   ├── login.vue
│   └── dashboard/
│       └── index.vue
└── convex/                   # Symlink or copy from project root
    └── _generated/
        └── api.d.ts
```

## Open Questions

1. **convex-nuxt + self-hosted URL** -- The `convex-nuxt` module may internally use `CONVEX_URL` or `NUXT_CONVEX_URL`. Need to verify it accepts a plain `http://` URL and not just `.convex.cloud` URLs. If it rejects it, fall back to manual plugin setup.

2. **Convex _generated directory** -- The generated API types are in the project root's `convex/_generated/`. The Nuxt dashboard needs access. Options: symlink, monorepo workspace, or copy during build.

3. **WebSocket on localhost** -- `ConvexClient` uses WebSocket. Verify self-hosted Convex at `:3210` serves WebSocket connections. The dev server (`npx convex dev --url http://localhost:3210`) should handle this.

4. **Cookie security** -- Using `httpOnly: false` on the session cookie so client-side JS can read it via `useCookie()`. For better security, consider: (a) keep the cookie httpOnly and use a Nitro API route to proxy auth state, or (b) store token in both an httpOnly cookie (for SSR) and a non-httpOnly one (for client reads).

## Sources
1. [Nuxt Quickstart - Convex Docs](https://docs.convex.dev/quickstart/nuxt) - Official quickstart with convex-nuxt
2. [Nuxt Client - Convex Docs](https://docs.convex.dev/client/vue/nuxt) - Vue/Nuxt client documentation
3. [Vue Client - Convex Docs](https://docs.convex.dev/client/vue) - Composables reference
4. [convex-nuxt GitHub](https://github.com/chris-visser/convex-nuxt) - Module source code
5. [convex-vue GitHub](https://github.com/chris-visser/convex-vue) - Underlying Vue integration
6. [better-convex-nuxt](https://github.com/lupinum-dev/better-convex-nuxt) - Alternative with SSR + auth
7. [ConvexHttpClient API](https://docs.convex.dev/api/classes/browser.ConvexHttpClient) - Server-side HTTP client
8. [Convex Self-Hosting](https://docs.convex.dev/self-hosting) - Self-hosted setup docs
9. [Self-Hosted README](https://github.com/get-convex/convex-backend/blob/main/self-hosted/README.md) - Env var config
10. [Nuxt Sessions & Auth](https://nuxt.com/docs/4.x/guide/recipes/sessions-and-authentication) - Nuxt cookie auth patterns
