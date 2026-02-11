import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, computed } from 'vue'

function setupMocks() {
  vi.stubGlobal('useCurrentProject', () => ({
    project: ref({ _id: 'proj123', slug: 'test-project' }),
    loading: ref(false),
    error: ref(null),
    slug: computed(() => 'test-project'),
  }))

  vi.stubGlobal('toValue', (val: any) => {
    if (val && typeof val === 'object' && 'value' in val) return val.value
    if (typeof val === 'function') return val()
    return val
  })

  let callCount = 0
  vi.stubGlobal('useConvexQuery', () => {
    callCount++
    if (callCount <= 1) {
      return {
        data: ref([
          { _id: 'task1', status: 'backlog', contentType: 'audience_research', metadata: { productId: 'prod1' } },
          { _id: 'task2', status: 'completed', contentType: 'audience_import', metadata: { productId: 'prod1' } },
          { _id: 'task3', status: 'researched', contentType: 'blog_post', metadata: { productId: 'prod1' } },
        ]),
        loading: ref(false),
        error: ref(null),
      }
    }
    return {
      data: ref({ total: 5, pending: 2, approved: 3, rejected: 0, needsEnrichment: 1 }),
      loading: ref(false),
      error: ref(null),
    }
  })
}

describe('useAudienceJobs composable', () => {
  beforeEach(() => {
    vi.resetModules()
    setupMocks()
  })

  it('should export expected reactive properties', async () => {
    const { useAudienceJobs } = await import('../../composables/useAudienceJobs')
    const result = useAudienceJobs(ref('prod1'))

    expect(result).toHaveProperty('audienceTasks')
    expect(result).toHaveProperty('activeTasks')
    expect(result).toHaveProperty('hasActiveJob')
    expect(result).toHaveProperty('stagingSummary')
    expect(result).toHaveProperty('hasPendingReview')
    expect(result).toHaveProperty('latestTaskId')
  })

  it('filters audience tasks by contentType and productId', async () => {
    const { useAudienceJobs } = await import('../../composables/useAudienceJobs')
    const result = useAudienceJobs(ref('prod1'))

    expect(result.audienceTasks.value).toHaveLength(2)
  })

  it('identifies active tasks (not completed/cancelled/blocked)', async () => {
    const { useAudienceJobs } = await import('../../composables/useAudienceJobs')
    const result = useAudienceJobs(ref('prod1'))

    expect(result.activeTasks.value).toHaveLength(1)
    expect(result.hasActiveJob.value).toBe(true)
  })

  it('reports hasPendingReview when staging summary has pending items', async () => {
    const { useAudienceJobs } = await import('../../composables/useAudienceJobs')
    const result = useAudienceJobs(ref('prod1'))

    expect(result.hasPendingReview.value).toBe(true)
  })

  it('gets latestTaskId from first audience task', async () => {
    const { useAudienceJobs } = await import('../../composables/useAudienceJobs')
    const result = useAudienceJobs(ref('prod1'))

    expect(result.latestTaskId.value).toBe('task1')
  })
})
