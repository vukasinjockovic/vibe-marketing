# Trend Research Procedures

> SOP for `vibe-trend-researcher` agent. Scrapes Reddit/web for trending topics, scores them with STEPPS virality framework, matches to focus group psychographics, and outputs trend briefs for engagement post generation.

## When This Runs

- Pipeline step in `full-engagement-batch` pipeline (step 1)
- Receives a task with `contentBatchId` linking to a content batch
- Content batch has `trendSources` (subreddits, URLs) and `contentThemes` (topic filters)

## Inputs

Load from Convex via the task's `contentBatchId`:

1. **Content batch** — `contentBatches:get` → trendSources, contentThemes, mixConfig
2. **Channel** — `channels:get` → platform, platformConfig (country restrictions)
3. **Focus groups** — `focusGroups:getByContentBatch` → psychographics, pain points, language patterns, emotional triggers
4. **Project** — `projects:get` → brand voice, description

## Process

### Step 1: Gather Raw Trends

For each source in `trendSources`:

- **Reddit subreddits** (e.g., `r/weddingplanning`, `r/newparents`):
  - Use Reddit MCP to fetch top 25 posts from last 7 days (hot + top/week)
  - Extract: title, score, comment count, top 3 comments, flair
  - Filter by `contentThemes` if provided (keyword match in title/comments)

- **Web sources** (URLs, search queries):
  - Use web search MCP for each query
  - Extract: headlines, snippets, publication dates
  - Prioritize last 7 days

### Step 2: Score with STEPPS Framework

For each gathered trend, score 1-5 on each STEPPS dimension:

| Dimension | Question |
|-----------|----------|
| **S**ocial Currency | Does sharing this make people look good/knowledgeable? |
| **T**riggers | Is this connected to everyday cues that keep it top-of-mind? |
| **E**motion | Does this evoke high-arousal emotions (awe, anger, anxiety, joy)? |
| **P**ublic | Is this visible — do people see others engaging with it? |
| **P**ractical Value | Is this useful — would people share to help others? |
| **S**tories | Can this be wrapped in a narrative people want to retell? |

Total STEPPS score = sum of 6 dimensions (max 30).

### Step 3: Match to Focus Groups

For each trend with STEPPS score >= 18:

- Compare trend keywords against focus group `painPoints`, `emotionalTriggers`, `coreDesires`
- Score relevance 1-5 per focus group
- Tag which focus groups this trend resonates with most
- Note which `languagePatterns` from the focus group could be woven in

### Step 4: Generate Trend Brief

For each qualified trend (STEPPS >= 18, focus group relevance >= 3):

```markdown
## Trend Brief: {trend_title}

### Source
- Platform: {reddit/web}
- URL: {source_url}
- Engagement: {score/comments or publication reach}
- Recency: {date}

### STEPPS Score: {total}/30
- Social Currency: {score} — {one-line reasoning}
- Triggers: {score} — {one-line reasoning}
- Emotion: {score} — {one-line reasoning}
- Public: {score} — {one-line reasoning}
- Practical Value: {score} — {one-line reasoning}
- Stories: {score} — {one-line reasoning}

### Focus Group Match
- Primary: {focus_group_name} (relevance: {score}/5)
- Secondary: {focus_group_name} (relevance: {score}/5)
- Key resonance: {which pain points/desires this hits}

### Post Angle
{2-3 sentences describing HOW to turn this trend into an engagement post}
- Suggested hook type: {question/emotional/interactive/debate/text-only}
- Language patterns to use: {from matched focus group}
- Emotion to target: {specific emotion from STEPPS analysis}
```

## Output

Write one trend brief file per task to:
```
projects/{project-slug}/engagement/{channel-slug}/batches/{batch-slug}/research/trend-brief-{N}.md
```

Where N is the task number (extracted from task title).

If no trends qualify (STEPPS < 18 or no focus group match >= 3), write a brief explaining why and suggest evergreen angles from the focus group data instead.

## Completion

Call `pipeline:completeStep` with:
- `outputPath`: path to the trend brief file
- `qualityScore`: average STEPPS score of selected trends (normalized to 1-10 scale)

## Error Handling

- If Reddit MCP unavailable: fall back to web search only, note degraded mode
- If no trendSources configured: generate briefs from focus group data alone (evergreen mode)
- If web search fails: log warning, use cached/evergreen content
- Always produce at least one trend brief per task — never leave the pipeline empty
