# Data Sources for Audience Intelligence

Where to find authentic audience data. Organized by source type with access methods and what to extract.

---

## 1. Reddit

**Why:** Unfiltered, authentic language. People on Reddit are anonymous and honest. The best source for language patterns, real frustrations, and identity markers.

**How to access:**
- Via `social_scraping_reddit` service (script: `scripts/scrape_reddit.py`)
- Via Brave Search: `site:reddit.com "{query}"`
- Manually browsing via web scraping

**What to search for:**
- `r/{niche}` -- the main subreddit for the industry
- `r/{niche} + "help"` or `"frustrated"` or `"struggling"`
- `r/{niche} + "recommend"` or `"worth it"` or `"review"`
- Cross-post subreddits: `r/AskReddit`, `r/NoStupidQuestions`
- Advice subreddits: `r/Advice`, `r/personalfinance`

**What to extract:**
- Direct quotes (language patterns)
- Problem descriptions in the poster's own words
- Identity markers: "as a [X], I..."
- Objection patterns: "I tried [X] but..."
- Emotional intensity markers
- Upvote counts (indicates resonance with the community)
- Top comments (often more articulate than the original post)

**Subreddit discovery strategy:**
1. Search for the product niche on reddit.com
2. Look at the sidebar of relevant subreddits for related communities
3. Check where competitors are mentioned
4. Search for cross-posts between communities

---

## 2. Competitor Websites

**Why:** Shows how competitors segment their audience, what messaging they use, and what problems they claim to solve.

**How to access:**
- Via `web_scraping` service (script: `scripts/analyze_competitors.py`)
- Via Brave Search for cached pages

**Pages to analyze:**
- **Homepage**: Headlines, hero section, value props
- **About page**: Mission, founding story (reveals audience values)
- **Pricing page**: Tiers reveal audience segments by budget/need
- **Testimonials page**: Real customer language and demographics
- **FAQ page**: Reveals common objections and concerns
- **Blog**: Topic selection reveals audience interests
- **Case studies**: Detailed audience demographics and outcomes

**What to extract:**
- Headlines and subheadlines (audience targeting signals)
- Testimonial quotes (authentic customer language)
- Feature emphasis (reveals what the audience cares about)
- Pricing tiers and their names (audience segmentation)
- FAQ questions (objection patterns)
- CTA text (what action they expect the audience to take)

---

## 3. Review Sites

**Why:** Reviews contain the most authentic post-purchase language. 3-star reviews are the goldmine -- they reveal what almost worked.

### SaaS / Software Products
- **G2** (g2.com): Structured reviews with pros/cons
- **Capterra** (capterra.com): Detailed software reviews
- **TrustRadius** (trustradius.com): In-depth B2B reviews
- **Product Hunt** (producthunt.com): Launch feedback and comments

### Consumer Products
- **Trustpilot** (trustpilot.com): Consumer service reviews
- **Amazon Reviews**: Product reviews with verified purchase tags
- **Consumer Reports**: Expert and user reviews

### Local / Service Businesses
- **Google Reviews**: Most accessible review source
- **Yelp** (yelp.com): Detailed service reviews
- **Better Business Bureau** (bbb.org): Complaint patterns

### App Reviews
- **Apple App Store**: iOS app reviews
- **Google Play Store**: Android app reviews

**How to access:**
- Via `web_scraping` service (script: `scripts/scrape_reviews.py`)
- Via Brave Search: `site:g2.com "{product name}"`
- Review aggregator APIs (where available)

**What to extract by rating:**
- **5-star reviews**: What delighted them? What words do happy customers use?
- **4-star reviews**: What was almost perfect? What small things are missing?
- **3-star reviews**: What went wrong that was fixable? What expectations were unmet?
- **2-star reviews**: What major issues exist? What alternatives are they considering?
- **1-star reviews**: What deal-breakers exist? What was the gap between expectation and reality?

---

## 4. Forums and Online Communities

**Why:** Niche forums contain domain-expert-level audience language and deeply specific pain points.

**General Forums:**
- **Quora** (quora.com): Question-answer format reveals exactly what people want to know
- **Stack Exchange** (various): Technical communities
- **Discord** (via web search): Community conversations

**Niche Forum Discovery:**
- Search: `"{niche} forum"` or `"{niche} community"`
- Look for industry-specific platforms
- Check subreddit sidebars for forum links

**How to access:**
- Via Brave Search: `site:quora.com "{niche} problem"`
- Via web scraping for forum threads

**What to extract:**
- Question phrasing (reveals awareness level)
- Problem descriptions
- "What worked for me" stories
- Debates between approaches (reveals market sophistication)
- Expert vs. beginner language differences

---

## 5. Social Media

**Why:** Real-time audience language, trending concerns, and cultural context.

### Twitter/X
- Search hashtags related to the niche
- Look at replies to competitor accounts
- Monitor complaint threads
- Check quote tweets of competitor content

### Facebook Groups
- Search for niche-specific groups
- Observe question patterns
- Note recurring frustrations
- Look at admin post engagement levels

### LinkedIn
- Industry-specific posts and comments
- Professional audience language
- B2B buying signals
- Career-related motivations

### TikTok / Instagram
- Comment sections on niche content
- Creator content themes (reveals audience interests)
- Hashtag analysis

**How to access:**
- Via Brave Search with site filters
- Via social media scraping services
- Via MCP tools (Twitter API, etc.)

**What to extract:**
- Conversational language (very different from formal writing)
- Emotional reactions (emojis, caps, exclamation marks)
- Hashtag self-identification
- Complaint patterns directed at competitors

---

## 6. Industry Reports and Data

**Why:** Provides demographic data, market size, and trend information that is hard to get from qualitative sources.

**Sources:**
- **SEMrush / Ahrefs**: Keyword data reveals what the audience searches for
- **Google Trends**: Interest over time, related queries, geographic data
- **Statista**: Market statistics and demographics
- **Pew Research**: Demographic and psychographic studies
- **US Census / Bureau of Labor Statistics**: Population data
- **Industry association reports**: Market-specific data
- **Think with Google**: Consumer insight data

**How to access:**
- Via Brave Search for published reports and summaries
- Via SEO tools (if configured as services)
- Via web scraping for publicly available report pages

**What to extract:**
- Market size and growth rate
- Demographic breakdowns (age, gender, income, geography)
- Behavioral trends (growing vs. declining interests)
- Spending patterns
- Technology adoption rates

---

## 7. Customer Support and Sales Data

**Why:** Direct insight into what customers struggle with, ask about, and object to.

**Sources (if available):**
- Support ticket themes
- FAQ page analytics
- Chat transcript analysis
- Sales call recordings/notes
- Cancellation surveys
- NPS feedback

**How to access:**
- Usually provided by the product team
- Look for published case studies that reference these
- Check competitor help centers for topic organization

**What to extract:**
- Most common questions (reveals confusion points)
- Most common complaints (reveals pain points)
- Reasons for churn (reveals unmet expectations)
- Feature requests (reveals desires)

---

## Source Priority for Research

Given limited time, prioritize sources in this order:

| Priority | Source | Why |
|----------|--------|-----|
| 1 | Reddit + Forums | Authentic language, unfiltered emotions |
| 2 | Reviews (G2, Trustpilot, Amazon) | Post-purchase honesty |
| 3 | Competitor websites | Audience targeting signals |
| 4 | Social media | Real-time language and trends |
| 5 | Industry reports | Demographic data |
| 6 | Customer support data | Direct customer voice (if available) |

When `social_scraping_reddit` is unavailable, use Brave Search with `site:reddit.com` to access cached Reddit content. When `web_scraping` is unavailable, use Brave Search to find review excerpts in search result snippets.
