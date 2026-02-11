# Research Report: MCP Servers for Marketing Automation Platform
Generated: 2026-02-11

## Summary

The MCP (Model Context Protocol) ecosystem has exploded to 17,000+ servers as of February 2026. For the Vibe Marketing Platform, there are production-ready MCP servers covering all 9 capability categories researched: SEO/keywords, web scraping, Reddit, Twitter/X, image generation, email, search (Perplexity), YouTube, and more. Many have official implementations from the service providers themselves (Ahrefs, Perplexity, Resend, Firecrawl, DataForSEO). The platform currently only has Playwright MCP configured.

## Questions Answered

### Q1: SEO/Keyword Research MCPs
**Answer:** 5+ viable options exist. Best picks: Official Ahrefs MCP (paid, comprehensive), DataForSEO MCP (pay-as-you-go, cheapest), Keywords Everywhere MCP (credit-based), SEO-MCP/cnych (free but scrapes Ahrefs), Semrush MCP (paid, comprehensive).
**Confidence:** High

### Q2: Web Scraping MCPs
**Answer:** 2 primary options. Firecrawl MCP (official, cloud or self-hosted) and Crawl4AI MCP (fully free, self-hosted). Both production-ready.
**Confidence:** High

### Q3: Reddit MCPs
**Answer:** Multiple community MCPs exist. WARNING: Reddit stopped issuing free API keys in December 2025. Some MCPs use public JSON endpoints (no auth), others use session cookies. Risk of account bans for automation.
**Confidence:** High

### Q4: Twitter/X MCPs
**Answer:** Several community MCPs available. EnesCinr/twitter-mcp is the most maintained. Requires Twitter Developer API keys (OAuth). Read + Write support.
**Confidence:** High

### Q5: Image Generation MCPs
**Answer:** Multiple options across providers. fal.ai MCP (600+ models, free tier), Together AI MCP (Flux free model), Replicate MCP (Flux), DALL-E MCP (OpenAI). fal.ai offers best breadth.
**Confidence:** High

### Q6: Email MCPs
**Answer:** Both Resend and SendGrid have MCP servers. Resend is official with 3,000 emails/month free. SendGrid has community MCPs with full marketing API support.
**Confidence:** High

### Q7: Perplexity Search MCP
**Answer:** Official Perplexity MCP server exists with Sonar, Sonar Pro, and Deep Research models. Pay-as-you-go at $1/M tokens. No permanent free tier but Pro subscribers get $5/month credit.
**Confidence:** High

### Q8: YouTube MCPs
**Answer:** Multiple MCPs available. anaisbetts/mcp-youtube (transcripts via yt-dlp), youtube-data-mcp-server (YouTube Data API v3), youtube-transcript-mcp (captions/subtitles).
**Confidence:** High

### Q9: Aggregate Directories
**Answer:** Major directories: mcpservers.org, mcp.so, mcp-awesome.com (1200+), punkpeye/awesome-mcp-servers (GitHub), PulseMCP (8240+).
**Confidence:** High

---

## Detailed Findings by Category

---

### 1. SEO / Keyword Research

#### 1a. Official Ahrefs MCP Server
- **GitHub:** https://github.com/ahrefs/ahrefs-mcp-server
- **npm:** `@ahrefs/mcp`
- **What it does:** Rank tracking, keyword research, batch analysis, search volume, competitor insights, backlink analysis, site audit, content explorer
- **Installation:**
  ```bash
  npm install --prefix=~/.global-node-modules @ahrefs/mcp -g
  ```
- **MCP config:**
  ```json
  {
    "ahrefs": {
      "command": "npx",
      "args": ["--prefix=~/.global-node-modules", "@ahrefs/mcp"],
      "env": { "API_KEY": "YOUR_AHREFS_API_V3_KEY" }
    }
  }
  ```
- **API Key:** Required. Ahrefs API v3 key from workspace settings. Requires Ahrefs subscription (Lite $99/mo+).
- **Free tier:** No. Requires paid Ahrefs plan.
- **Notes:** API v2 was discontinued Nov 2025. Must use v3.

#### 1b. DataForSEO MCP Server (OFFICIAL)
- **GitHub:** https://github.com/dataforseo/mcp-server-typescript (official) and https://github.com/Skobyn/dataforseo-mcp-server (community)
- **npm:** `dataforseo-mcp-server`
- **What it does:** SERP data, keyword research, backlinks, on-page SEO, domain analytics, content analysis, competitive intelligence. Extremely granular data.
- **Installation:**
  ```bash
  npx dataforseo-mcp-server
  # or: npm install -g dataforseo-mcp-server
  # or for Claude Code:
  claude mcp add dfs-mcp --env DATAFORSEO_USERNAME=<user> --env DATAFORSEO_PASSWORD=<pass> -- npx -y dataforseo-mcp-server
  ```
- **MCP config:**
  ```json
  {
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server"],
      "env": {
        "DATAFORSEO_USERNAME": "your_username",
        "DATAFORSEO_PASSWORD": "your_password"
      }
    }
  }
  ```
- **API Key:** Username + password (not a single key). Sign up at dataforseo.com.
- **Free tier:** $1 credit on signup + free Sandbox. No monthly fees. Pay-as-you-go: $0.60/1,000 SERPs (standard), $50 minimum top-up.
- **Best for:** Budget-conscious marketing platforms. Most affordable per-request pricing.

#### 1c. Semrush MCP Server
- **GitHub:** https://github.com/metehan777/semrush-mcp and https://github.com/mrkooblu/semrush-mcp
- **What it does:** Traffic analytics, position tracking, keyword research, backlinks, ad research, domain analytics, content analysis
- **Installation:**
  ```bash
  git clone https://github.com/metehan777/semrush-mcp.git
  cd semrush-mcp && npm install && npm run build
  ```
- **MCP config:**
  ```json
  {
    "semrush": {
      "command": "npx",
      "args": ["-y", "github:mrkooblu/semrush-mcp"],
      "env": { "SEMRUSH_API_KEY": "your_api_key" }
    }
  }
  ```
- **API Key:** Required. From Semrush account > Subscription info > API Units tab.
- **Free tier:** No. Requires Semrush subscription (~$130/mo+). API units consumed per request.

#### 1d. Keywords Everywhere MCP Server
- **GitHub:** https://github.com/hithereiamaliff/mcp-keywords-everywhere
- **What it does:** Keyword search volume, CPC, competition data, related keywords, domain analysis, traffic metrics, backlinks
- **Installation:** Node.js 18+. Clone + `npm install`, or use hosted endpoint.
- **API Key:** Required. Keywords Everywhere account needed. API requires purchased credits.
- **Free tier:** Account is free. API credits must be purchased ($10 for 100,000 credits).

#### 1e. SEO-MCP (Free Ahrefs Data)
- **GitHub:** https://github.com/cnych/seo-mcp
- **PyPI:** `seo-mcp`
- **What it does:** Backlink analysis, keyword ideas from Ahrefs data (scraping approach). Free.
- **Installation:**
  ```bash
  pip install seo-mcp
  # or: uv pip install seo-mcp
  ```
- **API Key:** Requires CAPSOLVER_API_KEY (for CAPTCHA solving). Python 3.10+.
- **Free tier:** Yes (tool itself is free). Need CapSolver credits for CAPTCHA.
- **WARNING:** Scrapes Ahrefs data. "For educational purposes only." May violate Ahrefs ToS.

---

### 2. Web Scraping

#### 2a. Firecrawl MCP Server (OFFICIAL)
- **GitHub:** https://github.com/firecrawl/firecrawl-mcp-server
- **npm:** `firecrawl-mcp`
- **What it does:** Single-page scrape (markdown/HTML/screenshot), full-site crawl with depth control, LLM-based structured data extraction from pages, web search
- **Installation:**
  ```bash
  npx -y firecrawl-mcp
  ```
- **MCP config:**
  ```json
  {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "YOUR_API_KEY" }
    }
  }
  ```
- **API Key:** Required. From firecrawl.dev/app/api-keys.
- **Free tier:** 500 credits on signup. Then pay-as-you-go.
- **Self-hosted option:** Yes. Can point to self-hosted Firecrawl instance via `FIRECRAWL_API_URL`.
- **Notes:** Y Combinator backed, $14.5M Series A (Aug 2025). 350,000+ developers.

#### 2b. Crawl4AI MCP Server (FREE, Self-Hosted)
- **GitHub:** https://github.com/sadiuysal/crawl4ai-mcp-server (also: https://github.com/BjornMelin/crawl4ai-mcp-server)
- **PyPI:** `crawl4ai-mcp-server`
- **Docker:** `uysalsadi/crawl4ai-mcp-server:latest`
- **What it does:** scrape, crawl, crawl_site, crawl_sitemap. Similar to Firecrawl but completely free and self-hosted.
- **Installation:**
  ```bash
  pip3 install crawl4ai-mcp-server
  # or Docker:
  docker pull uysalsadi/crawl4ai-mcp-server:latest
  ```
- **API Key:** None required. Fully self-hosted.
- **Free tier:** 100% free. Open source.
- **Best for:** This platform (already runs Crawl4AI via docker-compose.services.yml).

---

### 3. Reddit

#### 3a. mcp-server-reddit (Hawstein)
- **GitHub:** https://github.com/Hawstein/mcp-server-reddit
- **PyPI:** `mcp-server-reddit`
- **What it does:** Frontpage posts, subreddit info + hot posts, post details, comments. Uses redditwarp library.
- **Installation:**
  ```bash
  pip install mcp-server-reddit
  # or via uvx (no install needed):
  uvx mcp-server-reddit
  # or via Smithery:
  npx -y @smithery/cli install @Hawstein/mcp-server-reddit --client claude
  ```
- **MCP config (uvx):**
  ```json
  {
    "reddit": {
      "command": "uvx",
      "args": ["mcp-server-reddit"]
    }
  }
  ```
- **API Key:** None for public data. Uses Reddit's public API via redditwarp.
- **Free tier:** Yes, fully free for read-only public data.
- **License:** MIT

#### 3b. reddit-mcp (paltaio) - No Auth Required
- **GitHub/Glama:** https://glama.ai/mcp/servers/@paltaio/reddit-mcp
- **What it does:** Reddit public data using Reddit's public JSON API (no authentication needed).
- **API Key:** None required.
- **Free tier:** Fully free.

#### 3c. reddit-mcp (iris-alights) - Authenticated
- **Glama:** https://glama.ai/mcp/servers/@iris-alights/reddit-mcp
- **What it does:** Read-only AND authenticated access (commenting, voting). Uses browser session cookies instead of API keys.
- **API Key:** Uses browser session cookies.
- **WARNING:** Reddit banned free API keys Dec 2025. Automated access may result in account bans.

---

### 4. Twitter / X

#### 4a. twitter-mcp (EnesCinr) -- RECOMMENDED
- **GitHub:** https://github.com/EnesCinr/twitter-mcp
- **npm:** `@enescinar/twitter-mcp`
- **What it does:** Post tweets, search tweets. Updated Jan 2026.
- **Installation:**
  ```bash
  npx -y @enescinar/twitter-mcp
  ```
- **MCP config:**
  ```json
  {
    "twitter": {
      "command": "npx",
      "args": ["-y", "@enescinar/twitter-mcp"],
      "env": {
        "API_KEY": "your_api_key",
        "API_SECRET_KEY": "your_api_secret",
        "ACCESS_TOKEN": "your_access_token",
        "ACCESS_TOKEN_SECRET": "your_access_token_secret"
      }
    }
  }
  ```
- **API Key:** Required. Twitter Developer Portal (developer.twitter.com). 4 credentials needed: API key, API secret, access token, access token secret.
- **Free tier:** Twitter API Free tier allows 1,500 tweets/month write, limited read. Basic tier $100/mo.

#### 4b. x-mcp-server (mbelinky) -- OAuth 2.0
- **GitHub/mcpservers.org:** https://mcpservers.org/servers/mbelinky/x-mcp-server
- **What it does:** Enhanced X server with OAuth 2.0 support, v2 API media uploads, comprehensive rate limiting.
- **API Key:** OAuth 2.0 credentials required.

---

### 5. Image Generation

#### 5a. fal.ai MCP Server -- RECOMMENDED
- **npm:** `fal-ai-mcp-server`
- **GitHub:** https://github.com/el-el-san/fal-mcp-server (community) and https://github.com/raveenb/fal-mcp-server
- **What it does:** Access to 600+ AI models including Flux, Stable Diffusion, Recraft v3. Image generation, video generation, music/audio.
- **Installation:**
  ```bash
  npx -y fal-ai-mcp-server
  ```
- **MCP config:**
  ```json
  {
    "fal": {
      "command": "npx",
      "args": ["-y", "fal-ai-mcp-server"],
      "env": { "FAL_KEY": "your_fal_api_key" }
    }
  }
  ```
- **API Key:** Required. From fal.ai/dashboard/keys.
- **Free tier:** Yes. Free credits on signup (~$5-10 worth). Flux[dev] $0.025/image. Credits expire in 90 days.
- **Best for:** Marketing platform. Broadest model selection, cheap per-image.

#### 5b. Together AI MCP (Flux Schnell FREE)
- **GitHub:** https://github.com/manascb1344/together-mcp-server
- **npm:** `together-mcp`
- **What it does:** Image generation via Together AI's Flux.1 Schnell model (including free variant).
- **Installation:**
  ```bash
  npx together-mcp@latest
  ```
- **API Key:** Required. From api.together.xyz.
- **Free tier:** Has `black-forest-labs/FLUX.1-schnell-Free` model (free to use). Together AI gives $1 free credits on signup.
- **Best for:** Zero-cost image generation with decent quality.

#### 5c. DALL-E MCP Server
- **PulseMCP:** https://www.pulsemcp.com/servers/sammyl720-dall-e-image-generator
- **What it does:** DALL-E 3 image generation via OpenAI API.
- **API Key:** Required. OpenAI API key.
- **Free tier:** No. ~$0.04-0.08 per image depending on resolution.

#### 5d. Replicate Flux MCP
- **PulseMCP:** https://www.pulsemcp.com/servers/mikeyny-image-generation-replicate-flux-schnell
- **What it does:** Image generation via Replicate's Flux Schnell model.
- **API Key:** Required. Replicate API token.
- **Free tier:** Limited free credits on Replicate.

---

### 6. Email

#### 6a. Resend MCP Server (OFFICIAL) -- RECOMMENDED
- **GitHub:** https://github.com/resend/mcp-send-email (official) and https://github.com/PSU3D0/resend-mcp (49 tools, comprehensive)
- **What it does:**
  - Official: Send plain text/HTML emails, schedule delivery, CC/BCC, reply-to, custom sender
  - PSU3D0: 49 tools covering emails, domains, contacts, templates, broadcasts, webhooks
- **Installation:**
  ```bash
  # Official (build from source):
  git clone https://github.com/resend/mcp-send-email.git
  cd mcp-send-email && npm install && npm run build
  # Community comprehensive version:
  pip install resend-mcp
  ```
- **MCP config (official):**
  ```json
  {
    "resend": {
      "command": "node",
      "args": ["path/to/mcp-send-email/dist/index.js"],
      "env": { "RESEND_API_KEY": "re_your_key" }
    }
  }
  ```
- **API Key:** Required. From resend.com dashboard.
- **Free tier:** 3,000 emails/month (100/day). Marketing: unlimited emails to 1,000 contacts.
- **Paid:** $20/mo for 50K emails.

#### 6b. SendGrid MCP Server (Garoth)
- **GitHub:** https://github.com/Garoth/sendgrid-mcp
- **What it does:** Full SendGrid Marketing API: contact lists, templates, single sends, stats, email validation, unsubscribe groups.
- **Installation:**
  ```bash
  git clone https://github.com/Garoth/sendgrid-mcp.git
  cd sendgrid-mcp && npm install
  ```
- **MCP config:**
  ```json
  {
    "sendgrid": {
      "command": "node",
      "args": ["path/to/sendgrid-mcp/dist/index.js"],
      "env": { "SENDGRID_API_KEY": "SG.your_key" }
    }
  }
  ```
- **API Key:** Required. SendGrid account > Settings > API Keys.
- **Free tier:** SendGrid Free: 100 emails/day.

---

### 7. Perplexity Search

#### 7a. Perplexity MCP Server (OFFICIAL) -- RECOMMENDED
- **GitHub:** https://github.com/perplexityai/modelcontextprotocol
- **npm:** `@perplexity-ai/mcp-server`
- **What it does:** Real-time web search, conversational AI (sonar-pro), deep research (sonar-deep-research), advanced reasoning (sonar-reasoning-pro). Returns results with citations.
- **Installation:**
  ```bash
  npx -y @perplexity-ai/mcp-server
  # or for Claude Code:
  claude mcp add perplexity --env PERPLEXITY_API_KEY="your_key" -- npx -y @perplexity-ai/mcp-server
  ```
- **MCP config:**
  ```json
  {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": { "PERPLEXITY_API_KEY": "pplx-your_key" }
    }
  }
  ```
- **API Key:** Required. From perplexity.ai API Portal.
- **Free tier:** No permanent free tier. Pro subscribers get $5/mo credit. Sonar: $1/M tokens input + $1/M tokens output. Deep Research: more expensive.
- **Best for:** Agent research tasks. Much better than raw web scraping for information synthesis.

---

### 8. YouTube

#### 8a. mcp-youtube (anaisbetts) -- RECOMMENDED
- **GitHub:** https://github.com/anaisbetts/mcp-youtube
- **npm:** `@anaisbetts/mcp-youtube`
- **What it does:** Fetch YouTube video transcripts/subtitles via yt-dlp. Provide them as context to Claude.
- **Installation:**
  ```bash
  npx -y @anaisbetts/mcp-youtube
  ```
- **MCP config:**
  ```json
  {
    "youtube": {
      "command": "npx",
      "args": ["-y", "@anaisbetts/mcp-youtube"]
    }
  }
  ```
- **API Key:** None required. Uses yt-dlp for subtitle extraction.
- **Free tier:** 100% free. No API needed.
- **Requirement:** yt-dlp must be installed on system.

#### 8b. youtube-data-mcp-server (icraft2170)
- **GitHub:** https://github.com/icraft2170/youtube-data-mcp-server
- **What it does:** YouTube Data API v3 integration. Search videos, channel stats, engagement metrics, regional/category data.
- **API Key:** Required. YouTube Data API v3 key from Google Cloud Console.
- **Free tier:** YouTube Data API: 10,000 quota units/day free.

#### 8c. youtube-mcp-server (ZubeidHendricks) -- Full API
- **GitHub:** https://github.com/ZubeidHendricks/youtube-mcp-server
- **What it does:** Video management, Shorts creation, advanced analytics.
- **API Key:** Required. YouTube Data API v3 + OAuth.

---

### 9. Aggregate Directories

| Directory | URL | Count | Notes |
|-----------|-----|-------|-------|
| PulseMCP | https://www.pulsemcp.com/servers | 8,240+ | Searchable, ratings |
| mcp.so | https://mcp.so/ | 17,155+ | Largest directory |
| awesome-mcp-servers (GitHub) | https://github.com/punkpeye/awesome-mcp-servers | Curated | Community maintained |
| mcpservers.org | https://mcpservers.org/ | Curated | Categorized |
| mcp-awesome.com | https://mcp-awesome.com/ | 1,200+ | Quality-verified |
| Glama MCP | https://glama.ai/mcp/servers | Large | Good search |
| Smithery | https://smithery.ai/ | Growing | 1-click install |
| MCP Market | https://mcpmarket.com/ | Growing | Marketplace |

---

## Comparison Matrix: Recommended MCP Stack for Vibe Marketing

| Category | Recommended MCP | Free? | Monthly Cost | Priority |
|----------|----------------|-------|-------------|----------|
| **Web Scraping** | Crawl4AI MCP | YES (self-hosted) | $0 | HIGH - Already have Crawl4AI |
| **Web Scraping (premium)** | Firecrawl MCP | 500 credits free | Pay-as-you-go | MEDIUM |
| **SEO Keywords** | DataForSEO MCP | $1 credit | ~$0.60/1K SERPs | HIGH |
| **SEO (premium)** | Ahrefs MCP | No | $99+/mo | LOW (expensive) |
| **Search/Research** | Perplexity MCP | $5/mo credit (Pro) | ~$1/M tokens | HIGH |
| **Image Gen** | fal.ai MCP | Free credits | ~$0.025/image | HIGH |
| **Image Gen (free)** | Together AI MCP | Free Flux model | $0 | MEDIUM |
| **Email** | Resend MCP | 3K emails/mo | $0 | HIGH |
| **Reddit** | mcp-server-reddit | YES | $0 | MEDIUM |
| **Twitter/X** | twitter-mcp (EnesCinr) | 1500 tweets/mo | $0 (free tier) | MEDIUM |
| **YouTube** | mcp-youtube (anaisbetts) | YES | $0 | MEDIUM |

---

## Recommendations for Vibe Marketing Platform

### Immediate Additions (Free / Already Have Infrastructure)

1. **Crawl4AI MCP** -- You already run Crawl4AI via docker-compose. Adding the MCP gives agents direct scraping access.
2. **mcp-server-reddit** -- Free, no API key. Read-only Reddit data for research agents.
3. **mcp-youtube (anaisbetts)** -- Free, no API key. Video transcript extraction for content research.
4. **Resend MCP** -- 3,000 emails/month free. Sufficient for MVP email campaigns.

### High-Value Additions (Low Cost)

5. **DataForSEO MCP** -- $1 free credit, then ~$0.60/1K queries. Best value for keyword research.
6. **Perplexity MCP** -- Official server, Sonar models. $1/M tokens. Critical for research agents (oracle, content-researcher).
7. **fal.ai MCP** -- Free credits on signup. ~$0.025/image. For social media graphics and campaign assets.
8. **Together AI MCP** -- Has a completely free Flux Schnell model for basic image generation.

### When Budget Allows

9. **Firecrawl MCP** -- Premium scraping with JS rendering, better than Crawl4AI for complex sites.
10. **twitter-mcp** -- Requires Twitter Developer account. Free tier: 1,500 tweets/month.
11. **Ahrefs MCP** -- Only if already paying for Ahrefs ($99+/mo). Most comprehensive SEO data.
12. **Semrush MCP** -- Only if already paying for Semrush ($130+/mo).

### Proposed .mcp.json Configuration

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": { "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}" }
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    },
    "dataforseo": {
      "command": "npx",
      "args": ["-y", "dataforseo-mcp-server"],
      "env": {
        "DATAFORSEO_USERNAME": "${DATAFORSEO_USERNAME}",
        "DATAFORSEO_PASSWORD": "${DATAFORSEO_PASSWORD}"
      }
    },
    "reddit": {
      "command": "uvx",
      "args": ["mcp-server-reddit"]
    },
    "twitter": {
      "command": "npx",
      "args": ["-y", "@enescinar/twitter-mcp"],
      "env": {
        "API_KEY": "${TWITTER_API_KEY}",
        "API_SECRET_KEY": "${TWITTER_API_SECRET}",
        "ACCESS_TOKEN": "${TWITTER_ACCESS_TOKEN}",
        "ACCESS_TOKEN_SECRET": "${TWITTER_ACCESS_TOKEN_SECRET}"
      }
    },
    "fal": {
      "command": "npx",
      "args": ["-y", "fal-ai-mcp-server"],
      "env": { "FAL_KEY": "${FAL_KEY}" }
    },
    "resend": {
      "command": "node",
      "args": ["path/to/resend-mcp/dist/index.js"],
      "env": { "RESEND_API_KEY": "${RESEND_API_KEY}" }
    },
    "youtube": {
      "command": "npx",
      "args": ["-y", "@anaisbetts/mcp-youtube"]
    }
  }
}
```

### Implementation Notes

- The current `.mcp.json` only has Playwright MCP configured.
- Reddit MCP uses `uvx` (uv runner) -- ensure `uv` is installed (it is, based on CLAUDE.md context).
- YouTube MCP requires `yt-dlp` on PATH: `pip install yt-dlp` or `apt install yt-dlp`.
- Resend official MCP requires building from source. Consider PSU3D0/resend-mcp (pip install) for more comprehensive tooling (49 tools vs basic send).
- fal.ai free credits expire in 90 days; purchased credits last 365 days.
- DataForSEO has a $50 minimum top-up after the initial $1 credit.
- For Reddit, the Hawstein server (read-only) is safest. Do NOT use authenticated Reddit MCPs -- account ban risk is real.
- Twitter free tier is very limited (1,500 tweets/month write). For a marketing platform, Basic ($100/mo) may be needed.

---

## Sources

1. [Ahrefs MCP Server (GitHub)](https://github.com/ahrefs/ahrefs-mcp-server)
2. [DataForSEO MCP Server (Official)](https://github.com/dataforseo/mcp-server-typescript)
3. [DataForSEO MCP Server (Community)](https://github.com/Skobyn/dataforseo-mcp-server)
4. [DataForSEO Pricing](https://dataforseo.com/pricing)
5. [Semrush MCP Server](https://github.com/metehan777/semrush-mcp)
6. [Keywords Everywhere MCP](https://github.com/hithereiamaliff/mcp-keywords-everywhere)
7. [SEO-MCP Free Ahrefs](https://github.com/cnych/seo-mcp)
8. [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server)
9. [Firecrawl MCP Docs](https://docs.firecrawl.dev/mcp-server)
10. [Crawl4AI MCP Server](https://github.com/sadiuysal/crawl4ai-mcp-server)
11. [mcp-server-reddit (Hawstein)](https://github.com/Hawstein/mcp-server-reddit)
12. [twitter-mcp (EnesCinr)](https://github.com/EnesCinr/twitter-mcp)
13. [fal.ai MCP Server](https://github.com/el-el-san/fal-mcp-server)
14. [fal.ai Pricing](https://fal.ai/pricing)
15. [Together AI MCP](https://github.com/manascb1344/together-mcp-server)
16. [Resend MCP (Official)](https://github.com/resend/mcp-send-email)
17. [Resend MCP (Comprehensive)](https://github.com/PSU3D0/resend-mcp)
18. [Resend Pricing](https://resend.com/pricing)
19. [SendGrid MCP (Garoth)](https://github.com/Garoth/sendgrid-mcp)
20. [Perplexity MCP (Official)](https://github.com/perplexityai/modelcontextprotocol)
21. [Perplexity MCP Docs](https://docs.perplexity.ai/guides/mcp-server)
22. [mcp-youtube (anaisbetts)](https://github.com/anaisbetts/mcp-youtube)
23. [youtube-data-mcp-server](https://github.com/icraft2170/youtube-data-mcp-server)
24. [awesome-mcp-servers (GitHub)](https://github.com/punkpeye/awesome-mcp-servers)
25. [PulseMCP Directory](https://www.pulsemcp.com/servers)
26. [mcp.so Directory](https://mcp.so/)
27. [mcp-awesome.com](https://mcp-awesome.com/)
28. [mcpservers.org](https://mcpservers.org/)
29. [Ahrefs API Pricing](https://ahrefs.com/api/pricing)
30. [Perplexity API Pricing](https://docs.perplexity.ai/getting-started/pricing)

## Open Questions

- Crawl4AI MCP: Need to test if the MCP server can connect to the existing Crawl4AI Docker instance at :11235 or if it needs its own.
- Reddit API access: Long-term viability uncertain given Reddit's December 2025 API restrictions.
- Twitter/X: The free API tier may be too limited for a production marketing platform. Need to evaluate Basic ($100/mo) vs alternatives.
- Resend vs SendGrid: Resend has a more generous free tier (3K/mo vs 100/day) and a simpler API. SendGrid MCP has more marketing-specific tools.
