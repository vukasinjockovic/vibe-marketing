# Research Report: Video Script Writing Skill for Marketing Platform
Generated: 2026-02-11

## Summary

No published Claude Code skills specifically for video script writing exist on skills.sh or in major skill repositories. The coreyhaines31/marketingskills repo and skills.sh ecosystem have content-creator and copywriting skills but nothing video-specific. The existing `content-writing-procedures` skill already lists `video_script` as a deliverableType but has NO outline template for it (unlike blog posts, landing pages, emails, etc.). Building a dedicated `video-script-guide` skill would fill a clear gap, covering 7+ distinct video formats each with unique structural requirements.

## Questions Answered

### Q1: Do any published Claude Code skills for video scripting exist?
**Answer:** No. No dedicated video script writing skill was found on skills.sh, in the anthropics/skills repo, coreyhaines31/marketingskills, alirezarezvani/claude-skills, ComposioHQ/awesome-claude-skills, or VoltAgent/awesome-agent-skills. The closest matches are:
- `rickydwilson-dcs/claude-skills/content-creator` on skills.sh -- a general content creator, not video-specific
- `remotion-dev/skills` -- for programmatic VIDEO EDITING (rendering with code), not script writing
- `coreyhaines31/marketingskills` -- has copywriting, CRO, SEO skills but no video script skill
**Source:** skills.sh, GitHub repos listed above
**Confidence:** High

### Q2: What video script frameworks/structures are used in marketing?
**Answer:** Six primary frameworks emerged from research (detailed below in Findings).
**Confidence:** High

### Q3: What are platform-specific format requirements?
**Answer:** Comprehensive specs found for YouTube, TikTok, Instagram Reels, YouTube Shorts, LinkedIn, and webinar formats (detailed below).
**Confidence:** High

### Q4: What is the VSL (Video Sales Letter) structure?
**Answer:** Multiple VSL frameworks found, most notably Jon Benson's 5-Step VSL Process and the AIDA/PAS adaptations for video (detailed below).
**Confidence:** High

### Q5: How do video scripts differ from written copy?
**Answer:** Video scripts require timing markers, two-column AV format, B-roll cues, speaker directions, visual descriptions, and words-per-minute calculations that written copy does not (detailed below).
**Confidence:** High

## Detailed Findings

### Finding 1: No Published Video Script Skills Exist

**Source:** skills.sh, GitHub
**Key Points:**
- skills.sh has no results for "video", "video-script", "youtube", or "vsl"
- `coreyhaines31/marketingskills` covers: page-cro, copywriting, seo-audit, launch-strategy, marketing-ideas -- no video
- `remotion-dev/skills` is for video RENDERING with code (React components), not script writing
- The existing `content-writing-procedures/SKILL.md` at line 22 lists `video_script` as a deliverableType but Step 5 (Outline) has NO video script template -- it only covers blog posts, landing pages, emails, ad copy, and social posts
- This means the current system would attempt to write a video script using the generic writing procedure with no video-specific guidance

**Install commands for related skills (none are video-script-specific):**
```bash
# General content creator (not video-specific)
npx skills add rickydwilson-dcs/claude-skills  # content-creator skill

# Marketing skills (copywriting, CRO, SEO -- no video)
npx skills add coreyhaines31/marketingskills

# Video RENDERING (not writing) with Remotion
npx skills add remotion-dev/skills
```

### Finding 2: Six Core Video Script Frameworks for Marketing

**Sources:** CopyPosse, ClickFunnels, Maekersuite, HubSpot, JeremyMac
**Frameworks:**

#### Framework 1: Hook-Story-Offer (HSO)
- **Origin:** Russell Brunson / ClickFunnels
- **Best for:** Ads, VSLs, short promos
- **Structure:**
  1. **Hook** (3-5 sec) -- Pattern interrupt, bold claim, or question
  2. **Story** (60-80% of runtime) -- Relatable struggle, transformation journey
  3. **Offer** (10-20% of runtime) -- Clear CTA with value stack
- **Source:** https://www.clickfunnels.com/blog/hook-story-offer/

#### Framework 2: AIDA (Attention-Interest-Desire-Action)
- **Origin:** Classic direct response (Halbert, Ogilvy era)
- **Best for:** YouTube ads, product demos, explainer videos
- **Structure:**
  1. **Attention** -- Compelling hook, question, or bold statement
  2. **Interest** -- Facts, anecdotes, stories that make them lean in
  3. **Desire** -- Show transformation, paint the "after" picture
  4. **Action** -- Clear CTA with urgency
- **Source:** https://maekersuite.com/blog/picking-a-storytelling-framework-for-your-video-script

#### Framework 3: PAS (Problem-Agitate-Solve)
- **Origin:** Classic copywriting
- **Best for:** Short ads, TikTok/Reels, problem-focused content
- **Structure:**
  1. **Problem** -- Name the pain point directly
  2. **Agitate** -- Twist the knife, show consequences
  3. **Solve** -- Present your product as the relief
- **Source:** https://copyposse.com/blog/how-to-write-a-high-converting-video-sales-letter-vsl-from-scratch/

#### Framework 4: Story-Solution-Offer (SSO)
- **Origin:** Russell Brunson
- **Best for:** Longer VSLs, webinars
- **Structure:**
  1. **Story** -- Origin story or customer case study
  2. **Solution** -- How the solution was discovered/built
  3. **Offer** -- Complete value proposition with stack
- **Source:** https://www.jeremymac.com/blogs/news/how-to-write-video-sales-letter-scripts-that-convert-in-10-minutes-ultimate-beginners-guide

#### Framework 5: Perfect Webinar Framework
- **Origin:** Russell Brunson
- **Best for:** Webinars, long-form sales presentations
- **Structure:**
  1. **Introduction** (15 min) -- Origin story, build rapport, set expectations
  2. **Content: 3 Secrets** (45 min) -- Each secret breaks a false belief, teaches value
  3. **The Stack and Close** (20 min) -- Layer offer components showing value, price anchor, close
- **Key technique:** The "Stack" -- layering offer components to build perceived value far exceeding price
- **Source:** https://www.clickfunnels.com/blog/complete-guide-high-converting-webinar/

#### Framework 6: Cookie Cutter / Meet Bob (Explainer Videos)
- **Origin:** Explainer video industry standard
- **Cookie Cutter:** Opening > Problems > Solution > How It Works > Results
- **Meet Bob:** Character introduction > Their pain > Discovery > Transformation > CTA
- **Best for:** Product explainers, SaaS demos, animated videos
- **Source:** https://vidico.com/explainer-video-production/explainer-video-script/

### Finding 3: Platform-Specific Format Requirements

**Sources:** Joyspace, PostFast, LinkedIn Help, various platform guides

| Platform | Duration Sweet Spot | Aspect Ratio | Word Count | Key Notes |
|----------|-------------------|--------------|------------|-----------|
| **YouTube (long-form)** | 8-15 min (tutorial), 10-20 min (essay) | 16:9 (1920x1080) | 1200-2250 words | Chapters/timestamps, pattern interrupt every 60-90 sec |
| **YouTube Shorts** | 15-35 sec | 9:16 (1080x1920) | 50-90 words | First frame must hook, text overlay essential |
| **TikTok** | 15-30 sec (viral), 21-34 sec (story), up to 60 sec (educational) | 9:16 (1080x1920) | 50-150 words | Authentic/unpolished preferred, text captions mandatory |
| **Instagram Reels** | 15-45 sec (60-90 sec max) | 9:16 (1080x1920) | 50-150 words | More polished than TikTok, "vibe" matters |
| **LinkedIn Video** | 30-90 sec (highest engagement), max 15 min desktop | 4:5 (1080x1350) or 16:9 | 75-225 words | Professional tone, captions essential (85% watch muted) |
| **Webinar** | 45-60 min (sales), up to 90 min (educational) | 16:9 (1920x1080) | 6750-9000 words | 80/20 value/selling rule, first 5 min determine retention |
| **VSL** | 2-5 min (short), 15-45 min (long-form) | 16:9 (1920x1080) | 300-750 (short) / 2250-6750 (long) | Text-on-screen format common, no face needed |
| **Explainer Video** | 60-90 sec | 16:9 (1920x1080) | 180-240 words | Problem 30%, Solution 40%, Proof 20%, CTA 10% |
| **Testimonial** | 60-120 sec | 16:9 or 9:16 | 150-300 words | Question-guided, NOT fully scripted |

**Words-per-minute reference:** Average speaking pace is ~150 words/min. Fast-paced (ads/shorts) = ~170 wpm. Deliberate/authoritative = ~130 wpm.

### Finding 4: VSL (Video Sales Letter) Deep Dive

**Sources:** CopyPosse, JeremyMac, Jon Benson (inventor of VSL), Warrior Forum

**What makes a VSL unique:**
- Often NO face on camera -- just text slides with voiceover (Jon Benson's original format)
- Designed for ONE purpose: conversion
- Typically embedded on a landing page, auto-plays
- Can be short (2-5 min for low-ticket) or long (15-45 min for high-ticket)

**Jon Benson's 5-Step VSL Process:**
1. **Snap Suggestion** -- Pattern interrupt that gives viewers a reason to watch. USP mentioned within first 10 slides
2. **Reluctant Hero** -- Position yourself as relatable, show vulnerability about past struggles
3. **Problem-Agitate** -- Name the pain, twist the knife, show consequences of inaction
4. **Solution Reveal** -- Present the product as the discovered answer
5. **Stack and Close** -- Layer value components, price anchor, guarantee, urgency, CTA

**Comprehensive VSL Script Structure (synthesized from multiple sources):**
```
1. PATTERN INTERRUPT (0:00-0:15)
   - Bold claim, question, or shocking stat
   - "If you [pain point], then this is the most important video you'll ever watch"

2. QUALIFY THE VIEWER (0:15-0:30)
   - "This is for people who..."
   - Filter out non-buyers, make ideal buyers lean in

3. CREDIBILITY FLASH (0:30-0:45)
   - Quick proof: results, credentials, social proof
   - "I've helped X people do Y" or "As seen in Z"

4. PROBLEM IDENTIFICATION (0:45-2:00)
   - Name the problem they're experiencing
   - Use their exact language (from focus group data)
   - Show you understand their world

5. AGITATION (2:00-3:00)
   - Consequences of NOT solving this
   - Emotional cost, financial cost, time cost
   - "And it only gets worse because..."

6. COMMON SOLUTIONS THAT FAIL (3:00-4:00)
   - Name alternatives they've tried
   - Explain WHY those don't work (without trashing competitors)
   - "It's not your fault" messaging

7. THE DISCOVERY/ORIGIN STORY (4:00-6:00)
   - How you found/built the solution
   - Reluctant hero narrative
   - Make it personal and relatable

8. THE MECHANISM (6:00-8:00)
   - Explain WHY your solution works (unique mechanism)
   - Educational content that builds belief
   - "The reason this works is..."

9. PROOF & RESULTS (8:00-10:00)
   - Case studies, testimonials, data
   - Before/after transformations
   - Specific numbers and timelines

10. THE OFFER (10:00-12:00)
    - Name the product/program
    - List everything included (the "stack")
    - Assign value to each component

11. PRICE ANCHOR & REVEAL (12:00-13:00)
    - "You might expect to pay $X..."
    - Reveal actual price as a fraction
    - Frame as investment, not cost

12. BONUSES (13:00-14:00)
    - 2-3 relevant bonuses with their own value
    - Each solves a related pain point

13. GUARANTEE / RISK REVERSAL (14:00-14:30)
    - Money-back guarantee, specific terms
    - Shift risk from buyer to seller

14. URGENCY / SCARCITY (14:30-15:00)
    - Time-limited, quantity-limited, or bonus-limited
    - Must be genuine

15. FINAL CTA (15:00-15:30)
    - Clear instruction: "Click the button below"
    - Recap the transformation
    - "You have two choices..." close

16. POST-CTA REINFORCEMENT (15:30+)
    - Additional testimonials
    - FAQ handling
    - Second CTA
```

### Finding 5: How Video Scripts Differ from Written Copy

**Sources:** Celtx, StudioBinder, Synthesia, HubSpot, TechSmith

**Key differences that a video-script-guide skill MUST address:**

#### 1. Two-Column AV Format
Written copy is single-column. Video scripts use two columns:
```
| VISUAL (left)                    | AUDIO (right)                        |
|----------------------------------|--------------------------------------|
| WIDE SHOT: Office bullpen,       | NARRATOR (V.O.): Every morning,      |
| workers at desks. 9 AM clock.    | Sarah opens 47 browser tabs...       |
|                                  |                                      |
| CU: Sarah's face, overwhelmed    | ...and spends 3 hours just figuring  |
|                                  | out what to work on first.           |
|                                  |                                      |
| B-ROLL: Competitor dashboards,   | She's tried every tool out there.    |
| cluttered interfaces              |                                      |
|                                  |                                      |
| PRODUCT SHOT: Clean dashboard    | [MUSIC: Shift to upbeat]             |
| with single metric visible       | Until she found [Product Name].      |
```

#### 2. Timing and Pacing
- Every section needs a timestamp or duration marker
- 150 words = ~1 minute of speaking
- Pauses must be scripted: `[PAUSE 2 SEC]`
- Pattern interrupts needed every 60-90 seconds for retention

#### 3. Visual Cues and B-Roll Notes
- `[B-ROLL: Customer using product on laptop]`
- `[GFX: Animated stat -- "73% faster"]`
- `[LOWER THIRD: Jane Doe, CEO of Acme]`
- `[SCREEN RECORDING: Dashboard walkthrough]`
- `[TEXT ON SCREEN: "Step 1: Sign Up"]`
- `[TRANSITION: Cut to...]`

#### 4. Speaker Directions
- `[SPEAKER: Look directly at camera]`
- `[TONE: Empathetic, slow down]`
- `[ENERGY: Pick up pace here]`
- `[AD LIB: Share personal example]`
- Pronunciation guides for technical terms
- Emotion markers: `[EXCITED]`, `[SERIOUS]`, `[CONVERSATIONAL]`

#### 5. Sound Design Notes
- `[MUSIC: Upbeat background, fade in]`
- `[SFX: Notification ding]`
- `[MUSIC: Cut]`
- `[AMBIENT: Office sounds]`

#### 6. Platform-Specific Constraints
- Short-form: Script must account for text overlays covering 20-30% of screen
- YouTube: Must plan for chapter markers and timestamps
- Webinar: Include slide change cues
- VSL: Each "slide" of text is a separate visual cue

#### 7. The "Read Aloud" Test
Video scripts must sound natural when spoken. Written copy doesn't have this constraint. This means:
- Shorter sentences (spoken language has shorter working memory)
- Contractions required ("you're" not "you are")
- No complex subordinate clauses
- Rhythm matters -- vary sentence length for natural flow
- Avoid alliteration and tongue-twisters

### Finding 6: Current Gap in content-writing-procedures

**Source:** `/var/www/vibe-marketing/.claude/skills/content-writing-procedures/SKILL.md`
**Key Points:**
- Line 22 lists `video_script` as a valid `deliverableType`
- Step 5 (Outline) provides templates for: blog post, landing page, email, ad copy, social post
- **No video script outline template exists** -- this is the gap
- The skill would try to write a video script using generic writing procedures with no format-specific guidance
- No mention of two-column format, timing, visual cues, B-roll, or speaker directions anywhere
- The social-content skill mentions Reels/TikTok but only as post types, not script structures

### Finding 7: 2026 Video Marketing Trends

**Sources:** Search Engine Journal, Entrepreneur, Awakened Films
**Key Points:**
- YouTube Shorts for discovery, long-form for depth is the 2026 consensus strategy
- YouTube clarified monetization enforcement against "mass-produced" or "repetitive" content (July 2025)
- Authenticity emphasis: behind-the-scenes content > polished ads
- AI-generated video scripts are acceptable but must be original and authentic
- Short-form video 15-30 sec is the dominant format for paid acquisition
- Webinars remain the highest-converting format for high-ticket B2B

## Comparison Matrix: Video Script Frameworks by Use Case

| Framework | Best For | Duration | Complexity | Conversion Focus |
|-----------|----------|----------|------------|-----------------|
| Hook-Story-Offer | Paid ads, short promos | 15s-2min | Low | High |
| AIDA | YouTube ads, demos | 30s-5min | Medium | High |
| PAS | TikTok/Reels, short ads | 15s-60s | Low | Medium |
| Cookie Cutter | Product explainers | 60-90s | Medium | Medium |
| VSL (full) | Sales pages, high-ticket | 5-45min | High | Very High |
| Perfect Webinar | Webinars, presentations | 45-90min | Very High | Very High |
| Meet Bob | Animated explainers | 60-120s | Medium | Medium |
| Testimonial | Social proof content | 60-120s | Low (guided) | Medium |

## Recommendations

### For This Codebase

1. **Create `/var/www/vibe-marketing/.claude/skills/video-script-guide/SKILL.md`** as a new format skill that sits alongside `copywriting`, `email-sequence`, `social-content`, and `paid-ads`. It should be loaded when `deliverableType === "video_script"`.

2. **Add a video_script outline template to `content-writing-procedures`** in Step 5, similar to the existing blog post and landing page templates. This ensures the generic writing pipeline knows how to structure video content.

3. **The new skill should cover 7 sub-formats** via a `videoFormat` field in the content brief:
   - `youtube_longform` -- Tutorial/essay format (8-20 min)
   - `short_form` -- TikTok/Reels/Shorts (15-60 sec)
   - `vsl` -- Video Sales Letter (2-45 min)
   - `webinar` -- Perfect Webinar format (45-90 min)
   - `explainer` -- Product explainer (60-120 sec)
   - `testimonial` -- Customer story (60-120 sec, question-guided)
   - `linkedin_video` -- Professional thought leadership (30-90 sec)
   - `ad` -- Paid video ad (15-60 sec)

4. **The skill should enforce the two-column AV format** for all video scripts, with the visual column (camera directions, B-roll, graphics) and audio column (dialogue, narration, music/SFX cues).

5. **Layer model integration:** The L1-L4 skill layers from the existing system apply to video scripts too:
   - L1 (Schwartz awareness) determines hook intensity and proof density
   - L2 (Hormozi offers) shapes the offer section of VSLs/webinars
   - L3 (Cialdini persuasion) informs proof elements and authority positioning
   - L4 (Craft voice) determines the speaker's tone and energy
   - L5 (Humanizer) is especially critical -- video scripts must sound spoken, not written

### Implementation Notes

- Words-per-minute calculator should be built into the skill: 150 wpm standard, 170 wpm fast (ads), 130 wpm deliberate
- The `contentBrief` should include a `videoFormat` field that routes to the correct sub-template
- Short-form scripts (<60 sec) should use a simplified single-column format since timing is compressed
- VSL scripts need a "slide count" estimate (1 slide per 3-5 seconds for text-on-screen format)
- Testimonial scripts should output QUESTIONS, not dialogue -- the authenticity comes from unscripted answers
- The skill should cross-reference `mbook-brunson-expert` for Perfect Webinar framework details (since Expert Secrets covers webinar selling)
- The skill should cross-reference `mbook-brunson-dotcom` for funnel-integrated video scripts
- The skill should cross-reference `mbook-hormozi-offers` for VSL offer stacking
- Webinar scripts need slide change cues: `[SLIDE: Title of slide]`
- All scripts should include a RETENTION PLAN -- where pattern interrupts occur to prevent drop-off

## Sources

1. [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) -- Official skills reference
2. [Vercel Skills Repository](https://github.com/vercel-labs/skills) -- npx skills ecosystem
3. [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) -- Marketing skills for Claude Code
4. [skills.sh](https://skills.sh) -- Skills marketplace (no video scripts found)
5. [Remotion Agent Skills](https://www.remotion.dev/docs/ai/claude-code) -- Video rendering, not script writing
6. [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) -- Curated skills list
7. [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) -- 300+ agent skills catalog
8. [CopyPosse - How to Write a VSL](https://copyposse.com/blog/how-to-write-a-high-converting-video-sales-letter-vsl-from-scratch/) -- VSL structure
9. [ClickFunnels - Hook, Story, Offer](https://www.clickfunnels.com/blog/hook-story-offer/) -- HSO framework
10. [ClickFunnels - Perfect Webinar Guide](https://www.clickfunnels.com/blog/complete-guide-high-converting-webinar/) -- Brunson's webinar framework
11. [Maekersuite - Video Storytelling Frameworks](https://maekersuite.com/blog/picking-a-storytelling-framework-for-your-video-script) -- Framework comparison
12. [JeremyMac - VSL Scripts That Convert](https://www.jeremymac.com/blogs/news/how-to-write-video-sales-letter-scripts-that-convert-in-10-minutes-ultimate-beginners-guide) -- VSL writing guide
13. [Jon Benson](https://jonbenson.com/) -- VSL inventor, 5-Step VSL Process
14. [Celtx - AV Script Template](https://blog.celtx.com/essential-av-script-template-for-better-video-scripts/) -- Two-column format guide
15. [StudioBinder - Video Script Template](https://www.studiobinder.com/templates/av-scripts/video-script-template/) -- Professional AV format
16. [HubSpot - Video Script Writing](https://blog.hubspot.com/marketing/how-to-write-a-video-script-ht) -- Script template and guide
17. [Synthesia - Video Script Templates](https://www.synthesia.io/post/free-video-script-templates) -- 14 free templates
18. [Vidico - Explainer Video Script](https://vidico.com/explainer-video-production/explainer-video-script/) -- Cookie Cutter and Meet Bob formulas
19. [Joyspace - Ideal Video Length 2026](https://joyspace.ai/ideal-video-length-social-platform-2026) -- Platform duration data
20. [PostFast - TikTok Video Specs 2026](https://postfa.st/sizes/tiktok/video) -- TikTok dimensions/specs
21. [PostFast - LinkedIn Video Specs 2026](https://postfa.st/sizes/linkedin/video) -- LinkedIn dimensions/specs
22. [LinkedIn Help - Video Specifications](https://www.linkedin.com/help/linkedin/answer/a1311816) -- Official LinkedIn specs
23. [Share.one - Testimonial Video Templates](https://www.share.one/script-and-question-templates/) -- Testimonial question framework
24. [ContentBeta - Testimonial Scripts](https://www.contentbeta.com/blog/testimonial-video-script/) -- Before/after testimonial structure
25. [Search Engine Journal - YouTube Strategy 2026](https://www.searchenginejournal.com/youtube-ceo-reveals-your-video-marketing-strategy-for-2026/565783/) -- YouTube trends
26. [Entrepreneur - Video Content Strategies 2026](https://www.entrepreneur.com/growing-a-business/how-businesses-should-rethink-video-strategy-for-2026/500810) -- 2026 video marketing

## Open Questions

- What is the exact "Video 6" structure referenced in YouTube marketing 2026 content? (behind a paywall)
- Jon Benson's full course material is proprietary -- the 5-Step framework is public but detailed slide-by-slide templates are behind a paywall
- Should the skill generate storyboard-ready output (with image generation prompts for each visual cue)?
- Should the skill support multi-language video scripts (for international campaigns)?
- What is the team's preferred script format -- pure AV two-column, or a hybrid markdown format?
