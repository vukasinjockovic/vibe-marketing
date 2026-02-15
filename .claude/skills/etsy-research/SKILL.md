---
name: etsy-research
displayName: Etsy Research
description: Search Etsy for product listings, reviews, shop analytics, and autocomplete suggestions. Free Playwright-based scraping. Extracts pricing, review language, bestseller signals, and competitor analysis for digital product strategy and audience research.
category: research
type: tool
---

# Etsy Research

Search Etsy for product listings, extract reviews, analyze shops, and discover autocomplete suggestions. Free Playwright-based scraping with zero API cost. Extracts pricing intelligence, customer voice data, bestseller signals, and competitor analysis for digital product strategy and audience research.

---

## When to Use

- **Digital product research**: Etsy is the largest marketplace for digital downloads, printables, templates, and handmade goods. Research what sells, at what price, and why customers buy.
- **Customer voice mining**: Extract the exact words customers use in reviews. 1-star and 5-star reviews provide the most valuable copy material.
- **Competitive intelligence**: Analyze competitor shops -- pricing strategy, bestseller identification, product categories, and review sentiment.
- **Keyword discovery**: Etsy's autocomplete reveals what buyers actually search for on the platform. Different from Google -- Etsy queries have higher purchase intent.
- **Pricing strategy**: Understand market pricing, identify price tiers, and find the sweet spot between volume and margin.
- **Product gap analysis**: Mine reviews for unmet needs, feature requests, and quality complaints that reveal opportunities.

---

## Flow-Aware Routing

### Engagement Flow
Use `etsy_search.py` to find trending products and extract listing descriptions, tags, and titles that get clicks. Focus on what language and imagery drives engagement. Use `etsy_suggest.py` for topic expansion and discovering what buyers actually search for.

```bash
# Find what language works in listing titles
python .claude/skills/etsy-research/scripts/etsy_search.py \
    --query "grandparent memory book" --max-listings 30 --sort top_reviews --output json

# Discover buyer search terms
python .claude/skills/etsy-research/scripts/etsy_suggest.py \
    --seed-keywords "grandparent gift" "memory book" --expand-alphabet --output json
```

### Sales Flow
Use `etsy_search.py` + `etsy_reviews.py` + `etsy_shop.py` for competitive intelligence -- pricing strategy, bestseller identification, review-based product improvement. Focus on what sells, at what price, and why customers buy.

```bash
# Market overview: pricing, bestsellers, competition
python .claude/skills/etsy-research/scripts/etsy_search.py \
    --query "digital planner template" --max-listings 20 --sort top_reviews --output json

# Deep dive on a competitor shop
python .claude/skills/etsy-research/scripts/etsy_shop.py \
    --shop-name "DuncanandStone" --max-listings 20 --output json

# Review mining for product intelligence
python .claude/skills/etsy-research/scripts/etsy_reviews.py \
    --search "grandparent journal" --max-products 3 --reviews-per-product 20 --stars "1,5" --output json
```

### Audience Flow
Use `etsy_reviews.py` to mine customer voice data (same 1-star/5-star strategy as Amazon skill). Use `etsy_search.py` to identify market gaps and underserved niches.

```bash
# Voice mining: love phrases, hate phrases, product gaps
python .claude/skills/etsy-research/scripts/etsy_reviews.py \
    --url "https://www.etsy.com/listing/12345/product-name" \
    --max-reviews 30 --stars "1,5" --output json

# Market gap identification
python .claude/skills/etsy-research/scripts/etsy_search.py \
    --query "grandparent gift personalized" --max-listings 30 --output json
```

---

## Scripts

### 1. etsy_search.py -- Search Listings

Search Etsy for products and extract listing data with market metrics.

```bash
python .claude/skills/etsy-research/scripts/etsy_search.py \
    --query "grandparent memory book" \
    --max-listings 20 \
    --sort relevancy \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--query` | Yes | -- | Search query |
| `--max-listings` | No | 20 | Max listings to extract |
| `--sort` | No | relevancy | Sort: relevancy, most_recent, highest_price, lowest_price, top_reviews |
| `--output` | No | json | Output format: json or markdown |
| `--scroll-count` | No | 4 | Scroll count for loading more results |

**Extracts per listing:** title, price, shop name, rating, review count, listing URL, image URL, bestseller badge, star seller badge, ad/promoted flag, free shipping.

**Computed metrics:** average price, price range, % with free shipping, % bestsellers.

### 2. etsy_reviews.py -- Extract Reviews

Extract and analyze reviews from Etsy product listings.

```bash
# From a specific listing URL
python .claude/skills/etsy-research/scripts/etsy_reviews.py \
    --url "https://www.etsy.com/listing/12345/product-name" \
    --max-reviews 30 \
    --stars "1,5" \
    --output json

# Search-based (finds products, then scrapes reviews)
python .claude/skills/etsy-research/scripts/etsy_reviews.py \
    --search "grandparent journal" \
    --max-products 3 \
    --reviews-per-product 15 \
    --stars "1,2,5" \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--url` | One of url/search | -- | Direct listing URL |
| `--search` | One of url/search | -- | Search query to find products |
| `--max-reviews` | No | 30 | Max reviews per listing (--url mode) |
| `--max-products` | No | 3 | Max products to scrape (--search mode) |
| `--reviews-per-product` | No | 15 | Reviews per product (--search mode) |
| `--stars` | No | "1,2,3,4,5" | Star ratings to include |
| `--output` | No | json | Output format: json or markdown |

**Voice analysis output:**
- **love_phrases**: Phrases from 4-5 star reviews indicating delight
- **hate_phrases**: Phrases from 1-2 star reviews indicating frustration
- **product_gaps**: What reviewers explicitly wish existed
- **gift_mentions**: Buyer vs recipient language, gift occasion detection

### 3. etsy_shop.py -- Shop Analysis

Analyze an Etsy shop for competitive intelligence.

```bash
# By shop URL
python .claude/skills/etsy-research/scripts/etsy_shop.py \
    --url "https://www.etsy.com/shop/DuncanandStone" \
    --max-listings 20 \
    --output json

# By shop name
python .claude/skills/etsy-research/scripts/etsy_shop.py \
    --shop-name "DuncanandStone" \
    --max-listings 20 \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--url` | One of url/shop-name | -- | Direct shop URL |
| `--shop-name` | One of url/shop-name | -- | Shop name |
| `--max-listings` | No | 20 | Max listings to extract |
| `--output` | No | json | Output format: json or markdown |

**Extracts:** shop name, total sales, total reviews, average rating, member since, location, about text, top listings with pricing and review counts.

**Pricing analysis:** price range, average price, median price, pricing tiers, bestseller price range.

### 4. etsy_suggest.py -- Autocomplete Suggestions

Discover what buyers search for on Etsy.

```bash
python .claude/skills/etsy-research/scripts/etsy_suggest.py \
    --seed-keywords "grandparent gift" "memory book" \
    --expand-alphabet \
    --output json
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--seed-keywords` | Yes | -- | 1-10 seed keywords |
| `--expand-alphabet` | No | false | Query 'seed a' through 'seed z' |
| `--output` | No | json | Output format: json or markdown |
| `--delay` | No | 0.3 | Delay between requests (seconds) |
| `--force-browser` | No | false | Skip API, use Playwright |

**Method:** Tries Etsy's AJAX autocomplete API first (zero deps, fast). Falls back to Playwright browser automation if the API requires authentication.

---

## The 1-Star + 5-Star Strategy

Same approach as Amazon reviews research. The most valuable customer voice data lives at the extremes.

- **5-star reviews** reveal what customers love -- emotional triggers, unexpected delights, marketing hook material
- **1-star reviews** reveal what customers hate -- unmet expectations, quality failures, objection-handling copy
- **3-star reviews** are lukewarm and rarely contain intense emotional language

Use `--stars "1,5"` for the fastest, most actionable research. Add 2-star with `--stars "1,2,5"` to expand the frustration dataset.

---

## Etsy vs Amazon

| Dimension | Etsy | Amazon |
|-----------|------|--------|
| Product type | Handmade, vintage, digital downloads | Mass-manufactured |
| Seller type | Small shops, individual creators | Brands, FBA sellers |
| Buyer intent | Gift-giving, personalization, unique | Convenience, price |
| Reviews | Fewer but more emotional | More but often generic |
| Search behavior | Niche, specific, occasion-driven | Broad, comparison-driven |

Use both skills together for comprehensive market research. Etsy reveals the premium/personalized end of a market; Amazon reveals the mass-market end.

---

## How This Feeds Into Focus Groups

| Voice Analysis Field | Focus Group Field |
|---------------------|-------------------|
| love_phrases | marketingHooks, emotionalTriggers |
| hate_phrases | painPoints, objections |
| product_gaps | coreDesires, ebookAngles |
| gift_mentions | demographics (buyer/recipient personas) |

---

## Integration with Other Skills

1. **amazon-reviews-research**: Cross-reference Etsy and Amazon reviews for the same product category to get full-spectrum voice data.
2. **google-suggest-research**: Compare Etsy autocomplete with Google autocomplete to find platform-specific search behavior.
3. **audience-research-procedures**: Feed Etsy review language into focus group profiles.
4. **content-strategy**: Use Etsy listing titles and tags as content inspiration.
5. **mbook-schwarz-awareness**: Map Etsy buyer language to awareness stages.
6. **pricing-strategy**: Use Etsy pricing analysis for market positioning.

---

## Rate Limiting and Ethical Scraping

- **Delays**: 2-4 second random delays between page loads (stricter than Amazon).
- **CAPTCHA handling**: If Etsy shows a CAPTCHA, the script logs a warning and continues. It does not attempt to solve CAPTCHAs.
- **Cookie consent**: Automatically dismisses Etsy's GDPR cookie banner.
- **Session warm-up**: Homepage visit before scraping to establish cookies (same pattern as Amazon skill).
- **Volume**: Keep scraping reasonable. 3-5 products with 15-20 reviews each is typical.

---

## Prerequisites

```bash
pip install playwright && python -m playwright install chromium
```

`etsy_suggest.py` works without Playwright when the API is accessible (uses only stdlib urllib).

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| CAPTCHA on every request | Reduce frequency. Wait 15-30 minutes. Change IP. |
| No listings found | Try broader search terms. Check Etsy accessibility. |
| Empty reviews | Listing may have few reviews for selected stars. Try all stars. |
| suggest.py returns nothing | API may require auth. Use `--force-browser` flag. |
| Playwright not found | Run `pip install playwright && python -m playwright install chromium`. |
