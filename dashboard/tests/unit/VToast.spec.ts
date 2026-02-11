import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import VToast from '../../components/VToast.vue'

// Override the global useToast mock with test-controllable refs
const mockToasts = ref<Array<{ id: number; type: string; message: string }>>([])
const mockDismiss = vi.fn()

// Replace the global mock set up in tests/setup.ts
;(globalThis as any).__useToastMock = {
  toasts: mockToasts,
  dismiss: mockDismiss,
}

describe('VToast', () => {
  beforeEach(() => {
    mockToasts.value = []
    mockDismiss.mockClear()
  })

  it('renders toast messages', () => {
    mockToasts.value = [
      { id: 1, type: 'success', message: 'Item saved' },
    ]
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.text()).toContain('Item saved')
  })

  it('applies success color class', () => {
    mockToasts.value = [
      { id: 1, type: 'success', message: 'Done' },
    ]
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('bg-green-600')
  })

  it('applies error color class', () => {
    mockToasts.value = [
      { id: 1, type: 'error', message: 'Failed' },
    ]
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.html()).toContain('bg-red-600')
  })

  it('renders multiple toasts', () => {
    mockToasts.value = [
      { id: 1, type: 'success', message: 'First' },
      { id: 2, type: 'error', message: 'Second' },
    ]
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.text()).toContain('First')
    expect(wrapper.text()).toContain('Second')
  })

  it('calls dismiss when close button is clicked', async () => {
    mockToasts.value = [
      { id: 42, type: 'info', message: 'Test' },
    ]
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    const closeBtn = wrapper.find('button')
    await closeBtn.trigger('click')
    expect(mockDismiss).toHaveBeenCalledWith(42)
  })

  it('renders empty when no toasts', () => {
    mockToasts.value = []
    const wrapper = mount(VToast, {
      global: {
        stubs: { Teleport: true },
      },
    })
    // Container exists but no toast item divs inside
    expect(wrapper.findAll('[class*="rounded-lg"][class*="px-4"]').length).toBe(0)
  })
})
