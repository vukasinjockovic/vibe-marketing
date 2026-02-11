<script setup lang="ts">
const { project, loading } = useCurrentProject()

const route = useRoute()
const slug = computed(() => route.params.slug as string)

const tabs = computed(() => [
  { name: 'Overview', path: `/projects/${slug.value}` },
  { name: 'Products', path: `/projects/${slug.value}/products` },
  { name: 'Campaigns', path: `/projects/${slug.value}/campaigns` },
  { name: 'Pipeline', path: `/projects/${slug.value}/pipeline` },
])

function isActiveTab(tabPath: string) {
  return route.path === tabPath || (tabPath !== `/projects/${slug.value}` && route.path.startsWith(tabPath))
}
</script>

<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 rounded-lg bg-gray-200 animate-pulse" />
      <div>
        <div class="h-6 w-48 bg-gray-200 rounded animate-pulse" />
        <div class="h-4 w-24 bg-gray-100 rounded animate-pulse mt-1" />
      </div>
    </div>

    <!-- Project header -->
    <div v-else-if="project" class="mb-6">
      <div class="flex items-center gap-3 mb-4">
        <div
          class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg font-semibold"
          :style="{ backgroundColor: project.appearance?.color || '#6366f1' }"
        >
          {{ project.appearance?.icon || project.name[0] }}
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ project.name }}</h1>
          <p v-if="project.description" class="text-sm text-gray-500">{{ project.description }}</p>
        </div>
      </div>

      <!-- Tab navigation -->
      <nav class="flex gap-1 border-b border-gray-200">
        <NuxtLink
          v-for="tab in tabs"
          :key="tab.path"
          :to="tab.path"
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px"
          :class="isActiveTab(tab.path)
            ? 'border-primary-500 text-primary-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
        >
          {{ tab.name }}
        </NuxtLink>
      </nav>
    </div>

    <!-- Not found -->
    <div v-else class="text-center py-12">
      <p class="text-gray-500">Project not found</p>
      <NuxtLink to="/projects" class="text-primary-600 hover:underline text-sm mt-2 inline-block">
        Back to Projects
      </NuxtLink>
    </div>

    <!-- Nested pages -->
    <NuxtPage />
  </div>
</template>
