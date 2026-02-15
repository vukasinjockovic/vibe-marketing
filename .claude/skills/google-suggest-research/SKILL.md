---
name: google-suggest-research
displayName: Google Suggest Research
description: Discover what people actually type into Google by querying the Autocomplete API. Free, no API key. Expands seed keywords with alphabet, question, and preposition modifiers to uncover long-tail search intent. Used for content ideation, SEO keyword discovery, and audience language mining.
category: research
type: tool
---

# Google Suggest Research

Discover real search queries people type into Google. Uses the free Google Autocomplete/Suggest API -- no API key, no cost, no rate-limit signup.

## When to Use

- **Content ideation**: Find blog post topics, YouTube video ideas, FAQ pages
- **Keyword expansion**: Turn 1-2 seed keywords into 100+ long-tail variations
- **Audience language discovery**: Learn the exact phrases your market uses
- **SEO planning**: Identify question-based queries for featured snippets
- **Competitor/alternative discovery**: "X vs", "X alternative" surface via preposition expansion
- **Campaign research**: Feed expanded keywords into content-strategy and audience-research skills

## How to Invoke

The script is at `.claude/skills/google-suggest-research/scripts/google_suggest.py`.

### Quick keyword expansion (JSON output)

```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "grandparent gift" \
    --output json
```

### Full expansion with all modifiers

```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "grandparent gift" "gift for elderly parent" \
    --expand-alphabet \
    --expand-questions \
    --expand-prepositions \
    --output json
```

### Question-only expansion for FAQ/blog content

```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "wedding planner" \
    --expand-questions \
    --output markdown
```

### Localized search (non-US market)

```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "gift ideas" \
    --expand-questions \
    --lang de --country de \
    --output json
```

## Expansion Strategies

### Direct
Just the seed keyword itself. Returns Google's top 10 autocomplete suggestions. Always runs.

### Alphabet (`--expand-alphabet`)
Queries "seed a", "seed b", ... "seed z" to uncover long-tail variations Google would not show for the seed alone. Produces the most results (up to 260 per seed) but takes longer. Best for thorough keyword research. Skip for quick checks.

### Questions (`--expand-questions`)
Queries "what seed", "how seed", "why seed", "when seed", "where seed", "which seed", "who seed", "is seed", "can seed", "does seed". Excellent for:
- FAQ page content
- Blog post titles (answer the question in the post)
- YouTube video ideas (people search YouTube with questions)
- Understanding customer objections and concerns

### Prepositions (`--expand-prepositions`)
Queries "seed for", "seed with", "seed without", "seed vs", "seed near", "seed like". Reveals:
- Use cases and audiences ("gift for new grandparent")
- Comparisons ("X vs Y")
- Requirements ("planner with budget tracker")
- Alternatives ("service like X")

## Output Formats

### JSON (default)
Machine-readable. Contains `results` (per-seed breakdown), `all_unique_suggestions` (flat deduplicated list), and `top_themes` (extracted common words grouped by category).

### Markdown (`--output markdown`)
Human-readable report with headers per seed and expansion type. Good for saving directly to campaign research folders.

## Speed vs Thoroughness

| Strategy | Queries per seed | Time (0.3s delay) | Best for |
|----------|-----------------|-------------------|----------|
| Direct only | 1 | <1s | Quick check |
| + Questions | 11 | ~4s | Blog/FAQ ideation |
| + Prepositions | 17 | ~6s | Competitive research |
| + Alphabet | 27 | ~9s | Deep keyword mining |
| All three | 43 | ~14s | Full research phase |

Multiply by number of seeds. Use `--delay 0.2` for faster runs (slight rate-limit risk) or `--delay 0.5` for safer pacing.

## Integration with Other Skills

1. **audience-research-procedures**: Use expanded keywords as Reddit/review search queries
2. **content-strategy**: Feed `all_unique_suggestions` into topic clustering
3. **mbook-schwarz-awareness**: Map question expansions to awareness stages
4. **seo-audit**: Use results to identify content gaps
5. **programmatic-seo**: Long-tail keywords from alphabet expansion feed pSEO templates

## Examples by Niche

### Wedding/Events
```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "wedding planner" "destination wedding" "wedding budget" \
    --expand-questions --expand-prepositions \
    --output json
```

### Senior/Grandparent Gifts
```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "grandparent gift" "gift for elderly" "senior activity" \
    --expand-alphabet --expand-questions \
    --output markdown
```

### Fitness/Supplements
```bash
python .claude/skills/google-suggest-research/scripts/google_suggest.py \
    --seed-keywords "pre workout" "protein powder" "creatine" \
    --expand-questions --expand-prepositions \
    --output json
```

## Error Handling

- **Rate limiting (429)**: Automatic exponential backoff, up to 3 retries per query
- **Network errors**: Logged to stderr, returns empty list for that query, continues with others
- **Empty responses**: Gracefully skipped, no crash
- **Progress**: Printed to stderr so agents can monitor without polluting stdout JSON
