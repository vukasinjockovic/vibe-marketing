import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import VModal from '../../components/VModal.vue'

describe('VModal', () => {
  it('renders when modelValue is true', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test Modal' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.text()).toContain('Test Modal')
  })

  it('does not render content when modelValue is false', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: false, title: 'Hidden Modal' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.text()).not.toContain('Hidden Modal')
  })

  it('renders the title in h2', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'My Title' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.find('h2').text()).toBe('My Title')
  })

  it('renders default slot content', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test' },
      slots: { default: '<p>Modal body content</p>' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.text()).toContain('Modal body content')
  })

  it('renders footer slot when provided', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test' },
      slots: { footer: '<button class="save-btn">Save</button>' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.find('.save-btn').text()).toBe('Save')
  })

  it('emits update:modelValue false when close button is clicked', async () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test' },
      global: {
        stubs: { Teleport: true },
      },
    })
    // Find the close button (has x-mark icon)
    const closeBtn = wrapper.findAll('button').find(b => b.find('.i-heroicons-x-mark').exists())
    expect(closeBtn).toBeTruthy()
    await closeBtn!.trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
  })

  it('applies correct size class for sm', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test', size: 'sm' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('max-w-md')
  })

  it('applies correct size class for lg', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test', size: 'lg' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('max-w-2xl')
  })

  it('applies correct size class for xl', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test', size: 'xl' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('max-w-4xl')
  })

  it('applies default size class (md/max-w-lg)', () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test' },
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('max-w-lg')
  })

  it('emits close on Escape keydown', async () => {
    const wrapper = mount(VModal, {
      props: { modelValue: true, title: 'Test' },
      global: {
        stubs: { Teleport: true },
      },
    })
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
  })
})
