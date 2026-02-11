import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import ProductDetail from '../../pages/projects/[slug]/products/[id].vue'

const mockProduct = ref({
  _id: 'prod1',
  name: 'GymZilla',
  slug: 'gymzilla',
  description: 'Fitness platform',
  status: 'active',
  projectId: 'proj1',
  context: {
    whatItIs: 'A fitness platform',
    features: ['AI workouts', 'Progress tracking'],
    pricing: '$29/mo',
    usps: ['AI coaching', 'Community'],
    targetMarket: 'Fitness enthusiasts',
    website: 'https://gymzilla.com',
    competitors: ['Fitbit', 'MyFitnessPal'],
  },
  brandVoice: {
    tone: 'Motivational',
    style: 'Bold',
    vocabulary: { preferred: ['gains', 'level up'], avoided: ['lose', 'diet'] },
    examples: 'Push harder every day',
    notes: '',
  },
})

const mockFocusGroups = ref([
  { _id: 'fg1', name: 'Power Lifters', nickname: 'Iron Warriors', category: 'fitness', overview: 'Serious lifters' },
])

vi.stubGlobal('useCurrentProject', () => ({
  project: ref({ _id: 'proj1', name: 'Test', slug: 'test-project', appearance: { color: '#0ea5e9' }, stats: {} }),
  loading: ref(false),
  slug: computed(() => 'test-project'),
}))
vi.stubGlobal('useConvexQuery', () => ({
  data: mockProduct,
  loading: ref(false),
  error: ref(null),
}))
vi.stubGlobal('useConvexMutation', () => ({
  mutate: vi.fn().mockResolvedValue(undefined),
  loading: ref(false),
  error: ref(null),
}))
vi.stubGlobal('useToast', () => ({
  success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn(),
}))
vi.stubGlobal('useRoute', () => ({
  params: { slug: 'test-project', id: 'prod1' },
  path: '/projects/test-project/products/prod1',
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('ProductDetail (pages/projects/[slug]/products/[id].vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  function mountPage() {
    return mount(ProductDetail, {
      global: {
        stubs: {
          VPageHeader: { template: '<div class="page-header"><slot name="actions" /></div>', props: ['title', 'description'] },
          VStatusBadge: { template: '<span class="status-badge">{{ status }}</span>', props: ['status'] },
          VConfirmDialog: { template: '<div class="confirm-dialog" />', props: ['modelValue', 'title', 'message'] },
          VModal: { template: '<div class="modal" v-if="modelValue"><slot /></div>', props: ['modelValue', 'title', 'size'] },
          ProductForm: { template: '<div class="product-form" />', props: ['projectId', 'product'] },
          NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
        },
      },
    })
  }

  it('renders product name', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('GymZilla')
  })

  it('shows product description', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Fitness platform')
  })

  it('displays context information', () => {
    const wrapper = mountPage()
    const text = wrapper.text()
    expect(text).toContain('A fitness platform')
  })

  it('shows brand voice details', () => {
    const wrapper = mountPage()
    const text = wrapper.text()
    expect(text).toContain('Motivational')
  })

  it('has an edit button', () => {
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('edit') || html.includes('pencil')).toBe(true)
  })

  it('has an archive button with confirmation', () => {
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('archive') || html.includes('confirm-dialog')).toBe(true)
  })

  it('shows features list', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('AI workouts')
  })

  it('shows USPs list', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('AI coaching')
  })
})
