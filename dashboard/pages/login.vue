<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const { login, isAuthenticated } = useAuth()

// If already authenticated, redirect to home
if (isAuthenticated.value) {
  navigateTo('/')
}

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/')
  } catch (e: any) {
    error.value = e.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-sm mx-auto">
    <div class="text-center mb-8">
      <div class="flex items-center justify-center gap-3 mb-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white text-lg font-bold">
          V
        </div>
      </div>
      <h1 class="text-3xl font-bold text-white">Vibe Marketing</h1>
      <p class="text-muted-foreground/70 mt-2">AI Content Platform</p>
    </div>

    <form class="rounded-lg border bg-card text-card-foreground shadow-lg p-8" @submit.prevent="handleLogin">
      <h2 class="text-xl font-semibold mb-6">Sign in</h2>

      <div v-if="error" class="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
        {{ error }}
      </div>

      <div class="mb-4 space-y-1.5">
        <label class="block text-sm font-medium text-foreground" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          placeholder="you@example.com"
        />
      </div>

      <div class="mb-6 space-y-1.5">
        <label class="block text-sm font-medium text-foreground" for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          placeholder="Enter password"
        />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full inline-flex items-center justify-center rounded-md text-sm font-medium h-10 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Signing in...' : 'Sign in' }}
      </button>
    </form>
  </div>
</template>
