/**
 * Utility functions for resource content display.
 * Handles file type detection, content source resolution,
 * URL building, and breadcrumb generation for the resource detail page.
 */

export type ContentDisplayMode =
  | 'markdown'
  | 'plaintext'
  | 'html'
  | 'pdf'
  | 'image'
  | 'video'
  | 'audio'
  | 'office-doc'
  | 'office-sheet'
  | 'office-pres'
  | 'code'
  | 'unsupported'
  | 'empty'

export type ContentSource = 'db' | 'file' | 'url' | 'none'

/**
 * Extract the file extension from a file path (lowercased, without dot).
 */
export function getFileExtension(filePath: string | undefined | null): string {
  if (!filePath) return ''
  const match = filePath.match(/\.(\w+)$/i)
  return match ? match[1].toLowerCase() : ''
}

/**
 * Determine how to display content based on file extension and content availability.
 *
 * Priority:
 * 1. File extension determines display mode
 * 2. If content exists but no recognizable extension, default to markdown
 * 3. If neither content nor file path, return 'empty'
 */
export function getContentDisplayMode(
  filePath: string | undefined | null,
  content: string | undefined | null,
): ContentDisplayMode {
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
  // Unsupported with known extension
  if (ext) return 'unsupported'
  return 'empty'
}

/**
 * Build an API URL to fetch file content.
 * Text files use /api/file-content, binary files use /api/file-serve.
 */
export function buildFileUrl(filePath: string, mode: 'text' | 'binary'): string {
  const endpoint = mode === 'text' ? '/api/file-content' : '/api/file-serve'
  return `${endpoint}?path=${encodeURIComponent(filePath)}`
}

/**
 * Format a file size in bytes to a human-readable string.
 */
export function formatFileSize(bytes: number | undefined | null): string {
  if (!bytes || bytes === 0) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

interface ResourceData {
  content?: string | null
  filePath?: string | null
  fileUrl?: string | null
}

/**
 * Determine where to load content from, with priority:
 * 1. DB content (resource.content)
 * 2. File on disk (resource.filePath)
 * 3. External URL (resource.fileUrl)
 * 4. None
 */
export function resolveContentSource(resource: ResourceData): {
  source: ContentSource
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

interface BreadcrumbItem {
  label: string
  to: string
}

/**
 * Build breadcrumb navigation items for the resource detail page.
 */
export function buildBreadcrumbs(
  slug: string,
  resource: { title: string; campaignId?: string } | null,
  campaign: { name: string; _id: string } | null,
): BreadcrumbItem[] {
  const crumbs: BreadcrumbItem[] = [
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

/**
 * Determine if a file extension indicates a text-based file
 * (that should be fetched via the text endpoint).
 */
export function isTextFile(ext: string): boolean {
  return [
    'md', 'txt', 'csv', 'log', 'html', 'htm',
    'json', 'yaml', 'yml', 'js', 'ts', 'py', 'sh',
    'vue', 'jsx', 'tsx', 'xml', 'css', 'sql',
  ].includes(ext)
}

/**
 * Map of resource types to human-readable labels.
 */
export const typeLabels: Record<string, string> = {
  research_material: 'Research Material',
  brief: 'Brief',
  article: 'Article',
  landing_page: 'Landing Page',
  ad_copy: 'Ad Copy',
  social_post: 'Social Post',
  email_sequence: 'Email Sequence',
  email_excerpt: 'Email Excerpt',
  image_prompt: 'Image Prompt',
  image: 'Image',
  video_script: 'Video Script',
  lead_magnet: 'Lead Magnet',
  report: 'Report',
  brand_asset: 'Brand Asset',
}

/**
 * Status color classes for resource statuses.
 */
export const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  in_review: 'bg-blue-100 text-blue-700',
  reviewed: 'bg-amber-100 text-amber-700',
  humanized: 'bg-teal-100 text-teal-700',
  approved: 'bg-emerald-100 text-emerald-700',
  published: 'bg-green-100 text-green-700',
  archived: 'bg-muted text-muted-foreground',
}
