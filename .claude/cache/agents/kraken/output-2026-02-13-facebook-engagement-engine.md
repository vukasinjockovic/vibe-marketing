# Implementation Report: facebook-engagement-engine SKILL.md
Generated: 2026-02-13

## Task
Create a composite engagement agent skill at `/var/www/vibe-marketing/.claude/skills/facebook-engagement-engine/SKILL.md` that embeds knowledge from 5 sources to generate maximum-engagement Facebook posts.

## Sources Read

### FB Monetization (platform mechanics):
- `knowledge/nonfiction/facebook-monetization/00-overview.md`
- `knowledge/nonfiction/facebook-monetization/03-content-strategy.md`
- `knowledge/nonfiction/facebook-monetization/04-posting-schedule.md`
- `knowledge/nonfiction/facebook-monetization/06-growth-playbook.md`
- `knowledge/nonfiction/facebook-monetization/10-compliance.md`

### Berger/STEPPS (virality principles):
- `knowledge/nonfiction/berger-contagious/00-overview.md`
- `knowledge/nonfiction/berger-contagious/01-social-currency.md`
- `knowledge/nonfiction/berger-contagious/02-triggers.md`
- `knowledge/nonfiction/berger-contagious/03-emotion.md`
- `knowledge/nonfiction/berger-contagious/05-practical-value.md`
- `knowledge/nonfiction/berger-contagious/06-stories.md`
- `knowledge/nonfiction/berger-contagious/07-application-matrix.md`

### Voss (conversation engine):
- `ebook-analysis/voss-never-split/extraction.md` (703 lines, full extraction)

### Hook craft:
- `.claude/skills/mbook-sugarman-copywriting/SKILL.md` -- extracted: Slippery Slide, first-sentence craft, curiosity seeds
- `.claude/skills/mbook-ogilvy-advertising/SKILL.md` -- extracted: specificity, numbers, curiosity gaps
- `.claude/skills/mbook-halbert-boron/SKILL.md` -- extracted: mid-action openers, "They laughed when...", conditional hooks

## File Created
- `/var/www/vibe-marketing/.claude/skills/facebook-engagement-engine/SKILL.md` -- 800 lines

## Skill Structure (7 Sections)

### Section 1: Agent Identity
- Name, agent, goal, tone, format, image size
- Explicit DO/DO NOT lists -- no selling, no links, no products

### Section 2: The Engagement Stack (4 layers)
- **Layer A -- Platform Mechanics:** 11 content formats ranked, algorithm rules, posting schedule (half-past trick), content mix ratios (30/25/20/15/10), repost strategy, compliance guardrails
- **Layer B -- Virality Engine (STEPPS):** All 6 principles as operational checklist with action items, scoring template (0-5 per principle, /30 total), minimum thresholds (16+ to ship, 3+ principles at 3+), red flags table
- **Layer C -- Conversation Engine (Voss):** 6 techniques adapted for engagement -- Tactical Empathy, Labeling, Mirroring, Calibrated Questions, Late-Night FM DJ Voice, "That's Right" moments. Each has templates, rules, and engagement mechanism explanation.
- **Layer D -- Hook Craft:** Slippery Slide (Sugarman), Specificity (Ogilvy), Mid-Action Openers (Halbert), Story-Opening Formulas. ONLY attention/curiosity mechanics -- all sales psychology stripped.

### Section 3: Post Generation Framework
- Structured output format for every post: format, target audience, STEPPS score, primary hook, Voss technique, time slot, engagement goal, copy, image brief, "why this works"

### Section 4: Content Format Templates (10 formats)
1. Question posts (calibrated questions)
2. Emotional story posts (tactical empathy + awe)
3. Interactive posts (pick one, this or that)
4. Debate posts (controlled controversy)
5. Nostalgia posts (triggers + emotion)
6. Photo caption posts (image-first)
7. Fill-in-the-blank posts
8. Tag someone posts (social currency + public)
9. Unpopular opinion posts
10. Story time posts (Trojan Horse narratives)

### Section 5: Quality Gates (7 gates)
1. Sales Check -- reject if any selling detected
2. STEPPS Check -- 16+ score, 3+ principles at 3+
3. Hook Check -- first line must stop the scroll
4. Emotion Check -- must be high-arousal
5. Link Check -- no external links
6. Length Check -- appropriate for format
7. Human Check -- must sound like a real person

### Section 6: Research Integration
- Table mapping 5 research sources to post generation actions

### Section 7: Batch Generation Rules
- Content mix enforcement with exact counts per batch size
- Variety rules (no consecutive same-format/hook/segment)
- Focus group distribution
- Time slot assignment with A-post flagging
- Repost candidate marking
- Batch output header template

## Design Decisions
1. **No sales psychology leakage:** Verified via grep -- all mentions of urgency/scarcity/offers/CTAs are in "DO NOT" context only
2. **Stripped from hook craft:** Sugarman's urgency/fear triggers, Ogilvy's sales closing, Halbert's offer construction -- all removed. Only attention/curiosity mechanics retained.
3. **Operational, not reference:** Every embedded principle ties to a specific post-generation action
4. **Self-contained:** Agent does not need to invoke any other skills during generation
5. **Exactly 800 lines:** Dense and actionable, not verbose

## Notes
- Voss knowledge files were in `ebook-analysis/voss-never-split/extraction.md` (not in `knowledge/nonfiction/` -- entity files not yet created for Voss)
- The skill is already indexed and appearing in the skill registry
