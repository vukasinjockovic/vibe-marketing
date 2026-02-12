import { defineEventHandler, getQuery, createError } from 'h3'
import { readFile, stat } from 'fs/promises'
import { extname } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

const TEXT_EXTENSIONS = new Set([
  '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css',
  '.js', '.ts', '.vue', '.jsx', '.tsx', '.xml', '.csv',
  '.toml', '.ini', '.cfg', '.conf', '.sh', '.bash',
  '.py', '.rb', '.go', '.rs', '.java', '.c', '.cpp', '.h',
  '.env', '.gitignore', '.dockerfile', '.sql',
])

const MIME_MAP: Record<string, string> = {
  '.md': 'text/markdown',
  '.txt': 'text/plain',
  '.json': 'application/json',
  '.yaml': 'text/yaml',
  '.yml': 'text/yaml',
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.ts': 'application/typescript',
  '.vue': 'text/x-vue',
  '.py': 'text/x-python',
  '.sh': 'text/x-shellscript',
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

  if (!TEXT_EXTENSIONS.has(ext)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Not a supported text file type',
    })
  }

  try {
    const [content, fileStat] = await Promise.all([
      readFile(resolvedPath, 'utf-8'),
      stat(resolvedPath),
    ])

    return {
      content,
      mimeType: MIME_MAP[ext] || 'text/plain',
      size: fileStat.size,
      modified: fileStat.mtime.toISOString(),
    }
  } catch (err: any) {
    if (err.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: 'File not found',
      })
    }
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read file',
    })
  }
})
