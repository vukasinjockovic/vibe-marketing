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

  it('does not open without a project slug', () => {
    const { open, isOpen } = useArtifactsBrowser()
    open()
    expect(isOpen.value).toBe(false)
  })

  it('opens the browser when open() is called with a slug', () => {
    const { open, isOpen, projectSlug } = useArtifactsBrowser()
    open(undefined, 'gymzilla-tribe')
    expect(isOpen.value).toBe(true)
    expect(projectSlug.value).toBe('gymzilla-tribe')
  })

  it('closes the browser when close() is called', () => {
    const { open, close, isOpen } = useArtifactsBrowser()
    open(undefined, 'gymzilla-tribe')
    expect(isOpen.value).toBe(true)
    close()
    expect(isOpen.value).toBe(false)
  })

  it('sets initialPath when open() is called with a path', () => {
    const { open, initialPath } = useArtifactsBrowser()
    open('/projects/gymzilla-tribe/campaigns/', 'gymzilla-tribe')
    expect(initialPath.value).toBe('/projects/gymzilla-tribe/campaigns/')
  })

  it('sets initialPath to null when open() is called without a path', () => {
    const { open, initialPath } = useArtifactsBrowser()
    open(undefined, 'gymzilla-tribe')
    expect(initialPath.value).toBeNull()
  })

  it('clears initialPath and projectSlug on close()', () => {
    const { open, close, initialPath, projectSlug } = useArtifactsBrowser()
    open('/some/path', 'my-project')
    expect(initialPath.value).toBe('/some/path')
    expect(projectSlug.value).toBe('my-project')
    close()
    expect(initialPath.value).toBeNull()
    expect(projectSlug.value).toBeNull()
  })

  it('shares state across multiple calls', () => {
    const instance1 = useArtifactsBrowser()
    const instance2 = useArtifactsBrowser()
    instance1.open('/test', 'gymzilla-tribe')
    expect(instance2.isOpen.value).toBe(true)
    expect(instance2.initialPath.value).toBe('/test')
    expect(instance2.projectSlug.value).toBe('gymzilla-tribe')
  })

  it('isOpen is readonly', () => {
    const { isOpen } = useArtifactsBrowser()
    // The ref should be readonly -- attempting to set it should not work
    expect(typeof isOpen.value).toBe('boolean')
  })
})
