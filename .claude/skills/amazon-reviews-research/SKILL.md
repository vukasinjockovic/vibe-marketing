---
name: amazon-reviews-research
displayName: Amazon Reviews Research
description: Extract customer voice data from Amazon product reviews via Playwright browser automation. Free. Identifies love/hate phrases, product gaps, emotional triggers, and buyer-vs-user dynamics. Critical for copy mining and product gap analysis.
category: research
type: tool
---

# Amazon Reviews Research

Mine Amazon product reviews for real customer language, pain points, desires, and product opportunity gaps using Playwright browser automation. Zero API cost -- uses headless Chromium to browse Amazon like a human.

---

## When to Use

- **Copy mining**: Extract the exact words customers use to describe what they love and hate. These phrases become headlines, email subject lines, and ad hooks.
- **Product gap analysis**: Find what customers explicitly wish existed. These gaps are product development opportunities or positioning angles.
- **Audience language extraction**: Build language banks for focus group profiles. Real Amazon review language is dramatically different from marketing-speak.
- **Competitive intelligence**: See what customers say about competing products -- their strengths, weaknesses, and the emotional context around purchase decisions.
- **Buyer-vs-user research**: Especially for gift products, the buyer and user are different people with different needs. Reviews reveal both perspectives.

---

## The 1-Star + 5-Star Strategy

**The most valuable customer voice data lives at the extremes.**

- **5-star reviews** reveal what customers *love* -- the emotional triggers that drive purchase, the unexpected delights, and the specific language of satisfaction. These become your marketing hooks.
- **1-star reviews** reveal what customers *hate* -- unmet expectations, product failures, and the language of frustration. These become your objection-handling copy and product improvement roadmap.
- **3-star reviews** are lukewarm and generic ("it's fine"). They rarely contain the intense emotional language that makes great copy.

Use `--stars "1,5"` for the fastest, most actionable research. Add 2-star reviews (`--stars "1,2,5"`) to expand the hate dataset.

---

## Buyer vs. User Mismatch

Many products on Amazon are purchased by one person and used by another. This is especially common with:

- **Gift products** (journals, gadgets, books)
- **Children's products** (parent buys, child uses)
- **Elder care products** (adult child buys, parent uses)
- **Pet products** (human buys, pet "uses")

The mismatch reveals product opportunities:

| Who | What They Care About | Example |
|-----|---------------------|---------|
| Buyer | Presentation, price, gift-worthiness, shipping speed | "Beautiful packaging, arrived on time" |
| User | Functionality, comfort, ease of use, daily experience | "The font is too small for my eyes" |

When the buyer loves it but the user struggles, you have found a positioning gap. Your marketing can speak to the buyer's emotions while your product addresses the user's needs.

---

## Usage

### Search-Based (Finds Products Then Scrapes Reviews)

```bash
python .claude/skills/amazon-reviews-research/scripts/amazon_reviews.py \
    --search "grandparent journal" \
    --max-products 3 \
    --reviews-per-product 20 \
    --stars "1,5" \
    --sort helpful \
    --output json
```

### Direct Product URLs

```bash
python .claude/skills/amazon-reviews-research/scripts/amazon_reviews.py \
    --product-urls "https://www.amazon.com/dp/B07EXAMPLE" "https://www.amazon.com/dp/B08EXAMPLE" \
    --reviews-per-product 30 \
    --stars "1,2,5" \
    --output markdown
```

### Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--search` | One of search/urls | -- | Amazon search query |
| `--product-urls` | One of search/urls | -- | Direct Amazon product URLs |
| `--max-products` | No | 3 | Max products to scrape |
| `--reviews-per-product` | No | 20 | Max reviews per product |
| `--stars` | No | "1,2,3,4,5" | Comma-separated star ratings to focus on |
| `--sort` | No | "helpful" | Sort by "helpful" or "recent" |
| `--output` | No | "json" | Output format: "json" or "markdown" |

Progress messages go to stderr. Data goes to stdout.

---

## Output Structure

The JSON output contains:

- **products[]**: Each product with title, ASIN, price, rating, and collected reviews
- **voice_analysis.love_phrases**: Common phrases from 4-5 star reviews (marketing hook material)
- **voice_analysis.hate_phrases**: Common phrases from 1-2 star reviews (objection handling material)
- **voice_analysis.product_gaps**: What reviewers explicitly wish existed (product development leads)
- **voice_analysis.gift_occasions**: Detected gift-giving occasions (seasonal marketing triggers)
- **voice_analysis.buyer_vs_user**: Who is buying vs. who is using, and where they disagree
- **voice_analysis.emotional_triggers**: Recurring emotional themes (legacy, connection, fear, etc.)

---

## Practical Examples

### Grandparent Journal Niche

```bash
python .claude/skills/amazon-reviews-research/scripts/amazon_reviews.py \
    --search "grandparent memory book" \
    --max-products 5 \
    --reviews-per-product 25 \
    --stars "1,2,5" \
    --output json > /tmp/grandparent-journals.json
```

Expected findings:
- **Love**: "made my mom cry," "treasure forever," "wish I started sooner"
- **Hate**: "writing space too small," "prompts too generic," "fell apart"
- **Gaps**: Larger font, more photo spaces, digital companion, guided prompts by topic
- **Buyer/User split**: Adult children buy (gift appeal), grandparents use (usability matters)

### Fitness Equipment Niche

```bash
python .claude/skills/amazon-reviews-research/scripts/amazon_reviews.py \
    --search "resistance bands set" \
    --max-products 3 \
    --reviews-per-product 30 \
    --stars "1,5" \
    --output json > /tmp/resistance-bands.json
```

Expected findings:
- **Love**: "gym replacement," "travel-friendly," "physical therapy approved"
- **Hate**: "snapped during use," "handles broke," "resistance too light"
- **Gaps**: Better door anchors, exercise guide included, heavier resistance options

---

## How This Feeds Into Focus Groups

The voice_analysis output maps directly to focus group profile fields:

| Voice Analysis Field | Focus Group Field |
|---------------------|-------------------|
| love_phrases | marketingHooks, emotionalTriggers |
| hate_phrases | painPoints, objections |
| product_gaps | coreDesires, ebookAngles |
| emotional_triggers | emotionalTriggers, transformationPromise |
| buyer_vs_user | demographics (separate buyer/user personas) |
| gift_occasions | seasonalContext |

Use the `languagePatterns` field in focus groups to store the exact phrases from reviews. These are real customer words, not invented marketing copy.

---

## How This Feeds Into Product Development

| Voice Analysis Field | Product Decision |
|---------------------|-----------------|
| product_gaps | Feature roadmap priorities |
| hate_phrases | Problems your product must solve |
| love_phrases | Features to replicate or emphasize |
| buyer_vs_user.mismatch | Design for the user, market to the buyer |

---

## Known Limitations

- **Reviews per product**: Amazon shows ~8-13 "Top reviews" on the product detail page without requiring authentication. The `/product-reviews/` page requires sign-in, so the script cannot access paginated reviews. To compensate, scrape more products (`--max-products 5-10`) to increase the total review count.
- **Star distribution skew**: The "Top reviews" shown on product pages tend to skew toward higher ratings. To get more negative reviews, increase the number of products scraped -- some products will have negative reviews in their top results.
- **Star filtering**: The `--stars` flag filters collected reviews post-scrape. Since we can only collect what Amazon shows on the product page, some star ratings may have zero results for a given product.

---

## Rate Limiting and Ethical Scraping

- **Delays**: The script adds 2-4 second random delays between page loads to avoid triggering rate limits.
- **CAPTCHA handling**: If Amazon shows a CAPTCHA, the script logs a warning and moves to the next product. It does not attempt to solve CAPTCHAs.
- **Resource blocking**: Images, fonts, and other non-essential resources are blocked to reduce bandwidth and speed up scraping.
- **Headless browsing**: Uses headless Chromium with realistic user-agent strings.
- **Volume**: Keep scraping volume reasonable. 3-5 products with 20-30 reviews each is typical. Do not scrape hundreds of products in a single session.
- **Respect robots.txt**: Amazon's ToS restrict automated access. Use this tool for legitimate market research in reasonable volumes. Do not use for price monitoring, inventory tracking, or commercial data aggregation at scale.

---

## Prerequisites

```bash
pip install playwright && python -m playwright install chromium
```

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| CAPTCHA on every request | Reduce frequency. Try again after 10-15 minutes. Change IP if possible. |
| No products found | Try broader search terms. Check that Amazon is accessible from your network. |
| Empty reviews | The product may have few reviews for the selected star rating. Try `--stars "1,2,3,4,5"`. |
| Script hangs | Check network connectivity. The default timeout is 30 seconds per page load. |
| Playwright not found | Run `pip install playwright && python -m playwright install chromium`. |
