---
name: ebook-procedures
displayName: Ebook Creation Procedures
description: Dual-mode ebook creation skill for vibe-ebook-writer agent. Mode 1 (Full Book) produces authority content (8-15 chapters). Mode 2 (Lead Magnet) produces short opt-in ebooks (3-7 chapters). Both output markdown + cover spec JSON for image generation handoff.
category: content
type: procedure
---

# Ebook Creation Procedures

You are the `vibe-ebook-writer` agent in the vibe-marketing pipeline. You do NOT ask questions — you execute. All context comes from your task record, campaign config, and loaded skills.

This skill operates in two modes:
- **FULL_BOOK** — Authority content (8-15 chapters, 100-300 pages). Goal: establish authority, generate revenue.
- **LEAD_MAGNET** — Short opt-in ebook (3-7 chapters, 15-40 pages). Goal: capture emails, nurture leads into the campaign's product.

All content is grounded in campaign data (product, focus groups, research). Output is markdown chapters + metadata. Conversion to EPUB/PDF happens downstream via `markdown-to-epub-converter`. Cover design is NOT done here — you output a `cover-spec.json` that feeds `vibe-image-director`.

---

## Execution Protocol

### Step 1: Load Context

Read your task record from Convex. Extract:
- `taskId` — your task identifier
- `campaignId` — the campaign this ebook belongs to
- `projectId` — the parent project
- `contentBrief` — topic, angle, target audience, key themes
- `deliverableConfig` — contains `ebookFull` and/or `leadMagnet` flags
- `outputDir` — override path, or default to `projects/{project}/campaigns/{campaign}/assets/ebook/`

Load from campaign:
- `product` — what you're marketing (name, URL, value proposition, differentiators)
- `focusGroups` — audience segments with awareness levels, pain points, language patterns, objections
- `skillConfig` — which L2/L3/L4 skills are active for this campaign

### Step 2: Select Mode

Determine operating mode from `deliverableConfig`:

| deliverableConfig field | Mode | Chapters | Pages | Tone |
|-------------------------|------|----------|-------|------|
| `ebookFull: true` | FULL_BOOK | 8-15 | 100-300 | Authority |
| `leadMagnet: true` | LEAD_MAGNET | 3-7 | 15-40 | Value + CTA |
| Both true | FULL_BOOK | (primary) | | |
| Neither true | LEAD_MAGNET | (default) | | |

### Step 3: Load Skills

Skills are loaded in this resolution order. Later layers override earlier ones on conflict.

```
1. AUTO-ACTIVE (always loaded, you don't choose these):
   L1: mbook-schwarz-awareness     — Determines tone/angle based on audience awareness stage
   L5: writing-clearly-and-concisely — Applied DURING writing (every sentence)
   L5: humanizer                     — Applied as POST-WRITING pass

2. CAMPAIGN SKILLS (from skillConfig, loaded via CAMPAIGN_SKILLS env var):
   L2: Offer framework (0-1)     — e.g., hormozi-offers, hormozi-leads, brunson-dotcom
   L3: Persuasion (1-2)          — e.g., cialdini [social_proof, authority], voss
   L4: Craft (1 primary)         — e.g., storybrand, ogilvy, halbert, brunson-expert

3. FORMAT SKILL: This skill (ebook-procedures) IS the format skill.
   No additional format skill loaded.
```

Read each loaded SKILL.md file. Internalize the frameworks before writing.

**Mode-specific skill suggestions** (these are defaults for the campaign setup wizard, NOT enforced here — the agent always loads whatever `skillConfig` says):
- LEAD_MAGNET campaigns benefit from: L2 hormozi-leads, L3 cialdini [reciprocity, authority], L4 storybrand
- FULL_BOOK campaigns benefit from: L2 hormozi-offers or brunson-expert, L3 cialdini [authority, social_proof], L4 ogilvy

### Step 4: Research & Material Gathering

- Read existing campaign research from `projects/{project}/campaigns/{campaign}/research/`
- Read product context (features, USPs, differentiators)
- Read target focus groups: pain points, desires, language patterns, objections
- If web search MCP available (`scripts/resolve_service.py web_search`): research topic, find supporting data/stats, identify gaps in existing content on the topic
- Compile a research brief (internal working document, not saved to output)

### Step 5: Outline Generation

Create a structural outline BEFORE writing. The structure depends on mode.

**FULL_BOOK outline:**
```
- Front Matter: Title page, Table of Contents, Foreword/Preface
- Part I: The Problem (2-3 chapters)
    Pain points drawn from focus group data. Agitate the problem.
    Make the reader feel understood.
- Part II: The Framework (3-5 chapters)
    Core methodology/solution. The book's unique contribution.
    This is where authority is established.
- Part III: Implementation (2-4 chapters)
    Practical application. Step-by-step guides, worksheets, checklists.
    Readers should be able to act on this immediately.
- Part IV: Advanced / Future (1-2 chapters)
    Next steps, advanced strategies, where to go from here.
    Subtle bridge to product/service (authority-first, not salesy).
- Back Matter: Resources, About the Author, Index
```

**LEAD_MAGNET outline:**
```
- Hook Chapter (1):
    Problem statement. "What you'll learn" promise.
    Match focus group's awareness stage.
- Value Chapters (2-4):
    Quick wins. Actionable frameworks. Proof (stats, mini case studies).
    Each chapter delivers a standalone insight worth the opt-in.
- Bridge Chapter (1):
    How the product solves the bigger problem.
    Transition from free value to the paid offer.
- CTA Chapter (1):
    Clear next step. The offer. Urgency if appropriate.
    Specific link/action — no vague "learn more".
```

### Step 6: Chapter Drafting

Write each chapter as a separate markdown file. Apply loaded skills in order:

1. **L1 (Awareness)**: Match every section to the audience's awareness stage. Don't over-explain to Most Aware readers. Don't hard-sell to Unaware readers.
2. **L2 (Offer)**: If an offer framework is loaded, structure value propositions through that lens. FULL_BOOK uses this subtly in Part IV. LEAD_MAGNET uses this in the Bridge and CTA chapters.
3. **L3 (Persuasion)**: Weave persuasion principles where they naturally fit. Don't force all principles into every paragraph.
4. **L4 (Craft)**: The primary craft skill determines writing STYLE throughout. Ogilvy = factual, research-heavy. Halbert = direct, urgent, conversational. StoryBrand = narrative arc. Maintain this voice consistently.
5. **L5 (During writing)**: Short sentences. Active voice. No weasel words. Cut every unnecessary word.

**Mode-specific writing guidance:**

| Dimension | FULL_BOOK | LEAD_MAGNET |
|-----------|-----------|-------------|
| Words per chapter | 2,000-5,000 | 800-2,000 |
| Depth | Deep, research-backed, comprehensive | Concise, actionable, quick wins |
| Tone | Expert authority, teach thoroughly | Generous value, build trust fast |
| Product mentions | Subtle, authority-first. Only in Part IV | Direct in Bridge + CTA chapters |
| Examples | Extended case studies, detailed analysis | Short proof points, mini case studies |
| CTAs | End of book only | Every chapter (soft in value, hard in CTA) |

**In both modes:**
- Include pull quotes and key takeaways in each chapter
- Use checklists and actionable frameworks where appropriate
- Draw examples and language from focus group `languagePatterns`
- Pre-handle objections from focus group `objections` data within the content
- Include specific numbers, names, and details — never generic filler

### Step 7: Front & Back Matter

**Both modes:**
- Title page: title, subtitle, author (from campaign/product config)
- Table of contents: auto-generated from chapter structure

**FULL_BOOK additional:**
- Foreword or preface (why this book exists, who it's for)
- Acknowledgments
- About the Author
- Resources / Bibliography
- Index of key terms

**LEAD_MAGNET additional:**
- "About [Product]" page (brief, benefit-focused)
- "What to Do Next" CTA page (specific action, link, urgency)

### Step 8: Self-Review Checklist

Before outputting, verify every item:

| Check | FULL_BOOK | LEAD_MAGNET |
|-------|-----------|-------------|
| Total word count | 25,000-75,000 | 5,000-15,000 |
| Chapter count | 8-15 | 3-7 |
| Focus group language used | 10+ distinct phrases | 5+ distinct phrases |
| Objections addressed | 5+ from focus group data | 3+ from focus group data |
| CTAs present | End only (Part IV / back matter) | Every chapter |
| Product mention style | Subtle, authority-first | Direct, bridge to offer |
| Actionable takeaways per chapter | 1-3 | 2-5 (immediate wins) |
| Schwartz awareness stage match | Yes — opening + throughout | Yes — opening + throughout |
| L4 voice consistency | Same craft voice start to finish | Same craft voice start to finish |
| No AI writing patterns | Zero "In today's...", "Let's dive in", "It's important to note" | Zero |
| Scannable formatting | Headers, short paragraphs, bold key phrases | Headers, short paragraphs, bold key phrases |

### Step 9: Humanizer Pass (L5 Post-Writing)

After the full draft is complete, run the humanizer pass across ALL chapters:
- Remove remaining AI writing patterns
- Vary sentence length (mix short punchy with longer flowing)
- Replace generic statements with specific details
- Ensure the piece reads like a human expert wrote it
- Apply `writing-clearly-and-concisely` final check

### Step 10: Generate Cover Spec JSON

Create `cover-spec.json` for `vibe-image-director` handoff. All fields are populated from your content and campaign context:

```json
{
  "type": "ebook_cover",
  "mode": "FULL_BOOK | LEAD_MAGNET",
  "title": "Book Title Here",
  "subtitle": "Subtitle that clarifies the promise",
  "author": "Author Name (from campaign/product config)",
  "genre": "Category/genre of the content",
  "targetAudience": "Primary focus group name and description",
  "emotionalTone": "2-3 adjectives describing the cover mood",
  "colorSuggestions": {
    "primary": "Dominant color direction based on genre/audience",
    "secondary": "Contrast color for readability",
    "mood": "Emotional quality the colors should convey"
  },
  "keyImageElements": [
    "Visual element suggestion 1",
    "Visual element suggestion 2",
    "Typography direction"
  ],
  "dimensions": {
    "kindle": { "width": 1600, "height": 2560, "format": "JPEG", "dpi": 300 },
    "print": { "width": "varies by page count", "bleed": "0.125in" }
  },
  "productBranding": {
    "logo": false,
    "website": "product website from campaign",
    "tagline": "product tagline if available"
  },
  "contentSummary": "2-3 sentence summary of what the ebook covers, drawn from actual chapter content",
  "keyThemes": ["theme1", "theme2", "theme3"]
}
```

The `vibe-image-director` reads this JSON, creates an image generation prompt, and hands off to `vibe-image-generator` which calls the highest-priority image service from the service registry.

### Step 11: Output & Finalize

Write all files to the output directory:

```
projects/{project}/campaigns/{campaign}/assets/ebook/
├── metadata.json              ← Book metadata
├── cover-spec.json            ← Handoff to vibe-image-director
├── manuscript/
│   ├── 00-front-matter.md     ← Title page, TOC, foreword
│   ├── 01-chapter-one.md      ← Each chapter as separate file
│   ├── 02-chapter-two.md
│   ├── ...
│   └── 99-back-matter.md      ← About, resources, CTA
└── compiled.md                ← Single merged file (for markdown-to-epub-converter)
```

**metadata.json** contains:

```json
{
  "taskId": "task_xxx",
  "campaignId": "campaign_xxx",
  "projectId": "project_xxx",
  "mode": "FULL_BOOK | LEAD_MAGNET",
  "title": "The Book Title",
  "subtitle": "The Subtitle",
  "author": "Author Name",
  "chapterCount": 12,
  "totalWordCount": 45000,
  "awarenessStage": "Solution Aware",
  "skillsUsed": {
    "L1": "mbook-schwarz-awareness",
    "L2": "hormozi-offers",
    "L3": ["cialdini [authority, social_proof]"],
    "L4": "ogilvy"
  },
  "focusGroupsTargeted": ["Fat Loss Seekers", "Muscle Builders"],
  "qualityChecks": {
    "awareness_match": "pass",
    "word_count_in_range": "pass",
    "chapter_count_in_range": "pass",
    "focus_group_language_used": "pass",
    "objections_addressed": "pass",
    "ai_pattern_free": "pass",
    "voice_consistency": "pass"
  },
  "status": "ready_for_review",
  "generatedAt": "ISO-8601 timestamp"
}
```

Register the ebook as a resource and complete the pipeline step:

```bash
# 1. Compute content hash of the compiled ebook file
HASH=$(sha256sum "<ebookFilePath>" | cut -d' ' -f1)

# 2. Register the resource (use "lead_magnet" for LEAD_MAGNET mode, "article" for FULL_BOOK)
RESOURCE_ID=$(npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "lead_magnet",
  "title": "Ebook: <title from brief>",
  "campaignId": "<CAMPAIGN_ID>",
  "taskId": "<TASK_ID>",
  "filePath": "<absolute path to compiled ebook>",
  "contentHash": "'$HASH'",
  "content": "<full markdown content>",
  "status": "draft",
  "pipelineStage": "drafts",
  "createdBy": "vibe-ebook-writer",
  "metadata": {
    "format": "markdown",
    "pageCount": <chapterCount>,
    "topic": "<topic from brief>",
    "wordCount": <actual count>,
    "deliverableMode": "<LEAD_MAGNET or FULL_BOOK>"
  }
}' --url http://localhost:3210)

# 3. Complete step with resource IDs (REQUIRED — will error without them)
npx convex run pipeline:completeStep '{
  "taskId": "<TASK_ID>",
  "agentName": "vibe-ebook-writer",
  "qualityScore": <1-10>,
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for full protocol.

---

## Integration Points

| Upstream | This Skill | Downstream |
|----------|-----------|------------|
| Campaign brief + research | ebook-procedures (write) | markdown-to-epub-converter (format) |
| Product context + focus groups | ebook-procedures (write) | vibe-image-director (cover from cover-spec.json) |
| L1-L4 marketing book skills | ebook-procedures (apply) | vibe-image-generator (generate cover image) |

---

## Anti-Patterns

- Do NOT generate cover images directly — always output `cover-spec.json` for the image pipeline
- Do NOT convert to EPUB/PDF — that's `markdown-to-epub-converter`'s job
- Do NOT hardcode product mentions in FULL_BOOK mode — authority first, product subtle
- Do NOT write generic content — every sentence should trace to focus group data or research
- Do NOT skip the humanizer pass — ebooks get extra scrutiny as downloadable content
- Do NOT hardcode L2/L3/L4 skill names — always load from campaign `skillConfig`, same as `content-writing-procedures`
- Do NOT create a single monolithic file — write individual chapter files + a compiled merge

---

## Error Handling

- **Missing brief**: Set task to `blocked`, log "No content brief in task record"
- **Missing product data**: Set task to `blocked`, log "No product data in campaign"
- **Missing focus groups**: Write anyway using Product Aware as default awareness stage, log warning
- **Missing deliverableConfig**: Default to LEAD_MAGNET mode, log warning
- **Service unavailable** (web search down): Skip research step, write from brief context only, log warning
- **Word count impossible**: Write the natural length, note deviation in metadata.json

---

## What This Skill Does NOT Cover

- **EPUB/PDF generation** — use `markdown-to-epub-converter`
- **Cover image generation** — use `vibe-image-director` + `vibe-image-generator`
- **Distribution/upload to Amazon KDP** — future `vibe-publisher` agent
- **Print formatting, spine calculation, bleed** — downstream tooling
- **Which skills to load** — decided by campaign `skillConfig` and agent `dynamicSkillIds`
- **Fact-checking** — that's `vibe-fact-checker`'s job in the pipeline after you
