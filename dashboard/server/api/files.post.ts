import { defineEventHandler, readBody, createError } from 'h3'
import { mkdir, writeFile, stat } from 'fs/promises'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || typeof body.path !== 'string' || typeof body.type !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Request body must include "path" (string) and "type" ("file" | "folder")',
    })
  }

  if (body.type !== 'file' && body.type !== 'folder') {
    throw createError({
      statusCode: 400,
      statusMessage: 'type must be "file" or "folder"',
    })
  }

  const resolvedPath = sanitizePath(body.path)

  if (!isAllowedPath(resolvedPath)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  // Check it doesn't already exist
  try {
    await stat(resolvedPath)
    throw createError({
      statusCode: 409,
      statusMessage: 'Path already exists',
    })
  } catch (err: any) {
    if (err.statusCode === 409) throw err
    // ENOENT is expected — path doesn't exist yet
    if (err.code !== 'ENOENT') {
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to check path',
      })
    }
  }

  try {
    if (body.type === 'folder') {
      await mkdir(resolvedPath, { recursive: true })
    } else {
      await writeFile(resolvedPath, '', 'utf-8')
    }
    return { success: true }
  } catch (err: any) {
    throw createError({
      statusCode: 500,
      statusMessage: `Failed to create ${body.type}`,
    })
  }
})
