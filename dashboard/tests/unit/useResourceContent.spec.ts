import { describe, it, expect } from 'vitest'
import {
  getFileExtension,
  getContentDisplayMode,
  buildFileUrl,
  formatFileSize,
  resolveContentSource,
  buildBreadcrumbs,
} from '../../composables/useResourceContent'

describe('useResourceContent - getFileExtension', () => {
  it('extracts extension from file path', () => {
    expect(getFileExtension('path/to/file.md')).toBe('md')
    expect(getFileExtension('file.txt')).toBe('txt')
  })

  it('handles uppercase extensions', () => {
    expect(getFileExtension('photo.JPG')).toBe('jpg')
  })

  it('handles null/undefined/empty', () => {
    expect(getFileExtension(null)).toBe('')
    expect(getFileExtension(undefined)).toBe('')
    expect(getFileExtension('')).toBe('')
  })

  it('handles file paths with multiple dots', () => {
    expect(getFileExtension('file.name.with.dots.md')).toBe('md')
  })

  it('handles file paths without extension', () => {
    expect(getFileExtension('no-extension')).toBe('')
  })
})

describe('useResourceContent - getContentDisplayMode', () => {
  it('detects markdown files', () => {
    expect(getContentDisplayMode('research/output.md', null)).toBe('markdown')
  })

  it('detects plain text files', () => {
    expect(getContentDisplayMode('data/export.txt', null)).toBe('plaintext')
    expect(getContentDisplayMode('data/report.csv', null)).toBe('plaintext')
  })

  it('detects HTML files', () => {
    expect(getContentDisplayMode('pages/landing.html', null)).toBe('html')
  })

  it('detects PDF files', () => {
    expect(getContentDisplayMode('docs/guide.pdf', null)).toBe('pdf')
  })

  it('detects image files', () => {
    expect(getContentDisplayMode('assets/logo.png', null)).toBe('image')
    expect(getContentDisplayMode('assets/photo.jpg', null)).toBe('image')
    expect(getContentDisplayMode('assets/hero.webp', null)).toBe('image')
    expect(getContentDisplayMode('assets/icon.svg', null)).toBe('image')
  })

  it('detects video files', () => {
    expect(getContentDisplayMode('media/promo.mp4', null)).toBe('video')
    expect(getContentDisplayMode('media/clip.webm', null)).toBe('video')
  })

  it('detects audio files', () => {
    expect(getContentDisplayMode('audio/podcast.mp3', null)).toBe('audio')
    expect(getContentDisplayMode('audio/sample.wav', null)).toBe('audio')
  })

  it('detects Office documents', () => {
    expect(getContentDisplayMode('docs/report.docx', null)).toBe('office-doc')
    expect(getContentDisplayMode('data/analysis.xlsx', null)).toBe('office-sheet')
  })

  it('detects code files', () => {
    expect(getContentDisplayMode('scripts/build.js', null)).toBe('code')
    expect(getContentDisplayMode('config.json', null)).toBe('code')
  })

  it('falls back to markdown when content exists but no file path', () => {
    expect(getContentDisplayMode(null, '# Hello World')).toBe('markdown')
  })

  it('returns empty when no file path and no content', () => {
    expect(getContentDisplayMode(null, null)).toBe('empty')
  })

  it('returns unsupported for unknown extensions without content', () => {
    expect(getContentDisplayMode('file.xyz', null)).toBe('unsupported')
  })
})

describe('useResourceContent - buildFileUrl', () => {
  it('builds text file URL correctly', () => {
    const url = buildFileUrl('projects/test/output.md', 'text')
    expect(url).toBe('/api/file-content?path=projects%2Ftest%2Foutput.md')
  })

  it('builds binary file URL correctly', () => {
    const url = buildFileUrl('projects/test/logo.png', 'binary')
    expect(url).toBe('/api/file-serve?path=projects%2Ftest%2Flogo.png')
  })
})

describe('useResourceContent - formatFileSize', () => {
  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('formats kilobytes', () => {
    expect(formatFileSize(2048)).toBe('2.0 KB')
  })

  it('formats megabytes', () => {
    expect(formatFileSize(1048576)).toBe('1.0 MB')
  })

  it('handles null/undefined/zero', () => {
    expect(formatFileSize(null)).toBe('-')
    expect(formatFileSize(undefined)).toBe('-')
    expect(formatFileSize(0)).toBe('-')
  })
})

describe('useResourceContent - resolveContentSource', () => {
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
  })

  it('returns none when nothing available', () => {
    const result = resolveContentSource({})
    expect(result.source).toBe('none')
  })
})

describe('useResourceContent - buildBreadcrumbs', () => {
  it('builds basic breadcrumbs', () => {
    const crumbs = buildBreadcrumbs('my-project', { title: 'Research' }, null)
    expect(crumbs).toHaveLength(4)
    expect(crumbs[0].label).toBe('Projects')
    expect(crumbs[3].label).toBe('Research')
  })

  it('includes campaign when available', () => {
    const crumbs = buildBreadcrumbs(
      'my-project',
      { title: 'Article', campaignId: 'c1' },
      { name: 'Campaign A', _id: 'c1' },
    )
    expect(crumbs).toHaveLength(5)
    expect(crumbs[2].label).toBe('Campaign A')
  })
})
