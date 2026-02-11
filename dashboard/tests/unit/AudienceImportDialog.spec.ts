import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import AudienceImportDialog from '../../components/AudienceImportDialog.vue'

describe('AudienceImportDialog', () => {
  const defaultProps = {
    modelValue: true,
    projectId: 'proj123',
    productId: 'prod456',
  }

  beforeEach(() => {
    vi.stubGlobal('useToast', () => ({
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
      warning: vi.fn(),
      toasts: ref([]),
      dismiss: vi.fn(),
      show: vi.fn(),
    }))
    vi.stubGlobal('useConvexMutation', () => ({
      mutate: vi.fn().mockResolvedValue('doc123'),
      loading: ref(false),
      error: ref(null),
    }))
    vi.stubGlobal('useConvexQuery', () => ({
      data: ref({ _id: 'pipeline123', slug: 'document-import' }),
      loading: ref(false),
      error: ref(null),
    }))
  })

  it('renders when modelValue is true', () => {
    const wrapper = mount(AudienceImportDialog, {
      props: defaultProps,
      global: {
        stubs: { VModal: { template: '<div><slot /></div>', props: ['modelValue', 'title'] } },
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has a file input accepting .md, .txt, .docx, .pdf', () => {
    const wrapper = mount(AudienceImportDialog, {
      props: defaultProps,
      global: {
        stubs: { VModal: { template: '<div><slot /></div>', props: ['modelValue', 'title'] } },
      },
    })
    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('accept')).toContain('.md')
    expect(input.attributes('accept')).toContain('.txt')
    expect(input.attributes('accept')).toContain('.docx')
    expect(input.attributes('accept')).toContain('.pdf')
  })

  it('has auto-enrich checkbox defaulting to checked', () => {
    const wrapper = mount(AudienceImportDialog, {
      props: defaultProps,
      global: {
        stubs: { VModal: { template: '<div><slot /></div>', props: ['modelValue', 'title'] } },
      },
    })
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.exists()).toBe(true)
    expect((checkbox.element as HTMLInputElement).checked).toBe(true)
  })

  it('has a drag and drop zone', () => {
    const wrapper = mount(AudienceImportDialog, {
      props: defaultProps,
      global: {
        stubs: { VModal: { template: '<div><slot /></div>', props: ['modelValue', 'title'] } },
      },
    })
    const dropZone = wrapper.find('[data-testid="drop-zone"]')
    expect(dropZone.exists()).toBe(true)
  })

  it('emits update:modelValue when closing', async () => {
    const wrapper = mount(AudienceImportDialog, {
      props: defaultProps,
      global: {
        stubs: {
          VModal: {
            template: '<div><slot /><button data-testid="close" @click="$emit(\'update:modelValue\', false)">Close</button></div>',
            props: ['modelValue', 'title'],
            emits: ['update:modelValue'],
          },
        },
      },
    })
    await wrapper.find('[data-testid="close"]').trigger('click')
    expect(wrapper.emitted()['update:modelValue']).toBeTruthy()
  })
})
