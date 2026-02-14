<script setup lang="ts">
import { api } from '../../../convex/_generated/api'
import { RefreshCw, Bell } from 'lucide-vue-next'

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
          class="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          @click="markAll"
        >
          Mark All Delivered
        </button>
      </template>
    </VPageHeader>

    <div v-if="loading" class="text-muted-foreground">
      <RefreshCw class="animate-spin h-6 w-6 mb-2 inline-block" />
      Loading notifications...
    </div>

    <VEmptyState
      v-else-if="!notifications || notifications.length === 0"
      title="No pending notifications"
      description="You're all caught up. Notifications from agents will appear here."
    />

    <div v-else class="rounded-lg border bg-card text-card-foreground shadow-sm divide-y divide-border">
      <div
        v-for="notif in notifications"
        :key="notif._id"
        class="px-4 sm:px-6 py-4 flex items-start gap-3 sm:gap-4"
      >
        <div class="flex-shrink-0 mt-0.5">
          <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary">
            <Bell class="w-4 h-4" />
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-medium text-primary">{{ notif.fromAgent }}</span>
            <span v-if="notif._creationTime" class="text-xs text-muted-foreground/70">
              {{ timeAgo(notif._creationTime) }}
            </span>
          </div>
          <p class="text-sm text-muted-foreground">{{ notif.content }}</p>
          <NuxtLink
            v-if="notif.taskId"
            :to="`/tasks/${notif.taskId}`"
            class="text-xs text-primary hover:text-primary/80 mt-1 inline-block"
          >
            View task
          </NuxtLink>
        </div>
        <button
          class="flex-shrink-0 px-3 py-1 text-xs rounded-md font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors"
          @click="markOne(notif._id)"
        >
          Dismiss
        </button>
      </div>
    </div>
  </div>
</template>
