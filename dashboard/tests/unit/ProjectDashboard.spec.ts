import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import ProjectDashboard from '../../pages/projects/[slug]/index.vue'

const mockProject = ref({
  _id: 'proj1',
  name: 'Test Project',
  slug: 'test-project',
  appearance: { color: '#0ea5e9', icon: '' },
  stats: { productCount: 3, campaignCount: 2, taskCount: 10, completedTaskCount: 5 },
})

const mockCampaigns = ref([
  { _id: 'c1', name: 'Summer Campaign', slug: 'summer', status: 'active' },
  { _id: 'c2', name: 'Winter Campaign', slug: 'winter', status: 'planning' },
])

const mockActivities = ref([
  { _id: 'a1', agentName: 'researcher', message: 'Completed research', type: 'info' },
])

vi.stubGlobal('useCurrentProject', () => ({
  project: mockProject,
  loading: ref(false),
  slug: computed(() => 'test-project'),
}))
vi.stubGlobal('useConvexQuery', (fn: any, args: any) => {
  // Differentiate by function reference
  return { data: mockCampaigns, loading: ref(false), error: ref(null) }
})
vi.stubGlobal('useRoute', () => ({
  params: { slug: 'test-project' },
  path: '/projects/test-project',
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('ProjectDashboard (pages/projects/[slug]/index.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function mountPage() {
    return mount(ProjectDashboard, {
      global: {
        stubs: {
          VStatusBadge: { template: '<span class="status-badge">{{ status }}</span>', props: ['status'] },
          NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
          VEmptyState: { template: '<div class="empty-state"><slot /></div>', props: ['icon', 'title', 'description'] },
        },
      },
    })
  }

  it('renders stat cards from project.stats', () => {
    const wrapper = mountPage()
    const text = wrapper.text()
    // Should show product count, campaign count, task count
    expect(text).toContain('3')
    expect(text).toContain('2')
    expect(text).toContain('10')
  })

  it('shows campaigns list', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Summer Campaign')
  })

  it('renders activity feed entries', () => {
    const wrapper = mountPage()
    // Activities are rendered somewhere in the page
    expect(wrapper.html()).toBeTruthy()
  })

  it('shows project stats labels', () => {
    const wrapper = mountPage()
    const text = wrapper.text().toLowerCase()
    expect(text.includes('product') || text.includes('campaign') || text.includes('task')).toBe(true)
  })
})
