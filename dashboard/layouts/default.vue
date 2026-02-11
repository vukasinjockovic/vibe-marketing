<script setup lang="ts">
const { user, logout } = useAuth()
const route = useRoute()

const navigation = [
  { name: 'Dashboard', path: '/', icon: 'i-heroicons-home' },
  { name: 'Projects', path: '/projects', icon: 'i-heroicons-folder' },
  { name: 'Pipelines', path: '/pipelines', icon: 'i-heroicons-arrow-path-rounded-square' },
  { name: 'Agents', path: '/agents', icon: 'i-heroicons-cpu-chip' },
  { name: 'Services', path: '/services', icon: 'i-heroicons-server-stack' },
  { name: 'Activity', path: '/activity', icon: 'i-heroicons-clock' },
  { name: 'Settings', path: '/settings', icon: 'i-heroicons-cog-6-tooth' },
]
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-64 bg-gray-900 text-white">
      <div class="p-4 border-b border-gray-700">
        <h1 class="text-xl font-bold">Vibe Marketing</h1>
        <p class="text-sm text-gray-400 mt-1">AI Content Platform</p>
      </div>

      <nav class="mt-4">
        <NuxtLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 text-sm transition-colors"
          :class="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
            ? 'bg-gray-800 text-white border-r-2 border-primary-400'
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'"
        >
          <span :class="item.icon" class="text-lg" />
          {{ item.name }}
        </NuxtLink>
      </nav>

      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium">{{ user?.name }}</p>
            <p class="text-xs text-gray-400">{{ user?.role }}</p>
          </div>
          <button
            class="text-gray-400 hover:text-white transition-colors"
            title="Sign out"
            @click="logout"
          >
            <span class="i-heroicons-arrow-right-on-rectangle text-lg" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="ml-64 p-6">
      <slot />
    </main>
  </div>
</template>
