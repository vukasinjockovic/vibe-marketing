import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VStatusBadge from '../../components/VStatusBadge.vue'

describe('VStatusBadge', () => {
  it('renders status text with underscores replaced by spaces', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'in_progress' },
    })
    expect(wrapper.text()).toBe('in progress')
  })

  it('renders simple status text as-is', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'active' },
    })
    expect(wrapper.text()).toBe('active')
  })

  it('applies correct color classes for known statuses', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'completed' },
    })
    expect(wrapper.find('span').classes()).toContain('bg-green-100')
    expect(wrapper.find('span').classes()).toContain('text-green-700')
  })

  it('applies default gray color for unknown statuses', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'unknown_status' },
    })
    expect(wrapper.find('span').classes()).toContain('bg-gray-100')
    expect(wrapper.find('span').classes()).toContain('text-gray-600')
  })

  it('applies sm size classes when size is sm', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'active', size: 'sm' },
    })
    expect(wrapper.find('span').classes()).toContain('px-1.5')
    expect(wrapper.find('span').classes()).toContain('py-0.5')
  })

  it('applies md size classes by default', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'active' },
    })
    expect(wrapper.find('span').classes()).toContain('px-2')
    expect(wrapper.find('span').classes()).toContain('py-1')
  })

  it('has rounded-full and capitalize classes', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'active' },
    })
    expect(wrapper.find('span').classes()).toContain('rounded-full')
    expect(wrapper.find('span').classes()).toContain('capitalize')
  })

  it('maps blocked status to red colors', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'blocked' },
    })
    expect(wrapper.find('span').classes()).toContain('bg-red-100')
    expect(wrapper.find('span').classes()).toContain('text-red-700')
  })

  it('maps backlog status to gray colors', () => {
    const wrapper = mount(VStatusBadge, {
      props: { status: 'backlog' },
    })
    expect(wrapper.find('span').classes()).toContain('bg-gray-100')
    expect(wrapper.find('span').classes()).toContain('text-gray-700')
  })
})
