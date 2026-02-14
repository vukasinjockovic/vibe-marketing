import { marked } from 'marked'
import DOMPurify from 'dompurify'

interface ParsedMarkdown {
  frontmatter: Record<string, any> | null
  html: string
  rawContent: string
}

/**
 * Strip YAML frontmatter from markdown content.
 * Returns parsed frontmatter object and remaining content.
 */
function stripFrontmatter(content: string): { frontmatter: Record<string, any> | null; body: string } {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/)
  if (!match) return { frontmatter: null, body: content }

  const yamlBlock = match[1]
  const body = match[2]

  // Simple YAML key-value parser (handles flat key: value pairs)
  const frontmatter: Record<string, any> = {}
  for (const line of yamlBlock.split('\n')) {
    const kv = line.match(/^(\w[\w-]*)\s*:\s*(.*)$/)
    if (kv) {
      const key = kv[1]
      let value: any = kv[2].trim()
      // Handle arrays (simple inline [a, b, c])
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map((s: string) => s.trim().replace(/^["']|["']$/g, ''))
      }
      // Handle numbers
      else if (/^\d+(\.\d+)?$/.test(value)) {
        value = parseFloat(value)
      }
      // Handle booleans
      else if (value === 'true') value = true
      else if (value === 'false') value = false
      // Strip quotes
      else value = value.replace(/^["']|["']$/g, '')

      frontmatter[key] = value
    }
  }

  return { frontmatter: Object.keys(frontmatter).length > 0 ? frontmatter : null, body }
}

export function useMarkdown() {
  function parse(content: string | undefined | null): ParsedMarkdown {
    if (!content) return { frontmatter: null, html: '', rawContent: '' }

    const { frontmatter, body } = stripFrontmatter(content)
    const rawHtml = marked.parse(body, { async: false }) as string
    const html = DOMPurify.sanitize(rawHtml)

    return { frontmatter, html, rawContent: body }
  }

  return { parse }
}
