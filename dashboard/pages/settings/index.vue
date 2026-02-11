<script setup lang="ts">
const sections = [
  {
    title: 'Service Registry',
    description: 'Configure external API services, manage API keys, and set priorities.',
    path: '/services',
    icon: 'i-heroicons-server-stack',
  },
  {
    title: 'Notifications',
    description: 'View notification queue and configure Telegram alerts.',
    path: '/settings/notifications',
    icon: 'i-heroicons-bell',
  },
  {
    title: 'Agents',
    description: 'View and manage registered AI agents.',
    path: '/agents',
    icon: 'i-heroicons-cpu-chip',
  },
]
</script>

<template>
  <div>
    <VPageHeader title="Settings" description="Platform configuration and management" />

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <NuxtLink
        v-for="section in sections"
        :key="section.path"
        :to="section.path"
        class="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow group flex items-start gap-4"
      >
        <span :class="section.icon" class="text-2xl text-gray-400 group-hover:text-primary-600 transition-colors mt-0.5" />
        <div class="flex-1">
          <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            {{ section.title }}
          </h3>
          <p class="text-sm text-gray-500 mt-1">{{ section.description }}</p>
        </div>
        <span class="i-heroicons-chevron-right text-gray-300 group-hover:text-primary-500 transition-colors mt-1" />
      </NuxtLink>
    </div>
  </div>
</template>
