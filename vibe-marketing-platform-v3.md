# Vibe Marketing Platform — V3 Architecture
## Claude Code Agent Squad + Self-Hosted Convex + Skill-Driven Orchestration

> **A standalone, omnipotent AI marketing automation platform.** One Claude Max subscription ($200/mo), Claude Code in `--dangerously-skip-permissions` mode, 30+ agent skills, self-hosted Convex as the single database, configurable Service Registry for all external APIs, hierarchical Project → Product → Audience → Campaign data model, custom email/password auth, Netflix-style project selector, and a Vue dashboard for full control. Inspired by Mission Control (pbteja1998), purpose-built for marketing at scale.

---

## Table of Contents

1. [Core Architecture Overview](#1-core-architecture-overview)
2. [Infrastructure Stack](#2-infrastructure-stack)
3. [Data Model — The Hierarchy](#3-data-model--the-hierarchy)
4. [Service Registry System](#4-service-registry-system)
5. [Project Structure](#5-project-structure)
6. [The CLAUDE.md Master File](#6-the-claudemd-master-file)
7. [MCP Server Configuration](#7-mcp-server-configuration)
8. [Self-Hosted Convex Setup & Schema](#8-self-hosted-convex-setup--schema)
9. [Agent Architecture — Skills-First Design](#9-agent-architecture--skills-first-design)
10. [Audience Intelligence System](#10-audience-intelligence-system)
11. [Individual Agent Skill Specifications](#11-individual-agent-skill-specifications)
12. [The Orchestrator (vibe-orchestrator) — Heartbeat & Dispatch](#12-the-orchestrator-vibe-orchestrator--heartbeat--dispatch)
13. [Memory & Persistence System](#13-memory--persistence-system)
14. [Human-in-the-Loop & Approval System](#14-human-in-the-loop--approval-system)
15. [Dashboard — Vue + Convex](#15-dashboard--vue--convex)
16. [External Tool Integration Scripts](#16-external-tool-integration-scripts)
17. [Cost Analysis](#17-cost-analysis)
18. [Implementation Roadmap](#18-implementation-roadmap)

---

## 1. Core Architecture Overview

### Philosophy

- **Standalone platform** — not tied to any specific CMS. Publishes to any CMS via configurable API. Can integrate with BusinessPress, WordPress, Ghost, Webflow, or anything else later.
- **Fixed cost** — Claude Max $200/mo. More content = lower per-piece cost. No token anxiety.
- **Skills, not prompts** — Each agent is a full skill directory (SKILL.md + executable scripts + reference docs + sub-agents). Not a system prompt pasted into a database field.
- **Configurable everything** — Which APIs to use, which image generator, which SEO tool — all managed through a Service Registry in the dashboard. Agents read the registry and route to the active service.
- **Research once, use everywhere** — Product context, brand voice, and audience focus groups live at the product level. Campaigns reference them. Agents never waste time re-researching what's already known.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HETZNER VPS (Ubuntu 24)                            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      ~/vibe-marketing/                                │  │
│  │                                                                       │  │
│  │   CLAUDE.md          .mcp.json          .claude/skills/ (30+ agents) │  │
│  │   memory/            projects/          scripts/                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────┐  ┌────────────────────────────────────────────┐   │
│  │  Self-Hosted Convex  │  │  Mission Control Dashboard (Vue 3)        │   │
│  │  (Docker)            │  │  (Nuxt 3 + Convex + Tailwind)             │   │
│  │                      │  │                                            │   │
│  │  ALL data lives here │  │  Auth:                                     │   │
│  │  - Users & Sessions  │  │  - Login (email/password)                  │   │
│  │  - Projects          │  │  - Session cookie                          │   │
│  │  - Products          │  │                                            │   │
│  │  - Focus Groups      │  │  Pages:                                    │   │
│  │  - Campaigns         │  │  - Project Selector (Netflix-style cards)  │   │
│  │  - Tasks & Pipeline  │  │  - Project Dashboard                      │   │
│  │  - Agent Coordination│  │  - Products & Audiences                   │   │
│  │  - Content Metadata  │  │  - Campaigns                              │   │
│  │  - Service Registry  │  │  - Content Pipeline (kanban)              │   │
│  │  - Analytics         │  │  - Review Queue                           │   │
│  │  Port 3210           │  │  - Agent Status (global)                  │   │
│  └─────────────────────┘  │  - Service Registry (settings, global)     │   │
│                            │  - Analytics & Reports                    │   │
│                            │  Port 3000                                │   │
│                            └────────────────────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       CRON / PM2 / SYSTEMD                            │  │
│  │                                                                       │  │
│  │  Agent heartbeats (staggered cron jobs invoking Claude Code)          │  │
│  │  Notification daemon (delivers @mentions to agents)                   │  │
│  │  Registry sync (writes SERVICE_REGISTRY.md from Convex on change)    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Execution Model

Each agent runs as a **Claude Code CLI invocation** via cron:

```bash
# Generic invocation
cd ~/vibe-marketing && claude --dangerously-skip-permissions \
  --print \
  --model sonnet \
  "You are vibe-keyword-researcher. Read .claude/skills/keyword-research-procedures/SKILL.md, then execute your heartbeat protocol."
```

Agents wake up → read SKILL.md → read WORKING memory → check Convex for tasks/@mentions → do work → update state → exit. Non-interactive. Cost-efficient.

### Model Selection

| Model | Use For | Agents |
|-------|---------|--------|
| **Haiku** | Heartbeat checks, deterministic operations, simple queries | vibe-orchestrator, vibe-image-generator, vibe-video-generator |
| **Sonnet** | 90% of content creation, research, analysis | vibe-content-writer, vibe-content-reviewer, vibe-social-writer, vibe-email-writer, all routine creative |
| **Opus** | High-stakes: landing pages, ebooks, complex strategy, humanization | vibe-humanizer, vibe-landing-page-writer, vibe-ebook-writer, vibe-ad-writer, vibe-audience-researcher |

---

## 2. Infrastructure Stack

### Server

- **Hetzner Bare Metal** — 16 cores, 32 threads, 128GB RAM — ~€100/mo
- **OS**: Ubuntu 24.04 LTS

### Core Software

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | latest | Agent runtime (`npm i -g @anthropic-ai/claude-code`) |
| Self-hosted Convex | latest | Single database for everything |
| PostgreSQL 17 | 17.x | Convex backing store (Convex runs on top of it) |
| Node.js | 22 LTS | Convex functions, dashboard, scripts |
| Docker + Compose | latest | Convex containers |
| PM2 | latest | Process management (dashboard, notification daemon) |
| Caddy | latest | Reverse proxy + auto HTTPS |
| Python | 3.12+ | Agent utility scripts |

### Single Database: Self-Hosted Convex

**Convex is the ONLY database.** No separate PostgreSQL management. Convex self-hosted runs on PostgreSQL 17 internally, but you interact exclusively through Convex's TypeScript API. This gives you:

- Real-time reactivity (dashboard auto-updates)
- TypeScript type safety
- One query language, one API
- Built-in scheduling and background jobs
- Simpler stack, less to maintain

If analytics/reporting ever outgrow Convex, PostgreSQL can be added later as a dedicated analytics warehouse. But start simple.

---

## 3. Data Model — The Hierarchy

This is the core design decision. Everything flows from this hierarchy:

```
Platform (global)
├── Users & Auth                  ← Email/password login, sessions, roles
├── Service Registry              ← Which APIs/tools are active, keys, priorities
├── Pipelines                     ← Assembly line blueprints (global, project-agnostic)
├── Agents                        ← Global workers serving all projects
│
└── Projects                      ← Top-level grouping entity
    ├── GymZilla                  ← One business/venture = one project
    │   ├── Products
    │   │   ├── GymZilla App
    │   │   │   ├── Product Context       ← What it is, pricing, features, USPs
    │   │   │   ├── Brand Voice           ← Tone, style, vocabulary
    │   │   │   └── Focus Groups          ← 28 audience segments
    │   │   │       ├── #1 Fat Loss Seekers
    │   │   │       │   ├── Demographics
    │   │   │       │   ├── Psychographics
    │   │   │       │   ├── Core Desires
    │   │   │       │   ├── Pain Points
    │   │   │       │   ├── Fears & Beliefs
    │   │   │       │   ├── Objections
    │   │   │       │   ├── Emotional Triggers
    │   │   │       │   ├── Language Patterns
    │   │   │       │   ├── Marketing Hooks
    │   │   │       │   └── Transformation Promise
    │   │   │       ├── #2 Muscle Builders
    │   │   │       └── ... (28 total)
    │   │   │
    │   │   └── GymZilla Coaching
    │   │       ├── Product Context
    │   │       ├── Brand Voice
    │   │       └── Focus Groups (different segments)
    │   │
    │   ├── Campaigns
    │   │   ├── "Summer Shred Launch"
    │   │   │   ├── Product: GymZilla App
    │   │   │   ├── Pipeline: "Full Content Production" (frozen snapshot)
    │   │   │   ├── Target Focus Groups: #1, #3, #5
    │   │   │   ├── Seed Keywords
    │   │   │   ├── Competitors (for this angle)
    │   │   │   └── Folder: projects/gymzilla/campaigns/summer-shred/
    │   │   │
    │   │   └── "Beginner Series"
    │   │       ├── Product: GymZilla App
    │   │       ├── Pipeline: "Launch Package" (everything)
    │   │       ├── Target Focus Groups: #11, #13, #14
    │   │       └── ...
    │   │
    │   └── Documents, Media, Reports, Activities
    │
    └── Photo Prints               ← Another project
        ├── Products
        │   └── Photo Printing Biz
        │       ├── Product Context
        │       ├── Brand Voice
        │       └── Focus Groups
        ├── Campaigns
        │   └── "Valentine's Day Push"
        │       ├── Product: Photo Printing Biz
        │       ├── Pipeline: "Content Draft" (no images/social)
        │       ├── Target Focus Groups: #2 Couples, #5 Gift Buyers
        │       └── ...
        └── ...
```

### Why This Matters

When **vibe-keyword-researcher** researches keywords for the "Summer Shred" campaign, it reads:
1. GymZilla's product context (what we sell)
2. Focus groups #1, #3, #5 (who we're targeting)
3. Their specific **language patterns** to find keyword opportunities
4. Their specific **pain points** to identify content gaps

When **vibe-content-writer** writes an article for that campaign:
1. Same product context
2. Uses the focus groups' **emotional triggers** and **core desires** in the hook
3. Addresses their specific **objections** naturally in the copy
4. Writes in the tone defined by GymZilla's brand voice
5. Uses **marketing hooks** from the focus group profiles as subheading inspiration

When **AdCopy** writes ads:
1. Uses **language patterns** (exact phrases the audience uses) as ad copy
2. Pre-handles **common objections** in the ad
3. Leads with the **transformation promise**

**Research done ONCE. Used by every agent, every campaign targeting those groups.** No wasted cycles rediscovering what you already know.

### Deliverables (Per Campaign — Driven by Pipeline)

What a campaign produces is defined by its **pipeline selection** (which agents run) plus its **deliverable config** (which parallel outputs to generate). Example:

```
Campaign: GymZilla Summer Shred
Pipeline: "Full Content Production"

  Main pipeline outputs (sequential):
    ✅ Keyword research → campaigns/summer-shred/research/
    ✅ Content briefs → campaigns/summer-shred/briefs/
    ✅ Articles (2000+ words) → campaigns/summer-shred/final/
    
  Parallel deliverables (per article):
    ✅ Hero image (vibe-image-director) → campaigns/summer-shred/assets/images/
    ✅ Social posts: X, LinkedIn, Instagram → campaigns/summer-shred/assets/social/
    ✅ Email newsletter excerpt → campaigns/summer-shred/assets/email/
    ❌ Video script (not for this campaign)

  Per-campaign deliverables (via Launch Package pipeline):
    ❌ Landing page (would need Launch Package pipeline)
    ❌ Email sequence (would need Launch Package pipeline)
    ❌ Ad copy set (would need Launch Package pipeline)
```

The pipeline defines which agents run. The deliverable config on the campaign toggles which parallel branches actually fire. Both are set during campaign creation and frozen as snapshots.

---

## 4. Service Registry System

### The Problem

Agents need to use external services (SEO data, image generation, web scraping, social APIs, email sending, CMS publishing). But:
- You might switch from DataForSEO to Ahrefs
- You might use FLUX for hero images but Ideogram for text-in-image graphics
- You might not have a video generation API yet
- Some services have different use cases within the same category

Agents can't have this hardcoded. It needs to be configurable from the dashboard.

### Service Registry Data Model

```typescript
// In Convex schema
serviceCategories: defineTable({
  name: v.string(),              // "seo_keywords", "image_generation", "web_scraping"
  displayName: v.string(),       // "SEO & Keywords", "Image Generation"
  description: v.string(),
  icon: v.string(),              // Dashboard icon
}),

services: defineTable({
  categoryId: v.id("serviceCategories"),
  name: v.string(),              // "dataforseo", "flux_pro", "firecrawl"
  displayName: v.string(),       // "DataForSEO", "FLUX Pro (fal.ai)"
  description: v.string(),       // What it's best for
  isActive: v.boolean(),
  priority: v.number(),          // 1 = highest priority in category
  apiKeyField: v.string(),       // ENV var name: "DATAFORSEO_LOGIN"
  apiKeySet: v.boolean(),        // Whether the key is configured
  configJson: v.optional(v.string()), // Extra config (endpoints, models, etc.)
  costInfo: v.string(),          // "$0.05/image", "$50/mo min deposit"
  useCases: v.array(v.string()), // ["hero_images", "product_photos"]
  scriptPath: v.string(),        // Path to the wrapper script
  mcpServer: v.optional(v.string()), // MCP server name if applicable
  docs: v.optional(v.string()),  // URL to API docs
}).index("by_category", ["categoryId"])
  .index("by_active", ["isActive"]),
```

### Service Categories & Initial Services

```
SEO & Keywords
├── 1. DataForSEO          [$50 min deposit, pay-as-go]     scripts: query_dataforseo.py
├── 2. Ahrefs API          [$129+/mo subscription]           scripts: query_ahrefs.py
├── 3. SEMrush API         [$139+/mo subscription]           scripts: query_semrush.py
├── 4. Google Keyword Plan [Free via Google Ads API]         scripts: query_gkp.py
└── 5. AnswerThePublic     [Free tier / $9+/mo]              scripts: query_atp.py

SERP & Rank Tracking
├── 1. DataForSEO SERP     [included in DataForSEO]         scripts: query_serp.py
├── 2. Google Search Console [Free]                          scripts: query_gsc.py
└── 3. Bing Webmaster      [Free]                            scripts: query_bing.py

Web Scraping
├── 1. Firecrawl           [$19+/mo, LLM-ready markdown]    mcp: firecrawl
├── 2. Crawl4AI            [Free, self-hosted]               scripts: crawl4ai.py
├── 3. Apify               [Pay-as-go, 2000+ actors]         scripts: apify_scrape.py
└── 4. ScraperAPI          [$49+/mo, CAPTCHA handling]       scripts: scraper_api.py

Social Platform Scraping
├── X / Twitter
│   ├── 1. X API v2        [Free Essential / $100 Basic]     scripts: x_api.py
│   ├── 2. ScrapeCreators  [$10/5K credits]                  scripts: scrapecreators_x.py
│   └── 3. Apify X Actor   [Pay-as-go]                       scripts: apify_x.py
├── Reddit
│   ├── 1. Reddit API      [Free with rate limits]           scripts: reddit_api.py
│   └── 2. ScrapeCreators  [$10/5K credits]                  scripts: scrapecreators_reddit.py
├── LinkedIn
│   ├── 1. PhantomBuster   [$69+/mo]                         scripts: phantombuster_li.py
│   └── 2. ProxyCurl       [Pay-as-go]                       scripts: proxycurl.py
├── Facebook / Instagram
│   ├── 1. Graph API       [Free, official]                  scripts: meta_graph.py
│   └── 2. Apify Actors    [Pay-as-go]                       scripts: apify_meta.py
├── TikTok
│   ├── 1. TikTok API      [Limited official]                scripts: tiktok_api.py
│   └── 2. ScrapeCreators  [$10/5K credits]                  scripts: scrapecreators_tt.py
├── YouTube
│   ├── 1. YouTube Data v3 [Free quota]                      scripts: youtube_api.py
│   └── 2. Apify Actors    [Pay-as-go]                       scripts: apify_yt.py
└── VK
    └── 1. VK API          [Free, generous]                  scripts: vk_api.py

Image Generation
├── 1. FLUX Pro (fal.ai)   [$0.05-0.10/img]  use: hero images, product shots
├── 2. FLUX Schnell        [$0.003/img]       use: quick drafts, thumbnails
├── 3. Ideogram 3.0        [$7-20/mo]         use: text-in-images, infographics
├── 4. DALL-E 3            [$0.04-0.08/img]   use: general purpose
├── 5. Midjourney (ImagineAPI) [$10-30/mo]    use: artistic, brand imagery
├── 6. Leonardo.ai         [Free tier + $10+] use: character consistency
├── 7. Recraft V3          [API access]       use: vector, icon generation
└── 8. Google Imagen 4     [Vertex AI]        use: photorealism

Templated Image Generation (social graphics, banners)
├── 1. Bannerbear          [$49+/mo]          use: templated social images
└── 2. Placid              [$29+/mo]          use: templated OG images, banners

Video Generation
├── 1. Runway Gen-4        [$12-76/mo]        use: hero/ad videos, 4K
├── 2. Kling AI 2.1        [Budget-friendly]  use: volume social clips
├── 3. Pika Labs 2.0       [Free + $8/mo]     use: short social content
├── 4. Google Veo 3        [Vertex AI]        use: cinematic, with audio
├── 5. Sora 2              [OpenAI API]       use: narrative
├── 6. HeyGen              [$18+/mo]          use: AI presenter/explainer
└── 7. Synthesia           [$24+/mo]          use: professional presenter

AI Presenter / Talking Head
├── 1. HeyGen              [$18+/mo]
├── 2. Synthesia           [$24+/mo]
└── 3. D-ID                [Pay-as-go]

Email Sending
├── 1. SendGrid            [Free 100/day]     scripts: sendgrid.py
├── 2. Mailgun             [Free 100/day]     scripts: mailgun.py
├── 3. Brevo (Sendinblue)  [Free 300/day]     scripts: brevo.py
├── 4. Mailchimp           [Free tier]        scripts: mailchimp.py
└── 5. ConvertKit          [$29+/mo]          scripts: convertkit.py

Social Publishing
├── 1. Buffer              [Free + $6+/ch]    scripts: buffer_post.py
├── 2. X API v2 (direct)   [Free]             scripts: x_post.py
├── 3. LinkedIn API        [Free]             scripts: linkedin_post.py
├── 4. Facebook Graph API  [Free]             scripts: facebook_post.py
├── 5. Instagram Graph API [Free]             scripts: instagram_post.py
├── 6. Pinterest API       [Free]             scripts: pinterest_post.py
├── 7. TikTok API          [Limited]          scripts: tiktok_post.py
└── 8. VK API              [Free]             scripts: vk_post.py

CMS Publishing
├── 1. WordPress REST API  [Free]             scripts: wp_publish.py
├── 2. Ghost API           [Free]             scripts: ghost_publish.py
├── 3. Webflow CMS API     [Paid plan]        scripts: webflow_publish.py
├── 4. Custom REST API     [Configurable URL] scripts: custom_cms.py
└── 5. Static (markdown)   [Free]             scripts: static_publish.py

Content Quality
├── 1. Copyscape           [$0.03/check]      scripts: copyscape.py
├── 2. Copyleaks           [$9.16+/mo]        scripts: copyleaks.py
└── 3. LanguageTool        [Free tier]        scripts: languagetool.py

Web Search (for agents)
├── 1. Brave Search API    [Free tier]        mcp: brave-search
├── 2. Google Custom Search [Free 100/day]    scripts: google_search.py
└── 3. Perplexity API      [$0.20/1K queries] scripts: perplexity.py

Analytics & Tracking
├── 1. Google Search Console [Free]           scripts: gsc_analytics.py
├── 2. Google Analytics 4  [Free]             scripts: ga4_analytics.py
├── 3. Plausible           [Self-hosted/paid] scripts: plausible.py
└── 4. Umami               [Self-hosted/free] scripts: umami.py

Document Generation
├── 1. Pandoc              [Free, installed]  use: md→html, md→docx, md→pdf
├── 2. Calibre             [Free, installed]  use: epub/mobi generation
└── 3. Puppeteer/Playwright [Free]            use: html→pdf, screenshots

Notifications
├── 1. Telegram Bot API    [Free]             scripts: telegram_notify.py
├── 2. Discord Webhook     [Free]             scripts: discord_notify.py
└── 3. Slack Webhook       [Free]             scripts: slack_notify.py
```

### How Agents Use the Registry

The Service Registry lives in Convex. A daemon process watches for changes and writes a snapshot to disk:

**`memory/long-term/SERVICE_REGISTRY.md`** — Auto-generated, never hand-edited:

```markdown
# Service Registry (auto-generated — do not edit manually)
# Last updated: 2026-02-10T14:30:00Z

## SEO & Keywords
1. **dataforseo** [ACTIVE] — DataForSEO API
   Script: scripts/services/seo/query_dataforseo.py
   Config: location_code=2840, language=en
   
## Web Scraping
1. **firecrawl** [ACTIVE] — Firecrawl (LLM-ready markdown)
   MCP: firecrawl
   
## Image Generation  
1. **flux_pro** [ACTIVE] — FLUX Pro via fal.ai
   Script: scripts/services/images/flux_generate.py
   Use cases: hero_images, product_shots
2. **ideogram** [ACTIVE] — Ideogram 3.0
   Script: scripts/services/images/ideogram_generate.py
   Use cases: text_in_images, infographics, social_graphics

## Video Generation
(no active services)

## Social Scraping > X/Twitter
1. **x_api_v2** [ACTIVE] — X API v2 (Essential tier)
   Script: scripts/services/social/x_api.py

## Social Scraping > Reddit
1. **reddit_api** [ACTIVE] — Reddit Official API
   Script: scripts/services/social/reddit_api.py

## Email Sending
1. **sendgrid** [ACTIVE] — SendGrid (free tier)
   Script: scripts/services/email/sendgrid.py

## CMS Publishing
(no active services — manual export for now)

## Content Quality
1. **copyscape** [ACTIVE] — Copyscape API
   Script: scripts/services/quality/copyscape.py

## Notifications
1. **telegram** [ACTIVE] — Telegram Bot API
   Script: scripts/services/notifications/telegram_notify.py
```

Every agent's SKILL.md includes this instruction:

```
When you need an external service, read memory/long-term/SERVICE_REGISTRY.md.
Find the relevant category. Use the highest-priority ACTIVE service.
Run the script listed for that service. If the script fails, try the next
priority service in the same category. If no services are active in a
category, log a warning and skip that operation.
```

### Service Resolution Script

```python
#!/usr/bin/env python3
# scripts/resolve_service.py
# Usage: python resolve_service.py <category> [use_case]
# Returns the script path and config for the best matching active service.
#
# Example:
#   python resolve_service.py image_generation hero_images
#   → scripts/services/images/flux_generate.py

import json
import subprocess
import sys

def get_active_services(category, use_case=None):
    """Query Convex for active services in a category, sorted by priority"""
    result = subprocess.run(
        ["npx", "convex", "run", "services:getActiveByCategory",
         json.dumps({"category": category, "useCase": use_case}),
         "--url", "http://localhost:3210"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        return json.loads(result.stdout)
    return []

if __name__ == "__main__":
    category = sys.argv[1]
    use_case = sys.argv[2] if len(sys.argv) > 2 else None
    services = get_active_services(category, use_case)
    
    if not services:
        print(json.dumps({"error": f"No active services for {category}"}))
        sys.exit(1)
    
    best = services[0]
    print(json.dumps({
        "name": best["name"],
        "script": best["scriptPath"],
        "config": json.loads(best.get("configJson", "{}") or "{}"),
        "mcp": best.get("mcpServer"),
    }))
```

Agents can call this directly: `python scripts/resolve_service.py image_generation hero_images` and get back the right script to run.

### Dashboard: Service Registry Page

The Settings → Service Registry page in the dashboard shows:

- **Category tabs** across the top (SEO, Scraping, Images, Video, Email, etc.)
- Per category: **card grid** of all available services
  - Each card shows: service name, description, cost info, status toggle (active/inactive)
  - Drag-and-drop to reorder priority
  - "Configure" button opens a modal:
    - API key fields (stored in Convex, encrypted)
    - Extra config (JSON or form fields)
    - Use case tags (which sub-tasks this service handles)
    - "Test Connection" button that runs a quick API check
- **Active summary** at the top: "4 of 12 image services active, 2 of 5 SEO services active"
- When you toggle a service or change priority, the registry daemon auto-regenerates `SERVICE_REGISTRY.md`

---

## 5. Project Structure

```
~/vibe-marketing/                              ← Project root
├── CLAUDE.md                                  ← Master project instructions
├── .mcp.json                                  ← MCP server configuration
├── .claude/
│   ├── skills/                                ← KNOWLEDGE packages (what Claude knows)
│   │   │                                      ← Skills = instructions, references, scripts
│   │   │                                      ← Loaded on-demand via progressive disclosure
│   │   │                                      ← Multiple skills can activate simultaneously
│   │   │
│   │   ├── keyword-research-procedures/        ← How to do keyword research
│   │   │   ├── SKILL.md                       ← Step-by-step research methodology
│   │   │   ├── scripts/
│   │   │   │   ├── query_keywords.py          ← Calls resolve_service.py → SEO API
│   │   │   │   ├── analyze_serp.py
│   │   │   │   └── build_brief.py
│   │   │   └── references/
│   │   │       ├── keyword-strategy.md
│   │   │       └── brief-template.md
│   │   ├── content-writing-procedures/        ← How to write articles
│   │   │   ├── SKILL.md
│   │   │   ├── scripts/
│   │   │   │   ├── check_readability.py
│   │   │   │   ├── check_keyword_density.py
│   │   │   │   └── format_article.py
│   │   │   └── references/
│   │   │       ├── content-frameworks.md      ← AIDA, PAS, BAB, etc.
│   │   │       └── seo-on-page-checklist.md
│   │   ├── content-review-procedures/         ← How to review content
│   │   ├── orchestrator-procedures/           ← Orchestration + safety net logic
│   │   ├── audience-analysis-procedures/      ← How to parse/generate audiences
│   │   ├── audience-research-procedures/      ← How to research from scratch
│   │   ├── audience-enrichment-procedures/    ← How to enrich existing data
│   │   ├── social-writing-procedures/         ← Social post creation
│   │   ├── email-writing-procedures/          ← Email sequence writing
│   │   ├── landing-page-procedures/           ← Landing page copy
│   │   ├── ebook-procedures/                  ← Ebook creation
│   │   ├── ad-copy-procedures/                ← Ad writing
│   │   ├── competitor-procedures/             ← Competitor intelligence
│   │   ├── image-direction-procedures/        ← Image prompt engineering
│   │   │
│   │   ├── humanizer/                         ← FROM skills.sh — AI pattern detection
│   │   │   └── SKILL.md                       ← 16 pattern categories (Wikipedia-grade)
│   │   ├── marketing-psychology/              ← FROM skills.sh — 40+ mental models
│   │   │   └── SKILL.md
│   │   ├── referral-program/                  ← FROM skills.sh — referral design
│   │   │   └── SKILL.md
│   │   ├── claim-investigation/               ← FROM skills.sh — 7-phase fact-checking
│   │   │   └── SKILL.md
│   │   ├── ebook-analysis/                    ← FROM skills.sh — knowledge extraction
│   │   │   └── SKILL.md
│   │   ├── presentation-design/               ← FROM skills.sh — slide generation
│   │   │   └── SKILL.md
│   │   └── web-artifacts-builder/             ← FROM skills.sh — React artifact bundler
│   │       ├── SKILL.md
│   │       └── scripts/
│   │           ├── init-artifact.sh
│   │           └── bundle-artifact.sh
│   │
│   ├── agents/                                ← WORKERS (separate Claude instances)
│   │   │                                      ← Agents = identity + model + tools + personality
│   │   │                                      ← Each runs in its OWN context window
│   │   │                                      ← Agents LOAD skills as needed
│   │   │
│   │   ├── vibe-orchestrator.md               ← Pipeline orchestration (haiku, Bash/Read)
│   │   ├── vibe-keyword-researcher.md         ← Keyword research + briefs (sonnet, Bash/Read/Write)
│   │   ├── vibe-content-writer.md             ← Article writing (sonnet, Read/Write/Edit)
│   │   ├── vibe-content-reviewer.md           ← Quality review (sonnet, Read/Write)
│   │   ├── vibe-humanizer.md                  ← AI pattern breaking (opus, Read/Write/Edit)
│   │   ├── vibe-audience-parser.md            ← Document parser (sonnet, Read/Write/Bash)
│   │   ├── vibe-audience-researcher.md        ← Audience generator (opus, all tools)
│   │   ├── vibe-audience-enricher.md          ← Profile updater (sonnet, Read/Write/Bash)
│   │   ├── vibe-competitor-analyst.md         ← Competitor intel (sonnet, Bash/Read/Write)
│   │   ├── vibe-brand-monitor.md              ← Brand monitoring (sonnet, Bash/Read/Write)
│   │   ├── vibe-reddit-scout.md               ← Reddit scout (sonnet, Bash/Read/Write)
│   │   ├── vibe-twitter-scout.md              ← X/Twitter scout (sonnet, Bash/Read/Write)
│   │   ├── vibe-linkedin-scout.md             ← LinkedIn scout (sonnet, Bash/Read/Write)
│   │   ├── vibe-trend-detector.md             ← Trend detection (sonnet, Bash/Read)
│   │   ├── vibe-review-harvester.md           ← Review analyzer (sonnet, Bash/Read/Write)
│   │   ├── vibe-keyword-deep-researcher.md    ← Deep keyword research (sonnet, Bash/Read/Write)
│   │   ├── vibe-serp-analyzer.md              ← SERP analysis (sonnet, Bash/Read/Write)
│   │   ├── vibe-seo-auditor.md                ← SEO audit (sonnet, Bash/Read/Write)
│   │   ├── vibe-landing-page-writer.md        ← Landing pages (opus, Read/Write/Edit)
│   │   ├── vibe-email-writer.md               ← Email sequences (sonnet, Read/Write)
│   │   ├── vibe-social-writer.md              ← Social posts (sonnet, Read/Write)
│   │   ├── vibe-script-writer.md              ← Video scripts (sonnet, Read/Write)
│   │   ├── vibe-ebook-writer.md               ← Ebooks (opus, all tools)
│   │   ├── vibe-content-repurposer.md         ← Content multiplication (sonnet, Read/Write)
│   │   ├── vibe-ad-writer.md                  ← Advertising (sonnet, Read/Write)
│   │   ├── vibe-press-writer.md               ← PR/press (sonnet, Read/Write)
│   │   ├── vibe-fact-checker.md               ← Accuracy (sonnet, Read/Bash)
│   │   ├── vibe-plagiarism-checker.md         ← Copyscape (haiku, Bash/Read)
│   │   ├── vibe-image-director.md             ← Image prompts (sonnet, Read/Write)
│   │   ├── vibe-image-generator.md            ← Image generation (haiku, Bash/Read/Write)
│   │   ├── vibe-video-generator.md            ← Video generation (haiku, Bash/Read/Write)
│   │   │
│   │   │   # FUTURE (post-MVP):
│   │   │   # ├── vibe-publisher.md             ← CMS auto-publishing (haiku)
│   │   │   # ├── vibe-social-distributor.md    ← Social auto-posting (haiku)
│   │   │   # ├── vibe-email-distributor.md     ← Email dispatch (haiku)
│   │   │   # ├── vibe-analytics-reporter.md    ← Performance analytics (sonnet)
│   │   │   # ├── vibe-rank-tracker.md          ← Keyword positions (haiku)
│   │   │   # ├── vibe-content-refresher.md     ← Content decay detection (sonnet)
│   │   │   # └── vibe-roi-calculator.md        ← Cost/revenue attribution (sonnet)
│   │   │
│   │   └── ... (future agents)
│   │
│   └── commands/                              ← User-initiated slash commands
│       ├── standup.md                         ← /standup → vibe-orchestrator daily report
│       ├── review.md                          ← /review → open review queue
│       ├── new-campaign.md                    ← /new-campaign → campaign wizard
│       ├── research-audience.md               ← /research-audience → vibe-audience-researcher
│       └── pipeline-status.md                 ← /pipeline-status → show pipeline health
├── convex/                                    ← Convex schema & functions
│   ├── schema.ts                              ← Full schema definition
│   ├── auth.ts                                ← signIn, signOut, validateSession, me
│   ├── admin.ts                               ← createUser (internal action, bcrypt)
│   ├── projects.ts                            ← Project CRUD, updateStats
│   ├── products.ts                            ← Product CRUD
│   ├── focusGroups.ts                         ← Focus group CRUD
│   ├── campaigns.ts                           ← Campaign CRUD
│   ├── tasks.ts                               ← Task management
│   ├── content.ts                             ← Content pipeline
│   ├── agents.ts                              ← Agent coordination
│   ├── messages.ts                            ← Inter-agent messages
│   ├── activities.ts                          ← Activity feed
│   ├── notifications.ts                       ← @mention system
│   ├── services.ts                            ← Service registry CRUD
│   └── analytics.ts                           ← Analytics/reports
├── dashboard/                                 ← Vue 3 / Nuxt 3 dashboard
│   ├── nuxt.config.ts
│   ├── middleware/
│   │   └── auth.ts                            ← Session cookie check on every route
│   ├── composables/
│   │   ├── useAuth.ts                         ← Login/logout, session, current user
│   │   ├── useCurrentProject.ts               ← Derives projectId from route slug
│   │   └── useConvex.ts                       ← Convex query/mutation helpers
│   ├── pages/
│   │   ├── login.vue                          ← Email/password login
│   │   ├── index.vue                          ← Netflix-style project selector
│   │   ├── projects/
│   │   │   ├── new.vue                        ← Create new project
│   │   │   └── [slug]/
│   │   │       ├── index.vue                  ← Project dashboard
│   │   │       ├── products/
│   │   │       │   ├── index.vue              ← Product list
│   │   │       │   ├── new.vue                ← Create product wizard
│   │   │       │   └── [id]/
│   │   │       │       ├── index.vue          ← Product detail
│   │   │       │       └── audiences/
│   │   │       │           ├── index.vue      ← Focus group list
│   │   │       │           ├── [fgId].vue     ← Focus group detail/edit
│   │   │       │           ├── import.vue     ← Upload document → parse
│   │   │       │           └── research.vue   ← Generate from scratch
│   │   │       ├── campaigns/
│   │   │       │   ├── index.vue              ← Campaign list
│   │   │       │   ├── new.vue                ← Campaign creation wizard
│   │   │       │   └── [id]/
│   │   │       │       ├── index.vue          ← Campaign detail
│   │   │       │       └── review.vue         ← Post-pipeline review
│   │   │       ├── pipeline/
│   │   │       │   └── index.vue              ← Content kanban (project-scoped)
│   │   │       ├── review/
│   │   │       │   └── index.vue              ← Review queue (project-scoped)
│   │   │       ├── artifacts/
│   │   │       │   └── index.vue              ← Artifacts (project-scoped)
│   │   │       ├── analytics/
│   │   │       │   └── index.vue              ← Analytics (project-scoped)
│   │   │       └── settings.vue               ← Project settings (name, icon, archive)
│   │   ├── pipelines/                         ← Global pipeline library
│   │   │   ├── index.vue                      ← Pipeline library (presets + custom)
│   │   │   ├── [id].vue                       ← Pipeline builder (drag-and-drop)
│   │   │   └── new.vue                        ← New pipeline / fork from preset
│   │   ├── agents/
│   │   │   └── index.vue                      ← Agent status grid (global)
│   │   └── settings/                          ← Platform settings (global)
│   │       ├── services.vue                   ← Service Registry
│   │       ├── notifications.vue              ← Telegram/Discord config
│   │       ├── crons.vue                      ← Agent schedule management
│   │       └── general.vue                    ← Platform settings
│   ├── components/
│   └── package.json
├── scripts/                                   ← Shared utility scripts
│   ├── invoke-agent.sh                        ← Agent invocation wrapper
│   ├── setup-crons.sh                         ← Install all cron jobs
│   ├── resolve_service.py                     ← Service registry resolver
│   ├── sync_registry.py                       ← Convex → SERVICE_REGISTRY.md
│   ├── notify.py                              ← Multi-channel notification
│   └── services/                              ← Per-service API wrappers
│       ├── seo/
│       │   ├── query_dataforseo.py
│       │   ├── query_ahrefs.py
│       │   ├── query_gsc.py
│       │   └── query_semrush.py
│       ├── scraping/
│       │   ├── firecrawl_scrape.py
│       │   └── apify_scrape.py
│       ├── social/
│       │   ├── x_api.py
│       │   ├── reddit_api.py
│       │   └── phantombuster_li.py
│       ├── images/
│       │   ├── flux_generate.py
│       │   ├── ideogram_generate.py
│       │   └── dalle_generate.py
│       ├── video/
│       │   ├── runway_generate.py
│       │   └── kling_generate.py
│       ├── email/
│       │   ├── sendgrid.py
│       │   └── mailgun.py
│       ├── publishing/
│       │   ├── wp_publish.py
│       │   ├── ghost_publish.py
│       │   └── custom_cms.py
│       ├── quality/
│       │   ├── copyscape.py
│       │   └── languagetool.py
│       └── notifications/
│           ├── telegram_notify.py
│           └── discord_notify.py
├── projects/                                  ← Per-project data (NEW top-level)
│   ├── gymzilla/                              ← One folder per project (matches slug)
│   │   ├── campaigns/                         ← Campaign output for this project
│   │   │   └── {campaign-slug}/
│   │   │       ├── pipeline.json              ← Pipeline snapshot (frozen at creation)
│   │   │       ├── manifest.json              ← Index of everything produced
│   │   │       ├── research/                  ← Keyword reports, SERP analysis
│   │   │       ├── briefs/                    ← Content briefs
│   │   │       ├── drafts/                    ← Article drafts (working versions)
│   │   │       ├── reviewed/                  ← Post-review versions
│   │   │       ├── final/                     ← Approved, humanized final content
│   │   │       ├── assets/
│   │   │       │   ├── images/                ← Hero images, generated visuals
│   │   │       │   ├── social/                ← Social post content
│   │   │       │   ├── video/                 ← Video scripts/assets
│   │   │       │   └── email/                 ← Email sequences
│   │   │       ├── landing-pages/             ← If pipeline includes landing page agent
│   │   │       ├── ads/                       ← If pipeline includes ad copy agent
│   │   │       ├── artifacts/                 ← Interactive HTML artifacts
│   │   │       └── reports/                   ← Campaign summary, completion report
│   │   ├── memory/                            ← Project-scoped agent memory
│   │   │   ├── WORKING/                       ← Per-agent state for THIS project
│   │   │   │   └── {agent-name}.md
│   │   │   ├── daily/
│   │   │   └── long-term/
│   │   ├── uploads/                           ← User-uploaded docs for this project
│   │   ├── artifacts/                         ← Project-level artifacts
│   │   └── content/research/                  ← Research materials
│   │
│   └── photo-prints/                          ← Another project (same structure)
│       └── (same layout as above)
│
├── memory/                                    ← GLOBAL agent memory (kept)
│   ├── WORKING/                               ← Global agent working state
│   │   ├── vibe-orchestrator.md
│   │   └── ... (one per agent)
│   ├── daily/                                 ← Daily logs
│   │   └── YYYY-MM-DD.md
│   └── long-term/                             ← Persistent knowledge
│       ├── SERVICE_REGISTRY.md                ← Auto-generated from Convex
│       └── LESSONS_LEARNED.md
├── artifacts/                                 ← Platform-level artifacts (global)
│   ├── reports/                               ← Interactive dashboards, analytics
│   └── tools/                                 ← Mini-tools, calculators
├── logs/                                      ← Agent invocation logs
├── docker-compose.yml                         ← Convex + Dashboard
├── package.json
└── .env                                       ← Secrets
```

---

## 6. The CLAUDE.md Master File

Lean, universal, focused. ~120 instructions.

```markdown
# CLAUDE.md — Vibe Marketing Platform

## What This Is
A standalone AI marketing automation platform. 30+ specialized agents
(defined as skills in .claude/skills/) research, create, review, publish,
and analyze marketing content across multiple projects, products, and campaigns.

## Tech Stack
- Runtime: Claude Code (--dangerously-skip-permissions)
- Database: Self-hosted Convex (localhost:3210) — SINGLE database for everything
- Dashboard: Vue 3 / Nuxt 3 (localhost:3000) — email/password auth, session cookies
- Process manager: PM2
- Agent scripts: Python 3.12+ and Bash

## How Agents Work
Each agent is a skill directory in .claude/skills/{agent-name}/.
When invoked, an agent MUST:
1. Read its SKILL.md file first
2. Read memory/WORKING/{agent-name}.md for current state
3. Check Convex for assigned tasks and @mentions (via bash: npx convex run ...)
4. Determine the project context from the task's projectId
5. Execute work according to its skill instructions
6. Update WORKING memory and Convex task status
7. Exit cleanly (non-interactive mode)

## Project Context
All work happens within a project. When working on a task:
1. Get the task's projectId (every task has one)
2. Load the project (Convex: projects:get) — name, slug
3. Use project slug for file paths: projects/{project-slug}/campaigns/{campaign-slug}/
4. Write project-scoped memory to: projects/{project-slug}/memory/WORKING/{agent-name}.md
Global orchestrator state stays in: memory/WORKING/vibe-orchestrator.md

## Convex Access
Interact via CLI: npx convex run <function> '<json>' --url http://localhost:3210
Key functions: tasks:*, messages:*, agents:*, notifications:*,
  content:*, campaigns:*, products:*, focusGroups:*, services:*,
  projects:*, auth:*

## Data Hierarchy
Projects → Products → Focus Groups (audiences) → Campaigns → Tasks → Content
When working on a campaign task:
1. Load campaign details (Convex: campaigns:get) — includes projectId
2. Load the project context (Convex: projects:get)
3. Load the campaign's product context (Convex: products:get)
4. Load the campaign's target focus groups (Convex: focusGroups:getByCampaign)
5. Use focus group data (language patterns, pain points, hooks) in your work

Global entities (no projectId): Pipelines, Agents, Service Registry

## Service Registry
When you need an external service (SEO data, images, scraping, etc.):
1. Read memory/long-term/SERVICE_REGISTRY.md
2. Find the category you need
3. Use the highest-priority ACTIVE service
4. Run the script at the listed path
5. If it fails, try the next priority service in the same category
6. If no services active in category, log warning and skip

## File Conventions
- Project root: projects/{project-slug}/
- Campaign files: projects/{project-slug}/campaigns/{campaign-slug}/
  - Research: .../campaigns/{campaign-slug}/research/
  - Briefs: .../campaigns/{campaign-slug}/briefs/
  - Drafts: .../campaigns/{campaign-slug}/drafts/
  - Reviewed: .../campaigns/{campaign-slug}/reviewed/
  - Final: .../campaigns/{campaign-slug}/final/
  - Images: .../campaigns/{campaign-slug}/assets/images/
  - Social: .../campaigns/{campaign-slug}/assets/social/
  - Email: .../campaigns/{campaign-slug}/assets/email/
  - Artifacts: .../campaigns/{campaign-slug}/artifacts/
- Project memory: projects/{project-slug}/memory/WORKING/{agent-name}.md
- Project uploads: projects/{project-slug}/uploads/
- Global artifacts: artifacts/
- Global agent memory: memory/WORKING/{agent-name}.md
- Daily logs: memory/daily/YYYY-MM-DD.md
- Service registry: memory/long-term/SERVICE_REGISTRY.md
- Shared reference skills: .claude/skills/shared-references/

## Content Pipeline Statuses
backlog → researched → briefed → drafted → reviewed → humanized → completed

## Pipeline Contract
1. ALWAYS acquireLock before starting work — exit if not acquired
2. ALWAYS completeStep as your ABSOLUTE LAST action
3. NEVER update task status directly — only through pipeline:completeStep
4. NEVER auto-post to Reddit/X/LinkedIn — content goes to campaign folder only

## Rules
1. Pipeline runs uninterrupted — no human gates (MVP)
2. NEVER auto-post replies to Reddit/X/LinkedIn — ALWAYS queue for human
3. ALWAYS update memory/WORKING/{agent-name}.md after work
4. ALWAYS log activities to Convex (activities:log)
5. ALWAYS read the campaign's focus groups before creating content
6. ALWAYS check SERVICE_REGISTRY.md before calling any external API
7. Use haiku for heartbeats, sonnet for content, opus for high-stakes
8. Write content in markdown. Conversion happens at publish time.
9. ALWAYS include projectId when creating/querying project-scoped data

## Notification Protocol
To notify another agent:
  npx convex run notifications:create '{"mentionedAgent":"name","content":"msg"}'
Use @all for everyone. Use @human for Telegram notification to owner.

## Error Handling
1. Log error to memory/WORKING/{agent-name}.md
2. Log to Convex: activities:log with type "error"
3. Set task to "blocked" with notes
4. Notify vibe-orchestrator
5. Exit gracefully
```

---

## 7. MCP Server Configuration

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
    }
  }
}
```

**Note on Convex**: No dedicated MCP server needed. Agents access Convex via bash:
```bash
npx convex run tasks:listByAgent '{"agentName":"scout"}' --url http://localhost:3210
```

A thin wrapper at `scripts/cx.sh` simplifies:
```bash
#!/bin/bash
# scripts/cx.sh — Convex CLI shortcut
# Usage: ./scripts/cx.sh tasks:listByAgent '{"agentName":"scout"}'
npx convex run "$1" "$2" --url http://localhost:3210 2>/dev/null
```

Additional MCP servers (like a postgres MCP for direct analytics queries) can be added later as Convex backing-store access if needed.

---

## 8. Self-Hosted Convex Setup & Schema

### Docker Compose

The setup is exactly what Railway's template uses — 3 containers, all on your bare metal:

```yaml
version: '3.8'

services:
  convex-backend:
    image: ghcr.io/get-convex/convex-backend:latest
    ports:
      - "3210:3210"    # Client API
      - "3211:3211"    # Site/HTTP actions
    volumes:
      - convex-data:/convex/data
    environment:
      - DATABASE_URL=postgresql://convex:${CONVEX_DB_PASSWORD}@postgres:5432
      - INSTANCE_NAME=vibe-marketing
      - INSTANCE_SECRET=${CONVEX_INSTANCE_SECRET}
      - CONVEX_CLOUD_ORIGIN=http://localhost:3210
      - CONVEX_SITE_ORIGIN=http://localhost:3211
      - DISABLE_BEACON=true
      - REDACT_LOGS_TO_CLIENT=false
      - DATA_DIR=/convex/data
      - RUST_LOG=info
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  convex-dashboard:
    image: ghcr.io/get-convex/convex-dashboard:latest
    ports:
      - "6791:6791"
    environment:
      - CONVEX_BACKEND_URL=http://convex-backend:3210
    depends_on:
      - convex-backend
    restart: unless-stopped

  postgres:
    image: postgres:17-alpine
    volumes:
      - pg-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${CONVEX_DB_PASSWORD}
      - POSTGRES_DB=convex_self_hosted
      - POSTGRES_USER=convex
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U convex -d convex_self_hosted"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  convex-data:
  pg-data:
```

**How Convex + PostgreSQL works:**

PostgreSQL is Convex's **storage layer** — it replaces the default SQLite. You never interact with PostgreSQL directly. All data access goes through Convex's TypeScript API (`npx convex run ...`). Convex handles schema, indexing, transactions, and real-time subscriptions on top of PG.

On a 128GB RAM / 32-core bare metal Hetzner server, this is trivial. Convex recommends 4GB RAM for production with PG. Co-located PG + Convex on the same machine = ~1ms queries (matching their cloud product performance).

**Initial setup after docker-compose up:**

```bash
# Generate admin key
docker compose exec convex-backend ./generate_admin_key.sh
# Save the output → CONVEX_SELF_HOSTED_ADMIN_KEY in .env

# Set env for CLI
export CONVEX_SELF_HOSTED_URL='http://localhost:3210'
export CONVEX_SELF_HOSTED_ADMIN_KEY='<generated key>'

# Push schema
cd ~/vibe-marketing && npx convex deploy

# Verify
npx convex run --help
```

### Full Convex Schema

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({

  // ═══════════════════════════════════════════
  // USERS & AUTH — Custom email/password auth
  // ═══════════════════════════════════════════

  users: defineTable({
    email: v.string(),
    name: v.string(),
    passwordHash: v.string(),              // bcrypt hash
    role: v.union(
      v.literal("admin"),
      v.literal("editor"),
      v.literal("viewer"),
    ),
    status: v.union(
      v.literal("active"),
      v.literal("disabled"),
    ),
    lastLoginAt: v.optional(v.number()),
  }).index("by_email", ["email"]),

  sessions: defineTable({
    userId: v.id("users"),
    token: v.string(),                     // Random session token (crypto.randomUUID)
    expiresAt: v.number(),                 // Unix timestamp
    userAgent: v.optional(v.string()),
    ip: v.optional(v.string()),
  }).index("by_token", ["token"])
    .index("by_user", ["userId"]),

  // ═══════════════════════════════════════════
  // PROJECTS — Top-level grouping entity
  // ═══════════════════════════════════════════

  projects: defineTable({
    name: v.string(),                        // "GymZilla"
    slug: v.string(),                        // "gymzilla"
    description: v.optional(v.string()),

    // Visual identity for Netflix-style cards
    appearance: v.object({
      icon: v.optional(v.string()),          // Emoji: "🏋️" or icon ref
      color: v.string(),                     // Tailwind color: "emerald", "blue"
      coverImage: v.optional(v.string()),
    }),

    status: v.union(v.literal("active"), v.literal("archived")),

    // Denormalized stats for card display
    stats: v.optional(v.object({
      productCount: v.number(),
      campaignCount: v.number(),
      activeCampaignCount: v.number(),
      taskCount: v.number(),
      completedTaskCount: v.number(),
      lastActivityAt: v.optional(v.number()),
    })),

    createdBy: v.optional(v.id("users")),
    createdAt: v.number(),
  }).index("by_slug", ["slug"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // PRODUCTS — Per-project entities
  // ═══════════════════════════════════════════

  products: defineTable({
    projectId: v.id("projects"),           // Which project owns this product
    name: v.string(),                      // "GymZilla"
    slug: v.string(),                      // "gymzilla"
    description: v.string(),               // What is this product/business
    
    // Product context — what agents need to know
    context: v.object({
      whatItIs: v.string(),                // Product description
      features: v.array(v.string()),       // Key features list
      pricing: v.optional(v.string()),     // Pricing info
      usps: v.array(v.string()),           // Unique selling propositions
      targetMarket: v.string(),            // General target market
      website: v.optional(v.string()),
      competitors: v.array(v.string()),    // Competitor names/URLs
    }),
    
    // Brand voice — how content should sound
    brandVoice: v.object({
      tone: v.string(),                    // "Direct, no-BS, motivational"
      style: v.string(),                   // "Conversational with authority"
      vocabulary: v.object({
        preferred: v.array(v.string()),    // Words to use
        avoided: v.array(v.string()),      // Words to never use
      }),
      examples: v.optional(v.string()),    // Example content or links
      notes: v.optional(v.string()),       // Additional style notes
    }),
    
    status: v.union(v.literal("active"), v.literal("archived")),
  }).index("by_slug", ["slug"])
    .index("by_status", ["status"])
    .index("by_project", ["projectId"]),

  // ═══════════════════════════════════════════
  // FOCUS GROUPS — Audience segments per product
  // ═══════════════════════════════════════════

  focusGroups: defineTable({
    projectId: v.id("projects"),           // Denormalized for project-scoped queries
    productId: v.id("products"),
    
    // Identity
    number: v.number(),                    // #1, #2, etc.
    name: v.string(),                      // "Fat Loss Seekers"
    nickname: v.string(),                  // "The Scale Watchers"
    category: v.string(),                  // "Physical Transformation Desires"
    overview: v.string(),                  // Brief description
    
    // Demographics
    demographics: v.object({
      ageRange: v.string(),                // "25-55, peaks at 35-45"
      gender: v.string(),                  // "60% female, 40% male"
      income: v.string(),
      lifestyle: v.string(),
      triggers: v.array(v.string()),       // What triggers buying intent
    }),
    
    // Psychographics
    psychographics: v.object({
      values: v.array(v.string()),
      beliefs: v.array(v.string()),
      lifestyle: v.string(),
      identity: v.string(),               // How they see themselves
    }),
    
    // Marketing intelligence
    coreDesires: v.array(v.string()),      // What they deeply want
    painPoints: v.array(v.string()),       // What frustrates them
    fears: v.array(v.string()),            // What they're afraid of
    beliefs: v.array(v.string()),          // Worldview/beliefs
    objections: v.array(v.string()),       // Why they hesitate to buy
    emotionalTriggers: v.array(v.string()),// What activates buying
    languagePatterns: v.array(v.string()), // Exact phrases they use
    
    // Content angles
    ebookAngles: v.array(v.string()),      // Positioning ideas
    marketingHooks: v.array(v.string()),   // Headlines that resonate
    transformationPromise: v.string(),     // Before → After journey
    
    // Metadata
    source: v.union(
      v.literal("uploaded"),               // Parsed from document
      v.literal("researched"),             // Generated by audience-researcher
      v.literal("manual")                  // Created in dashboard
    ),
    lastEnriched: v.optional(v.number()),  // When audience-enricher last updated
    enrichmentNotes: v.optional(v.string()),
    
  }).index("by_product", ["productId"])
    .index("by_project", ["projectId"])
    .index("by_category", ["category"]),

  // ═══════════════════════════════════════════
  // PIPELINES — Assembly line blueprints (GLOBAL)
  // ═══════════════════════════════════════════

  pipelines: defineTable({
    name: v.string(),                      // "Full Content Production"
    slug: v.string(),                      // "full-content-production"
    description: v.string(),               // What this pipeline produces
    
    type: v.union(
      v.literal("preset"),                 // System-provided, locked
      v.literal("custom"),                 // User-created
    ),
    forkedFrom: v.optional(v.id("pipelines")), // If forked from a preset
    
    // Sequential main steps — locked, one-at-a-time
    mainSteps: v.array(v.object({
      order: v.number(),                   // 1, 2, 3...
      agent: v.optional(v.string()),       // "vibe-content-writer" or null (for onComplete)
      model: v.optional(v.string()),       // "sonnet", "opus", "haiku"
      label: v.string(),                   // "Write Article" (display name)
      description: v.optional(v.string()), // "Writes long-form article from brief"
      outputDir: v.optional(v.string()),   // "drafts", "research", "final" (subfolder in campaign dir)
    })),
    
    // Parallel branches — fire after a specific main step
    parallelBranches: v.optional(v.array(v.object({
      triggerAfterStep: v.number(),        // Main step order that triggers this
      agent: v.string(),                   // "vibe-image-director"
      model: v.optional(v.string()),
      label: v.string(),                   // "Generate Hero Image"
      description: v.optional(v.string()),
    }))),
    
    // Where parallel branches must complete before pipeline continues
    convergenceStep: v.optional(v.number()),
    
    // What happens when pipeline completes
    onComplete: v.object({
      telegram: v.boolean(),               // Send Telegram notification
      summary: v.boolean(),                // Generate campaign summary report
      generateManifest: v.boolean(),       // Generate manifest.json of all files
    }),
    
    // Validation metadata
    requiredAgentCategories: v.optional(v.array(v.string())), // For validation warnings
    
  }).index("by_type", ["type"])
    .index("by_slug", ["slug"]),

  // ═══════════════════════════════════════════
  // CAMPAIGNS — Marketing efforts
  // ═══════════════════════════════════════════

  campaigns: defineTable({
    projectId: v.id("projects"),           // Which project owns this campaign
    name: v.string(),                      // "Summer Shred Ebook Launch"
    slug: v.string(),
    description: v.string(),
    productId: v.id("products"),
    
    // Pipeline blueprint (snapshot copied from pipelines table at creation)
    pipelineId: v.id("pipelines"),         // Reference to source pipeline template
    pipelineSnapshot: v.any(),             // Full pipeline definition frozen at campaign creation
                                           // In-flight tasks use this, not the live pipeline
    
    // Which audiences this campaign targets
    targetFocusGroupIds: v.array(v.id("focusGroups")),
    
    // Which deliverables per article (derived from pipeline parallel branches)
    deliverableConfig: v.optional(v.object({
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      socialTikTok: v.optional(v.boolean()),
      socialPinterest: v.optional(v.boolean()),
      socialVK: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
      landingPage: v.optional(v.boolean()),
      emailSequence: v.optional(v.boolean()),
      leadMagnet: v.optional(v.boolean()),
      adCopySet: v.optional(v.boolean()),
      pressRelease: v.optional(v.boolean()),
      ebookFull: v.optional(v.boolean()),
    })),
    
    // Research inputs
    seedKeywords: v.array(v.string()),
    competitorUrls: v.array(v.string()),   // Competitors for THIS angle
    notes: v.optional(v.string()),
    
    // Publishing config (FUTURE — when publisher agents are built)
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),  // Service registry name
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
    
    status: v.union(
      v.literal("planning"),
      v.literal("active"),
      v.literal("paused"),
      v.literal("in_revision"),            // Re-opened for revisions
      v.literal("completed")
    ),
    
    // Lifecycle timestamps
    activatedAt: v.optional(v.number()),
    pausedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    
    // Goals
    targetArticleCount: v.optional(v.number()),  // How many articles to produce
    
  }).index("by_slug", ["slug"])
    .index("by_product", ["productId"])
    .index("by_project", ["projectId"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // TASKS & CONTENT PIPELINE
  // ═══════════════════════════════════════════

  tasks: defineTable({
    projectId: v.id("projects"),           // Denormalized for kanban/project-scoped queries
    title: v.string(),
    description: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    
    // ── PIPELINE TRACKING ──
    // The pipeline is an ordered array of steps this task must go through.
    // Generated from the campaign's pipeline snapshot when the task is created.
    // Each step knows: which agent handles it, what status it produces.
    pipeline: v.array(v.object({
      step: v.number(),                     // 0, 1, 2, 3...
      status: v.string(),                   // "researched", "briefed", "drafted"...
      agent: v.optional(v.string()),        // "vibe-content-writer" or null
      model: v.optional(v.string()),        // "sonnet", "opus", "haiku"
      description: v.string(),              // "Article written"
      outputDir: v.optional(v.string()),    // "drafts", "final", "research"
    })),
    pipelineStep: v.number(),               // Current step index (0-based into pipeline[])
    
    status: v.union(
      v.literal("backlog"),
      v.literal("researched"),
      v.literal("briefed"),
      v.literal("drafted"),
      v.literal("reviewed"),
      v.literal("revision_needed"),
      v.literal("humanized"),
      v.literal("completed"),               // Terminal: pipeline finished
      v.literal("cancelled"),               // Terminal: manually cancelled
      v.literal("blocked"),
      v.literal("completed"),               // Terminal: all done
      v.literal("cancelled"),               // Terminal: manually cancelled
      v.literal("blocked"),
    ),
    
    // ── AGENT LOCKING ──
    // Prevents double-processing. Only ONE agent can work on a task at a time.
    // Agent acquires lock before starting, releases on completion.
    lockedBy: v.optional(v.string()),       // Agent name holding the lock, null = available
    lockedAt: v.optional(v.number()),       // Timestamp when locked (for stale detection)
    
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high"),
      v.literal("urgent")
    ),
    
    assigneeNames: v.array(v.string()),
    createdBy: v.string(),               // "human" or agent name
    
    // Content specifics
    contentType: v.optional(v.string()), // "blog_post", "landing_page", etc.
    contentSlug: v.optional(v.string()), // File path slug
    contentBrief: v.optional(v.string()), // Markdown brief from vibe-keyword-researcher
    
    // Which deliverables needed (from campaign template, overridable)
    deliverables: v.optional(v.object({
      blogPost: v.optional(v.boolean()),
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
    })),
    deliverableStatus: v.optional(v.any()), // Track which are done
    
    // Quality
    qualityScore: v.optional(v.number()),
    readabilityScore: v.optional(v.number()),
    revisionCount: v.optional(v.number()),
    rejectionNotes: v.optional(v.string()),
    
    // Metadata
    targetKeywords: v.optional(v.array(v.string())),
    focusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    publishedUrl: v.optional(v.string()),
    subscriberNames: v.array(v.string()),
    metadata: v.optional(v.any()),
    
  }).index("by_status", ["status"])
    .index("by_campaign", ["campaignId"])
    .index("by_project", ["projectId"])
    .index("by_project_status", ["projectId", "status"])
    .index("by_priority", ["priority"]),

  // ═══════════════════════════════════════════
  // AGENT COORDINATION (GLOBAL)
  // ═══════════════════════════════════════════

  agents: defineTable({
    name: v.string(),                      // "vibe-keyword-researcher"
    displayName: v.string(),               // "Keyword Researcher"
    role: v.string(),                      // "Topic & Keyword Research"
    status: v.union(
      v.literal("idle"),
      v.literal("active"),
      v.literal("blocked"),
      v.literal("offline")
    ),
    currentTaskId: v.optional(v.id("tasks")),
    lastHeartbeat: v.number(),
    heartbeatCron: v.string(),             // Cron expression
    defaultModel: v.string(),              // "haiku" | "sonnet" | "opus"
    skillPath: v.string(),
    level: v.union(
      v.literal("intern"),
      v.literal("specialist"),
      v.literal("lead")
    ),
    stats: v.object({
      tasksCompleted: v.number(),
      avgQualityScore: v.optional(v.number()),
      lastActive: v.number(),
    }),
  }).index("by_name", ["name"])
    .index("by_status", ["status"]),

  messages: defineTable({
    taskId: v.id("tasks"),
    fromAgent: v.string(),
    content: v.string(),
    attachments: v.optional(v.array(v.string())),
    mentions: v.array(v.string()),
  }).index("by_task", ["taskId"]),

  activities: defineTable({
    projectId: v.optional(v.id("projects")), // Optional (some activities are global)
    type: v.string(),                      // "task_created", "content_drafted", etc.
    agentName: v.string(),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    message: v.string(),
    metadata: v.optional(v.any()),
  }).index("by_type", ["type"])
    .index("by_agent", ["agentName"])
    .index("by_project", ["projectId"]),

  notifications: defineTable({
    mentionedAgent: v.string(),
    fromAgent: v.string(),
    taskId: v.optional(v.id("tasks")),
    content: v.string(),
    delivered: v.boolean(),
    deliveredAt: v.optional(v.number()),
  }).index("by_undelivered", ["mentionedAgent", "delivered"]),

  documents: defineTable({
    projectId: v.optional(v.id("projects")), // Optional (some docs are global)
    title: v.string(),
    content: v.string(),
    type: v.union(
      v.literal("deliverable"),
      v.literal("research"),
      v.literal("brief"),
      v.literal("report"),
      v.literal("audience_doc")           // Uploaded audience documents
    ),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    productId: v.optional(v.id("products")),
    createdBy: v.string(),
    filePath: v.optional(v.string()),
  }).index("by_task", ["taskId"])
    .index("by_type", ["type"])
    .index("by_product", ["productId"])
    .index("by_project", ["projectId"]),

  // ═══════════════════════════════════════════
  // REVISIONS — Post-pipeline human correction requests
  // ═══════════════════════════════════════════

  revisions: defineTable({
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    
    // What the human requested
    type: v.union(
      v.literal("fix"),                    // "Fix this specific thing"
      v.literal("rethink"),                // "Rethink the approach, re-brief"
      v.literal("extend"),                 // "Create more of X"
    ),
    notes: v.string(),                     // Human's instructions
    
    // Which agents to dispatch for this revision
    agents: v.array(v.object({
      agent: v.string(),                   // "vibe-content-writer"
      model: v.string(),                   // "sonnet"
      order: v.number(),                   // Sequence order (1, 2, 3...)
    })),
    runMode: v.union(
      v.literal("sequential"),             // One after another
      v.literal("parallel"),               // All at once
    ),
    
    // Tracking
    status: v.union(
      v.literal("pending"),
      v.literal("in_progress"),
      v.literal("completed"),
    ),
    agentResults: v.optional(v.any()),     // Per-agent completion tracking
    
    // Versioning
    version: v.number(),                   // Revision 1, 2, 3...
    originalFilePath: v.string(),          // What's being revised
    revisedFilePath: v.optional(v.string()), // Where revised version lands
    
    requestedAt: v.number(),
    completedAt: v.optional(v.number()),
    requestedBy: v.literal("human"),
  }).index("by_task", ["taskId"])
    .index("by_campaign", ["campaignId"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // SERVICE REGISTRY (GLOBAL)
  // ═══════════════════════════════════════════

  serviceCategories: defineTable({
    name: v.string(),                      // "seo_keywords"
    displayName: v.string(),               // "SEO & Keywords"
    description: v.string(),
    icon: v.string(),
    sortOrder: v.number(),
  }).index("by_name", ["name"]),

  services: defineTable({
    categoryId: v.id("serviceCategories"),
    subcategory: v.optional(v.string()),   // "x_twitter", "reddit" (for social)
    name: v.string(),                      // "dataforseo"
    displayName: v.string(),               // "DataForSEO"
    description: v.string(),
    isActive: v.boolean(),
    priority: v.number(),                  // 1 = highest
    
    // Credentials (stored in Convex, written to .env on sync)
    apiKeyEnvVar: v.string(),              // "DATAFORSEO_LOGIN"
    apiKeyConfigured: v.boolean(),
    apiKeyValue: v.optional(v.string()),   // Encrypted/stored securely
    extraConfig: v.optional(v.string()),   // JSON: endpoints, model names, etc.
    
    // Integration
    scriptPath: v.string(),                // "scripts/services/seo/query_dataforseo.py"
    mcpServer: v.optional(v.string()),     // MCP server name if applicable
    
    // Info
    costInfo: v.string(),                  // "$50 min deposit, ~$0.60/1K SERPs"
    useCases: v.array(v.string()),         // ["hero_images", "product_shots"]
    docsUrl: v.optional(v.string()),
    
  }).index("by_category", ["categoryId"])
    .index("by_active", ["isActive"])
    .index("by_name", ["name"]),

  // ═══════════════════════════════════════════
  // ANALYTICS & TRACKING
  // ═══════════════════════════════════════════

  agentRuns: defineTable({
    projectId: v.optional(v.id("projects")), // Optional (some runs are global)
    agentName: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    startedAt: v.number(),
    finishedAt: v.optional(v.number()),
    durationSeconds: v.optional(v.number()),
    model: v.string(),
    status: v.union(
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed")
    ),
    itemsProcessed: v.optional(v.number()),
    errorLog: v.optional(v.string()),
  }).index("by_agent", ["agentName"])
    .index("by_campaign", ["campaignId"])
    .index("by_project", ["projectId"]),

  keywordClusters: defineTable({
    campaignId: v.id("campaigns"),
    primaryKeyword: v.string(),
    secondaryKeywords: v.array(v.string()),
    lsiKeywords: v.array(v.string()),
    searchVolume: v.number(),
    keywordDifficulty: v.number(),
    opportunityScore: v.number(),
    searchIntent: v.string(),
    serpAnalysis: v.optional(v.any()),
    contentBrief: v.optional(v.string()),
  }).index("by_campaign", ["campaignId"]),

  contentMetrics: defineTable({
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    publishedUrl: v.optional(v.string()),
    
    // SEO metrics (updated periodically)
    rankings: v.optional(v.any()),         // Keyword → position
    organicTraffic: v.optional(v.number()),
    impressions: v.optional(v.number()),
    clicks: v.optional(v.number()),
    ctr: v.optional(v.number()),
    
    // Social metrics
    socialEngagement: v.optional(v.any()), // Platform → {likes, shares, comments}
    
    // Email metrics
    emailMetrics: v.optional(v.any()),     // {opens, clicks, conversions}
    
    lastUpdated: v.number(),
  }).index("by_task", ["taskId"])
    .index("by_campaign", ["campaignId"]),

  mediaAssets: defineTable({
    projectId: v.optional(v.id("projects")), // Optional
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    type: v.union(v.literal("image"), v.literal("video")),
    provider: v.string(),                  // "flux_pro", "runway", etc.
    promptUsed: v.string(),
    filePath: v.string(),
    fileUrl: v.optional(v.string()),
    dimensions: v.optional(v.string()),
    generationCost: v.optional(v.number()),
  }).index("by_task", ["taskId"])
    .index("by_project", ["projectId"]),

  reports: defineTable({
    projectId: v.optional(v.id("projects")), // Optional
    type: v.union(
      v.literal("weekly_seo"),
      v.literal("weekly_content"),
      v.literal("monthly_roi"),
      v.literal("daily_standup")
    ),
    campaignId: v.optional(v.id("campaigns")),
    periodStart: v.number(),
    periodEnd: v.number(),
    data: v.any(),
    summary: v.string(),
    actionItems: v.optional(v.array(v.string())),
  }).index("by_type", ["type"])
    .index("by_project", ["projectId"]),
});
```

### Auth Functions (`convex/auth.ts`)

Custom email/password auth — no `@convex-dev/auth` (React-only client helpers don't work with Vue/Nuxt).

```typescript
// convex/auth.ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Sign in: verify credentials, create session, return token
export const signIn = mutation({
  args: { email: v.string(), password: v.string() },
  // → Validates password against bcrypt hash
  // → Creates session with crypto.randomUUID() token
  // → Returns { token, user } on success
});

// Sign out: delete session
export const signOut = mutation({
  args: { token: v.string() },
  // → Deletes session record
});

// Validate session: check token is valid and not expired
export const validateSession = query({
  args: { token: v.string() },
  // → Looks up session by token index
  // → Checks expiresAt > Date.now()
  // → Returns user record if valid, null if expired/missing
});

// Get current user profile
export const me = query({
  args: { token: v.string() },
  // → Validates session, returns user (email, name, role)
});
```

### User Creation (`convex/admin.ts`)

Users are created via terminal — no registration UI. Uses `internalAction` for bcrypt (requires Node.js runtime):

```typescript
// convex/admin.ts
import { internalAction, internalMutation } from "./_generated/server";
import { v } from "convex/values";

// Internal action (Node.js runtime) — hashes password, then calls mutation to insert
export const createUser = internalAction({
  args: {
    email: v.string(),
    password: v.string(),
    name: v.string(),
    role: v.union(v.literal("admin"), v.literal("editor"), v.literal("viewer")),
  },
  handler: async (ctx, args) => {
    // 1. Hash password with bcrypt
    // 2. Call internal mutation to insert user record
  },
});
```

```bash
# Create user from terminal
npx convex run admin:createUser \
  '{"email":"vuk@example.com","password":"...","name":"Vuk","role":"admin"}' \
  --url http://localhost:3210
```

### Project Functions (`convex/projects.ts`)

```typescript
// convex/projects.ts
import { mutation, query, internalMutation } from "./_generated/server";

// List active projects (for Netflix-style selector)
export const list = query({ /* returns active projects with stats */ });

// Get project by slug (used by useCurrentProject composable)
export const getBySlug = query({
  args: { slug: v.string() },
});

// Create project + initialize folder structure on disk
export const create = mutation({
  args: { name, slug, description, appearance },
  // → Inserts project record
  // → Schedules action to create projects/{slug}/ directory tree
});

// Update project metadata
export const update = mutation({ /* ... */ });

// Archive / unarchive project
export const archive = mutation({ /* sets status to "archived" */ });
export const unarchive = mutation({ /* sets status to "active" */ });

// Recompute denormalized stats (called after product/campaign/task changes)
export const updateStats = internalMutation({
  args: { projectId: v.id("projects") },
  // → Counts products, campaigns, tasks for this project
  // → Updates stats object on project record
});
```

---

## 9. Agent Architecture — Skills + Subagents Design

### Skills vs Agents: The Fundamental Split

In Claude Code, these are two different things:

| | **Skills** (`.claude/skills/`) | **Agents** (`.claude/agents/`) |
|---|---|---|
| **What** | Knowledge packages | Worker instances |
| **Analogy** | Training manual / textbook | Employee with a job title |
| **Context** | Injected INTO the current context | Own separate context window |
| **Invocation** | Auto-loaded when relevant (progressive disclosure) | Delegated by Claude or invoked explicitly |
| **Model** | Uses caller's model | Can specify own model (haiku/sonnet/opus) |
| **Tools** | No tool restrictions | Can restrict to specific tools (Read-only, etc.) |
| **Composition** | Multiple skills load simultaneously | Agents use skills as reference material |
| **File** | SKILL.md + scripts/ + references/ (directory) | Single .md file with YAML frontmatter |

**The relationship:** Agents LOAD Skills. The `vibe-content-writer` agent (worker) loads the `content-writing-procedures` skill (knowledge), the `marketing-psychology` skill (knowledge), and the `humanizer` skill (knowledge) — all in a single invocation.

### Why This Split Matters

**Without split (old design):** Everything crammed into one SKILL.md per agent. 2000+ lines of identity + procedures + references + scripts. Context bloat. Can't share knowledge between agents.

**With split:**
- Agent definition is lean (~50 lines): identity, model, tools, personality, which skills to load
- Procedural knowledge lives in reusable skills (can be shared across agents)
- External skills from skills.sh slot in cleanly as additional knowledge
- Skills from the community get better over time — we just `npx skills add` to update

### Agent File Format

```yaml
# .claude/agents/vibe-content-writer.md
---
name: vibe-content-writer
description: Long-form content writer. Use for drafting blog posts, articles,
  and guides. Activate when tasks have status "briefed" and need article content.
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

You are the content writer for Vibe Marketing Platform.

## Skills to Load
Before writing ANY content, load these skills:
- .claude/skills/content-writing/SKILL.md (your core writing process)
- .claude/skills/marketing-psychology/SKILL.md (persuasion frameworks)
When humanizing is needed, also load:
- .claude/skills/humanizer/SKILL.md (AI pattern detection & removal)

## Identity
You write like a knowledgeable insider — direct, specific, opinionated.
Never corporate. Never generic. Every paragraph earns its place.

## Execution Protocol
1. Read memory/WORKING/vibe-content-writer.md (your current state)
2. Check Convex for assigned tasks: ./scripts/cx.sh tasks:getByAgent '{"agent":"vibe-content-writer"}'
3. For each task:
   a. Load campaign context (product, brand voice, focus groups)
   b. Read the content brief
   c. Write the article following content-writing skill
   d. Save to projects/{project-slug}/campaigns/{campaign-slug}/drafts/{slug}.md
   e. Update task status to "drafted"
   f. @mention vibe-content-reviewer for review
4. Update memory/WORKING/vibe-content-writer.md
5. Log activity to Convex
6. Exit

## Quality Bar
- 1500-2500 words unless brief specifies otherwise
- Flesch-Kincaid 8-10 (readable but not dumbed down)
- Primary keyword in H1, first 100 words, 2-3 H2s
- At least 3 focus group pain points addressed naturally
- At least 1 objection pre-handled
- Zero AI slop patterns (humanizer skill handles this)
```

### Agent Invocation (Updated)

```bash
#!/bin/bash
# scripts/invoke-agent.sh
# Usage: ./invoke-agent.sh <agent-name> [model-override] [extra-prompt]

AGENT_NAME=$1
MODEL=${2:-"sonnet"}
PROMPT=${3:-""}

cd ~/vibe-marketing

claude --dangerously-skip-permissions \
  --print \
  --model "$MODEL" \
  --agent "$AGENT_NAME" \
  --allowedTools "Bash,Read,Write,Edit,Grep,Glob,mcp__brave-search,mcp__firecrawl" \
  "$PROMPT Execute your heartbeat protocol."
```

The `--agent` flag tells Claude Code to load the agent definition from `.claude/agents/{name}.md`, which sets up the system prompt, tool restrictions, and model. The agent then loads its skills as needed via progressive disclosure.

### Agent Roster — 26 MVP Agents (+7 Future: 3 Publishing + 4 Analytics)

**Research Phase (8 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-keyword-researcher | vibe-keyword-researcher.md | sonnet | */6h | Topic discovery, keyword research |
| vibe-competitor-analyst | vibe-competitor-analyst.md | sonnet | daily | Competitor intelligence |
| vibe-brand-monitor | vibe-brand-monitor.md | sonnet | */8h | Brand monitoring, social listening |
| vibe-reddit-scout | vibe-reddit-scout.md | sonnet | */8h | Reddit opportunity scouting |
| vibe-twitter-scout | vibe-twitter-scout.md | sonnet | */8h | X/Twitter opportunity scouting |
| vibe-linkedin-scout | vibe-linkedin-scout.md | sonnet | daily | LinkedIn opportunity scouting |
| vibe-trend-detector | vibe-trend-detector.md | sonnet | */12h | Trend detection |
| vibe-review-harvester | vibe-review-harvester.md | sonnet | weekly | Review analysis |

**Audience Intelligence (3 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-audience-parser | vibe-audience-parser.md | sonnet | on-demand | Parse uploaded audience docs |
| vibe-audience-researcher | vibe-audience-researcher.md | opus | on-demand | Generate focus groups from scratch |
| vibe-audience-enricher | vibe-audience-enricher.md | sonnet | weekly | Enrich existing focus groups |

**SEO Phase (3 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-keyword-deep-researcher | vibe-keyword-deep-researcher.md | sonnet | on-demand | Deep keyword cluster research |
| vibe-serp-analyzer | vibe-serp-analyzer.md | sonnet | on-demand | SERP competition analysis |
| vibe-seo-auditor | vibe-seo-auditor.md | sonnet | weekly | Technical SEO audit |

**Content Creation (10 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-content-writer | vibe-content-writer.md | sonnet | hourly | Long-form articles |
| vibe-landing-page-writer | vibe-landing-page-writer.md | opus | on-demand | Landing page copy |
| vibe-email-writer | vibe-email-writer.md | sonnet | on-demand | Email sequences |
| vibe-social-writer | vibe-social-writer.md | sonnet | */12h | Platform-specific social |
| vibe-script-writer | vibe-script-writer.md | sonnet | on-demand | Video scripts |
| vibe-ebook-writer | vibe-ebook-writer.md | opus | on-demand | Ebooks & lead magnets |
| vibe-content-repurposer | vibe-content-repurposer.md | sonnet | daily | Content multiplication |
| vibe-ad-writer | vibe-ad-writer.md | sonnet | on-demand | Advertising copy |
| vibe-press-writer | vibe-press-writer.md | sonnet | on-demand | PR & press releases |

**Quality Assurance (4 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-content-reviewer | vibe-content-reviewer.md | sonnet | */8h | Quality review & scoring |
| vibe-humanizer | vibe-humanizer.md | opus | triggered | AI pattern breaking |
| vibe-fact-checker | vibe-fact-checker.md | sonnet | triggered | Product accuracy |
| vibe-plagiarism-checker | vibe-plagiarism-checker.md | haiku | triggered | Copyscape check |

**Media Generation (3 agents)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-image-director | vibe-image-director.md | sonnet | on-demand | Image prompt engineering |
| vibe-image-generator | vibe-image-generator.md | haiku | on-demand | Image generation |
| vibe-video-generator | vibe-video-generator.md | haiku | on-demand | Video generation |

**Publishing & Distribution (FUTURE — post-MVP, once pipelines produce content and you're ready to auto-publish)**

<!-- 
These agents will be added when the platform needs to push content live automatically.
For MVP, the pipeline ends with files in the campaign folder. Human reviews and publishes manually.

| vibe-publisher | vibe-publisher.md | haiku | */3h | CMS publishing |
| vibe-social-distributor | vibe-social-distributor.md | haiku | */12h | Social distribution |
| vibe-email-distributor | vibe-email-distributor.md | haiku | on-demand | Email dispatch |
-->

**Analytics & Reporting (FUTURE — post-MVP, once content is published and generating data)**

<!-- 
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-analytics-reporter | vibe-analytics-reporter.md | sonnet | weekly | Performance analytics |
| vibe-rank-tracker | vibe-rank-tracker.md | haiku | daily | Keyword positions |
| vibe-content-refresher | vibe-content-refresher.md | sonnet | weekly | Content decay |
| vibe-roi-calculator | vibe-roi-calculator.md | sonnet | monthly | Cost & revenue |
-->

**Orchestration (1 agent)**
| Agent | Agent File | Model | Schedule | Function |
|-------|------------|-------|----------|----------|
| vibe-orchestrator | vibe-orchestrator.md | haiku | */10m | Pipeline orchestration & dispatch |

### External Skills (from skills.sh)

Instead of building everything from scratch, several community and official skills can be installed directly via `npx skills add` and used as-is or as foundations for our custom agent skills.

| Skill | Source | Install | Use In Platform |
|-------|--------|---------|-----------------|
| **Humanizer** | `softaworks/agent-toolkit` | `npx skills add https://github.com/softaworks/agent-toolkit --skill humanizer` | **Core dependency for Humanizer agent.** Wikipedia-grade AI pattern detection: 16 pattern categories (undue emphasis, copula avoidance, em dash overuse, rule-of-three, synonym cycling, etc.). Replaces our custom humanization — this is more comprehensive than what we'd build. Install directly into `.claude/skills/humanizer/` as the base, then layer our brand voice and marketing-specific rules on top. |
| **Marketing Psychology** | `coreyhaines31/marketingskills` | `npx skills add https://github.com/coreyhaines31/marketingskills --skill marketing-psychology` | **Reference skill for vibe-content-writer, vibe-ad-writer, vibe-landing-page-writer, vibe-email-writer, vibe-ebook-writer.** Contains 40+ mental models (First Principles, Jobs-to-Be-Done, Mimetic Desire, Hyperbolic Discounting, Endowment Effect, etc.) with specific marketing applications for each. Install to `.claude/skills/shared-references/marketing-psychology/` and reference from content-creation agents' SKILL.md files. |
| **Referral Program** | `coreyhaines31/marketingskills` | `npx skills add https://github.com/coreyhaines31/marketingskills --skill referral-program` | **Reference skill for strategy agents.** Covers referral vs affiliate program design, incentive sizing frameworks (LTV × margin - target CAC), the referral loop, trigger moments, share mechanisms. Useful when campaigns involve referral/viral components. Install to `.claude/skills/shared-references/referral-program/`. |
| **Claim Investigation** | `jwynia/agent-skills` | `npx skills add https://github.com/jwynia/agent-skills --skill claim-investigation` | **Foundation for FactChecker agent.** Systematic 7-phase fact-checking: claim decomposition → entity resolution → verification → source evaluation → narrative pattern recognition → synthesis. Much more rigorous than a simple "check facts" prompt. Install into `.claude/skills/fact-checker/` as the base methodology. |
| **Ebook Analysis** | `jwynia/agent-skills` | `npx skills add https://github.com/jwynia/agent-skills --skill ebook-analysis` | **Knowledge extraction tool.** Two modes: concept extraction (principle → tactic hierarchy) and entity extraction (studies, researchers, frameworks, anecdotes with citation traceability). Use to: (1) analyze marketing books to enrich our `marketing-psychology` reference, (2) extract competitor ebook structures for BookBuilder, (3) build a knowledge base from uploaded reference materials. Install to `.claude/skills/shared-references/ebook-analysis/`. |
| **Presentation Design** | `jwynia/agent-skills` | `npx skills add https://github.com/jwynia/agent-skills --skill presentation-design` | **For generating pitch decks, campaign presentations, client reports.** Useful for campaign pitch decks and periodic reporting. Install to `.claude/skills/presentation-design/`. |
| **Web Artifacts Builder** | `anthropics/skills` | `npx skills add https://github.com/anthropics/skills --skill web-artifacts-builder` | **For generating interactive HTML artifacts.** React 18 + TypeScript + Tailwind + shadcn/ui, bundled to single HTML files. Use for: campaign landing page previews, interactive reports, data visualizations, mini-tools for clients. Output to `artifacts/` directory. Install to `.claude/skills/shared-references/web-artifacts-builder/`. |
| **Find Skills** | `vercel-labs/skills` | `npx skills add https://github.com/vercel-labs/skills --skill find-skills` | **Meta-skill for Claude Code.** Not used by platform agents, but used by us (the developers) directly in Claude Code to discover new relevant skills on skills.sh as the ecosystem grows. Install globally, not in platform. |

**Installation approach:**

```bash
cd ~/vibe-marketing

# Core agent skills (installed as agent foundations)
npx skills add https://github.com/softaworks/agent-toolkit --skill humanizer
npx skills add https://github.com/jwynia/agent-skills --skill claim-investigation

# Shared reference skills (installed to shared-references/)
npx skills add https://github.com/coreyhaines31/marketingskills --skill marketing-psychology
npx skills add https://github.com/coreyhaines31/marketingskills --skill referral-program
npx skills add https://github.com/jwynia/agent-skills --skill ebook-analysis
npx skills add https://github.com/jwynia/agent-skills --skill presentation-design
npx skills add https://github.com/anthropics/skills --skill web-artifacts-builder
```

**How agents reference shared skills:**

In an agent's SKILL.md:
```markdown
## References
- For marketing psychology frameworks: read .claude/skills/shared-references/marketing-psychology/SKILL.md
- For humanization patterns: read .claude/skills/humanizer/SKILL.md
- For fact-checking methodology: read .claude/skills/fact-checker/SKILL.md
```

This means our agents stand on the shoulders of battle-tested community skills rather than reinventing the wheel. We customize and layer our specific product/campaign context on top.

---

## 10. Audience Intelligence System

This is the new subsystem that powers the Product → Focus Groups hierarchy.

### Skill 1: AudienceAnalyzer (Parse Uploaded Documents)

```
.claude/skills/audience-analyzer/
├── SKILL.md
├── scripts/
│   ├── parse_docx.py              ← Convert .docx to markdown via pandoc
│   ├── parse_pdf.py               ← Extract text from PDF
│   ├── extract_focus_groups.py    ← Regex/structural parsing for known formats
│   └── validate_focus_group.py    ← Ensure all required fields present
└── references/
    ├── focus-group-schema.md      ← Required fields and data types
    ├── parsing-patterns.md        ← Common document structures to recognize
    └── example-input-output.md    ← Example: raw text → structured JSON
```

**SKILL.md core:**
```markdown
---
name: audience-analyzer
description: Parse uploaded audience/focus group documents into structured
  focus group records in the database. Use when user uploads a .docx, .pdf,
  or .md file containing audience research, personas, or focus group profiles.
---

# AudienceAnalyzer — Document Parser

## Identity
You are AudienceAnalyzer. You take messy human-written audience research
documents and extract structured focus group profiles from them.

## Process
1. User uploads a document to uploads/ directory
2. Convert to readable text (scripts/parse_docx.py or parse_pdf.py)
3. Identify distinct audience segments in the document
4. For EACH segment, extract:
   - Name, nickname, category, overview
   - Demographics (age, gender, income, lifestyle, triggers)
   - Psychographics (values, beliefs, identity)
   - Core desires (array of strings)
   - Pain points (array of strings)
   - Fears & anxieties (array of strings)
   - Beliefs & worldview (array of strings)
   - Common objections (array of strings)
   - Emotional triggers (array of strings)
   - Language patterns (exact phrases — array of strings)
   - Ebook/content angles (array of strings)
   - Marketing hooks & headlines (array of strings)
   - Transformation promise (single string: before → after)
5. Validate each group has all required fields (scripts/validate_focus_group.py)
6. Present extraction summary to dashboard for human review
7. On approval, write to Convex: focusGroups:createBatch
8. Mark source document as processed

## Handling Missing Fields
If a field isn't present in the source document:
- Demographics: flag as "needs enrichment"
- Language patterns: flag as "needs enrichment"
- Everything else: extract what's available, mark gaps
- @mention AudienceEnricher to fill gaps later

## Output
For each focus group, output JSON matching the Convex focusGroups schema.
Log: "Extracted {N} focus groups from {filename}. {M} have complete data,
{K} flagged for enrichment."
```

### Skill 2: AudienceResearcher (Generate From Scratch)

```
.claude/skills/audience-researcher/
├── SKILL.md
├── scripts/
│   ├── scrape_reddit.py           ← Pull discussions from relevant subreddits
│   ├── scrape_reviews.py          ← G2/Trustpilot/Amazon reviews
│   ├── analyze_competitors.py     ← Scrape competitor messaging & testimonials
│   ├── analyze_ad_library.py      ← Meta Ad Library scraping
│   └── compile_audience_doc.py    ← Generate the final .md document
└── references/
    ├── research-methodology.md    ← Step-by-step research protocol
    ├── focus-group-template.md    ← Template for each group profile
    ├── data-sources.md            ← Where to find audience data per niche
    ├── psychographic-frameworks.md ← Maslow, VALS, lifestyle segmentation
    └── example-output.md          ← Example complete focus group document
```

**SKILL.md core:**
```markdown
---
name: audience-researcher
description: Generate comprehensive audience focus group profiles from scratch
  for a product. Use when user has a product but no existing audience research.
  Produces a document similar to a professional marketing intelligence report.
---

# AudienceResearcher — Audience Intelligence Generator

## Identity
You are AudienceResearcher. You create comprehensive audience segmentation
documents by combining web research, competitor analysis, review mining,
and marketing psychology frameworks.

## When Invoked
User says "I need audience research for [product]" or creates a product
in the dashboard without any focus groups and clicks "Research Audiences."

## Research Protocol
Read references/research-methodology.md for the full protocol. Summary:

### Phase 1: Product Understanding (read product context)
- What is the product? Who is it obviously for?
- What problems does it solve? What transformation does it promise?

### Phase 2: Market Research (use web scraping services from registry)
- Scrape 3-5 competitor websites (messaging, testimonials, pricing pages)
- Scrape relevant subreddits (scripts/scrape_reddit.py)
  - Find: complaints, questions, language, desires, frustrations
- Scrape product reviews if applicable (scripts/scrape_reviews.py)
  - G2, Trustpilot, Amazon, App Store — extract sentiment patterns
- Check Meta Ad Library for competitor ad angles (scripts/analyze_ad_library.py)

### Phase 3: Audience Segmentation
- Identify natural groupings (by goal, life stage, pain point, identity)
- Aim for 10-30 distinct focus groups depending on market breadth
- Use psychographic frameworks (references/psychographic-frameworks.md):
  - Schwartz Awareness Levels (who knows what about the problem?)
  - Lifestyle segmentation (how do their lives differ?)
  - Goal-based clustering (what are they trying to achieve?)

### Phase 4: Profile Generation
For EACH focus group, generate the full profile matching the
focusGroups schema. CRITICAL fields:
- Language patterns: These must be REAL phrases from Reddit/reviews,
  not made-up marketing speak. Actual words real people use.
- Pain points: Specific, not generic. "Scale won't budge despite
  'eating healthy'" not "struggles with weight loss"
- Marketing hooks: Written as actual usable headlines

### Phase 5: Output
1. Generate complete markdown document (scripts/compile_audience_doc.py)
2. Save to content/research/{product-slug}/audience-intelligence.md
3. Present summary in dashboard for human review
4. On approval, write all groups to Convex: focusGroups:createBatch
5. Store source document in Convex documents table

## Quality Check
Each focus group MUST have:
- At least 5 core desires
- At least 5 pain points
- At least 5 language patterns (from real sources, cited)
- At least 3 marketing hooks
- A specific transformation promise (not generic)
- Demographics with age range and gender split

Groups without sufficient data get flagged for manual review.
```

### Skill 3: AudienceEnricher (Living Document Updates)

```
.claude/skills/audience-enricher/
├── SKILL.md
├── scripts/
│   ├── scan_recent_mentions.py    ← Check social for new patterns
│   ├── analyze_content_performance.py ← Which hooks/angles worked?
│   └── update_focus_group.py      ← Write enrichment to Convex
└── references/
    ├── enrichment-sources.md      ← Where to find new data
    └── enrichment-protocol.md     ← How to validate new data
```

**SKILL.md core:**
```markdown
---
name: audience-enricher
description: Enrich existing focus group profiles with new data discovered
  through ongoing marketing operations. Run weekly or triggered by other agents
  when they discover new audience insights.
---

# AudienceEnricher — Audience Profile Updater

## Identity
You keep focus group profiles alive and growing. As the platform runs
campaigns, agents discover new pain points, language patterns, objections,
and triggers. You integrate these discoveries into the source profiles.

## Enrichment Sources
1. **vibe-brand-monitor findings**: New brand mentions with sentiment data
2. **vibe-reddit-scout / vibe-twitter-scout discoveries**: Reddit/X conversations revealing new pain points
3. **vibe-review-harvester data**: New review patterns and language
4. **Content performance**: Which hooks/angles got the most engagement?
   (from analytics dashboard — manual review until analytics agents built)
5. **Manual input**: Human adds notes in dashboard

## Weekly Heartbeat
1. Query Convex for focus groups where lastEnriched is >7 days ago
2. Check activities feed for agent discoveries tagged with focus group IDs
3. For each relevant discovery:
   - Validate it's genuinely new (not a duplicate of existing data)
   - Categorize: new pain point? new language pattern? new objection?
   - Append to the appropriate field
4. Update lastEnriched timestamp
5. Log enrichment summary to activities

## Triggered Enrichment
Other agents can @mention AudienceEnricher with specific findings:
"@AudienceEnricher: Found new language pattern for Fat Loss Seekers group:
'I've tried everything and nothing sticks' — appeared 15 times in
r/loseit this week."

Process: validate → categorize → append → log
```

### Dashboard Flow for Audiences

**Path 1: Upload existing document**
```
Products → Select Product → Audiences → "Import from Document"
  → Upload .docx/.pdf
  → AudienceAnalyzer processes it
  → Preview: "Found 28 focus groups. 25 complete, 3 need enrichment."
  → Review each group (edit/approve/reject)
  → "Import All Approved" → saved to Convex
```

**Path 2: Research from scratch**
```
Products → Select Product → Audiences → "Research Audiences"
  → Confirm product context is filled in
  → AudienceResearcher runs (takes 10-30 minutes)
  → Preview: "Generated 18 focus groups from market research."
  → Review each group (edit/approve/reject)
  → "Import All Approved" → saved to Convex
```

**Path 3: Manual creation**
```
Products → Select Product → Audiences → "Create Manually"
  → Form with all fields from the schema
  → Save → immediately available for campaigns
```

**Path 4: Enrichment**
```
Products → Select Product → Audiences → Select group → "Enrichment History"
  → See timeline of all additions/changes
  → AudienceEnricher runs weekly automatically
  → Human can also add notes manually via the form
```

---

## 11. Individual Agent Skill Specifications

### Key Agent Skills (Abbreviated — Full SKILL.md in each directory)

**vibe-keyword-researcher** — Every content brief now includes:
```
## Content Brief: "Best Fat Burners 2026"
Campaign: Summer Shred Launch
Product: GymZilla
Target Focus Groups: #1 Fat Loss Seekers, #5 Plateau Breakers

### Keyword Data
Primary: "best fat burners 2026" (vol: 4,200, KD: 38)
Secondary: "fat burner supplements that work", "top fat burners for men"
LSI: "thermogenic", "metabolism booster", "appetite suppressant"

### Audience Context (from Focus Groups)
Pain points to address:
- Scale won't budge despite 'eating healthy'
- Losing the same 10 pounds over and over
- Confused by conflicting supplement advice

Language to use (their words):
- "I've tried everything"
- "What actually works"
- "Sick of wasting money on supplements"

Hooks that resonate:
- "Stop wasting money on fat burners that don't work"
- "The truth about thermogenics (from someone who tested 12 brands)"

Objections to pre-handle:
- "Is this just another scam supplement?"
- "Why should I trust this over what my trainer says?"

Transformation promise:
From confused about supplements → confident buyer who knows exactly
what works and why

### Deliverables Needed (from campaign template)
- [x] Blog post (2000+ words)
- [x] Hero image
- [x] X thread + LinkedIn + Instagram
- [x] Email excerpt
- [ ] Video script (not for this campaign)
```

**vibe-content-writer** — Now reads focus group data:
```
Before writing, load this context:
1. Product context (Convex: products:get)
2. Brand voice (from product)
3. Target focus groups (Convex: focusGroups:getByCampaign)
4. Content brief (from task)

Use focus group language patterns as subheading inspiration.
Address their specific objections naturally in the body.
Lead with their core desires in the intro hook.
Close with their transformation promise.
```

**vibe-orchestrator** — Dispatches based on content template:
```
When a task reaches "drafted" status:
1. Read the task's campaign content template
2. For each checked deliverable:
   - blogPost done (it's the draft) ✓
   - heroImage needed? → dispatch vibe-image-director
   - socialX needed? → dispatch vibe-social-writer  
   - socialLinkedIn needed? → dispatch vibe-social-writer
   - emailExcerpt needed? → dispatch vibe-content-repurposer
   - videoScript needed? → dispatch vibe-script-writer
3. Create sub-tasks for each deliverable
4. Track completion in task.deliverableStatus
```

---

## 12. The Orchestrator (vibe-orchestrator) — Heartbeat & Dispatch

### How Tasks Move Through the Pipeline

This is the core question: **how does the system know when to pick up tasks?**

There are two mechanisms working together:

#### Mechanism 1: vibe-orchestrator's Cron Heartbeat (Safety Net — every 10 min)

vibe-orchestrator runs every 10 minutes via cron. It is NOT the primary dispatch mechanism — the push triggers (Mechanism 2) handle that. The cron is the safety net that catches:

- **Stale locks**: Agent crashed mid-work, lock held >30 min → release and re-dispatch
- **Orphaned tasks**: Task at a non-human-gate step with no lock → re-dispatch the agent
- **Incomplete deliverables**: Hero images, social posts not yet created → dispatch deliverable agents
- **Pipeline starvation**: Not enough tasks in the backlog → trigger vibe-keyword-researcher

See the `check_pipeline.py` script in the "vibe-orchestrator's Updated Role" section below for the full implementation.

#### Mechanism 2: Convex Push Triggers (Reactive, Fast — Primary Dispatch)

The critical rule: **the status update is the LAST thing an agent does.** The agent writes files, saves documents, does all its work, and ONLY THEN calls `pipeline:completeStep`. This Convex mutation atomically releases the lock, updates status, and triggers the next agent. By definition, the previous agent is 100% done when the next one starts.

**Three atomic operations that make this safe:**

```typescript
// convex/pipeline.ts

import { mutation, internalAction } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

// ══════════════════════════════════════════════
// 1. ACQUIRE LOCK — Agent calls this BEFORE starting work
// ══════════════════════════════════════════════
// Returns true if lock acquired, false if already locked.
// Agent MUST check return value. If false → EXIT immediately.

export const acquireLock = mutation({
  args: { 
    taskId: v.id("tasks"), 
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) return { acquired: false, reason: "task_not_found" };
    
    // Already locked by another agent?
    if (task.lockedBy && task.lockedBy !== args.agentName) {
      const lockAge = Date.now() - (task.lockedAt || 0);
      const STALE_THRESHOLD = 30 * 60 * 1000; // 30 minutes
      
      if (lockAge < STALE_THRESHOLD) {
        return { acquired: false, reason: "locked", lockedBy: task.lockedBy };
      }
      // Lock is stale (agent probably crashed) — steal it
      console.warn(`Stealing stale lock on ${args.taskId} from ${task.lockedBy}`);
    }
    
    await ctx.db.patch(args.taskId, {
      lockedBy: args.agentName,
      lockedAt: Date.now(),
    });
    
    return { acquired: true };
  },
});

// ══════════════════════════════════════════════
// 2. COMPLETE STEP — Agent calls this as ABSOLUTE LAST action
// ══════════════════════════════════════════════
// This is THE critical function. Atomically:
//   a) Validates agent holds the lock
//   b) Advances pipelineStep
//   c) Updates task status
//   d) Releases the lock (lockedBy = null)
//   e) Schedules next agent (or triggers onComplete if pipeline done)
//
// Because this is a Convex mutation, ALL of this is atomic.
// Next agent is scheduled AFTER the mutation commits.

export const completeStep = mutation({
  args: { 
    taskId: v.id("tasks"),
    agentName: v.string(),
    results: v.optional(v.any()),     // quality score, file paths, etc.
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new Error("Task not found");
    
    // Verify this agent holds the lock
    if (task.lockedBy !== args.agentName) {
      throw new Error(
        `Lock violation: ${args.agentName} tried to complete but ` +
        `${task.lockedBy || 'nobody'} holds the lock`
      );
    }
    
    // Advance to next step
    const currentStep = task.pipelineStep;
    const nextStep = currentStep + 1;
    const nextPipelineDef = task.pipeline[nextStep];
    
    if (!nextPipelineDef) {
      // Pipeline finished — last step done
      await ctx.db.patch(args.taskId, {
        status: "completed",
        pipelineStep: nextStep,
        lockedBy: undefined,
        lockedAt: undefined,
      });
      await ctx.scheduler.runAfter(0, internal.campaigns.checkCompletion, {
        campaignId: task.campaignId!,
      });
      return { next: null, taskCompleted: true };
    }
    
    // Build the patch
    const patchData: any = {
      status: nextPipelineDef.status,
      pipelineStep: nextStep,
      lockedBy: undefined,            // ← RELEASE THE LOCK
      lockedAt: undefined,
    };
    
    // Merge agent results
    if (args.results) {
      if (args.results.qualityScore !== undefined) 
        patchData.qualityScore = args.results.qualityScore;
      if (args.results.readabilityScore !== undefined)
        patchData.readabilityScore = args.results.readabilityScore;
      if (args.results.contentBrief !== undefined)
        patchData.contentBrief = args.results.contentBrief;
    }
    
    await ctx.db.patch(args.taskId, patchData);
    
    // Log activity
    await ctx.db.insert("activities", {
      type: `task_${nextPipelineDef.status}`,
      agentName: args.agentName,
      taskId: args.taskId,
      message: `${args.agentName} completed → task now "${nextPipelineDef.status}"`,
    });
    
    // Auto-dispatch next agent
    if (nextPipelineDef.agent) {
      await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
        taskId: args.taskId,
        agentName: nextPipelineDef.agent,
        model: nextPipelineDef.model || "sonnet",
      });
    }
    
    return { next: nextPipelineDef.agent, status: nextPipelineDef.status };
  },
});

// ══════════════════════════════════════════════
// 3. DISPATCH AGENT — Internal action that invokes Claude Code CLI
// ══════════════════════════════════════════════

export const dispatchAgent = internalAction({
  args: { 
    taskId: v.id("tasks"), 
    agentName: v.string(),
    model: v.string(),
  },
  handler: async (ctx, args) => {
    const { exec } = require('child_process');
    const cmd = [
      `cd ~/vibe-marketing &&`,
      `./scripts/invoke-agent.sh`,
      args.agentName,
      args.model,
      `"Process task ${args.taskId}"`,
    ].join(' ');
    
    exec(cmd, (error: any) => {
      if (error) console.error(`Failed to dispatch ${args.agentName}:`, error);
    });
  },
});

// ══════════════════════════════════════════════
// 4. REVISION — Reviewer sends task back to a previous step
// ══════════════════════════════════════════════

export const requestRevision = mutation({
  args: { 
    taskId: v.id("tasks"),
    agentName: v.string(),
    notes: v.string(),
    rewindToStep: v.number(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new Error("Task not found");
    if (task.lockedBy !== args.agentName) throw new Error("Lock violation");
    
    const targetStep = task.pipeline[args.rewindToStep];
    if (!targetStep) throw new Error("Invalid rewind step");
    
    await ctx.db.patch(args.taskId, {
      status: "revision_needed",
      pipelineStep: args.rewindToStep,
      lockedBy: undefined,
      lockedAt: undefined,
      rejectionNotes: args.notes,
      revisionCount: (task.revisionCount || 0) + 1,
    });
    
    if (targetStep.agent) {
      await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
        taskId: args.taskId,
        agentName: targetStep.agent,
        model: targetStep.model || "sonnet",
      });
    }
  },
});
```

### Pipeline Builder & Presets

Pipelines are first-class entities stored in Convex. Each campaign references a pipeline and gets a frozen snapshot at creation time. The pipeline defines the entire assembly line.

#### Preset Pipelines (Locked, System-Provided)

```typescript
// convex/seed/presetPipelines.ts — seeded on first deploy

const PRESET_PIPELINES = [
  {
    name: "Research Only",
    slug: "research-only",
    type: "preset",
    description: "Keyword research + SERP analysis. Output: research reports only.",
    mainSteps: [
      { order: 0, agent: null,                        label: "Created",            outputDir: "" },
      { order: 1, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Keyword Research",    outputDir: "research" },
      { order: 2, agent: "vibe-serp-analyzer",        model: "sonnet", label: "SERP Analysis",       outputDir: "research" },
    ],
    parallelBranches: [],
    onComplete: { telegram: true, summary: true, generateManifest: true },
  },
  {
    name: "Content Draft",
    slug: "content-draft",
    type: "preset",
    description: "Research → write → review → humanize. Output: final articles ready for review.",
    mainSteps: [
      { order: 0, agent: null,                        label: "Created",            outputDir: "" },
      { order: 1, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Keyword Research",    outputDir: "research" },
      { order: 2, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Content Brief",       outputDir: "briefs" },
      { order: 3, agent: "vibe-content-writer",       model: "sonnet", label: "Write Article",       outputDir: "drafts" },
      { order: 4, agent: "vibe-content-reviewer",     model: "sonnet", label: "Quality Review",      outputDir: "reviewed" },
      { order: 5, agent: "vibe-humanizer",            model: "opus",   label: "Humanize",            outputDir: "final" },
    ],
    parallelBranches: [],
    onComplete: { telegram: true, summary: true, generateManifest: true },
  },
  {
    name: "Full Content Production",
    slug: "full-content-production",
    type: "preset",
    description: "Articles + images + social posts + email excerpts. The standard pipeline.",
    mainSteps: [
      { order: 0, agent: null,                        label: "Created",            outputDir: "" },
      { order: 1, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Keyword Research",    outputDir: "research" },
      { order: 2, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Content Brief",       outputDir: "briefs" },
      { order: 3, agent: "vibe-content-writer",       model: "sonnet", label: "Write Article",       outputDir: "drafts" },
      { order: 4, agent: "vibe-content-reviewer",     model: "sonnet", label: "Quality Review",      outputDir: "reviewed" },
      { order: 5, agent: "vibe-humanizer",            model: "opus",   label: "Humanize",            outputDir: "final" },
    ],
    parallelBranches: [
      { triggerAfterStep: 3, agent: "vibe-image-director",     model: "sonnet", label: "Hero Image" },
      { triggerAfterStep: 3, agent: "vibe-social-writer",      model: "sonnet", label: "Social Posts" },
      { triggerAfterStep: 3, agent: "vibe-content-repurposer", model: "sonnet", label: "Email Excerpt" },
    ],
    convergenceStep: 5, // Parallel branches must complete before pipeline ends
    onComplete: { telegram: true, summary: true, generateManifest: true },
  },
  {
    name: "Launch Package",
    slug: "launch-package",
    type: "preset",
    description: "Everything: articles + landing page + email sequence + ads + images + social.",
    mainSteps: [
      { order: 0, agent: null,                        label: "Created",            outputDir: "" },
      { order: 1, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Keyword Research",    outputDir: "research" },
      { order: 2, agent: "vibe-keyword-researcher",   model: "sonnet", label: "Content Brief",       outputDir: "briefs" },
      { order: 3, agent: "vibe-content-writer",       model: "sonnet", label: "Write Article",       outputDir: "drafts" },
      { order: 4, agent: "vibe-content-reviewer",     model: "sonnet", label: "Quality Review",      outputDir: "reviewed" },
      { order: 5, agent: "vibe-humanizer",            model: "opus",   label: "Humanize",            outputDir: "final" },
    ],
    parallelBranches: [
      { triggerAfterStep: 3, agent: "vibe-image-director",      model: "sonnet", label: "Hero Image" },
      { triggerAfterStep: 3, agent: "vibe-social-writer",       model: "sonnet", label: "Social Posts" },
      { triggerAfterStep: 3, agent: "vibe-content-repurposer",  model: "sonnet", label: "Email Excerpt" },
      { triggerAfterStep: 2, agent: "vibe-landing-page-writer", model: "opus",   label: "Landing Page" },
      { triggerAfterStep: 2, agent: "vibe-email-writer",        model: "sonnet", label: "Email Sequence" },
      { triggerAfterStep: 2, agent: "vibe-ad-writer",           model: "sonnet", label: "Ad Copy Set" },
    ],
    convergenceStep: 5,
    onComplete: { telegram: true, summary: true, generateManifest: true },
  },
  {
    name: "Audience Discovery",
    slug: "audience-discovery",
    type: "preset",
    description: "Generate focus group profiles from scratch for a new market.",
    mainSteps: [
      { order: 0, agent: null,                         label: "Created",               outputDir: "" },
      { order: 1, agent: "vibe-audience-researcher",   model: "opus", label: "Research Audiences",    outputDir: "research" },
      { order: 2, agent: "vibe-audience-enricher",     model: "sonnet", label: "Enrich Profiles",     outputDir: "research" },
    ],
    parallelBranches: [],
    onComplete: { telegram: true, summary: true, generateManifest: true },
  },
];
```

#### Pipeline Builder — Drag-and-Drop UI

```
/pipelines page:

┌──────────────────────────────────────────────────────┐
│  PRESETS (locked, system-provided)                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│  │ Research   │ │ Content    │ │ Full       │        │
│  │ Only       │ │ Draft      │ │ Production │        │
│  │            │ │            │ │            │        │
│  │ [Use]      │ │ [Use]      │ │ [Use]      │        │
│  │ [Fork →]   │ │ [Fork →]   │ │ [Fork →]   │        │
│  └────────────┘ └────────────┘ └────────────┘        │
│  ┌────────────┐ ┌────────────┐                       │
│  │ Launch     │ │ Audience   │                       │
│  │ Package    │ │ Discovery  │                       │
│  │            │ │            │                       │
│  │ [Use]      │ │ [Use]      │                       │
│  │ [Fork →]   │ │ [Fork →]   │                       │
│  └────────────┘ └────────────┘                       │
│                                                      │
│  MY PIPELINES (custom, fully editable)                │
│  ┌──────────────┐ ┌──────────────┐                   │
│  │ GymZilla     │ │ Quick Social │                   │
│  │ Full Launch  │ │ Posts Only   │                   │
│  │              │ │              │                   │
│  │ [Use] [Edit] │ │ [Use] [Edit] │                   │
│  │ [Delete]     │ │ [Delete]     │                   │
│  └──────────────┘ └──────────────┘                   │
│                                                      │
│  [+ New Pipeline from Scratch]                       │
└──────────────────────────────────────────────────────┘

[Use]    → Attach pipeline to campaign (creates frozen snapshot)
[Fork →] → Create new custom pipeline pre-populated from preset
[Edit]   → Open drag-and-drop builder
```

**The Builder Canvas:**

```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline Builder: "GymZilla Full Launch"                   │
│                                                             │
│  AVAILABLE AGENTS          │  MAIN PIPELINE (sequential)    │
│  ─────────────────         │  ────────────────────────────  │
│  Research:                 │                                │
│  [🔍 Keyword Researcher]  │  ┌─ 1. Keyword Research ──┐   │
│  [📊 SERP Analyzer]       │  │   vibe-keyword-research │   │
│  [🕵️ Competitor Analyst]  │  └────────────────────────┘   │
│                            │          ↓                     │
│  Audience:                 │  ┌─ 2. Content Brief ─────┐   │
│  [👥 Audience Researcher] │  │   vibe-keyword-research │   │
│  [📈 Audience Enricher]   │  └────────────────────────┘   │
│                            │          ↓                     │
│  Content:                  │  ┌─ 3. Write Article ─────┐──→ PARALLEL:│
│  [✍️ Content Writer]      │  │   vibe-content-writer   │   [🖼 Hero Image]│
│  [📄 Landing Page Writer] │  └────────────────────────┘   [📱 Social Posts]│
│  [📧 Email Writer]        │          ↓                     [📧 Email Excerpt]│
│  [📢 Ad Writer]           │  ┌─ 4. Quality Review ────┐   │
│  [📱 Social Writer]       │  │   vibe-content-reviewer │   │
│                            │  └────────────────────────┘   │
│  Quality:                  │          ↓                     │
│  [✅ Content Reviewer]    │  ┌─ 5. Humanize ──────────┐   │
│  [🤖 Humanizer]           │  │   vibe-humanizer        │   │
│  [🔎 Fact Checker]        │  └────────────────────────┘   │
│                            │          ↓                     │
│  Media:                    │     ═══ onComplete ═══        │
│  [🎨 Image Director]      │     📨 Telegram notification   │
│  [🖼 Image Generator]     │     📋 Generate manifest       │
│  [🎬 Video Generator]     │     📊 Summary report          │
│                            │                                │
│  [💾 Save Pipeline]  [▶ Preview Flow]  [❌ Cancel]         │
└─────────────────────────────────────────────────────────────┘
```

Drag agents from left sidebar onto the main pipeline (sequential) or connect them as parallel branches from a main step. Reorder by dragging up/down. Remove by dragging back to sidebar.

#### Pipeline Validation Rules

Pipeline builder validates on save:

**Errors (cannot save):**
- Content writer without keyword researcher before it (no brief)
- Content reviewer without content writer before it (nothing to review)
- Humanizer without content writer before it (nothing to humanize)
- Empty pipeline (no agents)

**Warnings (can save, shows alert):**
- No content reviewer in pipeline (quality risk)
- No humanizer in pipeline (AI detection risk)
- Image director without content writer (no article context for images)
- Social writer without content writer (what are you promoting?)

**Contextual warnings (shown when attaching pipeline to campaign):**
- Audience researcher + campaign already has rich focus groups selected → "Did you mean vibe-audience-enricher?"
- Audience enricher + no focus groups selected → "No focus groups to enrich. Add groups or use vibe-audience-researcher."

#### How Pipelines Attach to Campaigns

```typescript
// When creating a campaign:
// 1. User selects a pipeline (preset or custom)
// 2. System creates a SNAPSHOT of the pipeline definition
// 3. Snapshot is frozen on the campaign — editing the pipeline later
//    doesn't affect in-flight campaigns

export const attachPipeline = mutation({
  args: { 
    campaignId: v.id("campaigns"),
    pipelineId: v.id("pipelines"),
  },
  handler: async (ctx, args) => {
    const pipeline = await ctx.db.get(args.pipelineId);
    if (!pipeline) throw new Error("Pipeline not found");
    
    // Snapshot the entire pipeline definition
    await ctx.db.patch(args.campaignId, {
      pipelineId: args.pipelineId,
      pipelineSnapshot: {
        name: pipeline.name,
        mainSteps: pipeline.mainSteps,
        parallelBranches: pipeline.parallelBranches,
        convergenceStep: pipeline.convergenceStep,
        onComplete: pipeline.onComplete,
        snapshotAt: Date.now(),
      },
    });
  },
});
```

### Pipeline Definition → Task Pipeline

When a task is created, the task's `pipeline` array is generated from the campaign's pipeline snapshot:

```typescript
// convex/tasks.ts

function generateTaskPipeline(campaignSnapshot: any): PipelineStep[] {
  // Convert pipeline mainSteps to task pipeline format
  return campaignSnapshot.mainSteps.map((step: any, i: number) => ({
    step: i,
    status: getStatusForStep(step),      // "backlog", "researched", "briefed", etc.
    agent: step.agent,
    model: step.model,
    description: step.label,
    outputDir: step.outputDir,
  }));
}

export const create = mutation({
  args: { 
    title: v.string(),
    description: v.string(),
    campaignId: v.id("campaigns"),
    contentType: v.string(),
    createdBy: v.string(),
  },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) throw new Error("Campaign not found");
    
    const pipeline = generateTaskPipeline(campaign.pipelineSnapshot);
    
    const taskId = await ctx.db.insert("tasks", {
      title: args.title,
      description: args.description,
      campaignId: args.campaignId,
      contentType: args.contentType,
      status: "backlog",
      pipeline: pipeline,                   // ← Task carries frozen pipeline steps
      pipelineStep: 0,
      lockedBy: undefined,
      lockedAt: undefined,
      priority: "medium",
      assigneeNames: [],
      createdBy: args.createdBy,
      deliverables: campaign.deliverableConfig || {},
      deliverableStatus: {},
      revisionCount: 0,
      subscriberNames: [],
    });
    
    // Auto-dispatch first agent
    const firstAgentStep = pipeline.find(s => s.agent !== null);
    if (firstAgentStep) {
      await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
        taskId,
        agentName: firstAgentStep.agent!,
        model: firstAgentStep.model || "sonnet",
      });
    }
    
    return taskId;
  },
});
```

### The Agent Contract — What Every Agent MUST Do

Every agent follows this exact sequence. No exceptions.

```
AGENT CONTRACT (every agent, every run):

┌─────────────────────────────────────────────────────────┐
│  1. ACQUIRE LOCK                                        │
│     → npx convex run pipeline:acquireLock               │
│       { taskId, agentName: "vibe-content-writer" }      │
│     → If acquired=false → EXIT immediately              │
│                                                         │
│  2. DO ALL WORK                                         │
│     → Read campaign context, product, focus groups      │
│     → Write files to disk                               │
│     → Save documents to Convex (documents table)        │
│     → Run quality checks, scripts, etc.                 │
│     → ALL files saved, ALL data written                 │
│                                                         │
│  3. COMPLETE STEP (absolute last action)                │
│     → npx convex run pipeline:completeStep              │
│       { taskId, agentName, results: { score: 8.2 } }   │
│     → This atomically:                                  │
│        ✓ Validates agent holds the lock                 │
│        ✓ Releases the lock                              │
│        ✓ Advances pipelineStep                          │
│        ✓ Updates task status                            │
│        ✓ Schedules next agent (or triggers onComplete)  │
│                                                         │
│  4. EXIT                                                │
│     → Agent process ends. Nothing more to do.           │
│     → Next agent already triggered by step 3.           │
└─────────────────────────────────────────────────────────┘

REVISION EXCEPTION (reviewer rejects):
  → Instead of completeStep, call pipeline:requestRevision
    { taskId, agentName, notes: "...", rewindToStep: 3 }
  → Task rewinds to step 3 (writer) with rejection notes
  → Writer gets dispatched, acquires lock, revises, completes
```

In the agent .md file:

```yaml
# .claude/agents/vibe-content-writer.md
---
name: vibe-content-writer
model: sonnet
tools: Read, Write, Edit, Bash, Grep, Glob
---

## Execution Protocol (STRICT ORDER — never deviate)

1. Read task ID from prompt argument
2. **ACQUIRE LOCK:**
   ```bash
   LOCK=$(npx convex run pipeline:acquireLock \
     '{"taskId":"'$TASK_ID'","agentName":"vibe-content-writer"}' \
     --url $CONVEX_URL)
   ```
   → If acquired=false → EXIT immediately

3. Load context:
   - Campaign + Product + Focus groups from Convex
   - Content brief from task record

4. Load skills + write the article

5. Save all files + documents to Convex

6. **COMPLETE STEP (nothing after this):**
   ```bash
   npx convex run pipeline:completeStep \
     '{"taskId":"'$TASK_ID'","agentName":"vibe-content-writer","results":{}}' \
     --url $CONVEX_URL
   ```

7. EXIT
```

### Parallel Deliverables (Don't Block the Main Pipeline)

Deliverable agents (image, social, email) run alongside the review pipeline via a separate tracking mechanism:

```typescript
// convex/deliverables.ts
// Deliverable agents use their own completion tracking,
// separate from the main pipeline lock system.

export const completeDeliverable = mutation({
  args: {
    taskId: v.id("tasks"),
    deliverableType: v.string(),   // "heroImage", "socialX", "emailExcerpt"
    agentName: v.string(),
    filePath: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new Error("Task not found");
    
    const updated = { ...(task.deliverableStatus || {}) };
    updated[args.deliverableType] = {
      completed: true,
      completedAt: Date.now(),
      completedBy: args.agentName,
      filePath: args.filePath,
    };
    
    await ctx.db.patch(args.taskId, { deliverableStatus: updated });
    
    // Check if ALL required deliverables are done
    const required = task.deliverables || {};
    const allDone = Object.entries(required)
      .filter(([_, needed]) => needed)
      .every(([type, _]) => updated[type]?.completed);
    
    if (allDone) {
      await ctx.db.insert("activities", {
        type: "all_deliverables_complete",
        agentName: args.agentName,
        taskId: args.taskId,
        message: `All deliverables complete for "${task.title}"`,
      });
    }
  },
});
```

Deliverables don't block the main pipeline. The article goes through draft → review → humanize → completed. Meanwhile hero image, social posts, email excerpts get created in parallel by their own agents. The `onComplete` trigger checks that both the main pipeline AND all parallel deliverables are done before marking the campaign complete.

### vibe-orchestrator's Updated Role (Safety Net Only)

With push triggers as the primary dispatch, vibe-orchestrator becomes a health monitor:

```python
#!/usr/bin/env python3
# scripts/check_pipeline.py — runs every 10 min via cron

def check_pipeline():
    """Safety net: find stuck/orphaned tasks and recover them"""
    
    # === STALE LOCK DETECTION ===
    stale = cx("pipeline:findStaleLocks", '{"maxAgeMinutes":30}')
    for task in (stale or []):
        print(f"  ⚠️  Stale lock: {task['title']} by {task['lockedBy']} "
              f"for {task['lockAge']}min — releasing")
        cx("pipeline:releaseStaleLock", f'{{"taskId":"{task["_id"]}"}}')
        step = task['pipeline'][task['pipelineStep']]
        if step.get('agent'):
            invoke(step['agent'], step.get('model', 'sonnet'),
                   f"Retry task {task['_id']} (recovered from stale lock)")
    
    # === ORPHANED TASK DETECTION ===
    orphaned = cx("pipeline:findOrphanedTasks") or []
    for task in orphaned:
        step = task['pipeline'][task['pipelineStep']]
        if step.get('agent'):
            print(f"  🔄 Orphaned: {task['title']} at step "
                  f"{task['pipelineStep']} — dispatching {step['agent']}")
            invoke(step['agent'], step.get('model', 'sonnet'),
                   f"Process task {task['_id']}")
    
    # === DELIVERABLE TRACKING ===
    incomplete = cx("tasks:withIncompleteDeliverables") or []
    for task in incomplete:
        ds = task.get("deliverableStatus", {})
        deliverables = task.get("deliverables", {})
        if deliverables.get("heroImage") and not ds.get("heroImage", {}).get("completed"):
            invoke("vibe-image-director", "sonnet",
                   f"Create hero image for task {task['_id']}")
    
    # === HEALTH REPORT ===
    counts = cx("tasks:countByStatus") or {}
    locked = cx("pipeline:countLocked") or 0
    print(f"  Pipeline: {counts}  |  Active locks: {locked}")
```

#### The Full Flow (MVP — Files in Campaign Folder)

```
TASK LIFECYCLE — article goes backlog to completed:

1. Task created (status: "backlog", pipelineStep: 0)
   → Convex auto-dispatches first agent from task.pipeline[1]

2. vibe-keyword-researcher:
   → acquireLock ✓
   → research keywords, write brief
   → save to projects/{project}/campaigns/{slug}/research/ and .../briefs/
   → completeStep → status: "briefed", lock released
   → Convex triggers vibe-content-writer

3. vibe-content-writer:
   → acquireLock ✓
   → load product context + focus groups + brief
   → write article → save to projects/{project}/campaigns/{slug}/drafts/
   → completeStep → status: "drafted", lock released
   → Convex triggers vibe-content-reviewer
   → ALSO: vibe-orchestrator dispatches deliverable agents (parallel)
     → vibe-image-director → projects/{project}/campaigns/{slug}/assets/images/
     → vibe-social-writer → projects/{project}/campaigns/{slug}/assets/social/
     → vibe-content-repurposer → projects/{project}/campaigns/{slug}/assets/email/

4. vibe-content-reviewer:
   → acquireLock ✓
   → review article, score quality
   → If score >= 7: completeStep → status: "reviewed" → triggers vibe-humanizer
   → If score < 7: requestRevision → rewind to step 3 → triggers vibe-content-writer

5. vibe-humanizer:
   → acquireLock ✓
   → remove AI patterns
   → save final version to projects/{project}/campaigns/{slug}/final/
   → completeStep → status: "completed" → pipeline complete ✓
   → Convex checks campaign completion

NO HUMAN GATE IN PIPELINE — pipeline runs uninterrupted.
Files land in campaign folder. Telegram notifies you. 
You review in dashboard whenever you want.
```

Key guarantees:
- **No overlapping work**: Lock prevents two agents from working on the same task
- **No premature dispatch**: Next agent starts ONLY after completeStep commits
- **Crash recovery**: Stale locks detected by vibe-orchestrator every 10 min
- **Pipeline visibility**: Task carries its full pipeline array — dashboard shows exactly where each task is and what comes next
- **Uninterrupted flow**: No human gates in the pipeline — agents run to completion, human reviews at leisure

### Campaign Lifecycle

```
CAMPAIGN STATES:

planning → active → completed → in_revision → completed
                 ↕                           ↗
              paused          (revision done)

planning:      Campaign created, pipeline selected, config being set up.
active:        Pipeline running. Agents processing tasks.
paused:        Temporarily stopped. No new tasks. Existing tasks can finish.
completed:     All tasks done. Files in campaign folder. Telegram sent.
in_revision:   Human requested revisions. Re-opened for targeted agent work.
completed:     Revisions done. Back to completed. Can re-open again.
```

**How a campaign completes (onComplete flow):**

```typescript
// convex/campaigns.ts

export const checkCompletion = mutation({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) return;
    
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_campaign", q => q.eq("campaignId", args.campaignId))
      .collect();
    
    const terminalStatuses = ["completed", "cancelled"];
    const allDone = tasks.length > 0 && 
      tasks.every(t => terminalStatuses.includes(t.status));
    
    if (allDone) {
      await ctx.db.patch(args.campaignId, { 
        status: "completed",
        completedAt: Date.now(),
      });
      
      // Run onComplete actions from pipeline config
      const pipeline = campaign.pipelineSnapshot;
      
      if (pipeline.onComplete.generateManifest) {
        await ctx.scheduler.runAfter(0, internal.campaigns.generateManifest, {
          campaignId: args.campaignId,
        });
      }
      
      if (pipeline.onComplete.summary) {
        await ctx.scheduler.runAfter(0, internal.campaigns.generateSummary, {
          campaignId: args.campaignId,
        });
      }
      
      if (pipeline.onComplete.telegram) {
        await ctx.scheduler.runAfter(0, internal.notifications.sendCampaignComplete, {
          campaignId: args.campaignId,
        });
      }
    }
  },
});

// Generate manifest.json — index of everything the campaign produced
export const generateManifest = internalAction({
  handler: async (ctx, args) => {
    // Scans projects/{project}/campaigns/{slug}/ directory
    // Builds JSON index: { articles: [...], images: [...], social: [...] }
    // Saves to projects/{project}/campaigns/{slug}/manifest.json
  },
});

// Send Telegram summary
// "✅ Campaign 'Summer Shred' complete!
//  📝 8 articles in final/
//  🖼 8 hero images in assets/images/
//  📱 16 social posts in assets/social/
//  📧 8 email excerpts in assets/email/
//  Review: https://marketing.yourdomain.com/campaigns/summer-shred"
```

### Campaign Files — Everything Inside the Campaign

Each campaign is a self-contained folder within its project. The project + campaign IS the organizing principle.

```
projects/{project-slug}/campaigns/{campaign-slug}/
├── pipeline.json                    ← Pipeline definition snapshot (frozen at creation)
├── manifest.json                    ← Generated on completion: index of everything produced
│
├── research/                        ← Keyword reports, SERP analysis, competitor intel
│   ├── keyword-clusters.json
│   ├── serp-analysis-protein-powder.md
│   └── competitor-breakdown.md
│
├── briefs/                          ← Content briefs per article
│   ├── best-protein-powder-guide.brief.md
│   └── morning-routine-fat-loss.brief.md
│
├── drafts/                          ← Working draft versions
│   ├── best-protein-powder-guide.md
│   └── best-protein-powder-guide.v2.md     ← After revision
│
├── reviewed/                        ← Post-reviewer versions (with quality scores)
│   └── best-protein-powder-guide.reviewed.md
│
├── final/                           ← Approved, humanized final content
│   ├── best-protein-powder-guide.md         ← Current final version
│   ├── best-protein-powder-guide.meta.json  ← Metadata (keywords, scores, dates)
│   └── morning-routine-fat-loss.md
│
├── assets/
│   ├── images/                      ← Hero images, generated visuals
│   │   ├── best-protein-powder-guide-hero.png
│   │   └── best-protein-powder-guide-hero-v2.png  ← After revision
│   ├── social/                      ← Social post content (ready to copy-paste)
│   │   ├── best-protein-powder-guide-x.md
│   │   ├── best-protein-powder-guide-linkedin.md
│   │   └── best-protein-powder-guide-instagram.md
│   ├── video/                       ← Video scripts/assets
│   └── email/                       ← Email sequences
│       └── best-protein-powder-guide-excerpt.md
│
├── landing-pages/                   ← If pipeline includes landing page agent
├── ads/                             ← If pipeline includes ad copy agent
├── artifacts/                       ← Interactive HTML artifacts
│   ├── landing-page-preview.html
│   └── competitor-analysis.html
│
└── reports/                         ← Campaign summary, revision history
    └── completion-summary.md        ← Generated on onComplete
```

When campaign completes:
- All files stay in place — `final/` is the permanent archive
- `manifest.json` generated: complete index of every file produced
- Convex record keeps links to all tasks + documents + revisions
- Dashboard shows campaign as "completed" with full file browser
- Nothing gets deleted — it's your content library forever
- Campaign can be re-opened for revisions → status: "in_revision"

### Post-Pipeline Review & Revision System

Pipelines run uninterrupted. Human reviews content in the dashboard AFTER completion. Three types of actions:

**Type A — Fix: "Fix this specific thing"**
Targeted revision. You know what's wrong and which agent should fix it.
Examples: "Tone too aggressive," "Claims in section 3 are wrong," "Image style doesn't match brand"

**Type B — Rethink: "Rethink the approach"** 
The brief or angle was wrong. Need to re-do from a specific pipeline step.
Examples: "Wrong competitors," "Pivot the strategy," "Target different pain points"

**Type C — Extend: "Create more of X"**
Not a rejection — adding new work to a completed campaign.
Examples: "3 more image variations," "Add TikTok social posts," "Write an email sequence too"

**Dashboard Review UI:**

```
/campaigns/:id/review                ← Post-pipeline content review

Each content piece shows:
┌─────────────────────────────────────────────────┐
│  "Best Protein Powder Guide" — Article          │
│  Pipeline: completed ✓  |  Quality: 8.2/10     │
│                                                 │
│  [👁 Preview] [📊 Diff with previous version]   │
│                                                 │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐│
│  │ ✅ Approve  │ │ ✏️ Revise    │ │ ➕ Extend ││
│  └─────────────┘ └──────────────┘ └───────────┘│
│                                                 │
│  Approve: mark as reviewed-by-human (no action) │
│                                                 │
│  Revise (opens panel):                          │
│  ┌─────────────────────────────────────────────┐│
│  │ What needs to change?                       ││
│  │ [textarea for human instructions]           ││
│  │                                             ││
│  │ Which agents should handle this?            ││
│  │ ☑ vibe-content-writer (rewrite with notes)  ││
│  │ ☐ vibe-content-reviewer (re-review after)   ││
│  │ ☑ vibe-fact-checker (verify claims)         ││
│  │ ☐ vibe-humanizer (re-humanize after)        ││
│  │ ☐ vibe-image-director (new images)          ││
│  │                                             ││
│  │ Run mode:                                   ││
│  │ ○ Sequential (writer → then fact-checker)   ││
│  │ ○ Parallel (both at once)                   ││
│  │                                             ││
│  │ [Submit Revision Request]                   ││
│  └─────────────────────────────────────────────┘│
│                                                 │
│  Extend (opens panel):                          │
│  │ ☐ More articles (opens keyword input)        │
│  │ ☐ Additional images (count + style notes)    │
│  │ ☐ Social posts for new platforms             │
│  │ ☐ Email sequence                             │
│  │ ☐ Landing page                               │
│  │ ☐ Ad copy set                                │
│  │ [Submit Extension]                           │
└─────────────────────────────────────────────────┘
```

**Smart defaults when selecting revision agents:**
When you select `vibe-content-writer`, system auto-suggests (pre-checks) `vibe-content-reviewer` + `vibe-humanizer` after it. You can uncheck if it's a minor edit.

**Revision execution flow:**

```
1. Human submits revision request in dashboard
2. Convex creates revision record (revisions table)
3. Campaign status → "in_revision"
4. System dispatches selected agents with context:
   - Original file path
   - Human's notes/instructions
   - Campaign context (product, focus groups)
5. Agent reads original content + notes → produces new version
   - Saves as versioned file: article.v2.md (never overwrites)
6. When all revision agents complete → revision status: "completed"
7. If no more pending revisions → campaign status: "completed"
8. Telegram: "Revision complete for campaign X — review updated content"
```

**Extension execution:**
Extension creates new tasks on the campaign, not revisions. These run through the campaign's pipeline like any other task. Campaign goes back to "active" while new tasks process, then "completed" again when done.

---

## 13. Memory & Persistence System

*(Same three-layer system as V2)*

**Layer 1**: `memory/WORKING/{agent}.md` — Current task state (read first on every wake)
**Layer 2**: `memory/daily/YYYY-MM-DD.md` — Daily activity logs
**Layer 3**: `memory/long-term/` — Persistent knowledge:
- `SERVICE_REGISTRY.md` — Auto-generated from Convex
- `LESSONS_LEARNED.md` — What worked/didn't, calibration notes

**Product context and brand voice now live in Convex** (not files), loaded per-campaign by each agent. This is cleaner than file-based because multiple products coexist without file-naming conflicts.

**Focus group data lives in Convex**, queried by agents when working on a campaign task. The data is structured and searchable, not a raw markdown file that needs parsing every time.

---

## 14. Human-in-the-Loop — Post-Pipeline Review Model

### Design Philosophy

Pipelines run **uninterrupted** — no human gates blocking the assembly line. Agents do their work, files land in the campaign folder, Telegram notifies you. You review content whenever you want in the dashboard. This decouples pipeline speed from human availability.

### What You Review (When You Want)

1. **Completed articles** — read, approve, request revisions, or extend
2. **Generated images** — approve, request new variations with different prompts
3. **Social posts** — approve or edit before manual posting (NEVER auto-posted)
4. **Email sequences** — review before sending
5. **Ad copy** — review before campaign launch
6. **New focus groups** — review before import to database (from audience-researcher)

### What You DON'T Need to Touch (Unless You Want)

- Pipeline execution — runs automatically
- Agent scheduling — cron handles it
- File organization — agents save to correct campaign folders
- Quality checks — vibe-content-reviewer handles scoring
- AI pattern detection — vibe-humanizer handles it
- Task routing — pipeline definition handles it

### Review Channels

1. **Dashboard** (`/campaigns/:id/review`) — full preview, diff view, revision panel
2. **Telegram Bot** — notification + quick approve/reject inline keyboard
3. **Dashboard notification badge** — shows count of items ready for review

### Revision Workflow

See "Post-Pipeline Review & Revision System" above (section 12) for the full revision architecture including Type A (fix), Type B (rethink), and Type C (extend) flows.

---

## 15. Dashboard — Vue + Convex (Web-Accessible, Real-Time)

The dashboard is a **web application** accessible from any browser. It connects to Convex over WebSocket for real-time updates — when an agent changes a task status, your browser updates instantly without refresh.

### Tech Stack

- **Nuxt 3** (Vue 3 + server routes + auto-imports + SSR/SPA mode)
- **Convex Vue client** (`@convex-dev/convex-vue` or custom composables)
- **Tailwind CSS** + custom design system
- **TypeScript** throughout
- **Caddy** reverse proxy with auto-HTTPS (e.g., `marketing.yourdomain.com`)

### Deployment

The dashboard runs as a Nuxt 3 app via PM2, fronted by Caddy for HTTPS:

```bash
# Build and start
cd ~/vibe-marketing/dashboard
npm run build
pm2 start .output/server/index.mjs --name dashboard

# Caddy config (/etc/caddy/Caddyfile)
marketing.yourdomain.com {
    reverse_proxy localhost:3000
}

# Convex dashboard (optional, dev only)
convex.yourdomain.com {
    reverse_proxy localhost:6791
}

# Convex backend (needed for dashboard WebSocket connection)
convex-api.yourdomain.com {
    reverse_proxy localhost:3210
}
```

The dashboard connects to Convex backend at `convex-api.yourdomain.com` (or `localhost:3210` if accessed from the same server). All Convex queries are real-time subscriptions — data flows through WebSocket, not polling.

### Real-Time Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Browser (any device)                                            │
│  https://marketing.yourdomain.com                                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Nuxt 3 App (Vue 3 + Convex Client)                        │ │
│  │                                                             │ │
│  │  WebSocket connection → convex-api.yourdomain.com           │ │
│  │                                                             │ │
│  │  useQuery(api.tasks.listByStatus, { status: "drafted" })    │ │
│  │  → Auto-updates when ANY agent changes a task               │ │
│  │                                                             │ │
│  │  useMutation(api.services.update, { ... })                  │ │
│  │  → Saves service registry changes → triggers sync daemon    │ │
│  │  → SERVICE_REGISTRY.md regenerated → agents read new config │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
        │ WebSocket (real-time subscriptions)
        ▼
┌──────────────────────────────────────────────────────────────────┐
│  Hetzner Bare Metal                                              │
│                                                                  │
│  Caddy (HTTPS) → Nuxt 3 (port 3000)                            │
│                → Convex Backend (port 3210) ← agents also here  │
│                → Convex Dashboard (port 6791, dev only)         │
│                                                                  │
│  Agents (Claude Code CLI via cron) ──────→ Convex Backend       │
│    └── update task status ─→ WebSocket push ─→ your browser     │
└──────────────────────────────────────────────────────────────────┘
```

When you're watching the Pipeline board and vibe-content-reviewer finishes reviewing an article, the card moves from "drafted" to "reviewed" column in your browser **in real-time** without you doing anything.

### Authentication — Custom Email/Password

Custom auth (NOT `@convex-dev/auth` — its client helpers are React-only). For a closed app with terminal-created users:

**Flow:**
1. User visits any route → `middleware/auth.ts` checks for session cookie
2. No cookie or expired session → redirect to `/login`
3. `/login` page: email + password form → calls `auth.signIn` mutation
4. On success: set HttpOnly session cookie with token, redirect to `/`
5. Session cookie checked on every route via Nuxt middleware

**Components:**
- **Login page** (`/login`) — centered card, email/password fields
- **Nuxt middleware** (`middleware/auth.ts`) — checks session cookie, validates via `auth.validateSession`
- **Session cookie** — HttpOnly, contains session token, expires with session
- **Composable** `useAuth()` — provides `user`, `isAuthenticated`, `signIn()`, `signOut()`
- **User creation** — via terminal only (`npx convex run admin:createUser`)

**Roles:**
| Role | Permissions |
|------|------------|
| `admin` | Full access: create users, manage projects, all CRUD |
| `editor` | Create/edit content, manage campaigns, run agents |
| `viewer` | Read-only dashboard access |

### Page Map

```
═══════════════════════════════════════
AUTH ROUTES
═══════════════════════════════════════

/login                               ← Login page
├── Centered card with email + password fields
├── On success: set session cookie, redirect to /
└── On failure: error message (invalid credentials)

═══════════════════════════════════════
GLOBAL ROUTES (no project context)
═══════════════════════════════════════

/                                    ← Netflix-style project selector
├── Full-screen page (no sidebar)
├── Project cards grid:
│   ├── Each card: icon, name, color accent, campaign count, last activity
│   └── "Create New Project" card → /projects/new
├── [Show Archived Projects] toggle
└── System health bar (Convex status, agent count)

/projects/new                        ← Create project
├── Name, description
├── Appearance: icon picker (emoji), color picker (Tailwind palette)
└── On create: initializes projects/{slug}/ directory tree

/pipelines                           ← Pipeline Library (global)
├── PRESETS section (locked, system-provided)
│   ├── Pipeline cards: name, description, agent count, step visualization
│   ├── [Use] → attach to campaign (creates frozen snapshot)
│   └── [Fork →] → create new custom pipeline from this preset
├── MY PIPELINES section (custom, fully editable)
│   ├── Pipeline cards: name, description, forked from, last used
│   ├── [Use] [Edit] [Delete]
│   └── [+ New Pipeline from Scratch]
└── /pipelines/:id                   ← Pipeline Builder (drag-and-drop)
    ├── Left sidebar: available agents grouped by category
    ├── Main lane: sequential steps (drag to reorder)
    ├── Parallel lane: agents branching from main steps
    ├── onComplete config (telegram, summary, manifest toggles)
    ├── Validation warnings/errors (real-time as you build)
    └── [Save] [Preview Flow] [Cancel]

/agents                              ← Agent management (global)
├── Agent cards: name, role, status indicator, current task, last heartbeat
├── "Run Now" button per agent (invokes Claude Code CLI)
├── Agent detail panel:
│   ├── Run history (from agentRuns table — start, duration, status)
│   ├── Tasks completed total + this week
│   ├── Quality score trends (if applicable)
│   ├── Working memory preview (current WORKING/{agent}.md)
│   └── Cron schedule (editable — saves to Convex + regenerates crontab)
└── Global controls: Pause All / Resume All / Run Standup Now

/settings                            ← Platform configuration (global)
├── /settings/services               ← SERVICE REGISTRY
│   ├── Category tabs (SEO, Scraping, Images, Video, Email, etc.)
│   ├── Per service card: name, description, cost, status toggle
│   ├── Drag-and-drop priority ordering within category
│   ├── Configure modal: API keys, extra config, test connection
│   ├── Changes auto-sync to SERVICE_REGISTRY.md in real-time
│   └── Active summary banner: "4/12 image services active"
├── /settings/notifications          ← Telegram/Discord bot setup
│   ├── Bot token, chat ID
│   ├── Notification preferences (what triggers alerts)
│   └── Test notification button
├── /settings/crons                  ← Agent schedule management
│   ├── Agent schedule table (agent → cron expression → last run)
│   ├── Edit cron expressions inline
│   ├── Save regenerates crontab on server
│   └── Enable/disable individual agents
└── /settings/general                ← Platform settings
    ├── Platform name, timezone
    ├── Default content word count targets
    ├── Default model preferences
    └── Backup/export settings

═══════════════════════════════════════
PROJECT-SCOPED ROUTES (/projects/:slug/...)
═══════════════════════════════════════

Navigation: [🏋️ GymZilla ▾] Dashboard | Products | Campaigns | Pipeline | Review | Analytics
            ↑ dropdown to switch projects

/projects/:slug                      ← Project dashboard
├── Activity feed (real-time, filtered to this project)
├── Pipeline summary (counts per status for this project)
├── Quick actions (approve, create task, invoke agent)
└── Project stats (products, campaigns, tasks)

/projects/:slug/products             ← Product management
├── Product cards grid
├── Create new product (wizard: name → context → brand voice)
└── /projects/:slug/products/:id     ← Product detail
    ├── Product context (inline edit, auto-saves to Convex)
    ├── Brand voice (inline edit)
    ├── Focus groups count + link
    └── Campaigns using this product

/projects/:slug/products/:id/audiences ← Focus Group management
├── Focus group cards (filterable by category)
├── "Import from Document" → upload .docx/.pdf → audience-analyzer agent
├── "Research Audiences" → triggers audience-researcher agent
├── "Create Manually" → form with all schema fields
└── /projects/:slug/products/:id/audiences/:fgId ← Focus group detail
    ├── All fields displayed + inline editable
    ├── Enrichment history timeline
    └── Campaigns targeting this group

/projects/:slug/campaigns            ← Campaign management
├── Campaign cards (filter by status, product, pipeline)
├── Create new campaign wizard:
│   Step 1: Select product (from this project)
│   Step 2: Select pipeline (from global presets or custom pipelines)
│   Step 3: Select target focus groups (checkboxes — one or more)
│           ⚠️ Contextual warnings if pipeline has audience agents
│           but focus groups already selected (see Pipeline Validation)
│   Step 4: Toggle deliverables (which parallel branches to activate)
│   Step 5: Add seed keywords + competitor URLs
│   Step 6: Review & activate
└── /projects/:slug/campaigns/:id    ← Campaign detail
    ├── Campaign config (all fields editable while in "planning")
    ├── Pipeline visualization (shows main steps + parallel branches)
    ├── Content pipeline (mini kanban for this campaign only)
    ├── Campaign folder browser (tree view of projects/{slug}/campaigns/{campaign}/)
    ├── Keyword clusters discovered
    ├── Agent activity log for this campaign
    └── /projects/:slug/campaigns/:id/review ← Post-pipeline content review
        ├── Content list (articles, images, social, etc.)
        ├── Each item: Preview + Approve / Revise / Extend buttons
        ├── Revision panel (select agents, add notes, sequential/parallel)
        ├── Extension panel (add new work types to campaign)
        ├── Version diff view (v1 vs v2 side-by-side)
        └── Revision history timeline

/projects/:slug/pipeline             ← Content pipeline (project kanban)
├── Kanban columns: backlog → researched → briefed → drafted →
│   reviewed → humanized → completed
├── Filters: campaign, pipeline, content type, agent, date range
├── Card click → slide-out detail panel:
│   ├── Content preview (rendered markdown)
│   ├── Pipeline step indicator (where in the pipeline)
│   ├── Comment thread (agent @mentions and notes)
│   ├── Quality scores (reviewer's rubric breakdown)
│   ├── Deliverable checklist (what's done, what's pending)
│   ├── Revision history (diffs between versions)
│   └── File links (project campaign folder paths)
└── Pipeline health bar (tasks per status, avg time per step)

/projects/:slug/review               ← Review queue (project-scoped)
├── Completed campaigns with content awaiting human review
├── Per-campaign expandable sections
├── Each content piece: inline preview + Approve / Revise / Extend
├── Revision requests in progress (status tracking)
├── Focus groups pending import review
└── Batch approve (for trusted content types)

/projects/:slug/artifacts            ← Artifact management (project-scoped)
├── Project artifacts (reports, tools, visualizations)
├── Per-campaign artifacts (landing page previews, competitor analysis)
├── Upload artifact / Generate with web-artifacts-builder
├── Preview in-browser (rendered HTML)
├── Download / share link
└── CRUD: create, view, edit metadata, delete

/projects/:slug/analytics            ← Reports & metrics (project-scoped)
├── Agent productivity (tasks/week, quality scores, run durations) ← from agentRuns table
├── Cost tracking (agent runs × model cost, external API usage) ← from agentRuns + service logs
├── Content pipeline stats (pieces per stage, throughput)
└── [FUTURE] Content performance, keyword movement, ROI reports ← needs analytics agents

/projects/:slug/settings             ← Project settings
├── Project name, description
├── Appearance (icon, color)
├── Archive / unarchive project
└── Danger zone: delete project
```

### Core Composables (Vue + Convex)

```typescript
// composables/useAuth.ts
// Manages login/logout, session cookie, current user
export function useAuth() {
  const token = useCookie('session_token', { httpOnly: false }) // Read-only in client

  // Real-time session validation
  const { data: user } = useQuery(api.auth.me, { token: token.value })

  const isAuthenticated = computed(() => !!user.value)

  async function signIn(email: string, password: string) {
    const result = await useMutation(api.auth.signIn)({ email, password })
    token.value = result.token
    navigateTo('/')
  }

  async function signOut() {
    await useMutation(api.auth.signOut)({ token: token.value })
    token.value = null
    navigateTo('/login')
  }

  return { user, isAuthenticated, signIn, signOut }
}

// composables/useCurrentProject.ts
// Derives projectId from route.params.slug via Convex subscription
export function useCurrentProject() {
  const route = useRoute()
  const slug = computed(() => route.params.slug as string)

  // Real-time project subscription — auto-updates on stat changes
  const { data: project } = useQuery(
    api.projects.getBySlug,
    computed(() => slug.value ? { slug: slug.value } : 'skip')
  )

  const projectId = computed(() => project.value?._id)

  return { project, projectId, slug }
}

// composables/useConvex.ts
import { useQuery, useMutation } from '@convex-vue/core'
import { api } from '~/convex/_generated/api'

// Real-time task subscription — auto-updates on any change
export function useTasksByStatus(status: Ref<string>) {
  return useQuery(api.tasks.listByStatus, { status })
}

// Project-scoped tasks
export function useProjectTasks(projectId: Ref<string>) {
  return useQuery(api.tasks.listByProject, { projectId })
}

// Real-time agent status — heartbeats update live
export function useAgentStatuses() {
  return useQuery(api.agents.listAll)
}

// Real-time activity feed — new activities appear instantly
export function useActivityFeed(limit = 50, projectId?: Ref<string>) {
  return useQuery(api.activities.recent, { limit, projectId: projectId?.value })
}

// Project list for selector
export function useProjects() {
  return useQuery(api.projects.list)
}

// Mutations — trigger server-side changes
export function useApproveTask() {
  return useMutation(api.tasks.approve)
}

export function useUpdateService() {
  return useMutation(api.services.update)
}

export function useInvokeAgent() {
  // This calls a Convex action that runs a bash command on the server
  return useMutation(api.agents.invokeNow)
}
```

### Running Agents from Dashboard

The "Run Now" button calls a Convex action that invokes Claude Code:

```typescript
// convex/agents.ts
import { action } from "./_generated/server";
import { v } from "convex/values";

export const invokeNow = action({
  args: { agentName: v.string(), prompt: v.optional(v.string()) },
  handler: async (ctx, args) => {
    const { agentName, prompt } = args;
    
    // Execute Claude Code CLI on the server
    const { exec } = require('child_process');
    const cmd = `cd ~/vibe-marketing && ./scripts/invoke-agent.sh ${agentName} ${prompt || ''}`;
    
    exec(cmd, (error, stdout, stderr) => {
      // Log result to agentRuns table
    });
    
    return { started: true, agent: agentName };
  },
});
```

### Service Registry — Live Edit Flow

```
Dashboard Settings → Edit service priority/toggle/API key
  → useMutation(api.services.update) → Convex saves
  → Convex trigger/action runs sync_registry.py
  → SERVICE_REGISTRY.md regenerated on disk
  → Next agent invocation reads updated registry
  → Agent uses new service priority/credentials
```

All of this happens within seconds. No deployment, no restart.

### Environment Configuration for Dashboard

```bash
# dashboard/.env
NUXT_CONVEX_URL=https://convex-api.yourdomain.com  # Production
# OR
NUXT_CONVEX_URL=http://localhost:3210                # Dev

NUXT_PUBLIC_APP_NAME="Vibe Marketing"
NUXT_PUBLIC_APP_URL="https://marketing.yourdomain.com"
```

---

## 16. External Tool Integration Scripts

All service wrapper scripts live in `scripts/services/` and follow a common pattern:

```python
#!/usr/bin/env python3
"""
Service: DataForSEO — Keyword Research
Category: seo_keywords
Usage: python scripts/services/seo/query_dataforseo.py <command> [args]
Commands:
  keyword_suggestions <seed1> <seed2> ...
  serp_analysis <keyword>
  keyword_volume <keyword1> <keyword2> ...
"""

import os, sys, json, requests

LOGIN = os.environ.get("DATAFORSEO_LOGIN")
PASSWORD = os.environ.get("DATAFORSEO_PASSWORD")
BASE = "https://api.dataforseo.com/v3"

def keyword_suggestions(seeds, location=2840, language="en"):
    resp = requests.post(f"{BASE}/dataforseo_labs/google/keyword_suggestions/live",
        auth=(LOGIN, PASSWORD),
        json=[{"keywords": seeds, "location_code": location,
               "language_code": language, "limit": 100}])
    items = resp.json().get("tasks",[{}])[0].get("result",[{}])[0].get("items",[])
    results = []
    for i in items:
        kw = {
            "keyword": i["keyword"],
            "volume": i.get("keyword_info",{}).get("search_volume", 0),
            "difficulty": i.get("keyword_properties",{}).get("keyword_difficulty", 0),
            "cpc": i.get("keyword_info",{}).get("cpc", 0),
            "intent": i.get("search_intent_info",{}).get("main_intent", "unknown"),
        }
        vol = kw["volume"] or 0
        diff = kw["difficulty"] or 50
        kw["opportunity"] = round(vol * (1 - diff/100), 1)
        results.append(kw)
    results.sort(key=lambda x: x["opportunity"], reverse=True)
    print(json.dumps(results[:50], indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "keyword_suggestions":
        keyword_suggestions(sys.argv[2:])
    elif cmd == "serp_analysis":
        # ... SERP analysis implementation
        pass
    else:
        print(__doc__)
```

Each service script is:
- Self-contained (reads its own env vars)
- CLI-friendly (agents call via bash)
- JSON output (agents parse the result)
- Documented (--help shows usage)

---

## 17. Cost Analysis

### Fixed Monthly

| Item | Cost |
|------|------|
| Claude Max subscription | $200 |
| Hetzner bare metal (shared with other projects) | ~$100 (amortized ~$20) |
| **Fixed total** | **$220** |

*Note: The Hetzner bare metal runs multiple projects (BusinessPress, code-server instances, etc.), so the marketing platform's fair share is ~$20/mo of the $100 total server cost.*

### Variable (estimated for ~60-100 articles/month)

| Service | Est. Usage | Est. Cost |
|---------|-----------|-----------|
| DataForSEO | 5K keywords + 2K SERPs | $30-50 |
| Firecrawl | 500 scrapes | $19 |
| Copyscape | 60 checks | $2 |
| FLUX Pro (images) | 60 images | $3-6 |
| Buffer/social | Free-$6 | $0-6 |
| SendGrid | Free tier | $0 |
| Google APIs | Free | $0 |
| **Variable total** | | **$55-85** |

### **Total: ~$275-305/month**

Output: 60-100 articles + 300+ social posts + emails + monitoring + analytics.
Per-article cost (fully loaded): **~$3-5**

---

## 18. Implementation Roadmap

### Phase 1 — Foundation (Week 1-2)
**Goal**: Auth, projects, core pipeline working end-to-end with locking + push triggers

- [ ] VPS setup: Docker, Node.js 22, Python 3.12, Claude Code
- [ ] Deploy self-hosted Convex (docker-compose with PG17 backing)
- [ ] Push Convex schema (users, sessions, projects, pipelines, revisions + all tables with projectId), seed service categories
- [ ] Build auth system: `convex/auth.ts` (signIn, signOut, validateSession, me)
- [ ] Build user creation: `convex/admin.ts` (internalAction with bcrypt)
- [ ] Create initial admin user via terminal
- [ ] Build projects CRUD: `convex/projects.ts` (list, getBySlug, create, update, archive, updateStats)
- [ ] Create `projects/` directory structure convention (per-project campaigns, memory, uploads)
- [ ] Seed preset pipelines (Research Only, Content Draft, Full Content Production, Launch Package, Audience Discovery)
- [ ] Create project structure, CLAUDE.md, .mcp.json
- [ ] Install external skills from skills.sh (humanizer, marketing-psychology, claim-investigation, ebook-analysis, web-artifacts-builder, presentation-design, referral-program)
- [ ] Build pipeline engine: acquireLock, completeStep, requestRevision, dispatchAgent
- [ ] Build vibe-orchestrator skill + invoke-agent.sh + setup-crons.sh
- [ ] Build vibe-keyword-researcher skill + DataForSEO scripts
- [ ] Build vibe-content-writer skill + readability/keyword scripts
- [ ] Build vibe-content-reviewer skill + quality scoring
- [ ] Build vibe-humanizer skill
- [ ] Set up Telegram bot for notifications + onComplete handler
- [ ] Test: researcher → writer → reviewer → humanizer → onComplete → Telegram

### Phase 2 — Dashboard Core + Pipeline Builder (Week 3-4)
**Goal**: Dashboard with auth, project selector, products, audiences, campaigns, pipeline builder

- [ ] Nuxt 3 project, Convex Vue integration, Tailwind
- [ ] Login page (`/login`) — email/password form
- [ ] Auth middleware (`middleware/auth.ts`) — session cookie check
- [ ] `useAuth()` composable — login/logout, session management
- [ ] Netflix-style project selector (`/`) — project cards with icons, stats, colors
- [ ] Create project page (`/projects/new`) — name, icon picker, color picker
- [ ] `useCurrentProject()` composable — derives projectId from route slug
- [ ] Project-scoped layout with project switcher dropdown in nav
- [ ] Products CRUD pages (list, detail, create wizard) — under `/projects/:slug/products`
- [ ] vibe-audience-parser skill (parse uploaded .docx/.pdf)
- [ ] Audiences pages (list, detail, import, manual create) — under `/projects/:slug/products/:id/audiences`
- [ ] Pipeline Library page (presets + custom pipelines) — global at `/pipelines`
- [ ] Pipeline Builder page (drag-and-drop with validation)
- [ ] Campaigns CRUD pages (list, detail, creation wizard) — under `/projects/:slug/campaigns`
- [ ] Campaign folder browser (tree view of `projects/{slug}/campaigns/{campaign}/`)
- [ ] Service Registry page (settings → services) — global at `/settings/services`
- [ ] Service Registry sync daemon (Convex → SERVICE_REGISTRY.md)
- [ ] Pipeline kanban board (project-scoped at `/projects/:slug/pipeline`)
- [ ] Agent status page (global at `/agents`)
- [ ] Activity feed (real-time, project-scoped)

### Phase 3 — Content + Intelligence Agents (Week 5-6)
**Goal**: Full content production pipeline, audience intelligence, media generation

- [ ] Build vibe-social-writer + vibe-content-repurposer skills
- [ ] Build vibe-audience-researcher skill (generate from scratch)
- [ ] Build vibe-audience-enricher skill (weekly enrichment)
- [ ] Build vibe-competitor-analyst + vibe-brand-monitor skills
- [ ] Build vibe-reddit-scout + vibe-twitter-scout + vibe-linkedin-scout skills
- [ ] Build vibe-image-director + vibe-image-generator skills
- [ ] Build vibe-plagiarism-checker + vibe-fact-checker skills
- [ ] Post-pipeline review page (`/projects/:slug/campaigns/:id/review`)
- [ ] Revision system (submit revisions, dispatch agents, version tracking)
- [ ] Campaign extension system (add new work to completed campaigns)
- [ ] Project-scoped review queue (`/projects/:slug/review`)
- [ ] Telegram inline review (quick approve/reject buttons)
- [ ] Notification daemon (PM2)

### Phase 4 — Full Agent Roster + Polish (Week 7-8)
**Goal**: All 26 MVP agents operational

- [ ] Build vibe-landing-page-writer, vibe-email-writer, vibe-script-writer
- [ ] Build vibe-ebook-writer, vibe-ad-writer, vibe-press-writer
- [ ] Build vibe-video-generator (if video services active)
- [ ] Build vibe-seo-auditor, vibe-review-harvester, vibe-trend-detector
- [ ] Build vibe-keyword-deep-researcher, vibe-serp-analyzer
- [ ] Analytics pages in dashboard (agent productivity, cost tracking, pipeline stats)
- [ ] Campaign completion summary reports (manifest.json generation)
- [ ] Pipeline health monitoring dashboard
- [ ] Version diff viewer for revisions

### Phase 5 — Publishing Agents + Analytics + Optimization (Ongoing)
- [ ] Build vibe-publisher (CMS auto-publishing)
- [ ] Build vibe-social-distributor (social auto-posting)
- [ ] Build vibe-email-distributor (email dispatch)
- [ ] Build vibe-analytics-reporter (performance reporting)
- [ ] Build vibe-rank-tracker (keyword position monitoring)
- [ ] Build vibe-content-refresher (content decay detection)
- [ ] Build vibe-roi-calculator (cost/revenue attribution)
- [ ] Add publishing steps to pipeline presets (new preset: "Full Publish")
- [ ] A/B test content approaches, tune prompts
- [ ] Agent Teams for collaborative tasks (experimental)
- [ ] Multi-language support (Serbian, Lithuanian, etc.)
- [ ] Content calendar view in dashboard
- [ ] CMS integration bridge (BusinessPress, WordPress, etc.)
- [ ] Mobile-responsive dashboard

---

## Appendix A: Environment Variables (.env)

```bash
# Claude Code
ANTHROPIC_API_KEY=sk-ant-...

# Convex Self-Hosted
CONVEX_SELF_HOSTED_URL=http://localhost:3210
CONVEX_SELF_HOSTED_ADMIN_KEY=...      # Generated via generate_admin_key.sh
CONVEX_INSTANCE_SECRET=...            # Random secret for instance
CONVEX_DB_PASSWORD=...                # PostgreSQL password for convex user

# SEO
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...

# Scraping
FIRECRAWL_API_KEY=...
BRAVE_API_KEY=...

# Social Platforms
X_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
LINKEDIN_ACCESS_TOKEN=...

# Image Generation
FAL_AI_KEY=...

# Content Quality
COPYSCAPE_USERNAME=...
COPYSCAPE_API_KEY=...

# Email
SENDGRID_API_KEY=...

# Social Publishing
BUFFER_ACCESS_TOKEN=...

# Analytics
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GA4_PROPERTY_ID=...

# Notifications
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Appendix B: Marketing Frameworks

All embedded in agent skill reference files:
- Copywriting: AIDA, PAS, BAB, PASTOR, FAB, 4 U's, StoryBrand → `quill/references/content-frameworks.md`
- Marketing Psychology: 40+ mental models (from skills.sh) → `.claude/skills/shared-references/marketing-psychology/SKILL.md`
- Persuasion: Schwartz, Cialdini, Hormozi, Ogilvy → `landing-craft/references/persuasion-frameworks.md`
- SEO: On-page checklist, E-E-A-T → `quill/references/seo-on-page-checklist.md`
- Humanization: 16 AI pattern categories (from skills.sh) → `.claude/skills/humanizer/SKILL.md`
- Fact-checking: 7-phase claim investigation (from skills.sh) → `.claude/skills/fact-checker/SKILL.md`
- Audience: Maslow, VALS, lifestyle segmentation → `audience-researcher/references/psychographic-frameworks.md`
- Referral/Viral: Program design, incentive sizing (from skills.sh) → `.claude/skills/shared-references/referral-program/SKILL.md`

## Appendix C: Knowledge Base (via ebook-analysis skill)

The `ebook-analysis` skill from skills.sh provides a structured knowledge extraction pipeline.
Use it to build a marketing knowledge base from books, guides, and competitor content:

```
knowledge/
├── _index.md                    # Master registry
├── marketing/
│   ├── frameworks/              # Mental models, strategies
│   ├── studies/                 # Research cited in books
│   ├── researchers/             # Key marketing thinkers
│   ├── anecdotes/               # Case studies, examples
│   └── concepts/                # Ideas, principles
├── seo/
│   ├── frameworks/
│   └── studies/
└── copywriting/
    ├── frameworks/
    └── anecdotes/
```

This becomes a growing reference library that agents can query for evidence-backed
marketing claims, proven frameworks, and real-world case studies to cite in content.

---

*Document version: 3.0*
*Architecture: Claude Code Max + Self-Hosted Convex (single DB) + Skill Directories + Service Registry + Product/Audience/Campaign Hierarchy*
*Dashboard: Vue 3 / Nuxt 3 + Convex real-time*
*Database: Self-hosted Convex backed by PostgreSQL 17 (on Hetzner bare metal — 128GB RAM, 32 threads)*
*External skills: 7 community/official skills from skills.sh integrated*
*Estimated monthly cost: ~$275-305 for full marketing automation*
*Status: Standalone platform, CMS-agnostic, integration-ready*
