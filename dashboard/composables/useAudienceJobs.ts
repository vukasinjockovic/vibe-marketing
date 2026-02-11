import { api } from '../../convex/_generated/api'
import type { MaybeRefOrGetter } from 'vue'

export function useAudienceJobs(productId?: MaybeRefOrGetter<string | undefined>) {
  const { project } = useCurrentProject()
  const projectId = computed(() => project.value?._id)

  const { data: allTasks } = useConvexQuery(
    api.tasks.listByProject,
    computed(() => projectId.value ? { projectId: projectId.value } : 'skip'),
  )

  const audienceTasks = computed(() => {
    if (!allTasks.value) return []
    const pid = productId ? toValue(productId) : undefined
    return allTasks.value.filter((t: any) => {
      const isAudienceType = t.contentType === 'audience_research' || t.contentType === 'audience_import'
      if (!isAudienceType) return false
      // If productId provided, filter by it; otherwise show all audience tasks
      return pid ? t.metadata?.productId === pid : true
    })
  })

  const activeTasks = computed(() => audienceTasks.value.filter((t: any) =>
    !['completed', 'cancelled', 'blocked'].includes(t.status),
  ))

  const hasActiveJob = computed(() => activeTasks.value.length > 0)

  // Get staging summary for the most recent task
  const latestTaskId = computed(() => audienceTasks.value[0]?._id)
  const { data: stagingSummary } = useConvexQuery(
    api.focusGroupStaging.getSummary,
    computed(() => latestTaskId.value ? { taskId: latestTaskId.value } : 'skip'),
  )

  const hasPendingReview = computed(() => (stagingSummary.value?.pending || 0) > 0)

  return { audienceTasks, activeTasks, hasActiveJob, stagingSummary, hasPendingReview, latestTaskId }
}
