# External Services Registry — Complete Provider Catalog
Generated: 2026-02-11

## Summary

The external-services-registry.md defines a **capability-first architecture** with 20 capability categories, 90+ provider options, and clear free/paid tiers. Agents depend on abstract capabilities (e.g., "seo_keywords"), not specific services. The platform resolves capabilities to concrete providers at runtime via Convex + `resolve_service.py`.

**Key Architecture Points:**
- 18 Official MCPs, 17 Community MCPs, 10 Script-only integrations
- 4 Self-hosted services (Crawl4AI, LanguageTool, Plausible, Umami)
- 23 of 31 agents can run at $0/mo (free tiers + self-hosted)
- Automatic fallback system when primary providers fail
- Dashboard UI for priority ordering and API key management

---

## 1. SEO & Keywords (`seo_keywords`)

**Used By:** vibe-keyword-researcher, vibe-seo-auditor, vibe-keyword-deep-researcher

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **DataForSEO** | $50 min deposit, ~$0.60/1K SERPs | No | No | Community: `dataforseo-mcp-server` (PyPI) | `pip install dataforseo-mcp-server` | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` |
| 2 | **Ahrefs** | $129+/mo | No | No | Official: `ahrefs/ahrefs-mcp-server` (remote) | Remote MCP | `AHREFS_API_KEY` |
| 3 | **SEMrush** | $139+/mo | No | No | Official: `developer.semrush.com/api/basics/semrush-mcp/` (remote) | Remote MCP | `SEMRUSH_API_KEY` |
| 4 | **Google Keyword Planner** | Free (via Google Ads API) | Yes | No | Script only | `pip install google-ads` | `GOOGLE_ADS_DEVELOPER_TOKEN` |
| 5 | **AnswerThePublic** | Free tier / $9+/mo | Yes (limited) | No | Script only | HTTP API | N/A |

**Scripts:** `scripts/services/seo/query_dataforseo.py`, `query_ahrefs.py`, `query_semrush.py`, `query_gkp.py`, `query_atp.py`

**Recommendation:** DataForSEO (cheapest, broadest coverage) or Google Keyword Planner (only truly free option). Add Ahrefs for backlink analysis if budget allows.

---

## 2. SERP & Rank Tracking (`serp_tracking`)

**Used By:** vibe-serp-analyzer, vibe-seo-auditor

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **DataForSEO SERP** | Included with DataForSEO | No | No | Same as DataForSEO | Same as DataForSEO | Same as DataForSEO |
| 2 | **Google Search Console** | Free | Yes | No | Community: `ahonn/mcp-server-gsc` | `npx -y @anthropic-ai/mcp-server-gsc` or git clone | OAuth2 service account JSON |
| 3 | **Bing Webmaster** | Free | Yes | No | Script only | HTTP API | `BING_WEBMASTER_API_KEY` |

**Scripts:** `scripts/services/seo/query_serp.py`, `query_gsc.py`, `query_bing.py`

**Recommendation:** GSC is essential (free, authoritative data). DataForSEO SERP for competitive analysis.

---

## 3. Web Scraping (`web_scraping`)

**Used By:** vibe-competitor-analyst, vibe-content-writer, vibe-seo-auditor, vibe-brand-monitor

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Firecrawl** | $19+/mo (500 pages free) | Yes (500 pages) | No | Official: `firecrawl-mcp` (npm) | `npx -y firecrawl-mcp` | `FIRECRAWL_API_KEY` |
| 2 | **Crawl4AI** | Free (self-hosted) | Yes | Yes | Script only | `docker pull unclecode/crawl4ai` | None (runs on :11235) |
| 3 | **Apify** | Pay-as-go ($5 free/mo) | Yes ($5 credit) | No | Community (low quality) | HTTP API | `APIFY_TOKEN` |
| 4 | **ScraperAPI** | $49+/mo | No | No | Script only | HTTP API | `SCRAPER_API_KEY` |

**Scripts:** `scripts/services/scraping/firecrawl_scrape.py`, `crawl4ai.py`, `apify_scrape.py`, `scraper_api.py`

**Recommendation:** Firecrawl MCP (primary, LLM-ready markdown). Crawl4AI for batch jobs + free self-hosted fallback. Apify for specialized scrapers.

**Self-Hosted Details:**
- **Crawl4AI:** Docker image `unclecode/crawl4ai`, port 11235, ~512MB RAM, replaces Firecrawl for batch crawling

---

## 4. Social Media Scraping

### X/Twitter (`social_scraping_x`)
**Used By:** vibe-twitter-scout

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **X API v2** | Free (Essential) / $100/mo (Basic) | Yes | No | Community (multiple repos) | HTTP API | `X_BEARER_TOKEN` |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script only | HTTP API | N/A |
| 3 | **Apify X Actor** | Pay-as-go | Yes ($5 credit) | No | Script only | HTTP API via Apify | `APIFY_TOKEN` |

**Script:** `scripts/services/social/x_api.py`

### Reddit (`social_scraping_reddit`)
**Used By:** vibe-reddit-scout

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Reddit API** | Free (100 req/min) | Yes | No | Community: `GeLi2001/reddit-mcp`, `Hawstein/mcp-server-reddit` | `pip install praw` or git clone | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script only | HTTP API | N/A |

**Script:** `scripts/services/social/reddit_api.py`

### LinkedIn (`social_scraping_linkedin`)
**Used By:** vibe-linkedin-scout

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **PhantomBuster** | $69+/mo | No | No | Script only | HTTP API | `PHANTOMBUSTER_API_KEY` |
| 2 | **ProxyCurl** | Pay-as-go ($0.01/profile) | No | No | Script only | HTTP API | `PROXYCURL_API_KEY` |
| 3 | **LinkedIn API** | Free (limited to own company) | Yes (limited) | No | Community: `linkedin-mcp-server` (npm) | `npm install linkedin-mcp-server` | `LINKEDIN_ACCESS_TOKEN` |

**Scripts:** `scripts/services/social/phantombuster_li.py`, `proxycurl.py`

### Meta (FB/IG) (`social_scraping_meta`)
**Used By:** vibe-social-writer, vibe-brand-monitor

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Meta Graph API** | Free | Yes | No | Community: `facebook-mcp-server` | HTTP API | `META_ACCESS_TOKEN` |
| 2 | **Apify Actors** | Pay-as-go | Yes ($5 credit) | No | Script only | HTTP API via Apify | `APIFY_TOKEN` |

**Script:** `scripts/services/social/meta_graph.py`

### TikTok (`social_scraping_tiktok`)
**Used By:** vibe-trend-detector

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **TikTok API** | Limited official access | Limited | No | Script only | HTTP API | `TIKTOK_API_KEY` |
| 2 | **ScrapeCreators** | $10/5K credits | No | No | Script only | HTTP API | N/A |

**Script:** `scripts/services/social/tiktok_api.py`

### YouTube (`social_scraping_youtube`)
**Used By:** vibe-trend-detector, vibe-review-harvester

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **YouTube Data API v3** | Free (10K units/day) | Yes | No | Community: `youtube-mcp-server` (npm), `@kirbah/mcp-youtube` | `npm install youtube-mcp-server` | `YOUTUBE_API_KEY` |
| 2 | **Apify YouTube Actors** | Pay-as-go | Yes ($5 credit) | No | Script only | HTTP API via Apify | `APIFY_TOKEN` |

**Script:** `scripts/services/social/youtube_api.py`

### VK (`social_scraping_vk`)
**Used By:** vibe-social-writer

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **VK API** | Free (generous limits) | Yes | No | Script only | HTTP API | `VK_SERVICE_TOKEN` |

**Script:** `scripts/services/social/vk_api.py`

---

## 5. Image Generation (`image_generation`)

**Used By:** vibe-image-generator

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | Best For | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|----------|
| 1 | **FLUX.2 [pro]** (fal.ai) | $0.03/MP (~$0.03 for 1024x1024) | No | No | Community: `fal-ai-mcp-server` v2.1 (npm) | `npx fal-ai-mcp-server` | Hero images, product shots, photorealism | `FAL_KEY` |
| 2 | **FLUX.2 [dev] Turbo** (fal.ai) | $0.008/MP (~$0.008 for 1024x1024) | No | No | Same fal.ai MCP | Same | Quick drafts, thumbnails, bulk generation | `FAL_KEY` |
| 3 | **GPT Image 1.5** (OpenAI) | $0.009-0.17/img | No | No | Community: `SureScaleAI/openai-gpt-image-mcp` | `npx openai-gpt-image-mcp` | General purpose, editing/inpainting, text rendering | `OPENAI_API_KEY` |
| 4 | **Ideogram 3.0** | $0.04-0.05/img; Plans: $8-60/mo | Yes (10 slow/day, public) | No | Community: `@sunwood-ai-labs/ideagram-mcp-server` (npm) | `npx @sunwood-ai-labs/ideagram-mcp-server` | Text-in-images, infographics, multi-language text | `IDEOGRAM_API_KEY` |
| 5 | **Google Imagen 4** | $0.02-0.06/img (Fast/Standard/Ultra) | No | No | Community (Google Genmedia MCP in preview) | Gemini API or Vertex AI SDK | Photorealism, 4K output, product photography | `GOOGLE_CLOUD_PROJECT` or `GOOGLE_API_KEY` |
| 6 | **Recraft V3** | $0.04/raster, $0.08/vector; $10-48/mo | Yes (50 daily) | No | Official: `recraft-ai/mcp-recraft-server` | `npx @anthropic-ai/mcp-recraft-server` | Vector/SVG generation, icons, text positioning | `RECRAFT_API_KEY` |
| 7 | **Midjourney V7** (via ImagineAPI/PiAPI) | $10-120/mo + API proxy fee | No | No | Community: `z23cc/midjourney-mcp` | HTTP API | Artistic, brand imagery, character consistency | `IMAGINEAPI_KEY` |
| 8 | **Leonardo.ai Phoenix** | Free + $10-24/mo (API: $9-299/mo) | Yes (limited) | No | Community: `ish-joshi/leonardo-mcp-server` | HTTP API | Character consistency, prompt adherence | `LEONARDO_API_KEY` |
| 9 | **Replicate** (multi-model) | $0.003-0.055/img | No | No | Official: hosted at `mcp.replicate.com` | Remote MCP (OAuth) | Access to 600+ models (FLUX.2, Ideogram, Seedream, etc.) | `REPLICATE_API_TOKEN` |

**Scripts:** `scripts/services/images/flux_generate.py`, `ideogram_generate.py`, `gpt_image_generate.py`, `imagen_generate.py`

**Recommendation:** FLUX.2 [pro] (best quality/cost). FLUX.2 [dev] Turbo for drafts/bulk. GPT Image 1.5 for general purpose + editing. Ideogram 3.0 for text-heavy designs. Recraft V3 for vectors/icons (official MCP).

---

## 6. Templated Images (`templated_images`)

**Used By:** vibe-image-generator (optional)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Bannerbear** | $49+/mo | No | No | Script only | HTTP API | `BANNERBEAR_API_KEY` |
| 2 | **Placid** | $29+/mo | No | No | Script only | HTTP API | `PLACID_API_KEY` |

**Recommendation:** Skip for MVP. Only needed for pixel-perfect branded templates.

---

## 7. Video Generation (`video_generation`)

**Used By:** vibe-video-generator

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | Best For | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|----------|
| 1 | **Runway Gen-4** | $12-76/mo | No | No | Community: `wheattoast11/mcp-video-gen` | `git clone` + install | Hero/ad videos, 4K, motion control | `RUNWAY_API_KEY` |
| 2 | **Kling AI 2.1** | Budget-friendly | No | No | Script only | HTTP API | Volume social clips | `KLING_API_KEY` |
| 3 | **Pika Labs 2.0** | Free + $8/mo | Yes | No | Script only | HTTP API | Short social content, quick iterations | `PIKA_API_KEY` |
| 4 | **Google Veo 3** | Vertex AI pricing | No | No | Community: `mario-andreschak/mcp-veo2`, `alohc/veo-mcp-server` | `git clone` + install | Cinematic quality, includes audio | `GOOGLE_CLOUD_PROJECT` |
| 5 | **Sora 2** (OpenAI) | OpenAI API pricing | No | No | Script only | HTTP API | Narrative, story-driven | `OPENAI_API_KEY` |

**Scripts:** `scripts/services/video/runway_generate.py`, `veo_generate.py`, `kling_generate.py`, `pika_generate.py`, `sora_generate.py`

**Recommendation:** Runway Gen-4 (primary, best motion control). Google Veo 3 for cinematic content with audio. Kling for budget bulk clips. Pika for quick social teasers.

---

## 8. AI Presenter / Talking Head (`ai_presenter`)

**Used By:** vibe-video-generator (optional)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **HeyGen** | $18+/mo | No | No | Script only | HTTP API | `HEYGEN_API_KEY` |
| 2 | **Synthesia** | $24+/mo | No | No | Script only | HTTP API | `SYNTHESIA_API_KEY` |
| 3 | **D-ID** | Pay-as-go | No | No | Script only | HTTP API | `DID_API_KEY` |

**Scripts:** `scripts/services/video/heygen_presenter.py`, `synthesia_presenter.py`, `did_presenter.py`

**Recommendation:** HeyGen (cheapest, good quality). Synthesia for professional/corporate. D-ID for one-off photo animations.

---

## 9. Voice Synthesis (`voice_synthesis`)

**Used By:** vibe-video-generator (optional)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **ElevenLabs** | Free tier + $5+/mo | Yes | No | Official: `elevenlabs/elevenlabs-mcp` | `docker pull mcp/elevenlabs` | `ELEVENLABS_API_KEY` |

**Recommendation:** ElevenLabs is the clear winner. Official MCP, best quality, good free tier. No alternatives needed.

---

## 10. Email Sending (`email_sending`)

**Used By:** vibe-email-writer

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **SendGrid** | Free (100/day) | Yes | No | Community: `Garoth/sendgrid-mcp`, `@cong/sendgrid-mcp` (JSR) | `npm install sendgrid-mcp` | `SENDGRID_API_KEY` |
| 2 | **Mailgun** | Free (100/day, 30-day trial) | Yes (trial) | No | Official: `mailgun/mailgun-mcp-server` | `git clone` + install | `MAILGUN_API_KEY`, `MAILGUN_DOMAIN` |
| 3 | **Brevo** (Sendinblue) | Free (300/day) | Yes | No | Script only | HTTP API | `BREVO_API_KEY` |
| 4 | **Mailchimp** | Free tier | Yes | No | Script only | HTTP API | `MAILCHIMP_API_KEY` |
| 5 | **ConvertKit** | $29+/mo | No | No | Script only | HTTP API | `CONVERTKIT_API_SECRET` |

**Scripts:** `scripts/services/email/sendgrid.py`, `mailgun.py`, `brevo.py`, `mailchimp.py`, `convertkit.py`

**Recommendation:** SendGrid (highest free tier for transactional) or Mailgun (official MCP). Brevo for marketing campaigns.

---

## 11. Social Publishing (`social_publishing`)

**Used By:** vibe-social-writer

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Buffer** | Free + $6+/channel/mo | Yes (limited) | No | Script only (Zapier bridge) | HTTP API | N/A |
| 2 | **X API v2** (posting) | Free (Essential) | Yes | No | Community | HTTP API | `X_BEARER_TOKEN` |
| 3 | **LinkedIn API** | Free (limited) | Yes | No | Community: `linkedin-mcp-server` (npm) | `npm install linkedin-mcp-server` | `LINKEDIN_ACCESS_TOKEN` |
| 4 | **Meta Graph API** | Free | Yes | No | Community | HTTP API | `META_ACCESS_TOKEN` |
| 5 | **Pinterest API** | Free | Yes | No | Script only | HTTP API | N/A |
| 6 | **TikTok API** | Limited | Limited | No | Script only | HTTP API | `TIKTOK_API_KEY` |
| 7 | **VK API** | Free | Yes | No | Script only | HTTP API | `VK_SERVICE_TOKEN` |

**Note:** Social posting is NEVER automated. Agents draft content, human approves in dashboard, THEN publishing triggers.

---

## 12. CMS Publishing (`cms_publishing`)

**Used By:** vibe-content-writer (optional)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **WordPress REST API** | Free | Yes | Yes | Official: `WordPress/mcp-adapter` (WP plugin) | Install WP plugin | `WORDPRESS_URL`, `WORDPRESS_APP_PASSWORD` |
| 2 | **Ghost API** | Free (self-hosted) / $9+/mo | Yes (self-hosted) | Yes | Community: `@fanyangmeng/ghost-mcp` (npm) | `npm install @fanyangmeng/ghost-mcp` | `GHOST_API_URL`, `GHOST_ADMIN_API_KEY` |
| 3 | **Webflow CMS API** | Paid plan required | No | No | Official: `webflow/mcp-server` | `git clone` + install | `WEBFLOW_API_TOKEN` |
| 4 | **Custom REST API** | Varies | Varies | Varies | Script only | Configurable URL | N/A |
| 5 | **Static (markdown)** | Free | Yes | Yes | Script (file write) | No install | None |

**Scripts:** `scripts/services/publishing/wp_publish.py`, `ghost_publish.py`, `webflow_publish.py`, `custom_cms.py`, `static_publish.py`

**Recommendation:** WordPress MCP (official, excellent). Webflow MCP (official). Ghost community MCP (decent). For MVP, "Static" (just write markdown files) is fine.

---

## 13. Content Quality (`content_quality`)

**Used By:** vibe-content-reviewer, vibe-plagiarism-checker

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **LanguageTool** | Free (open source) | Yes | Yes | Script only (adjacent grammar MCP exists) | `docker pull erikvl87/languagetool` | None (self-hosted) |
| 2 | **Copyscape** | $0.03/check | No | No | Script only | HTTP API | `COPYSCAPE_USER`, `COPYSCAPE_API_KEY` |
| 3 | **Copyleaks** | $9.16+/mo | No | No | Script only | HTTP API | `COPYLEAKS_API_KEY` |

**Scripts:** `scripts/services/quality/languagetool.py`, `copyscape.py`, `copyleaks.py`

**Note:** LanguageTool can be self-hosted (Docker) for unlimited free usage.

**Self-Hosted Details:**
- **LanguageTool:** Docker image `erikvl87/languagetool`, port 8081, 512MB-1GB RAM, ~2GB disk (n-grams), replaces LanguageTool Cloud API

---

## 14. Web Search (`web_search`)

**Used By:** All research agents (8+)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Brave Search** | Free (2K/mo) / $3/1K | Yes | No | Official: `@anthropic-ai/mcp-server-brave-search` (npm) | `npx -y @anthropic-ai/mcp-server-brave-search` | `BRAVE_API_KEY` |
| 2 | **Google Custom Search** | Free (100/day) | Yes | No | Script only | HTTP API | `GOOGLE_CSE_API_KEY`, `GOOGLE_CSE_CX` |
| 3 | **Perplexity** | $0.20/1K queries | No | No | Official: `perplexityai/modelcontextprotocol` | `git clone` + install | `PERPLEXITY_API_KEY` |

**Recommendation:** Brave Search MCP (primary, already in Claude Code's default MCP set). Perplexity MCP for deep research (synthesized answers). Google CSE for specific site:search patterns.

---

## 15. Analytics (`analytics`)

**Used By:** Dashboard, vibe-seo-auditor

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Google Search Console** | Free | Yes | No | Community: `ahonn/mcp-server-gsc` | `git clone` + install | OAuth2 service account JSON |
| 2 | **Google Analytics 4** | Free | Yes | No | Official (Google): `developers.google.com/analytics/devguides/MCP` | Google Cloud SDK | `GA4_PROPERTY_ID`, `GOOGLE_APPLICATION_CREDENTIALS` |
| 3 | **Plausible** | Self-hosted (free) / $9+/mo | Yes (self-hosted) | Yes | Script only | `docker pull plausible/analytics` | Self-hosted URL |
| 4 | **Umami** | Self-hosted (free) | Yes (self-hosted) | Yes | Script only | `docker pull ghcr.io/umami-software/umami` | Self-hosted URL |

**Scripts:** `scripts/services/analytics/gsc_analytics.py`, `ga4_analytics.py`, `plausible.py`, `umami.py`

**Recommendation:** GSC + GA4 (standard pair, both have MCP servers, GA4 is official from Google). Plausible/Umami for privacy-friendly analytics.

**Self-Hosted Details:**
- **Plausible:** Docker image `plausible/analytics`, port 8000, ~256MB RAM, ~500MB disk
- **Umami:** Docker image `ghcr.io/umami-software/umami`, port 3001, ~128MB RAM, ~200MB disk

---

## 16. Advertising (`advertising`) — FUTURE

**Used By:** FUTURE agents (post-MVP)

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Google Ads** | Pay-per-click | No | No | Official: `googleads/google-ads-mcp` (Python) | `pip install google-ads-mcp` | `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CUSTOMER_ID` |
| 2 | **Meta Ads** (FB + IG) | Pay-per-click | No | No | Community: `pipeboard-co/meta-ads-mcp`, `gomarble-ai/facebook-ads-mcp-server` | `git clone` + install | `META_ADS_ACCESS_TOKEN` |

**Recommendation:** Not needed for MVP content generation. Google Ads has official MCP. Meta Ads has community MCPs.

---

## 17. Notifications (`notifications`)

**Used By:** vibe-orchestrator

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Telegram Bot API** | Free | Yes | No | Community: `chigwell/telegram-mcp`, `sparfenyuk/mcp-telegram` | `pip install telegram-mcp` or git clone | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| 2 | **Discord Webhook** | Free | Yes | No | Community: `mcp-discord` (npm), `barryyip0625/mcp-discord` | `npm install mcp-discord` | `DISCORD_WEBHOOK_URL` |
| 3 | **Slack Webhook** | Free | Yes | No | Official: `@modelcontextprotocol/server-slack` (npm) | `npx -y @modelcontextprotocol/server-slack` | `SLACK_BOT_TOKEN` |

**Scripts:** `scripts/services/notifications/telegram_notify.py`, `discord_notify.py`, `slack_notify.py`

**Recommendation:** Telegram (primary, free, simple, mobile). Slack MCP (official, excellent for teams). Discord for community-facing alerts.

---

## 18. Document Generation (`document_generation`) — LOCAL

**Used By:** vibe-ebook-writer

| Priority | Provider | Cost | Free Tier | Self-Hosted | MCP Server | Install Method | API Keys |
|----------|----------|------|-----------|-------------|------------|----------------|----------|
| 1 | **Pandoc** | Free (local) | Yes | Yes | Bash only | `apt install pandoc` or `brew install pandoc` | None |
| 2 | **Calibre** | Free (local) | Yes | Yes | Bash only | `apt install calibre` or `brew install calibre` | None |
| 3 | **Puppeteer/Playwright** | Free (local) | Yes | Yes | Script only | `npm install puppeteer` or `pip install playwright` | None |

**Recommendation:** All local tools. No API keys. Pandoc for format conversion. Calibre for ebook formats. Puppeteer for HTML-to-PDF and screenshots.

---

## MCP Server Registry Summary

### Official MCP Servers (18)
Firecrawl, Brave Search, Perplexity, Ahrefs, SEMrush, GA4, Mailgun, Slack, WordPress, Webflow, ElevenLabs, Google Ads, Stripe, Cloudflare, Vercel, GitHub, Recraft, Replicate

### Community MCP Servers (17)
DataForSEO, GSC, Reddit, X/Twitter, LinkedIn, YouTube, SendGrid, Telegram, Discord, Ghost, GPT Image (OpenAI), fal.ai, Runway, Meta Ads, Google Imagen, Google Veo, Ideogram

### Script-Only Integrations (10)
Google Keyword Planner, AnswerThePublic, Bing Webmaster, Crawl4AI, ScraperAPI, Apify, PhantomBuster, ProxyCurl, Copyscape, LanguageTool, Buffer, Bannerbear/Placid

### Local Tools (3)
Pandoc, Calibre, Puppeteer

---

## Self-Hosted Services

Managed by `docker-compose.services.yml`:

| Service | Docker Image | Port | RAM | Disk | Replaces | Capability |
|---------|-------------|------|-----|------|----------|-----------|
| **Crawl4AI** | `unclecode/crawl4ai` | 11235 | ~512MB | ~1GB | Firecrawl (batch) | web_scraping |
| **LanguageTool** | `erikvl87/languagetool` | 8081 | 512MB-1GB | ~2GB | LanguageTool Cloud | content_quality |
| **Plausible** | `plausible/analytics` | 8000 | ~256MB | ~500MB | Google Analytics 4 | analytics |
| **Umami** | `ghcr.io/umami-software/umami` | 3001 | ~128MB | ~200MB | Google Analytics 4 | analytics |

**URLs:**
- `CRAWL4AI_URL=http://localhost:11235`
- `LANGUAGETOOL_URL=http://localhost:8081`

---

## Free Minimum Stack

**23 of 31 agents** can run at $0/mo:

| Agent Category | Free Services | Setup |
|---------------|---------------|-------|
| Orchestration | Telegram Bot | @BotFather (free) |
| Content Writers (9 agents) | None (skills only) | No setup |
| Quality (2 agents) | LanguageTool (self-hosted), Brave Search | Docker + Brave API (free 2K/mo) |
| SEO (3 agents) | Google Keyword Planner + GSC + Brave | Google Ads account (free) + GSC OAuth + Brave |
| Scraping (3 agents) | Brave Search + Crawl4AI | Brave + `docker pull unclecode/crawl4ai` |
| Social (3 agents) | Reddit API, X API v2 Essential, YouTube Data API | Platform API keys (free) |
| Audience (3 agents) | Brave Search (optional) | Brave or no setup |

**Agents requiring spend:**
- vibe-linkedin-scout: $69/mo (PhantomBuster, no free alternative)
- vibe-plagiarism-checker: ~$3/mo (Copyscape, no free alternative)
- vibe-image-generator: ~$2.40/mo (FLUX.2 [dev] Turbo, 300 images)
- vibe-video-generator: $0 (Pika free tier, limited)

**Total minimum viable spend: ~$73/mo** (dominated by LinkedIn) or **~$4/mo** (without LinkedIn)

---

## Complete .env Template

The setup script (`scripts/setup.sh`) writes this template to `.env` (chmod 600):

```bash
# Self-Hosted Services
CRAWL4AI_URL=http://localhost:11235
LANGUAGETOOL_URL=http://localhost:8081

# Web Search
BRAVE_API_KEY=
PERPLEXITY_API_KEY=
GOOGLE_CSE_API_KEY=
GOOGLE_CSE_CX=

# SEO & Keywords
DATAFORSEO_LOGIN=
DATAFORSEO_PASSWORD=
AHREFS_API_KEY=
SEMRUSH_API_KEY=
GOOGLE_ADS_DEVELOPER_TOKEN=

# SERP & Rank Tracking
# GSC_SERVICE_ACCOUNT_JSON=path/to/service-account.json
BING_WEBMASTER_API_KEY=

# Web Scraping
FIRECRAWL_API_KEY=
APIFY_TOKEN=
SCRAPER_API_KEY=

# Social: X/Twitter
X_BEARER_TOKEN=

# Social: Reddit
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=vibe-marketing/1.0

# Social: LinkedIn
PHANTOMBUSTER_API_KEY=
PROXYCURL_API_KEY=
LINKEDIN_ACCESS_TOKEN=

# Social: Meta (FB/IG)
META_ACCESS_TOKEN=

# Social: TikTok
TIKTOK_API_KEY=

# Social: YouTube
YOUTUBE_API_KEY=

# Social: VK
VK_SERVICE_TOKEN=

# Image Generation
FAL_KEY=
OPENAI_API_KEY=
IDEOGRAM_API_KEY=
GOOGLE_CLOUD_PROJECT=
REPLICATE_API_TOKEN=
IMAGINEAPI_KEY=
LEONARDO_API_KEY=
RECRAFT_API_KEY=

# Templated Images
BANNERBEAR_API_KEY=
PLACID_API_KEY=

# Video Generation
RUNWAY_API_KEY=
KLING_API_KEY=
PIKA_API_KEY=
# SORA: uses OPENAI_API_KEY above

# AI Presenter
HEYGEN_API_KEY=
SYNTHESIA_API_KEY=
DID_API_KEY=

# Voice / Audio
ELEVENLABS_API_KEY=

# Email Sending
SENDGRID_API_KEY=
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
BREVO_API_KEY=
MAILCHIMP_API_KEY=
CONVERTKIT_API_SECRET=

# CMS Publishing
WORDPRESS_URL=
WORDPRESS_APP_PASSWORD=
GHOST_API_URL=
GHOST_ADMIN_API_KEY=
WEBFLOW_API_TOKEN=

# Content Quality
COPYSCAPE_USER=
COPYSCAPE_API_KEY=
COPYLEAKS_API_KEY=

# Analytics
GA4_PROPERTY_ID=
# GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Advertising (FUTURE)
GOOGLE_ADS_CUSTOMER_ID=
META_ADS_ACCESS_TOKEN=

# Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=
SLACK_BOT_TOKEN=

# Infrastructure
GITHUB_PERSONAL_ACCESS_TOKEN=
CLOUDFLARE_API_TOKEN=
STRIPE_SECRET_KEY=

# Self-Hosted Analytics (optional)
PLAUSIBLE_SECRET_KEY=
PLAUSIBLE_DB_PASSWORD=
UMAMI_DB_PASSWORD=
```

---

## Key Architectural Patterns

### 1. Capability Abstraction
Agents declare **capabilities** (not services) in SKILL.md. Runtime resolution via `resolve_service.py` queries Convex for active providers.

### 2. Automatic Fallback
When primary provider fails, `resolve_service.py --skip <failed_name>` returns next-priority provider. Up to 3 retries before task is blocked.

### 3. Health Monitoring
Cron job (`scripts/health_check_services.py`) runs every 15 minutes, tests each active service, updates Convex `serviceHealth` table. Auto-skips "down" services.

### 4. Agent Gating
Pipeline builder UI shows agent status:
- **ENABLED (green):** All required capabilities have >= 1 active provider
- **DISABLED (gray):** Any required capability has 0 providers
- **DEGRADED (yellow badge):** Required capabilities met, but optional capabilities missing

### 5. Dashboard Configuration
Settings -> Services page:
- Capability tabs (SEO, Scraping, Images, etc.)
- Drag-and-drop priority ordering
- API key entry (encrypted in Convex)
- Test Connection button per service
- Agent impact panel shows affected agents

---

## Cost Tiers Summary

| Tier | Monthly Cost | What You Get |
|------|-------------|-------------|
| **Free** | $0 + Claude Max ($200) | 23/31 agents enabled via free tiers + self-hosted |
| **Growth** | $90-95 + Claude Max | Free tier + DataForSEO, Firecrawl, FLUX.2, Ideogram, Copyscape, ElevenLabs |
| **Pro** | $365-475 + Claude Max | Growth + Ahrefs, Runway, Veo, PhantomBuster, HeyGen, CMS publishing |

**Minimum viable setup: ~$4/mo** (plagiarism + images) or **~$73/mo** (if LinkedIn scraping needed).

