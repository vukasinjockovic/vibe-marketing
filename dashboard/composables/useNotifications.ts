import { computed } from 'vue'
import { api } from '../../convex/_generated/api'

export function useNotifications() {
  const { token } = useAuth()

  const { data: notifications } = useConvexQuery(
    api.notifications.listForDashboard,
    computed(() => token.value ? { token: token.value } : 'skip' as const),
  )

  const { data: unreadCount } = useConvexQuery(
    api.notifications.countUnread,
    computed(() => token.value ? { token: token.value } : 'skip' as const),
  )

  const { mutate: markAllReadMutation } = useConvexMutation(api.notifications.markAllRead)

  async function markAllRead() {
    if (!token.value) return
    await markAllReadMutation({ token: token.value })
  }

  return {
    notifications: computed(() => notifications.value || []),
    unreadCount: computed(() => unreadCount.value || 0),
    markAllRead,
  }
}
