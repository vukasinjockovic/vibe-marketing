import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VConfirmDialog from '../../components/VConfirmDialog.vue'
import VModal from '../../components/VModal.vue'

// VConfirmDialog uses <VModal> which is auto-imported in Nuxt but must be
// explicitly registered in test environment.
const globalConfig = {
  global: {
    stubs: { Teleport: true },
    components: { VModal },
  },
}

describe('VConfirmDialog', () => {
  const baseProps = {
    modelValue: true,
    title: 'Confirm Action',
    message: 'Are you sure you want to proceed?',
  }

  it('renders the message text', () => {
    const wrapper = mount(VConfirmDialog, {
      props: baseProps,
      ...globalConfig,
    })
    expect(wrapper.text()).toContain('Are you sure you want to proceed?')
  })

  it('renders Cancel and Confirm buttons', () => {
    const wrapper = mount(VConfirmDialog, {
      props: baseProps,
      ...globalConfig,
    })
    const buttons = wrapper.findAll('button')
    const buttonTexts = buttons.map(b => b.text())
    expect(buttonTexts).toContain('Cancel')
    expect(buttonTexts).toContain('Confirm')
  })

  it('uses custom confirm label when provided', () => {
    const wrapper = mount(VConfirmDialog, {
      props: { ...baseProps, confirmLabel: 'Delete' },
      ...globalConfig,
    })
    const buttons = wrapper.findAll('button')
    const buttonTexts = buttons.map(b => b.text())
    expect(buttonTexts).toContain('Delete')
  })

  it('emits confirm when confirm button is clicked', async () => {
    const wrapper = mount(VConfirmDialog, {
      props: baseProps,
      ...globalConfig,
    })
    const confirmBtn = wrapper.findAll('button').find(b => b.text() === 'Confirm')
    await confirmBtn!.trigger('click')
    expect(wrapper.emitted('confirm')).toBeTruthy()
  })

  it('emits update:modelValue false when cancel is clicked', async () => {
    const wrapper = mount(VConfirmDialog, {
      props: baseProps,
      ...globalConfig,
    })
    const cancelBtn = wrapper.findAll('button').find(b => b.text() === 'Cancel')
    await cancelBtn!.trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([false])
  })

  it('disables confirm button when loading is true', () => {
    const wrapper = mount(VConfirmDialog, {
      props: { ...baseProps, loading: true },
      ...globalConfig,
    })
    const confirmBtn = wrapper.findAll('button').find(b => b.text() === 'Confirm')
    expect(confirmBtn).toBeTruthy()
    expect(confirmBtn!.attributes('disabled')).toBeDefined()
  })

  it('applies custom confirmClass', () => {
    const wrapper = mount(VConfirmDialog, {
      props: { ...baseProps, confirmClass: 'bg-red-600 hover:bg-red-700' },
      ...globalConfig,
    })
    const confirmBtn = wrapper.findAll('button').find(b => b.text() === 'Confirm')
    expect(confirmBtn).toBeTruthy()
    expect(confirmBtn!.classes()).toContain('bg-red-600')
  })

  it('uses VModal internally', () => {
    const wrapper = mount(VConfirmDialog, {
      props: baseProps,
      ...globalConfig,
    })
    expect(wrapper.findComponent(VModal).exists()).toBe(true)
  })
})
