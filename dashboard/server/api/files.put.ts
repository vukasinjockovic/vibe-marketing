import { defineEventHandler, readBody, createError } from 'h3'
import { rename, stat, mkdir } from 'fs/promises'
import { dirname, join, basename } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

/**
 * Move a file or folder to a new directory.
 * Body: { sourcePath: string, destDir: string }
 * Moves sourcePath into destDir, keeping the original name.
 */
export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || typeof body.sourcePath !== 'string' || typeof body.destDir !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Request body must include "sourcePath" (string) and "destDir" (string)',
    })
  }

  const resolvedSource = sanitizePath(body.sourcePath)
  const resolvedDestDir = sanitizePath(body.destDir)

  if (!isAllowedPath(resolvedSource) || !isAllowedPath(resolvedDestDir)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  const name = basename(resolvedSource)
  const resolvedDest = join(resolvedDestDir, name)

  if (!isAllowedPath(resolvedDest)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: destination outside allowed directory',
    })
  }

  // Don't move into itself
  if (resolvedSource === resolvedDest) {
    return { success: true, noop: true }
  }

  // Prevent moving a folder into its own subtree
  if (resolvedDestDir.startsWith(resolvedSource + '/')) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Cannot move a folder into itself',
    })
  }

  // Check source exists
  try {
    await stat(resolvedSource)
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Source not found' })
    }
    throw createError({ statusCode: 500, statusMessage: 'Failed to check source' })
  }

  // Check dest dir exists
  try {
    const destStat = await stat(resolvedDestDir)
    if (!destStat.isDirectory()) {
      throw createError({ statusCode: 400, statusMessage: 'Destination is not a directory' })
    }
  } catch (err: any) {
    if (err.statusCode) throw err
    if (err.code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Destination directory not found' })
    }
    throw createError({ statusCode: 500, statusMessage: 'Failed to check destination' })
  }

  // Check dest doesn't already have this name
  try {
    await stat(resolvedDest)
    throw createError({ statusCode: 409, statusMessage: `"${name}" already exists in the destination folder` })
  } catch (err: any) {
    if (err.statusCode === 409) throw err
    if (err.code !== 'ENOENT') {
      throw createError({ statusCode: 500, statusMessage: 'Failed to check destination' })
    }
  }

  try {
    await rename(resolvedSource, resolvedDest)
    return { success: true }
  } catch (err: any) {
    throw createError({ statusCode: 500, statusMessage: 'Failed to move' })
  }
})
