import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VEmptyState from '../../components/VEmptyState.vue'

describe('VEmptyState', () => {
  it('renders the title', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Projects' },
    })
    expect(wrapper.find('h3').text()).toBe('No Projects')
  })

  it('renders description when provided', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Projects', description: 'Create your first project to get started.' },
    })
    expect(wrapper.find('p').text()).toBe('Create your first project to get started.')
  })

  it('does not render description when not provided', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Projects' },
    })
    expect(wrapper.find('p.text-muted-foreground').exists()).toBe(false)
  })

  it('renders icon slot when provided', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Data' },
      slots: { icon: '<svg data-testid="test-icon"></svg>' },
    })
    expect(wrapper.find('[data-testid="test-icon"]').exists()).toBe(true)
  })

  it('does not render icon container when no icon slot', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Data' },
    })
    // The icon container (rounded-full bg-muted) should not exist
    expect(wrapper.find('.bg-muted').exists()).toBe(false)
  })

  it('renders default slot for action', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'No Projects' },
      slots: { default: '<button>Create Project</button>' },
    })
    expect(wrapper.find('button').text()).toBe('Create Project')
  })

  it('does not render action wrapper when no slot provided', () => {
    const wrapper = mount(VEmptyState, {
      props: { title: 'Empty' },
    })
    expect(wrapper.find('.mt-4').exists()).toBe(false)
  })
})
