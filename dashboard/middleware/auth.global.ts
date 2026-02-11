export default defineNuxtRouteMiddleware((to) => {
  // Allow login page without auth
  if (to.path === '/login') return

  const { isAuthenticated } = useAuth()

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
