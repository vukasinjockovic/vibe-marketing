import { defineEventHandler, readBody, createError } from 'h3'
import { rename, stat } from 'fs/promises'
import { dirname, join } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || typeof body.path !== 'string' || typeof body.newName !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Request body must include "path" (string) and "newName" (string)',
    })
  }

  const newName = body.newName.trim()
  if (!newName || newName.includes('/') || newName.includes('\\')) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid name: must not be empty or contain path separators',
    })
  }

  const resolvedOld = sanitizePath(body.path)
  if (!isAllowedPath(resolvedOld)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  const resolvedNew = join(dirname(resolvedOld), newName)
  if (!isAllowedPath(resolvedNew)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: new path outside allowed directory',
    })
  }

  // Check source exists
  try {
    await stat(resolvedOld)
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Source path not found' })
    }
    throw createError({ statusCode: 500, statusMessage: 'Failed to check source' })
  }

  // Check destination doesn't exist
  try {
    await stat(resolvedNew)
    throw createError({ statusCode: 409, statusMessage: 'A file or folder with that name already exists' })
  } catch (err: any) {
    if (err.statusCode === 409) throw err
    if (err.code !== 'ENOENT') {
      throw createError({ statusCode: 500, statusMessage: 'Failed to check destination' })
    }
  }

  try {
    await rename(resolvedOld, resolvedNew)
    return { success: true }
  } catch (err: any) {
    throw createError({ statusCode: 500, statusMessage: 'Failed to rename' })
  }
})
