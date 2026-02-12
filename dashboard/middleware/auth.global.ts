export default defineNuxtRouteMiddleware(async (to) => {
  // Allow login page without auth
  if (to.path === '/login') return

  const { isAuthenticated, token, fetchUser } = useAuth()

  // If we have a session cookie but user isn't loaded yet (page refresh),
  // restore the user from the server before deciding to redirect.
  if (token.value && !isAuthenticated.value) {
    await fetchUser()
  }

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
