import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, computed } from 'vue'
import AgentDetail from '../../pages/agents/[name].vue'

// Mock data
const mockAgent = ref<any>({
  _id: 'agent1',
  name: 'vibe-researcher',
  displayName: 'Vibe Researcher',
  role: 'Research specialist for marketing content',
  status: 'active',
  defaultModel: 'sonnet',
  level: 'specialist',
  skillPath: '.claude/skills/vibe-researcher',
  agentFilePath: 'scripts/agents/vibe-researcher.sh',
  currentTaskId: 'task1',
  lastHeartbeat: Date.now() - 120000,
  stats: {
    tasksCompleted: 42,
    avgQualityScore: 8.5,
    lastActive: Date.now() - 120000,
  },
  staticSkillIds: [],
  dynamicSkillIds: [],
})

const mockRuns = ref<any[]>([
  {
    _id: 'run1',
    agentName: 'vibe-researcher',
    startedAt: Date.now() - 300000,
    finishedAt: Date.now() - 180000,
    durationSeconds: 120,
    model: 'sonnet',
    status: 'completed',
    itemsProcessed: 5,
  },
  {
    _id: 'run2',
    agentName: 'vibe-researcher',
    startedAt: Date.now() - 60000,
    model: 'sonnet',
    status: 'running',
  },
])

const mockActivities = ref<any[]>([
  { _id: 'act1', agentName: 'vibe-researcher', type: 'info', message: 'Started research task' },
  { _id: 'act2', agentName: 'vibe-researcher', type: 'complete', message: 'Research completed' },
  { _id: 'act3', agentName: 'vibe-researcher', type: 'error', message: 'API rate limit hit' },
])

const mockLoadingAgent = ref(false)
const mockLoadingRuns = ref(false)
const mockLoadingActivities = ref(false)

vi.stubGlobal('useRoute', () => ({
  params: { name: 'vibe-researcher' },
}))

// Track call order: component calls useConvexQuery 3 times in order: agent, runs, activities
let useConvexQueryCallCount = 0
vi.stubGlobal('useConvexQuery', (fn: any, args: any) => {
  const callIndex = useConvexQueryCallCount++
  if (callIndex === 0) {
    return { data: mockAgent, loading: mockLoadingAgent, error: ref(null) }
  }
  if (callIndex === 1) {
    return { data: mockRuns, loading: mockLoadingRuns, error: ref(null) }
  }
  if (callIndex === 2) {
    return { data: mockActivities, loading: mockLoadingActivities, error: ref(null) }
  }
  return { data: ref(null), loading: ref(false), error: ref(null) }
})

vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('AgentDetail (pages/agents/[name].vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useConvexQueryCallCount = 0
    mockLoadingAgent.value = false
    mockLoadingRuns.value = false
    mockLoadingActivities.value = false
    mockAgent.value = {
      _id: 'agent1',
      name: 'vibe-researcher',
      displayName: 'Vibe Researcher',
      role: 'Research specialist for marketing content',
      status: 'active',
      defaultModel: 'sonnet',
      level: 'specialist',
      skillPath: '.claude/skills/vibe-researcher',
      agentFilePath: 'scripts/agents/vibe-researcher.sh',
      currentTaskId: 'task1',
      lastHeartbeat: Date.now() - 120000,
      stats: {
        tasksCompleted: 42,
        avgQualityScore: 8.5,
        lastActive: Date.now() - 120000,
      },
      staticSkillIds: [],
      dynamicSkillIds: [],
    }
  })

  function mountPage() {
    return mount(AgentDetail, {
      global: {
        stubs: {
          VPageHeader: {
            template: '<div class="page-header"><h1>{{ title }}</h1><slot name="actions" /></div>',
            props: ['title', 'description'],
          },
          VStatusBadge: {
            template: '<span class="status-badge">{{ status }}</span>',
            props: ['status'],
          },
          VDataTable: {
            template: '<div class="data-table"><slot v-for="row in rows" :name="`cell-status`" :row="row" /><slot v-for="row in rows" :name="`cell-duration`" :row="row" /></div>',
            props: ['columns', 'rows', 'loading', 'emptyMessage'],
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

  it('renders agent display name', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Vibe Researcher')
  })

  it('renders agent status badge', () => {
    const wrapper = mountPage()
    const badges = wrapper.findAll('.status-badge')
    expect(badges.length).toBeGreaterThan(0)
    expect(badges.some(b => b.text() === 'active')).toBe(true)
  })

  it('shows agent role', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Research specialist for marketing content')
  })

  it('shows agent model', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('sonnet')
  })

  it('shows agent level', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('specialist')
  })

  it('shows agent skill path', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('.claude/skills/vibe-researcher')
  })

  it('shows tasks completed stat', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('42')
  })

  it('shows average quality score', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('8.5')
  })

  it('shows back link to /agents', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a')
    const hrefs = links.map(l => l.attributes('href'))
    expect(hrefs).toContain('/agents')
  })

  it('renders loading state when agent is loading', () => {
    mockLoadingAgent.value = true
    mockAgent.value = null
    const wrapper = mountPage()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('loading') || html.includes('animate-spin')).toBe(true)
  })

  it('renders activity log entries', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Started research task')
    expect(wrapper.text()).toContain('Research completed')
  })

  it('shows runs data table', () => {
    const wrapper = mountPage()
    expect(wrapper.find('.data-table').exists()).toBe(true)
  })

  it('handles agent not found', () => {
    mockAgent.value = null
    mockLoadingAgent.value = false
    const wrapper = mountPage()
    // Should not crash, should show a not-found or empty state
    expect(wrapper.html()).toBeTruthy()
  })
})
