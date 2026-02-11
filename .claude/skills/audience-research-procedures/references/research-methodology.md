# Research Methodology

Step-by-step protocol for the vibe-audience-researcher agent. Follow these phases in order. Do not skip phases -- each builds on the previous.

---

## Phase 1: Product Context Analysis (5 minutes)

**Goal:** Deeply understand what is being sold and to whom the company thinks they are selling.

1. Load product record from Convex
2. Read all product context fields:
   - `whatItIs` -- what the product actually does
   - `features` -- feature list (reveals what the company values)
   - `pricing` -- price point (critical for income segmentation)
   - `usps` -- how they differentiate (reveals assumed audience values)
   - `targetMarket` -- stated target (often too broad, but a starting point)
   - `website` -- for additional context
   - `competitors` -- named competitors
3. Note gaps in understanding -- these become search queries
4. Check for existing focus groups on this product
5. Load brand voice -- this tells you HOW they want to speak, which reveals assumed audience

**Output:** A mental model of the product and its market position. List of specific questions to answer through research.

## Phase 2: Competitor Research (10 minutes)

**Goal:** Understand the competitive landscape and how competitors position to their audiences.

1. For each named competitor (and any discovered through search):
   - Scrape their homepage and key landing pages
   - Extract: headlines, value props, testimonials, pricing tiers
   - Note: who they speak to (audience signals in copy)
   - Note: what problems they claim to solve
   - Note: what objections they address (FAQs, guarantees)
2. Search for competitor comparisons:
   - `"{competitor1} vs {competitor2}"`
   - `"alternatives to {competitor1}"`
   - `"{competitor1} review"`
3. Map the competitor landscape:
   - Who targets beginners vs. advanced?
   - Who targets budget vs. premium?
   - Where are the positioning gaps?

**Output:** Competitive landscape map with audience targeting patterns.

## Phase 3: Forum and Reddit Research (10 minutes)

**Goal:** Mine real human language, unfiltered emotions, and authentic pain points.

1. Identify relevant subreddits and forums
2. Search for problem-expression posts:
   - "help with [problem]"
   - "struggling with [challenge]"
   - "frustrated by [issue]"
   - "looking for [solution]"
3. Search for identity-expression posts:
   - "as a [identity], I..."
   - "anyone else who [description]?"
4. Search for purchase-decision posts:
   - "is [product/category] worth it?"
   - "thinking about [action]"
   - "has anyone tried [solution]?"
5. For each relevant post:
   - Record the EXACT language used
   - Note emotional intensity (mild frustration vs. desperation)
   - Note demographic signals (age, gender, situation mentions)
   - Read top comments for additional perspectives

**Output:** Language bank with attributed quotes, organized by theme.

## Phase 4: Review Analysis (5 minutes)

**Goal:** Extract satisfaction themes, complaint themes, and buyer language from reviews.

1. Search for reviews of the product and competitors on:
   - G2 / Capterra (SaaS products)
   - Trustpilot (general products)
   - Amazon (physical products)
   - App Store / Google Play (mobile products)
   - Industry-specific review sites
2. Categorize reviews:
   - 5-star: What delighted them? What language do happy customers use?
   - 3-star: What was missing? What almost worked? (reveals unmet needs)
   - 1-star: What went wrong? What were expectations? (reveals awareness gaps)
3. Extract:
   - Direct quotes (becomes language patterns)
   - Recurring complaints (becomes pain points)
   - Demographic mentions (enriches segments)
   - Feature requests (reveals unmet desires)

**Output:** Categorized review excerpts with extracted themes.

## Phase 5: Segmentation (10 minutes)

**Goal:** Transform raw research into distinct, non-overlapping audience segments.

1. Spread all findings in front of you (metaphorically)
2. Look for natural clusters:
   - Who wants the SAME outcome but for DIFFERENT reasons?
   - Who faces the SAME problem but in DIFFERENT contexts?
   - Who uses DIFFERENT language to describe SIMILAR needs?
3. Test each proposed segment:
   - Would a message to Segment A feel wrong to Segment B?
   - Does each segment have unique language?
   - Does each segment have unique objections?
4. Group segments into 4-6 categories
5. Assign awareness levels (Schwartz model)
6. Assign sophistication levels
7. Number and name each group
8. Write a 1-line distinctness statement for each: "This group is different because..."

**Output:** Finalized list of 15-30 segments with names, nicknames, categories, and awareness levels.

## Phase 6: Profile Generation (15 minutes per batch of 5)

**Goal:** Build deep, research-backed profiles for each segment.

For each group:
1. Write the overview (why this group exists, what unites them)
2. Fill demographics (draw from research data, not assumptions)
3. Fill psychographics (values, beliefs, identity)
4. List core desires (5+, from research evidence)
5. List pain points (5+, using their language)
6. List fears (5+, emotional depth)
7. List beliefs (5+, their worldview)
8. List objections (5+, why they hesitate)
9. List emotional triggers (5+, what activates buying)
10. List language patterns (5+, EXACT QUOTES from research)
11. Generate ebook angles (3+, titles that would attract this group)
12. Generate marketing hooks (3+, headlines that stop scrolling)
13. Write transformation promise (emotionally resonant before-to-after)
14. Assign awareness stage with reasoning

**Quality check after each batch of 5:**
- Are language patterns actually from research?
- Are groups truly distinct?
- Do any profiles feel thin? If so, do more targeted research.

## Phase 7: Quality Validation (5 minutes)

**Goal:** Ensure output meets the quality bar.

Run through this checklist:
- [ ] Every group has 5+ items in all required list fields
- [ ] Language patterns are authentic (not marketing-speak)
- [ ] No two groups could be merged without loss
- [ ] Awareness stages have documented reasoning
- [ ] Demographics are specific (not "adults 18-65")
- [ ] Transformation promises are emotionally distinct
- [ ] Marketing hooks would actually stop someone scrolling
- [ ] Total group count is 15-30

If any check fails, fix it before proceeding.

## Phase 8: Output Generation (5 minutes)

**Goal:** Produce all deliverables.

1. Generate the markdown document using `compile_audience_doc.py`
2. Save to filesystem at `projects/{project-slug}/research/`
3. Save document record to Convex `documents` table
4. Parse each group into JSON and write to `focusGroupStaging` table
5. Calculate completeness scores
6. Complete the pipeline step

---

## Total Expected Time: 45-75 minutes

Adjust based on:
- **Market breadth**: Broad markets need more groups
- **Service availability**: Missing services = shorter research phase
- **Existing data**: If groups already exist, focus on gaps
- **Research richness**: Some niches have more online discussion than others
