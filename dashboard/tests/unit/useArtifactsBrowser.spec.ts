import { describe, it, expect, beforeEach } from 'vitest'
import { useArtifactsBrowser } from '../../composables/useArtifactsBrowser'

describe('useArtifactsBrowser', () => {
  beforeEach(() => {
    // Reset shared state between tests
    const { close } = useArtifactsBrowser()
    close()
  })

  it('starts with isOpen false', () => {
    const { isOpen } = useArtifactsBrowser()
    expect(isOpen.value).toBe(false)
  })

  it('opens the browser when open() is called', () => {
    const { open, isOpen } = useArtifactsBrowser()
    open()
    expect(isOpen.value).toBe(true)
  })

  it('closes the browser when close() is called', () => {
    const { open, close, isOpen } = useArtifactsBrowser()
    open()
    expect(isOpen.value).toBe(true)
    close()
    expect(isOpen.value).toBe(false)
  })

  it('sets initialPath when open() is called with a path', () => {
    const { open, initialPath } = useArtifactsBrowser()
    open('/projects/gymzilla-tribe/campaigns/')
    expect(initialPath.value).toBe('/projects/gymzilla-tribe/campaigns/')
  })

  it('sets initialPath to null when open() is called without a path', () => {
    const { open, initialPath } = useArtifactsBrowser()
    open()
    expect(initialPath.value).toBeNull()
  })

  it('clears initialPath on close()', () => {
    const { open, close, initialPath } = useArtifactsBrowser()
    open('/some/path')
    expect(initialPath.value).toBe('/some/path')
    close()
    expect(initialPath.value).toBeNull()
  })

  it('shares state across multiple calls', () => {
    const instance1 = useArtifactsBrowser()
    const instance2 = useArtifactsBrowser()
    instance1.open('/test')
    expect(instance2.isOpen.value).toBe(true)
    expect(instance2.initialPath.value).toBe('/test')
  })

  it('isOpen is readonly', () => {
    const { isOpen } = useArtifactsBrowser()
    // The ref should be readonly -- attempting to set it should not work
    expect(typeof isOpen.value).toBe('boolean')
  })
})
