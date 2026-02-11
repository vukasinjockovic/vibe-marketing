import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import ProjectSlug from '../../pages/projects/[slug].vue'

// Mock Nuxt auto-imports
const mockProject = ref({
  _id: 'proj1',
  name: 'Test Project',
  slug: 'test-project',
  appearance: { color: '#0ea5e9', icon: '' },
  stats: { productCount: 3, campaignCount: 2, taskCount: 10, completedTaskCount: 5 },
})
const mockLoading = ref(false)

vi.stubGlobal('useCurrentProject', () => ({
  project: mockProject,
  loading: mockLoading,
  slug: computed(() => 'test-project'),
}))
vi.stubGlobal('useRoute', () => ({
  params: { slug: 'test-project' },
  path: '/projects/test-project',
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('ProjectSlug layout (pages/projects/[slug].vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockProject.value = {
      _id: 'proj1',
      name: 'Test Project',
      slug: 'test-project',
      appearance: { color: '#0ea5e9', icon: '' },
      stats: { productCount: 3, campaignCount: 2, taskCount: 10, completedTaskCount: 5 },
    }
    mockLoading.value = false
  })

  function mountPage() {
    return mount(ProjectSlug, {
      global: {
        stubs: {
          NuxtLink: { template: '<a :href="to" :class="$attrs.class"><slot /></a>', props: ['to'] },
          NuxtPage: { template: '<div class="nuxt-page">Page Content</div>' },
        },
      },
    })
  }

  it('renders project name', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Test Project')
  })

  it('shows loading state when project is loading', () => {
    mockLoading.value = true
    mockProject.value = null as any
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('loading') || html.includes('animate-spin') || html.includes('skeleton')).toBe(true)
  })

  it('renders tab navigation links', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a')
    const hrefs = links.map(l => l.attributes('href'))
    expect(hrefs).toContain('/projects/test-project')
    expect(hrefs).toContain('/projects/test-project/products')
    expect(hrefs).toContain('/projects/test-project/campaigns')
  })

  it('renders NuxtPage for nested routes', () => {
    const wrapper = mountPage()
    expect(wrapper.find('.nuxt-page').exists()).toBe(true)
  })

  it('shows project color swatch', () => {
    const wrapper = mountPage()
    const html = wrapper.html()
    expect(html).toContain('#0ea5e9')
  })

  it('has Overview, Products, Campaigns, Pipeline tabs', () => {
    const wrapper = mountPage()
    const text = wrapper.text()
    expect(text).toContain('Overview')
    expect(text).toContain('Products')
    expect(text).toContain('Campaigns')
    expect(text).toContain('Pipeline')
  })
})
