---
name: google-trends-research
displayName: Google Trends Research
description: Pull trending keyword data, seasonal patterns, related queries, and regional interest from Google Trends. Free, no API key required. Used during research phases to identify content timing, keyword opportunities, and audience geography.
category: research
type: custom
---

# Google Trends Research

A free research tool that pulls real-time keyword trend data from Google Trends. No API key or paid service required. Uses the `pytrends` library (unofficial Google Trends API).

---

## When to Use

- **Research phase** of engagement and sales flows (step 1)
- **Keyword discovery** -- find what your audience is actually searching for
- **Seasonal planning** -- identify when interest peaks for content calendar timing
- **Content calendar** -- schedule content around seasonal spikes
- **Competitor keyword comparison** -- compare brand/product keyword interest
- **Geographic targeting** -- identify which US states have highest interest
- **Trend validation** -- confirm whether a topic is growing or declining

Agents that should use this tool:
- `vibe-audience-researcher` -- during audience discovery
- `vibe-keyword-researcher` -- during keyword research
- `vibe-engagement-trend-researcher` -- during trend analysis
- `vibe-content-strategist` -- when planning content calendars

---

## How to Invoke

### Basic Usage (JSON output)

```bash
python /var/www/vibe-marketing/.claude/skills/google-trends-research/scripts/google_trends.py \
    --keywords "grandparent gift" "wedding planner" \
    --timeframe "today 12-m" \
    --geo "US" \
    --output json
```

### Markdown Report (human-readable)

```bash
python /var/www/vibe-marketing/.claude/skills/google-trends-research/scripts/google_trends.py \
    --keywords "baby memory book" "first year baby" \
    --timeframe "today 12-m" \
    --output markdown
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--keywords` | Yes | -- | 1-5 keywords to research |
| `--timeframe` | No | `today 12-m` | Time range for data |
| `--geo` | No | `US` | Geographic region |
| `--output` | No | `json` | Output format: `json` or `markdown` |
| `--category` | No | `0` | Google Trends category ID (0 = all) |

### Timeframe Options

| Value | Meaning |
|-------|---------|
| `today 1-m` | Last 30 days |
| `today 3-m` | Last 90 days |
| `today 12-m` | Last 12 months (default, best for seasonal analysis) |
| `today 5-y` | Last 5 years (good for long-term trend direction) |

---

## Example: Wedding/Family Niche

```bash
python /var/www/vibe-marketing/.claude/skills/google-trends-research/scripts/google_trends.py \
    --keywords "wedding planner" "wedding checklist" "destination wedding" \
    --timeframe "today 12-m" \
    --geo "US" \
    --output json
```

This reveals:
- Peak wedding search months (January for planning, June for execution)
- Rising queries like "micro wedding" or "elopement packages"
- Which US states have highest wedding interest (useful for geo-targeted ads)

## Example: Grandparent/Senior Niche

```bash
python /var/www/vibe-marketing/.claude/skills/google-trends-research/scripts/google_trends.py \
    --keywords "grandparent gift" "gift for grandma" "personalized grandparent" \
    --timeframe "today 12-m" \
    --geo "US" \
    --output json
```

This reveals:
- Seasonal peaks around Grandparents Day (September), Christmas (December), Mother's/Father's Day
- Rising queries showing new product trends
- Regional hotspots for targeting

---

## How to Interpret Output

### Interest Over Time

Values are normalized 0-100 relative to the peak within the queried period. A value of 100 means peak popularity; 50 means half of peak popularity. Use this to:
- Identify upward or downward trends
- Find the best months to publish content
- Compare relative interest between keywords

### Seasonal Peaks

Computed automatically from interest-over-time data. A month is flagged as a "peak" when its average interest exceeds the overall average. Use this directly for content calendar planning:
- Schedule content 2-4 weeks BEFORE peak months
- Increase ad spend during peak months
- Create evergreen content for low-interest months

### Related Queries

- **Rising queries**: Keywords gaining popularity rapidly. The value is a percentage increase (e.g., "250" means 250% growth). These are content gold -- create content targeting these before competitors do.
- **Top queries**: Most frequently searched related terms. These are established demand -- use them for SEO-optimized cornerstone content.

### Related Topics

Similar to related queries but at the topic level (Google's entity graph). Useful for:
- Content clustering and pillar page strategy
- Understanding the broader context of your niche
- Discovering adjacent markets

### Interest by Region

Shows which US states (or sub-regions) have the highest search interest. Use this for:
- Geo-targeted ad campaigns
- Local content variations
- Understanding regional demand differences

---

## Integration with Other Skills

### Feeds Into

- **audience-research-procedures** -- Use trend data to validate audience size and timing. If a keyword has zero interest, the audience segment may be too niche.
- **content-strategy** -- Use seasonal peaks and rising queries to plan the content calendar. Rising queries become blog topics, social posts, and email subjects.
- **trend-research-procedures** -- Supplements Reddit trend data with Google search volume trends. Cross-reference STEPPS-scored Reddit trends with Google Trends interest to validate virality potential.

### Workflow Example

1. Run google-trends-research to identify seasonal peaks and rising queries
2. Use rising queries as input for audience-research Reddit scraping (search terms)
3. Cross-reference regional interest with focus group demographics
4. Feed seasonal peaks into content calendar for campaign timing

---

## Rate Limiting

Google Trends has undocumented rate limits. The script adds 2-second delays between API calls. If you get rate-limited (429 errors or empty responses):
- Wait 60 seconds and retry
- Reduce keyword count (use 1-2 instead of 5)
- Use a longer timeframe (fewer data points)

---

## Error Handling

- If pytrends is not installed, the script prints a clear error message and exits
- If a specific data fetch fails (e.g., related queries), it logs a warning to stderr and returns empty data for that section rather than crashing
- If a keyword returns no data, it appears in the output with empty arrays
- All status/progress messages go to stderr; only the final JSON/markdown output goes to stdout
