import { defineEventHandler, createError } from 'h3'
import { readdir, readFile, stat } from 'fs/promises'
import { join, resolve } from 'path'
import { createHash } from 'crypto'
import matter from 'gray-matter'

const PROJECT_ROOT = '/var/www/vibe-marketing'
const SKILLS_DIR = join(PROJECT_ROOT, '.claude/skills')
const CONFIG_PATH = join(PROJECT_ROOT, 'scripts/sync-skills-config.json')
const CONVEX_URL = process.env.NUXT_PUBLIC_CONVEX_URL || 'http://localhost:3210'

// Layer mapping from frontmatter metadata
const LAYER_TO_CATEGORY: Record<string, string> = {
  L1: 'L1_audience',
  L2: 'L2_offer',
  L3: 'L3_persuasion',
  L4: 'L4_craft',
  L5: 'L5_quality',
}

// Category detection patterns for skills without standard frontmatter
const CATEGORY_PATTERNS: [RegExp, string][] = [
  [/^mbook-schwarz/, 'L1_audience'],
  [/^mbook-hormozi-(offers|leads)/, 'L2_offer'],
  [/^mbook-brunson/, 'L2_offer'],
  [/^mbook-cialdini|^mbook-voss|^mbook-miller/, 'L3_persuasion'],
  [/^mbook-halbert|^mbook-sugarman|^mbook-ogilvy/, 'L4_craft'],
  [/^(writing-clearly|humanizer)/, 'L5_quality'],
  [/^(audience|focus-group|discovery)/, 'research'],
  [/^(content-|social-|email-|video-script|copywriting|copy-editing)/, 'content'],
  [/^(image-|media-|presentation)/, 'media'],
  [/^(page-cro|signup|onboarding|form-cro|popup|paywall|pricing|referral|ab-test|analytics|seo-|schema-markup|programmatic|paid-ads|launch|free-tool|competitor|marketing-)/, 'marketing'],
  [/^(claim-investigation|content-strategy|product-marketing)/, 'marketing'],
  [/^(ebook-|non-fiction)/, 'content'],
]

function matchCategory(slug: string): string {
  for (const [pattern, category] of CATEGORY_PATTERNS) {
    if (pattern.test(slug)) return category
  }
  return 'content' // default
}

function matchesExclude(slug: string, patterns: string[]): boolean {
  for (const pattern of patterns) {
    if (pattern.endsWith('*')) {
      if (slug.startsWith(pattern.slice(0, -1))) return true
    } else if (slug === pattern) {
      return true
    }
  }
  return false
}

interface FrontmatterData {
  name?: string
  displayName?: string
  description?: string
  tagline?: string
  dashboardDescription?: string
  category?: string
  type?: string
  isAutoActive?: boolean
  isCampaignSelectable?: boolean
  subSelections?: { key: string; label: string; description?: string }[]
  metadata?: { layer?: string; mode?: string }
}

function detectType(slug: string): 'mbook' | 'procedure' | 'community' | 'custom' {
  if (slug.startsWith('mbook-')) return 'mbook'
  if (slug.endsWith('-procedures')) return 'procedure'
  return 'custom'
}

async function convexRun(fn: string, args: string): Promise<string> {
  const { execSync } = await import('child_process')
  const { writeFileSync, unlinkSync } = await import('fs')
  const tmpFile = join('/tmp', `convex-args-${Date.now()}-${Math.random().toString(36).slice(2)}.json`)
  writeFileSync(tmpFile, args)
  try {
    return execSync(`npx convex run ${fn} "$(cat ${tmpFile})" --url ${CONVEX_URL}`, {
      cwd: PROJECT_ROOT,
      timeout: 30000,
      encoding: 'utf-8',
    })
  } finally {
    try { unlinkSync(tmpFile) } catch {}
  }
}

export default defineEventHandler(async () => {
  let config: { excludePatterns: string[] }
  try {
    const raw = await readFile(CONFIG_PATH, 'utf-8')
    config = JSON.parse(raw)
  } catch {
    config = { excludePatterns: [] }
  }

  // Read all skill directories (including symlinks)
  let dirs: string[]
  try {
    const entries = await readdir(SKILLS_DIR, { withFileTypes: true })
    dirs = entries.filter((e) => e.isDirectory() || e.isSymbolicLink()).map((e) => e.name)
  } catch (e: any) {
    throw createError({ statusCode: 500, statusMessage: `Cannot read skills dir: ${e.message}` })
  }

  // Get existing skills from Convex
  let existingSkills: any[]
  try {
    const result = await convexRun('skills:list', '{}')
    existingSkills = JSON.parse(result)
  } catch {
    existingSkills = []
  }

  const existingBySlug = new Map(existingSkills.map((s: any) => [s.slug, s]))
  const syncedSlugs = new Set<string>()

  let synced = 0
  let unchanged = 0
  let skipped = 0
  let missing = 0
  const errors: string[] = []

  for (const dir of dirs) {
    // Check exclude patterns
    if (matchesExclude(dir, config.excludePatterns)) {
      skipped++
      continue
    }

    const skillMdPath = join(SKILLS_DIR, dir, 'SKILL.md')
    let content: string
    try {
      content = await readFile(skillMdPath, 'utf-8')
    } catch {
      // No SKILL.md - skip
      skipped++
      continue
    }

    const slug = dir
    syncedSlugs.add(slug)

    // Compute hash
    const hash = createHash('md5').update(content).digest('hex')

    // Check if unchanged
    const existing = existingBySlug.get(slug)
    if (existing && existing.fileHash === hash) {
      unchanged++
      continue
    }

    // Parse frontmatter
    const { data: fm, content: body } = matter(content) as { data: FrontmatterData; content: string }

    // Determine category
    let category = fm.category || ''
    if (!category && fm.metadata?.layer) {
      category = LAYER_TO_CATEGORY[fm.metadata.layer] || ''
    }
    if (!category) {
      category = matchCategory(slug)
    }

    // Build description from frontmatter or first paragraph
    const description = fm.description ||
      body.split('\n').find((l) => l.trim() && !l.startsWith('#'))?.trim() ||
      `Skill: ${slug}`

    const displayName = fm.displayName || fm.name ||
      slug.split('-').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')

    const isAutoActive = fm.isAutoActive ?? fm.metadata?.mode === 'auto-active' ?? false
    const isCampaignSelectable = fm.isCampaignSelectable ?? !isAutoActive

    const upsertArgs = JSON.stringify({
      slug,
      name: slug,
      displayName,
      description,
      category,
      type: fm.type || detectType(slug),
      isAutoActive,
      isCampaignSelectable,
      filePath: `.claude/skills/${slug}/SKILL.md`,
      fileHash: hash,
      tagline: fm.tagline || undefined,
      dashboardDescription: fm.dashboardDescription || undefined,
      subSelections: fm.subSelections || undefined,
    })

    try {
      await convexRun('skills:upsertBySlug', upsertArgs)
      synced++
    } catch (e: any) {
      errors.push(`${slug}: ${e.message?.slice(0, 100)}`)
    }
  }

  // Mark missing skills (in Convex but no longer on filesystem)
  for (const [slug, skill] of existingBySlug) {
    if (!syncedSlugs.has(slug) && !matchesExclude(slug, config.excludePatterns)) {
      // Check if file actually exists
      try {
        await stat(join(SKILLS_DIR, slug, 'SKILL.md'))
      } catch {
        // File doesn't exist - mark as missing
        if (skill.syncStatus !== 'file_missing') {
          try {
            await convexRun('skills:markMissing', JSON.stringify({ id: skill._id }))
            missing++
          } catch (e: any) {
            errors.push(`markMissing ${slug}: ${e.message?.slice(0, 100)}`)
          }
        }
      }
    }
  }

  return {
    synced,
    unchanged,
    skipped,
    missing,
    total: dirs.length,
    errors,
  }
})
