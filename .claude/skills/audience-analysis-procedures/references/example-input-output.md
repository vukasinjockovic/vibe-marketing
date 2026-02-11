# Example: Raw Text to Structured JSON

## Input (Raw Markdown)

```markdown
**FOCUS GROUP #1**

**Fat Loss Seekers**

*"The Scale Watchers"*

**OVERVIEW**

Individuals whose primary goal is reducing body fat and seeing lower
numbers on the scale.

**DEMOGRAPHICS**

  **Age**            25-55, peaks at 35-45
  **Gender**         60% female, 40% male
  **Income**         Middle to upper-middle class
  **Lifestyle**      Sedentary to moderately active
  **Triggers**       Photos of themselves, upcoming events

**PSYCHOGRAPHICS**

  **Values**         Health, appearance, self-control, discipline
  **Beliefs**        Weight loss = willpower, calories in/out
  **Lifestyle**      Busy professionals, parents
  **Identity**       See themselves as someone who 'used to be fit'

**CORE DESIRES (What They Want)**

- See visible changes in the mirror and photos
- Fit into old clothes or buy smaller sizes
- Feel comfortable in a swimsuit

**PAIN POINTS (What Frustrates Them)**

- Scale won't budge despite 'eating healthy'
- Losing the same 10 pounds over and over

**FEARS & ANXIETIES**

- Being stuck at this weight forever
- Health complications from excess weight

**BELIEFS & WORLDVIEW**

- Some people are just naturally thin
- My metabolism is broken/slow

**COMMON OBJECTIONS (Why They Hesitate)**

*"I've tried everything already"*
*"I don't have time to meal prep"*

**EMOTIONAL TRIGGERS (What Activates Buying)**

- Seeing unflattering photos of themselves
- Clothes feeling tight

**LANGUAGE PATTERNS (Exact Phrases They Use)**

*"I want to lose X pounds"*
*"Nothing I try works"*

**EBOOK POSITIONING ANGLES**

**1. "The Last Fat Loss Guide You'll Ever Need"**

**MARKETING HOOKS & HEADLINES**

- "Still counting calories and still not losing weight?"

**TRANSFORMATION PROMISE**

**From frustrated dieter constantly battling the scale -> confident
individual who understands their body**
```

## Output (Structured JSON)

```json
{
  "number": 1,
  "name": "Fat Loss Seekers",
  "nickname": "The Scale Watchers",
  "category": null,
  "overview": "Individuals whose primary goal is reducing body fat and seeing lower numbers on the scale.",
  "demographics": {
    "ageRange": "25-55, peaks at 35-45",
    "gender": "60% female, 40% male",
    "income": "Middle to upper-middle class",
    "lifestyle": "Sedentary to moderately active",
    "triggers": ["Photos of themselves", "upcoming events"]
  },
  "psychographics": {
    "values": ["Health", "appearance", "self-control", "discipline"],
    "beliefs": ["Weight loss = willpower", "calories in/out"],
    "lifestyle": "Busy professionals, parents",
    "identity": "See themselves as someone who 'used to be fit'"
  },
  "coreDesires": [
    "See visible changes in the mirror and photos",
    "Fit into old clothes or buy smaller sizes",
    "Feel comfortable in a swimsuit"
  ],
  "painPoints": [
    "Scale won't budge despite 'eating healthy'",
    "Losing the same 10 pounds over and over"
  ],
  "fears": [
    "Being stuck at this weight forever",
    "Health complications from excess weight"
  ],
  "beliefs": [
    "Some people are just naturally thin",
    "My metabolism is broken/slow"
  ],
  "objections": [
    "I've tried everything already",
    "I don't have time to meal prep"
  ],
  "emotionalTriggers": [
    "Seeing unflattering photos of themselves",
    "Clothes feeling tight"
  ],
  "languagePatterns": [
    "I want to lose X pounds",
    "Nothing I try works"
  ],
  "ebookAngles": [
    "The Last Fat Loss Guide You'll Ever Need"
  ],
  "marketingHooks": [
    "Still counting calories and still not losing weight?"
  ],
  "transformationPromise": "From frustrated dieter constantly battling the scale -> confident individual who understands their body",
  "completenessScore": 0.0,
  "missingFields": [
    "awarenessStage",
    "sophisticationLevel",
    "contentPreferences",
    "influenceSources",
    "purchaseBehavior",
    "competitorContext",
    "communicationStyle",
    "seasonalContext",
    "negativeTriggers",
    "awarenessSignals"
  ]
}
```

## Notes

- The `completenessScore` is 0% because all 10 enrichment fields are missing. This is expected for raw document imports -- enrichment agents will fill these fields later.
- The `category` is null because the fitness doc format does not include an explicit category label within each group section. The category headings (e.g., "PHYSICAL TRANSFORMATION DESIRES") appear above the group, not inside it.
- Array fields strip bullet markers, quote formatting, and unicode symbols from items.
- The transformation promise strips bold markers and joins multi-line text.
