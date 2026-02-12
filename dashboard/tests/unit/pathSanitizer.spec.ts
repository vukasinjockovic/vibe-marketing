import { describe, it, expect } from 'vitest'
import { sanitizePath, isAllowedPath, ALLOWED_BASE } from '../../server/utils/pathSanitizer'

describe('pathSanitizer', () => {
  describe('ALLOWED_BASE', () => {
    it('is set to /var/www/vibe-marketing', () => {
      expect(ALLOWED_BASE).toBe('/var/www/vibe-marketing')
    })
  })

  describe('sanitizePath', () => {
    it('resolves a relative path within allowed base', () => {
      const result = sanitizePath('/projects/gymzilla-tribe/campaigns/')
      expect(result).toBe('/var/www/vibe-marketing/projects/gymzilla-tribe/campaigns')
    })

    it('resolves root to allowed base + /projects', () => {
      const result = sanitizePath('/')
      expect(result).toBe('/var/www/vibe-marketing/projects')
    })

    it('resolves empty path to allowed base + /projects', () => {
      const result = sanitizePath('')
      expect(result).toBe('/var/www/vibe-marketing/projects')
    })

    it('resolves undefined path to allowed base + /projects', () => {
      const result = sanitizePath(undefined)
      expect(result).toBe('/var/www/vibe-marketing/projects')
    })
  })

  describe('isAllowedPath', () => {
    it('allows paths within /var/www/vibe-marketing/', () => {
      expect(isAllowedPath('/var/www/vibe-marketing/projects/foo')).toBe(true)
    })

    it('allows the base path itself', () => {
      expect(isAllowedPath('/var/www/vibe-marketing')).toBe(true)
    })

    it('rejects paths outside the base', () => {
      expect(isAllowedPath('/etc/passwd')).toBe(false)
    })

    it('rejects directory traversal attempts', () => {
      expect(isAllowedPath('/var/www/vibe-marketing/../../../etc/passwd')).toBe(false)
    })

    it('rejects paths that start with the base but traverse out', () => {
      // path.resolve would normalize this
      expect(isAllowedPath('/var/www/vibe-marketing/projects/../../etc/passwd')).toBe(false)
    })

    it('allows deeply nested paths', () => {
      expect(isAllowedPath('/var/www/vibe-marketing/projects/foo/campaigns/bar/drafts/article.md')).toBe(true)
    })

    it('rejects null-byte injection attempts', () => {
      expect(isAllowedPath('/var/www/vibe-marketing/projects/foo\0/etc/passwd')).toBe(false)
    })
  })
})
