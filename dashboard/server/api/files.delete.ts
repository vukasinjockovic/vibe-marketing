import { defineEventHandler, readBody, createError } from 'h3'
import { rm, stat } from 'fs/promises'
import { sanitizePath, isAllowedPath, ALLOWED_BASE } from '../utils/pathSanitizer'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || typeof body.path !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Request body must include "path" (string)',
    })
  }

  const resolvedPath = sanitizePath(body.path)

  if (!isAllowedPath(resolvedPath)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  // Prevent deleting the base directory itself
  if (resolvedPath === ALLOWED_BASE) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Cannot delete the root directory',
    })
  }

  try {
    const fileStat = await stat(resolvedPath)
    await rm(resolvedPath, { recursive: fileStat.isDirectory() })
    return { success: true }
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: 'Path not found',
      })
    }
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to delete',
    })
  }
})
