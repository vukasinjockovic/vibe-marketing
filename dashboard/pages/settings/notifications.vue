<script setup lang="ts">
import { api } from '../../../convex/_generated/api'

const { data: notifications, loading } = useConvexQuery(
  api.notifications.listUndelivered,
  { mentionedAgent: '@human' }
)

const { mutate: markDelivered } = useConvexMutation(api.notifications.markDelivered)
const { mutate: markAllDelivered } = useConvexMutation(api.notifications.markAllDelivered)
const toast = useToast()

async function markOne(id: string) {
  try {
    await markDelivered({ id: id as any })
    toast.success('Marked as delivered')
  } catch (e: any) {
    toast.error(e.message)
  }
}

async function markAll() {
  try {
    await markAllDelivered({ mentionedAgent: '@human' })
    toast.success('All notifications marked as delivered')
  } catch (e: any) {
    toast.error(e.message)
  }
}

function timeAgo(ts: number) {
  const diff = Date.now() - ts
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}
</script>

<template>
  <div>
    <VPageHeader title="Notifications" description="Agent notifications targeted at you (@human)">
      <template #actions>
        <button
          v-if="notifications && notifications.length > 0"
          class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
          @click="markAll"
        >
          Mark All Delivered
        </button>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-gray-500">
      <span class="i-heroicons-arrow-path animate-spin text-2xl mb-2 block" />
      Loading notifications...
    </div>

    <VEmptyState
      v-else-if="!notifications || notifications.length === 0"
      icon="i-heroicons-bell-slash"
      title="No pending notifications"
      description="You're all caught up. Notifications from agents will appear here."
    />

    <div v-else class="bg-white rounded-lg shadow divide-y">
      <div
        v-for="notif in notifications"
        :key="notif._id"
        class="px-6 py-4 flex items-start gap-4"
      >
        <div class="flex-shrink-0 mt-0.5">
          <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700">
            <span class="i-heroicons-bell text-sm" />
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-medium text-primary-700">{{ notif.fromAgent }}</span>
            <span v-if="notif._creationTime" class="text-xs text-gray-400">
              {{ timeAgo(notif._creationTime) }}
            </span>
          </div>
          <p class="text-sm text-gray-700">{{ notif.content }}</p>
          <NuxtLink
            v-if="notif.taskId"
            :to="`/tasks/${notif.taskId}`"
            class="text-xs text-primary-600 hover:text-primary-700 mt-1 inline-block"
          >
            View task
          </NuxtLink>
        </div>
        <button
          class="flex-shrink-0 px-3 py-1 text-xs rounded-md font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
          @click="markOne(notif._id)"
        >
          Dismiss
        </button>
      </div>
    </div>
  </div>
</template>
