---
name: image-director-engagement
displayName: Image Director -- Engagement
description: Specialized image prompt engineering for engagement social posts. Produces scroll-stopping visuals using STEPPS virality scoring, platform-specific formats (TOBI, meme, grid, quote card, nostalgic photo), and engagement psychology. Reads post content to infer visual intent when no explicit imageIntent is provided.
category: media
type: procedure
mode: on-demand
agent: vibe-image-director
---

# Image Director -- Engagement

You are the `vibe-image-director` agent processing content from an **engagement pipeline** (content batches from `vibe-facebook-engine` or similar engagement-focused agents). This skill supersedes `image-prompt-engineering` for engagement content. Use `image-prompt-engineering` for sales campaigns, articles, landing pages, and ebook covers.

**Purpose:** Transform engagement post text into scroll-stopping visual prompts. Your images must feel organic, human, and emotionally resonant -- never corporate, never stock-photo, never branded. The image's only job is to stop the scroll and amplify the post's engagement potential.

**Critical Rule: No logos, no watermarks, no brand marks, no URLs.** Engagement visuals must look like something a real person would share from their camera roll or create on Canva at 11 PM. The moment an image looks "produced," trust dies and engagement collapses.

---

## 1. Execution Protocol

### Step 1: Load Context

Read your task record from Convex. Extract:
- `taskId` -- your task identifier
- `campaignId` -- the campaign this belongs to (may be a `contentBatchId` for engagement batches)
- `projectId` -- the parent project
- `outputDir` -- default to `projects/{project}/campaigns/{campaign}/assets/images/`

Load from campaign/project:
- `product` -- brand colors, visual identity notes (used sparingly -- engagement images are low-brand)
- `focusGroups` -- target audience demographics and psychographics (affects visual tone, era references, emotional register)

### Step 2: Find Parent Post Resources

```bash
POSTS=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"social_post"
}' --url http://localhost:3210)
```

If no posts exist, check for `article` type as fallback:
```bash
ARTICLES=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"article"
}' --url http://localhost:3210)
```

If neither exists, the upstream writer has not completed -- set task to `blocked`.

### Step 3: For Each Post -- Determine Image Intent

Read the post content from the resource's `filePath` or `content` field. Parse the structured post output looking for the `### Image Intent` section.

**IF the post includes an `Image Intent` section** (from facebook-engagement-engine):
- Extract `Format`, `Hook text for image`, and `Visual concept`
- Map the format string to the canonical intent key (see Section 3)

**IF the post does NOT include an `Image Intent` section** (legacy posts or agents that don't produce one):
- Run the Image Intent Detection algorithm (Section 2)
- Infer intent from post content signals

**IF the post format is `Text-only`** or Image Intent is `NONE`:
- Skip image generation for this post
- Do not register an image_prompt resource

### Step 4: Generate Prompt + Output JSON

For each post that needs an image:
1. Build the prompt using the format-specific rules (Section 3)
2. Score against STEPPS Visual criteria (Section 4)
3. Validate against Quality Gates (Section 9)
4. Write the prompt spec JSON file
5. Register as a child resource with `parentResourceId` pointing to the post

---

## 2. Image Intent Detection

When the upstream writing agent does not provide an explicit `imageIntent`, infer it from the post content. Scan the post text for these signals IN ORDER -- first match wins.

### Detection Table

| Priority | Content Signals | Inferred Intent | Visual Format |
|----------|----------------|----------------|---------------|
| 1 | Contains "Pick one" / "One has to go" / "Choose" / "Eliminate one" / numbered options (1. 2. 3. 4.) | `choose_grid` | 2x2 or 4-panel grid layout |
| 2 | Contains "Unpopular opinion" / "Hot take" / "I don't care what anyone says" / debate framing | `tobi_bold` | Bold text on solid/gradient background |
| 3 | Contains a fill-in-the-blank pattern ("_______" or "________") | `tobi_minimal` | Clean, minimal text-on-background |
| 4 | Post is a short quote or profound statement (core statement under 20 words, no question) | `quote_card` | Stylized text on textured/blurred background |
| 5 | Contains "Tag someone who" / "Share if you" / "Send this to" | `emotional_photo` | Warm, relatable photo matching the emotion |
| 6 | Contains nostalgic references: decade names ("the 90s", "back in 2003"), "remember when", "used to", era-specific objects (disposable cameras, VHS, dial-up) | `nostalgic_photo` | Vintage-filtered, era-appropriate photography |
| 7 | Contains a personal story / narrative arc (5+ sentences, chronological structure, emotional payoff) | `photo_text_overlay` | Emotional photo with hook line overlaid |
| 8 | Contains a question inviting personal stories ("What was yours?", "How did you...", "What would you tell...") | `emotional_photo` | Evocative photo that prompts the question visually |
| 9 | Contains humor / irony / relatability markers ("literally", "me when", "nobody:", "that moment when") | `meme` | Meme-format: image + bold top/bottom text |
| 10 | Generic / unclear / no strong signal | `photo_text_overlay` | Default: photo with text overlay |

### Detection Algorithm

```
FOR each post:
  1. Check for interactive markers (numbered options, "pick one") → choose_grid
  2. Check for opinion markers ("unpopular opinion", "hot take") → tobi_bold
  3. Check for fill-in-blank ("_______") → tobi_minimal
  4. Count core statement words (excluding setup). If < 20 and no question mark → quote_card
  5. Check for tag/share directives → emotional_photo
  6. Check for nostalgia markers (decade refs, "remember when", era objects) → nostalgic_photo
  7. Check sentence count and narrative structure → photo_text_overlay
  8. Check for open-ended questions → emotional_photo
  9. Check for humor markers → meme
  10. Default → photo_text_overlay
```

---

## 3. Visual Format Specifications

### 3.1 TOBI Bold (`tobi_bold`)

**Use for:** Hot takes, unpopular opinions, provocative statements, debate starters.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Bold, large text (2-8 words max) as the dominant visual element
- Text centered vertically and horizontally
- Background: solid color, diagonal gradient, or subtle texture (paper, concrete, fabric)
- Colors: high-contrast combinations -- dark background + white text, or brand-adjacent bold color + black text
- Font direction: heavy sans-serif, all-caps or title case, tight letter-spacing
- No imagery behind text -- the text IS the image
- Minimum font size equivalent: 72pt+ (must dominate the frame)

**Prompt pattern:**
```
Bold typographic design, [exact text in quotes] in heavy white sans-serif font centered on [background description], [color palette], high contrast, clean modern design, Instagram quote post aesthetic, 1080x1350 vertical format
```

**Negative prompts (format-specific):**
```
photograph, person, face, landscape, complex background, busy pattern, thin font, small text, decorative elements, borders, frames, clipart
```

**Recommended service:** Ideogram 3.0 (best text rendering)
**Fallback:** GPT Image 1.5

---

### 3.2 TOBI Minimal (`tobi_minimal`)

**Use for:** Fill-in-the-blanks, reflective thoughts, gentle questions, incomplete sentences.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Clean, elegant text on subtle background
- More whitespace than TOBI Bold -- text breathes
- Background: soft gradients, muted tones, blurred nature, paper texture
- Font direction: medium-weight sans-serif or elegant serif, lower case preferred
- Text placement: center or slightly above center
- Color palette: muted, warm -- cream, soft grey, dusty rose, sage green
- The blank line ("_______") should be visually prominent

**Prompt pattern:**
```
Minimalist typographic design, [exact text with blank line] in elegant [serif/sans-serif] font on [soft background], muted [color palette], generous whitespace, calming aesthetic, social media quote post, 1080x1350 vertical
```

**Negative prompts (format-specific):**
```
bold text, aggressive, high contrast, neon colors, busy background, photograph, person, cluttered
```

**Recommended service:** Ideogram 3.0
**Fallback:** GPT Image 1.5

---

### 3.3 Photo + Text Overlay (`photo_text_overlay`)

**Use for:** Story posts, emotional narratives, personal anecdotes, default when intent is unclear.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Emotional or aspirational photograph as full-bleed background
- Hook line or key phrase overlaid in bold, readable text
- Text placement: bottom 25-30% of image, centered horizontally
- Semi-transparent dark gradient (0.4-0.6 opacity) behind text area for readability
- Text: bold sans-serif, white, with subtle drop shadow or text stroke
- Photo subject: matches the emotional core of the post (see Emotion Mapping below)
- Shallow depth of field preferred -- keeps focus on mood, not details
- Natural lighting -- golden hour, overcast diffused, or warm indoor ambient

**Text selection rules:**
- Extract the hook line (first 1-2 sentences) OR the emotional payoff line
- Keep text on image to 15 words maximum
- If the post is a story, use the opening hook
- If the post is emotional, use the climactic line

**Prompt pattern:**
```
[Subject description] in [setting], [lighting description], [emotional mood], [color tones], shallow depth of field, authentic candid photography style, warm and human, NOT stock photography, with space in the lower third for text overlay, 1080x1350 vertical format, 4:5 aspect ratio
```

**Negative prompts (format-specific):**
```
text, words, letters, watermark, stock photo, posed, fake smile, corporate, staged, studio lighting, flash photography, selfie, brand logo
```

**Recommended service:** FLUX.2 [pro] (best photorealism) or GPT Image 1.5
**Fallback:** Google Imagen 4

### Emotion-to-Subject Mapping

| Post Emotion | Photo Subject Direction |
|-------------|----------------------|
| Awe / wonder | Vast landscape, dramatic sky, tiny human in grand scene |
| Warmth / love | Close human connection -- hands touching, embrace, shared look |
| Nostalgia | Warm-toned everyday moment, sun-drenched, slightly soft focus |
| Humor / lightness | Playful moment, unexpected juxtaposition, candid laughter |
| Determination / strength | Forward motion, sunrise, uphill path, hands gripping |
| Tenderness | Small intimate detail -- a hand on a cheek, a child's fingers, a pet curled up |
| Bittersweetness | Rain on a window, empty chair with sunset, wilting flowers in golden light |

---

### 3.4 Meme Format (`meme`)

**Use for:** Humor, irony, relatability, "me when" moments, absurd observations.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Relatable image (generated scene, not stock) as the main visual
- Bold white text with black outline or stroke (Impact-style or modern bold sans-serif)
- Top text: setup / context (4-8 words max)
- Bottom text: punchline / payoff (4-8 words max)
- Image should depict a recognizable situation, expression, or reaction
- Keep the image simple -- one subject, one clear emotion or action
- Slightly imperfect aesthetic (not too polished -- memes should feel casual)

**Text extraction rules:**
- Split the post into setup and punchline
- If the post has a clear two-part structure, use that split
- If the post is a single statement, put the context on top and the punchline on bottom
- If the post is too long, distill to the funniest/most relatable 2 lines

**Prompt pattern:**
```
[Scene description matching the humor], [expression/reaction], relatable everyday moment, candid photography style or illustration, warm tones, slightly humorous mood, space for bold text overlay at top and bottom, 1080x1350 vertical, meme format layout
```

**Negative prompts (format-specific):**
```
text, words, watermark, perfect, polished, corporate, professional photography, glamorous, editorial
```

**Recommended service:** Ideogram 3.0 (if text is baked into the image) or FLUX.2 [pro] (if text is added post-generation)
**Fallback:** GPT Image 1.5

---

### 3.5 Choose Grid (`choose_grid`)

**Use for:** Interactive posts with 4 options -- "pick one," "one has to go," "eliminate one."

**Dimensions:** 1080 x 1080 (1:1 square -- grids work better square)

**Composition:**
- 2x2 panel layout, equal quadrants
- Thin white borders between panels (4-8px equivalent)
- Each panel: one option clearly depicted
- Number labels (1, 2, 3, 4) in corner of each panel -- white text, dark semi-transparent circle background
- Each panel contains either:
  - A representative image of the option, OR
  - Styled text on a colored background (if options are abstract)
- Visual style must be consistent across all 4 panels (same lighting, same style, same color treatment)
- Clean, simple visuals -- the audience needs to instantly recognize each option

**Prompt pattern:**
```
2x2 grid layout with thin white borders, four panels showing [option 1], [option 2], [option 3], [option 4], each panel clearly distinct, consistent [style] across all panels, numbered 1-4 in corners, clean and recognizable, social media interactive post, 1080x1080 square format
```

**Negative prompts (format-specific):**
```
merged panels, overlapping, unclear boundaries, complex scenes, tiny details, text-heavy, busy backgrounds, inconsistent styles between panels
```

**Recommended service:** FLUX.2 [pro] (clean multi-panel generation)
**Fallback:** GPT Image 1.5

---

### 3.6 Quote Card (`quote_card`)

**Use for:** Short profound statements, poetry-like lines, philosophical observations, memorable one-liners.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Stylized text as the primary visual element
- Background: blurred photography, watercolor wash, gradient, textured paper, or bokeh
- Font: elegant serif, handwritten script, or refined sans-serif -- NOT Impact, NOT bold
- Text centered with generous margins (at least 15% on each side)
- Optional: thin decorative line above and below quote
- Optional: small attribution line if quoting someone (smaller font, lighter weight)
- Color: text should contrast with background but not harshly -- off-white on dark, charcoal on light
- The overall feel should be "something you'd screenshot and save"

**Prompt pattern:**
```
Elegant quote card design, [quote text] in [font style] on [background description], [color palette], refined and shareable aesthetic, generous whitespace, social media quote post, slightly textured, warm tones, 1080x1350 vertical
```

**Negative prompts (format-specific):**
```
bold aggressive font, neon, busy background, photograph of person, cluttered, corporate, template look, generic motivational poster
```

**Recommended service:** Ideogram 3.0 (elegant text rendering)
**Fallback:** GPT Image 1.5

---

### 3.7 Nostalgic Photo (`nostalgic_photo`)

**Use for:** "Remember when" posts, decade references, era-specific nostalgia, "back in the day" content.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Photography style that matches the era referenced in the post
- Film grain, slightly faded colors, warm color shift
- Subjects and scenes must match the specific nostalgia trigger (see Era Guide below)
- Avoid ALL modern elements: no smartphones, no flat-screen TVs, no modern cars, no LED lights
- Natural or tungsten lighting -- no flash (flash kills the nostalgic mood)
- Slightly imperfect framing (the "found photo" aesthetic)
- No text on image -- the photo alone must evoke the era

**Era-Specific Visual Guide:**

| Era | Color Treatment | Key Visual Cues | Lighting |
|-----|----------------|-----------------|----------|
| 1970s | Warm orange/brown cast, desaturated greens | Wood paneling, shag carpet, large sunglasses, muscle cars, Polaroids | Warm tungsten, golden afternoon |
| 1980s | High saturation, neon accents, slightly blue shadows | Neon signs, arcade machines, boomboxes, roller rinks, VHS tapes | Mixed neon + daylight |
| 1990s | Muted, slightly green-shifted, low contrast | Dial-up computers, disposable cameras, scrunchies, Walkmans, malls | Overcast diffused, flash snapshot |
| 2000s | Oversaturated, slightly warm, digital noise | Flip phones, low-rise jeans, early iPods, Myspace aesthetic | Flash photography, indoor fluorescent |
| "Childhood" (generic) | Warm, sun-drenched, slightly overexposed | Running in sprinklers, popsicle drips, bike rides, screen doors | Golden hour, summer afternoon |

**Prompt pattern:**
```
[Era-appropriate scene], [specific objects/subjects from the post], [era color treatment], film grain, [era-specific lighting], authentic vintage photography feel, NOT modern, NOT digital, nostalgic and warm, 1080x1350 vertical, 4:5 aspect ratio
```

**Negative prompts (format-specific):**
```
modern, contemporary, smartphone, flat screen TV, LED lights, current fashion, clean digital look, HDR, oversharped, text, watermark, logo
```

**Recommended service:** FLUX.2 [pro] (best era-specific photorealism)
**Fallback:** GPT Image 1.5

---

### 3.8 Emotional Photo (`emotional_photo`)

**Use for:** Tag-someone posts, question posts inviting personal stories, posts about universal human experiences.

**Dimensions:** 1080 x 1350 (4:5 vertical)

**Composition:**
- Pure photography -- NO text on image
- Warm, human, authentic-feeling (the opposite of stock photography)
- Subject should match the specific emotion and situation in the post
- Shallow depth of field, natural lighting strongly preferred
- Diverse subjects -- vary age, ethnicity, body type across a batch
- Real-feeling moments: candid expressions, imperfect framing, authentic environments
- Color treatment: warm, slightly desaturated, film-like (not Instagram-filtered)
- The photo should make someone pause and feel something before they even read the caption

**Emotion-to-Scene Mapping:**

| Post Theme | Photo Direction |
|-----------|----------------|
| Parent-child love | Adult holding child's hand, child on parent's shoulders, bedtime moment |
| Romantic love | Couple's hands intertwined, forehead touching, laughing together at a table |
| Friendship | Two people laughing on a bench, arm-in-arm walking, shared meal |
| Loss / missing someone | Empty chair, old photograph held in weathered hands, sunset silhouette |
| Achievement / pride | Graduation, finish line, hands raised, tears of joy |
| Everyday beauty | Morning coffee steam, rain on a window, sunlight through curtains |
| Animals / pets | Dog resting head on owner's lap, cat curled on a sunny windowsill |

**Prompt pattern:**
```
[Scene matching post theme], authentic candid photography, [natural lighting direction], warm tones, shallow depth of field, genuine human moment, NOT stock photography, NOT posed, emotional and intimate, [diverse subject description], 1080x1350 vertical, 4:5 aspect ratio
```

**Negative prompts (format-specific):**
```
stock photo, corporate, posed, fake smile, staged, studio, flash, perfect hair, perfect makeup, model, advertisement, text, watermark, logo, brand
```

**Recommended service:** FLUX.2 [pro] (authentic human photography)
**Fallback:** GPT Image 1.5

---

## 4. STEPPS Visual Scoring

Every image prompt gets scored against STEPPS specifically for the VISUAL component (independent of the post text). The image alone must contribute to virality.

### Visual STEPPS Diagnostic

| Principle | Scoring Question | Scoring Guide |
|-----------|-----------------|---------------|
| **Social Currency** | Does sharing this IMAGE make the sharer look good, tasteful, or emotionally intelligent? | 0 = generic / 5 = "I need to share this aesthetic" |
| **Triggers** | Is the visual tied to an everyday cue (coffee, sunset, commute, bedtime, morning)? | 0 = abstract / 5 = triggers a daily moment |
| **Emotion** | Does the IMAGE ALONE (without text) evoke high-arousal emotion? | 0 = flat / 5 = gut-punch feeling |
| **Public** | Is the visual style recognizable as a "type" of post? (quote card, meme, grid = high recognition) | 0 = ambiguous / 5 = instantly categorizable |
| **Practical Value** | Does the image convey useful info at a glance? (grid with options = high / emotional photo = low) | 0 = decorative / 5 = informative visual |
| **Stories** | Does the image imply a narrative? (before/after, a frozen moment, a journey) | 0 = static / 5 = "what happened here?" |

### Scoring Rules

- Score each principle 0-5
- Total possible: 30
- **Minimum threshold: 16/30** -- below this, rework the prompt
- **At least 3 principles must score 3+** for the visual alone
- **Emotion must score 3+** -- if the image evokes nothing, it fails regardless of total

### Format-Typical Score Profiles

| Format | Social Currency | Triggers | Emotion | Public | Practical | Stories | Typical Total |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| tobi_bold | 4 | 2 | 4 | 5 | 2 | 1 | 18 |
| tobi_minimal | 3 | 3 | 3 | 4 | 2 | 1 | 16 |
| photo_text_overlay | 4 | 3 | 5 | 4 | 1 | 4 | 21 |
| meme | 5 | 3 | 4 | 5 | 1 | 2 | 20 |
| choose_grid | 3 | 2 | 2 | 5 | 5 | 1 | 18 |
| quote_card | 4 | 3 | 4 | 5 | 2 | 2 | 20 |
| nostalgic_photo | 5 | 4 | 5 | 3 | 1 | 5 | 23 |
| emotional_photo | 4 | 3 | 5 | 3 | 1 | 4 | 20 |

---

## 5. Platform-Specific Rules

### Facebook (Primary Target)

- **ALWAYS 1080 x 1350** (4:5 vertical) for feed posts -- maximum feed real estate
- **Exception:** `choose_grid` uses 1080 x 1080 (1:1 square)
- No logos, no watermarks, no brand marks -- kills organic feel
- No stock photo aesthetics -- kills trust
- Text on images must be readable at mobile thumbnail size (minimum ~40pt equivalent, or ~3% of image height)
- Facebook compresses images aggressively -- avoid fine details that will artifact
- Vertical images get 30-40% more feed real estate than square, and 60%+ more than horizontal
- Avoid images that look like ads -- Facebook's algorithm de-prioritizes ad-like content in organic feeds

### Instagram (Future-Ready)

- Feed: 1080 x 1350 (same as Facebook -- create once, post twice)
- Stories/Reels covers: 1080 x 1920 (9:16) -- separate prompt if needed
- Higher aesthetic bar than Facebook -- cleaner, more curated
- Carousel-aware: if producing multiple images for one post, first image must hook, subsequent images reveal
- Hashtag culture means the visual must stand alone without caption context

### Cross-Platform Image Rules

| Rule | Rationale |
|------|-----------|
| No text smaller than 40pt equivalent | Unreadable on mobile thumbnails |
| Max 20% of image area covered by text | Facebook may suppress reach for text-heavy images |
| Avoid pure white or pure black backgrounds | Gets lost in feed UI chrome |
| Include at least one warm color | Warm colors outperform cool in engagement metrics |
| Faces increase engagement 38% | Include human faces when format allows |

---

## 6. Technical Prompt Construction

Use the engagement-tuned framework. Order matters -- most image models weight earlier tokens more heavily.

### Prompt Structure

```
[Subject] + [Action/State] + [Setting] + [Style/Medium] + [Lighting] + [Color Palette] + [Composition] + [Mood] + [Text Elements] + [Technical Specs]
```

### Component Guide

| Component | Engagement-Specific Rules |
|-----------|--------------------------|
| **Subject** | Describe concretely. "A woman in her 60s laughing at a kitchen table" not "an older person." Specificity = authenticity. |
| **Action/State** | Capture a MOMENT, not a pose. "mid-laugh with eyes closed" not "smiling at camera." Candid beats posed. |
| **Setting** | Real environments only. Kitchens, parks, porches, cafes, living rooms. Never studios, never offices, never conference rooms. |
| **Style/Medium** | Default: "authentic candid photography, NOT stock photography." For TOBI: "bold typographic design." For meme: "relatable everyday photography." |
| **Lighting** | Natural always. "Soft natural window light," "golden hour warmth," "overcast diffused daylight." Never flash. Never studio. |
| **Color Palette** | Warm tones dominate. "Warm earth tones," "golden and amber," "soft muted pastels." Avoid clinical blues and greens. |
| **Composition** | Specify text areas. "Space in the lower third for text overlay." "Subject left, negative space right." "Centered with generous margins." |
| **Mood** | Name the feeling the viewer should have. "Bittersweet nostalgia," "warm recognition," "quiet awe," "lighthearted amusement." |
| **Text Elements** | NEW for engagement. What text appears (exact words or "no text"), font direction, placement, color. See below. |
| **Technical** | "1080x1350, 4:5 aspect ratio, high resolution, sharp focus" -- always include dimensions explicitly. |

### Text Elements Component

For formats that include text on the image (TOBI, quote_card, photo_text_overlay, meme):

```json
"textElements": {
  "hasText": true,
  "textContent": "The exact words to render on the image",
  "fontDirection": "bold sans-serif, white, drop shadow" | "elegant serif, charcoal, no effects" | "Impact bold, white with black stroke",
  "placement": "centered" | "bottom 25%, centered" | "top: setup / bottom: punchline",
  "readableAtThumbnail": true
}
```

For formats without text (emotional_photo, nostalgic_photo):
```json
"textElements": {
  "hasText": false
}
```

---

## 7. Engagement-Specific Negative Prompts

### Universal Engagement Negatives

Include in EVERY engagement image prompt, in addition to format-specific negatives:

```
stock photo, corporate, posed, fake smile, staged, sterile, clinical,
professional headshot, business meeting, laptop stock photo, handshake,
generic office, shutterstock watermark, istock, getty,
oversaturated HDR, overly processed, Instagram filter overdone,
advertisement, commercial, promotional, brand logo, watermark, URL,
perfect teeth, perfect hair, model, catalogue, fashion shoot,
clip art, cartoon (unless meme), vector illustration (unless TOBI),
3D render, CGI, uncanny valley, AI face artifacts
```

### Why These Negatives Matter

Engagement images live or die on authenticity. The Facebook audience (primarily millennials, Gen X, boomers) has developed acute radar for:
- **Stock photo aesthetics:** Overlit, perfectly diverse groups shaking hands or pointing at laptops. Instant scroll-past.
- **Corporate polish:** Anything that feels like a brand produced it. Organic reach plummets.
- **AI artifacts:** Distorted hands, wrong number of fingers, melted text. Destroys trust.
- **Over-processing:** HDR glow, extreme saturation, heavy vignettes. Screams "not real."

---

## 8. Service Recommendations

| Visual Format | Primary Service | Why | Fallback |
|--------------|----------------|-----|----------|
| `tobi_bold` | Ideogram 3.0 | Best text rendering -- bold text is the entire image | GPT Image 1.5 |
| `tobi_minimal` | Ideogram 3.0 | Reliable elegant text rendering | GPT Image 1.5 |
| `photo_text_overlay` | FLUX.2 [pro] | Best photorealism for background photo; text added in post-processing or use GPT Image 1.5 for one-shot | GPT Image 1.5 |
| `meme` | Ideogram 3.0 | Reliable multi-zone text rendering (top + bottom) | GPT Image 1.5 |
| `choose_grid` | FLUX.2 [pro] | Clean multi-panel generation with consistent style | GPT Image 1.5 |
| `quote_card` | Ideogram 3.0 | Elegant text rendering with decorative backgrounds | GPT Image 1.5 |
| `nostalgic_photo` | FLUX.2 [pro] | Best era-specific photorealism, film grain, color grading | GPT Image 1.5 |
| `emotional_photo` | FLUX.2 [pro] | Most authentic human photography generation | GPT Image 1.5 |

### Service Selection Logic

```
IF format requires text on image (tobi_bold, tobi_minimal, quote_card, meme):
  → Primary: Ideogram 3.0 (text specialist)
  → Fallback: GPT Image 1.5 (good text + good photo)

IF format is pure photography (nostalgic_photo, emotional_photo):
  → Primary: FLUX.2 [pro] (photorealism specialist)
  → Fallback: GPT Image 1.5

IF format is hybrid photo + text (photo_text_overlay):
  → Primary: GPT Image 1.5 (handles both well)
  → Alternative: FLUX.2 [pro] for photo, text added in post-processing

IF format is structured layout (choose_grid):
  → Primary: FLUX.2 [pro] (clean structured generation)
  → Fallback: GPT Image 1.5
```

---

## 9. Quality Gates

Every image prompt must pass ALL gates before output.

### Gate 1: STEPPS Visual Score
- Total must be 16+ / 30
- At least 3 principles must score 3+
- Emotion must score 3+
- **FAIL action:** Rework the visual concept. Change the subject, lighting, or composition to increase emotional impact.

### Gate 2: Text Readability
- If the format includes text, it must be readable at mobile thumbnail size (~120px wide preview)
- Text content must be 15 words or fewer on the image
- Text must contrast sufficiently with background
- **FAIL action:** Simplify text, increase font size direction, add darker gradient behind text area.

### Gate 3: Stock Photo Detector
- Does the prompt contain ANY of: "diverse group," "business professional," "pointing at screen," "team meeting," "high five," "thumbs up"?
- Does the subject feel generic rather than specific?
- **FAIL action:** Make the subject specific. "A woman in her 60s with grey hair at a kitchen table" not "a diverse group of people."

### Gate 4: Format-Intent Match
- Does the visual format match the post's intent?
- Opinion posts must use TOBI, not emotional photo
- Interactive posts must use choose_grid, not quote card
- Nostalgic posts must use nostalgic_photo with correct era treatment
- **FAIL action:** Reassign format using the Detection Table.

### Gate 5: Dimension Check
- Vertical posts: exactly 1080 x 1350
- Grid posts: exactly 1080 x 1080
- **FAIL action:** Correct dimensions in the output JSON.

### Gate 6: No Branding
- Prompt must not include brand names, logos, URLs, or product names
- Image must not look like an advertisement
- **FAIL action:** Remove all brand references. Engagement images are brand-invisible.

---

## 10. Output JSON Format

Write a prompt spec JSON file for each post that needs an image.

```json
{
  "taskId": "task_xxx",
  "campaignId": "campaign_xxx",
  "parentResourceId": "resource_xxx",
  "imageIntent": "photo_text_overlay",
  "imageFormat": "engagement_social",
  "dimensions": {
    "width": 1080,
    "height": 1350,
    "aspectRatio": "4:5"
  },
  "prompt": "A woman in her late 20s sitting on a porch step at golden hour, looking down at an old letter in her hands, warm amber light, shallow depth of field, authentic candid photography, NOT stock photography, bittersweet nostalgia mood, space in the lower 25% for text overlay, 1080x1350 vertical format, 4:5 aspect ratio",
  "negativePrompt": "stock photo, corporate, posed, fake smile, staged, sterile, clinical, professional headshot, business meeting, shutterstock watermark, istock, getty, oversaturated HDR, overly processed, text, words, letters, watermark, logo, brand, advertisement",
  "textElements": {
    "hasText": true,
    "textContent": "She kept the napkin from their first date for 23 years.",
    "fontDirection": "elegant serif, white, subtle drop shadow",
    "placement": "bottom 25%, centered",
    "readableAtThumbnail": true
  },
  "style": {
    "medium": "photography",
    "substyle": "authentic candid",
    "lighting": "golden hour, natural",
    "colorPalette": ["warm amber", "soft gold", "muted earth"],
    "mood": "bittersweet nostalgia, quiet tenderness"
  },
  "steppsVisualScore": {
    "socialCurrency": 4,
    "triggers": 3,
    "emotion": 5,
    "public": 4,
    "practicalValue": 1,
    "stories": 5,
    "total": 22
  },
  "recommendedService": "flux2_pro",
  "fallbackService": "gpt_image_1_5",
  "serviceNotes": "Pure photography with text overlay -- FLUX.2 Pro for the photo, text can be composited in post-processing or use GPT Image 1.5 for one-shot generation.",
  "variations": {
    "requested": 2,
    "variationNotes": "Vary lighting (golden hour vs overcast) and subject age for audience breadth"
  },
  "metadata": {
    "postFormat": "Emotional Story",
    "sourcePostNumber": 7,
    "focusGroup": "Newlyweds",
    "hookTechnique": "Specific detail (Ogilvy)",
    "generatedAt": "2026-02-15T14:30:00Z"
  }
}
```

Write to: `{outputDir}/prompt-engagement-{intent}-{postNumber}-{taskId}.json`

---

## 11. Multi-Article Campaign Mode

When the task description contains "Produce N articles in a single pipeline run" or the task has multiple parent social_post resources:

### 1. Parse post count
Extract N from the task description or count the social_post resources returned by `resources:listByTaskAndType`.

### 2. Load parent post resources
```bash
POSTS=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"social_post"
}' --url http://localhost:3210)
```

### 3. Check existing image prompts (skip-already-done)
```bash
EXISTING=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"image_prompt"
}' --url http://localhost:3210)
```
Skip posts that already have associated image prompts (match via `parentResourceId`).

### 4. Create image prompts for EACH post
For each post resource:
- Read the post content from `filePath` or `content` field
- Determine image intent (Section 2)
- Skip text-only posts (no image needed)
- Run the full prompt engineering protocol
- Register each image prompt as a CHILD resource:

```bash
npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "image_prompt",
  "title": "Engagement image prompt: <intent> for Post <i>",
  "campaignId": "<CAMPAIGN_ID>",
  "taskId": "<TASK_ID>",
  "parentResourceId": "<POST_RESOURCE_ID>",
  "filePath": "<path to prompt JSON>",
  "status": "draft",
  "createdBy": "vibe-image-director",
  "metadata": {
    "style": "<format>",
    "dimensions": "1080x1350",
    "provider": "<recommended service>",
    "imageIntent": "<intent>",
    "steppsVisualScore": <total>
  }
}' --url http://localhost:3210
```

For efficiency with many prompts, use `resources:batchCreate`.

### 5. Call completeBranch ONCE
Pass ALL image prompt resource IDs in a single call:

```bash
npx convex run pipeline:completeBranch '{
  "taskId": "<TASK_ID>",
  "branchLabel": "image-prompt",
  "agentName": "vibe-image-director",
  "resourceIds": ["id1","id2","id3"]
}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for the full multi-article protocol.

---

## 12. Engagement Psychology -- Visual Principles

These principles, synthesized from Berger (STEPPS visual triggers), Sugarman (sensory engagement), and Ogilvy (composition that sells), govern WHY certain images stop the scroll.

### 12.1 The Curiosity Gap (Sugarman)

Images that show PART of a story create an irresistible pull to read the caption. The viewer's mind demands completion.

**Apply by:**
- Showing a reaction without showing the cause (a woman crying + smiling = "what happened?")
- Showing an object with significance but no context (an old key, a worn letter, a single shoe)
- Showing a moment just before or just after the event (not the event itself)

### 12.2 Specificity Creates Believability (Ogilvy)

Specific visual details make an image feel REAL. Generic scenes feel fake.

**Apply by:**
- "A chipped coffee mug with a faded logo" not "a coffee cup"
- "A 1996 Toyota Corolla with a dented fender" not "a car"
- "Hands with flour dust and a thin gold wedding band" not "someone baking"
- Include one imperfect detail in every photo prompt (scratched table, wrinkled shirt, mismatched socks)

### 12.3 High-Arousal Color (Berger)

Warm colors (red, orange, amber, gold) create physiological arousal. The body's response to warm colors mirrors the arousal that drives sharing behavior.

**Apply by:**
- Default to warm color palettes for engagement images
- Use golden hour lighting when possible (warm + authentic)
- Reserve cool tones (blue, grey, silver) for reflective/nostalgic moods only
- Never use clinical colors (bright white, hospital green, sterile blue) -- they suppress engagement

### 12.4 Face Bias

Human brains process faces before any other visual element. Images with faces receive 38% more engagement on average (multiple platform studies).

**Apply by:**
- Include human faces when the format allows (emotional_photo, photo_text_overlay, nostalgic_photo)
- Show genuine expressions, not posed smiles
- Shallow depth of field with face in focus
- Exception: TOBI, quote_card, and choose_grid do not need faces

### 12.5 The "Screenshot Worth" Test

Before finalizing any prompt, ask: "Would someone screenshot this image to send to a specific person?" If the answer is no, the image is not engaging enough.

- Quote cards must be screenshot-worthy (the text must resonate alone)
- Emotional photos must be screenshot-worthy (the moment must be striking)
- Memes must be screenshot-worthy (the humor must land visually)
- Grids must be screenshot-worthy (the options must spark "what would you pick?")

---

## 13. Integration Points

| Upstream | This Skill | Downstream |
|----------|-----------|------------|
| `vibe-facebook-engine` (social_post resources with Image Intent) | image-director-engagement (analyze + prompt) | `vibe-image-generator` (generate image) |
| Any engagement agent (social_post resources without Image Intent) | image-director-engagement (infer intent + prompt) | `vibe-image-generator` (generate image) |
| Campaign brand config (colors, identity) | image-director-engagement (apply minimally) | Dashboard (display generated images) |

---

## 14. Anti-Patterns

| # | Anti-Pattern | What Goes Wrong |
|---|-------------|----------------|
| AP-01 | **Stock photo prompt** | Using language like "diverse group of people smiling" produces generic, trust-killing images. |
| AP-02 | **Branded engagement images** | Adding logos, watermarks, or brand names to engagement content kills organic feel and reach. |
| AP-03 | **Wrong format for intent** | Using emotional_photo for an interactive "pick one" post. The grid IS the engagement mechanic. |
| AP-04 | **Text too small** | Text on image that is unreadable at mobile thumbnail size. If you have to squint, it fails. |
| AP-05 | **Ignoring era cues** | Nostalgic post about the 90s with an image that has modern elements. One anachronism ruins the spell. |
| AP-06 | **Over-processed aesthetic** | HDR glow, extreme saturation, heavy vignettes. Screams "not authentic." |
| AP-07 | **Missing negative prompts** | Every AI image model defaults to stock-photo aesthetics. Without explicit negatives, you get corporate. |
| AP-08 | **Too many text words** | More than 15 words on an image becomes unreadable. Distill to the hook line only. |
| AP-09 | **Cold color palette** | Blue, grey, and green tones suppress engagement arousal. Default warm unless the post specifically calls for melancholy. |
| AP-10 | **Skipping STEPPS scoring** | Generating prompts without scoring means no quality control on visual virality. Every image gets scored. |

---

## 15. Error Handling

- **Missing parent posts:** Set task to `blocked`, log "No social_post resources found for task"
- **Text-only post (no image needed):** Skip gracefully, do not create an image_prompt resource
- **Ambiguous intent:** Default to `photo_text_overlay` -- the most versatile format
- **Missing focus group data:** Use neutral emotional defaults (warm, human, authentic)
- **Service unavailable:** Recommend fallback service in the JSON; `vibe-image-generator` handles retries
- **Post content too short to infer intent:** Default to `emotional_photo` -- safest engagement format

---

## What This Skill Does NOT Cover

- **Image generation** -- that is `vibe-image-generator`'s job
- **Sales/campaign imagery** -- use `image-prompt-engineering` for non-engagement content
- **Video thumbnails** -- separate skill
- **Brand identity creation** -- this skill deliberately minimizes brand presence
- **Image editing/compositing** -- downstream tooling handles text overlay compositing if needed
- **Instagram Stories/Reels** -- future extension (this version targets feed posts)
