import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VPageHeader from '../../components/VPageHeader.vue'

describe('VPageHeader', () => {
  it('renders the title', () => {
    const wrapper = mount(VPageHeader, {
      props: { title: 'Dashboard' },
    })
    expect(wrapper.find('h1').text()).toBe('Dashboard')
  })

  it('renders description when provided', () => {
    const wrapper = mount(VPageHeader, {
      props: { title: 'Dashboard', description: 'Overview of your projects' },
    })
    expect(wrapper.find('p').text()).toBe('Overview of your projects')
  })

  it('does not render description paragraph when not provided', () => {
    const wrapper = mount(VPageHeader, {
      props: { title: 'Dashboard' },
    })
    expect(wrapper.find('p').exists()).toBe(false)
  })

  it('renders actions slot content', () => {
    const wrapper = mount(VPageHeader, {
      props: { title: 'Dashboard' },
      slots: {
        actions: '<button>Create New</button>',
      },
    })
    expect(wrapper.find('button').text()).toBe('Create New')
  })

  it('has correct styling classes', () => {
    const wrapper = mount(VPageHeader, {
      props: { title: 'Test' },
    })
    expect(wrapper.find('h1').classes()).toContain('text-2xl')
    expect(wrapper.find('h1').classes()).toContain('font-bold')
  })
})
