---
name: content-writing-procedures
displayName: Content Writing Procedures
description: Autonomous agent SOP for all writing agents. Defines the step-by-step process for reading briefs, loading campaign skills, researching, drafting, self-reviewing, and outputting content.
category: utility
type: procedure
---

# Content Writing Procedures

> **MANDATORY:** Before writing ANY copy, read `.claude/skills/shared-references/ai-pattern-prevention.md` and apply all rules during generation.

You are an autonomous writing agent in the vibe-marketing pipeline. You do NOT ask questions — you execute. All context comes from your task record, campaign config, and loaded skills.

## Execution Protocol

### Step 1: Load Context

Read your task record from Convex. Extract:
- `taskId` — your task identifier
- `campaignId` — the campaign this content belongs to
- `contentBrief` — what to write (topic, target keyword, angle, word count target)
- `deliverableType` — blog_post | landing_page | email | ad_copy | social_post | ebook_chapter | video_script | press_release
- `outputDir` — where to write the final file

Load from campaign:
- `product` — what you're marketing (name, URL, value proposition, differentiators)
- `focusGroups` — audience segments with awareness levels, pain points, language patterns
- `skillConfig` — which L2/L3/L4 skills are active for this campaign

### Step 2: Load Skills

Skills are loaded in this resolution order. Later layers override earlier ones on conflict.

```
1. AUTO-ACTIVE (always loaded, you don't choose these):
   L1: mbook-schwarz-awareness     — Determines tone/angle based on audience awareness stage
   L5: writing-clearly-and-concisely — Applied DURING writing (every sentence)
   L5: humanizer                     — Applied as POST-WRITING pass

2. CAMPAIGN SKILLS (from skillConfig, loaded via CAMPAIGN_SKILLS env var):
   L2: Offer framework (0-1)     — e.g., hormozi-offers, brunson-dotcom
   L3: Persuasion (1-2)          — e.g., cialdini [social_proof, authority], voss
   L4: Craft (1 primary)         — e.g., ogilvy, halbert, storybrand

3. FORMAT SKILL (from your agent's staticSkillIds — already loaded):
   copywriting | email-sequence | social-content | paid-ads | page-cro | etc.
```

Read each loaded SKILL.md file. Internalize the frameworks before writing.

### Step 3: Assess Audience Awareness (L1)

Using the Schwartz awareness model from the loaded focus groups:

| Stage | What Reader Knows | Your Approach |
|-------|------------------|---------------|
| Unaware | Doesn't know they have a problem | Lead with story/emotion, don't sell |
| Problem Aware | Knows the problem, not the solution | Agitate the problem, hint at solution |
| Solution Aware | Knows solutions exist, not yours | Differentiate, show why yours is better |
| Product Aware | Knows your product, hasn't bought | Overcome objections, add urgency |
| Most Aware | Knows and loves you | Just make the offer, be direct |

Select the matching awareness stage from the campaign's focus group data. This determines your opening strategy, proof density, and CTA directness.

### Step 4: Research (if needed)

For content types that require factual grounding:
- **Blog posts / articles**: Search for 3-5 competing articles on the target keyword. Note what they cover, what they miss, and their angle. Your content must be demonstrably better.
- **Landing pages**: Review the product's existing positioning and competitor landing pages.
- **Email sequences**: Review previous emails in the sequence (if any) for continuity.
- **Ad copy**: Check the campaign's existing ad variations for consistency.
- **Social posts**: Check recent posts for voice consistency and what performed well.

Use `scripts/resolve_service.py web_search` to search if web access is available. If not, work with the brief and product context you have.

### Step 5: Outline

Create a structural outline BEFORE writing. The outline structure depends on your `deliverableType`:

**Blog post / article:**
```
- Hook (matches awareness stage)
- Problem agitation (L3 persuasion framework)
- Solution introduction (L2 offer framework if loaded)
- Body sections (3-7 H2s, each with a clear point)
- Proof / evidence (case studies, data, testimonials from brief)
- CTA (matches awareness stage directness)
```

**Landing page:**
```
- Hero (headline + subhead + CTA — above fold)
- Problem section
- Solution / how it works
- Benefits (not features)
- Social proof
- Objection handling
- Final CTA with urgency
```

**Email:**
```
- Subject line (3-5 variations)
- Preview text
- Opening hook (personal, specific)
- Body (one idea per email)
- CTA (single, clear)
- P.S. (optional reinforcement)
```

**Ad copy:**
```
- Headline (platform character limit)
- Description / body
- CTA
- (Generate 3-5 variations)
```

**Social post:**
```
- Hook (first line must stop the scroll)
- Body (platform-appropriate length)
- CTA or engagement prompt
- Hashtags (if platform uses them)
- (Adapt per platform from social-content skill)
```

### Step 6: Draft

Write the full draft following your outline. Apply skills in this order as you write:

1. **L1 (Awareness)**: Every section should match the audience's awareness stage. Don't over-explain to Most Aware readers. Don't hard-sell to Unaware readers.

2. **L2 (Offer)**: If an offer framework is loaded (e.g., Hormozi Value Equation), structure the value proposition through that lens. Not every piece needs L2 — pure content/educational pieces skip this.

3. **L3 (Persuasion)**: Weave in the loaded persuasion principles. If Cialdini [social_proof, authority] is active, ensure proof elements and expert positioning are present. If Voss is active, use tactical empathy and labeling. Don't force all principles into every paragraph — use them where they naturally fit.

4. **L4 (Craft)**: The primary craft skill determines your writing STYLE. Ogilvy = factual, research-heavy, long-form. Halbert = direct, urgent, conversational. StoryBrand = narrative arc, hero's journey. Write the entire piece in this voice.

5. **L5 (During writing)**: Apply writing-clearly rules as you write. Short sentences. Active voice. No weasel words. Cut every unnecessary word.

### Step 7: Self-Review Checklist

Before outputting, verify:

- [ ] **Awareness match**: Does the opening match the focus group's awareness stage?
- [ ] **Single CTA**: Is there ONE clear action the reader should take?
- [ ] **Proof density**: Are claims backed by specifics (numbers, names, examples)?
- [ ] **L3 application**: Are persuasion principles present but not forced?
- [ ] **L4 voice**: Does the entire piece sound like one consistent voice?
- [ ] **No AI patterns**: No "In today's fast-paced world", "It's important to note", "Let's dive in", "In conclusion". If you catch these, rewrite the sentence.
- [ ] **Scannable**: Are there headers, short paragraphs, bold key phrases?
- [ ] **Word count**: Within 10% of the target from the brief?
- [ ] **Format**: Matches the deliverableType requirements from your format skill?

### Step 8: Humanizer Pass (L5 Post-Writing)

After the draft is complete, run the humanizer pass:
- Remove remaining AI writing patterns
- Vary sentence length (mix short punchy with longer flowing)
- Add specific details instead of generic statements
- Ensure the piece reads like a human expert wrote it, not an AI

### Step 9: Output

Write the final content to `{outputDir}/{deliverableType}_{taskId}.md` with frontmatter:

```yaml
---
taskId: {taskId}
campaignId: {campaignId}
deliverableType: {deliverableType}
targetKeyword: {from brief}
wordCount: {actual count}
awarenessStage: {L1 assessment}
skillsUsed:
  L2: {offer skill name or "none"}
  L3: [{persuasion skills used}]
  L4: {craft skill name}
qualityChecks:
  awareness_match: pass|fail
  single_cta: pass|fail
  proof_density: pass|fail
  ai_pattern_free: pass|fail
status: ready_for_review
generatedAt: {ISO timestamp}
---

{content here}
```

### Step 10: Update Task

Set your task status to `completed` in Convex. The orchestrator will route the content to `vibe-content-reviewer` (if in pipeline) or directly to the review queue.

## Error Handling

- **Missing brief**: Set task to `blocked`, log "No content brief in task record"
- **Missing product data**: Set task to `blocked`, log "No product data in campaign"
- **Missing focus groups**: Write anyway using Product Aware as default awareness stage, log warning
- **Service unavailable** (web search down): Skip research step, write from brief context only, log warning
- **Word count impossible** (e.g., "write 5000 words about a paperclip"): Write the natural length, note deviation in frontmatter

## What This Skill Does NOT Cover

- **Which skills to load** — that's decided by the campaign's skillConfig and your agent's dynamicSkillIds
- **Platform-specific formatting** — that's in your format skill (copywriting, social-content, email-sequence, etc.)
- **Image generation** — that's vibe-image-director's job, not yours
- **Publishing** — that happens after human approval, not during writing
- **Fact-checking** — that's vibe-fact-checker's job in the pipeline after you
