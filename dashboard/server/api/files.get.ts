import { defineEventHandler, getQuery, createError } from 'h3'
import { readdir, stat } from 'fs/promises'
import { join } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const requestedPath = query.path as string | undefined

  const resolvedPath = sanitizePath(requestedPath)

  if (!isAllowedPath(resolvedPath)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  try {
    const dirEntries = await readdir(resolvedPath, { withFileTypes: true })

    const entries = await Promise.all(
      dirEntries
        .filter((entry) => !entry.name.startsWith('.'))
        .map(async (entry) => {
          const fullPath = join(resolvedPath, entry.name)
          // Compute relative path from the vibe-marketing root
          const relativePath = fullPath.replace('/var/www/vibe-marketing', '')

          let size: number | undefined
          let modified: string | undefined

          try {
            const info = await stat(fullPath)
            size = info.size
            modified = info.mtime.toISOString()
          } catch {
            // stat may fail for symlinks etc -- that's ok
          }

          return {
            name: entry.name,
            isDirectory: entry.isDirectory(),
            path: relativePath,
            size,
            modified,
          }
        }),
    )

    // Sort: directories first, then alphabetical
    entries.sort((a, b) => {
      if (a.isDirectory && !b.isDirectory) return -1
      if (!a.isDirectory && b.isDirectory) return 1
      return a.name.localeCompare(b.name)
    })

    return { entries }
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: 'Directory not found',
      })
    }
    if (err.code === 'ENOTDIR') {
      throw createError({
        statusCode: 400,
        statusMessage: 'Path is not a directory',
      })
    }
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read directory',
    })
  }
})
