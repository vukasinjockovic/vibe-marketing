<script setup lang="ts">
import { Bell } from 'lucide-vue-next'

const { notifications, unreadCount, markAllRead } = useNotifications()
const open = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

function toggle() {
  open.value = !open.value
}

function onClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside, true))
onUnmounted(() => document.removeEventListener('click', onClickOutside, true))

function formatTime(ts: number) {
  if (!ts) return ''
  const diffMs = Date.now() - ts
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

async function handleMarkAllRead() {
  await markAllRead()
}
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <button
      class="relative flex items-center justify-center w-8 h-8 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
      @click="toggle"
    >
      <Bell :size="18" />
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full bg-destructive text-destructive-foreground text-[10px] font-bold"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <div
      v-if="open"
      class="absolute right-0 top-full mt-2 w-80 rounded-lg border bg-popover text-popover-foreground shadow-lg z-50"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b">
        <h4 class="text-sm font-semibold">Notifications</h4>
        <button
          v-if="unreadCount > 0"
          class="text-xs text-primary hover:underline"
          @click="handleMarkAllRead"
        >
          Mark all read
        </button>
      </div>

      <div v-if="notifications.length === 0" class="px-4 py-8 text-center text-sm text-muted-foreground">
        No notifications yet
      </div>

      <div v-else class="max-h-80 overflow-y-auto divide-y divide-border">
        <div
          v-for="n in notifications"
          :key="n._id"
          class="px-4 py-3 text-sm"
          :class="!n.isRead ? 'bg-primary/5 border-l-2 border-l-primary' : ''"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0 flex-1">
              <p class="font-medium text-foreground">{{ n.fromAgent }}</p>
              <p class="text-muted-foreground mt-0.5 line-clamp-2">{{ n.content }}</p>
            </div>
            <span class="text-xs text-muted-foreground/60 whitespace-nowrap shrink-0">
              {{ formatTime(n._creationTime) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
