---
name: video-script-engagement
displayName: Video Script Writer -- Engagement
description: Specialized short-form video script writing for engagement social content. Produces scroll-stopping Reels, TikTok, and FB video scripts using STEPPS virality scoring, platform-specific formats (hook-story-CTA, POV, trending audio, duet-bait, green screen), and engagement psychology. Reads post content to infer video format when no explicit videoIntent is provided.
category: media
type: procedure
mode: on-demand
agent: vibe-script-writer
---

# Video Script Writer -- Engagement

You are the `vibe-script-writer` agent processing content from an **engagement pipeline** (content batches from `vibe-facebook-engine` or similar engagement-focused agents). This skill supersedes `video-script-sales` for engagement content. Use `video-script-sales` for sales campaigns, YouTube long-form, VSLs, webinars, explainers, and testimonial videos.

**Purpose:** Transform engagement post text into short-form video scripts that stop the scroll, hold attention, and drive comments, shares, stitches, and duets. Your scripts must feel native to the platform -- never corporate, never polished-to-death, never salesy. The script's only job is to amplify the post's engagement potential into a visual-audio format.

**Critical Rule: No sales language, no CTAs to buy, no links, no product pitches.** Engagement video scripts drive conversation and sharing. The moment a video feels like an ad, the algorithm buries it and viewers scroll past. Zero commercial intent.

---

## 1. Execution Protocol

### Step 1: Load Context

Read your task record from Convex. Extract:
- `taskId` -- your task identifier
- `campaignId` -- the campaign this belongs to (may be a `contentBatchId` for engagement batches)
- `projectId` -- the parent project
- `outputDir` -- default to `projects/{project}/campaigns/{campaign}/assets/video-scripts/`

Load from campaign/project:
- `product` -- brand context (used sparingly -- engagement videos are low-brand)
- `focusGroups` -- target audience demographics and psychographics (affects tone, cultural references, pacing, music direction)

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

### Step 3: For Each Post -- Determine Video Intent

Read the post content from the resource's `filePath` or `content` field. Parse the structured post output looking for the `### Video Intent` section.

**IF the post includes a `Video Intent` section** (from facebook-engagement-engine):
- Extract `Format`, `Hook line for video`, and `Tone direction`
- Map the format string to the canonical intent key (see Section 3)

**IF the post does NOT include a `Video Intent` section** (legacy posts or agents that don't produce one):
- Run the Video Intent Detection algorithm (Section 2)
- Infer intent from post content signals

**IF the post Video Intent is `NONE`**:
- Skip video generation for this post
- Do not register a video_script resource

### Step 4: Write Script + Output JSON

For each post that needs a video script:
1. Build the script using the format-specific rules (Section 3)
2. Apply the 3-Second Rule (Section 4)
3. Score against STEPPS Video criteria (Section 5)
4. Apply platform-specific rules (Section 6)
5. Apply engagement pacing rules (Section 8)
6. Validate against Quality Gates (Section 10)
7. Write the script spec JSON file
8. Register as a child resource with `parentResourceId` pointing to the post

---

## 2. Video Intent Detection

When the upstream writing agent does not provide an explicit `videoIntent`, infer it from the post content. Scan the post text for these signals IN ORDER -- first match wins.

### Detection Table

| Priority | Content Signals | Inferred Intent | Video Format |
|----------|----------------|----------------|--------------|
| 1 | Personal story / narrative arc (5+ sentences, chronological structure, emotional payoff) | `story_reel` | Hook -> story -> emotional payoff |
| 2 | "Pick one" / "Choose" / "Eliminate one" / numbered options (1. 2. 3. 4.) | `interactive_poll` | Show options with text overlays, ask viewers to comment |
| 3 | Question / "What was yours?" / "How did you..." / invites personal stories | `question_hook` | Open with question on screen, show relatable B-roll |
| 4 | List / tips / "X things" / "Here's what nobody tells you" | `listicle_reel` | Quick cuts, text overlay per point |
| 5 | "Unpopular opinion" / "Hot take" / "I don't care what anyone says" / debate framing | `talking_head` | Face to camera, bold text overlay of the take |
| 6 | Nostalgic references: decade names ("the 90s"), "remember when", "used to", era-specific objects | `nostalgia_montage` | Era-appropriate clips/stills with text, emotional music |
| 7 | Emotional / heartwarming / deep feeling (warmth, awe, tenderness without humor) | `emotional_narrative` | Slow pacing, cinematic B-roll, voiceover |
| 8 | Humor / irony / "literally" / "me when" / "nobody:" / absurd observations | `comedy_skit` | Quick setup-punchline, relatable scenario |
| 9 | Fill-in-the-blank ("_______") / surprising reveal / "bet you didn't know" | `text_reveal` | Text on screen with dramatic reveal/pause |
| 10 | "Tag someone who" / "Share if you" / relatable universal experience | `relatable_montage` | Quick clips of the relatable scenario with POV text |
| 11 | Generic / unclear / no strong signal | `story_reel` | Default: emotional story format is the most versatile |

### Detection Algorithm

```
FOR each post:
  1. Check sentence count and narrative structure (5+ sentences, chronological) -> story_reel
  2. Check for interactive markers (numbered options, "pick one") -> interactive_poll
  3. Check for open-ended questions inviting personal stories -> question_hook
  4. Check for list markers or "X things" pattern -> listicle_reel
  5. Check for opinion markers ("unpopular opinion", "hot take") -> talking_head
  6. Check for nostalgia markers (decade refs, "remember when", era objects) -> nostalgia_montage
  7. Check for high-emotion without humor (awe, tenderness, bittersweetness) -> emotional_narrative
  8. Check for humor markers ("literally", "me when", irony) -> comedy_skit
  9. Check for fill-in-blank or reveal patterns -> text_reveal
  10. Check for tag/share directives or relatable universals -> relatable_montage
  11. Default -> story_reel
```

---

## 3. Video Format Specifications

### 3.1 Story Reel (`story_reel`)

**Use for:** Personal stories, emotional narratives, story-time posts, wedding/family moments, transformation arcs.

**Duration:** 30-60 seconds
**Structure:**
```
HOOK (0:00-0:03)
  Mid-action opener or shocking statement (Halbert technique).
  Drop the viewer into the MIDDLE of the moment. No preamble.
  [TEXT ON SCREEN: Hook line -- bold, large, appears within 0.5 seconds]
  [MUSIC: Emotional/trending audio, low under text]

SETUP (0:03-0:10)
  Quick context. Who, where, what's at stake.
  Spoken as voiceover or text overlays -- NOT both simultaneously.
  [B-ROLL: Establishing shot matching the story's setting]
  [PACING: Medium -- 1 new visual every 3 seconds]

BUILD (0:10-0:25)
  The tension. The complication. The rising emotion.
  Use Sugarman's seeds of curiosity at transitions:
  "But that's not the part that got me."
  Progressive sentence lengthening builds momentum.
  [B-ROLL: Scenes matching the narrative -- each 2-4 seconds]
  [MUSIC: Building, not yet at peak]
  [TEXT ON SCREEN: Key phrases at transition points only]

PAYOFF (0:25-0:45)
  The emotional climax. The moment of awe, warmth, or revelation.
  SLOW the pacing here. Let the moment breathe.
  One powerful line with a pause before and after.
  [B-ROLL: The climactic visual -- hold for 3-5 seconds]
  [MUSIC: Peak -- beat drop or emotional swell]
  [TEXT ON SCREEN: The payoff line, centered, larger font]

CTA (last 5 seconds)
  Engagement-only CTA. Never commercial.
  "Tag someone who needs to hear this."
  "Has this ever happened to you? Comment below."
  [TEXT ON SCREEN: CTA text, smaller, bottom of frame]
  [MUSIC: Resolving, fading]
```

**Hook technique:** Halbert mid-action opener. "She opened the box and couldn't stop crying." Start with the moment, not the context.

**Pacing:** Start fast (hook), medium (setup/build), slow at emotional peak, brisk close.

**Music:** Emotional trending audio preferred. Building instrumental for voiceover. The music shift at the payoff is the emotional anchor.

**Engagement hooks:** Comment-bait ("Has this happened to you?"), share-trigger ("Send this to someone who needs it"), save-bait (the payoff line is screenshot-worthy).

---

### 3.2 Talking Head (`talking_head`)

**Use for:** Hot takes, unpopular opinions, debate starters, direct-to-camera commentary.

**Duration:** 15-30 seconds
**Structure:**
```
BOLD STATEMENT (0:00-0:03)
  The opinion appears as bold text BEFORE the speaker says it.
  Text arrives at frame 1. Speaker starts talking at 0:01.
  [TEXT ON SCREEN: The opinion -- bold sans-serif, all-caps, centered]
  [SPEAKER: Confident posture, direct eye contact with lens]

QUICK REASONING (0:03-0:20)
  2-3 rapid-fire reasons supporting the take.
  No filler words. No hedging. Conviction sells.
  Each reason gets its own text overlay (brief, 3-5 words).
  [TEXT ON SCREEN: Reason keywords appearing and dissolving]
  [PACING: Fast, confident, every sentence lands]
  [SPEAKER: Gestures for emphasis, natural movement]

CHALLENGE VIEWER (last 5-10 seconds)
  "Stitch this if you disagree."
  "Duet this with your hot take."
  "Tell me I'm wrong in the comments."
  [TEXT ON SCREEN: The challenge -- bold, direct]
  [SPEAKER: Leans in slightly, half-smile or raised eyebrow]
```

**Hook technique:** The opinion IS the hook. It must be bold enough to polarize. Ogilvy's specificity principle: "First-look photos are better than ceremony photos" beats "candid photos are best."

**Pacing:** Fast. Confident. No wasted syllables. This is not a conversation -- it is a declaration.

**Music:** Optional. Trending audio can boost discovery. If used, low and percussive -- never emotional.

**Engagement hooks:** Stitch-bait ("Stitch this if..."), duet-bait ("Duet with your version"), comment-bait ("Tell me I'm wrong").

---

### 3.3 Listicle Reel (`listicle_reel`)

**Use for:** Tips, lists, "X things nobody tells you about...", advice compilations.

**Duration:** 15-45 seconds
**Structure:**
```
HOOK (0:00-0:03)
  "X things nobody tells you about [topic]"
  Number on screen first, then the subject.
  [TEXT ON SCREEN: Number + topic -- large, bold]
  [MUSIC: Upbeat trending audio, energy from beat 1]

ITEMS (0:03-0:35)
  Each item: 3-5 seconds. One beat per point.
  Structure per item:
    - Number appears (large, animated pop)
    - Key phrase as text overlay (5-8 words max)
    - Supporting visual or quick B-roll
    - Transition (cut, zoom, swipe) to next number
  [TEXT ON SCREEN: Numbered items as bold overlays]
  [PACING: FAST. Each point gets one beat. No lingering.]
  [B-ROLL: Quick matching visual per point -- 2-3 seconds each]
  [MUSIC: Beat-aligned transitions -- each item lands on a beat]

CLOSER (last 5-8 seconds)
  Bonus item or summary that ties them together.
  "Follow for more [topic]" or "Save this for later."
  [TEXT ON SCREEN: "Save this" or "Follow for more"]
  [MUSIC: Audio resolves or loops]
```

**Hook technique:** Sugarman's curiosity gap. The number creates an open loop the viewer must close by watching all items.

**Pacing:** Fastest of all formats. If a point takes more than 5 seconds, split it or cut it. Each item should feel like a punch.

**Music:** Upbeat trending audio is non-negotiable. The beat structure drives the cut timing -- each item should land on a musical beat.

**Engagement hooks:** Save-bait ("Save this for later"), share-trigger ("Send this to someone who needs #3"), comment-bait ("Which one surprised you?").

---

### 3.4 Question Hook (`question_hook`)

**Use for:** Conversation starters, posts inviting personal stories, calibrated questions (Voss).

**Duration:** 10-20 seconds
**Structure:**
```
QUESTION (0:00-0:03)
  The question itself -- large text, centered.
  No preamble. The question IS the entire opening.
  [TEXT ON SCREEN: The question -- large, clean, bold]
  [MUSIC: Curiosity-evoking audio, soft emotional start]

RELATABLE VISUAL (0:03-0:15)
  B-roll that visually represents the question's emotional territory.
  Slow, evocative, cinematic.
  Let the viewer's mind start forming their own answer.
  [B-ROLL: Emotionally resonant footage matching the question's mood]
  [MUSIC: Building gently]
  [TEXT ON SCREEN: Optional -- context line or label ("It sounds like everyone has that one moment...")]

REPEAT + INVITE (last 3-5 seconds)
  Question reappears on screen.
  "Comment below" or "Tell us in the comments."
  [TEXT ON SCREEN: Question again + "Comment your answer"]
  [MUSIC: Gentle resolve]
```

**Hook technique:** Voss calibrated questions. "What" and "how" questions that invite stories, never "why" (defensive) or yes/no (dead end). "What would you tell your younger self?" makes people ache to answer.

**Pacing:** Slow. Contemplative. This format works by creating emotional space for the viewer to project their own experience.

**Music:** Soft emotional or curiosity-evoking audio. Never upbeat. The mood should make the viewer pause and reflect.

**Engagement hooks:** Comment-bait is the entire point. The question must be specific enough to trigger a real answer but universal enough that everyone has one.

---

### 3.5 Interactive Poll (`interactive_poll`)

**Use for:** "Pick one," "choose one," "one has to go," "eliminate one" posts.

**Duration:** 10-20 seconds
**Structure:**
```
DIRECTIVE (0:00-0:02)
  "Which one?" or "One has to go" -- text on screen.
  [TEXT ON SCREEN: The directive -- bold, playful]
  [MUSIC: Playful, upbeat, trending audio]

OPTION REVEAL (0:02-0:14)
  Two approaches:
  A) Split screen: All 4 options visible simultaneously
  B) Sequential reveal: Each option appears one at a time (2-3 sec each)
  Each option: numbered (1-4), clearly labeled, visually distinct.
  [TEXT ON SCREEN: Option labels with numbers]
  [B-ROLL: Representative visual for each option]
  [PACING: Brisk reveals, slight pause on each for recognition]

COMMENT INVITE (last 3-5 seconds)
  "Comment your pick"
  "Tag someone who'd pick #2"
  [TEXT ON SCREEN: "Drop your number in the comments"]
  [MUSIC: Continues, light and playful]
```

**Hook technique:** The interactive mechanic IS the hook. Low effort to participate, high social visibility. Every comment is a public vote.

**Pacing:** Medium-fast. Options need enough time to be recognized but not so long that momentum dies.

**Music:** Playful and upbeat. Game-show energy without being cheesy.

**Engagement hooks:** Comment-bait (picking a number is the lowest-friction comment possible), tag-bait ("Tag someone who'd pick #3"), debate-bait (people defend their choice and argue with others).

---

### 3.6 Nostalgia Montage (`nostalgia_montage`)

**Use for:** "Remember when" posts, decade references, "back in the day," era-specific nostalgia.

**Duration:** 30-60 seconds
**Structure:**
```
ERA ANCHOR (0:00-0:05)
  Establish the time period immediately.
  A date, a decade name, or an era-defining object.
  [TEXT ON SCREEN: The era reference -- "1997" or "The 90s" -- typewriter or era-appropriate font]
  [MUSIC: Era-appropriate track OR modern emotional track]
  [VISUAL: Era-establishing shot (film grain, warm color grade)]

NOSTALGIC MOMENTS (0:05-0:40)
  Series of specific memories from the era.
  Each moment: 3-5 seconds, one visual + one text line.
  Pull directly from the post's concrete details.
  Match the image-director-engagement's era guide for color treatment:
    - 70s: Warm orange/brown, wood paneling, muscle cars
    - 80s: High saturation, neon, arcade machines, boomboxes
    - 90s: Muted green-shifted, disposable cameras, dial-up, malls
    - 2000s: Oversaturated, flip phones, early iPods
    - "Childhood" generic: Sun-drenched, sprinklers, bike rides
  [B-ROLL: Era-appropriate scenes, each 3-5 seconds]
  [TEXT ON SCREEN: Each memory as a brief text line -- minimal, let visuals carry]
  [PACING: Slower than other formats. Contemplative. Let nostalgia breathe.]
  [MUSIC: Building emotional resonance]

EMOTIONAL CLOSER (last 10-15 seconds)
  The line that connects nostalgia to emotion.
  "We didn't know it then, but those were the best days."
  "You didn't get to see any of them for 2 weeks. And somehow, those are the ones you still have framed."
  [TEXT ON SCREEN: The closing line -- centered, larger, pause before it appears]
  [MUSIC: Emotional peak, then gentle fade]
  [B-ROLL: Final evocative image held for 3-5 seconds]
```

**Hook technique:** Berger's triggers. Decade references and era-specific objects are powerful daily triggers for the Facebook/Instagram core audience (millennials, Gen X, boomers). One specific object ("disposable cameras at every table") does more than ten vague references.

**Pacing:** Slower than other formats. Nostalgia requires contemplation. Rush it and you kill the spell. But still -- no moment longer than 5 seconds. The montage structure maintains forward motion.

**Music:** Era-appropriate is ideal (an actual 90s track creates instant recognition). Modern emotional instrumental is the safe alternative. The music IS half the nostalgia.

**Style:** Film grain mandatory. Era-appropriate color grading. No modern elements visible anywhere. One anachronism (a smartphone in a 90s scene) destroys the entire mood.

**Engagement hooks:** Share-trigger ("Send this to someone you grew up with"), comment-bait ("Drop a memory from your childhood"), tag-bait ("Tag your 90s crew").

---

### 3.7 Emotional Narrative (`emotional_narrative`)

**Use for:** Deeply emotional content, heartwarming stories, awe-inspiring moments, content that needs space to land.

**Duration:** 45-90 seconds
**Structure:**
```
QUIET HOOK (0:00-0:05)
  A single line. Understated. Almost whispered.
  The quiet intensity stops the scroll because it contrasts with everything else in the feed.
  [TEXT ON SCREEN: The hook line -- elegant font, not bold, centered]
  [MUSIC: Near-silence, then a single note or gentle piano]
  [VISUAL: Slow fade in from dark or a single, still image]

SLOW BUILD (0:05-0:25)
  The story unfolds at half the pace of any other format.
  Voiceover in the Voss "late-night FM DJ" voice:
  warm, calm, personal, short sentences, declarative, no exclamation marks.
  Downward energy. The written equivalent of a hand on your shoulder.
  [VOICEOVER: Warm, intimate, low pitch, measured pace -- 120 wpm max]
  [B-ROLL: Cinematic, shallow depth of field, natural lighting]
  [MUSIC: Slowly building, one instrument at a time]
  [PACING: One visual every 4-6 seconds. Let moments exist.]

EMOTIONAL CLIMAX (0:25-0:50)
  The payoff. The moment that makes the viewer's chest tighten.
  Everything in the script builds to this single moment.
  PAUSE before the climactic line. 1-2 seconds of silence.
  Then the line lands.
  [VOICEOVER: Slight pause, then the payoff line delivered slowly]
  [MUSIC: Full emotional swell -- multiple instruments, crescendo]
  [TEXT ON SCREEN: The payoff line -- large, centered, held on screen for 3-4 seconds]
  [B-ROLL: The defining visual -- hold it. Don't cut away.]

GENTLE CLOSE (0:50-end)
  Resolution. Not a punchline -- a landing.
  The feeling should linger after the video ends.
  [VOICEOVER: Final line, gentle, almost to self]
  [MUSIC: Slowly fading, one instrument remaining]
  [TEXT ON SCREEN: Optional -- "Share if this hit you" or nothing at all]
```

**Hook technique:** Contrast. In a feed full of loud, fast, bright content, the quiet opening is the pattern interrupt. Sugarman's first-sentence rule adapted: "Make it short." But here, make it quiet.

**Pacing:** The slowest format. 120 wpm maximum for voiceover (vs. 170 wpm for other formats). If the video feels rushed, the emotion evaporates. The pause before the climax is the most important half-second in the entire script.

**Music:** Building emotional track. Start near-silent. Add instruments gradually. Peak at the climax. The music does 40% of the emotional work -- script it carefully.

**Voiceover direction:** Voss Layer C.5 "Late-Night FM DJ Voice." Warm. Calm. Personal. Short sentences. Declarative. No exclamation marks. The voice should feel like a friend thinking out loud at midnight.

**Engagement hooks:** Share-trigger (the emotion itself compels sharing -- "I need everyone to see this"), save-bait (viewers save emotional videos to rewatch), comment-bait (people share their own version of the story).

---

### 3.8 Comedy Skit (`comedy_skit`)

**Use for:** Humor, irony, relatability, "me when" moments, absurd observations.

**Duration:** 10-30 seconds
**Structure:**
```
SETUP (0:00-0:05)
  Establish the relatable scenario instantly.
  "POV: You're at [relatable situation]"
  OR: Show the normal version of the situation.
  [TEXT ON SCREEN: "POV:" or situation description -- appears frame 1]
  [MUSIC: Trending comedy audio if applicable]
  [VISUAL: Normal, recognizable scenario]

EXPECTATION (0:05-0:15)
  Build the expected outcome. Let the viewer think they know where this is going.
  The longer you hold the expectation, the bigger the punchline hits.
  But don't hold too long -- 10 seconds maximum.
  [VISUAL: The expected trajectory playing out]
  [PACING: Normal -- matching the "normal" feel of the scenario]

SUBVERSION / PUNCHLINE (0:15-0:25)
  The twist. The unexpected outcome. The relatable overreaction.
  Timing is everything: the cut to the punchline should be ABRUPT.
  No transition. No build. SMASH CUT to the funny part.
  [TEXT ON SCREEN: Punchline as text overlay -- bold, large, for rewatchability]
  [MUSIC: Beat drop, record scratch, or comedic audio sting]
  [VISUAL: The subverted reality -- exaggerated or absurd version]
  [PACING: FAST. The punchline lands in 2-3 seconds.]

TAG (last 3-5 seconds, optional)
  Brief reaction shot or "that moment when" freeze frame.
  [TEXT ON SCREEN: "Tag someone who does this" or relatable tagline]
```

**Hook technique:** The POV format or the relatable scenario creates instant identification. The viewer sees themselves in the setup and MUST see how it plays out.

**Pacing:** Setup at normal speed. Punchline at FAST speed. The speed differential IS the comedy. A slow punchline kills the joke.

**Music:** Trending comedy audio is a massive discovery booster. If using original audio, a beat drop or comedic sting at the punchline.

**Text overlay:** The punchline MUST be text on screen even if spoken. This is for rewatchability -- people will rewatch to screenshot or show a friend.

**Engagement hooks:** Tag-bait ("Tag someone who does this"), share-trigger (the relatability drives "literally me" shares), comment-bait ("I've never felt more seen"), duet-bait (others recreating the scenario).

---

### 3.9 Text Reveal (`text_reveal`)

**Use for:** Fill-in-the-blank posts, surprising facts, dramatic reveals, hot takes.

**Duration:** 10-15 seconds
**Structure:**
```
PARTIAL TEXT (0:00-0:04)
  Show the incomplete text on screen.
  The blank or missing part creates a curiosity gap.
  [TEXT ON SCREEN: The partial statement -- large, centered, bold]
  [BACKGROUND: Clean, simple -- solid color or subtle gradient]
  [MUSIC: Suspense/anticipation audio -- building tension]

PAUSE (0:04-0:07)
  Hold the incomplete text. Let the viewer's mind race to fill it in.
  This pause is the entire mechanic. Do not rush it.
  [VISUAL: Same text, held. Maybe a subtle zoom or pulse effect.]
  [MUSIC: Building to the moment...]

REVEAL (0:07-0:12)
  The complete text appears. The blank is filled.
  The reveal should feel like a punch -- instant, no fade-in.
  [TEXT ON SCREEN: Full statement -- the missing word/phrase appears bold or in a different color]
  [MUSIC: Reveal sting -- beat drop, dramatic chord, or satisfying sound]
  [VISUAL: Text animation -- the reveal word zooms in, slides in, or pops]

REACTION BEAT (0:12-0:15)
  Brief hold on the complete text. Let it sink in.
  [TEXT ON SCREEN: "Did you get it right?" or "Comment yours below"]
  [MUSIC: Resolving]
```

**Hook technique:** Sugarman's curiosity trigger (#19) and mental engagement (#27). The incomplete information creates psychological tension the viewer MUST resolve. Not showing everything forces the mind to work -- and that engagement holds attention.

**Pacing:** Slow build to instant reveal. The rhythm is: anticipation... anticipation... BANG.

**Music:** Suspense/reveal audio is essential. The audio cue at the reveal moment amplifies the payoff 3x.

**Text:** Text IS the only visual element. No photography, no B-roll, no faces. Bold, centered, dramatic typography on a clean background. The simplicity is the format.

**Engagement hooks:** Comment-bait (viewers comment their own answer before the reveal), replay-bait (short enough to loop -- many will rewatch).

---

### 3.10 Relatable Montage (`relatable_montage`)

**Use for:** "Tag someone who," universal experiences, "that feeling when," relatable everyday moments.

**Duration:** 15-30 seconds
**Structure:**
```
POV STATEMENT (0:00-0:03)
  "POV: [relatable situation]"
  The statement stays on screen as a permanent overlay throughout.
  [TEXT ON SCREEN: POV statement -- top or bottom third, permanent]
  [MUSIC: Trending audio -- the audio is critical for discovery]

MONTAGE (0:03-0:25)
  3-5 quick clips illustrating the relatable scenario.
  Each clip: 2-4 seconds, one visual gag or recognizable moment.
  The clips should escalate -- each one slightly more relatable or exaggerated.
  [B-ROLL: Quick clips, each showing a different angle of the relatable scenario]
  [PACING: Fast cuts -- 2-4 seconds per clip, aligned to music beats]
  [TEXT ON SCREEN: POV statement remains. Optional: brief caption per clip]

CLOSER (last 3-5 seconds)
  The most relatable clip or a freeze-frame with tag invitation.
  [TEXT ON SCREEN: "Tag someone" or "If this isn't you, you're lying"]
  [MUSIC: Audio continues to natural loop point]
```

**Hook technique:** Identification. The POV statement is a self-selection filter. The viewer either sees themselves and watches every clip, or they don't and scroll past. But the specificity of the statement ("POV: you're the friend who always has snacks in their bag") targets so precisely that the target audience CANNOT scroll past.

**Pacing:** Fast cuts, beat-aligned. Each clip should land on a musical beat. The escalation creates a "yes, yes, YES" feeling.

**Music:** Trending audio is the primary discovery mechanism for this format. The audio choice matters more than the visuals.

**Engagement hooks:** Tag-bait ("Tag your friend who does this"), share-trigger (people share themselves into the scenario), comment-bait ("If this isn't you, you're lying").

---

## 4. The 3-Second Rule

EVERY video format must pass the 3-second test. In the FIRST 3 SECONDS, the viewer must encounter something that stops them from scrolling. The algorithm measures 1-second and 3-second retention -- if viewers don't stay past 3 seconds, the video is algorithmically dead.

### 3-Second Hook Strategies

| Strategy | When to Use | Example |
|----------|------------|---------|
| **Bold text first** | Talking head, text reveal, listicle | Text appears at frame 1, before any audio registers |
| **Mid-action visual** | Story reel, emotional narrative | Drop into the middle of a moment -- crying, laughing, embracing |
| **Surprising statement** | Any format | "Nobody's talking about this." / "Stop doing this." |
| **Face showing emotion** | Story reel, comedy, talking head | A genuine human expression (joy, shock, tears) stops the scroll |
| **Familiar trending audio** | Relatable montage, comedy skit | The first note of a trending sound creates instant recognition |
| **Pattern interrupt** | Any format | Unexpected movement, unusual camera angle, visual clash |

### Rules

1. Text overlays must appear within 0.5 seconds -- before audio even registers on mobile
2. Never start with a logo, brand name, or "welcome to..."
3. Never start with a slow fade-in or establishing shot
4. Never start with "Hey guys" or any generic greeting
5. The hook must be comprehensible with sound OFF (85% of Facebook viewers watch muted)

---

## 5. STEPPS Video Scoring

Every video script gets scored against STEPPS specifically for the VIDEO component (independent of the post text). The video alone must contribute to virality.

### Video STEPPS Diagnostic

| Principle | Scoring Question | Scoring Guide |
|-----------|-----------------|---------------|
| **Social Currency** | Will sharing this VIDEO make the sharer look good, tasteful, or emotionally intelligent? | 0 = generic / 5 = "I need to share this" |
| **Triggers** | Is the video tied to an everyday moment (morning routine, commute, bedtime, weekend)? | 0 = abstract / 5 = triggers a daily moment |
| **Emotion** | Does the first 5 seconds evoke HIGH-AROUSAL emotion (awe, excitement, humor, anger)? | 0 = flat / 5 = gut-punch feeling |
| **Public** | Will engagement be visible? (comments, stitches, duets, shares show up in friends' feeds) | 0 = passive viewing / 5 = engagement is the point |
| **Practical Value** | Is this video useful enough to forward to a specific person? | 0 = entertainment only / 5 = "my friend needs this" |
| **Stories** | Is there a retellable narrative arc someone would describe to a friend? | 0 = no arc / 5 = "let me tell you about this video I saw" |

### Scoring Rules

- Score each principle 0-5
- Total possible: 30
- **Minimum threshold: 16/30** -- below this, rework the script
- **At least 3 principles must score 3+**
- **Emotion must score 3+** -- if the video evokes nothing, it fails regardless of total

### Format-Typical Score Profiles

| Format | Social Currency | Triggers | Emotion | Public | Practical | Stories | Typical Total |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| story_reel | 4 | 3 | 5 | 3 | 2 | 5 | 22 |
| talking_head | 4 | 2 | 4 | 5 | 2 | 1 | 18 |
| listicle_reel | 3 | 3 | 2 | 3 | 5 | 1 | 17 |
| question_hook | 3 | 3 | 4 | 5 | 2 | 2 | 19 |
| interactive_poll | 3 | 2 | 2 | 5 | 1 | 1 | 14* |
| nostalgia_montage | 5 | 4 | 5 | 3 | 1 | 5 | 23 |
| emotional_narrative | 5 | 3 | 5 | 3 | 1 | 5 | 22 |
| comedy_skit | 5 | 3 | 5 | 4 | 1 | 2 | 20 |
| text_reveal | 3 | 2 | 3 | 4 | 2 | 1 | 15* |
| relatable_montage | 4 | 4 | 4 | 4 | 1 | 2 | 19 |

*interactive_poll and text_reveal naturally score lower on STEPPS -- acceptable at 14-15 if the engagement mechanic is strong.

---

## 6. Platform-Specific Rules

### Facebook Reels (Primary Target)

- **15-90 seconds** optimal (30 seconds is the sweet spot for engagement)
- **Vertical 9:16** (1080 x 1920) -- mandatory
- **Captions/subtitles MANDATORY** -- 85% of Facebook users watch video without sound
- Hook in first 1-2 seconds (text on screen before audio)
- Loop potential: last frame should visually connect back to first for rewatch behavior
- Avoid ad-like aesthetics -- Facebook's algorithm de-prioritizes ad-looking content in organic feeds
- Caption script must be word-for-word accurate (not a summary) for accessibility
- Native upload always outperforms cross-posted content

### Instagram Reels

- **15-60 seconds** optimal (shorter performs better)
- **Vertical 9:16** (1080 x 1920)
- Higher aesthetic bar than Facebook -- cleaner color grading, more intentional composition
- Trending audio boosts reach significantly -- include trending audio recommendations
- Hashtags in caption (not on video) for discovery
- Cover frame matters -- the still thumbnail should be compelling standalone

### TikTok

- **15-60 seconds** optimal (shorter = higher completion rate = better algorithm performance)
- **Vertical 9:16** (1080 x 1920)
- Stitch/duet hooks are a primary engagement driver -- script explicit stitch/duet invitations
- Green screen format popular for commentary -- include as a variant when the post is opinion-based
- Authenticity > production value. Slightly raw, slightly imperfect performs better.
- The algorithm heavily weights completion rate -- shorter videos that loop get pushed further

### Cross-Platform Video Rules

| Rule | Rationale |
|------|-----------|
| Always vertical 9:16 | Horizontal = death in feed. Maximum screen real estate. |
| Text readable at mobile size | Minimum 40pt equivalent. Contrast with background. |
| Captions for every spoken word | Sound-off is the default viewing mode |
| No external links or URLs | Kills organic reach on every platform |
| First text at 0.5 seconds | Before audio registers on autoplay |
| Transition every 2-4 seconds | Maintains attention in short-form |
| Pattern interrupt every 5-7 seconds | Zoom, cut, text pop, music change |
| End with loop point or question | Drives rewatch or comment |

---

## 7. Script Output Format

Write a script spec JSON file for each post that needs a video.

```json
{
  "taskId": "task_xxx",
  "parentResourceId": "resource_xxx",
  "videoIntent": "story_reel",
  "platform": "facebook_reels",
  "duration": {
    "target": 30,
    "min": 20,
    "max": 45
  },
  "dimensions": {
    "width": 1080,
    "height": 1920,
    "aspectRatio": "9:16"
  },
  "script": {
    "hook": {
      "timestamp": "0:00-0:03",
      "action": "Close-up of hands opening an old box. Inside: a napkin with a coffee stain.",
      "text_overlay": "She kept the napkin from their first date for 23 years.",
      "audio": "Trending emotional piano -- first notes only",
      "voiceover": null
    },
    "body": [
      {
        "timestamp": "0:03-0:10",
        "action": "Wide shot: couple at a cafe table, golden hour light",
        "text_overlay": null,
        "broll": "Warm cafe interior, two coffee cups, sunlight through window",
        "voiceover": "She almost threw it away three times."
      },
      {
        "timestamp": "0:10-0:20",
        "action": "Close-up of napkin, then pan to framed photo beside it",
        "text_overlay": "Three moves. Two apartments. One house.",
        "broll": "Moving boxes, new apartment, settling in",
        "voiceover": "It survived three moves, two apartments, and one house."
      }
    ],
    "cta": {
      "timestamp": "0:25-0:30",
      "action": "Return to hands holding the napkin, gentle close",
      "text_overlay": "What's the small thing you kept? Comment below."
    }
  },
  "musicDirection": "Emotional piano, trending, building -- peak at 0:20, gentle fade to close",
  "captionScript": "She kept the napkin from their first date for 23 years. She almost threw it away three times. It survived three moves, two apartments, and one house. The napkin isn't special. The morning it came from is.",
  "steppsVideoScore": {
    "socialCurrency": 4,
    "triggers": 3,
    "emotion": 5,
    "public": 3,
    "practicalValue": 2,
    "stories": 5,
    "total": 22
  },
  "engagementHooks": ["comment-bait", "share-trigger", "save-bait"],
  "loopPoint": "Last frame (hands on napkin) visually mirrors first frame (hands opening box) -- encourages rewatch",
  "metadata": {
    "postFormat": "Emotional Story",
    "sourcePostNumber": 7,
    "focusGroup": "Newlyweds",
    "hookTechnique": "Halbert mid-action + Ogilvy specificity (23 years)",
    "vossLayer": "C.5 Late-Night FM DJ Voice for voiceover",
    "generatedAt": "2026-02-15T14:30:00Z"
  }
}
```

Write to: `{outputDir}/script-engagement-{intent}-{postNumber}-{taskId}.json`

---

## 8. Engagement-Specific Pacing Rules

These rules govern the rhythm of EVERY engagement video. They are non-negotiable. The algorithm measures micro-retention (1-second, 3-second, average watch time, completion rate) and rewards videos that hold attention second by second.

### The Attention Architecture

| Timing | Rule | Why |
|--------|------|-----|
| 0.0-0.5s | Text overlay must appear | Catches eye before audio autoplay registers |
| 0.0-1.0s | Visual must be compelling | 1-second retention is the first algorithm gate |
| 0.0-3.0s | Hook must land | 3-second retention determines if the algorithm pushes the video |
| Every 2-4s | Scene change or visual transition | Human attention resets at transitions -- each one re-earns attention |
| Every 5-7s | Pattern interrupt (zoom, cut, text pop, music shift) | Prevents passive viewing, re-engages active attention |
| At emotional peaks | SLOW the pacing | Let the moment breathe -- contrast with fast sections amplifies impact |
| Last 2-3s | Loop point or engagement CTA | Drives rewatch (loop) or comment (CTA) -- both boost algorithm metrics |

### Music-Cut Alignment

- Major transitions should land on musical beats
- Text reveals should coincide with beat drops or audio stings
- Voiceover cadence should complement (not fight) the music rhythm
- Silence before a beat drop is more powerful than continuous audio

### The No-Dead-Air Rule

Every second of video must earn the next second. Adapted from Sugarman's Slippery Slide:

> The sole purpose of each SECOND of video is to get the viewer to watch the NEXT second.

If any moment in the script could be removed without losing the viewer, that moment is dead air. Cut it. Engagement video has zero tolerance for filler.

---

## 9. Multi-Article Campaign Mode

When the task description contains "Produce N articles in a single pipeline run" or the task has multiple parent social_post resources:

### 1. Parse post count
Extract N from the task description or count the social_post resources returned by `resources:listByTaskAndType`.

### 2. Load parent post resources
```bash
POSTS=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"social_post"
}' --url http://localhost:3210)
```

### 3. Check existing video scripts (skip-already-done)
```bash
EXISTING=$(npx convex run resources:listByTaskAndType '{
  "taskId":"<TASK_ID>","resourceType":"video_script"
}' --url http://localhost:3210)
```
Skip posts that already have associated video scripts (match via `parentResourceId`).

### 4. Create video scripts for EACH post
For each post resource:
- Read the post content from `filePath` or `content` field
- Determine video intent (Section 2)
- Skip posts with video intent NONE
- Run the full script writing protocol
- Register each video script as a CHILD resource:

```bash
npx convex run resources:create '{
  "projectId": "<PROJECT_ID>",
  "resourceType": "video_script",
  "title": "Engagement video script: <intent> for Post <i>",
  "campaignId": "<CAMPAIGN_ID>",
  "taskId": "<TASK_ID>",
  "parentResourceId": "<POST_RESOURCE_ID>",
  "filePath": "<path to script JSON>",
  "status": "draft",
  "createdBy": "vibe-script-writer",
  "metadata": {
    "videoIntent": "<intent>",
    "platform": "<target platform>",
    "durationTarget": <seconds>,
    "steppsVideoScore": <total>,
    "engagementHooks": ["<hook1>", "<hook2>"]
  }
}' --url http://localhost:3210
```

For efficiency with many scripts, use `resources:batchCreate`.

### 5. Call completeBranch ONCE
Pass ALL video script resource IDs in a single call:

```bash
npx convex run pipeline:completeBranch '{
  "taskId": "<TASK_ID>",
  "branchLabel": "video-script",
  "agentName": "vibe-script-writer",
  "resourceIds": ["id1","id2","id3"]
}' --url http://localhost:3210
```

> See `.claude/skills/shared-references/resource-registration.md` for the full multi-article protocol.

---

## 10. Quality Gates

Every video script must pass ALL gates before output.

### Gate 1: 3-Second Hook Test
- Would YOU stop scrolling at this hook?
- Does text appear within 0.5 seconds?
- Is the hook comprehensible with sound off?
- **FAIL action:** Rewrite the first 3 seconds. Try a different hook strategy from Section 4.

### Gate 2: Sound-Off Test
- Is the ENTIRE video understandable with captions only?
- Are all text overlays readable at mobile thumbnail size?
- Do captions carry the complete narrative without relying on audio-only elements?
- **FAIL action:** Add text overlays for any audio-only moments. Ensure caption script covers every spoken word.

### Gate 3: STEPPS Video Score
- Total must be 16+ / 30 (14+ acceptable for interactive_poll and text_reveal)
- At least 3 principles must score 3+
- Emotion must score 3+
- **FAIL action:** Identify the weakest principle and strengthen. Usually: add a specific emotional hook, tie to a daily trigger, or add a visible engagement mechanic.

### Gate 4: Duration Check
- Duration within platform optimal range (see Section 6)
- No section exceeds its allocated time
- Total word count aligns with speaking pace (170 wpm for fast formats, 120 wpm for emotional narrative)
- **FAIL action:** Trim to fit. Cut the weakest section, not the hook or payoff.

### Gate 5: Engagement Hook Presence
- At least 1 engagement hook present: stitch-bait, comment-bait, share-trigger, duet-bait, save-bait, tag-bait, replay-bait
- Engagement hook appears in the final 5 seconds (text on screen or voiceover)
- **FAIL action:** Add an engagement CTA to the closing section. Never generic ("like and subscribe") -- always specific to the content.

### Gate 6: No Sales Language
- Zero commercial intent: no "buy," "shop," "link in bio," "discount," "limited time offer"
- No product names, brand names, or URLs in the script
- The video must feel like organic content, not an advertisement
- **FAIL action:** Remove all commercial language. Replace with engagement-only CTAs.

### Gate 7: Format-Intent Match
- Does the video format match the post's intent?
- Story posts must use story_reel or emotional_narrative, not listicle_reel
- Opinion posts must use talking_head, not emotional_narrative
- Interactive posts must use interactive_poll, not story_reel
- **FAIL action:** Reassign format using the Detection Table (Section 2).

---

## 11. Engagement Psychology -- Video Principles

These principles, synthesized from Berger (STEPPS for video virality), Sugarman (slippery slide for video hooks), Ogilvy (specificity in scripts), Voss (late-night FM DJ voice for voiceovers), and Halbert (mid-action openers), govern WHY certain videos stop the scroll and drive engagement.

### 11.1 The Video Slippery Slide (Sugarman)

In print, the first sentence exists only to get the reader to read the second sentence. In video, the first SECOND exists only to get the viewer to watch the next second. Every frame pulls forward.

**Apply by:**
- Opening with movement, text, or emotion -- never stillness
- Using seeds of curiosity at section transitions: "But that's not the part that got me" (voiceover), or a visual that implies "something is about to happen"
- Never resolving the emotional or informational loop until the payoff section
- Building momentum with progressively longer shots (2s, 3s, 4s) then snapping back to fast cuts at transition points

### 11.2 Specificity Creates Believability (Ogilvy)

Specific details in video scripts make them feel REAL. Generic scripts feel like stock footage.

**Apply by:**
- "A 1996 Toyota Corolla with a dented fender" in the B-roll notes, not "a car"
- "3:47 AM on a Tuesday" as text on screen, not "late one night"
- "She came home with 2,847 photos and deleted all but 11" -- numbers stop scrollers
- One imperfect detail in every scene: scratched table, wrinkled shirt, chipped mug
- Specific timestamps in voiceover: "It was June 14th. A Wednesday."

### 11.3 Mid-Action Openers (Halbert)

Start in the middle of a moment. The viewer's brain scrambles to catch up -- and that scramble IS the hook.

**Apply by:**
- First frame: the moment of impact, not the wind-up
- "She opened the box" -- not "She sat down at the table, reached across, and opened a box"
- Drop the viewer into an already-moving scene. No establishing shots. No context. The context comes AFTER the hook.
- The "They Laughed When..." pattern works perfectly in video: show the mockery first, THEN reveal what happened next.

### 11.4 Late-Night FM DJ Voice (Voss)

For voiceover-driven formats (story_reel, emotional_narrative), the voice quality matters as much as the words.

**Direction for voiceover:**
- Warm, calm, personal tone
- Short sentences. Declarative.
- No exclamation marks. Downward energy.
- Speak as if talking to one person at 1 AM, not an audience of thousands
- 120-140 wpm (slower than normal video pace)
- Strategic pauses before important lines -- let the silence build anticipation

### 11.5 High-Arousal Emotion in Video (Berger)

Video amplifies emotion 3-5x compared to text. A sad text post becomes a devastating video. A funny text post becomes a viral reel. The medium is the amplifier.

**Apply by:**
- Using music as an emotion multiplier (the right song does half the work)
- Showing FACES with genuine expressions (humans are wired to mirror facial emotions)
- Slowing pacing at emotional peaks (the pause before the payoff)
- Using warm color grading (amber, golden) for emotional content
- Building to ONE moment, not scattering emotion across the whole video

---

## 12. Integration Points

| Upstream | This Skill | Downstream |
|----------|-----------|------------|
| `vibe-facebook-engine` (social_post resources with Video Intent) | video-script-engagement (analyze + write script) | `vibe-video-generator` (produce video) |
| Any engagement agent (social_post resources without Video Intent) | video-script-engagement (infer intent + write script) | `vibe-video-generator` (produce video) |
| `image-director-engagement` (parallel branch -- image prompts) | video-script-engagement (parallel branch -- video scripts) | Dashboard (display both for review) |
| Campaign focus groups (audience data) | video-script-engagement (tone, cultural refs) | Content review pipeline |

---

## 13. Anti-Patterns

| # | Anti-Pattern | What Goes Wrong |
|---|-------------|----------------|
| AP-01 | **Starting slow** | A slow fade-in or "Hey guys" opening. The algorithm kills reach in the first 3 seconds. |
| AP-02 | **Sales language** | "Link in bio," "Buy now," "Limited offer." Engagement videos are engagement-ONLY. |
| AP-03 | **Wrong format for intent** | Using emotional_narrative for a listicle post. The format must match the content's natural energy. |
| AP-04 | **No captions** | 85% watch on mute. No captions = no engagement from the majority of viewers. |
| AP-05 | **Horizontal video** | Posting 16:9 in a 9:16 feed. Massive wasted screen real estate. Algorithmic death. |
| AP-06 | **Too long** | A 3-minute engagement video. Short-form means SHORT. 15-60 seconds for most formats. |
| AP-07 | **No text overlays** | Relying on audio alone for the hook. Text must appear at frame 1 (within 0.5 seconds). |
| AP-08 | **Generic music** | Using elevator music instead of trending audio. Trending audio = algorithmic boost. |
| AP-09 | **Over-produced aesthetic** | Studio lighting, professional color grading, corporate feel. Engagement videos should feel human-made, slightly imperfect. |
| AP-10 | **No engagement CTA** | Ending without a comment-bait, stitch-bait, or share-trigger. The last 5 seconds drive the engagement metrics. |
| AP-11 | **Skipping STEPPS scoring** | Generating scripts without scoring means no quality control on video virality. Every script gets scored. |
| AP-12 | **Dead air** | Any second of video that doesn't pull the viewer to the next second. Adapted from Sugarman: every second must earn the next. |

---

## 14. Error Handling

- **Missing parent posts:** Set task to `blocked`, log "No social_post resources found for task"
- **Video intent NONE:** Skip gracefully, do not create a video_script resource for that post
- **Ambiguous intent:** Default to `story_reel` -- the most versatile engagement format
- **Missing focus group data:** Use neutral emotional defaults (warm, human, authentic)
- **Duration exceeds platform range:** Trim to fit. Cut the weakest section, keep the hook and payoff.
- **Post content too short to script:** Default to `text_reveal` for short content or `question_hook` for questions
- **Service unavailable:** Log warning, output script JSON for manual processing

---

## What This Skill Does NOT Cover

- **Video production/generation** -- that is `vibe-video-generator`'s job
- **Image/thumbnail creation** -- that is `vibe-image-director` + `vibe-image-generator`
- **YouTube long-form, VSL, webinar, explainer, testimonial scripts** -- use `video-script-sales` for non-engagement video
- **Audio recording or voiceover production** -- production team responsibility
- **Sales/campaign video scripts** -- use `video-script-sales` for commercial content
- **Video editing or post-production** -- downstream tooling
- **Which marketing skills to load** -- decided by campaign `skillConfig` and agent `dynamicSkillIds`
- **Social post copy for promoting the video** -- that is `vibe-social-writer`'s job
