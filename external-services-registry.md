# External Services Registry — Integration & Setup Guide

> Complete capability-first architecture for all external services used by the vibe-marketing
> platform. Agents depend on **capabilities**, not specific services. The setup script installs
> everything, prompts for API keys, and the dashboard gates agents based on which capabilities
> have active providers.
>
> **Related docs:**
> - `vibe-marketing-platform-v3.md` section 4 (Service Registry System)
> - `vibe-marketing-platform-v3.md` section 7 (MCP Server Configuration)
> - `vibe-marketing-platform-v3.md` section 13 (Writing Strategy System)

---

## 1. Architecture Overview

### Capability Abstraction Layer

Agents never reference specific services directly. Instead, every agent declares which **capabilities** it requires, and the platform resolves those capabilities to concrete service providers at runtime. This decouples agents from vendors and enables zero-code service swapping.

```
Agent SKILL.md                    Capability Layer                Service Providers
+-----------------------+        +------------------+        +---------------------+
| vibe-keyword-researcher|  --->  | seo_keywords     |  --->  | 1. DataForSEO       |
| requires:              |        |                  |        | 2. Ahrefs           |
|   - seo_keywords       |        +------------------+        | 3. SEMrush          |
|   - web_search         |                                    +---------------------+
+-----------------------+
```

### Service Resolution Flow

```
1. Agent receives task from orchestrator
2. Agent's SKILL.md declares: "resolve_service.py <capability> [use_case]"
3. resolve_service.py queries Convex serviceCategories + services tables
4. Returns the highest-priority ACTIVE provider for that capability
5. Agent executes the provider's script or calls its MCP tool
6. If provider fails --> resolve_service.py returns next-priority provider (fallback)
7. If all providers fail --> agent logs error, sets task to "blocked"
```

### Integration Points

```
scripts/setup.sh             --> Installs everything, prompts for API keys
docker-compose.services.yml  --> Self-hosted containers (Crawl4AI, LanguageTool, etc.)
.mcp.json                    --> MCP server entries (env var placeholders)
.env                         --> API keys (written by setup script)
Convex services table        --> Runtime service state (active/inactive, priority)
scripts/resolve_service.py   --> Agent-facing service resolution with fallback
Dashboard Settings/Services  --> UI for toggling services, reordering priority
```

---

## 2. Service Capabilities

The abstract layer. Agents depend on these capability keys, never on specific service names.

| Capability Key | Display Name | Required By (agents) | Min Providers Needed | Free Tier Available? | Self-Hosted Option? |
|----------------|-------------|---------------------|---------------------|---------------------|-------------------|
| `seo_keywords` | SEO & Keywords | vibe-keyword-researcher, vibe-seo-auditor, vibe-keyword-deep-researcher | 1 | Yes (Google Keyword Planner) | No |
| `serp_tracking` | SERP & Rank Tracking | vibe-serp-analyzer, vibe-seo-auditor | 1 | Yes (Google Search Console) | No |
| `web_scraping` | Web Scraping | vibe-competitor-analyst, vibe-content-writer, vibe-seo-auditor, vibe-brand-monitor | 1 | Yes (Crawl4AI) | Yes (Crawl4AI) |
| `social_scraping_x` | X/Twitter Scraping | vibe-twitter-scout | 1 | Yes (X API Free Essential) | No |
| `social_scraping_reddit` | Reddit Scraping | vibe-reddit-scout | 1 | Yes (Reddit API) | No |
| `social_scraping_linkedin` | LinkedIn Scraping | vibe-linkedin-scout | 1 | No | No |
| `social_scraping_meta` | Meta (FB/IG) Scraping | vibe-social-writer, vibe-brand-monitor | 1 | Yes (Meta Graph API) | No |
| `social_scraping_tiktok` | TikTok Scraping | vibe-trend-detector | 1 | No | No |
| `social_scraping_youtube` | YouTube Scraping | vibe-trend-detector, vibe-review-harvester | 1 | Yes (YouTube Data API v3) | No |
| `social_scraping_vk` | VK Scraping | vibe-social-writer | 1 | Yes (VK API) | No |
| `image_generation` | Image Generation | vibe-image-generator | 1 | No (all paid, but very cheap) | No |
| `templated_images` | Templated Image Gen | vibe-image-generator | 0 (OPTIONAL) | No | No |
| `video_generation` | Video Generation | vibe-video-generator | 1 | Yes (Pika free tier) | No |
| `ai_presenter` | AI Presenter / Talking Head | vibe-video-generator | 0 (OPTIONAL) | No | No |
| `voice_synthesis` | Voice / Audio | vibe-video-generator | 0 (OPTIONAL) | Yes (ElevenLabs free tier) | No |
| `email_sending` | Email Sending | vibe-email-writer | 1 | Yes (SendGrid 100/day, Brevo 300/day) | No |
| `social_publishing` | Social Publishing | vibe-social-writer | 1 | Yes (direct platform APIs) | No |
| `cms_publishing` | CMS Publishing | vibe-content-writer | 0 (OPTIONAL) | Yes (WordPress, Static) | Yes (self-hosted WP/Ghost) |
| `content_quality` | Content Quality | vibe-content-reviewer, vibe-plagiarism-checker | 1 | Yes (LanguageTool self-hosted) | Yes (LanguageTool) |
| `web_search` | Web Search | All research agents (8+) | 1 | Yes (Brave 2K/mo) | No |
| `analytics` | Analytics & Tracking | Dashboard, vibe-seo-auditor | 1 | Yes (GSC, GA4, Plausible, Umami) | Yes (Plausible, Umami) |
| `advertising` | Advertising Platforms | FUTURE | 0 (FUTURE) | No | No |
| `notifications` | Notifications | vibe-orchestrator | 1 | Yes (Telegram, Discord, Slack) | No |
| `document_generation` | Document Generation | vibe-ebook-writer | 0 (LOCAL) | Yes (all local tools) | Yes (Pandoc, Calibre, Puppeteer) |

---

## 3. Agent Dependency Matrix

This is the core table that determines agent gating in the pipeline builder. If an agent's REQUIRED capabilities have zero active providers, it is disabled (undraggable) in the pipeline UI.

### Research Phase Agents

| Agent | web_search | seo_keywords | serp_tracking | web_scraping | social_scraping_x | social_scraping_reddit | social_scraping_linkedin | social_scraping_meta | social_scraping_tiktok | social_scraping_youtube | content_quality | Free Minimum Path |
|-------|-----------|-------------|--------------|-------------|-------------------|----------------------|------------------------|---------------------|----------------------|------------------------|----------------|------------------|
| vibe-keyword-researcher | REQUIRED | REQUIRED | -- | -- | -- | -- | -- | -- | -- | -- | -- | Brave Search (free) + Google Keyword Planner (free) |
| vibe-competitor-analyst | REQUIRED | -- | -- | REQUIRED | -- | -- | -- | -- | -- | -- | -- | Brave Search (free) + Crawl4AI (self-hosted) |
| vibe-brand-monitor | REQUIRED | -- | -- | REQUIRED | -- | -- | OPTIONAL | -- | -- | -- | -- | Brave Search (free) + Crawl4AI (self-hosted) |
| vibe-reddit-scout | -- | -- | -- | -- | -- | REQUIRED | -- | -- | -- | -- | -- | Reddit API (free) |
| vibe-twitter-scout | -- | -- | -- | -- | REQUIRED | -- | -- | -- | -- | -- | -- | X API v2 Essential (free) |
| vibe-linkedin-scout | -- | -- | -- | -- | -- | -- | REQUIRED | -- | -- | -- | -- | PhantomBuster ($69/mo) or ProxyCurl (pay-as-go) |
| vibe-trend-detector | REQUIRED | -- | -- | -- | -- | -- | -- | -- | OPTIONAL | REQUIRED | -- | Brave Search (free) + YouTube Data API (free) |
| vibe-review-harvester | REQUIRED | -- | -- | REQUIRED | -- | -- | -- | -- | -- | OPTIONAL | -- | Brave Search (free) + Crawl4AI (self-hosted) |

### Audience Intelligence Agents

| Agent | web_search | web_scraping | social_scraping_reddit | social_scraping_x | Free Minimum Path |
|-------|-----------|-------------|----------------------|-------------------|------------------|
| vibe-audience-parser | -- | -- | -- | -- | No external services needed (parses uploaded docs) |
| vibe-audience-researcher | REQUIRED | OPTIONAL | OPTIONAL | OPTIONAL | Brave Search (free) |
| vibe-audience-enricher | REQUIRED | OPTIONAL | OPTIONAL | OPTIONAL | Brave Search (free) |

### SEO Phase Agents

| Agent | seo_keywords | serp_tracking | web_scraping | web_search | content_quality | Free Minimum Path |
|-------|-------------|--------------|-------------|-----------|----------------|------------------|
| vibe-keyword-deep-researcher | REQUIRED | REQUIRED | -- | REQUIRED | -- | Google Keyword Planner (free) + GSC (free) + Brave (free) |
| vibe-serp-analyzer | REQUIRED | REQUIRED | -- | REQUIRED | -- | Google Keyword Planner (free) + GSC (free) + Brave (free) |
| vibe-seo-auditor | REQUIRED | REQUIRED | REQUIRED | REQUIRED | OPTIONAL | Google Keyword Planner (free) + GSC (free) + Crawl4AI (self-hosted) + Brave (free) |

### Content Creation Agents

| Agent | web_search | image_generation | email_sending | social_publishing | cms_publishing | document_generation | Free Minimum Path |
|-------|-----------|-----------------|--------------|-------------------|---------------|--------------------|--------------------|
| vibe-content-writer | OPTIONAL | -- | -- | -- | OPTIONAL | -- | No external services required (skills only) |
| vibe-landing-page-writer | OPTIONAL | -- | -- | -- | -- | -- | No external services required (skills only) |
| vibe-email-writer | -- | -- | OPTIONAL | -- | -- | -- | No external services required for drafting; SendGrid (free) for sending |
| vibe-social-writer | -- | -- | -- | OPTIONAL | -- | -- | No external services required for drafting; direct APIs (free) for posting |
| vibe-script-writer | -- | -- | -- | -- | -- | -- | No external services required (skills only) |
| vibe-ebook-writer | -- | -- | -- | -- | -- | REQUIRED | Pandoc + Calibre (local, free) |
| vibe-content-repurposer | -- | -- | -- | -- | -- | -- | No external services required (skills only) |
| vibe-ad-writer | -- | -- | -- | -- | -- | -- | No external services required (skills only) |
| vibe-press-writer | -- | -- | -- | -- | -- | -- | No external services required (skills only) |

### Quality Assurance Agents

| Agent | content_quality | web_search | Free Minimum Path |
|-------|----------------|-----------|------------------|
| vibe-content-reviewer | OPTIONAL | -- | LanguageTool self-hosted (free) |
| vibe-humanizer | -- | -- | No external services required (skills only) |
| vibe-fact-checker | REQUIRED | REQUIRED | Brave Search (free) |
| vibe-plagiarism-checker | REQUIRED | -- | Copyscape ($0.03/check) -- no free alternative |

### Media Generation Agents

| Agent | image_generation | templated_images | video_generation | ai_presenter | voice_synthesis | Free Minimum Path |
|-------|-----------------|-----------------|-----------------|-------------|----------------|------------------|
| vibe-image-director | -- | -- | -- | -- | -- | No external services required (creates prompts only) |
| vibe-image-generator | REQUIRED | OPTIONAL | -- | -- | -- | FLUX.2 [dev] Turbo via fal.ai ($0.008/img, near-free) |
| vibe-video-generator | -- | -- | REQUIRED | OPTIONAL | OPTIONAL | Pika Labs free tier |

### Orchestration & Infrastructure

| Agent | notifications | analytics | Free Minimum Path |
|-------|-------------|----------|------------------|
| vibe-orchestrator | REQUIRED | -- | Telegram Bot (free) |

### FUTURE Agents (Post-MVP)

| Agent | Capability Needed | Status |
|-------|------------------|--------|
| vibe-publisher | cms_publishing | FUTURE |
| vibe-social-distributor | social_publishing | FUTURE |
| vibe-email-distributor | email_sending | FUTURE |
| vibe-analytics-reporter | analytics | FUTURE |
| vibe-rank-tracker | serp_tracking | FUTURE |
| vibe-content-refresher | analytics, web_search | FUTURE |
| vibe-roi-calculator | analytics | FUTURE |

---

## 4. Service Providers by Capability

### seo_keywords

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **DataForSEO** | $50 min deposit, pay-as-go (~$0.60/1K SERPs) | No | No | Both (MCP + script) | Community (`dataforseo-mcp-server` PyPI) | `pip install dataforseo-mcp-server` |
| 2 | **Ahrefs** | $129+/mo | No | No | MCP | Official (`ahrefs/ahrefs-mcp-server` GitHub, remote) | Remote MCP (no local install) |
| 3 | **SEMrush** | $139+/mo | No | No | MCP | Official (`developer.semrush.com/api/basics/semrush-mcp/`) | Remote MCP (no local install) |
| 4 | **Google Keyword Planner** | Free (via Google Ads API) | Yes | No | Script | No | `pip install google-ads` |
| 5 | **AnswerThePublic** | Free tier / $9+/mo | Yes (limited) | No | Script | No | HTTP API (no install) |

**Recommendation:** Start with DataForSEO (cheapest, broadest coverage). Add Ahrefs MCP if budget allows -- it is official and excellent for backlink analysis. SEMrush MCP is good for competitor gap analysis. Google Keyword Planner is the only truly free option. You do not need all of them.

**Scripts:** `scripts/services/seo/query_dataforseo.py`, `scripts/services/seo/query_ahrefs.py`, `scripts/services/seo/query_semrush.py`, `scripts/services/seo/query_gkp.py`, `scripts/services/seo/query_atp.py`
**API keys:** `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` / `AHREFS_API_KEY` / `SEMRUSH_API_KEY` / `GOOGLE_ADS_DEVELOPER_TOKEN`

### serp_tracking

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **DataForSEO SERP** | Included with DataForSEO | No | No | Both | Community (same as DataForSEO) | Same as DataForSEO |
| 2 | **Google Search Console** | Free | Yes | No | Both | Community (`ahonn/mcp-server-gsc` GitHub) | `npx -y @anthropic-ai/mcp-server-gsc` (or git clone) |
| 3 | **Bing Webmaster** | Free | Yes | No | Script | No | HTTP API (no install) |

**Recommendation:** GSC is essential (free, authoritative data). DataForSEO SERP for competitive analysis. Bing is low priority.

**Scripts:** `scripts/services/seo/query_serp.py`, `scripts/services/seo/query_gsc.py`, `scripts/services/seo/query_bing.py`
**API keys:** GSC uses OAuth2 service account JSON / `BING_WEBMASTER_API_KEY`

### web_scraping

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Firecrawl** | $19+/mo (free tier: 500 pages) | Yes (500 pages) | No | MCP | Official (`firecrawl-mcp` npm) | `npx -y firecrawl-mcp` |
| 2 | **Crawl4AI** | Free (self-hosted) | Yes | Yes | Script | No | `docker pull unclecode/crawl4ai` |
| 3 | **Apify** | Pay-as-go ($5 free/mo) | Yes ($5 credit) | No | Script | Community (low quality) | HTTP API (no install) |
| 4 | **ScraperAPI** | $49+/mo | No | No | Script | No | HTTP API (no install) |

**Recommendation:** Firecrawl MCP is the primary scraper -- official MCP, LLM-ready markdown output. Crawl4AI for batch jobs and as a free self-hosted fallback. Apify for specialized scrapers (job listings, review sites). ScraperAPI only if you hit CAPTCHA walls.

**Scripts:** `scripts/services/scraping/firecrawl_scrape.py`, `scripts/services/scraping/crawl4ai.py`, `scripts/services/scraping/apify_scrape.py`, `scripts/services/scraping/scraper_api.py`
**API keys:** `FIRECRAWL_API_KEY` / `APIFY_TOKEN` / `SCRAPER_API_KEY`

### social_scraping_x

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **X API v2** | Free (Essential) / $100/mo (Basic) | Yes | No | Both | Community (multiple repos, no official) | HTTP API (no install) |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script | No | HTTP API (no install) |
| 3 | **Apify X Actor** | Pay-as-go | Yes ($5 credit) | No | Script | No | HTTP API via Apify |

### social_scraping_reddit

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Reddit API** | Free (rate limited: 100 req/min) | Yes | No | Both | Community (`GeLi2001/reddit-mcp`, `Hawstein/mcp-server-reddit`) | `pip install praw` or MCP: git clone |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script | No | HTTP API (no install) |

### social_scraping_linkedin

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **PhantomBuster** | $69+/mo | No | No | Script | No | HTTP API (no install) |
| 2 | **ProxyCurl** | Pay-as-go ($0.01/profile) | No | No | Script | No | HTTP API (no install) |
| 3 | **LinkedIn API** | Free (limited to own company) | Yes (limited) | No | Both | Community (`linkedin-mcp-server` npm) | `npm install linkedin-mcp-server` |

### social_scraping_meta

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Meta Graph API** | Free | Yes | No | Both | Community (`facebook-mcp-server`) | HTTP API (no install) |
| 2 | **Apify Actors** | Pay-as-go | Yes ($5 credit) | No | Script | No | HTTP API via Apify |

### social_scraping_tiktok

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **TikTok API** | Limited official access | Limited | No | Script | No | HTTP API (no install) |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script | No | HTTP API (no install) |

### social_scraping_youtube

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **YouTube Data API v3** | Free (10K units/day) | Yes | No | Both | Community (`youtube-mcp-server` npm, `@kirbah/mcp-youtube`) | `npm install youtube-mcp-server` |
| 2 | **Apify YouTube Actors** | Pay-as-go | Yes ($5 credit) | No | Script | No | HTTP API via Apify |

### social_scraping_vk

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **VK API** | Free (generous limits) | Yes | No | Script | No | HTTP API (no install) |

**Social Scraping Recommendation:** X API v2 (Free Essential tier) + Reddit API (free) as primary social scrapers. PhantomBuster for LinkedIn (no good free alternative). Meta Graph API for FB/IG. YouTube Data API for video research. VK API for Russian markets. Community MCPs for Reddit and YouTube are decent; use scripts for the rest.

**Scripts:** `scripts/services/social/x_api.py`, `scripts/services/social/reddit_api.py`, `scripts/services/social/phantombuster_li.py`, `scripts/services/social/proxycurl.py`, `scripts/services/social/meta_graph.py`, `scripts/services/social/tiktok_api.py`, `scripts/services/social/youtube_api.py`, `scripts/services/social/vk_api.py`
**API keys:** `X_BEARER_TOKEN` / `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` / `PHANTOMBUSTER_API_KEY` / `PROXYCURL_API_KEY` / `META_ACCESS_TOKEN` / `TIKTOK_API_KEY` / `YOUTUBE_API_KEY` / `VK_SERVICE_TOKEN`

### image_generation

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method | Best For |
|----------|---------|------|-----------|-------------|-------------|------|----------------|----------|
| 1 | **FLUX.2 [pro]** (via fal.ai) | $0.03/MP (~$0.03 for 1024x1024) | No | No | Both | Community (`fal-ai-mcp-server` npm v2.1) | `npx fal-ai-mcp-server` | Hero images, product shots, photorealism |
| 2 | **FLUX.2 [dev] Turbo** (via fal.ai) | $0.008/MP (~$0.008 for 1024x1024) | No | No | Both | (same fal.ai MCP) | Same as above | Quick drafts, thumbnails, bulk generation |
| 3 | **GPT Image 1.5** (OpenAI) | $0.009-0.17/img (low/med/high quality) | No | No | Both | Community (`SureScaleAI/openai-gpt-image-mcp`) | `npx openai-gpt-image-mcp` | General purpose, editing/inpainting, text rendering |
| 4 | **Ideogram 3.0** | API: ~$0.04-0.05/img; Plans: $8-60/mo | Yes (10 slow/day, public) | No | Both | Community (`@sunwood-ai-labs/ideagram-mcp-server` npm) | `npx @sunwood-ai-labs/ideagram-mcp-server` | Text-in-images, infographics, multi-language text |
| 5 | **Google Imagen 4** | $0.02-0.06/img (Fast/Standard/Ultra) | No | No | Both | Community (Google Genmedia MCP in preview) | Gemini API or Vertex AI SDK | Photorealism, 4K output, product photography |
| 6 | **Recraft V3** | $0.04/raster, $0.08/vector; Plans: $10-48/mo | Yes (50 daily) | No | Both | Official (`recraft-ai/mcp-recraft-server`) | `npx @anthropic-ai/mcp-recraft-server` | Vector/SVG generation, icons, text positioning |
| 7 | **Midjourney V7** (via ImagineAPI/PiAPI) | MJ: $10-120/mo + API proxy fee | No | No | Script | Community (3rd-party API: `z23cc/midjourney-mcp`) | HTTP API (no install) | Artistic, brand imagery, character consistency |
| 8 | **Leonardo.ai Phoenix** | Free + $10-24/mo (API: $9-299/mo) | Yes (limited) | No | Both | Community (`ish-joshi/leonardo-mcp-server`, official docs) | HTTP API (no install) | Character consistency, prompt adherence |
| 9 | **Replicate** (multi-model) | $0.003-0.055/img | No | No | Both | Official (hosted at `mcp.replicate.com`) | Remote MCP (OAuth) | Access to 600+ models (FLUX.2, Ideogram, Seedream, etc.) |

**Recommendation:** FLUX.2 [pro] (via fal.ai MCP) as primary -- best quality/cost ratio. FLUX.2 [dev] Turbo for drafts/bulk. GPT Image 1.5 for general purpose + editing/inpainting (replaces DALL-E 3, deprecated May 2026). Ideogram 3.0 for text-heavy designs (now with MCP). Google Imagen 4 for photorealistic shots (now on Gemini API, not just Vertex). Recraft V3 for vectors/icons (official MCP). Midjourney/Leonardo only for specialized brand work.

**Scripts:** `scripts/services/images/flux_generate.py`, `scripts/services/images/ideogram_generate.py`, `scripts/services/images/gpt_image_generate.py`, `scripts/services/images/imagen_generate.py`
**API keys:** `FAL_KEY` / `OPENAI_API_KEY` / `IDEOGRAM_API_KEY` / `GOOGLE_CLOUD_PROJECT` (for Vertex AI) or `GOOGLE_API_KEY` (for Gemini API) / `REPLICATE_API_TOKEN` / `IMAGINEAPI_KEY` / `LEONARDO_API_KEY` / `RECRAFT_API_KEY`

### templated_images

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Bannerbear** | $49+/mo | No | No | Script | No | HTTP API (no install) |
| 2 | **Placid** | $29+/mo | No | No | Script | No | HTTP API (no install) |

**Recommendation:** Only needed when you want pixel-perfect branded templates (e.g., "every blog post gets the same OG image layout with title + hero image + logo"). Skip for MVP -- AI-generated images are sufficient.

### video_generation

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method | Best For |
|----------|---------|------|-----------|-------------|-------------|------|----------------|----------|
| 1 | **Runway Gen-4** | $12-76/mo | No | No | Both | Community (`wheattoast11/mcp-video-gen` GitHub) | `git clone` + install | Hero/ad videos, 4K, motion control |
| 2 | **Kling AI 2.1** | Budget-friendly | No | No | Script | No | HTTP API (no install) | Volume social clips |
| 3 | **Pika Labs 2.0** | Free + $8/mo | Yes | No | Script | No | HTTP API (no install) | Short social content, quick iterations |
| 4 | **Google Veo 3** | Vertex AI pricing | No | No | Both | Community (`mario-andreschak/mcp-veo2`, `alohc/veo-mcp-server`) | `git clone` + install | Cinematic quality, includes audio |
| 5 | **Sora 2** (OpenAI) | OpenAI API pricing | No | No | Script | No | HTTP API (no install) | Narrative, story-driven |

**Recommendation:** Runway Gen-4 as primary (best motion control). Google Veo 3 for cinematic content with audio. Kling for budget bulk clips. Pika for quick social teasers. Sora when OpenAI API access stabilizes.

**Scripts:** `scripts/services/video/runway_generate.py`, `scripts/services/video/veo_generate.py`, `scripts/services/video/kling_generate.py`, `scripts/services/video/pika_generate.py`, `scripts/services/video/sora_generate.py`
**API keys:** `RUNWAY_API_KEY` / `GOOGLE_CLOUD_PROJECT` / `KLING_API_KEY` / `PIKA_API_KEY` / `OPENAI_API_KEY`

### ai_presenter

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **HeyGen** | $18+/mo | No | No | Script | No | HTTP API (no install) |
| 2 | **Synthesia** | $24+/mo | No | No | Script | No | HTTP API (no install) |
| 3 | **D-ID** | Pay-as-go | No | No | Script | No | HTTP API (no install) |

**Recommendation:** HeyGen for most use cases (cheapest, good quality). Synthesia for professional/corporate. D-ID for one-off photo animations.

**Scripts:** `scripts/services/video/heygen_presenter.py`, `scripts/services/video/synthesia_presenter.py`, `scripts/services/video/did_presenter.py`
**API keys:** `HEYGEN_API_KEY` / `SYNTHESIA_API_KEY` / `DID_API_KEY`

### voice_synthesis

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **ElevenLabs** | Free tier + $5+/mo | Yes | No | MCP | Official (`elevenlabs/elevenlabs-mcp` GitHub) | Docker: `docker pull mcp/elevenlabs` |

**Recommendation:** ElevenLabs is the clear winner -- official MCP, best quality, good free tier. No alternatives needed.

**API keys:** `ELEVENLABS_API_KEY`

### email_sending

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **SendGrid** | Free (100/day) | Yes | No | Both | Community (`Garoth/sendgrid-mcp`, `@cong/sendgrid-mcp` JSR) | `npm install sendgrid-mcp` |
| 2 | **Mailgun** | Free (100/day, 30-day trial) | Yes (trial) | No | MCP | Official (`mailgun/mailgun-mcp-server` GitHub) | `git clone` + install |
| 3 | **Brevo** (Sendinblue) | Free (300/day) | Yes | No | Script | No | HTTP API (no install) |
| 4 | **Mailchimp** | Free tier | Yes | No | Script | No | HTTP API (no install) |
| 5 | **ConvertKit** | $29+/mo | No | No | Script | No | HTTP API (no install) |

**Recommendation:** SendGrid (highest free tier for transactional) or Mailgun (official MCP, cleaner API). Brevo for marketing campaigns if you want a separate system. Mailchimp/ConvertKit only if user already has an account.

**Scripts:** `scripts/services/email/sendgrid.py`, `scripts/services/email/mailgun.py`, `scripts/services/email/brevo.py`, `scripts/services/email/mailchimp.py`, `scripts/services/email/convertkit.py`
**API keys:** `SENDGRID_API_KEY` / `MAILGUN_API_KEY` + `MAILGUN_DOMAIN` / `BREVO_API_KEY` / `MAILCHIMP_API_KEY` / `CONVERTKIT_API_SECRET`

### social_publishing

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Buffer** | Free + $6+/channel/mo | Yes (limited) | No | Script | No (Zapier bridge only) | HTTP API (no install) |
| 2 | **X API v2** (posting) | Free (Essential) | Yes | No | Both | Community | HTTP API (no install) |
| 3 | **LinkedIn API** | Free (limited) | Yes | No | Both | Community (`linkedin-mcp-server` npm) | `npm install linkedin-mcp-server` |
| 4 | **Meta Graph API** | Free | Yes | No | Both | Community | HTTP API (no install) |
| 5 | **Pinterest API** | Free | Yes | No | Script | No | HTTP API (no install) |
| 6 | **TikTok API** | Limited | Limited | No | Script | No | HTTP API (no install) |
| 7 | **VK API** | Free | Yes | No | Script | No | HTTP API (no install) |

**Note:** Social posting is NEVER automated -- agents draft content, human approves in dashboard, THEN publishing triggers. This is a design principle in v3.

### cms_publishing

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **WordPress REST API** | Free | Yes | Yes (self-hosted WP) | MCP | Official (`WordPress/mcp-adapter` WP plugin) | Install WP plugin |
| 2 | **Ghost API** | Free (self-hosted) / $9+/mo | Yes (self-hosted) | Yes | Both | Community (`@fanyangmeng/ghost-mcp` npm) | `npm install @fanyangmeng/ghost-mcp` |
| 3 | **Webflow CMS API** | Paid plan required | No | No | MCP | Official (`webflow/mcp-server` GitHub) | `git clone` + install |
| 4 | **Custom REST API** | Varies | Varies | Varies | Script | No | Configurable URL |
| 5 | **Static (markdown)** | Free | Yes | Yes | Script (just file write) | No | No install needed |

**Recommendation:** Depends on target CMS. WordPress MCP is official and excellent. Webflow MCP is official. Ghost community MCP is decent. For MVP, "Static" (just write markdown files) is fine -- publish manually until CMS integration is built.

**Scripts:** `scripts/services/publishing/wp_publish.py`, `scripts/services/publishing/ghost_publish.py`, `scripts/services/publishing/webflow_publish.py`, `scripts/services/publishing/custom_cms.py`, `scripts/services/publishing/static_publish.py`
**API keys:** `WORDPRESS_URL` + `WORDPRESS_APP_PASSWORD` / `GHOST_API_URL` + `GHOST_ADMIN_API_KEY` / `WEBFLOW_API_TOKEN`

### content_quality

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **LanguageTool** | Free tier (open source) | Yes | Yes | Script | No (adjacent grammar MCP exists) | `docker pull erikvl87/languagetool` |
| 2 | **Copyscape** | $0.03/check | No | No | Script | No | HTTP API (no install) |
| 3 | **Copyleaks** | $9.16+/mo | No | No | Script | No | HTTP API (no install) |

**Note:** Copyscape and LanguageTool have NO MCP servers. Both have simple REST APIs -- Python scripts are straightforward. LanguageTool can be self-hosted (Docker) for unlimited free usage.

**Scripts:** `scripts/services/quality/languagetool.py`, `scripts/services/quality/copyscape.py`, `scripts/services/quality/copyleaks.py`
**API keys:** `COPYSCAPE_USER` + `COPYSCAPE_API_KEY` / `COPYLEAKS_API_KEY` / LanguageTool: none if self-hosted

### web_search

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Brave Search** | Free (2K/mo) / $3/1K | Yes | No | MCP | Official (`@anthropic-ai/mcp-server-brave-search` npm) | `npx -y @anthropic-ai/mcp-server-brave-search` |
| 2 | **Google Custom Search** | Free (100/day) | Yes | No | Script | No | HTTP API (no install) |
| 3 | **Perplexity** | $0.20/1K queries | No | No | MCP | Official (`perplexityai/modelcontextprotocol` GitHub) | `git clone` + install |

**Recommendation:** Brave Search MCP as primary (already in Claude Code's default MCP set). Perplexity MCP for deep research (returns synthesized answers, not just links). Google CSE only for specific site:search patterns.

**API keys:** `BRAVE_API_KEY` / `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_CX` / `PERPLEXITY_API_KEY`

### analytics

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Google Search Console** | Free | Yes | No | Both | Community (`ahonn/mcp-server-gsc` GitHub) | `git clone` + install |
| 2 | **Google Analytics 4** | Free | Yes | No | MCP | Official (Google) (`developers.google.com/analytics/devguides/MCP`) | Google Cloud SDK |
| 3 | **Plausible** | Self-hosted (free) / $9+/mo | Yes (self-hosted) | Yes | Script | No | `docker pull plausible/analytics` |
| 4 | **Umami** | Self-hosted (free) | Yes (self-hosted) | Yes | Script | No | `docker pull ghcr.io/umami-software/umami` |

**Recommendation:** GSC + GA4 are the standard pair. Both have MCP servers (GA4 is official from Google). Plausible/Umami are alternatives if you want privacy-friendly analytics -- pick one.

**Scripts:** `scripts/services/analytics/gsc_analytics.py`, `scripts/services/analytics/ga4_analytics.py`, `scripts/services/analytics/plausible.py`, `scripts/services/analytics/umami.py`
**API keys:** GSC uses OAuth2 service account JSON / `GA4_PROPERTY_ID` / Plausible: self-hosted URL / Umami: self-hosted URL

### advertising (FUTURE)

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Google Ads** | Pay-per-click | No | No | MCP | Official (`googleads/google-ads-mcp` GitHub, Python) | `pip install google-ads-mcp` |
| 2 | **Meta Ads** (FB + IG) | Pay-per-click | No | No | Both | Community (`pipeboard-co/meta-ads-mcp`, `gomarble-ai/facebook-ads-mcp-server`) | `git clone` + install |

**Recommendation:** Both are FUTURE features -- not needed for MVP content generation. When ready, Google Ads has an official MCP. Meta Ads has community MCPs that work.

### notifications

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Telegram Bot API** | Free | Yes | No | Both | Community (`chigwell/telegram-mcp`, `sparfenyuk/mcp-telegram`) | `pip install telegram-mcp` or git clone |
| 2 | **Discord Webhook** | Free | Yes | No | Both | Community (`mcp-discord` npm, `barryyip0625/mcp-discord`) | `npm install mcp-discord` |
| 3 | **Slack Webhook** | Free | Yes | No | MCP | Official (`@modelcontextprotocol/server-slack` npm) | `npx -y @modelcontextprotocol/server-slack` |

**Recommendation:** Telegram as primary (free, simple, mobile). Slack MCP is official and excellent if the team uses Slack. Discord for community-facing alerts. Pick one for MVP.

**Scripts:** `scripts/services/notifications/telegram_notify.py`, `scripts/services/notifications/discord_notify.py`, `scripts/services/notifications/slack_notify.py`
**API keys:** `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` / `DISCORD_WEBHOOK_URL` / `SLACK_BOT_TOKEN`

### document_generation (LOCAL)

| Priority | Service | Cost | Free Tier? | Self-Hosted? | Integration | MCP? | Install Method |
|----------|---------|------|-----------|-------------|-------------|------|----------------|
| 1 | **Pandoc** | Free (installed locally) | Yes | Yes (local tool) | Bash | No | `apt install pandoc` or `brew install pandoc` |
| 2 | **Calibre** | Free (installed locally) | Yes | Yes (local tool) | Bash | No | `apt install calibre` or `brew install calibre` |
| 3 | **Puppeteer/Playwright** | Free (installed locally) | Yes | Yes (local tool) | Script | No | `npm install puppeteer` or `pip install playwright` |

**Recommendation:** All three are local tools. No API keys needed. Pandoc is the workhorse for format conversion. Calibre for ebook formats. Puppeteer for HTML-to-PDF and screenshots.

---

## 5. Self-Hosted Services

Services that run locally as Docker containers, eliminating recurring costs and API rate limits.

| Service | Docker Image | Default Port | RAM | Disk | Replaces | Capability |
|---------|-------------|-------------|-----|------|----------|-----------|
| **Crawl4AI** | `unclecode/crawl4ai` | 11235 | ~512MB | ~1GB | Firecrawl (for batch crawling) | web_scraping |
| **LanguageTool** | `erikvl87/languagetool` | 8081 | 512MB-1GB | ~2GB (n-grams) | LanguageTool Cloud API | content_quality |
| **Plausible** | `plausible/analytics` | 8000 | ~256MB | ~500MB | Google Analytics 4 | analytics |
| **Umami** | `ghcr.io/umami-software/umami` | 3001 | ~128MB | ~200MB | Google Analytics 4 | analytics |

### When to Use Self-Hosted vs Cloud

| Scenario | Use Self-Hosted | Use Cloud |
|----------|----------------|-----------|
| Batch crawling 1000+ pages | Crawl4AI (no rate limits) | -- |
| Interactive single-page scrape | -- | Firecrawl MCP (LLM-ready markdown) |
| Grammar/style checking | LanguageTool Docker (unlimited) | -- |
| Privacy-first analytics | Plausible or Umami | -- |
| Quick setup, no Docker | -- | Cloud APIs |

The self-hosted containers are managed by `docker-compose.services.yml` (see Section 6 for the full spec).

---

## 6. Setup Script Specification

The setup script (`scripts/setup.sh`) is the single entry point for configuring all external services. It installs local tools, pulls Docker images, writes MCP config, and prompts for API keys.

### Prerequisites

The script checks for these before proceeding:

```bash
# Required
docker --version        # Docker 24+
docker compose version  # Docker Compose v2+
node --version          # Node.js 22+
python3 --version       # Python 3.12+
npx convex --version    # Convex CLI

# Optional (installed by script if missing)
pandoc --version
calibre --version
```

### Script Flow

```
scripts/setup.sh
|
|-- 1. CHECK PREREQUISITES
|   |-- Docker, Node.js, Python, Convex CLI
|   |-- Exit with clear error message if missing
|
|-- 2. INSTALL MCP SERVERS
|   |-- Write/update .mcp.json with all MCP server entries
|   |-- Each entry uses ${ENV_VAR} placeholders
|   |-- MCP servers are "ready but inactive" until keys provided
|
|-- 3. PULL SELF-HOSTED DOCKER IMAGES
|   |-- docker compose -f docker-compose.services.yml pull
|   |-- Images: crawl4ai, languagetool
|   |-- Optional: plausible, umami (prompted)
|
|-- 4. START SELF-HOSTED CONTAINERS
|   |-- docker compose -f docker-compose.services.yml up -d
|   |-- Wait for health checks to pass
|   |-- Print status of each container
|
|-- 5. VALIDATE PYTHON DEPENDENCIES
|   |-- pip install -r requirements.services.txt
|   |-- Includes: praw, tweepy, google-ads, requests, etc.
|
|-- 6. INSTALL LOCAL TOOLS
|   |-- pandoc (if not present): apt install pandoc
|   |-- calibre (if not present): apt install calibre
|   |-- puppeteer: npm install puppeteer (project-local)
|
|-- 7. INTERACTIVE API KEY PROMPTS
|   |-- Groups by capability
|   |-- For each capability:
|   |     "=== SEO & Keywords ==="
|   |     "Enter DataForSEO login (or press Enter to skip): "
|   |     "Enter DataForSEO password (or press Enter to skip): "
|   |     "Enter Ahrefs API key (or press Enter to skip): "
|   |     ...
|   |-- Skipped keys are left empty in .env
|
|-- 8. WRITE .env
|   |-- Merge new keys with existing .env (preserve existing values)
|   |-- Add self-hosted service URLs (CRAWL4AI_URL, LANGUAGETOOL_URL, etc.)
|   |-- chmod 600 .env
|
|-- 9. SEED CONVEX TABLES
|   |-- npx convex run services:seedCategories --url http://localhost:3210
|   |-- npx convex run services:seedServices --url http://localhost:3210
|   |-- Sets isActive=true for services with API keys
|   |-- Sets isActive=true for all self-hosted services
|   |-- Sets isActive=false for services without keys
|
|-- 10. HEALTH CHECKS
|    |-- Test each active service:
|    |     curl -s http://localhost:11235/health  (Crawl4AI)
|    |     curl -s http://localhost:8081/v2/check (LanguageTool)
|    |     python scripts/services/seo/query_dataforseo.py --test
|    |     ... (each script supports --test flag)
|    |-- Print pass/fail per service
|
|-- 11. PRINT SUMMARY
|    |-- "ENABLED AGENTS (all required capabilities met):"
|    |--   vibe-content-writer ............ OK (no external deps)
|    |--   vibe-keyword-researcher ........ OK (seo_keywords: DataForSEO)
|    |--   ...
|    |-- "DISABLED AGENTS (missing capabilities):"
|    |--   vibe-twitter-scout ............ MISSING: social_scraping_x
|    |--   vibe-image-generator .......... MISSING: image_generation
|    |--   ...
|    |-- "DEGRADED AGENTS (optional capabilities missing):"
|    |--   vibe-content-reviewer ......... WARNING: content_quality (no provider)
|    |--   ...
```

### docker-compose.services.yml

```yaml
version: '3.8'

services:
  crawl4ai:
    image: unclecode/crawl4ai
    ports:
      - "11235:11235"
    environment:
      - MAX_CONCURRENT_TASKS=5
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11235/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  languagetool:
    image: erikvl87/languagetool
    ports:
      - "8081:8010"
    environment:
      - Java_Xms=512m
      - Java_Xmx=1g
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8010/v2/languages"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: uncomment if you want self-hosted analytics
  # plausible:
  #   image: plausible/analytics
  #   ports:
  #     - "8000:8000"
  #   environment:
  #     - BASE_URL=http://localhost:8000
  #     - SECRET_KEY_BASE=${PLAUSIBLE_SECRET_KEY}
  #   depends_on:
  #     - plausible-db
  #   restart: unless-stopped
  #
  # plausible-db:
  #   image: postgres:16-alpine
  #   volumes:
  #     - plausible-data:/var/lib/postgresql/data
  #   environment:
  #     - POSTGRES_PASSWORD=${PLAUSIBLE_DB_PASSWORD}
  #     - POSTGRES_DB=plausible
  #   restart: unless-stopped
  #
  # umami:
  #   image: ghcr.io/umami-software/umami:postgresql-latest
  #   ports:
  #     - "3001:3000"
  #   environment:
  #     - DATABASE_URL=postgresql://umami:${UMAMI_DB_PASSWORD}@umami-db:5432/umami
  #   depends_on:
  #     - umami-db
  #   restart: unless-stopped
  #
  # umami-db:
  #   image: postgres:16-alpine
  #   volumes:
  #     - umami-data:/var/lib/postgresql/data
  #   environment:
  #     - POSTGRES_PASSWORD=${UMAMI_DB_PASSWORD}
  #     - POSTGRES_DB=umami
  #   restart: unless-stopped

# volumes:
#   plausible-data:
#   umami-data:
```

---

## 7. MCP Server Registry

Complete `.mcp.json` with ALL MCP servers. Each entry uses `${ENV_VAR}` placeholders so they are "ready but inactive" until the corresponding API key is set in `.env`.

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-fetch"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "/home/deploy/vibe-marketing"]
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "perplexityai/modelcontextprotocol"],
      "env": { "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}" }
    },
    "dataforseo": {
      "command": "python",
      "args": ["-m", "dataforseo_mcp_server"],
      "env": {
        "DATAFORSEO_LOGIN": "${DATAFORSEO_LOGIN}",
        "DATAFORSEO_PASSWORD": "${DATAFORSEO_PASSWORD}"
      }
    },
    "ahrefs": {
      "command": "npx",
      "args": ["-y", "ahrefs-mcp-server"],
      "env": { "AHREFS_API_KEY": "${AHREFS_API_KEY}" }
    },
    "semrush": {
      "url": "https://api.semrush.com/mcp/v1",
      "env": { "SEMRUSH_API_KEY": "${SEMRUSH_API_KEY}" }
    },
    "google-search-console": {
      "command": "npx",
      "args": ["-y", "mcp-server-gsc"],
      "env": { "GSC_SERVICE_ACCOUNT_JSON": "${GSC_SERVICE_ACCOUNT_JSON}" }
    },
    "reddit": {
      "command": "npx",
      "args": ["-y", "mcp-server-reddit"],
      "env": {
        "REDDIT_CLIENT_ID": "${REDDIT_CLIENT_ID}",
        "REDDIT_CLIENT_SECRET": "${REDDIT_CLIENT_SECRET}"
      }
    },
    "youtube": {
      "command": "npx",
      "args": ["-y", "youtube-mcp-server"],
      "env": { "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}" }
    },
    "linkedin": {
      "command": "npx",
      "args": ["-y", "linkedin-mcp-server"],
      "env": { "LINKEDIN_ACCESS_TOKEN": "${LINKEDIN_ACCESS_TOKEN}" }
    },
    "fal-ai": {
      "command": "npx",
      "args": ["-y", "mcp-fal-ai-image"],
      "env": { "FAL_KEY": "${FAL_KEY}" }
    },
    "dalle": {
      "command": "npx",
      "args": ["-y", "imagegen-mcp"],
      "env": { "OPENAI_API_KEY": "${OPENAI_API_KEY}" }
    },
    "replicate": {
      "command": "npx",
      "args": ["-y", "@gongrzhe/image-gen-server"],
      "env": { "REPLICATE_API_TOKEN": "${REPLICATE_API_TOKEN}" }
    },
    "runway": {
      "command": "node",
      "args": ["node_modules/mcp-video-gen/dist/index.js"],
      "env": { "RUNWAY_API_KEY": "${RUNWAY_API_KEY}" }
    },
    "veo": {
      "command": "node",
      "args": ["node_modules/mcp-veo2/dist/index.js"],
      "env": { "GOOGLE_CLOUD_PROJECT": "${GOOGLE_CLOUD_PROJECT}" }
    },
    "elevenlabs": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "ELEVENLABS_API_KEY", "mcp/elevenlabs"],
      "env": { "ELEVENLABS_API_KEY": "${ELEVENLABS_API_KEY}" }
    },
    "sendgrid": {
      "command": "npx",
      "args": ["-y", "sendgrid-mcp"],
      "env": { "SENDGRID_API_KEY": "${SENDGRID_API_KEY}" }
    },
    "mailgun": {
      "command": "node",
      "args": ["node_modules/mailgun-mcp-server/dist/index.js"],
      "env": {
        "MAILGUN_API_KEY": "${MAILGUN_API_KEY}",
        "MAILGUN_DOMAIN": "${MAILGUN_DOMAIN}"
      }
    },
    "wordpress": {
      "command": "npx",
      "args": ["-y", "wordpress-mcp-adapter"],
      "env": {
        "WORDPRESS_URL": "${WORDPRESS_URL}",
        "WORDPRESS_APP_PASSWORD": "${WORDPRESS_APP_PASSWORD}"
      }
    },
    "ghost": {
      "command": "npx",
      "args": ["-y", "@fanyangmeng/ghost-mcp"],
      "env": {
        "GHOST_API_URL": "${GHOST_API_URL}",
        "GHOST_ADMIN_API_KEY": "${GHOST_ADMIN_API_KEY}"
      }
    },
    "webflow": {
      "command": "npx",
      "args": ["-y", "webflow-mcp-server"],
      "env": { "WEBFLOW_API_TOKEN": "${WEBFLOW_API_TOKEN}" }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": { "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}" }
    },
    "telegram": {
      "command": "python",
      "args": ["-m", "telegram_mcp"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "${TELEGRAM_CHAT_ID}"
      }
    },
    "discord": {
      "command": "npx",
      "args": ["-y", "mcp-discord"],
      "env": { "DISCORD_WEBHOOK_URL": "${DISCORD_WEBHOOK_URL}" }
    },
    "google-analytics": {
      "command": "npx",
      "args": ["-y", "google-analytics-mcp"],
      "env": {
        "GA4_PROPERTY_ID": "${GA4_PROPERTY_ID}",
        "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}"
      }
    },
    "google-ads": {
      "command": "python",
      "args": ["-m", "google_ads_mcp"],
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "${GOOGLE_ADS_DEVELOPER_TOKEN}",
        "GOOGLE_ADS_CUSTOMER_ID": "${GOOGLE_ADS_CUSTOMER_ID}"
      }
    },
    "meta-ads": {
      "command": "node",
      "args": ["node_modules/meta-ads-mcp/dist/index.js"],
      "env": { "META_ADS_ACCESS_TOKEN": "${META_ADS_ACCESS_TOKEN}" }
    },
    "stripe": {
      "url": "https://mcp.stripe.com",
      "env": { "STRIPE_SECRET_KEY": "${STRIPE_SECRET_KEY}" }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}" }
    },
    "cloudflare": {
      "command": "npx",
      "args": ["-y", "@cloudflare/mcp-server-cloudflare"],
      "env": { "CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}" }
    }
  }
}
```

### MCP Availability Summary

| Status | Count | Services |
|--------|-------|----------|
| **Official MCP** | 18 | Firecrawl, Brave Search, Perplexity, Ahrefs, SEMrush, GA4, Mailgun, Slack, WordPress, Webflow, ElevenLabs, Google Ads, Stripe, Cloudflare, Vercel, GitHub, Recraft, Replicate |
| **Community MCP** | 17 | DataForSEO, GSC, Reddit, X/Twitter, LinkedIn, YouTube, SendGrid, Telegram, Discord, Ghost, GPT Image (OpenAI), fal.ai, Runway, Meta Ads, Google Imagen, Google Veo, Ideogram |
| **No MCP** | 10 | Google Keyword Planner, AnswerThePublic, Bing Webmaster, Crawl4AI, ScraperAPI, Apify, PhantomBuster, ProxyCurl, Copyscape, LanguageTool, Buffer, Bannerbear/Placid |
| **Local tools** | 3 | Pandoc, Calibre, Puppeteer |

---

## 8. Agent Gating Rules (Pipeline Builder)

How the dashboard determines if an agent is draggable in the pipeline builder UI.

### State Definitions

```
ENABLED (draggable):
  ALL required capabilities have >= 1 active provider
  Agent card: full color, draggable into pipeline

DISABLED (dimmed, undraggable):
  ANY required capability has 0 active providers
  Agent card: grayed out, undraggable
  Tooltip: "Requires: [missing capabilities]. Configure in Settings -> Services."

DEGRADED (draggable with warning badge):
  All required capabilities met
  BUT some optional capabilities have 0 providers
  Agent card: full color + orange warning badge
  Badge tooltip: "Limited: [missing optional capabilities]"
```

### Gating Logic (Pseudocode)

```python
def get_agent_state(agent):
    required_caps = agent.get_required_capabilities()
    optional_caps = agent.get_optional_capabilities()

    missing_required = []
    for cap in required_caps:
        providers = get_active_providers(cap)
        if len(providers) == 0:
            missing_required.append(cap)

    if missing_required:
        return AgentState.DISABLED, missing_required

    missing_optional = []
    for cap in optional_caps:
        providers = get_active_providers(cap)
        if len(providers) == 0:
            missing_optional.append(cap)

    if missing_optional:
        return AgentState.DEGRADED, missing_optional

    return AgentState.ENABLED, []
```

### Specific Agent Gating Examples

| Agent | State Rule | Example |
|-------|-----------|---------|
| vibe-content-writer | **ALWAYS ENABLED** | No required external services. Skills only. Optional: web_search, cms_publishing. |
| vibe-landing-page-writer | **ALWAYS ENABLED** | No required external services. Skills only. Optional: web_search. |
| vibe-humanizer | **ALWAYS ENABLED** | No external services. Pure skills. |
| vibe-script-writer | **ALWAYS ENABLED** | No external services. Pure skills. |
| vibe-content-repurposer | **ALWAYS ENABLED** | No external services. Pure skills. |
| vibe-ad-writer | **ALWAYS ENABLED** | No external services. Pure skills. |
| vibe-press-writer | **ALWAYS ENABLED** | No external services. Pure skills. |
| vibe-image-director | **ALWAYS ENABLED** | Creates image prompts only, does not call APIs. |
| vibe-audience-parser | **ALWAYS ENABLED** | Parses uploaded documents, no external services. |
| vibe-keyword-researcher | DISABLED if no `seo_keywords` provider active | "Requires: seo_keywords. Configure DataForSEO, Ahrefs, or SEMrush in Settings -> Services." |
| vibe-image-generator | DISABLED if no `image_generation` provider active | "Requires: image_generation. Configure FLUX.2, GPT Image, or other in Settings -> Services." |
| vibe-video-generator | DISABLED if no `video_generation` provider active | "Requires: video_generation. Configure Runway, Pika, or other in Settings -> Services." |
| vibe-twitter-scout | DISABLED if no `social_scraping_x` provider active | "Requires: social_scraping_x. Configure X API v2 in Settings -> Services." |
| vibe-reddit-scout | DISABLED if no `social_scraping_reddit` provider active | "Requires: social_scraping_reddit. Configure Reddit API in Settings -> Services." |
| vibe-linkedin-scout | DISABLED if no `social_scraping_linkedin` provider active | "Requires: social_scraping_linkedin. Configure PhantomBuster or ProxyCurl in Settings -> Services." |
| vibe-competitor-analyst | DISABLED if no `web_scraping` provider active | "Requires: web_scraping. Configure Firecrawl or Crawl4AI in Settings -> Services." |
| vibe-serp-analyzer | DISABLED if no `seo_keywords` OR no `serp_tracking` provider active | "Requires: seo_keywords, serp_tracking." |
| vibe-plagiarism-checker | DISABLED if no `content_quality` provider active | "Requires: content_quality. Configure Copyscape or LanguageTool in Settings -> Services." |
| vibe-fact-checker | DISABLED if no `web_search` provider active | "Requires: web_search. Configure Brave Search in Settings -> Services." |
| vibe-content-reviewer | DEGRADED if no `content_quality` provider | Can still review content using skills-based analysis, but cannot run grammar/plagiarism checks. |
| vibe-brand-monitor | DEGRADED if no `social_scraping_meta` provider | Can monitor web + core scraping, but Facebook/Instagram brand mentions limited. |
| vibe-trend-detector | DEGRADED if no `social_scraping_tiktok` provider | Can detect trends via YouTube + web, but TikTok trends unavailable. |
| vibe-email-writer | DEGRADED if no `email_sending` provider | Can draft emails, but cannot send test/preview emails. |
| vibe-social-writer | DEGRADED if no `social_publishing` provider | Can draft social posts, but cannot publish directly. |

### Pipeline Validation

When a user tries to **start** a campaign pipeline, the dashboard validates:

```
For each agent step in the pipeline:
  if agent.state == DISABLED:
    BLOCK pipeline start
    Show: "Cannot start pipeline. Agent [name] requires: [missing capabilities]."
  if agent.state == DEGRADED:
    WARN but allow
    Show: "Warning: [name] running in degraded mode. Missing: [capabilities]."
```

---

## 9. Priority & Fallback System

How `resolve_service.py` picks the right provider and handles failures.

### Resolution Algorithm

```
1. Agent calls: python scripts/resolve_service.py <capability> [use_case]
2. Query Convex for all ACTIVE providers in that capability category
3. Sort by user-configured priority (1 = highest)
4. If use_case provided, filter to providers whose useCases array includes it
5. Return top provider (name, script path, config, MCP server name)
6. Agent executes the provider
7. If provider fails:
   a. Agent calls: python scripts/resolve_service.py <capability> [use_case] --skip <failed_provider>
   b. resolve_service.py returns next priority provider
   c. Repeat until success or all providers exhausted
8. If all providers fail:
   a. Agent logs error to Convex (activities:log type="error")
   b. Agent sets task to "blocked" with notes
   c. Agent notifies vibe-orchestrator
```

### resolve_service.py (with fallback support)

```python
#!/usr/bin/env python3
# scripts/resolve_service.py
# Usage:
#   python resolve_service.py <capability> [use_case]
#   python resolve_service.py <capability> [use_case] --skip provider1,provider2
#
# Returns JSON: {"name": "...", "script": "...", "config": {...}, "mcp": "..."}
# Exit code 1 if no active providers found.

import json
import subprocess
import sys

def get_active_services(capability, use_case=None, skip=None):
    """Query Convex for active services in a capability, sorted by priority."""
    result = subprocess.run(
        ["npx", "convex", "run", "services:getActiveByCategory",
         json.dumps({"category": capability, "useCase": use_case}),
         "--url", "http://localhost:3210"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        services = json.loads(result.stdout)
    else:
        services = []

    # Filter out skipped providers
    if skip:
        skip_set = set(skip.split(","))
        services = [s for s in services if s["name"] not in skip_set]

    return services

if __name__ == "__main__":
    capability = sys.argv[1]
    use_case = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None

    skip = None
    for i, arg in enumerate(sys.argv):
        if arg == "--skip" and i + 1 < len(sys.argv):
            skip = sys.argv[i + 1]

    services = get_active_services(capability, use_case, skip)

    if not services:
        print(json.dumps({
            "error": f"No active services for capability '{capability}'"
                     + (f" (use_case: {use_case})" if use_case else "")
                     + (f" (skipped: {skip})" if skip else ""),
            "capability": capability,
        }))
        sys.exit(1)

    best = services[0]
    print(json.dumps({
        "name": best["name"],
        "script": best["scriptPath"],
        "config": json.loads(best.get("configJson", "{}") or "{}"),
        "mcp": best.get("mcpServer"),
        "fallback_count": len(services) - 1,
    }))
```

### How Agents Use Fallback

Example in a SKILL.md instruction:

```markdown
## Service Resolution with Fallback

When you need an external service:
1. Run: `python scripts/resolve_service.py <capability> [use_case]`
2. Execute the returned script or MCP tool
3. If the script/tool fails (non-zero exit, timeout, API error):
   a. Run: `python scripts/resolve_service.py <capability> [use_case] --skip <failed_name>`
   b. Try the next provider
   c. Repeat up to 3 times
4. If all providers fail, set task to "blocked" and notify orchestrator
```

---

## 10. Free Minimum Stack

The absolute cheapest way to enable each agent, using self-hosted services and free API tiers.

| Agent | Free Services Needed | Setup Command(s) | Monthly Cost |
|-------|---------------------|-------------------|-------------|
| vibe-orchestrator | Telegram Bot | Create bot via @BotFather | $0 |
| vibe-content-writer | None (skills only) | -- | $0 |
| vibe-landing-page-writer | None (skills only) | -- | $0 |
| vibe-email-writer | None for drafting; SendGrid free for sending | Sign up at sendgrid.com | $0 |
| vibe-social-writer | None for drafting; direct APIs for posting | Platform API keys (free) | $0 |
| vibe-script-writer | None (skills only) | -- | $0 |
| vibe-ebook-writer | Pandoc + Calibre (local) | `apt install pandoc calibre` | $0 |
| vibe-content-repurposer | None (skills only) | -- | $0 |
| vibe-ad-writer | None (skills only) | -- | $0 |
| vibe-press-writer | None (skills only) | -- | $0 |
| vibe-humanizer | None (skills only) | -- | $0 |
| vibe-image-director | None (prompts only) | -- | $0 |
| vibe-audience-parser | None (parses uploads) | -- | $0 |
| vibe-content-reviewer | LanguageTool self-hosted | `docker pull erikvl87/languagetool` | $0 |
| vibe-fact-checker | Brave Search (free 2K/mo) | Sign up at brave.com/search/api | $0 |
| vibe-keyword-researcher | Google Keyword Planner + Brave Search | Google Ads account (free) + Brave | $0 |
| vibe-keyword-deep-researcher | Google Keyword Planner + GSC + Brave | Google Ads + GSC OAuth + Brave | $0 |
| vibe-serp-analyzer | Google Keyword Planner + GSC + Brave | Same as above | $0 |
| vibe-seo-auditor | GKP + GSC + Crawl4AI + Brave | Same + `docker pull unclecode/crawl4ai` | $0 |
| vibe-competitor-analyst | Brave Search + Crawl4AI | Brave + Crawl4AI Docker | $0 |
| vibe-brand-monitor | Brave Search + Crawl4AI | Brave + Crawl4AI Docker | $0 |
| vibe-reddit-scout | Reddit API (free) | Create Reddit app at reddit.com/prefs/apps | $0 |
| vibe-twitter-scout | X API v2 Essential (free) | Apply at developer.x.com | $0 |
| vibe-trend-detector | YouTube Data API + Brave Search | Google Cloud project (free tier) + Brave | $0 |
| vibe-review-harvester | Brave Search + Crawl4AI | Brave + Crawl4AI Docker | $0 |
| vibe-audience-researcher | Brave Search (free) | Brave | $0 |
| vibe-audience-enricher | Brave Search (free) | Brave | $0 |
| vibe-linkedin-scout | PhantomBuster or ProxyCurl | No free option | **$69/mo** (PhantomBuster) |
| vibe-plagiarism-checker | Copyscape | No free option | **~$3/mo** (100 checks) |
| vibe-image-generator | FLUX.2 [dev] Turbo via fal.ai | Sign up at fal.ai | **~$2.40/mo** (300 images) |
| vibe-video-generator | Pika Labs free tier | Sign up at pika.art | $0 (limited) |

### Summary

- **23 of 31 agents** can run at $0/mo (free tiers + self-hosted)
- **3 agents** need minimal spend (~$4/mo total: plagiarism + images)
- **1 agent** requires meaningful spend ($69/mo: LinkedIn scout)
- **4 agents** are FUTURE (not counted)
- **Total minimum viable spend: ~$73/mo** (dominated by LinkedIn if needed, otherwise ~$4/mo)

This is in addition to the Claude Max subscription ($200/mo) which powers all agent execution.

---

## 11. Full Stack (All Services)

### Free Tier ($0/mo + Claude Max)

| Category | Service | What You Get |
|----------|---------|-------------|
| Web Search | Brave Search | 2,000 queries/mo |
| Web Scraping | Crawl4AI (self-hosted) | Unlimited batch crawling |
| Web Scraping | Firecrawl | 500 pages/mo |
| SEO | Google Keyword Planner | Keyword volumes (free via Ads API) |
| SERP | Google Search Console | Own site data (free) |
| Social | Reddit API | 100 req/min (free) |
| Social | X API v2 Essential | Read-only, limited (free) |
| Social | YouTube Data API v3 | 10K units/day (free) |
| Social | Meta Graph API | Own page data (free) |
| Social | VK API | Generous limits (free) |
| Email | SendGrid | 100 emails/day |
| Email | Brevo | 300 emails/day |
| Quality | LanguageTool (self-hosted) | Unlimited grammar checks |
| Analytics | GSC + GA4 | Standard web analytics |
| Notifications | Telegram Bot | Unlimited |
| Documents | Pandoc + Calibre + Puppeteer | All local |

### Growth Tier ($50-100/mo)

Everything in Free Tier, plus:

| Category | Service | Cost | What You Get |
|----------|---------|------|-------------|
| SEO | DataForSEO | $50 deposit (pay-as-go) | Full keyword + SERP + competitor data |
| Web Scraping | Firecrawl paid | $19/mo | 5,000+ pages, LLM-ready markdown |
| Images | FLUX.2 [pro] (fal.ai) | ~$3-9/mo | High-quality hero images |
| Images | Ideogram 3.0 | $8/mo | Text-in-image graphics |
| Quality | Copyscape | ~$3/mo | Plagiarism detection |
| Voice | ElevenLabs | $5/mo | Basic voiceover |

**Total: ~$90-95/mo** (+ $200 Claude Max)

### Pro Tier ($200-500/mo)

Everything in Growth Tier, plus:

| Category | Service | Cost | What You Get |
|----------|---------|------|-------------|
| SEO | Ahrefs | $129/mo | Official MCP, backlink analysis, keyword gap |
| Video | Runway Gen-4 | $28/mo (Standard) | Hero/ad videos, 4K |
| Video | Google Veo 3 | ~$20/mo (usage) | Cinematic with audio |
| Social | PhantomBuster | $69/mo | LinkedIn scraping |
| Presenter | HeyGen | $18/mo | AI presenter videos |
| CMS | WordPress/Ghost | $0-9/mo | Auto-publishing |
| Ads | Google Ads MCP | Pay-per-click | Campaign management |

**Total: ~$365-475/mo** (+ $200 Claude Max)

---

## 12. API Key Management

### How Keys Flow

```
1. User runs scripts/setup.sh (or enters keys in Dashboard -> Settings -> Services)
2. Keys are written to .env file (chmod 600)
3. sync_registry.py reads .env, updates Convex services table (apiKeySet = true/false)
4. Agent calls resolve_service.py -> queries Convex -> returns provider with active key
5. Agent runs provider script, which reads key from .env (via os.environ or dotenv)
```

### Complete .env.template

```bash
# =============================================================================
# VIBE MARKETING PLATFORM — Environment Variables
# Generated by scripts/setup.sh
# =============================================================================

# --- Self-Hosted Services ---
CRAWL4AI_URL=http://localhost:11235
LANGUAGETOOL_URL=http://localhost:8081

# --- Web Search ---
BRAVE_API_KEY=
PERPLEXITY_API_KEY=
GOOGLE_CSE_API_KEY=
GOOGLE_CSE_CX=

# --- SEO & Keywords ---
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
AHREFS_API_KEY=
SEMRUSH_API_KEY=
GOOGLE_ADS_DEVELOPER_TOKEN=

# --- SERP & Rank Tracking ---
# GSC_SERVICE_ACCOUNT_JSON=path/to/service-account.json
BING_WEBMASTER_API_KEY=

# --- Web Scraping ---
FIRECRAWL_API_KEY=
APIFY_TOKEN=
SCRAPER_API_KEY=

# --- Social: X/Twitter ---
X_BEARER_TOKEN=

# --- Social: Reddit ---
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=vibe-marketing/1.0

# --- Social: LinkedIn ---
PHANTOMBUSTER_API_KEY=
PROXYCURL_API_KEY=
LINKEDIN_ACCESS_TOKEN=

# --- Social: Meta (FB/IG) ---
META_ACCESS_TOKEN=

# --- Social: TikTok ---
TIKTOK_API_KEY=

# --- Social: YouTube ---
YOUTUBE_API_KEY=

# --- Social: VK ---
VK_SERVICE_TOKEN=

# --- Image Generation ---
FAL_KEY=
OPENAI_API_KEY=
IDEOGRAM_API_KEY=
GOOGLE_CLOUD_PROJECT=
REPLICATE_API_TOKEN=
IMAGINEAPI_KEY=
LEONARDO_API_KEY=
RECRAFT_API_KEY=

# --- Templated Images ---
BANNERBEAR_API_KEY=
PLACID_API_KEY=

# --- Video Generation ---
RUNWAY_API_KEY=
KLING_API_KEY=
PIKA_API_KEY=
# SORA: uses OPENAI_API_KEY above

# --- AI Presenter ---
HEYGEN_API_KEY=
SYNTHESIA_API_KEY=
DID_API_KEY=

# --- Voice / Audio ---
ELEVENLABS_API_KEY=

# --- Email Sending ---
SENDGRID_API_KEY=
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
BREVO_API_KEY=
MAILCHIMP_API_KEY=
CONVERTKIT_API_SECRET=

# --- CMS Publishing ---
WORDPRESS_URL=
WORDPRESS_APP_PASSWORD=
GHOST_API_URL=
GHOST_ADMIN_API_KEY=
WEBFLOW_API_TOKEN=

# --- Content Quality ---
COPYSCAPE_USER=
COPYSCAPE_API_KEY=
COPYLEAKS_API_KEY=

# --- Analytics ---
GA4_PROPERTY_ID=
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# --- Advertising (FUTURE) ---
GOOGLE_ADS_CUSTOMER_ID=
META_ADS_ACCESS_TOKEN=

# --- Notifications ---
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=
SLACK_BOT_TOKEN=

# --- Infrastructure ---
GITHUB_PERSONAL_ACCESS_TOKEN=
CLOUDFLARE_API_TOKEN=
STRIPE_SECRET_KEY=

# --- Self-Hosted Analytics (optional) ---
PLAUSIBLE_SECRET_KEY=
PLAUSIBLE_DB_PASSWORD=
UMAMI_DB_PASSWORD=
```

### Dashboard Service Configuration UI

The Settings -> Services page in the dashboard shows:

- **Capability tabs** across the top (SEO, Scraping, Images, Video, Email, etc.)
- Per capability: **card grid** of all available providers
  - Each card shows: service name, description, cost info, status toggle (active/inactive)
  - Green checkmark if API key is set, red X if not
  - Drag-and-drop to reorder priority within the capability
  - "Configure" button opens a modal:
    - API key fields (stored in Convex, encrypted)
    - Extra config (JSON or form fields)
    - Use case tags (which sub-tasks this service handles)
    - "Test Connection" button that runs a quick API health check
- **Active summary** at the top: "4 of 9 image providers active, 2 of 5 SEO providers active"
- **Agent impact** panel: "Changing this will affect: vibe-keyword-researcher, vibe-seo-auditor"
- When you toggle a service or change priority, the registry daemon auto-regenerates `memory/long-term/SERVICE_REGISTRY.md`

---

## 13. Service Health Monitoring

How the platform monitors external service health and availability.

### Periodic Health Checks

A cron job runs every 15 minutes:

```bash
# In crontab
*/15 * * * * cd ~/vibe-marketing && python scripts/health_check_services.py >> logs/service-health.log 2>&1
```

The health check script:

1. Queries Convex for all ACTIVE services
2. For each active service, runs its `--test` endpoint:
   - Self-hosted: `curl` health endpoint (e.g., `http://localhost:11235/health`)
   - Cloud API: lightweight API call (e.g., DataForSEO account info endpoint)
   - MCP: tries to initialize the MCP server process
3. Records result in Convex `serviceHealth` table:
   - `status`: "healthy" / "degraded" / "down"
   - `latencyMs`: response time
   - `lastChecked`: timestamp
   - `errorMessage`: if down, what went wrong
4. If a service transitions from "healthy" to "down":
   - Sends notification via active notification provider
   - Dashboard shows red status indicator

### Dashboard Status Indicators

| Color | Meaning | Tooltip |
|-------|---------|---------|
| Green | Healthy | "DataForSEO: responding (120ms). Last checked: 2 min ago." |
| Yellow | Degraded | "Firecrawl: slow response (2400ms). May affect agent performance." |
| Red | Down | "X API v2: rate limited (429). Retry after: 15 min." |
| Gray | Inactive | "Ahrefs: not configured. No API key set." |

### Auto-Fallback

When the health check detects a service is down:

1. The service's status is set to "degraded" or "down" in Convex
2. `resolve_service.py` automatically skips "down" services
3. Next-priority provider is returned to agents
4. When the primary service recovers (next health check passes), it resumes as top priority
5. A notification is sent: "DataForSEO recovered. Resuming as primary SEO provider."

### Quota & Expiry Monitoring

For services with usage limits:

| Service | Quota Check | Alert Threshold |
|---------|-------------|-----------------|
| Brave Search | 2,000/mo free | Alert at 80% (1,600 queries) |
| Firecrawl | 500 pages/mo free | Alert at 80% (400 pages) |
| YouTube Data API | 10,000 units/day | Alert at 90% (9,000 units) |
| SendGrid | 100/day free | Alert at 90% (90 emails) |
| fal.ai | Pay-as-go | Alert when account balance < $5 |

Alerts are delivered via the configured notification provider (Telegram/Slack/Discord).

---

## How Services Connect to Skills and Agents

```
External Service --> Service Registry (Convex) --> resolve_service.py --> Skill script
                                                                            |
                                              Agent loads skill --> runs script --> gets data
```

**Example flow: keyword research**
```
1. vibe-keyword-researcher wakes up (cron)
2. Loads keyword-research-procedures/SKILL.md
3. SKILL.md says: "Run scripts/resolve_service.py seo_keywords"
4. resolve_service.py checks Convex --> DataForSEO is #1 priority, ACTIVE
5. Returns: scripts/services/seo/query_dataforseo.py
6. Agent runs the script with keyword parameters
7. Gets JSON response --> writes content brief
```

**Example flow: image generation**
```
1. vibe-image-generator gets task (pipeline dispatch)
2. Loads image-generation-procedures/SKILL.md
3. SKILL.md says: "Run scripts/resolve_service.py image_generation hero_images"
4. resolve_service.py --> FLUX.2 [pro] (fal.ai) is #1 for hero_images
5. Agent calls fal.ai MCP tool OR runs flux_generate.py
6. Gets image URL --> downloads to campaign assets folder
```

**Example flow: fallback in action**
```
1. vibe-competitor-analyst needs to scrape a competitor site
2. Calls: resolve_service.py web_scraping
3. Returns: Firecrawl (#1 priority)
4. Firecrawl returns 429 (rate limited)
5. Agent calls: resolve_service.py web_scraping --skip firecrawl
6. Returns: Crawl4AI (#2 priority, self-hosted)
7. Crawl4AI succeeds --> agent continues with scraped data
```
