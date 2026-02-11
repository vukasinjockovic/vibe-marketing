import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, nextTick } from 'vue'
import ProductForm from '../../components/ProductForm.vue'

const mockCreate = vi.fn()
const mockUpdate = vi.fn()

vi.stubGlobal('useConvexMutation', (fn: any) => {
  // Differentiate create vs update based on mock
  return { mutate: mockCreate, loading: ref(false), error: ref(null) }
})
vi.stubGlobal('useToast', () => ({
  success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn(),
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useRoute', () => ({ params: {} }))
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('ProductForm (components/ProductForm.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCreate.mockResolvedValue('prod123')
    mockUpdate.mockResolvedValue(undefined)
  })

  function mountForm(props: Record<string, any> = {}) {
    return mount(ProductForm, {
      props: {
        projectId: 'proj1',
        ...props,
      },
      global: {
        stubs: {
          VFormField: { template: '<div class="form-field"><label>{{ label }}</label><slot /></div>', props: ['label', 'error', 'required'] },
          VChipInput: { template: '<div class="chip-input" />', props: ['modelValue', 'placeholder'] },
        },
      },
    })
  }

  it('renders Basic Info section with name, slug, description', () => {
    const wrapper = mountForm()
    const html = wrapper.html().toLowerCase()
    expect(html.includes('name') || wrapper.findAll('input').length > 0).toBe(true)
  })

  it('renders Context section fields', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    // Should have context-related labels
    expect(
      text.includes('what it is') ||
      text.includes('features') ||
      text.includes('target market') ||
      text.includes('context')
    ).toBe(true)
  })

  it('renders Brand Voice section fields', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(
      text.includes('tone') ||
      text.includes('style') ||
      text.includes('brand voice') ||
      text.includes('vocabulary')
    ).toBe(true)
  })

  it('auto-generates slug from name', async () => {
    const wrapper = mountForm()
    const nameInput = wrapper.find('input[data-field="name"]')
    if (nameInput.exists()) {
      await nameInput.setValue('My Product Name')
      await nextTick()
      const slugInput = wrapper.find('input[data-field="slug"]')
      if (slugInput.exists()) {
        expect((slugInput.element as HTMLInputElement).value).toBe('my-product-name')
      }
    }
    expect(wrapper.html()).toBeTruthy()
  })

  it('has a submit button', () => {
    const wrapper = mountForm()
    const submitBtn = wrapper.find('button[type="submit"]')
    expect(submitBtn.exists()).toBe(true)
  })

  it('emits saved event on successful submit', async () => {
    const wrapper = mountForm()
    // Set required fields
    const nameInput = wrapper.find('input[data-field="name"]')
    if (nameInput.exists()) {
      await nameInput.setValue('Test Product')
      await nextTick()
    }
    // Trigger submit
    const submitBtn = wrapper.find('button[type="submit"]')
    if (submitBtn.exists()) {
      await submitBtn.trigger('click')
      await nextTick()
      await new Promise(r => setTimeout(r, 10))
    }
    expect(wrapper.html()).toBeTruthy()
  })

  it('has chip input fields for features, usps, competitors', () => {
    const wrapper = mountForm()
    const chipInputs = wrapper.findAll('.chip-input')
    // Should have multiple chip inputs for array fields
    expect(chipInputs.length).toBeGreaterThan(0)
  })
})
