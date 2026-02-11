# External Services Registry — Integration Guide

> Complete inventory of all external services used by the vibe-marketing platform,
> how each can be integrated (MCP server, direct API, or both), cost tiers,
> and which agents/skills need them.
>
> **Related docs:**
> - `vibe-marketing-platform-v3.md` section 4 (Service Registry System)
> - `vibe-marketing-platform-v3.md` section 13 (Writing Strategy System — skill→agent bindings)

---

## Integration Methods

| Method | How It Works | When to Use |
|--------|-------------|-------------|
| **MCP Server** | Runs as a subprocess via `.mcp.json`. Agent calls tools like `mcp__firecrawl__scrape`. Real-time, no script needed. | When an official/well-maintained MCP exists. Preferred method. |
| **Direct API (script)** | Python script in `scripts/services/` calls REST API, returns JSON. Agent runs: `python scripts/services/seo/query_dataforseo.py`. | When no MCP exists, or MCP is too immature. |
| **Both** | MCP for interactive use, script for batch/cron jobs. | When you need both real-time agent access AND scheduled batch processing. |

**Decision rule:** Use MCP if official/well-maintained. Fall back to script if MCP is community-only with low maintenance. Some services benefit from both (e.g., Firecrawl MCP for agent scraping + script for batch crawls).

---

## 1. SEO & Keywords

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **DataForSEO** | $50 min deposit, pay-as-go (~$0.60/1K SERPs) | Both | Community | `dataforseo-mcp-server` (PyPI) | vibe-keyword-researcher, vibe-serp-analyzer, vibe-seo-auditor |
| 2 | **Ahrefs** | $129+/mo | MCP | Official | `ahrefs/ahrefs-mcp-server` (GitHub, remote) | vibe-keyword-researcher, vibe-competitor-analyst, vibe-seo-auditor |
| 3 | **SEMrush** | $139+/mo | MCP | Official | `developer.semrush.com/api/basics/semrush-mcp/` | vibe-keyword-researcher, vibe-competitor-analyst |
| 4 | **Google Keyword Planner** | Free (via Google Ads API) | Script | No | — | vibe-keyword-researcher |
| 5 | **AnswerThePublic** | Free tier / $9+/mo | Script | No | — | vibe-keyword-researcher |

**Recommendation:** Start with DataForSEO (cheapest, broadest coverage). Add Ahrefs MCP if budget allows — it's official and excellent for backlink analysis. SEMrush MCP is good for competitor gap analysis. You don't need all three.

**Script:** `scripts/services/seo/query_dataforseo.py`
**API keys:** `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` / `AHREFS_API_KEY` / `SEMRUSH_API_KEY`

---

## 2. SERP & Rank Tracking

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **DataForSEO SERP** | Included with DataForSEO | Both | Same as DataForSEO | (same) | vibe-serp-analyzer |
| 2 | **Google Search Console** | Free | Both | Community | `ahonn/mcp-server-gsc` (GitHub) | vibe-seo-auditor, analytics dashboard |
| 3 | **Bing Webmaster** | Free | Script | No | — | vibe-seo-auditor |

**Recommendation:** GSC is essential (free, authoritative data). DataForSEO SERP for competitive analysis. Bing is low priority.

**Script:** `scripts/services/seo/query_serp.py`, `scripts/services/seo/query_gsc.py`
**API keys:** GSC uses OAuth2 service account JSON

---

## 3. Web Scraping

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Firecrawl** | $19+/mo (free tier: 500 pages) | MCP | Official | `firecrawl-mcp` (npm) | vibe-competitor-analyst, vibe-content-writer (research), vibe-seo-auditor |
| 2 | **Crawl4AI** | Free (self-hosted) | Script | No | — | Batch crawling, sitemap analysis |
| 3 | **Apify** | Pay-as-go ($5 free/mo) | Script | Community (low quality) | — | Specialized scraping actors |
| 4 | **ScraperAPI** | $49+/mo | Script | No | — | CAPTCHA-protected sites |

**Recommendation:** Firecrawl MCP is the primary scraper — official MCP, LLM-ready markdown output. Crawl4AI for batch jobs. Apify for specialized scrapers (job listings, review sites). ScraperAPI only if you hit CAPTCHA walls.

**MCP config:** Already referenced in v3 `.mcp.json` as `firecrawl`
**API keys:** `FIRECRAWL_API_KEY` / `APIFY_TOKEN`

---

## 4. Social Platform Scraping / Monitoring

### X / Twitter

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **X API v2** | Free (Essential) / $100/mo (Basic) | Both | Community | Multiple repos (no official) | vibe-twitter-scout |
| 2 | **ScrapeCreators** | $10/5K credits | Script | No | — | Backup for X data |
| 3 | **Apify X Actor** | Pay-as-go | Script | No | — | Bulk historical scraping |

### Reddit

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Reddit API** | Free (rate limited: 100 req/min) | Both | Community | `GeLi2001/reddit-mcp`, `Hawstein/mcp-server-reddit` | vibe-reddit-scout |
| 2 | **ScrapeCreators** | $10/5K credits | Script | No | — | Backup |

### LinkedIn

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **PhantomBuster** | $69+/mo | Script | No | — | vibe-linkedin-scout |
| 2 | **ProxyCurl** | Pay-as-go ($0.01/profile) | Script | No | — | Profile enrichment |
| 3 | **LinkedIn API** | Free (limited to own company) | Both | Community | `linkedin-mcp-server` (npm) | Company page posting |

### Facebook / Instagram

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Meta Graph API** | Free | Both | Community | `facebook-mcp-server` | Social posting, ad management |
| 2 | **Apify Actors** | Pay-as-go | Script | No | — | Public page scraping |

### TikTok

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **TikTok API** | Limited official access | Script | No | — | vibe-social-writer (posting) |
| 2 | **ScrapeCreators** | $10/5K credits | Script | No | — | Trend scraping |

### YouTube

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **YouTube Data API v3** | Free (10K units/day) | Both | Community | `youtube-mcp-server` (npm), `@kirbah/mcp-youtube` | vibe-trend-detector, competitor research |
| 2 | **Apify YouTube Actors** | Pay-as-go | Script | No | — | Comment/transcript scraping |

### VK

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **VK API** | Free (generous limits) | Script | No | — | vibe-social-writer (VK posting) |

**Recommendation:** X API v2 (Free Essential tier) + Reddit API (free) as primary social scrapers. PhantomBuster for LinkedIn (no good free alternative). Meta Graph API for FB/IG. YouTube Data API for video research. Community MCPs for Reddit and X are decent; use scripts for the rest.

---

## 5. Image Generation

| # | Service | Cost | Integration | MCP Available? | MCP Package | Best For | Used By |
|---|---------|------|-------------|---------------|-------------|----------|---------|
| 1 | **FLUX Pro** (via fal.ai) | $0.05-0.10/img | Both | Community | `mcp-fal-ai-image` (npm) | Hero images, product shots | vibe-image-generator |
| 2 | **FLUX Schnell** (via fal.ai) | $0.003/img | Both | (same fal.ai MCP) | Quick drafts, thumbnails | vibe-image-generator |
| 3 | **Ideogram 3.0** | $7-20/mo | Script | No | — | Text-in-images, infographics, social graphics | vibe-image-generator |
| 4 | **DALL-E 3** (OpenAI) | $0.04-0.08/img | Both | Community | `spartanz51/imagegen-mcp` | General purpose | vibe-image-generator |
| 5 | **Midjourney** (via ImagineAPI) | $10-30/mo | Script | No | — | Artistic, brand imagery | vibe-image-generator |
| 6 | **Leonardo.ai** | Free tier + $10+/mo | Script | No | — | Character consistency | vibe-image-generator |
| 7 | **Recraft V3** | API access | Script | No | — | Vector, icon generation | vibe-image-generator |
| 8 | **Google Imagen 4** | Vertex AI pricing | Both | Community | `falahgs/imagen-3.0-generate-google-mcp-server`, via fal.ai | Photorealism, realistic faces | vibe-image-generator |
| 9 | **Replicate** (multi-model) | Pay-per-use | Both | Community | `@gongrzhe/image-gen-server` (npm), `awkoy/replicate-flux-mcp` | Access to any model on Replicate | vibe-image-generator |

**Recommendation:** FLUX Pro (via fal.ai MCP) as primary — best quality/cost ratio. FLUX Schnell for drafts. Ideogram for anything with text in the image. DALL-E 3 as fallback. Google Imagen 4 for photorealistic shots where FLUX falls short. Midjourney/Leonardo only for specialized brand work.

**Script:** `scripts/services/images/flux_generate.py`, `scripts/services/images/ideogram_generate.py`, `scripts/services/images/dalle_generate.py`, `scripts/services/images/imagen_generate.py`
**API keys:** `FAL_KEY` / `OPENAI_API_KEY` / `IDEOGRAM_API_KEY` / `GOOGLE_CLOUD_PROJECT` (for Vertex AI)

---

## 6. Templated Image Generation

| # | Service | Cost | Integration | MCP Available? | MCP Package | Best For | Used By |
|---|---------|------|-------------|---------------|-------------|----------|---------|
| 1 | **Bannerbear** | $49+/mo | Script | No | — | Templated social images (consistent brand) | vibe-image-generator |
| 2 | **Placid** | $29+/mo | Script | No | — | OG images, banners from templates | vibe-image-generator |

**Recommendation:** Only needed when you want pixel-perfect branded templates (e.g., "every blog post gets the same OG image layout with title + hero image + logo"). Skip for MVP — AI-generated images are sufficient.

---

## 7. Video Generation

| # | Service | Cost | Integration | MCP Available? | MCP Package | Best For | Used By |
|---|---------|------|-------------|---------------|-------------|----------|---------|
| 1 | **Runway Gen-4** | $12-76/mo | Both | Community | `wheattoast11/mcp-video-gen` (GitHub) | Hero/ad videos, 4K, motion control | vibe-video-generator |
| 2 | **Kling AI 2.1** | Budget-friendly | Script | No | — | Volume social clips | vibe-video-generator |
| 3 | **Pika Labs 2.0** | Free + $8/mo | Script | No | — | Short social content, quick iterations | vibe-video-generator |
| 4 | **Google Veo 3** | Vertex AI pricing | Both | Community | `mario-andreschak/mcp-veo2`, `alohc/veo-mcp-server` | Cinematic quality, includes audio | vibe-video-generator |
| 5 | **Sora 2** (OpenAI) | OpenAI API pricing | Script | No | — | Narrative, story-driven | vibe-video-generator |

**Recommendation:** Runway Gen-4 as primary (best motion control). Google Veo 3 for cinematic content with audio. Kling for budget bulk clips. Pika for quick social teasers. Sora when OpenAI API access stabilizes.

**Script:** `scripts/services/video/runway_generate.py`, `scripts/services/video/veo_generate.py`, `scripts/services/video/kling_generate.py`
**API keys:** `RUNWAY_API_KEY` / `GOOGLE_CLOUD_PROJECT` / `KLING_API_KEY`

---

## 8. AI Presenter / Talking Head

| # | Service | Cost | Integration | MCP Available? | MCP Package | Best For | Used By |
|---|---------|------|-------------|---------------|-------------|----------|---------|
| 1 | **HeyGen** | $18+/mo | Script | No | — | AI presenter/explainer videos | vibe-video-generator |
| 2 | **Synthesia** | $24+/mo | Script | No | — | Professional presenter, multi-language | vibe-video-generator |
| 3 | **D-ID** | Pay-as-go | Script | No | — | Photo-to-video, talking head | vibe-video-generator |

**Recommendation:** HeyGen for most use cases (cheapest, good quality). Synthesia for professional/corporate. D-ID for one-off photo animations.

---

## 9. Voice / Audio

| # | Service | Cost | Integration | MCP Available? | MCP Package | Best For | Used By |
|---|---------|------|-------------|---------------|-------------|----------|---------|
| 1 | **ElevenLabs** | Free tier + $5+/mo | MCP | Official | `elevenlabs/elevenlabs-mcp` (GitHub) | Voiceover, podcast, narration | vibe-video-generator, FUTURE: podcast agent |

**Recommendation:** ElevenLabs is the clear winner — official MCP, best quality, good free tier. No alternatives needed.

**MCP config:** `elevenlabs` via Docker image `mcp/elevenlabs`
**API keys:** `ELEVENLABS_API_KEY`

---

## 10. Email Sending

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **SendGrid** | Free (100/day) | Both | Community | `Garoth/sendgrid-mcp`, `@cong/sendgrid-mcp` (JSR) | vibe-email-writer (sending after approval) |
| 2 | **Mailgun** | Free (100/day, 30-day trial) | MCP | Official | `mailgun/mailgun-mcp-server` (GitHub) | Transactional email |
| 3 | **Brevo** (Sendinblue) | Free (300/day) | Script | No | — | Marketing campaigns |
| 4 | **Mailchimp** | Free tier | Script | No | — | Newsletter, audience management |
| 5 | **ConvertKit** | $29+/mo | Script | No | — | Creator-focused email sequences |

**Recommendation:** SendGrid (highest free tier for transactional) or Mailgun (official MCP, cleaner API). Brevo for marketing campaigns if you want a separate system. Mailchimp/ConvertKit only if user already has an account.

**Script:** `scripts/services/email/sendgrid.py`, `scripts/services/email/mailgun.py`
**API keys:** `SENDGRID_API_KEY` / `MAILGUN_API_KEY` + `MAILGUN_DOMAIN`

---

## 11. Social Publishing

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Buffer** | Free + $6+/channel/mo | Script | No (Zapier bridge only) | — | Multi-platform scheduling |
| 2 | **X API v2** (posting) | Free (Essential) | Both | Community | — | Direct X/Twitter posting |
| 3 | **LinkedIn API** | Free (limited) | Both | Community | `linkedin-mcp-server` (npm) | LinkedIn posting |
| 4 | **Meta Graph API** | Free | Both | Community | — | Facebook + Instagram posting |
| 5 | **Pinterest API** | Free | Script | No | — | Pin creation |
| 6 | **TikTok API** | Limited | Script | No | — | TikTok posting |
| 7 | **VK API** | Free | Script | No | — | VK posting |

**Recommendation:** Buffer as the unified publishing layer (covers X, LinkedIn, FB, IG, Pinterest, TikTok from one API). Direct APIs as fallback for platforms Buffer doesn't cover (VK) or when you need more control.

**Note:** Social posting is NEVER automated — agents draft content, human approves in dashboard, THEN publishing triggers. This is a design principle in v3.

---

## 12. CMS Publishing

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **WordPress REST API** | Free | MCP | Official | `WordPress/mcp-adapter` (WP plugin) | Publishing approved articles |
| 2 | **Ghost API** | Free (self-hosted) / $9+/mo | Both | Community | `@fanyangmeng/ghost-mcp` (npm) | Publishing to Ghost blogs |
| 3 | **Webflow CMS API** | Paid plan required | MCP | Official | `webflow/mcp-server` (GitHub) | Publishing to Webflow sites |
| 4 | **Custom REST API** | Varies | Script | No | — | Any CMS with a REST endpoint |
| 5 | **Static (markdown)** | Free | Script (just file write) | No | — | Markdown export to disk |

**Recommendation:** Depends on target CMS. WordPress MCP is official and excellent. Webflow MCP is official. Ghost community MCP is decent. For MVP, "Static" (just write markdown files) is fine — publish manually until CMS integration is built.

---

## 13. Content Quality

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Copyscape** | $0.03/check | Script | **No** | — | vibe-plagiarism-checker |
| 2 | **Copyleaks** | $9.16+/mo | Script | No | — | AI detection + plagiarism |
| 3 | **LanguageTool** | Free tier (open source) | Script | **No** (adjacent grammar MCP exists) | — | vibe-content-reviewer (grammar/style) |

**Note:** Copyscape and LanguageTool have NO MCP servers. Both have simple REST APIs — Python scripts are straightforward. LanguageTool can also be self-hosted (Java) for unlimited free usage.

**Script:** `scripts/services/quality/copyscape.py`, `scripts/services/quality/languagetool.py`
**API keys:** `COPYSCAPE_USER` + `COPYSCAPE_API_KEY` / LanguageTool: none if self-hosted

---

## 14. Web Search (for agent research)

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Brave Search** | Free (2K/mo) / $3/1K | MCP | Official | `@modelcontextprotocol/server-brave-search` (npm) | All research agents |
| 2 | **Google Custom Search** | Free (100/day) | Script | No | — | SEO research |
| 3 | **Perplexity** | $0.20/1K queries | MCP | Official | `perplexityai/modelcontextprotocol` (GitHub) | Deep research, fact-checking |

**Recommendation:** Brave Search MCP as primary (already in Claude Code's default MCP set). Perplexity MCP for deep research (returns synthesized answers, not just links). Google CSE only for specific site:search patterns.

**MCP config:** `brave-search` already standard in Claude Code
**API keys:** `BRAVE_API_KEY` / `PERPLEXITY_API_KEY`

---

## 15. Analytics & Tracking

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Google Search Console** | Free | Both | Community | `ahonn/mcp-server-gsc` (GitHub) | vibe-seo-auditor, analytics dashboard |
| 2 | **Google Analytics 4** | Free | MCP | Official (Google) | `developers.google.com/analytics/devguides/MCP` | Analytics reporting |
| 3 | **Plausible** | Self-hosted (free) / $9+/mo | Script | No | — | Privacy-friendly analytics |
| 4 | **Umami** | Self-hosted (free) | Script | No | — | Privacy-friendly analytics |

**Recommendation:** GSC + GA4 are the standard pair. Both have MCP servers (GA4 is official from Google). Plausible/Umami are alternatives if you want privacy-friendly analytics — pick one.

---

## 16. Advertising Platforms

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Google Ads** | Pay-per-click | MCP | Official (Google) | `googleads/google-ads-mcp` (GitHub, Python) | FUTURE: ad campaign management |
| 2 | **Meta Ads** (FB + IG) | Pay-per-click | Both | Community | `pipeboard-co/meta-ads-mcp`, `gomarble-ai/facebook-ads-mcp-server` | FUTURE: social ad campaigns |

**Recommendation:** Both are FUTURE features — not needed for MVP content generation. When ready, Google Ads has an official MCP. Meta Ads has community MCPs that work.

---

## 17. Notifications

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Telegram Bot API** | Free | Both | Community | `chigwell/telegram-mcp`, `sparfenyuk/mcp-telegram` | Pipeline notifications, review alerts |
| 2 | **Discord Webhook** | Free | Both | Community | `mcp-discord` (npm), `barryyip0625/mcp-discord` | Team notifications |
| 3 | **Slack Webhook** | Free | MCP | Official | `@modelcontextprotocol/server-slack` (npm) | Team notifications |

**Recommendation:** Telegram as primary (free, simple, mobile). Slack MCP is official and excellent if the team uses Slack. Discord for community-facing alerts. Pick one for MVP.

**Script:** `scripts/services/notifications/telegram_notify.py`
**API keys:** `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`

---

## 18. Document Generation

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **Pandoc** | Free (installed locally) | Bash | No (local tool) | — | md→html, md→docx, md→pdf |
| 2 | **Calibre** | Free (installed locally) | Bash | No (local tool) | — | epub/mobi generation |
| 3 | **Puppeteer/Playwright** | Free (installed locally) | Script | No (local tool) | — | html→pdf, screenshots |

**Recommendation:** All three are local tools, already available on the server. No API keys needed. Pandoc is the workhorse for format conversion.

---

## 19. Infrastructure & DevOps

| # | Service | Cost | Integration | MCP Available? | MCP Package | Used By |
|---|---------|------|-------------|---------------|-------------|---------|
| 1 | **GitHub** | Free | MCP | Official | `github/github-mcp-server` (Go binary) | Code hosting, CI/CD |
| 2 | **Cloudflare** | Free tier | MCP | Official | `@cloudflare/mcp-server-cloudflare` (npm) | DNS, CDN, Workers |
| 3 | **Vercel** | Free tier | MCP | Official | `@vercel/mcp-adapter` (npm) | Dashboard hosting (if migrating from PM2) |
| 4 | **Stripe** | Pay-as-go | MCP | Official | `@stripe/mcp` (npm), remote: `mcp.stripe.com` | FUTURE: payment processing |

**Recommendation:** GitHub MCP already available via `gh` CLI. Cloudflare for CDN/DNS. Vercel only if you migrate dashboard hosting. Stripe is a FUTURE feature.

---

## MCP Availability Summary

| Status | Count | Services |
|--------|-------|----------|
| **Official MCP** | 16 | Firecrawl, Brave Search, Perplexity, Ahrefs, SEMrush, GA4, Mailgun, Slack, WordPress, Webflow, ElevenLabs, Google Ads, Stripe, Cloudflare, Vercel, GitHub |
| **Community MCP** | 17 | DataForSEO, GSC, Reddit, X/Twitter, LinkedIn, YouTube, SendGrid, Telegram, Discord, Ghost, DALL-E, Replicate, fal.ai, Runway, Meta Ads, Google Imagen, Google Veo |
| **No MCP** | 12 | Google Keyword Planner, AnswerThePublic, Bing Webmaster, Crawl4AI, ScraperAPI, Apify, PhantomBuster, ProxyCurl, Copyscape, LanguageTool, Buffer, Bannerbear/Placid |
| **Local tools** | 3 | Pandoc, Calibre, Puppeteer |

---

## MVP Service Stack (Recommended)

The minimum set of services to get the first campaign pipeline running:

| Category | Service | Integration | Why |
|----------|---------|-------------|-----|
| **Web Search** | Brave Search | MCP (official) | Already in Claude Code default |
| **Web Scraping** | Firecrawl | MCP (official) | LLM-ready markdown |
| **SEO** | DataForSEO | Script + MCP | Cheapest, broadest coverage |
| **Social Scraping** | Reddit API | Script | Free, good for audience research |
| **Social Scraping** | X API v2 | Script | Free Essential tier |
| **Image Gen** | FLUX Pro (fal.ai) | MCP (community) | Best quality/cost |
| **Image Gen** | Ideogram 3.0 | Script | Text-in-images |
| **Notifications** | Telegram | Script | Free, simple |
| **Quality** | LanguageTool | Script (self-hosted) | Free, unlimited |

**Total recurring cost:** ~$50 DataForSEO deposit + $19 Firecrawl + ~$5 fal.ai credits = **~$74/mo** (plus Claude Max $200/mo).

### Phase 2 Additions

| Category | Service | Integration | Why |
|----------|---------|-------------|-----|
| **SEO** | Ahrefs | MCP (official) | Backlink analysis, keyword gap |
| **Video** | Runway Gen-4 | Script + MCP | Hero videos |
| **Video** | Google Veo 3 | Script + MCP | Cinematic with audio |
| **Email** | SendGrid or Mailgun | Script or MCP | Email sequence delivery |
| **Image Gen** | Google Imagen 4 | Script | Photorealism |
| **CMS** | WordPress or Ghost | MCP | Auto-publishing approved content |
| **Voice** | ElevenLabs | MCP (official) | Voiceover for videos |

### Phase 3 Additions (FUTURE)

| Category | Service | Integration | Why |
|----------|---------|-------------|-----|
| **Ads** | Google Ads | MCP (official) | Ad campaign management |
| **Ads** | Meta Ads | MCP (community) | Social ad campaigns |
| **Analytics** | GA4 | MCP (official) | ROI tracking |
| **Social Publishing** | Buffer | Script | Multi-platform scheduling |
| **Payments** | Stripe | MCP (official) | If selling content/services |

---

## How Services Connect to Skills and Agents

```
External Service → Service Registry (Convex) → resolve_service.py → Skill script
                                                                        ↓
                                              Agent loads skill → runs script → gets data
```

**Example flow: keyword research**
```
1. vibe-keyword-researcher wakes up (cron)
2. Loads keyword-research-procedures/SKILL.md
3. SKILL.md says: "Run scripts/resolve_service.py seo_keywords"
4. resolve_service.py checks Convex → DataForSEO is #1 priority, ACTIVE
5. Returns: scripts/services/seo/query_dataforseo.py
6. Agent runs the script with keyword parameters
7. Gets JSON response → writes content brief
```

**Example flow: image generation**
```
1. vibe-image-generator gets task (pipeline dispatch)
2. Loads image-generation-procedures/SKILL.md
3. SKILL.md says: "Run scripts/resolve_service.py image_generation hero_images"
4. resolve_service.py → FLUX Pro (fal.ai) is #1 for hero_images
5. Agent calls fal.ai MCP tool OR runs flux_generate.py
6. Gets image URL → downloads to campaign assets folder
```

---

## API Key Management

All API keys are stored in Convex `services` table (`apiKeyValue` field) and written to `.env` by the sync daemon. Agents read from `.env` or receive keys via the service resolution script.

**Required `.env` entries for MVP:**

```bash
# SEO
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=

# Scraping
FIRECRAWL_API_KEY=

# Images
FAL_KEY=
IDEOGRAM_API_KEY=

# Social
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Search
BRAVE_API_KEY=
```

**Phase 2 additions:**

```bash
# SEO
AHREFS_API_KEY=

# Images
OPENAI_API_KEY=
GOOGLE_CLOUD_PROJECT=

# Video
RUNWAY_API_KEY=

# Email
SENDGRID_API_KEY=

# Voice
ELEVENLABS_API_KEY=

# CMS
WORDPRESS_URL=
WORDPRESS_APP_PASSWORD=
```
