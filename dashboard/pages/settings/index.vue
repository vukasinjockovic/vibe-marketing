<script setup lang="ts">
import { Inbox, Bell, Monitor, ChevronRight } from 'lucide-vue-next'
import type { Component } from 'vue'

const sections: Array<{ title: string; description: string; path: string; icon: Component }> = [
  {
    title: 'Service Registry',
    description: 'Configure external API services, manage API keys, and set priorities.',
    path: '/services',
    icon: Inbox,
  },
  {
    title: 'Notifications',
    description: 'View notification queue and configure Telegram alerts.',
    path: '/settings/notifications',
    icon: Bell,
  },
  {
    title: 'Agents',
    description: 'View and manage registered AI agents.',
    path: '/agents',
    icon: Monitor,
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
        class="rounded-lg border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow group flex items-start gap-4"
      >
        <component :is="section.icon" class="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors mt-0.5 flex-shrink-0" />
        <div class="flex-1">
          <h3 class="font-semibold text-foreground group-hover:text-primary transition-colors">
            {{ section.title }}
          </h3>
          <p class="text-sm text-muted-foreground mt-1">{{ section.description }}</p>
        </div>
        <ChevronRight class="w-4 h-4 text-muted-foreground/40 group-hover:text-primary transition-colors mt-1 flex-shrink-0" />
      </NuxtLink>
    </div>
  </div>
</template>
