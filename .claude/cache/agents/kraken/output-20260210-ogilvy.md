# Implementation Report: Ogilvy on Advertising -- Full Extraction + Entity + Skill Synthesis
Generated: 2026-02-10

## Task
Complete three-phase extraction from David Ogilvy's "Ogilvy on Advertising" (10,008 lines):
1. Concept extraction to extraction.md
2. Entity extraction to knowledge base
3. Skill synthesis to SKILL.md

## Phase 1: Extraction (extraction.md)

**File:** `/var/www/vibe-marketing/ebook-analysis/ogilvy-on-advertising/extraction.md`
**Lines:** 538

### Contents
- 50 Decision Rules (DR-01 through DR-50) covering homework, headlines, body copy, illustrations, layout, typography, TV, and strategy
- 7 Formulas & Templates (Rolls-Royce formula, two Ogilvy layouts, editorial-format, positively good, direct response TV, long copy typography boosters, direct mail testing hierarchy)
- 12 Principles & Mechanisms (5x headline rule, brand image theory, Big Idea, research-first, salesmanship in print, moving parade, consumer is not a moron, promise/large promise, story appeal, advertising as production cost, repertory of brands, heavy users)
- 20 Anti-Patterns (creativity without sales, irrelevant sex, committees, intuition over knowledge, reverse type, all caps, ignoring captions, too many objectives, changing ads too soon, promotions over advertising, celebrity testimonials, cartoons for adults, musical vignettes, naming competitors, background music, scene changes, artdirectoritis, fatuous slogans, initials, jingles)
- 12 Concrete Examples (Rolls-Royce, Hathaway, Schweppes, Dove, VW, Avis, Marlboro, Merrill Lynch, Puerto Rico, Shell, Pepperidge Farm, Mercedes-Benz)
- 6 Agent Instructions (pre-writing research, headline writing, body copy writing, layout/design, TV commercial, quality checklist)

## Phase 2: Entity Extraction (Knowledge Base)

**Directory:** `/var/www/vibe-marketing/knowledge/nonfiction/ogilvy-on-advertising/`
**Total entities:** 25 files

### Frameworks (5)
- `frameworks/big-idea.md` -- The Big Idea and five-question validation test
- `frameworks/brand-image-theory.md` -- Brand image as product personality
- `frameworks/editorial-layout.md` -- Editorial-format ad layout system
- `frameworks/positioning.md` -- "What the product does, and who it is for"
- `frameworks/research-first-approach.md` -- Six-step homework workflow

### Concepts (5)
- `concepts/long-copy-typography.md` -- Specific typography techniques with percentages
- `concepts/moving-parade.md` -- Why good ads should repeat, not be replaced
- `concepts/salesmanship-in-print.md` -- Foundational definition of advertising
- `concepts/scientific-advertising.md` -- Hopkins' empirical tradition
- `concepts/story-appeal.md` -- Rudolph's curiosity-photography research

### Anecdotes (7)
- `anecdotes/rolls-royce-ad.md` -- "At 60 miles an hour" factual long-copy exemplar
- `anecdotes/hathaway-eyepatch.md` -- Story appeal in action, 30+ year campaign
- `anecdotes/dove-campaign.md` -- Positioning power, 25+ year campaign
- `anecdotes/volkswagen-campaign.md` -- Cultural positioning by Bernbach/DDB
- `anecdotes/marlboro-cowboy.md` -- Brand image power, 25+ year campaign
- `anecdotes/mercedes-benz-campaign.md` -- Factual approach, 10K to 40K cars/year
- `anecdotes/puerto-rico-campaign.md` -- Long copy for economic development

### People (7)
- `people/ogilvy-david.md` -- Author entity
- `people/lasker-albert.md` -- Lord & Thomas, "salesmanship in print"
- `people/hopkins-claude.md` -- Scientific Advertising, test marketing inventor
- `people/bernbach-bill.md` -- DDB, VW/Avis campaigns, originality champion
- `people/burnett-leo.md` -- Chicago school, Marlboro cowboy
- `people/rubicam-raymond.md` -- Y&R, research + creativity, Ogilvy's hero
- `people/resor-stanley.md` -- JWT, consensus management, research pioneer

### Quotes (1)
- `_ogilvy-on-advertising-quotes.md` -- 30+ quotes organized by theme

## Phase 3: Skill Synthesis (SKILL.md)

**File:** `/var/www/vibe-marketing/.claude/skills/mbook-ogilvy-advertising/SKILL.md`
**Lines:** 581 (within 500-700 target range)

### Sections
1. When This Skill Is Active (on-demand triggers)
2. Core Philosophy (5 foundational truths with exact quotes)
3. The Big Idea (5-question test, process for finding ideas)
4. Headline Rules (8 decision rules + anti-pattern table)
5. Body Copy Rules (opening, tone/style, content, structure -- 15 decision rules)
6. Visual and Layout Rules (layout order, editorial format, illustration rules, typography anti-patterns)
7. Direct Response Principles (key rules, testing hierarchy)
8. Pre-Writing Checklist (6 steps, all checkboxes)
9. Decision Rules Summary (4 tables: Strategy, Headline, Copy, Visual/Layout, TV -- 33 total rules)
10. Anti-Patterns (17-row table)
11. Writing Rules Ranked (7 must-follow, 6 should-follow, 5 nice-to-have)
12. Post-Writing Quality Checks (14 verification items)
13. Ogilvy's Factual Long-Copy Formula (structure + typography)
14. The Parity Product Formula
15. Key Statistics Reference (15 statistics with citations)
16. Key Quotes (13 foundational quotes)

### Statistics Preserved
All specific percentages and numbers from the book are preserved in the skill:
- 5x headline readers vs body copy readers
- 4x more readers for benefit headlines
- 80% never read body copy
- 22% more recall for news headlines
- 28% more recall for quoted headlines
- 13% more readership with drop-initials
- 12% more readership with leading
- 10% more readers for headlines below illustrations
- 20% below average for blind headlines
- 6x more article readers than ad readers
- 4x more caption readers than body copy readers
- 100% more memorable for 4-color
- 32% of beer-drinkers drink 80% of beer
- 1 in 100 campaigns contains a Big Idea

## Notes
- The skill follows the reference format from mbook-schwarz-awareness/SKILL.md
- YAML frontmatter uses layer: 4 (advertising-craft), type: advertising-craft, mode: on-demand
- Every decision rule includes exact Ogilvy quotes as evidence
- The skill is operational: an AI agent reading it can execute every rule without ambiguity
