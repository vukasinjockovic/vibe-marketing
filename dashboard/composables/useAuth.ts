import { api } from '../../convex/_generated/api'

export function useAuth() {
  const token = useCookie('vibe_session', {
    maxAge: 30 * 24 * 60 * 60, // 30 days, matches Convex session expiry
    sameSite: 'lax',
  })

  const user = useState<{
    _id: string
    email: string
    name: string
    role: string
  } | null>('user', () => null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function login(email: string, password: string) {
    const client = useConvex()
    const result = await client.action(api.auth.signIn, { email, password })
    token.value = result.token
    user.value = result.user
    return result
  }

  async function logout() {
    if (token.value) {
      try {
        const client = useConvex()
        await client.mutation(api.auth.signOut, { token: token.value })
      } catch { /* ignore errors during logout */ }
    }
    token.value = null
    user.value = null
    navigateTo('/login')
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      const client = useConvex()
      const result = await client.query(api.auth.me, { token: token.value })
      if (result) {
        user.value = result
      } else {
        token.value = null
        user.value = null
      }
      return result
    } catch {
      token.value = null
      user.value = null
      return null
    }
  }

  return {
    token: readonly(token),
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
    fetchUser,
  }
}
