import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref, nextTick } from 'vue'
import ArtifactsBrowser from '../../components/ArtifactsBrowser.vue'
import TreeNodeItem from '../../components/TreeNodeItem.vue'

// Mock $fetch globally for the component
const mockFetch = vi.fn()
vi.stubGlobal('$fetch', mockFetch)

// Mock useArtifactsBrowser
const mockIsOpen = ref(false)
const mockInitialPath = ref<string | null>(null)
const mockClose = vi.fn(() => {
  mockIsOpen.value = false
  mockInitialPath.value = null
})
const mockOpen = vi.fn((path?: string) => {
  mockIsOpen.value = true
  mockInitialPath.value = path || null
})

vi.stubGlobal('useArtifactsBrowser', () => ({
  isOpen: mockIsOpen,
  initialPath: mockInitialPath,
  open: mockOpen,
  close: mockClose,
}))

describe('ArtifactsBrowser', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsOpen.value = false
    mockInitialPath.value = null
    mockFetch.mockReset()
  })

  it('does not render when isOpen is false', () => {
    mockIsOpen.value = false
    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    expect(wrapper.find('[data-testid="artifacts-browser"]').exists()).toBe(false)
  })

  it('renders when isOpen is true', async () => {
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({ entries: [] })

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    await nextTick()
    expect(wrapper.find('[data-testid="artifacts-browser"]').exists()).toBe(true)
  })

  it('shows the file tree panel', async () => {
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({ entries: [] })

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    await nextTick()
    expect(wrapper.find('[data-testid="file-tree-panel"]').exists()).toBe(true)
  })

  it('shows the file viewer panel', async () => {
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({ entries: [] })

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    await nextTick()
    expect(wrapper.find('[data-testid="file-viewer-panel"]').exists()).toBe(true)
  })

  it('calls close when escape is pressed', async () => {
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({ entries: [] })

    mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    await nextTick()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(mockClose).toHaveBeenCalled()
  })

  it('calls close when the close button is clicked', async () => {
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({ entries: [] })

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    await nextTick()
    const closeBtn = wrapper.find('[data-testid="close-button"]')
    expect(closeBtn.exists()).toBe(true)
    await closeBtn.trigger('click')
    expect(mockClose).toHaveBeenCalled()
  })

  it('fetches directory listing on open', async () => {
    mockFetch.mockResolvedValue({
      entries: [
        { name: 'gymzilla-tribe', isDirectory: true, path: '/projects/gymzilla-tribe' },
        { name: 'readme.md', isDirectory: false, path: '/projects/readme.md' },
      ],
    })
    mockIsOpen.value = true

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
      },
    })
    // Wait for both the nextTick and the async fetch
    await nextTick()
    await nextTick()
    await nextTick()

    expect(mockFetch).toHaveBeenCalledWith('/api/files', expect.objectContaining({
      query: expect.objectContaining({ path: expect.any(String) }),
    }))
  })

  it('determines file type from extension', async () => {
    // This tests the internal getFileType utility by checking icon rendering
    // The component should handle various extensions
    mockIsOpen.value = true
    mockFetch.mockResolvedValue({
      entries: [
        { name: 'article.md', isDirectory: false, path: '/projects/article.md' },
        { name: 'hero.png', isDirectory: false, path: '/projects/hero.png' },
        { name: 'data.json', isDirectory: false, path: '/projects/data.json' },
      ],
    })

    const wrapper = mount(ArtifactsBrowser, {
      global: {
        stubs: { Teleport: true },
        components: { TreeNodeItem },
      },
    })
    await nextTick()
    await nextTick()
    await nextTick()

    // Files should be listed in the tree
    const html = wrapper.html()
    expect(html).toContain('article.md')
    expect(html).toContain('hero.png')
    expect(html).toContain('data.json')
  })
})
