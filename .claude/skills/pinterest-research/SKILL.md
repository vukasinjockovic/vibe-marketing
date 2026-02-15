---
name: pinterest-research
displayName: Pinterest Research
description: Search Pinterest for trending pins, boards, and visual content ideas. Free Playwright-based scraping. Extracts pin descriptions, engagement signals, board themes, and visual trends for content planning and audience research.
category: research
type: tool
---

# Pinterest Research

Search Pinterest for trending pins, boards, and visual content ideas. Free Playwright-based scraping -- no API key, no cost. Extracts pin descriptions, engagement signals (saves/repins), board themes, and visual trends for content planning and audience research.

## When to Use

- **Visual content ideation**: Find pin styles, image formats, and visual trends that drive engagement
- **Audience interest mapping**: Discover what boards target demographics curate and follow
- **Seasonal trend discovery**: Track seasonal and emerging visual trends via Pinterest Trends
- **Product research**: Find product photography styles, pricing, and conversion-focused pin descriptions
- **Content hook mining**: Extract descriptions and titles from viral pins (high save counts)
- **Campaign research**: Feed pin themes and audience data into content-strategy and audience-research skills

## Scripts

### 1. `pinterest_search.py` -- Pin Search

Search Pinterest for pins matching a query. Extracts descriptions, engagement data, images, and pinner info.

```bash
# Quick search (JSON output)
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "grandparent gifts" \
    --output json

# More results with extra scrolling
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "wedding centerpieces" \
    --max-pins 50 \
    --scroll-count 8 \
    --output json

# Markdown output for saving to research folder
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "home office decor" \
    --output markdown
```

**Output fields per pin:** description, pin_url, image_url, repin_count (saves), pinner_name, board_name

**Sorted by:** repin count (highest engagement first)

### 2. `pinterest_boards.py` -- Board Analysis

Analyze Pinterest boards for theme and audience research. Works in two modes: direct URL or search.

```bash
# Analyze a specific board
python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --url "https://www.pinterest.com/username/boardname/" \
    --max-pins 30 \
    --output json

# Search for boards by topic
python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --search "wedding planning boards" \
    --max-boards 5 \
    --output json
```

**Output fields per board:** name, description, pin_count, follower_count, creator, top pins (with descriptions), identified themes (word frequency analysis)

### 3. `pinterest_trends.py` -- Trending Topics

Scrape Pinterest Trends page for trending searches and seasonal data. Tries urllib first (fast), falls back to Playwright if JS rendering is needed.

```bash
# General trends
python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --output json

# Category-specific trends
python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --category "weddings" \
    --output json

# Markdown for research docs
python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --category "home" \
    --output markdown
```

**Supported categories:** weddings, home, food, diy, fashion, beauty, travel

## Flow-Aware Routing

### Engagement Flow
Use `pinterest_search.py` to find viral pins (high repin/save counts). Extract descriptions and hooks that drive saves. Focus on:
- Emotional triggers in pin descriptions
- Visual styles that get high engagement
- Seasonal trends and timing
- Title/description patterns that compel saves

```bash
# Find highest-engagement pins for hook mining
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "motivational fitness quotes" \
    --max-pins 50 \
    --output json
```

### Sales Flow
Use `pinterest_search.py` + `pinterest_boards.py` to find product pins, Etsy links, pricing, and conversion-focused pin descriptions. Focus on:
- Product photography styles
- Pricing anchors and buy-now language
- Shop-the-look and product collection patterns
- Affiliate and direct-sale pin formats

```bash
# Find product pins
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "pre workout supplement" \
    --max-pins 30 \
    --output json

# Analyze product boards
python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --search "fitness supplement products" \
    --max-boards 3 \
    --output json
```

### Audience Flow
Use `pinterest_search.py` + `pinterest_boards.py` to build audience profiles from board curation patterns. Focus on:
- What boards target demographics maintain
- Adjacent interest clusters (what else do they pin?)
- Visual preference patterns (colors, styles, aesthetics)
- Board organization and naming patterns

```bash
# Discover audience interests via board analysis
python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --search "new mom gift ideas" \
    --max-boards 5 \
    --output json

# Seasonal trends for campaign timing
python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --category "weddings" \
    --output json
```

## Technical Notes

- **No API key required** -- all scripts use Playwright browser automation
- **Anti-bot measures**: Random delays (2-4s), realistic viewports (1920x1080), user-agent rotation, stealth navigator overrides
- **Infinite scroll handling**: Configurable scroll count for loading more pins
- **Pinterest login not required**: Search URLs (`/search/pins/?q=`) are publicly accessible
- **Graceful degradation**: pinterest_trends.py tries urllib first, falls back to Playwright
- **Rate limiting**: Built-in random delays between actions; Pinterest blocks aggressive scraping

## Requirements

```bash
pip install playwright && python -m playwright install chromium
```

## Integration with Other Skills

1. **audience-research-procedures**: Feed board themes into audience profiling
2. **content-strategy**: Use trending pins/topics for content calendar planning
3. **image-director-sales**: Extract visual styles from top pins for image generation
4. **mbook-schwarz-awareness**: Map pin engagement patterns to awareness stages
5. **social-content**: Use pin descriptions as templates for social media posts
6. **google-suggest-research**: Cross-reference pin trends with Google search volume
7. **amazon-reviews-research**: Combine Pinterest visual trends with Amazon purchase intent

## Examples by Niche

### Wedding/Events
```bash
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "destination wedding ideas 2026" \
    --max-pins 30 --output json

python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --search "wedding planning inspiration" \
    --max-boards 5 --output json

python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --category "weddings" --output json
```

### Home/Interior Design
```bash
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "small apartment decor ideas" \
    --max-pins 40 --output json

python .claude/skills/pinterest-research/scripts/pinterest_trends.py \
    --category "home" --output json
```

### Fitness/Health
```bash
python .claude/skills/pinterest-research/scripts/pinterest_search.py \
    --query "meal prep for weight loss" \
    --max-pins 30 --output json

python .claude/skills/pinterest-research/scripts/pinterest_boards.py \
    --search "fitness motivation boards" \
    --max-boards 3 --output json
```

## Error Handling

- **Anti-bot blocking**: Detected via page content analysis; logged to stderr, returns empty results
- **Network timeouts**: 30-second timeout per page load; graceful fallback
- **Empty results**: Returns valid JSON with `total_pins: 0` or `total_boards: 0`
- **Missing Playwright**: Clear error message with install instructions
- **Progress**: Printed to stderr so agents can monitor without polluting stdout JSON
