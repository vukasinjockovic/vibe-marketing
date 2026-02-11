<script setup lang="ts">
import { api } from '../../../convex/_generated/api'

const { data: projects, loading } = useConvexQuery(api.projects.list, {})
</script>

<template>
  <div>
    <VPageHeader title="Projects" description="Manage your marketing projects">
      <template #actions>
        <NuxtLink
          to="/projects/new"
          class="bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
        >
          New Project
        </NuxtLink>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-gray-500">Loading...</div>

    <VEmptyState
      v-else-if="!projects?.length"
      icon="i-heroicons-folder-plus"
      title="No projects yet"
      description="Create your first project to start building campaigns."
    >
      <NuxtLink
        to="/projects/new"
        class="inline-block bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
      >
        Create Project
      </NuxtLink>
    </VEmptyState>

    <div v-else class="grid grid-cols-3 gap-6">
      <NuxtLink
        v-for="project in projects"
        :key="project._id"
        :to="`/projects/${project.slug}`"
        class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center gap-3 mb-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg"
            :style="{ backgroundColor: project.appearance.color }"
          >
            {{ project.appearance.icon || project.name[0] }}
          </div>
          <div>
            <h3 class="font-semibold">{{ project.name }}</h3>
            <p class="text-sm text-gray-500">{{ project.slug }}</p>
          </div>
        </div>
        <p v-if="project.description" class="text-sm text-gray-600 mb-3">{{ project.description }}</p>
        <div v-if="project.stats" class="flex gap-4 text-xs text-gray-500">
          <span>{{ project.stats.productCount }} products</span>
          <span>{{ project.stats.campaignCount }} campaigns</span>
          <span>{{ project.stats.taskCount }} tasks</span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
