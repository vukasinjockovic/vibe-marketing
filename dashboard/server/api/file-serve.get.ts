import { defineEventHandler, getQuery, createError, setResponseHeader } from 'h3'
import { readFile, stat } from 'fs/promises'
import { extname } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

const BINARY_MIME_MAP: Record<string, string> = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.pdf': 'application/pdf',
  '.zip': 'application/zip',
  '.tar': 'application/x-tar',
  '.gz': 'application/gzip',
}

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const requestedPath = query.path as string | undefined

  if (!requestedPath) {
    throw createError({
      statusCode: 400,
      statusMessage: 'path query parameter is required',
    })
  }

  const resolvedPath = sanitizePath(requestedPath)

  if (!isAllowedPath(resolvedPath)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  const ext = extname(resolvedPath).toLowerCase()
  const mimeType = BINARY_MIME_MAP[ext]

  if (!mimeType) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Unsupported file type for binary serving',
    })
  }

  try {
    const fileStat = await stat(resolvedPath)
    if (fileStat.isDirectory()) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Path is a directory, not a file',
      })
    }

    const content = await readFile(resolvedPath)

    setResponseHeader(event, 'Content-Type', mimeType)
    setResponseHeader(event, 'Content-Length', fileStat.size.toString())
    setResponseHeader(event, 'Cache-Control', 'public, max-age=3600')

    return content
  } catch (err: any) {
    if (err.statusCode) throw err
    if (err.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: 'File not found',
      })
    }
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to serve file',
    })
  }
})
