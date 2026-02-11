# Implementation Report: External Services Registry Rewrite
Generated: 2026-02-11

## Task
Complete rewrite of `/var/www/vibe-marketing/external-services-registry.md` from a service-by-service listing (483 lines) to a capability-first architecture (1438 lines) supporting agent dependency gating and setup script specification.

## What Changed

### Structure (Old vs New)
- **Old:** 19 sections organized by service type (SEO, SERP, Scraping, Social, etc.)
- **New:** 13 sections organized by capability architecture (capabilities, agent matrix, providers, gating, setup, health)

### New Sections Added
1. **Architecture Overview** - Capability abstraction layer, resolution flow diagram, integration points
2. **Service Capabilities** - 25 capability keys with display names, required agents, free tier info, self-hosted options
3. **Agent Dependency Matrix** - 31 agents x capabilities, REQUIRED/OPTIONAL/-- per cell, free minimum path per agent
4. **Service Providers by Capability** - All existing services reorganized by capability, with new columns (Self-Hosted?, Install Method)
5. **Self-Hosted Services** - Dedicated section for Crawl4AI, LanguageTool, Plausible, Umami with Docker details
6. **Setup Script Specification** - Full 11-step flow for `scripts/setup.sh`, including `docker-compose.services.yml`
7. **MCP Server Registry** - Complete `.mcp.json` with 30 MCP server entries (up from 4)
8. **Agent Gating Rules** - ENABLED/DISABLED/DEGRADED states with pseudocode and 20+ specific examples
9. **Priority & Fallback System** - Updated `resolve_service.py` with `--skip` fallback support
10. **Free Minimum Stack** - Per-agent cost table showing 23 of 31 agents run at $0/mo
11. **Full Stack (All Services)** - Three tiers: Free ($0), Growth ($90-95/mo), Pro ($365-475/mo)
12. **API Key Management** - Complete `.env.template` with 60+ variables, key flow diagram, dashboard UI description
13. **Service Health Monitoring** - Cron-based health checks, dashboard indicators, auto-fallback, quota monitoring

### All Existing Services Preserved
Every service from the original document is retained:
- 5 SEO services (DataForSEO, Ahrefs, SEMrush, Google Keyword Planner, AnswerThePublic)
- 3 SERP services (DataForSEO SERP, GSC, Bing)
- 4 scraping services (Firecrawl, Crawl4AI, Apify, ScraperAPI)
- 12 social scraping services across 7 platforms
- 9 image generation services + 2 templated image services
- 5 video generation services + 3 AI presenter services
- 1 voice synthesis service (ElevenLabs)
- 5 email services, 7 social publishing services, 5 CMS services
- 3 content quality services, 3 web search services, 4 analytics services
- 2 advertising services (FUTURE), 3 notification services, 3 document generation tools

### New Additions
- Crawl4AI Docker details (`docker pull unclecode/crawl4ai`, port 11235)
- LanguageTool self-hosted Docker details (`docker pull erikvl87/languagetool`, port 8081)
- Plausible self-hosted analytics (`docker pull plausible/analytics`)
- Umami self-hosted analytics (`docker pull ghcr.io/umami-software/umami`)
- 26 additional MCP server entries in `.mcp.json`
- `docker-compose.services.yml` full specification

## File
- `/var/www/vibe-marketing/external-services-registry.md` - 1438 lines (was 483)

## Notes
- No tests applicable (documentation file, not code)
- The document is self-contained and can be read independently
- Agent dependency matrix covers all 31 current agents + 7 FUTURE agents
- Setup script spec is detailed enough for direct implementation
