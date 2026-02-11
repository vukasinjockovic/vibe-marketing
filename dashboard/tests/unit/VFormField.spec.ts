import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VFormField from '../../components/VFormField.vue'

describe('VFormField', () => {
  it('renders the label text', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email' },
    })
    expect(wrapper.find('label').text()).toContain('Email')
  })

  it('shows required asterisk when required is true', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email', required: true },
    })
    expect(wrapper.find('span.text-red-500').exists()).toBe(true)
    expect(wrapper.find('span.text-red-500').text()).toBe('*')
  })

  it('does not show asterisk when required is false', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email' },
    })
    expect(wrapper.find('span.text-red-500').exists()).toBe(false)
  })

  it('shows hint text when provided and no error', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email', hint: 'Enter your work email' },
    })
    const hint = wrapper.findAll('p').find(p => p.classes().includes('text-gray-500'))
    expect(hint).toBeTruthy()
    expect(hint!.text()).toBe('Enter your work email')
  })

  it('shows error message when provided', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email', error: 'Email is required' },
    })
    const error = wrapper.findAll('p').find(p => p.classes().includes('text-red-600'))
    expect(error).toBeTruthy()
    expect(error!.text()).toBe('Email is required')
  })

  it('hides hint when error is shown', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email', hint: 'Enter email', error: 'Required' },
    })
    const hint = wrapper.findAll('p').find(p => p.classes().includes('text-gray-500'))
    expect(hint).toBeUndefined()
  })

  it('renders slot content (the input)', () => {
    const wrapper = mount(VFormField, {
      props: { label: 'Email' },
      slots: { default: '<input type="email" />' },
    })
    expect(wrapper.find('input').exists()).toBe(true)
  })
})
