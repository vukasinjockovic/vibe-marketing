# Implementation Report: Building a StoryBrand 2.0 -- Extraction + Entity + Skill
Generated: 2026-02-10

## Task
Extract material from Donald Miller's "Building a StoryBrand 2.0" (3,963 lines), create structured entity files, and synthesize a comprehensive Claude Code skill for narrative-structure content writing.

## Phase 1: Extraction

**File:** `/var/www/vibe-marketing/ebook-analysis/miller-storybrand/extraction.md` (628 lines)

### What Was Extracted:
- **15 Decision Rules** (DR-01 through DR-15) -- covering hero positioning, survival connection, problem depth, guide traits, plan types, CTA types, stakes calibration, success specificity, grunt test, repetition strategy
- **10 Formulas & Templates** (F-01 through F-10) -- SB7 Framework (complete), BrandScript template, One-Liner formula, Website wireframe (8 sections), Nurture email formula, Sales email formula, Email drip pattern, Testimonial questions, Fear appeal (4-step), Before/After grid
- **10 Principles & Mechanisms** (P-01 through P-10) -- survival mechanism, noise problem, story as sense-making, story gap, if-you-confuse-you-lose, brands-as-hero-fail, loss aversion, cognitive dissonance, messaging-as-memorization, guide archetype
- **11 Anti-Patterns** (AP-01 through AP-11) -- brand as hero, too many words, no clear CTA, missing villain, external-only problems, no stakes, vague success, no plan, Tidal mistake, backstory first, information dump
- **13 Concrete Examples** (E-01 through E-13) -- Spectrum Brands, Kyle Shultz, Nicole Burke, industrial painter, luxury resort, Tidal, Apple, CarMax, MaxStrength, Vitality Aesthetics, Dave Ramsey, Gerber, Calix
- **5 Agent Instructions** (AI-01 through AI-05) -- creating a BrandScript, applying SB7 to landing pages, email sequences, one-liners, ad copy
- **20 Key Quotes** for calibration

## Phase 2: Entity Extraction

### Frameworks (3 files):
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/frameworks/sb7-framework.md`
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/frameworks/brandscript-template.md`
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/frameworks/one-liner-formula.md`

### Concepts (3 files):
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/concepts/guide-vs-hero.md`
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/concepts/the-villain.md`
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/concepts/three-levels-of-problem.md`

### Anecdotes (1 file):
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/anecdotes/client-stories.md`

### People (1 file):
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/people/donald-miller.md`

### Quotes (1 file):
- `/var/www/vibe-marketing/knowledge/nonfiction/building-a-storybrand/_quotes.md` (20+ quotes)

## Phase 3: Skill Synthesis

**File:** `/var/www/vibe-marketing/.claude/skills/mbook-miller-storybrand/SKILL.md` (719 lines)

### Sections:
1. **When Active** -- activation conditions and pre-writing checks
2. **The SB7 Framework** -- all 7 elements with full details, tables, examples, rules + 2 bonus elements (Identity Transformation, Controlling Idea)
3. **The BrandScript** -- complete fill-in template
4. **Decision Rules** -- 12 numbered operational rules (DR-01 through DR-12)
5. **Pre-Writing Checklist** -- 16 checkbox items
6. **Content Type Application** -- 8 content types with templates:
   - Landing page / website (8-section wireframe)
   - Email nurture sequence (pattern + formulas)
   - One-liner (elevator pitch)
   - Digital/social ads
   - Sales conversations / scripts
   - Lead generators (5 types + title formula)
   - Testimonial collection (5 questions)
   - Referral system (4 steps)
7. **Anti-Patterns** -- 14 failure modes with fixes
8. **Writing Rules (Ranked)** -- 7 must-follow, 6 should-follow, 3 nice-to-have
9. **Post-Writing Quality Checks** -- 12 verification items
10. **Key Quotes** -- 15 calibration quotes
11. **Quick-Reference BrandScript Examples** -- Tesla, Nespresso, Edward Jones, House Painting

## Notes
- The skill is the most template-heavy in the collection, matching StoryBrand's highly structured nature
- The BrandScript fill-in template, website wireframe, email formulas, one-liner formula, and testimonial questions are all preserved as operational copy-paste tools
- Every SB7 element includes rules, examples, and tables for quick reference
- The skill follows the format and quality standard of the Schwartz awareness skill (mbook-schwarz-awareness)
