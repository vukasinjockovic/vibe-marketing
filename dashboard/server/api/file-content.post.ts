import { defineEventHandler, readBody, createError } from 'h3'
import { writeFile, stat } from 'fs/promises'
import { extname } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

const WRITABLE_EXTENSIONS = new Set([
  '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css',
  '.js', '.ts', '.vue', '.jsx', '.tsx', '.xml', '.csv',
  '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
  '.py', '.rb', '.go', '.rs', '.java', '.c', '.cpp', '.h',
  '.sql',
])

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body || typeof body.path !== 'string' || typeof body.content !== 'string') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Request body must include "path" (string) and "content" (string)',
    })
  }

  const resolvedPath = sanitizePath(body.path)

  if (!isAllowedPath(resolvedPath)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  const ext = extname(resolvedPath).toLowerCase()

  if (!WRITABLE_EXTENSIONS.has(ext)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Not a writable file type',
    })
  }

  // Verify the file already exists (don't create new files via this endpoint)
  try {
    const fileStat = await stat(resolvedPath)
    if (fileStat.isDirectory()) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Path is a directory, not a file',
      })
    }
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: 'File not found. This endpoint only updates existing files.',
      })
    }
    if (err.statusCode) throw err
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to verify file',
    })
  }

  try {
    await writeFile(resolvedPath, body.content, 'utf-8')
    return { success: true }
  } catch (err: any) {
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to write file',
    })
  }
})
