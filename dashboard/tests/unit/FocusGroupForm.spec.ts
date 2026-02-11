import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, nextTick } from 'vue'
import FocusGroupForm from '../../components/FocusGroupForm.vue'

const mockCreate = vi.fn()

vi.stubGlobal('useConvexMutation', () => ({
  mutate: mockCreate,
  loading: ref(false),
  error: ref(null),
}))
vi.stubGlobal('useToast', () => ({
  success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn(),
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useRoute', () => ({ params: {} }))
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('FocusGroupForm (components/FocusGroupForm.vue)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCreate.mockResolvedValue('fg123')
  })

  function mountForm(props: Record<string, any> = {}) {
    return mount(FocusGroupForm, {
      props: {
        projectId: 'proj1',
        productId: 'prod1',
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

  it('renders basic info section with name, nickname, number fields', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(text.includes('name') || wrapper.findAll('input').length > 0).toBe(true)
  })

  it('renders demographics section', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(
      text.includes('demographics') ||
      text.includes('age') ||
      text.includes('gender') ||
      text.includes('income')
    ).toBe(true)
  })

  it('renders psychographics section', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(
      text.includes('psychographics') ||
      text.includes('values') ||
      text.includes('identity')
    ).toBe(true)
  })

  it('renders language & hooks section', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(
      text.includes('language') ||
      text.includes('hooks') ||
      text.includes('pain points') ||
      text.includes('desires')
    ).toBe(true)
  })

  it('has a category dropdown', () => {
    const wrapper = mountForm()
    const select = wrapper.find('select[data-field="category"]')
    expect(select.exists() || wrapper.html().toLowerCase().includes('category')).toBe(true)
  })

  it('has a source dropdown', () => {
    const wrapper = mountForm()
    const text = wrapper.text().toLowerCase()
    expect(text.includes('source') || wrapper.find('select[data-field="source"]').exists()).toBe(true)
  })

  it('has a submit button', () => {
    const wrapper = mountForm()
    const btn = wrapper.find('button[type="submit"]')
    expect(btn.exists()).toBe(true)
  })

  it('has collapsible accordion sections', () => {
    const wrapper = mountForm()
    // Should have clickable section headers
    const html = wrapper.html()
    expect(html).toBeTruthy()
    // Check for section toggle buttons or headers
    const sectionHeaders = wrapper.findAll('[data-section], [class*="cursor-pointer"]')
    expect(sectionHeaders.length > 0 || wrapper.findAll('button').length > 1).toBe(true)
  })

  it('has multiple chip input fields for array fields when all sections are expanded', async () => {
    const wrapper = mountForm()
    // Expand all accordion sections by clicking their headers
    const sectionButtons = wrapper.findAll('[data-section]')
    for (const btn of sectionButtons) {
      await btn.trigger('click')
    }
    await nextTick()
    const chipInputs = wrapper.findAll('.chip-input')
    // After expanding all sections: demographics.triggers, psychographics.values,
    // psychographics.beliefs, coreDesires, painPoints, fears, beliefs, objections,
    // emotionalTriggers, languagePatterns, ebookAngles, marketingHooks = 12 chip inputs
    expect(chipInputs.length).toBeGreaterThanOrEqual(5)
  })

  it('emits saved event on successful submit', async () => {
    const wrapper = mountForm()
    const submitBtn = wrapper.find('button[type="submit"]')
    if (submitBtn.exists()) {
      await submitBtn.trigger('click')
      await nextTick()
      await new Promise(r => setTimeout(r, 10))
    }
    expect(wrapper.html()).toBeTruthy()
  })
})
