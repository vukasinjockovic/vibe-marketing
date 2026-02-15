import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

// Test the file extension utility function that determines content display mode
describe('Resource Detail - File Type Detection', () => {
  // These utility functions will be extracted into a composable
  function getFileExtension(filePath: string | undefined | null): string {
    if (!filePath) return ''
    const match = filePath.match(/\.(\w+)$/i)
    return match ? match[1].toLowerCase() : ''
  }

  function getContentDisplayMode(filePath: string | undefined | null, content: string | undefined | null): string {
    // Content source priority:
    // 1. If content exists in DB, check if it looks like markdown
    // 2. If filePath exists, determine by extension
    // 3. If neither, return 'empty'

    const ext = getFileExtension(filePath)

    // Markdown
    if (ext === 'md' || (!ext && content)) return 'markdown'
    // Plain text
    if (['txt', 'csv', 'log'].includes(ext)) return 'plaintext'
    // HTML
    if (ext === 'html' || ext === 'htm') return 'html'
    // PDF
    if (ext === 'pdf') return 'pdf'
    // Images
    if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'].includes(ext)) return 'image'
    // Video
    if (['mp4', 'webm', 'mov'].includes(ext)) return 'video'
    // Audio
    if (['mp3', 'wav', 'ogg'].includes(ext)) return 'audio'
    // Office documents
    if (['docx', 'doc'].includes(ext)) return 'office-doc'
    // Spreadsheets
    if (['xlsx', 'xls'].includes(ext)) return 'office-sheet'
    // Presentations
    if (['pptx', 'ppt'].includes(ext)) return 'office-pres'
    // Code files
    if (['js', 'ts', 'py', 'sh', 'json', 'yaml', 'yml', 'vue', 'jsx', 'tsx'].includes(ext)) return 'code'
    // If we have content but unknown extension, treat as markdown
    if (content) return 'markdown'
    // Unsupported
    if (ext) return 'unsupported'
    return 'empty'
  }

  it('detects markdown files', () => {
    expect(getContentDisplayMode('research/output.md', null)).toBe('markdown')
  })

  it('detects plain text files', () => {
    expect(getContentDisplayMode('data/export.txt', null)).toBe('plaintext')
    expect(getContentDisplayMode('data/report.csv', null)).toBe('plaintext')
  })

  it('detects HTML files', () => {
    expect(getContentDisplayMode('pages/landing.html', null)).toBe('html')
    expect(getContentDisplayMode('pages/landing.htm', null)).toBe('html')
  })

  it('detects PDF files', () => {
    expect(getContentDisplayMode('docs/guide.pdf', null)).toBe('pdf')
  })

  it('detects image files', () => {
    expect(getContentDisplayMode('assets/logo.png', null)).toBe('image')
    expect(getContentDisplayMode('assets/photo.jpg', null)).toBe('image')
    expect(getContentDisplayMode('assets/photo.jpeg', null)).toBe('image')
    expect(getContentDisplayMode('assets/banner.gif', null)).toBe('image')
    expect(getContentDisplayMode('assets/hero.webp', null)).toBe('image')
    expect(getContentDisplayMode('assets/icon.svg', null)).toBe('image')
  })

  it('detects video files', () => {
    expect(getContentDisplayMode('media/promo.mp4', null)).toBe('video')
    expect(getContentDisplayMode('media/clip.webm', null)).toBe('video')
    expect(getContentDisplayMode('media/recording.mov', null)).toBe('video')
  })

  it('detects audio files', () => {
    expect(getContentDisplayMode('audio/podcast.mp3', null)).toBe('audio')
    expect(getContentDisplayMode('audio/sample.wav', null)).toBe('audio')
    expect(getContentDisplayMode('audio/track.ogg', null)).toBe('audio')
  })

  it('detects Office documents', () => {
    expect(getContentDisplayMode('docs/report.docx', null)).toBe('office-doc')
    expect(getContentDisplayMode('docs/legacy.doc', null)).toBe('office-doc')
  })

  it('detects spreadsheets', () => {
    expect(getContentDisplayMode('data/analysis.xlsx', null)).toBe('office-sheet')
    expect(getContentDisplayMode('data/old.xls', null)).toBe('office-sheet')
  })

  it('detects presentations', () => {
    expect(getContentDisplayMode('slides/deck.pptx', null)).toBe('office-pres')
    expect(getContentDisplayMode('slides/old.ppt', null)).toBe('office-pres')
  })

  it('detects code files', () => {
    expect(getContentDisplayMode('scripts/build.js', null)).toBe('code')
    expect(getContentDisplayMode('scripts/main.ts', null)).toBe('code')
    expect(getContentDisplayMode('config.json', null)).toBe('code')
    expect(getContentDisplayMode('config.yaml', null)).toBe('code')
  })

  it('falls back to markdown when content exists but no file path', () => {
    expect(getContentDisplayMode(null, '# Hello World\nSome content')).toBe('markdown')
    expect(getContentDisplayMode(undefined, 'Some text content')).toBe('markdown')
  })

  it('falls back to markdown when content exists with unknown extension', () => {
    expect(getContentDisplayMode('file.unknown', '# Hello')).toBe('markdown')
  })

  it('returns unsupported for unknown extensions without content', () => {
    expect(getContentDisplayMode('file.xyz', null)).toBe('unsupported')
  })

  it('returns empty when no file path and no content', () => {
    expect(getContentDisplayMode(null, null)).toBe('empty')
    expect(getContentDisplayMode(undefined, undefined)).toBe('empty')
    expect(getContentDisplayMode('', '')).toBe('empty')
  })

  it('handles file paths with multiple dots', () => {
    expect(getContentDisplayMode('file.name.with.dots.md', null)).toBe('markdown')
    expect(getContentDisplayMode('archive.2024.01.pdf', null)).toBe('pdf')
  })

  it('handles uppercase extensions', () => {
    expect(getFileExtension('photo.JPG')).toBe('jpg')
    expect(getFileExtension('DOC.PDF')).toBe('pdf')
  })

  it('extracts file extension correctly', () => {
    expect(getFileExtension('path/to/file.md')).toBe('md')
    expect(getFileExtension('file.txt')).toBe('txt')
    expect(getFileExtension(null)).toBe('')
    expect(getFileExtension(undefined)).toBe('')
    expect(getFileExtension('')).toBe('')
    expect(getFileExtension('no-extension')).toBe('')
  })
})

// Test the file URL builder
describe('Resource Detail - File URL Builder', () => {
  function buildFileUrl(filePath: string, mode: 'text' | 'binary'): string {
    const endpoint = mode === 'text' ? '/api/file-content' : '/api/file-serve'
    return `${endpoint}?path=${encodeURIComponent(filePath)}`
  }

  it('builds text file URL correctly', () => {
    const url = buildFileUrl('projects/test/research/output.md', 'text')
    expect(url).toBe('/api/file-content?path=projects%2Ftest%2Fresearch%2Foutput.md')
  })

  it('builds binary file URL correctly', () => {
    const url = buildFileUrl('projects/test/assets/logo.png', 'binary')
    expect(url).toBe('/api/file-serve?path=projects%2Ftest%2Fassets%2Flogo.png')
  })

  it('encodes special characters in path', () => {
    const url = buildFileUrl('projects/my project/file (1).md', 'text')
    expect(url).toContain(encodeURIComponent('projects/my project/file (1).md'))
  })
})

// Test the breadcrumb builder
describe('Resource Detail - Breadcrumb Builder', () => {
  function buildBreadcrumbs(
    slug: string,
    resource: { title: string; campaignId?: string } | null,
    campaign: { name: string; _id: string } | null,
  ) {
    const crumbs = [
      { label: 'Projects', to: '/projects' },
      { label: slug, to: `/projects/${slug}` },
      { label: 'Resources', to: `/projects/${slug}/resources` },
    ]

    if (campaign) {
      crumbs.splice(2, 0, {
        label: campaign.name,
        to: `/projects/${slug}/campaigns/${campaign._id}`,
      })
    }

    if (resource) {
      crumbs.push({ label: resource.title, to: '' })
    }

    return crumbs
  }

  it('builds basic breadcrumbs without campaign', () => {
    const crumbs = buildBreadcrumbs('my-project', { title: 'Research Output' }, null)
    expect(crumbs).toHaveLength(4)
    expect(crumbs[0].label).toBe('Projects')
    expect(crumbs[1].label).toBe('my-project')
    expect(crumbs[2].label).toBe('Resources')
    expect(crumbs[3].label).toBe('Research Output')
  })

  it('includes campaign in breadcrumbs when available', () => {
    const crumbs = buildBreadcrumbs(
      'my-project',
      { title: 'Article Draft', campaignId: 'camp123' },
      { name: 'Summer Campaign', _id: 'camp123' },
    )
    expect(crumbs).toHaveLength(5)
    expect(crumbs[2].label).toBe('Summer Campaign')
    expect(crumbs[2].to).toContain('campaigns/camp123')
    expect(crumbs[3].label).toBe('Resources')
    expect(crumbs[4].label).toBe('Article Draft')
  })

  it('handles null resource gracefully', () => {
    const crumbs = buildBreadcrumbs('my-project', null, null)
    expect(crumbs).toHaveLength(3)
    expect(crumbs[2].label).toBe('Resources')
  })
})

// Test human-readable file size formatter
describe('Resource Detail - File Size Formatter', () => {
  function formatFileSize(bytes: number | undefined | null): string {
    if (!bytes || bytes === 0) return '-'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  }

  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('formats kilobytes', () => {
    expect(formatFileSize(2048)).toBe('2.0 KB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
  })

  it('formats megabytes', () => {
    expect(formatFileSize(1048576)).toBe('1.0 MB')
    expect(formatFileSize(5242880)).toBe('5.0 MB')
  })

  it('formats gigabytes', () => {
    expect(formatFileSize(1073741824)).toBe('1.0 GB')
  })

  it('handles null/undefined/zero', () => {
    expect(formatFileSize(null)).toBe('-')
    expect(formatFileSize(undefined)).toBe('-')
    expect(formatFileSize(0)).toBe('-')
  })
})

// Test the MIME type helper
describe('Resource Detail - MIME Type Detection', () => {
  function getMimeType(ext: string): string {
    const mimeMap: Record<string, string> = {
      md: 'text/markdown',
      txt: 'text/plain',
      csv: 'text/csv',
      html: 'text/html',
      htm: 'text/html',
      json: 'application/json',
      yaml: 'text/yaml',
      yml: 'text/yaml',
      js: 'application/javascript',
      ts: 'application/typescript',
      py: 'text/x-python',
      sh: 'text/x-shellscript',
      vue: 'text/x-vue',
      png: 'image/png',
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      gif: 'image/gif',
      webp: 'image/webp',
      svg: 'image/svg+xml',
      mp4: 'video/mp4',
      webm: 'video/webm',
      mov: 'video/quicktime',
      mp3: 'audio/mpeg',
      wav: 'audio/wav',
      ogg: 'audio/ogg',
      pdf: 'application/pdf',
      docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    return mimeMap[ext] || 'application/octet-stream'
  }

  it('returns correct MIME for common text types', () => {
    expect(getMimeType('md')).toBe('text/markdown')
    expect(getMimeType('txt')).toBe('text/plain')
    expect(getMimeType('html')).toBe('text/html')
  })

  it('returns correct MIME for image types', () => {
    expect(getMimeType('png')).toBe('image/png')
    expect(getMimeType('jpg')).toBe('image/jpeg')
    expect(getMimeType('svg')).toBe('image/svg+xml')
  })

  it('returns correct MIME for media types', () => {
    expect(getMimeType('mp4')).toBe('video/mp4')
    expect(getMimeType('mp3')).toBe('audio/mpeg')
  })

  it('returns octet-stream for unknown types', () => {
    expect(getMimeType('xyz')).toBe('application/octet-stream')
    expect(getMimeType('')).toBe('application/octet-stream')
  })
})

// Test resource content source resolution
describe('Resource Detail - Content Source Resolution', () => {
  interface ResourceData {
    content?: string | null
    filePath?: string | null
    fileUrl?: string | null
  }

  function resolveContentSource(resource: ResourceData): {
    source: 'db' | 'file' | 'url' | 'none'
    value: string
  } {
    if (resource.content) {
      return { source: 'db', value: resource.content }
    }
    if (resource.filePath) {
      return { source: 'file', value: resource.filePath }
    }
    if (resource.fileUrl) {
      return { source: 'url', value: resource.fileUrl }
    }
    return { source: 'none', value: '' }
  }

  it('prioritizes DB content over file path', () => {
    const result = resolveContentSource({
      content: '# Hello',
      filePath: 'some/file.md',
    })
    expect(result.source).toBe('db')
    expect(result.value).toBe('# Hello')
  })

  it('falls back to file path when no content', () => {
    const result = resolveContentSource({
      content: null,
      filePath: 'some/file.md',
    })
    expect(result.source).toBe('file')
    expect(result.value).toBe('some/file.md')
  })

  it('falls back to file URL when no content or path', () => {
    const result = resolveContentSource({
      content: null,
      filePath: null,
      fileUrl: 'https://example.com/file.pdf',
    })
    expect(result.source).toBe('url')
  })

  it('returns none when nothing is available', () => {
    const result = resolveContentSource({})
    expect(result.source).toBe('none')
  })

  it('treats empty string content as no content', () => {
    const result = resolveContentSource({
      content: '',
      filePath: 'some/file.md',
    })
    expect(result.source).toBe('file')
  })
})
