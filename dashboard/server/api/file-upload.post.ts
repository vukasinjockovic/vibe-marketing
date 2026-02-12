import { defineEventHandler, readMultipartFormData, createError } from 'h3'
import { writeFile, stat } from 'fs/promises'
import { join } from 'path'
import { sanitizePath, isAllowedPath } from '../utils/pathSanitizer'

/**
 * Upload a file to a target directory.
 * Multipart form: field "file" (the file) + field "destDir" (target directory path).
 */
export default defineEventHandler(async (event) => {
  const formData = await readMultipartFormData(event)

  if (!formData || formData.length === 0) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Multipart form data required with "file" and "destDir" fields',
    })
  }

  const filePart = formData.find((p) => p.name === 'file')
  const destDirPart = formData.find((p) => p.name === 'destDir')

  if (!filePart || !filePart.data || !filePart.filename) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing "file" field with a filename',
    })
  }

  if (!destDirPart || !destDirPart.data) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing "destDir" field',
    })
  }

  const destDir = destDirPart.data.toString('utf-8').trim()
  const resolvedDir = sanitizePath(destDir)

  if (!isAllowedPath(resolvedDir)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: path outside allowed directory',
    })
  }

  // Sanitize filename: strip path separators
  const filename = filePart.filename.replace(/[/\\]/g, '').trim()
  if (!filename) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid filename',
    })
  }

  const resolvedDest = join(resolvedDir, filename)

  if (!isAllowedPath(resolvedDest)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Access denied: destination outside allowed directory',
    })
  }

  // Check dest dir exists
  try {
    const dirStat = await stat(resolvedDir)
    if (!dirStat.isDirectory()) {
      throw createError({ statusCode: 400, statusMessage: 'Destination is not a directory' })
    }
  } catch (err: any) {
    if (err.statusCode) throw err
    if (err.code === 'ENOENT') {
      throw createError({ statusCode: 404, statusMessage: 'Destination directory not found' })
    }
    throw createError({ statusCode: 500, statusMessage: 'Failed to check destination' })
  }

  // Check file doesn't already exist
  try {
    await stat(resolvedDest)
    throw createError({ statusCode: 409, statusMessage: `"${filename}" already exists in the destination folder` })
  } catch (err: any) {
    if (err.statusCode === 409) throw err
    if (err.code !== 'ENOENT') {
      throw createError({ statusCode: 500, statusMessage: 'Failed to check destination' })
    }
  }

  try {
    await writeFile(resolvedDest, filePart.data)
    return { success: true, filename, path: resolvedDest }
  } catch (err: any) {
    throw createError({ statusCode: 500, statusMessage: 'Failed to write uploaded file' })
  }
})
