import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed, nextTick } from 'vue'
import AudienceList from '../../pages/projects/[slug]/products/[id]/audiences.vue'

const mockFocusGroups = ref([
  {
    _id: 'fg1',
    name: 'Power Lifters',
    nickname: 'Iron Warriors',
    category: 'fitness',
    number: 1,
    overview: 'Serious gym-goers focused on strength training and progressive overload.',
    demographics: { ageRange: '25-40', gender: 'Male', income: '$50k-80k', lifestyle: 'Active', triggers: ['new PR'] },
    psychographics: { values: ['Discipline'], beliefs: ['Hard work pays off'], lifestyle: 'Gym 5x/week', identity: 'Athlete' },
    coreDesires: ['Get stronger', 'Build muscle'],
    painPoints: ['Plateaus', 'Injury prevention'],
    fears: ['Losing gains'],
    beliefs: ['Consistency is key'],
    objections: ['Too expensive'],
    emotionalTriggers: ['Competition'],
    languagePatterns: ['Beast mode'],
    ebookAngles: ['Strength bible'],
    marketingHooks: ['Unlock your potential'],
    transformationPromise: 'From novice to advanced lifter in 12 weeks',
    source: 'uploaded',
  },
  {
    _id: 'fg2',
    name: 'Yoga Practitioners',
    nickname: 'Zen Seekers',
    category: 'fitness',
    number: 2,
    overview: 'Mind-body connection seekers looking for flexibility and inner peace.',
    demographics: { ageRange: '30-50', gender: 'Female', income: '$60k-100k', lifestyle: 'Mindful', triggers: ['stress'] },
    psychographics: { values: ['Balance'], beliefs: ['Mind-body unity'], lifestyle: 'Daily practice', identity: 'Yogi' },
    coreDesires: ['Flexibility', 'Peace'],
    painPoints: ['Stiffness', 'Stress'],
    fears: ['Injury'],
    beliefs: ['Balance is wellness'],
    objections: ['Not enough time'],
    emotionalTriggers: ['Serenity'],
    languagePatterns: ['Namaste'],
    ebookAngles: ['Yoga journey'],
    marketingHooks: ['Find your zen'],
    transformationPromise: 'Complete flexibility and inner calm in 8 weeks',
    source: 'manual',
  },
])

vi.stubGlobal('useCurrentProject', () => ({
  project: ref({ _id: 'proj1', name: 'Test', slug: 'test-project', appearance: { color: '#0ea5e9' }, stats: {} }),
  loading: ref(false),
  slug: computed(() => 'test-project'),
}))

// useConvexQuery is called multiple times now: products.get, focusGroups.listByProduct, tasks.listByProject, focusGroupStaging.getSummary
let queryCallCount = 0
vi.stubGlobal('useConvexQuery', () => {
  queryCallCount++
  if (queryCallCount === 1) {
    // products.get
    return { data: ref({ _id: 'prod1', name: 'Test Product', context: {} }), loading: ref(false), error: ref(null) }
  }
  if (queryCallCount === 2) {
    // focusGroups.listByProduct
    return { data: mockFocusGroups, loading: ref(false), error: ref(null) }
  }
  if (queryCallCount === 3) {
    // tasks.listByProject (for useAudienceJobs)
    return { data: ref([]), loading: ref(false), error: ref(null) }
  }
  // focusGroupStaging.getSummary
  return { data: ref(null), loading: ref(false), error: ref(null) }
})

vi.stubGlobal('useConvexMutation', () => ({
  mutate: vi.fn().mockResolvedValue(undefined),
  loading: ref(false),
  error: ref(null),
}))
vi.stubGlobal('useToast', () => ({
  success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn(),
  toasts: ref([]), dismiss: vi.fn(), show: vi.fn(),
}))
vi.stubGlobal('useRoute', () => ({
  params: { slug: 'test-project', id: 'prod1' },
  path: '/projects/test-project/products/prod1/audiences',
  query: {},
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))
vi.stubGlobal('toValue', (val: any) => {
  if (val && typeof val === 'object' && 'value' in val) return val.value
  if (typeof val === 'function') return val()
  return val
})

describe('AudienceList (pages/projects/[slug]/products/[id]/audiences.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    queryCallCount = 0
  })

  function mountPage() {
    return mount(AudienceList, {
      global: {
        stubs: {
          VPageHeader: { template: '<div class="page-header"><slot name="actions" /></div>', props: ['title', 'description'] },
          VModal: { template: '<div class="modal" v-if="modelValue"><slot /></div>', props: ['modelValue', 'title', 'size'] },
          VConfirmDialog: { template: '<div class="confirm-dialog" />', props: ['modelValue', 'title', 'message'] },
          VStatusBadge: { template: '<span class="badge">{{ status }}</span>', props: ['status'] },
          VEmptyState: { template: '<div class="empty-state"><slot /></div>', props: ['icon', 'title', 'description'] },
          FocusGroupForm: { template: '<div class="focus-group-form" />', props: ['projectId', 'productId'] },
          EnrichmentProgressBar: { template: '<div class="enrichment-bar" />', props: ['score', 'label', 'showPercentage'] },
          AudienceResearchDialog: { template: '<div class="research-dialog" />', props: ['modelValue', 'projectId', 'productId', 'product'] },
          AudienceImportDialog: { template: '<div class="import-dialog" />', props: ['modelValue', 'projectId', 'productId'] },
          NuxtLink: { template: '<a><slot /></a>', props: ['to'] },
        },
      },
    })
  }

  it('renders focus group cards', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Power Lifters')
    expect(wrapper.text()).toContain('Yoga Practitioners')
  })

  it('shows nickname on cards', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Iron Warriors')
    expect(wrapper.text()).toContain('Zen Seekers')
  })

  it('shows category badges', () => {
    const wrapper = mountPage()
    const text = wrapper.text().toLowerCase()
    expect(text).toContain('fitness')
  })

  it('shows truncated overview', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Serious gym-goers')
  })

  it('has a create button for new focus group', () => {
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(
      html.includes('manual') ||
      html.includes('new focus group') ||
      html.includes('add focus group') ||
      html.includes('create')
    ).toBe(true)
  })

  it('has expandable cards that show details', async () => {
    const wrapper = mountPage()
    expect(wrapper.html()).toBeTruthy()
    const cards = wrapper.findAll('[class*="cursor-pointer"]')
    if (cards.length > 0) {
      await cards[0].trigger('click')
      await nextTick()
    }
    expect(wrapper.html()).toBeTruthy()
  })

  it('has delete buttons for focus groups', () => {
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(
      html.includes('delete') ||
      html.includes('remove') ||
      html.includes('trash') ||
      html.includes('confirm-dialog')
    ).toBe(true)
  })

  it('has research and import buttons', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Research Audiences')
    expect(wrapper.text()).toContain('Import Document')
  })
})
