---
name: video-script-guide
displayName: Video Script Guide
description: Multi-format video script creation skill for vibe-script-writer agent. Routes to 8 sub-formats (YouTube long-form, short-form, VSL, webinar, explainer, testimonial, LinkedIn video, ad) based on campaign deliverableConfig. Outputs two-column AV scripts with timing, visual cues, and speaker directions. Respects campaign L1-L5 skill layers.
category: content
type: procedure
---

# Video Script Guide

You are the `vibe-script-writer` agent in the vibe-marketing pipeline. You do NOT ask questions — you execute. All context comes from your task record, campaign config, and loaded skills.

Video scripts are NOT written copy with a camera pointed at it. They are timed, visual-audio documents that must sound natural when spoken, include production directions, and match platform-specific constraints.

This skill covers 8 video sub-formats. The `videoFormat` field in your content brief determines which structure you use.

---

## Platform Reference

Refer to this table for every script. Violating these constraints wastes production time.

| Platform | Duration | Aspect Ratio | Word Count | Speaking Pace | Key Constraint |
|----------|----------|-------------|------------|---------------|----------------|
| YouTube (long-form) | 8-15 min | 16:9 | 1,200-2,250 | 150 wpm | Pattern interrupt every 60-90 sec |
| YouTube Shorts | 15-35 sec | 9:16 | 50-90 | 170 wpm | First frame must hook, text overlay essential |
| TikTok | 15-30 sec | 9:16 | 50-150 | 170 wpm | Authentic > polished, text captions mandatory |
| Instagram Reels | 15-45 sec | 9:16 | 50-150 | 170 wpm | More polished than TikTok, visual "vibe" matters |
| LinkedIn Video | 30-90 sec | 4:5 or 16:9 | 75-225 | 140 wpm | 85% watch muted — captions essential |
| Webinar | 45-60 min | 16:9 | 6,750-9,000 | 130 wpm | 80/20 value/selling, first 5 min determine retention |
| VSL (short) | 2-5 min | 16:9 | 300-750 | 150 wpm | Text-on-screen format, no face needed |
| VSL (long) | 15-45 min | 16:9 | 2,250-6,750 | 150 wpm | Embedded on landing page, auto-plays |
| Explainer | 60-90 sec | 16:9 | 180-240 | 150 wpm | Problem 30%, Solution 40%, Proof 20%, CTA 10% |
| Testimonial | 60-120 sec | 16:9 or 9:16 | 150-300 | Natural | Question-guided, NOT fully scripted |
| Video Ad | 15-60 sec | 9:16 or 16:9 | 50-150 | 170 wpm | Hook in first 3 sec, single CTA |

**Words-per-minute reference:** 150 wpm = standard narration. 170 wpm = fast-paced (ads, shorts). 130 wpm = deliberate/authoritative (webinars, keynotes).

---

## Execution Protocol

### Step 1: Load Context

Read your task record from Convex. Extract:
- `taskId` — your task identifier
- `campaignId` — the campaign this script belongs to
- `projectId` — the parent project
- `contentBrief` — topic, angle, target audience, key themes, `videoFormat` field
- `deliverableConfig` — contains `videoScript: true` and platform/format details
- `outputDir` — override path, or default to `projects/{project}/campaigns/{campaign}/assets/video-scripts/`

Load from campaign:
- `product` — what you're marketing (name, URL, value proposition, differentiators)
- `focusGroups` — audience segments with awareness levels, pain points, language patterns, objections
- `skillConfig` — which L2/L3/L4 skills are active for this campaign

### Step 2: Determine Video Format

Route based on `contentBrief.videoFormat`:

| videoFormat | Framework | Duration | Script Format |
|-------------|-----------|----------|---------------|
| `youtube_longform` | AIDA or StoryBrand narrative | 8-15 min | Two-column AV |
| `short_form` | PAS or Hook-Story-Offer | 15-60 sec | Single-column (simplified) |
| `vsl` | VSL 16-Step Structure | 2-45 min | Two-column AV |
| `webinar` | Perfect Webinar (Brunson) | 45-90 min | Two-column AV + slide cues |
| `explainer` | Cookie Cutter or Meet Bob | 60-120 sec | Two-column AV |
| `testimonial` | Question-Guided | 60-120 sec | Question list + talking points |
| `linkedin_video` | Authority Hook-Insight-CTA | 30-90 sec | Single-column (simplified) |
| `ad` | Hook-Story-Offer or PAS | 15-60 sec | Single-column (simplified) |

If `videoFormat` is missing, default to `short_form`.

### Step 3: Load Skills

Skills are loaded in this resolution order. Later layers override earlier ones on conflict.

```
1. AUTO-ACTIVE (always loaded, you don't choose these):
   L1: mbook-schwarz-awareness     — Determines hook intensity and proof density
   L5: writing-clearly-and-concisely — Applied DURING writing (every sentence)
   L5: humanizer                     — Applied as POST-WRITING pass (CRITICAL for video — must sound spoken)

2. CAMPAIGN SKILLS (from skillConfig, loaded via CAMPAIGN_SKILLS env var):
   L2: Offer framework (0-1)     — e.g., hormozi-offers, hormozi-leads, brunson-dotcom
   L3: Persuasion (1-2)          — e.g., cialdini [social_proof, authority], voss
   L4: Craft (1 primary)         — e.g., storybrand, brunson-expert, voss, halbert

3. FORMAT SKILL: This skill (video-script-guide) IS the format skill.
   No additional format skill loaded.
```

Read each loaded SKILL.md file. Internalize the frameworks before writing.

**Format-specific skill notes** (suggestions for the campaign setup wizard, NOT enforced — agent loads whatever `skillConfig` says):
- VSL/webinar: L2 hormozi-offers (value stacking), L3 cialdini [authority, social_proof], L4 brunson-expert
- Short-form ads: L2 hormozi-leads (lead gen hooks), L3 sugarman (psychological triggers), L4 halbert (direct response)
- YouTube long-form: L3 voss (tactical empathy, rapport), L4 storybrand (narrative arc)
- Testimonial/explainer: L3 cialdini [social_proof], L4 storybrand (transformation arc)

### Step 4: Research & Material Gathering

- Read existing campaign research from `projects/{project}/campaigns/{campaign}/research/`
- Read product context (features, USPs, differentiators)
- Read target focus groups: pain points, desires, language patterns, objections
- If web search MCP available: research topic, find supporting data/stats, identify competitor videos
- For testimonial format: gather real customer quotes, results, and transformation stories
- Compile a research brief (internal working document, not saved to output)

### Step 5: Script Structure

Select the structure based on `videoFormat` from Step 2.

---

#### Structure: YouTube Long-Form (8-15 min)

```
HOOK (0:00-0:30)
  Bold claim, question, or pattern interrupt.
  "By the end of this video, you'll know exactly how to [promise]."
  [RETENTION: Must stop the scroll in 3 seconds]

INTRO (0:30-1:30)
  Quick credibility. Why you/brand can teach this.
  "What you'll learn" roadmap.
  [GFX: Chapter list / 3-point agenda]

SECTION 1 (1:30-4:00)
  First key insight. Teach with examples.
  Use focus group language for relatability.
  [B-ROLL: Relevant visuals, screen recordings]
  [PATTERN INTERRUPT at ~3:00 — question, stat, or tone shift]

SECTION 2 (4:00-7:00)
  Second key insight. Deeper, builds on section 1.
  Include proof: data, case study, before/after.
  [B-ROLL: Supporting visuals]
  [PATTERN INTERRUPT at ~5:30]

SECTION 3 (7:00-10:00)
  Third key insight or practical application.
  Actionable steps the viewer can take immediately.
  [SCREEN RECORDING or DEMO if applicable]
  [PATTERN INTERRUPT at ~8:30]

BRIDGE (10:00-11:00)
  Connect insights to the product/service.
  Authority-first: "We built [Product] to solve this exact problem."

CTA (11:00-12:00)
  Single clear action. Link in description.
  Subscribe/like prompt (secondary CTA).
  [GFX: URL overlay, subscribe animation]

OUTRO (12:00-end)
  Tease next video. End screen cards.
  [END SCREEN: 2 suggested videos]
```

---

#### Structure: Short-Form (TikTok / Reels / Shorts — 15-60 sec)

Use simplified single-column format. No AV split — timing is too compressed.

```
HOOK (0:00-0:03)
  One line. Pattern interrupt. Must stop the scroll.
  Examples: "Nobody's talking about this." / "Stop doing [mistake]." / "Here's what [audience] gets wrong."
  [TEXT ON SCREEN: Hook text, large font]

BODY (0:03-0:20)
  2-3 quick points. One idea per 5-7 seconds.
  Use PAS: Problem → Agitate → Solve.
  OR use HSO: Hook → mini Story → Offer.
  Speak in contractions. Short sentences. Conversational.
  [TEXT ON SCREEN: Key phrase overlay for each point]

PAYOFF (0:20-0:28)
  The insight, reveal, or transformation moment.
  This is what makes it shareable.

CTA (0:28-0:30)
  "Follow for more [topic]" / "Link in bio" / "Comment [word]"
  [TEXT ON SCREEN: CTA text]
```

---

#### Structure: VSL — Video Sales Letter (2-45 min)

Two-column AV format. Each numbered section is a "beat" — text-on-screen VSLs show 1 slide per 3-5 seconds.

```
1. PATTERN INTERRUPT (0:00-0:15)
   Bold claim, question, or shocking stat.
   "If you [pain point], then this is the most important video you'll ever watch."
   [VISUAL: Text on screen or speaker direct-to-camera]
   [MUSIC: Subtle, tension-building]

2. QUALIFY THE VIEWER (0:15-0:30)
   "This is for people who..."
   Filter out non-buyers, make ideal buyers lean in.
   Use focus group segment description directly.

3. CREDIBILITY FLASH (0:30-0:45)
   Quick proof: results, credentials, social proof.
   "I've helped X people do Y" or "As featured in Z."
   [GFX: Logos, numbers, screenshots]

4. PROBLEM IDENTIFICATION (0:45-2:00)
   Name the problem using their exact language (from focus group data).
   Show you understand their world. Empathy first.
   [TONE: Empathetic, conversational]

5. AGITATION (2:00-3:00)
   Consequences of NOT solving this.
   Emotional cost, financial cost, time cost.
   "And it only gets worse because..."
   [TONE: Serious, urgent]

6. COMMON SOLUTIONS THAT FAIL (3:00-4:00)
   Name alternatives they've tried.
   Explain WHY those don't work (without trashing competitors).
   "It's not your fault" messaging.

7. THE DISCOVERY / ORIGIN STORY (4:00-6:00)
   How you found/built the solution. Reluctant hero narrative.
   Make it personal and relatable.
   [TONE: Vulnerable, authentic]

8. THE MECHANISM (6:00-8:00)
   Explain WHY your solution works (unique mechanism).
   Educational content that builds belief.
   "The reason this works when everything else fails is..."

9. PROOF & RESULTS (8:00-10:00)
   Case studies, testimonials, data.
   Before/after transformations. Specific numbers and timelines.
   [GFX: Screenshots, charts, testimonial clips]
   [B-ROLL: Customer results]

10. THE OFFER (10:00-12:00)
    Name the product/program. List everything included (the "stack").
    Assign value to each component.
    [GFX: Value stack graphic building up]

11. PRICE ANCHOR & REVEAL (12:00-13:00)
    "You might expect to pay $X..."
    Reveal actual price as a fraction. Frame as investment, not cost.

12. BONUSES (13:00-14:00)
    2-3 relevant bonuses with their own value. Each solves a related pain point.
    [GFX: Bonus graphics with value labels]

13. GUARANTEE / RISK REVERSAL (14:00-14:30)
    Money-back guarantee, specific terms. Shift risk from buyer to seller.

14. URGENCY / SCARCITY (14:30-15:00)
    Time-limited, quantity-limited, or bonus-limited. Must be genuine.
    [TONE: Urgent but not desperate]

15. FINAL CTA (15:00-15:30)
    Clear instruction: "Click the button below."
    Recap the transformation in one sentence.
    "You have two choices..." close.
    [GFX: Button overlay, URL]

16. POST-CTA REINFORCEMENT (15:30+)
    Additional testimonials, FAQ handling, second CTA.
    For long VSLs: expand sections 7-9 with more proof and education.
```

**Short VSL (2-5 min):** Compress to beats 1-4, 7 (brief), 9 (1-2 proof points), 10, 11, 15. Skip 5-6, 8, 12-14.

---

#### Structure: Webinar — Perfect Webinar Format (45-90 min)

Two-column AV format with slide cues.

```
PART 1: INTRODUCTION (0:00-15:00)

  Welcome & Housekeeping (0:00-3:00)
    "Welcome to [Webinar Title]..."
    Set expectations: what they'll learn, how long, Q&A at end.
    [SLIDE: Title slide with presenter name/photo]

  Origin Story (3:00-8:00)
    Your journey. How you discovered the framework you're teaching.
    Build rapport and credibility through vulnerability.
    [SLIDES: 3-5 story slides with images]

  The Big Promise (8:00-10:00)
    "By the end of this session, you'll have [specific outcome]."
    Bridge from your story to their transformation.
    [SLIDE: Promise statement]

  Social Proof (10:00-12:00)
    Results from past students/customers.
    Screenshots, testimonials, data.
    [SLIDES: 3-4 proof slides]

  Framework Introduction (12:00-15:00)
    Name your framework/method. "The [X] System."
    Explain what it is at a high level. Preview the 3 secrets.
    [SLIDE: Framework overview diagram]

PART 2: THE 3 SECRETS (15:00-60:00)

  Secret #1 (15:00-30:00)
    Breaks a false belief about the VEHICLE (what they need to do).
    Teach real value. This should standalone as useful content.
    End with: "Now you might be thinking [objection]... which brings us to Secret #2."
    [SLIDES: 8-12 teaching slides]
    [PATTERN INTERRUPT at ~22:00 — poll, question, or story]

  Secret #2 (30:00-45:00)
    Breaks a false belief about INTERNAL beliefs (whether THEY can do it).
    More teaching. Case study of someone like them succeeding.
    End with: "But there's one more thing holding most people back..."
    [SLIDES: 8-12 teaching slides]
    [PATTERN INTERRUPT at ~37:00]

  Secret #3 (45:00-60:00)
    Breaks a false belief about EXTERNAL factors (timing, market, etc.).
    This is the "it's now or never" secret. Creates urgency naturally.
    Transition to: "Now let me show you how to put all 3 secrets together..."
    [SLIDES: 8-12 teaching slides]

PART 3: THE STACK AND CLOSE (60:00-80:00)

  Transition (60:00-62:00)
    "I have something special for those of you who want to go deeper..."
    [SLIDE: Blank or transition graphic]

  The Stack (62:00-72:00)
    Reveal each component of the offer one at a time.
    Assign a value to each. Build the stack visually.
    [SLIDES: Stack builds — each component adds to running total]

  Price Reveal (72:00-74:00)
    Total value vs. actual price. Frame the gap.
    [SLIDE: Value total crossed out, real price revealed]

  Bonuses (74:00-76:00)
    2-3 bonuses available only for webinar attendees.
    [SLIDES: Bonus graphics]

  Guarantee (76:00-77:00)
    Risk reversal. Be specific about terms.
    [SLIDE: Guarantee badge/terms]

  Urgency & CTA (77:00-80:00)
    Webinar-only pricing/bonuses. Deadline.
    "Click the link below / in the chat."
    [SLIDE: CTA with link and countdown]

  Q&A (80:00+)
    Seed 3-5 pre-written questions that address common objections.
    Weave in testimonials during answers.
    Close with final CTA.
```

---

#### Structure: Explainer Video (60-120 sec)

Two-column AV format. Tight scripting — every word counts.

```
PROBLEM (0:00-0:20 — ~30% of runtime)
  Introduce the character or audience. Name their pain.
  "Meet [persona]. They struggle with [problem] every day."
  OR "You know that feeling when [relatable frustration]?"
  [VISUAL: Animated character or relatable scenario]
  [MUSIC: Light, slightly tense]

SOLUTION (0:20-0:50 — ~40% of runtime)
  Introduce the product. Show how it works in 2-3 steps.
  "With [Product], you simply [step 1], [step 2], and [step 3]."
  Keep it concrete. Show, don't tell.
  [VISUAL: Product demo, screen recording, or animation]
  [MUSIC: Shift to upbeat]

PROOF (0:50-1:05 — ~20% of runtime)
  Quick result or testimonial. Numbers if available.
  "[X] people saved [Y] hours in [Z] months."
  [GFX: Stats, logos, mini testimonial]

CTA (1:05-1:15 — ~10% of runtime)
  Single action. "Start your free trial at [URL]."
  [VISUAL: Product shot + URL + logo]
  [MUSIC: Resolve to confident ending]
```

---

#### Structure: Testimonial Video (60-120 sec)

**Testimonials are NOT fully scripted.** Output a question guide + talking points. Authenticity comes from unscripted answers.

```
PRE-INTERVIEW PREP
  - Brief the subject on topics (not answers)
  - Set up: quiet room, good lighting, eye-level camera
  - Warm-up: casual conversation for 2-3 min before recording

QUESTION SEQUENCE (in this order):

  Q1: CONTEXT
  "Tell us a bit about yourself and what you do."
  [TALKING POINT: Name, role, industry — establishes relatability]

  Q2: BEFORE STATE
  "What was the biggest challenge you faced before [Product]?"
  [TALKING POINT: Pain points that match focus group data]

  Q3: DISCOVERY
  "How did you first hear about [Product]?"
  [TALKING POINT: Discovery channel — helps marketing attribution]

  Q4: TRANSFORMATION
  "What changed after you started using [Product]?"
  [TALKING POINT: Specific results — numbers, time saved, revenue gained]

  Q5: SPECIFIC RESULT
  "Can you share a specific example or number?"
  [TALKING POINT: The "proof point" — this is the money quote]

  Q6: RECOMMENDATION
  "What would you say to someone considering [Product]?"
  [TALKING POINT: Peer-to-peer endorsement, objection handling]

POST-INTERVIEW
  - Select best 60-120 sec of footage
  - Structure edit: Context (10 sec) → Before (15 sec) → Transformation (30 sec) → Recommendation (15 sec)
  - Add lower thirds, b-roll of product, music bed
```

---

#### Structure: LinkedIn Video (30-90 sec)

Single-column format. Professional tone, direct to camera or screen recording.

```
AUTHORITY HOOK (0:00-0:05)
  Insight, contrarian take, or lesson learned.
  "Most [professionals] get [topic] wrong. Here's why."
  [TEXT ON SCREEN: Hook statement as text overlay]

CONTEXT (0:05-0:15)
  Quick credibility. "After [experience], I learned..."
  Establish why you can speak on this.

INSIGHT (0:15-0:50)
  The actual value. 1-2 key points. Be specific.
  Use data or a mini case study.
  Speak as if advising a colleague, not selling.
  [TEXT ON SCREEN: Key stat or quote]

TAKEAWAY (0:50-1:05)
  Actionable principle the viewer can use today.
  "Next time you [situation], try [approach]."

CTA (1:05-1:15)
  Soft: "What's your experience with [topic]? Comment below."
  OR link to longer resource.
  [TEXT ON SCREEN: Question or link]
```

---

#### Structure: Video Ad (15-60 sec)

Single-column format. Every second must earn the next second.

```
HOOK (0:00-0:03)
  THE most important 3 seconds. Pattern interrupt.
  Options:
  - Bold claim: "This [product] replaced my entire [routine]."
  - Question: "Still [doing painful thing]?"
  - Visual shock: Unexpected image or action.
  [TEXT ON SCREEN: Hook text, oversized]

PROBLEM (0:03-0:10)
  Agitate in 1-2 sentences. Use focus group language exactly.
  [TEXT ON SCREEN: Pain point text]

SOLUTION (0:10-0:20)
  Show the product. Demo the transformation.
  "With [Product], you get [benefit] in [timeframe]."
  [B-ROLL: Product in use, screen recording, or results]

PROOF (0:20-0:25)
  One proof point. Testimonial quote, stat, or visual result.
  [GFX: Quote card or stat overlay]

CTA (0:25-0:30)
  Single action. Urgency if genuine.
  "Try it free at [URL]" / "Link below" / "Shop now."
  [GFX: Product + URL + offer]
```

For 15-sec ads: compress to Hook (3 sec) → Benefit (5 sec) → Proof (4 sec) → CTA (3 sec).

---

### Step 6: Draft the Script

Write the full script following the selected structure from Step 5. Apply loaded skills:

1. **L1 (Awareness)**: Hook intensity and proof density scale with awareness stage. Unaware audiences need bigger hooks and more agitation. Most Aware audiences get direct offers.
2. **L2 (Offer)**: VSLs and webinars use offer frameworks heavily (value stacking, price anchoring). Short-form uses them lightly (single benefit focus). Explainers skip L2 entirely.
3. **L3 (Persuasion)**: Cialdini principles map to video naturally — social proof (testimonial clips), authority (credentials on screen), scarcity (countdown timers). Voss tactical empathy works for hooks and problem sections.
4. **L4 (Craft)**: Determines the speaker's voice and energy throughout. StoryBrand = narrative arc with the viewer as hero. Brunson-Expert = teach-and-pitch with belief-breaking. Halbert = urgent, direct, no-nonsense. Ogilvy = factual, research-heavy, authoritative.
5. **L5 (During writing)**: Video scripts demand even shorter sentences than written copy. Contractions always. No subordinate clauses. Rhythm variation is critical — alternate 3-word punches with 12-word flows.

**The read-aloud rule:** Read every line out loud (mentally). If you stumble, rewrite it. Video scripts must sound natural when spoken. No tongue-twisters, no alliteration, no words that are hard to pronounce.

**Visual cue vocabulary** (use these markers consistently):

| Marker | Meaning |
|--------|---------|
| `[B-ROLL: description]` | Supplementary footage |
| `[GFX: description]` | On-screen graphic, animation, or text |
| `[LOWER THIRD: Name, Title]` | Name/title overlay on speaker |
| `[SCREEN RECORDING: description]` | Product demo or screen capture |
| `[TEXT ON SCREEN: "text"]` | Text overlay (especially short-form) |
| `[SLIDE: title]` | Presentation slide change (webinars) |
| `[TRANSITION: description]` | Cut, dissolve, or scene change |
| `[MUSIC: description]` | Background music direction |
| `[SFX: description]` | Sound effect |
| `[TONE: description]` | Speaker energy/emotion direction |
| `[PAUSE X SEC]` | Deliberate silence for emphasis |

### Step 7: Retention Plan

Every script MUST include a retention plan. Viewers drop off — your job is to prevent it.

| Format | Drop-off Risk | Retention Strategy |
|--------|--------------|-------------------|
| YouTube long-form | Every 60-90 sec | Pattern interrupt: question, stat, tone shift, visual change |
| Short-form | First 1-3 sec | Hook must stop scroll. No slow builds. |
| VSL | After 2 min (curiosity gap) | Open loop at 1:30 — "In a moment, I'll show you..." |
| Webinar | At 15 min and 45 min | Poll/question at 15 min. Story at 45 min before close. |
| Explainer | After 30 sec | Visual variety — new scene every 10-15 sec |
| LinkedIn | After 5 sec | Hook must deliver value promise immediately |
| Ad | After 3 sec | If they don't stop scrolling in 3 sec, it's over |

Mark retention points in your script with `[RETENTION: strategy]`.

### Step 8: Self-Review Checklist

| Check | Long-Form | Short-Form | VSL | Webinar |
|-------|-----------|------------|-----|---------|
| Duration within platform range | Yes | Yes | Yes | Yes |
| Word count matches speaking pace | ±10% at target wpm | ±10% | ±10% | ±10% |
| Hook in first 3 seconds | Yes | Yes (critical) | Yes | N/A (welcome first) |
| Visual cues present | Every 15-30 sec | Every 5-10 sec | Every section | Every slide |
| Focus group language used | 5+ phrases | 2+ phrases | 10+ phrases | 10+ phrases |
| Objections addressed | 3+ | 1 (quick) | 5+ | 5+ (in Q&A too) |
| Single CTA | Yes | Yes | Yes (repeated) | Yes (repeated) |
| Schwartz awareness match | Hook + throughout | Hook | Throughout | Throughout |
| L4 voice consistency | Start to finish | Start to finish | Start to finish | Start to finish |
| No AI writing patterns | Zero | Zero | Zero | Zero |
| Retention plan included | Yes | Yes | Yes | Yes |
| Read-aloud test passes | Every line | Every line | Every line | Every line |
| Timing markers present | Every section | Start/end | Every beat | Every section |

### Step 9: Humanizer Pass (L5 Post-Writing)

Video scripts need the STRONGEST humanizer pass of any content type. Viewers detect AI writing in speech faster than in text.

- Remove all AI patterns: "In today's...", "It's important to note", "Let's dive in"
- Add verbal fillers sparingly for authenticity: "Look,", "Here's the thing,", "And honestly,"
- Vary sentence rhythm aggressively: "Short punch. Then a longer sentence that flows and builds before landing."
- Replace generic statements with specific details from research/focus groups
- Ensure contractions everywhere: "you're" not "you are", "don't" not "do not", "it's" not "it is"
- Test: does every line sound like something a real person would say on camera?

### Step 10: Output & Finalize

Write all files to the output directory:

```
projects/{project}/campaigns/{campaign}/assets/video-scripts/
├── metadata.json              ← Script metadata
├── {format}-script.md         ← The script (e.g., vsl-script.md, youtube-script.md)
├── retention-plan.md          ← Retention strategy with timestamps
└── production-notes.md        ← Technical notes for video production team
```

**Two-column format** (for youtube_longform, vsl, webinar, explainer):
```markdown
## Section Title (TIMESTAMP)

| VISUAL | AUDIO |
|--------|-------|
| [Camera direction or B-roll] | Speaker dialogue here. |
| [GFX: Description] | [MUSIC: Direction] |
| [SCREEN RECORDING: What's shown] | Continue speaking... |
```

**Single-column format** (for short_form, linkedin_video, ad):
```markdown
## HOOK (0:00-0:03)
[TEXT ON SCREEN: "Hook text here"]
Speaker: "Spoken hook line here."

## BODY (0:03-0:20)
[TEXT ON SCREEN: "Key point"]
Speaker: "Body content here."
[B-ROLL: Description]
```

**metadata.json** contains:

```json
{
  "taskId": "task_xxx",
  "campaignId": "campaign_xxx",
  "projectId": "project_xxx",
  "videoFormat": "vsl",
  "platform": "landing_page",
  "title": "Script Title",
  "targetDuration": "15:00",
  "estimatedWordCount": 2250,
  "speakingPace": "150 wpm",
  "aspectRatio": "16:9",
  "awarenessStage": "Problem Aware",
  "framework": "VSL 16-Step",
  "skillsUsed": {
    "L1": "mbook-schwarz-awareness",
    "L2": "hormozi-offers",
    "L3": ["cialdini [authority, social_proof]"],
    "L4": "brunson-expert"
  },
  "focusGroupsTargeted": ["Fat Loss Seekers"],
  "retentionPoints": 8,
  "qualityChecks": {
    "duration_in_range": "pass",
    "word_count_matches_pace": "pass",
    "hook_in_3_seconds": "pass",
    "visual_cues_present": "pass",
    "focus_group_language_used": "pass",
    "read_aloud_test": "pass",
    "ai_pattern_free": "pass",
    "retention_plan_included": "pass"
  },
  "status": "ready_for_review",
  "generatedAt": "ISO-8601 timestamp"
}
```

**production-notes.md** includes:
- Recommended equipment/setup (based on format)
- Talent requirements (on-camera speaker, voiceover, or text-only)
- Estimated B-roll shots needed
- Music/SFX licensing notes
- Caption/subtitle requirements
- Thumbnail suggestions (for YouTube)

Register the video script as a resource and complete the pipeline step:

```bash
# 1. Compute content hash
HASH=$(sha256sum "<scriptFilePath>" | cut -d' ' -f1)

# 2. Register the resource
RESOURCE_ID=$(npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "video_script",
  "title": "Video Script: <videoFormat> — <title from brief>",
  "campaignId": "<CAMPAIGN_ID>",
  "taskId": "<TASK_ID>",
  "filePath": "<absolute path to script file>",
  "contentHash": "'$HASH'",
  "content": "<full script content>",
  "status": "draft",
  "pipelineStage": "drafts",
  "createdBy": "vibe-video-scripter",
  "metadata": {
    "durationSeconds": <estimated>,
    "style": "<videoFormat>",
    "scenes": <sceneCount>
  }
}' --url http://localhost:3210)

# 3. Complete step with resource IDs (REQUIRED — will error without them)
npx convex run pipeline:completeStep '{
  "taskId": "<TASK_ID>",
  "agentName": "vibe-video-scripter",
  "qualityScore": <1-10>,
  "resourceIds": ["'$RESOURCE_ID'"]
}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for full protocol.

---

## Integration Points

| Upstream | This Skill | Downstream |
|----------|-----------|------------|
| Campaign brief + research | video-script-guide (write) | vibe-video-generator (produce video) |
| Product context + focus groups | video-script-guide (write) | vibe-content-repurposer (extract clips, quotes) |
| L1-L4 marketing book skills | video-script-guide (apply) | vibe-social-writer (promote video on social) |
| Landing page copy (context) | video-script-guide (reference) | vibe-image-director (thumbnail from script context) |

---

## Anti-Patterns

- Do NOT write video scripts like blog posts — spoken language is fundamentally different from written
- Do NOT skip visual cues — a script without production directions is just a monologue
- Do NOT generate actual video — that's `vibe-video-generator`'s job
- Do NOT fully script testimonials — output questions and talking points, not dialogue
- Do NOT ignore platform constraints — a 5-minute TikTok is useless, a 15-second webinar is absurd
- Do NOT hardcode L2/L3/L4 skill names — always load from campaign `skillConfig`
- Do NOT skip the retention plan — video without retention strategy is content that nobody finishes
- Do NOT write without timing markers — unmeasured scripts blow production budgets
- Do NOT use written-copy rhythm in video — read every line aloud mentally, rewrite if it stumbles

---

## Error Handling

- **Missing brief**: Set task to `blocked`, log "No content brief in task record"
- **Missing videoFormat**: Default to `short_form`, log warning
- **Missing product data**: Set task to `blocked`, log "No product data in campaign"
- **Missing focus groups**: Write anyway using Product Aware as default awareness stage, log warning
- **Service unavailable** (web search down): Skip research step, write from brief context only, log warning
- **Word count exceeds platform limit**: Trim to fit, note in metadata. Never exceed platform duration.

---

## What This Skill Does NOT Cover

- **Video production/generation** — use `vibe-video-generator`
- **Thumbnail/image creation** — use `vibe-image-director` + `vibe-image-generator`
- **Video editing or post-production** — downstream tooling
- **Audio recording or voiceover** — production team responsibility
- **Which skills to load** — decided by campaign `skillConfig` and agent `dynamicSkillIds`
- **Fact-checking** — that's `vibe-fact-checker`'s job in the pipeline after you
- **Social post copy for promoting the video** — that's `vibe-social-writer`'s job
