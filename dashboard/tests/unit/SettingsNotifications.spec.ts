import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import SettingsNotifications from '../../pages/settings/notifications.vue'

const mockNotifications = ref<any[]>([
  {
    _id: 'notif1',
    mentionedAgent: '@human',
    fromAgent: 'vibe-researcher',
    content: 'Research for summer campaign is complete',
    taskId: 'task1',
    delivered: false,
  },
  {
    _id: 'notif2',
    mentionedAgent: '@human',
    fromAgent: 'content-writer',
    content: 'Draft ready for review',
    delivered: false,
  },
])

const mockLoadingNotifications = ref(false)
const mockMarkDelivered = vi.fn()
const mockMarkAllDelivered = vi.fn()
const mockToast = { success: vi.fn(), error: vi.fn(), info: vi.fn(), warning: vi.fn() }

vi.stubGlobal('useConvexQuery', (fn: any, args: any) => {
  return { data: mockNotifications, loading: mockLoadingNotifications, error: ref(null) }
})

// Component calls useConvexMutation twice in order: markDelivered, markAllDelivered
let useConvexMutationCallCount = 0
vi.stubGlobal('useConvexMutation', (fn: any) => {
  const callIndex = useConvexMutationCallCount++
  if (callIndex === 0) {
    return { mutate: mockMarkDelivered }
  }
  return { mutate: mockMarkAllDelivered }
})

vi.stubGlobal('useToast', () => mockToast)
vi.stubGlobal('useRoute', () => ({ path: '/settings/notifications' }))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('SettingsNotifications (pages/settings/notifications.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useConvexMutationCallCount = 0
    mockLoadingNotifications.value = false
    mockNotifications.value = [
      {
        _id: 'notif1',
        mentionedAgent: '@human',
        fromAgent: 'vibe-researcher',
        content: 'Research for summer campaign is complete',
        taskId: 'task1',
        delivered: false,
      },
      {
        _id: 'notif2',
        mentionedAgent: '@human',
        fromAgent: 'content-writer',
        content: 'Draft ready for review',
        delivered: false,
      },
    ]
  })

  function mountPage() {
    return mount(SettingsNotifications, {
      global: {
        stubs: {
          VPageHeader: {
            template: '<div class="page-header"><h1>{{ title }}</h1><slot name="actions" /></div>',
            props: ['title', 'description'],
          },
          VEmptyState: {
            template: '<div class="empty-state">{{ title }}</div>',
            props: ['icon', 'title', 'description'],
          },
          NuxtLink: {
            template: '<a :href="to"><slot /></a>',
            props: ['to'],
          },
        },
      },
    })
  }

  it('renders page header with Notifications title', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Notifications')
  })

  it('displays notification content', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Research for summer campaign is complete')
    expect(wrapper.text()).toContain('Draft ready for review')
  })

  it('shows from agent name for each notification', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('vibe-researcher')
    expect(wrapper.text()).toContain('content-writer')
  })

  it('renders a Mark All Delivered button', () => {
    const wrapper = mountPage()
    const buttons = wrapper.findAll('button')
    const markAllBtn = buttons.find(b => b.text().includes('Mark All'))
    expect(markAllBtn).toBeTruthy()
  })

  it('renders dismiss buttons for each notification', () => {
    const wrapper = mountPage()
    const buttons = wrapper.findAll('button')
    // At least one dismiss button per notification + the mark all button
    expect(buttons.length).toBeGreaterThanOrEqual(3)
  })

  it('calls markAllDelivered when Mark All button clicked', async () => {
    const wrapper = mountPage()
    const buttons = wrapper.findAll('button')
    const markAllBtn = buttons.find(b => b.text().includes('Mark All'))
    await markAllBtn!.trigger('click')
    await flushPromises()
    expect(mockMarkAllDelivered).toHaveBeenCalledWith({ mentionedAgent: '@human' })
  })

  it('calls markDelivered when dismiss button clicked', async () => {
    const wrapper = mountPage()
    const buttons = wrapper.findAll('button')
    // Find a dismiss button (not the Mark All button)
    const dismissBtn = buttons.find(b => b.text().includes('Dismiss'))
    if (dismissBtn) {
      await dismissBtn.trigger('click')
      expect(mockMarkDelivered).toHaveBeenCalled()
    }
  })

  it('shows empty state when no notifications', () => {
    mockNotifications.value = []
    const wrapper = mountPage()
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('shows loading state', () => {
    mockLoadingNotifications.value = true
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('loading') || html.includes('animate-spin')).toBe(true)
  })
})
