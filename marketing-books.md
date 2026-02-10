# Marketing Books → Skills Reference

> These books get distilled into Claude Code skills that vibe-marketing agents
> invoke during content creation. Each skill encodes a specific framework,
> not just knowledge — it changes HOW the agent writes.

---

## Skill Categories (Not "Tones")

These aren't tones. They're **layers** that stack. A single piece of copy might use
Schwartz (to match awareness level) + Hormozi (to structure the offer) + Voss
(to pre-handle objections) + Ogilvy (for headline craft). The question isn't
"which one?" — it's "which combination?"

**You don't use all of them.** A typical campaign loads 2-4 skills total (plus the
auto-active ones). Each layer is pick-some-or-none, not pick-all.

### Layer Model

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: AUDIENCE UNDERSTANDING (auto — not selectable) │
│ Always active. Derived from focus group data.           │
│ mbook-schwarz-awareness                                      │
└─────────────────────────────────────────────────────────┘
         ↓ informs
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: OFFER STRUCTURE (pick 0-1, rarely 2)           │
│ Skip entirely if no offer/product pitch in this content.│
│ hormozi-offer · hormozi-leads · brunson-funnels         │
└─────────────────────────────────────────────────────────┘
         ↓ shapes
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: PERSUASION MECHANICS (pick 1-2)                │
│ The psychological toolkit. Don't overload — 2 max.      │
│ cialdini · voss · sugarman · marketing-psychology       │
└─────────────────────────────────────────────────────────┘
         ↓ expressed through
┌─────────────────────────────────────────────────────────┐
│ LAYER 4: COPY CRAFT (pick 1 primary, optional secondary)│
│ These are writing STYLES — mutually exclusive primary.   │
│ ogilvy · halbert · storybrand · brunson-positioning     │
└─────────────────────────────────────────────────────────┘
         ↓ polished by
┌─────────────────────────────────────────────────────────┐
│ LAYER 5: QUALITY (auto — not selectable)                │
│ Always runs post-writing.                               │
│ humanizer · writing-clearly                             │
└─────────────────────────────────────────────────────────┘
```

---

### Layer Details — Dashboard Option Descriptions

These descriptions appear in the dashboard when creating a campaign. Each option
has a name, a one-line tagline, and a paragraph explaining when and why to use it.

---

#### Layer 1: Audience Understanding (Auto-Active)

> This layer runs automatically. The system reads the awareness stage from your
> selected focus groups and adjusts the entire copy approach — headline formula,
> opening strategy, CTA style — without you needing to configure anything.

**`mbook-schwarz-awareness`** — *Match copy to how aware your reader already is*

Based on Eugene Schwartz's 5 Stages of Market Awareness. An "Unaware" reader
needs a story that reveals a problem they didn't know they had. A "Most Aware"
reader just needs the deal. This skill ensures your agents don't write
awareness-mismatched copy — the #1 reason marketing content fails to convert.
Auto-derived from each focus group's `awarenessStage` field.

---

#### Layer 2: Offer Structure (Pick 0-1)

> How you frame the thing you're selling (or giving away). Skip this layer
> entirely for pure content campaigns (blog series, social content) where
> there's no direct offer. Select one when your campaign includes landing pages,
> ads, email sequences, or lead magnets that present a specific offer.

**`hormozi-offer`** — *Make your offer so good people feel stupid saying no*

Alex Hormozi's Value Equation: maximize the Dream Outcome and Perceived
Likelihood of Achievement while minimizing Time Delay and Effort & Sacrifice.
Use this when writing landing pages, pricing sections, ad copy, or any content
where you're asking someone to buy or sign up. The agent will structure every
benefit through the value equation lens and apply Grand Slam Offer principles:
stack bonuses, reverse risk with guarantees, and use ethical scarcity. Best for:
landing pages, ads, sales emails, pricing pages.

**`hormozi-leads`** — *Design content that turns strangers into leads*

Alex Hormozi's lead generation framework from $100M Leads. Structures your
content as a give-to-ask pipeline: free value first (blog posts, tools,
checklists), then lead magnet conversion, then nurture to customer. The agent
will apply lead magnet design principles (solve a narrow problem completely),
the Core 4 advertising methods, and the give-to-ask ratio. Best for: ebooks,
lead magnets, content strategy, top-of-funnel blog posts, email opt-in pages.

**`brunson-funnels`** — *Position content within a multi-step funnel journey*

Russell Brunson's funnel frameworks from DotCom Secrets. Places each piece of
content on a Value Ladder (free → low-ticket → mid → high-ticket) and structures
email sequences using proven patterns: Soap Opera Sequence for launches (5-email
story arc with cliffhangers) or Seinfeld Sequence for ongoing nurture (daily
entertainment + value). Also applies the Hook → Story → Offer framework to every
piece. Best for: launch campaigns, multi-step funnels, email sequences, upsell pages.

---

#### Layer 3: Persuasion Mechanics (Pick 1-2)

> The psychological tools your agent uses while writing. These are tactical —
> they influence word choice, argument structure, and how objections are handled.
> Pick 1-2 that match your campaign's angle. Using more than 2 creates conflicting
> instructions and dilutes the copy's focus.

**`cialdini-persuasion`** — *Apply proven principles of human persuasion*

Robert Cialdini's 7 Principles of Influence. When you select this skill, you also
pick WHICH principles to emphasize (not all 7 at once):
- **Reciprocity** — Give value first, then ask. Best for: blog intros, lead magnets.
- **Commitment/Consistency** — Get small yeses that lead to the big yes. Best for: email sequences, multi-step funnels.
- **Social Proof** — Show others already trust you (testimonials, numbers, case studies). Best for: landing pages, ads.
- **Authority** — Position as the expert with credentials, data, endorsements. Best for: blog posts, ebooks.
- **Liking** — Be relatable, share identity, use humor. Best for: social posts, email voice.
- **Scarcity** — Limited time or quantity (real, ethical constraints only). Best for: ad copy, launch campaigns.
- **Unity** — Create tribe belonging, "we" identity. Best for: brand voice, community content.

The agent weaves 2-3 selected principles naturally into the copy rather than
applying all 7 generically.

**`voss-tactical-empathy`** — *Lower the reader's guard before you persuade*

Chris Voss's FBI negotiation techniques adapted for marketing copy. This skill
changes how your agent handles objections and opens conversations. Instead of
ignoring reader skepticism, the agent leads with it:
- **Accusation Audit** — Name the objection before the reader thinks it: "You're probably thinking this is just another..."
- **Labeling** — Put emotions into words in subheads and hooks: "It seems like you've tried everything and nothing sticks"
- **No-Oriented Questions** — CTAs that feel safe: "Would it be ridiculous to try this for 30 days?"
- **That's Right Moment** — Summarize the reader's situation so accurately they internally nod along

Pairs perfectly with Cialdini: Voss lowers the guard, Cialdini persuades.
Best for: landing pages, email subject lines, ad hooks, any content targeting
skeptical or burned audiences.

**`sugarman-triggers`** — *Embed psychological hooks that pull readers forward*

Joseph Sugarman's 30+ psychological triggers from The Adweek Copywriting Handbook.
Micro-level copy moves that make each sentence compel the reader to read the next
one (the "Slippery Slide" principle). When you select this skill, you also pick
WHICH triggers to emphasize:
- **Curiosity** — Open loops, incomplete patterns. Best for: email subject lines, social hooks.
- **Specificity** — Exact numbers, precise details. Best for: blog posts, ads.
- **Storytelling** — Narrative that carries the reader. Best for: email, ebooks.
- **Exclusivity** — "Not for everyone." Best for: premium positioning.
- **Urgency** — Time pressure (ethical). Best for: launch campaigns, ads.
- **Simplicity** — Make the complex feel easy. Best for: landing pages, onboarding.

Best for: social posts, email sequences, ad copy, any short-form content where
every word must earn its place.

**`marketing-psychology`** — *Apply mental models from behavioral economics*

40+ mental models (already installed from coreyhaines31/marketingskills) including
First Principles, Jobs-to-Be-Done, Mimetic Desire, Hyperbolic Discounting,
Endowment Effect, Loss Aversion, and more. This is the broadest skill — it gives
the agent a library of behavioral economics concepts to draw from. Less
prescriptive than Cialdini or Voss, more of a "think about this from multiple
angles" toolkit. Best for: strategy-heavy content, thought leadership, content
where you want the agent to find the most resonant angle rather than follow a
specific formula.

---

#### Layer 4: Copy Craft (Pick 1 Primary)

> This is the WRITING STYLE — how the final copy reads. Pick one as your primary
> voice. These are largely mutually exclusive: you can't write in Ogilvy's
> measured, fact-heavy style AND Halbert's urgent, emotional style simultaneously.
> You can optionally pick a secondary for specific sections (e.g., StoryBrand for
> the narrative intro, then Ogilvy for the body).

**`ogilvy-copywriting`** — *Fact-driven, headline-first, authoritative long copy*

David Ogilvy's advertising principles. The headline does 80% of the work — it
must promise a specific benefit, not be clever. Body copy is long, detailed, and
packed with facts, numbers, and specifics ("At 60 miles an hour, the loudest
noise comes from the electric clock"). Every claim is backed by data. The tone
is confident but never hype-y — an expert speaking to an intelligent reader.
Research before writing is mandatory. Best for: blog posts, authority content,
product reviews, ads where credibility matters more than urgency.

**`halbert-direct-response`** — *Urgent, personal, emotional, action-driving*

Gary Halbert's direct response copywriting from The Boron Letters. Write to ONE
person (not an audience) — use the focus group to pick a specific person and
write as if you're talking to them across a table. AIDA structure but make every
transition invisible. Pile on benefits, then pile on more, then add bonuses.
Every piece needs a reason to act NOW. If it doesn't sound like a conversation
when read aloud, rewrite it. Best for: sales emails, ad copy, landing pages,
flash sale campaigns, anything where the goal is immediate action.

**`storybrand-framework`** — *Hero's journey narrative: the customer is the hero*

Donald Miller's StoryBrand 7-part framework. Every piece of content follows a
narrative structure: the Customer (Hero) has a Problem, meets your Brand (Guide)
who shows Empathy and Authority, gives them a Plan, calls them to Action, helps
them avoid Failure, and leads to Success (transformation). The customer is ALWAYS
the hero — your brand is the mentor, never the protagonist. Creates emotionally
compelling content that naturally moves toward a call to action without feeling
like a sales pitch. Best for: landing pages, email sequences, ebooks, video
scripts, brand storytelling, "About Us" pages.

**`brunson-positioning`** — *Origin stories, epiphany bridges, belief reframing*

Russell Brunson's expert positioning frameworks from Expert Secrets. Content opens
with an Epiphany Bridge — the moment of discovery that changed everything. Origin
Stories follow 4 elements: backstory, wall, epiphany, plan. The 3 Secret Formula
reframes beliefs across three dimensions to break through resistance. Creates a
sense of "this person discovered something I need to know." Best for: ebook
introductions, course content, webinar scripts, personal brand content, "how I
discovered" blog posts, launch sequences.

---

#### Layer 5: Quality (Auto-Active)

> Always runs after the content agent finishes writing. Not configurable —
> these are quality standards, not creative choices.

**`humanizer`** — *Remove AI writing patterns and add authentic voice*

Detects and rewrites 24 categories of AI-generated writing patterns: inflated
significance, copula avoidance ("serves as" instead of "is"), rule-of-three
overuse, em-dash abuse, synonym cycling, promotional language, and more. Doesn't
just remove patterns — adds authentic voice with opinions, varied rhythm,
acknowledged complexity, and specific emotional language.

**`writing-clearly`** — *Tight, clear, forceful prose (Strunk's rules)*

Applies William Strunk Jr.'s composition principles: omit needless words, use
active voice, put statements in positive form, use definite/specific/concrete
language. Also catches AI-specific weaknesses: puffery words (pivotal, crucial),
empty -ing constructions, and overused vocabulary (delve, leverage, multifaceted).

---

### How Campaigns Select Skills

**Auto-active (always on, not selectable):**
- `mbook-schwarz-awareness` — derived from focus group awareness level
- `humanizer` + `writing-clearly` — always run post-writing

**Campaign-level selection (set at campaign creation, "Writing Strategy" step):**
- Layer 2: Pick 0-1 offer framework (skip for pure content campaigns)
- Layer 3: Pick 1-2 persuasion mechanics (with sub-selections for principles/triggers)
- Layer 4: Pick 1 primary copy style (optional secondary for mixed content)

**Content-type defaults (auto-suggested, one-click apply):**

When you select a content type, the dashboard pre-fills a recommended skill combo.
You can accept, modify, or start from scratch.

| Content Type | Layer 2 | Layer 3 | Layer 4 | Why This Combo |
|---|---|---|---|---|
| Blog post | — | cialdini [authority, social_proof] | ogilvy | Authority-driven, fact-heavy content that builds trust with proof |
| Landing page | hormozi-offer | voss + cialdini [scarcity, social_proof] | halbert | Value equation + objection audit + urgency = high-conversion page |
| Email sequence | — | sugarman [curiosity, urgency] + voss | halbert | Hook-driven subject lines, empathy openers, personal tone |
| Ad copy | hormozi-offer | cialdini [scarcity] | halbert | Direct response value prop with urgency |
| Ebook / lead magnet | hormozi-leads | cialdini [authority, reciprocity] | storybrand | Lead-to-customer journey with narrative structure |
| Social post | — | sugarman [curiosity, specificity] | — | Pure hook triggers, short-form, no copy style needed |
| Video script | — | voss | storybrand | Narrative structure with empathy-first approach |

**Dashboard UX — "Writing Strategy" step:**

```
Campaign Creation → Step 3: Writing Strategy

  ┌─────────────────────────────────────────────────────────────┐
  │ AWARENESS TARGETING (auto-detected from your focus groups)  │
  │                                                             │
  │ Focus Group #1 "Fat Loss Seekers"  → ● Problem Aware       │
  │ Focus Group #5 "Plateau Breakers"  → ● Solution Aware      │
  │                                                             │
  │ Your agents will automatically adjust headline formulas,    │
  │ opening strategies, and CTA styles per awareness stage.     │
  └─────────────────────────────────────────────────────────────┘

  ┌─ Offer Framework (pick 0-1) ────────────────────────────────┐
  │                                                              │
  │ ☑ Hormozi Value Equation                                     │
  │   Make offers irresistible using the value equation.         │
  │                                                              │
  │ ☐ Hormozi Lead Magnets                                       │
  │   Structure content as a give-to-ask lead gen pipeline.      │
  │                                                              │
  │ ☐ Brunson Funnels                                            │
  │   Position content within a multi-step funnel journey.       │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  ┌─ Persuasion Mechanics (pick 1-2) ───────────────────────────┐
  │                                                              │
  │ ☑ Cialdini Persuasion                                        │
  │   Apply proven influence principles.                         │
  │   Sub-select: ☑ Social Proof  ☑ Authority  ☐ Scarcity       │
  │               ☐ Reciprocity   ☐ Commitment ☐ Liking ☐ Unity │
  │                                                              │
  │ ☑ Voss Tactical Empathy                                      │
  │   Lead with objections, name emotions, lower the guard.      │
  │                                                              │
  │ ☐ Sugarman Triggers                                          │
  │   Embed psychological hooks that pull readers forward.        │
  │   Sub-select: ☐ Curiosity ☐ Specificity ☐ Urgency           │
  │               ☐ Storytelling ☐ Exclusivity ☐ Simplicity      │
  │                                                              │
  │ ☐ Marketing Psychology                                       │
  │   Broad behavioral economics mental models.                  │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  ┌─ Copy Style (pick 1 primary) ───────────────────────────────┐
  │                                                              │
  │ ◉ Ogilvy — Fact-driven, headline-first, authoritative       │
  │   Specific benefits, data-backed claims, expert tone.        │
  │                                                              │
  │ ○ Halbert — Urgent, personal, emotional, action-driving     │
  │   Write to one person, pile on benefits, act NOW.            │
  │                                                              │
  │ ○ StoryBrand — Hero's journey, customer is the hero         │
  │   Narrative structure: problem → guide → plan → success.     │
  │                                                              │
  │ ○ Brunson — Origin stories, epiphany bridges                │
  │   Discovery narratives that reframe beliefs.                 │
  │                                                              │
  │ Optional secondary: [None ▾]                                 │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  [Apply defaults for: Blog Post ▾]  [Reset All]  [Advanced ▾]
```

**Real examples showing typical skill loads (2-4 skills, not 11):**

Example 1 — "GymZilla Summer Shred Blog Series":
```
Layer 1: mbook-schwarz-awareness = Problem Aware        ← auto
Layer 2: (none)                                     ← blog posts, no direct offer
Layer 3: cialdini [authority, social_proof]          ← 1 skill, 2 principles
Layer 4: ogilvy-copywriting                         ← primary style
Layer 5: humanizer + writing-clearly                ← auto
Total skills loaded by agent: 4 (schwartz + cialdini + ogilvy + humanizer/writing)
```

Example 2 — "GymZilla Black Friday Landing Page":
```
Layer 1: mbook-schwarz-awareness = Product Aware         ← auto
Layer 2: hormozi-offer                              ← value equation for the offer
Layer 3: voss-tactical-empathy + cialdini [scarcity] ← 2 skills
Layer 4: halbert-direct-response                    ← urgent, direct style
Layer 5: humanizer + writing-clearly                ← auto
Total skills loaded by agent: 6 (schwartz + hormozi + voss + cialdini + halbert + humanizer/writing)
```

Example 3 — "Photo Prints Valentine's Day Email Sequence":
```
Layer 1: mbook-schwarz-awareness = Solution Aware        ← auto
Layer 2: (none)                                     ← nurture emails, not selling yet
Layer 3: sugarman [curiosity, storytelling]          ← 1 skill, 2 triggers
Layer 4: storybrand-framework                       ← narrative emails
Layer 5: humanizer + writing-clearly                ← auto
Total skills loaded by agent: 4 (schwartz + sugarman + storybrand + humanizer/writing)
```

The agent reads the campaign's skill selection and loads those skills before writing.

---

## Tier 1 — Must Have (Core Pipeline Skills)

### 1. Breakthrough Advertising — Eugene M. Schwartz

- **Amazon:** https://www.amazon.com/Breakthrough-Advertising-Eugene-M-Schwartz/dp/0887232981
- **Skill name:** `mbook-schwarz-awareness`
- **Layer:** 1 (Audience Understanding) — always auto-active
- **Invoked by:** All content agents, auto-derived from focus group data

**Core Framework — 5 Stages of Market Awareness:**

| Stage | Reader Knows | Copy Approach |
|---|---|---|
| Most Aware | Your product, ready to buy | Lead with offer/deal, minimal persuasion |
| Product Aware | Your product exists, unsure | Differentiate, prove superiority |
| Solution Aware | Solutions exist, not yours | Position your solution as best fit |
| Problem Aware | Has the pain, no solutions | Agitate the problem, introduce solution |
| Unaware | Doesn't know they have a problem | Lead with story/emotion, reveal the problem |

**Platform integration:**
- Content agents check awareness stage BEFORE choosing copy approach
- Different headline formulas per stage, different opening strategies, different CTA styles
- This is the single most impactful skill — it determines everything else

**Sources:**
- Book itself is the primary source (out of print, expensive, but the framework is well-documented)

---

#### Auto-Detection: Deriving Awareness Stage from Focus Group Data

The awareness stage is **not a manual field**. It's automatically classified from
three fields that already exist in every focus group profile: `beliefs`,
`objections`, and `languagePatterns`. The classification runs when a focus group
is created or updated, and the result is stored as a computed field that humans
can override in the dashboard.

**Why these three fields?** They reveal what the person already knows:
- **Beliefs** show what framework they're operating in (problem-level thinking vs. solution-level thinking)
- **Objections** show what they're comparing against (nothing vs. other solutions vs. your product)
- **Language patterns** show what questions they're asking (vague vs. specific vs. product-named)

**Classification Rules:**

The classifier scans three fields and matches against universal patterns.
These work for ANY niche — fitness, SaaS, ecommerce, education, anything.

**Unaware** — Doesn't know they have a problem
```
Signals:
  beliefs:    Focus on identity, not problems
              ("I'm just not a [type] person", "That's not for people like me")
  objections: About the CATEGORY itself
              ("Do I even need this?", "I'm fine as I am")
  language:   No niche-specific vocabulary, general life dissatisfaction,
              no mention of solutions or methods

Copy approach: Lead with story or emotion that reveals a problem they didn't
know they had. Never open with the solution — they don't know they need one.
```

**Problem Aware** — Feels the pain, doesn't know solutions exist
```
Signals:
  beliefs:    Focus on the PROBLEM itself
              ("Something is wrong", "If I could just fix [pain], everything
              would be better", "I deserve better than this")
  objections: About FEASIBILITY
              ("Is it too late for me?", "Can I really...?",
              "I don't know where to start", "What if I fail?")
  language:   Questions about the problem, NOT about solutions or methods
              ("I want to feel [desired state]", "I don't know what to do",
              "Where do I even start?", emotional/identity language)

Copy approach: Agitate the problem, validate their pain, then introduce the
concept that solutions exist. Lead with empathy, not methods.
```

**Solution Aware** — Knows solutions exist, hasn't found the right one
```
Signals:
  beliefs:    Reference SOLUTIONS and methods by name or concept
              ("I've tried [method] and it didn't work",
              "The right approach should give results",
              "Maybe I need to change my strategy")
  objections: About DIFFERENTIATION
              ("I've already tried [similar thing]", "How is this different?",
              "I've been doing [method] and it's not working",
              "Why should I trust this over what I'm already doing?")
  language:   References past attempts, specific methods, frustration with
              approaches that didn't work
              ("I've tried everything", "Nothing works",
              "I've been doing this for months with no results")

Copy approach: Position your solution as the one that works where others
failed. Acknowledge what they've tried. Differentiate on mechanism/approach.
```

**Product Aware** — Knows your product, not sure it's right for them
```
Signals:
  beliefs:    Reference YOUR PRODUCT or brand by name
  objections: About YOUR SPECIFIC OFFERING
              ("Is [your product] worth it?", "Why [your product] over
              [competitor]?", "Does this cover my specific situation?")
  language:   Uses your product/brand name, compares features,
              asks about specifics, pricing, guarantees

  Note: Rarely present in focus group profiles since those describe market
  segments, not existing customers. Identified from behavioral data:
  - Website analytics (returning visitors, pricing page views)
  - Email subscribers who haven't purchased
  - People mentioning your product on social media

Copy approach: Prove superiority, address product-specific doubts, show
social proof from similar customers, remove risk with guarantees.
```

**Most Aware** — Knows your product, ready to buy, just needs the push
```
Signals:
  beliefs:    Already trust the product/brand
  objections: About PRICE or TIMING only
              ("Is it worth the money?", "Should I start now or wait?",
              "Is there a discount coming?")
  language:   Decision language, not research language
              ("Should I buy?", "Is there a deal?", "When does it launch?")

  Note: Almost never present in focus group profiles. Identified from:
  - Cart abandoners
  - Pricing page visitors
  - People who've consumed lots of free content
  - Past customers considering upsells

Copy approach: Lead with the offer. Minimal persuasion needed — just give
them the deal, the guarantee, and the CTA. Don't over-explain.
```

**Confidence scoring:**

| Condition | Confidence |
|---|---|
| All 3 fields (beliefs + objections + language) point to same stage | High |
| 2 of 3 fields agree, 1 is ambiguous | Medium |
| Fields point to different stages (e.g., beliefs = Problem, objections = Solution) | Low — flag for human review |
| Insufficient data in one or more fields | Low — flag for enrichment |

When confidence is Low, the dashboard highlights the focus group with a
"Needs Review" badge and shows the conflicting signals.

**Implementation:**

```typescript
// Convex schema addition to focusGroups table:
awarenessStage: v.union(
  v.literal("unaware"),
  v.literal("problem_aware"),
  v.literal("solution_aware"),
  v.literal("product_aware"),
  v.literal("most_aware"),
),
awarenessStageSource: v.union(
  v.literal("auto"),       // Classified by mbook-schwarz-awareness skill
  v.literal("manual"),     // Human override in dashboard
),
awarenessSignals: v.optional(v.object({
  beliefSignals: v.array(v.string()),    // Which beliefs triggered classification
  objectionSignals: v.array(v.string()), // Which objections triggered it
  languageSignals: v.array(v.string()),  // Which language patterns triggered it
  confidence: v.union(v.literal("high"), v.literal("medium"), v.literal("low")),
})),
```

**Dashboard display:**

```
Focus Group: [Name]
Awareness Stage: ● [Stage] (auto-detected, [confidence])  [Override ▾]

Signals used:
  Beliefs: "[matched belief]"
  Objections: "[matched objection]", "[matched objection]"
  Language: "[matched pattern]", "[matched pattern]"
```

The human can click [Override] to change the stage. The override is stored as
`awarenessStageSource: "manual"` and won't be re-classified on future updates
unless the human resets it to auto.

The human can click [Override] to change the stage if they disagree. The override
is stored as `awarenessStageSource: "manual"` and won't be re-classified on
future updates unless the human resets it to auto.

---

#### Focus Group Schema Enhancements

Beyond awareness stage, focus groups should capture richer data to give content
agents more context. These fields extend the base focus group template.

**8 New Fields — What Agents Need to Write Better Copy:**

| Field | Type | Description | Which Agents Use It |
|---|---|---|---|
| `contentPreferences` | `object` | What content formats and lengths this segment actually consumes. Fields: `preferredFormats` (array: "short_video", "long_article", "podcast", "infographic", "email", "carousel"), `attentionSpan` ("quick_scan", "medium_read", "deep_dive"), `tonePreference` ("casual", "professional", "motivational", "data_driven"). | `vibe-content-writer`, `vibe-social-writer` — determines format, length, and voice |
| `platformHabits` | `object` | Where this segment spends time online and when. Fields: `primaryPlatforms` (array: "instagram", "youtube", "tiktok", "linkedin", "facebook", "reddit", "email", "podcast_apps"), `peakEngagementTimes` (array of day-part strings like "weekday_morning", "weekend_evening"), `contentDiscovery` ("algorithm_feed", "search", "peer_recommendation", "influencer"). | `vibe-social-writer`, `vibe-ad-writer` — determines platform-specific copy and posting strategy |
| `influenceSources` | `object` | Who and what influences this segment's decisions. Fields: `trustedVoices` (array of strings — types, not names: "fitness_youtubers", "reddit_communities", "doctors", "friends"), `decisionDrivers` (array: "peer_reviews", "expert_opinion", "data_evidence", "personal_experience", "celebrity_endorsement"), `skepticismLevel` ("low", "medium", "high"). | `vibe-content-writer`, `vibe-ad-writer` — informs authority positioning and social proof strategy |
| `competitorAwareness` | `object` | What alternatives this segment has tried or knows about. Fields: `knownAlternatives` (array of strings — generic categories, not brand names: "gym_memberships", "home_workout_apps", "personal_trainers"), `pastExperiences` (array of objects: `{ category, outcome, sentiment }`), `switchingBarriers` (array: "cost", "habit", "contracts", "social_ties", "skepticism"). | `vibe-landing-page-writer`, `vibe-ad-writer` — powers differentiation copy and objection handling |
| `buyingProcess` | `object` | How this segment makes purchase decisions. Fields: `decisionSpeed` ("impulse", "considered", "extended_research"), `stakeholders` (array: "self_only", "partner", "family", "peer_group"), `researchBehavior` ("reads_reviews", "asks_friends", "tries_free_first", "compares_prices", "needs_guarantee"), `priceAnchor` ("budget_conscious", "value_seeker", "premium_willing", "price_insensitive"). | `vibe-landing-page-writer`, `vibe-email-writer` — shapes CTA urgency, guarantee framing, and funnel length |
| `priceSensitivity` | `object` | How price factors into this segment's decisions. Fields: `range` ("free_only", "low_ticket", "mid_range", "premium", "enterprise"), `valuePerception` ("cheapest_wins", "roi_focused", "quality_first", "prestige_matters"), `dealTriggers` (array: "discount", "bundle", "guarantee", "payment_plan", "free_trial"). | `vibe-landing-page-writer`, `vibe-ad-writer` — determines pricing language, discount strategy, guarantee positioning |
| `timeHorizon` | `object` | How quickly this segment expects results and how long they'll commit. Fields: `expectedResults` ("immediate", "weeks", "months", "long_term"), `commitmentWindow` ("one_time", "short_term", "ongoing", "seasonal"), `patienceLevel` ("wants_instant", "willing_to_wait", "marathon_mindset"). | `vibe-email-writer`, `vibe-content-writer` — sets expectation framing and drip sequence pacing |
| `seasonalTriggers` | `object` | When this segment is most receptive to messaging. Fields: `peakMotivation` (array: "new_year", "summer_prep", "back_to_school", "holiday", "post_holiday", "birthday_milestone"), `lifeMoments` (array: "career_change", "new_parent", "health_scare", "breakup", "retirement", "moving"), `externalTriggers` (array: "viral_trend", "news_event", "competitor_failure", "seasonal_sale"). | `vibe-content-writer`, `vibe-ad-writer`, `vibe-email-writer` — powers campaign timing, urgency hooks, and seasonal angles |

**Convex schema for new fields:**

```typescript
// Add to focusGroups table:
contentPreferences: v.optional(v.object({
  preferredFormats: v.array(v.string()),
  attentionSpan: v.string(),
  tonePreference: v.string(),
})),
platformHabits: v.optional(v.object({
  primaryPlatforms: v.array(v.string()),
  peakEngagementTimes: v.array(v.string()),
  contentDiscovery: v.string(),
})),
influenceSources: v.optional(v.object({
  trustedVoices: v.array(v.string()),
  decisionDrivers: v.array(v.string()),
  skepticismLevel: v.string(),
})),
competitorAwareness: v.optional(v.object({
  knownAlternatives: v.array(v.string()),
  pastExperiences: v.array(v.object({
    category: v.string(),
    outcome: v.string(),
    sentiment: v.string(),
  })),
  switchingBarriers: v.array(v.string()),
})),
buyingProcess: v.optional(v.object({
  decisionSpeed: v.string(),
  stakeholders: v.array(v.string()),
  researchBehavior: v.string(),
  priceAnchor: v.string(),
})),
priceSensitivity: v.optional(v.object({
  range: v.string(),
  valuePerception: v.string(),
  dealTriggers: v.array(v.string()),
})),
timeHorizon: v.optional(v.object({
  expectedResults: v.string(),
  commitmentWindow: v.string(),
  patienceLevel: v.string(),
})),
seasonalTriggers: v.optional(v.object({
  peakMotivation: v.array(v.string()),
  lifeMoments: v.array(v.string()),
  externalTriggers: v.array(v.string()),
})),
```

---

#### Focus Group Enrichment Log

Focus groups are **living profiles** — they get richer over time as agents research,
campaigns run, and humans add context. The enrichment log tracks every addition
with provenance so you can see what was added, when, by whom, and why.

**Why append-only?** Enrichments never overwrite each other. An agent might add
social media research today, and a human might add interview insights next week.
Both entries stay in the log with full attribution. If data conflicts, the most
recent entry with the highest confidence wins — but old entries remain for audit.

**Schema:**

```typescript
// Add to focusGroups table:

// Structured enrichment log (append-only, timestamped)
enrichments: v.optional(v.array(v.object({
  timestamp: v.string(),         // ISO 8601
  source: v.union(
    v.literal("agent"),          // Added by a vibe-marketing agent
    v.literal("human"),          // Added manually in dashboard
    v.literal("import"),         // Bulk import from external data
    v.literal("campaign_feedback"), // Derived from campaign performance
  ),
  agentId: v.optional(v.string()),   // Which agent added this (if source=agent)
  userId: v.optional(v.string()),    // Which user added this (if source=human)
  campaignId: v.optional(v.string()),// Which campaign (if source=campaign_feedback)
  field: v.string(),                 // Which field was enriched ("beliefs", "contentPreferences", etc.)
  previousValue: v.optional(v.any()),// What the field was before (for change tracking)
  newValue: v.any(),                 // What was added/changed
  confidence: v.union(
    v.literal("high"),
    v.literal("medium"),
    v.literal("low"),
  ),
  reasoning: v.string(),            // Why this enrichment was made
}))),

// Free-text research notes (human-written context that doesn't fit structured fields)
researchNotes: v.optional(v.string()),
```

**Dashboard display:**

```
Focus Group: [Name]

📋 Enrichment History (3 entries)
─────────────────────────────────────────
  2025-06-15  agent (vibe-research-agent)
  Field: influenceSources
  Added: trustedVoices = ["reddit_communities", "youtube_reviewers"]
  Confidence: medium
  Reason: "Scraped r/fitness and cross-referenced with YouTube comment sentiment"

  2025-06-18  human (jane@company.com)
  Field: competitorAwareness
  Added: knownAlternatives = ["peloton", "crossfit_boxes"]
  Confidence: high
  Reason: "From customer interview batch #3 — 8 of 12 mentioned these"

  2025-07-01  campaign_feedback (campaign:summer-shred-2025)
  Field: contentPreferences.attentionSpan
  Changed: "medium_read" → "quick_scan"
  Confidence: medium
  Reason: "Blog posts had 23% bounce rate, short-form video had 4x engagement"

Research Notes:
  "This group skews younger (22-28) and is heavily influenced by TikTok
   fitness creators. They distrust traditional advertising but respond well
   to 'day in my life' content formats. Interview subjects mentioned they
   feel 'talked down to' by most fitness brands."
```

**How agents use enrichments:**

Content agents don't read the full enrichment log. Instead:
1. The system resolves the latest value for each field (most recent + highest confidence wins)
2. Agents receive the resolved focus group profile with all fields populated
3. If an agent needs provenance (e.g., to cite a source), it can query the enrichment log
4. The `researchNotes` field is included in the agent's context as free-text background

---

### 2. $100M Offers — Alex Hormozi

- **Amazon:** https://www.amazon.com/100M-Offers-People-Refuse-Making/dp/1737475731
- **Skill name:** `hormozi-offer`
- **Layer:** 2 (Offer Structure)
- **Invoked by:** `vibe-landing-page-writer`, `vibe-ad-writer`, `vibe-email-writer`, `vibe-content-writer`

**Core Frameworks:**
- **Value Equation:** Dream Outcome × Perceived Likelihood of Achievement / Time Delay × Effort & Sacrifice
- **Grand Slam Offer:** Stack so much value the price becomes irrelevant
- **Bonuses & Guarantees:** Risk reversal mechanics
- **Scarcity & Urgency:** Ethical urgency (cohort-based, real limits)
- **Naming:** How to name offers for maximum perceived value

**Platform integration:**
- When writing landing pages or ads, agent applies value equation to every section
- Focus group `coreDesires` = Dream Outcome, `objections` = Perceived Likelihood barriers
- `transformationPromise` maps directly to the before/after of the value equation
- Guides how agents frame pricing, bonuses, and guarantees in copy

---

### 3. $100M Leads — Alex Hormozi

- **Amazon:** https://www.amazon.com/100M-Leads-Strangers-Want-Stuff/dp/1737475774
- **Skill name:** `hormozi-leads`
- **Layer:** 2 (Offer Structure)
- **Invoked by:** `vibe-email-writer`, `vibe-landing-page-writer`, `vibe-ebook-writer`, `vibe-content-writer`

**Core Frameworks:**
- **Lead Magnet Design:** 7 steps to create lead magnets that convert
- **Content-to-Lead Pipeline:** Free content → engaged audience → lead → customer
- **Core 4 Advertising Methods:** Warm outreach, cold outreach, content, paid ads
- **Give-to-Ask Ratio:** How much free value before the ask
- **Lead Magnet Types:** Checklists, templates, trials, tools, courses, assessments

**Platform integration:**
- Powers the "Launch Package" pipeline's lead magnet creation
- `vibe-ebook-writer` uses this to structure ebooks as lead magnets (not just content)
- Email sequences use the give-to-ask ratio framework
- Guides content strategy: which blog posts are top-of-funnel lead generation vs. nurture

---

### 4. Influence — Robert Cialdini

- **Amazon:** https://www.amazon.com/Influence-New-Expanded-Psychology-Persuasion/dp/0062937650
- **Skill name:** `cialdini-persuasion`
- **Layer:** 3 (Persuasion Mechanics)
- **Invoked by:** All content agents (when selected for campaign)

**Core Framework — 7 Principles:**

| Principle | Copy Application | Agent Use |
|---|---|---|
| Reciprocity | Give value first (free content, tools) | Blog intros, lead magnets |
| Commitment/Consistency | Small yeses → big yes | Email sequences, multi-step funnels |
| Social Proof | Testimonials, numbers, case studies | Landing pages, ads |
| Authority | Expert positioning, credentials, data | Blog posts, ebooks |
| Liking | Relatability, shared identity, humor | Social posts, email voice |
| Scarcity | Limited time/quantity (ethical) | Ad copy, landing pages |
| Unity | "We" identity, tribe belonging | Brand voice, community content |

**Platform integration:**
- Agent checks campaign's selected Cialdini principles
- Each content type has natural principle affinities (landing pages lean on scarcity + social proof)
- Focus group `emotionalTriggers` map to specific principles
- Can specify primary principle per campaign: "This campaign leads with Authority + Social Proof"

---

## Tier 2 — High Value (Copy Sharpeners)

### 5. Never Split the Difference — Chris Voss

- **Amazon:** https://www.amazon.com/Never-Split-Difference-Negotiating-Depended/dp/0062407805
- **Skill name:** `voss-tactical-empathy`
- **Layer:** 3 (Persuasion Mechanics)
- **Invoked by:** `vibe-ad-writer`, `vibe-landing-page-writer`, `vibe-email-writer`, `vibe-content-writer`

**Core Techniques for Marketing:**

| Technique | Marketing Application | Example |
|---|---|---|
| Accusation Audit | Lead with the reader's objection before they think it | "You're probably thinking this is just another supplement scam..." |
| Labeling | Name the reader's emotion in subheads/hooks | "It seems like you've tried everything and nothing sticks" |
| Mirroring | Use reader's exact language (from `languagePatterns`) | Headlines using phrases from Reddit/reviews |
| No-Oriented Questions | CTAs that invite "no" to reduce resistance | "Would it be ridiculous to try this for 30 days?" |
| Tactical Empathy | Opening copy that demonstrates you GET IT | Show you understand before you pitch |
| Late-Night FM DJ Voice | Tone calibration — calm authority vs hype | Brand voice tone enforcement |
| That's Right | Get the reader to internally say "that's right" | Summarize their situation so accurately they nod along |

**Platform integration:**
- Focus group `objections` feed directly into Accusation Audits
- Focus group `languagePatterns` are mirroring data
- Particularly powerful for: landing pages, email subject lines, ad hooks
- Pairs perfectly with Cialdini (Voss = lower the guard, Cialdini = persuade)

**Sources:**
- [5 Chris Voss Techniques for Marketing Copy — Richard Batt](https://richardbatt.co.uk/2023/03/10/5-chris-voss-negotiation-techniques-from-never-split-the-difference-to-improve-your-marketing-copy/)
- [10 Things from Never Split the Difference — Goldmine Marketing](https://goldmine.marketing/10-things-youll-learn-from-never-split-the-difference-by-chris-voss/)
- [Chris Voss Tactics for B2B — Renegade Marketing](https://renegademarketing.com/blog/never-split-the-difference-chris-voss-essential-negotiation-tactics-for-b2b-leaders/)
- [Field-Tested Negotiation — Marketing Speak](https://www.marketingspeak.com/a-field-tested-approach-to-negotiation-with-chris-voss/)

---

### 6. Building a StoryBrand — Donald Miller

- **Amazon:** https://www.amazon.com/Building-StoryBrand-Clarify-Message-Customers/dp/0718033329
- **Skill name:** `storybrand-framework`
- **Layer:** 4 (Copy Craft)
- **Invoked by:** `vibe-landing-page-writer`, `vibe-email-writer`, `vibe-ebook-writer`, `vibe-script-writer`

**Core Framework — 7-Part Story:**

| Element | Role | Copy Element |
|---|---|---|
| Hero | The customer (NOT you) | "You" language throughout |
| Problem | External, internal, philosophical | Pain points from focus groups |
| Guide | Your brand (authority + empathy) | Position as the mentor |
| Plan | Clear steps (3-step plan) | "Here's how it works: 1, 2, 3" |
| Call to Action | Direct + transitional | "Start now" + "Download free guide" |
| Failure | What happens if they don't act | Stakes, consequences |
| Success | The transformation | `transformationPromise` from focus group |

**Platform integration:**
- Primary framework for landing pages and email sequences
- Every landing page follows: Hero → Problem → Guide → Plan → CTA → Failure → Success
- Video scripts use this as narrative backbone
- Maps perfectly to focus group data: painPoints=Problem, transformationPromise=Success

---

### 7. Ogilvy on Advertising — David Ogilvy

- **Amazon:** https://www.amazon.com/Ogilvy-Advertising-David/dp/039472903X
- **Skill name:** `ogilvy-copywriting`
- **Layer:** 4 (Copy Craft)
- **Invoked by:** `vibe-content-writer`, `vibe-ad-writer`, `vibe-content-reviewer`

**Core Principles:**
- **Headline is 80% of the ad** — 5x more people read the headline than body
- **Specificity over cleverness** — "At 60 miles an hour, the loudest noise comes from the electric clock"
- **Long copy sells** — People who read past the headline are prospects; give them everything
- **Research before writing** — Know the product cold before typing a word
- **Promise a benefit in the headline** — Not features, not cleverness
- **Facts over adjectives** — Data, numbers, specifics beat vague claims
- **Don't be boring** — You can't bore someone into buying

**Platform integration:**
- Default copy craft skill for blog posts and ads
- `vibe-content-reviewer` uses Ogilvy principles as quality checklist
- Headline generation follows Ogilvy formulas
- Pairs with: Cialdini (authority principle), Schwartz (awareness-appropriate specificity)

---

### 8. The Adweek Copywriting Handbook — Joseph Sugarman

- **Amazon:** https://www.amazon.com/Adweek-Copywriting-Handbook-Advertising-Copywriter/dp/0470051248
- **Skill name:** `sugarman-triggers`
- **Layer:** 3 (Persuasion Mechanics)
- **Invoked by:** `vibe-content-writer`, `vibe-email-writer`, `vibe-social-writer`, `vibe-ad-writer`

**Core Framework — 30+ Psychological Triggers:**
- Curiosity, Specificity, Storytelling, Authority, Proof of Value
- Sense of Urgency, Exclusivity, Simplicity, Human Connection
- Guilt, Greed, Desire to Belong, Desire to Collect
- The "Slippery Slide" — every line's job is to make you read the next line

**Platform integration:**
- Trigger selection per content type (email → curiosity + urgency, blog → authority + specificity)
- The "Slippery Slide" principle = quality metric for content reviewer
- Social posts especially benefit from trigger-based hooks
- Complementary to Cialdini (Sugarman = micro-copy triggers, Cialdini = macro persuasion)

---

## Tier 3 — Specialist (Deep Cuts)

### 9. DotCom Secrets — Russell Brunson

- **Amazon:** https://www.amazon.com/DotCom-Secrets-Underground-Playbook-Growing/dp/1401960464
- **Skill name:** `brunson-funnels`
- **Layer:** 2 (Offer Structure)
- **Invoked by:** `vibe-landing-page-writer`, `vibe-email-writer` (when funnel campaign)

**Core Frameworks:**
- Value Ladder (free → low-ticket → mid → high-ticket)
- Soap Opera Email Sequence (5-email story arc)
- Seinfeld Email Sequence (daily entertainment + value)
- Hook → Story → Offer framework
- Attractive Character (4 identity types)

**Platform integration:**
- Useful when campaigns involve multi-step funnels
- Soap Opera sequence → `vibe-email-writer` for launch campaigns
- Hook → Story → Offer → social media and ad frameworks
- Future: when funnel-building features are added to the platform

---

### 10. Expert Secrets — Russell Brunson

- **Amazon:** https://www.amazon.com/Expert-Secrets-Underground-Playbook-Creating/dp/1401970605
- **Skill name:** `brunson-positioning`
- **Layer:** 4 (Copy Craft)
- **Invoked by:** `vibe-ebook-writer`, `vibe-landing-page-writer`, `vibe-script-writer`

**Core Frameworks:**
- Epiphany Bridge — share the moment you discovered the truth
- Origin Story — 4 elements (backstory, wall, epiphany, plan)
- 3 Secret Formula — reframe beliefs across 3 dimensions
- Perfect Webinar Framework
- Stack Slide — offer presentation structure

**Platform integration:**
- Ebook introductions use epiphany bridge
- Landing page "About" sections use origin story
- Video scripts use the 3 Secret formula
- Pairs with StoryBrand for narrative-heavy content

---

### 11. The Boron Letters — Gary Halbert

- **Amazon:** https://www.amazon.com/Boron-Letters-Gary-C-Halbert/dp/1484825985
- **Skill name:** `halbert-direct-response`
- **Layer:** 4 (Copy Craft)
- **Invoked by:** `vibe-ad-writer`, `vibe-email-writer`, `vibe-landing-page-writer`

**Core Principles:**
- **AIDA mastery** — Attention, Interest, Desire, Action (but make each transition invisible)
- **List selection > copy** — The best copy to the wrong list = failure
- **Write to ONE person** — Not "Dear customer" but "Dear [specific person from focus group]"
- **Pile on the benefits** — Then pile on more. Then add bonuses.
- **Urgency is oxygen** — Every piece needs a reason to act NOW
- **Read it aloud** — If it doesn't sound like a conversation, rewrite it

**Platform integration:**
- High-urgency campaigns (flash sales, limited launches)
- Direct response email sequences
- The "write to ONE person" principle maps to focus group targeting
- `vibe-content-reviewer` uses "read aloud" as quality check heuristic

---

## Skill Invocation Summary

### Always Active (not selectable)
```
mbook-schwarz-awareness     — Auto-derived from focus group awarenessStage
humanizer              — Post-writing AI pattern removal
writing-clearly        — Post-writing prose cleanup
```

### Campaign-Level Selection (checkbox grid at campaign creation)
```
Layer 2 — Offer Structure:
  hormozi-offer          — Value equation framing
  hormozi-leads          — Lead magnet / content-to-lead
  brunson-funnels        — Funnel stage positioning

Layer 3 — Persuasion Mechanics:
  cialdini-persuasion    — Principle selection (can pick specific principles)
  voss-tactical-empathy  — Accusation audit, labeling, no-oriented questions
  sugarman-triggers      — Psychological trigger selection
  marketing-psychology   — Mental model activation (already installed)

Layer 4 — Copy Craft (primary + optional secondary):
  ogilvy-copywriting     — Headline-first, proof-heavy, long copy
  halbert-direct-response — Urgent, personal, emotional, AIDA
  storybrand-framework   — Hero's journey, 7-part narrative
  brunson-positioning    — Epiphany bridge, origin story
```

### Convex Schema Addition
```typescript
// Add to campaigns table:
skillConfig: v.optional(v.object({
  offerFrameworks: v.array(v.string()),      // ["hormozi-offer"]
  persuasionStack: v.array(v.string()),      // ["cialdini-persuasion", "voss-tactical-empathy"]
  primaryCopyStyle: v.string(),              // "ogilvy-copywriting"
  secondaryCopyStyle: v.optional(v.string()),// "storybrand-framework"
  cialdiniPrinciples: v.optional(v.array(v.string())), // ["social_proof", "authority"]
  sugarmanTriggers: v.optional(v.array(v.string())),   // ["curiosity", "specificity"]
})),
```

### Agent Loading Pattern
```markdown
# In any content agent's execution:
1. Load campaign skillConfig
2. For each skill in offerFrameworks + persuasionStack + primaryCopyStyle:
   - Read .claude/skills/{skill-name}/SKILL.md
3. Apply in layer order: awareness → offer → persuasion → craft
4. Write content
5. Post-processing: humanizer → writing-clearly
```
