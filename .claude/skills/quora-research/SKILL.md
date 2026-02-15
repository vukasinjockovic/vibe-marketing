---
name: quora-research
displayName: Quora Research
description: Find and extract questions, answers, and audience voice data from Quora. Free. Combines Brave Search API for discovery with Playwright for content extraction. Mines real questions people ask, expert answers, and emotional language patterns.
category: research
type: tool
---

# Quora Research

Mine Quora for real questions people ask, expert answers with persuasion analysis, and deep audience voice data. Uses web search (Brave or Google) to discover Quora URLs, then Playwright to extract content from question pages. Zero API cost beyond optional Brave Search key.

---

## When to Use

- **Content ideation**: Find questions with proven demand (high upvotes/followers) for blog posts, videos, and social content
- **Audience voice mining**: Extract the raw emotional language of your target market -- pain points, desires, objections, and the exact words they use
- **Expert answer analysis**: Study how experts structure persuasive answers -- personal stories, authority claims, specific recommendations
- **Product positioning**: Find "what should I buy" style questions to understand how your market evaluates solutions
- **Headline templates**: Extract question phrasing patterns that resonate with audiences (e.g., "Is it normal to...", "How do I deal with...")
- **Objection discovery**: Identify real objections and concerns people voice publicly

---

## Flow-Aware Routing

### Engagement Flow
Use `quora_questions.py` to find high-upvote questions (content ideas with proven demand). Extract question phrasing for headline templates. Identify recurring themes for content calendar.

```bash
python .claude/skills/quora-research/scripts/quora_questions.py \
    --topic "home gym equipment" \
    --max-questions 20 \
    --output json
```

### Sales Flow
Use `quora_answers.py` to find expert answers that recommend products/services. Extract the persuasion patterns used. Identify "what should I buy" style questions for product positioning.

```bash
python .claude/skills/quora-research/scripts/quora_answers.py \
    --topic "best protein powder for beginners" \
    --max-questions 5 \
    --answers-per-question 5 \
    --output json
```

### Audience Flow
Use `quora_voice_mine.py` to build audience voice profiles from question askers' language. Extract pain points, desires, objections, and the emotional vocabulary of the target market.

```bash
python .claude/skills/quora-research/scripts/quora_voice_mine.py \
    --topic "grandparent loneliness" \
    --max-questions 10 \
    --output json
```

---

## Scripts

### 1. quora_questions.py -- Question Discovery

Find Quora questions via web search and extract metadata from each question page.

```bash
python .claude/skills/quora-research/scripts/quora_questions.py \
    --topic "grandparent gifts" \
    --max-questions 20 \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--topic` | Yes | -- | Topic to search for |
| `--max-questions` | No | 20 | Max questions to extract |
| `--output` | No | json | Output format: "json" or "markdown" |

**Output fields per question:**
- question_title, url, description
- answer_count, follower_count, upvote_count
- tags, date_asked

Results sorted by engagement (followers + upvotes).

---

### 2. quora_answers.py -- Answer Extraction

Extract answers from Quora question pages with persuasion pattern analysis.

**URL mode** (single question):
```bash
python .claude/skills/quora-research/scripts/quora_answers.py \
    --url "https://www.quora.com/What-is-the-best-gift-for-grandparents" \
    --max-answers 10 \
    --output json
```

**Topic mode** (find questions, then extract answers):
```bash
python .claude/skills/quora-research/scripts/quora_answers.py \
    --topic "wedding planning tips" \
    --max-questions 5 \
    --answers-per-question 5 \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--url` | One of url/topic | -- | Quora question URL |
| `--topic` | One of url/topic | -- | Topic search (finds questions first) |
| `--max-answers` | No | 10 | Max answers in URL mode |
| `--max-questions` | No | 5 | Max questions in topic mode |
| `--answers-per-question` | No | 5 | Max answers per question in topic mode |
| `--output` | No | json | Output format: "json" or "markdown" |

**Output fields per answer:**
- text (full answer), author_name, author_credentials
- upvote_count, date
- product_mentions (detected brands/products)
- links (external URLs in the answer)
- persuasion_patterns: personal_story, authority, specific_recommendation, social_proof, data_evidence

---

### 3. quora_voice_mine.py -- Deep Voice Mining

The most valuable script for audience research. Combines question discovery + answer extraction + NLP-style analysis.

```bash
python .claude/skills/quora-research/scripts/quora_voice_mine.py \
    --topic "grandparent loneliness" \
    --max-questions 10 \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--topic` | Yes | -- | Topic to mine voice data for |
| `--max-questions` | No | 10 | Max questions to analyze |
| `--output` | No | json | Output format: "json" or "markdown" |

**Voice data extracted:**

| Field | Description | Example |
|-------|-------------|---------|
| pain_phrases | Exact phrases describing problems/frustrations | "I feel so alone since my wife passed" |
| desire_phrases | Exact phrases describing wants/goals | "I just want to stay connected with my grandkids" |
| objection_phrases | Phrases showing resistance/doubt | "but technology is so confusing" |
| emotional_vocabulary | High-emotion words used frequently | "heartbroken", "priceless", "devastated" |
| question_patterns | How people frame their questions | "Is it normal to...", "How do I deal with..." |
| product_mentions | Specific products/services mentioned | "FaceTime", "Alexa", "Kindle" |
| demographic_signals | Age, gender, role, life stage signals | "65-year-old grandmother", "retired teacher" |

---

## How This Feeds Into Focus Groups

| Voice Mining Field | Focus Group Field |
|-------------------|-------------------|
| pain_phrases | painPoints |
| desire_phrases | coreDesires, transformationPromise |
| objection_phrases | objections |
| emotional_vocabulary | emotionalTriggers, languagePatterns |
| question_patterns | marketingHooks (reframe as headlines) |
| product_mentions | competitorAwareness |
| demographic_signals | demographics |

---

## How This Feeds Into Content Strategy

| Voice Mining Field | Content Application |
|-------------------|-------------------|
| pain_phrases | Blog post intros, ad hooks, email subject lines |
| desire_phrases | Landing page headlines, CTA copy |
| objection_phrases | FAQ sections, objection-handling email sequences |
| question_patterns | Blog post titles (answer the exact question) |
| product_mentions | Competitor comparison content, "vs" pages |

---

## Practical Examples

### Grandparent/Senior Niche
```bash
python .claude/skills/quora-research/scripts/quora_voice_mine.py \
    --topic "grandparent loneliness elderly isolation" \
    --max-questions 15 \
    --output json > /tmp/grandparent-voice.json
```

### Fitness/Weight Loss
```bash
python .claude/skills/quora-research/scripts/quora_questions.py \
    --topic "losing weight after 40" \
    --max-questions 20 \
    --output json > /tmp/weight-loss-questions.json

python .claude/skills/quora-research/scripts/quora_voice_mine.py \
    --topic "weight loss plateau frustrated" \
    --max-questions 10 \
    --output json > /tmp/weight-loss-voice.json
```

### B2B/SaaS
```bash
python .claude/skills/quora-research/scripts/quora_answers.py \
    --topic "best project management tool for small teams" \
    --max-questions 5 \
    --answers-per-question 10 \
    --output json > /tmp/pm-tool-answers.json
```

---

## Quora Login Wall Bypass

Quora shows a login wall after viewing 2-3 pages. The scripts handle this automatically:

1. Appends `?share=1` to all Quora URLs (bypasses login wall for shared links)
2. If login modal appears, removes the overlay DOM element via JavaScript
3. Re-enables scrolling by resetting body overflow
4. Extracts what is visible before the wall if all else fails

---

## Rate Limiting and Ethical Scraping

- **Delays**: Random 3-5 second delays between page loads
- **Resource blocking**: Images, fonts, and media are blocked to reduce bandwidth
- **Stealth**: Realistic user agents, webdriver detection disabled, human-like viewport
- **Volume**: Keep to 10-20 questions per session. Do not scrape at scale.
- **Respect ToS**: Use for legitimate market research in reasonable volumes only

---

## Prerequisites

```bash
pip install playwright && python -m playwright install chromium
```

Optional: Set `BRAVE_API_KEY` environment variable for faster question discovery via Brave Search API. Falls back to Google search via urllib (no API key needed) if Brave is unavailable.

---

## Integration with Other Skills

1. **google-suggest-research**: Use expanded keywords as Quora search topics
2. **amazon-reviews-research**: Combine Quora voice data with Amazon review voice data for richer language profiles
3. **audience-research-procedures**: Feed voice mining output directly into focus group profiles
4. **content-strategy**: Use question patterns and pain phrases for topic clustering
5. **mbook-schwarz-awareness**: Map question patterns to awareness stages (unaware people ask different questions than solution-aware people)
6. **copywriting**: Use pain_phrases and desire_phrases as raw material for headlines and hooks
7. **email-sequence**: Use objection_phrases for objection-handling emails in nurture sequences

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| No questions found | Try broader topic terms. Quora may not cover very niche topics. |
| Login wall blocks content | Scripts handle this automatically. If persistent, try a different IP or wait 10-15 minutes. |
| Empty answer text | Quora lazy-loads answers. The scripts scroll and expand, but some pages may resist. |
| Brave API not working | Set BRAVE_API_KEY env var, or let it fall back to Google search automatically. |
| Playwright not found | Run `pip install playwright && python -m playwright install chromium`. |
| Rate limiting | Reduce --max-questions. Add longer delays between sessions. |
