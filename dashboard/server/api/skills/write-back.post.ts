import { defineEventHandler, readBody, createError } from 'h3'
import { readFile, writeFile } from 'fs/promises'
import { join } from 'path'
import { createHash } from 'crypto'
import matter from 'gray-matter'

const PROJECT_ROOT = '/var/www/vibe-marketing'
const CONVEX_URL = process.env.NUXT_PUBLIC_CONVEX_URL || 'http://localhost:3210'

// Fields that map to YAML frontmatter
const FRONTMATTER_FIELDS = ['displayName', 'description', 'tagline', 'category', 'type', 'isAutoActive', 'isCampaignSelectable', 'dashboardDescription'] as const

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

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  if (!body?.skillId || !body?.updatedFields) {
    throw createError({ statusCode: 400, statusMessage: 'skillId and updatedFields required' })
  }

  // Get the skill from Convex to find filePath
  let skill: any
  try {
    const result = await convexRun('skills:get', JSON.stringify({ id: body.skillId }))
    skill = JSON.parse(result)
  } catch (e: any) {
    throw createError({ statusCode: 404, statusMessage: `Skill not found: ${e.message}` })
  }

  if (!skill?.filePath) {
    throw createError({ statusCode: 400, statusMessage: 'Skill has no filePath' })
  }

  const absolutePath = join(PROJECT_ROOT, skill.filePath)

  // Read existing file
  let fileContent: string
  try {
    fileContent = await readFile(absolutePath, 'utf-8')
  } catch (e: any) {
    throw createError({ statusCode: 404, statusMessage: `SKILL.md not found: ${e.message}` })
  }

  // Parse existing frontmatter with gray-matter
  const parsed = matter(fileContent)
  const existingData = parsed.data || {}

  // Merge updated fields into frontmatter
  const updatedFm: Record<string, any> = { ...existingData }
  for (const field of FRONTMATTER_FIELDS) {
    if (body.updatedFields[field] !== undefined) {
      updatedFm[field] = body.updatedFields[field]
    }
  }

  // Rebuild file with updated frontmatter
  const newContent = matter.stringify(parsed.content, updatedFm)

  // Write back
  await writeFile(absolutePath, newContent, 'utf-8')

  // Update Convex record with new hash
  const newHash = createHash('md5').update(newContent).digest('hex')
  try {
    await convexRun('skills:upsertBySlug', JSON.stringify({
      slug: skill.slug,
      name: skill.name,
      displayName: body.updatedFields.displayName || skill.displayName,
      description: body.updatedFields.description || skill.description,
      category: body.updatedFields.category || skill.category,
      type: body.updatedFields.type || skill.type,
      isAutoActive: body.updatedFields.isAutoActive ?? skill.isAutoActive,
      isCampaignSelectable: body.updatedFields.isCampaignSelectable ?? skill.isCampaignSelectable,
      filePath: skill.filePath,
      fileHash: newHash,
      tagline: body.updatedFields.tagline || skill.tagline,
      dashboardDescription: body.updatedFields.dashboardDescription || skill.dashboardDescription,
    }))
  } catch {
    // Non-fatal - sync will catch up
  }

  return { ok: true, filePath: skill.filePath }
})
