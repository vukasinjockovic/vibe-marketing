import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import ProductList from '../../pages/projects/[slug]/products/index.vue'

const mockProject = ref({
  _id: 'proj1',
  name: 'Test Project',
  slug: 'test-project',
  appearance: { color: '#0ea5e9', icon: '' },
  stats: { productCount: 2, campaignCount: 0, taskCount: 0, completedTaskCount: 0 },
})

const mockProducts = ref([
  {
    _id: 'prod1',
    name: 'GymZilla',
    slug: 'gymzilla',
    description: 'Fitness platform',
    status: 'active',
    context: { whatItIs: 'A fitness platform', features: ['workouts'], pricing: '$29/mo', usps: ['AI coaching'], targetMarket: 'fitness enthusiasts', website: 'https://gymzilla.com', competitors: [] },
    brandVoice: { tone: 'Motivational', style: 'Bold', vocabulary: { preferred: ['gains'], avoided: ['lose'] } },
  },
  {
    _id: 'prod2',
    name: 'NutriTrack',
    slug: 'nutritrack',
    description: 'Nutrition tracker',
    status: 'active',
    context: { whatItIs: 'Nutrition app', features: ['tracking'], pricing: '$9/mo', usps: ['Easy logging'], targetMarket: 'health-conscious', website: '', competitors: [] },
    brandVoice: { tone: 'Friendly', style: 'Casual', vocabulary: { preferred: ['fuel'], avoided: ['diet'] } },
  },
])

vi.stubGlobal('useCurrentProject', () => ({
  project: mockProject,
  loading: ref(false),
  slug: computed(() => 'test-project'),
}))
vi.stubGlobal('useConvexQuery', () => ({
  data: mockProducts,
  loading: ref(false),
  error: ref(null),
}))
vi.stubGlobal('useToast', () => ({
  success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn(),
}))
vi.stubGlobal('useRoute', () => ({
  params: { slug: 'test-project' },
  path: '/projects/test-project/products',
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('ProductList (pages/projects/[slug]/products/index.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function mountPage() {
    return mount(ProductList, {
      global: {
        stubs: {
          VPageHeader: { template: '<div class="page-header"><slot name="actions" /></div>', props: ['title', 'description'] },
          VModal: { template: '<div class="modal" v-if="modelValue"><slot /><slot name="footer" /></div>', props: ['modelValue', 'title', 'size'] },
          VEmptyState: { template: '<div class="empty-state"><slot /></div>', props: ['icon', 'title', 'description'] },
          NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
          ProductForm: { template: '<div class="product-form" />', props: ['projectId'] },
        },
      },
    })
  }

  it('renders product cards', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('GymZilla')
    expect(wrapper.text()).toContain('NutriTrack')
  })

  it('shows product descriptions', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Fitness platform')
  })

  it('has a New Product button', () => {
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('new product') || html.includes('add product') || html.includes('create')).toBe(true)
  })

  it('renders page header', () => {
    const wrapper = mountPage()
    expect(wrapper.find('.page-header').exists()).toBe(true)
  })
})
