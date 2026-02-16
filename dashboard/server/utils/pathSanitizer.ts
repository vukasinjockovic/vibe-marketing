import { resolve } from 'path'

export const ALLOWED_BASE = '/var/www/vibe-marketing'
const DEFAULT_ROOT = '/var/www/vibe-marketing/projects'

/**
 * Check if a resolved absolute path is within the allowed base directory.
 * Uses path.resolve() to normalize and then checks prefix.
 */
export function isAllowedPath(inputPath: string): boolean {
  // Reject null bytes
  if (inputPath.includes('\0')) {
    return false
  }
  const resolved = resolve(inputPath)
  return resolved === ALLOWED_BASE || resolved.startsWith(ALLOWED_BASE + '/')
}

/**
 * Sanitize a user-provided path, resolving it relative to the allowed base.
 * Returns the resolved absolute path (always within ALLOWED_BASE).
 * For empty/root paths, returns the default projects root.
 */
export function sanitizePath(inputPath: string | undefined | null): string {
  if (!inputPath || inputPath === '/') {
    return DEFAULT_ROOT
  }

  // If already an absolute path within the allowed base, use it directly
  if (inputPath.startsWith(ALLOWED_BASE + '/')) {
    const resolved = resolve(inputPath)
    if (!isAllowedPath(resolved)) return DEFAULT_ROOT
    return resolved
  }

  // Otherwise resolve relative to the allowed base
  const resolved = resolve(ALLOWED_BASE, inputPath.replace(/^\//, ''))

  if (!isAllowedPath(resolved)) {
    return DEFAULT_ROOT
  }

  return resolved
}
