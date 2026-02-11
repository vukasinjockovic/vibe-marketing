# Research Report: MCP Server Availability Audit (36 Services)
Generated: 2026-02-11

## Summary

MCP (Model Context Protocol) adoption has exploded since Anthropic's late-2024 release. Of the 36 services researched, **30+ have at least community MCP servers**, and roughly **15 have official/vendor-maintained servers**. The ecosystem is heavily weighted toward community implementations, with quality varying significantly. Official servers from Stripe, Cloudflare, GitHub, Ahrefs, SEMrush, Brave, Slack, Webflow, ElevenLabs, Google (Ads, Analytics, Imagen/Veo), Mailgun, and WordPress are the most reliable. Notable gaps: no MCP server exists for Copyscape or Buffer (native); LanguageTool has no dedicated MCP server (only adjacent grammar-checker MCPs).

## Master Table

| # | Service | MCP Available? | Official/Community | Package / Repo | Maintained? | Notes |
|---|---------|---------------|-------------------|----------------|-------------|-------|
| 1 | **Firecrawl** | YES | Official | `firecrawl-mcp` (npm) / [github.com/firecrawl/firecrawl-mcp-server](https://github.com/firecrawl/firecrawl-mcp-server) | Well-maintained | Official from Firecrawl. Supports scraping, crawling, batch, search. Needs `FIRECRAWL_API_KEY`. |
| 2 | **Brave Search** | YES | Official | `@modelcontextprotocol/server-brave-search` (npm) / [github.com/brave/brave-search-mcp-server](https://github.com/brave/brave-search-mcp-server) | Well-maintained | In the official MCP servers repo. Web, local, image, video, news search. Needs `BRAVE_API_KEY`. |
| 3 | **Perplexity** | YES | Official | [github.com/perplexityai/modelcontextprotocol](https://github.com/perplexityai/modelcontextprotocol) | Well-maintained | Official from Perplexity. Direct web search via Perplexity Search API. |
| 4 | **DataForSEO** | YES | Community | `dataforseo-mcp-server` (PyPI) / [github.com/Skobyn/dataforseo-mcp-server](https://github.com/Skobyn/dataforseo-mcp-server) | Moderate | Comprehensive stdio MCP server. Also: [github.com/aimonk2025/dataforseo-ai-mcp-server](https://github.com/aimonk2025/dataforseo-ai-mcp-server) for AI visibility tracking. |
| 5 | **Ahrefs** | YES | Official | [github.com/ahrefs/ahrefs-mcp-server](https://github.com/ahrefs/ahrefs-mcp-server) | Well-maintained | Official from Ahrefs. Remote MCP server (no local setup). Rank tracking, keyword research, competitor insights. Also: [github.com/cnych/seo-mcp](https://github.com/cnych/seo-mcp) (free community alternative using Ahrefs data). |
| 6 | **SEMrush** | YES | Official | [developer.semrush.com/api/basics/semrush-mcp/](https://developer.semrush.com/api/basics/semrush-mcp/) | Well-maintained | Official from SEMrush (launched Sep 2025). Domain analytics, keyword data, competitive research. |
| 7 | **Google Search Console** | YES | Community | `mcp-server-gsc` / [github.com/ahonn/mcp-server-gsc](https://github.com/ahonn/mcp-server-gsc) | Moderate | Up to 25K rows performance data. Also: [github.com/AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) (SEO-focused). Requires Google Cloud service account. |
| 8 | **Google Analytics** | YES | Official (Google) | [developers.google.com/analytics/devguides/MCP](https://developers.google.com/analytics/devguides/MCP) | Well-maintained | Official from Google. Chat with Analytics data, build custom agents. |
| 9 | **Reddit API** | YES | Community | [github.com/GeLi2001/reddit-mcp](https://github.com/GeLi2001/reddit-mcp) / [github.com/Hawstein/mcp-server-reddit](https://github.com/Hawstein/mcp-server-reddit) | Moderate | Multiple community options. Read-only mostly. Reddit restricted API access Dec 2025, so credentials may be hard to get. |
| 10 | **X/Twitter API** | YES | Community | Multiple: [github.com/taazkareem/twitter](https://www.pulsemcp.com/servers/taazkareem-twitter) / [github.com/datawhisker/x](https://www.pulsemcp.com/servers/datawhisker-x) | Moderate | No official X MCP server. Community servers for posting/searching. Needs X API v2 bearer token. |
| 11 | **LinkedIn API** | YES | Community | `linkedin-mcp-server` (npm) / [github.com/felipfr/linkedin-mcpserver](https://github.com/felipfr/linkedin-mcpserver) | Moderate | No official LinkedIn MCP. Some use unofficial Voyager API (login/password), others use official OAuth. Quality varies. |
| 12 | **YouTube API** | YES | Community | `youtube-mcp-server` (npm) / [github.com/ZubeidHendricks/youtube-mcp-server](https://github.com/ZubeidHendricks/youtube-mcp-server) | Moderate | Multiple community options. Also: `@kirbah/mcp-youtube` (token-optimized), transcript servers. No official Google YouTube MCP. |
| 13 | **SendGrid** | YES | Community | [github.com/Garoth/sendgrid-mcp](https://github.com/Garoth/sendgrid-mcp) / `@cong/sendgrid-mcp` (JSR) | Moderate | Contact lists, templates, single sends, stats. Also Twilio blog has tutorial for building one. Not official from Twilio/SendGrid. |
| 14 | **Mailgun** | YES | Official | [github.com/mailgun/mailgun-mcp-server](https://github.com/mailgun/mailgun-mcp-server) | Well-maintained | Official open-source from Mailgun. Email performance metrics, natural language analytics. |
| 15 | **Telegram** | YES | Community | [github.com/chigwell/telegram-mcp](https://github.com/chigwell/telegram-mcp) / [github.com/sparfenyuk/mcp-telegram](https://github.com/sparfenyuk/mcp-telegram) | Moderate | Many community options (10+). Telethon-based (MTProto) or Bot API-based. Read/send messages, manage chats. |
| 16 | **Discord** | YES | Community | `mcp-discord` (npm) / [github.com/barryyip0625/mcp-discord](https://github.com/barryyip0625/mcp-discord) | Moderate | Multiple implementations. Full CRUD on channels, messages, webhooks. Needs Discord bot token. |
| 17 | **Slack** | YES | Official | `@modelcontextprotocol/server-slack` (npm) | Well-maintained | In the official MCP servers repo. Channels, messages, threads, reactions. Needs `SLACK_BOT_TOKEN` + `SLACK_TEAM_ID`. Also: [github.com/korotovsky/slack-mcp-server](https://github.com/korotovsky/slack-mcp-server) (more powerful community alternative). |
| 18 | **WordPress** | YES | Official | [github.com/WordPress/mcp-adapter](https://github.com/WordPress/mcp-adapter) (canonical) / `wordpress-mcp-server` (npm) | Well-maintained | WordPress core team is integrating MCP via `mcp-adapter` plugin (WP 6.9+). Automattic's `wordpress-mcp` is being deprecated in favor of this. Also community `@respira/wordpress-mcp-server` on npm. |
| 19 | **Ghost CMS** | YES | Community | `@fanyangmeng/ghost-mcp` (npm) / [github.com/MFYDev/ghost-mcp](https://github.com/MFYDev/ghost-mcp) | Moderate | Many community options (6+). Post/page/member management via Ghost Admin API. JWT auth. Also: [github.com/mtane0412/ghost-mcp-server](https://github.com/mtane0412/ghost-mcp-server), [github.com/siva-sub/ghost-cms-mcp-server](https://github.com/siva-sub/ghost-cms-mcp-server). |
| 20 | **Webflow** | YES | Official | [github.com/webflow/mcp-server](https://github.com/webflow/mcp-server) | Well-maintained | Official from Webflow. Create elements, styles, manage CMS collections, assets, custom code. Powers Webflow's own AI features. |
| 21 | **DALL-E / OpenAI Images** | YES | Community | [github.com/spartanz51/imagegen-mcp](https://github.com/spartanz51/imagegen-mcp) / [github.com/merlinrabens/image-gen-mcp-server](https://github.com/merlinrabens/image-gen-mcp-server) | Moderate | Multiple community servers. Supports DALL-E 2, DALL-E 3, gpt-image-1. Text-to-image + image-to-image. No official OpenAI MCP. |
| 22 | **Replicate** | YES | Community | `@gongrzhe/image-gen-server` (npm) / [github.com/awkoy/replicate-flux-mcp](https://github.com/awkoy/replicate-flux-mcp) | Moderate | Multiple Flux-focused servers. Also multi-provider: [github.com/iplanwebsites/image-mcp](https://mcpservers.org/servers/iplanwebsites/image-mcp). Needs `REPLICATE_API_TOKEN`. |
| 23 | **fal.ai** | YES | Community | `mcp-fal-ai-image` (npm) / `fal-ai-mcp-server` (npm) | Moderate | Multiple npm packages. Access to 600+ fal.ai models (Flux, SD, etc.). Also Imagen 4 via fal.ai. Needs `FAL_KEY`. |
| 24 | **Runway** | YES | Community | [github.com/wheattoast11/mcp-video-gen](https://github.com/wheattoast11/mcp-video-gen) | Low-Moderate | Combined RunwayML + Luma AI server. Text-to-video and image-to-video. Community maintained (single developer). |
| 25 | **ElevenLabs** | YES | Official | [github.com/elevenlabs/elevenlabs-mcp](https://github.com/elevenlabs/elevenlabs-mcp) / Docker: `mcp/elevenlabs` | Well-maintained | Official from ElevenLabs. TTS, voice cloning, transcription, voice agents. Free tier (10K credits/mo). |
| 26 | **Copyscape** | NO | -- | -- | -- | No MCP server found. Copyscape has a REST API that could be wrapped, but nobody has built an MCP server for it yet. |
| 27 | **LanguageTool** | PARTIAL | Community (adjacent) | [github.com/acforu/grammar-police-mcp](https://github.com/acforu/grammar-police-mcp) | Low | No dedicated LanguageTool MCP server. `grammar-police-mcp` does grammar checking in Claude but uses its own engine. Also `grammarly-mcp` exists. Could wrap LanguageTool API into MCP relatively easily. |
| 28 | **Buffer** | PARTIAL | Via Zapier | [zapier.com/mcp/buffer](https://zapier.com/mcp/buffer) | Moderate | No native Buffer MCP server. Available through Zapier's MCP bridge or Composio. Alternative: `crosspost` MCP for multi-platform social posting. |
| 29 | **Google Ads** | YES | Official (Google) | [github.com/googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp) (Python) | Well-maintained | Official from Google (launched Oct 2025). Read-only (GAQL queries). Apache-licensed, experimental. Install via `pipx`. Also: [github.com/cohnen/mcp-google-ads](https://github.com/cohnen/mcp-google-ads) (community). |
| 30 | **Meta Ads** | YES | Community | [github.com/pipeboard-co/meta-ads-mcp](https://github.com/pipeboard-co/meta-ads-mcp) / [github.com/gomarble-ai/facebook-ads-mcp-server](https://github.com/gomarble-ai/facebook-ads-mcp-server) | Moderate | Multiple community servers. Campaign analysis, creative review, performance metrics. OAuth auth via Facebook Marketing API. Also: [github.com/brijr/meta-mcp](https://github.com/brijr/meta-mcp). |
| 31 | **Stripe** | YES | Official | `@stripe/mcp` (npm) / Remote: `https://mcp.stripe.com` | Well-maintained | Official from Stripe. Remote server with OAuth or local via `npx -y @stripe/mcp --tools=all`. Also `@stripe/agent-toolkit` for framework integrations. |
| 32 | **Cloudflare** | YES | Official | `@cloudflare/mcp-server-cloudflare` (npm) / [github.com/cloudflare/mcp-server-cloudflare](https://github.com/cloudflare/mcp-server-cloudflare) | Well-maintained | Official from Cloudflare. Workers, D1, KV, R2, analytics. 13 MCP servers available. Some features need paid plan. |
| 33 | **Vercel** | YES | Official | [vercel.com/docs/mcp/vercel-mcp](https://vercel.com/docs/mcp/vercel-mcp) / `@vercel/mcp-adapter` (npm) | Well-maintained | Official from Vercel. Manage teams, projects, deployments, search docs. Also supports hosting your own MCP servers. |
| 34 | **GitHub** | YES | Official | [github.com/github/github-mcp-server](https://github.com/github/github-mcp-server) (Go binary) | Well-maintained | Official from GitHub. Remote + local. Repos, issues, PRs, Actions, code analysis, Dependabot. Replaces older `@modelcontextprotocol/server-github`. |
| 35 | **Google Imagen** | YES | Community | [github.com/falahgs/imagen-3.0-generate-google-mcp-server](https://github.com/falahgs/imagen-3.0-generate-google-mcp-server) / via Google's MCP toolbox | Low-Moderate | Community servers for Imagen 3/4. Also accessible via fal.ai MCP server. Google's own `google/mcp` repo has Genmedia tools but marked "not officially supported." |
| 36 | **Google Veo** | YES | Community | [github.com/mario-andreschak/mcp-veo2](https://github.com/mario-andreschak/mcp-veo2) / [github.com/alohc/veo-mcp-server](https://github.com/alohc/veo-mcp-server) | Low-Moderate | Text-to-video, image-to-video, video extension. Veo 2 and Veo 3 servers exist. Community maintained. |

## Detailed Findings

### Tier 1: Official, Well-Maintained (Vendor-Backed)

These have official repositories maintained by the service vendor:

| Service | Package | Install |
|---------|---------|---------|
| Firecrawl | `firecrawl-mcp` | `npx -y firecrawl-mcp` |
| Brave Search | `@modelcontextprotocol/server-brave-search` | `npx -y @modelcontextprotocol/server-brave-search` |
| Perplexity | `perplexityai/modelcontextprotocol` | Clone + configure |
| Ahrefs | `ahrefs/ahrefs-mcp-server` | Remote MCP (no local setup needed) |
| SEMrush | Via developer.semrush.com | Configure in MCP client |
| Google Analytics | Via developers.google.com | Configure per Google docs |
| Google Ads | `googleads/google-ads-mcp` | `pipx install` from GitHub |
| Mailgun | `mailgun/mailgun-mcp-server` | Clone + configure |
| Slack | `@modelcontextprotocol/server-slack` | `npx -y @modelcontextprotocol/server-slack` |
| WordPress | `WordPress/mcp-adapter` | WP plugin (6.9+) |
| Webflow | `webflow/mcp-server` | Configure per Webflow docs |
| ElevenLabs | `elevenlabs/elevenlabs-mcp` | `npx elevenlabs-mcp` or Docker |
| Stripe | `@stripe/mcp` | `npx -y @stripe/mcp --tools=all` or remote `mcp.stripe.com` |
| Cloudflare | `@cloudflare/mcp-server-cloudflare` | `npx @cloudflare/mcp-server-cloudflare` |
| Vercel | `@vercel/mcp-adapter` | Configure per Vercel docs |
| GitHub | `github/github-mcp-server` | Remote server or Go binary |

### Tier 2: Community, Actively Maintained

Good community servers with regular updates:

| Service | Best Option | Install |
|---------|------------|---------|
| DataForSEO | `dataforseo-mcp-server` | `pip install dataforseo-mcp-server` |
| Google Search Console | `ahonn/mcp-server-gsc` | npm/npx |
| Reddit | `GeLi2001/reddit-mcp` | FastMCP (Python) |
| X/Twitter | Multiple options | npm/npx |
| LinkedIn | `linkedin-mcp-server` | npm |
| YouTube | `youtube-mcp-server` | npm |
| SendGrid | `Garoth/sendgrid-mcp` | Deno/TypeScript |
| Telegram | `chigwell/telegram-mcp` | Python (Telethon) |
| Discord | `mcp-discord` | npm |
| Ghost CMS | `@fanyangmeng/ghost-mcp` | npm |
| DALL-E/OpenAI | `spartanz51/imagegen-mcp` | npm |
| Replicate | `@gongrzhe/image-gen-server` | npm |
| fal.ai | `mcp-fal-ai-image` | npm |
| Meta Ads | `pipeboard-co/meta-ads-mcp` | npm |

### Tier 3: Limited/Gaps

| Service | Status | Notes |
|---------|--------|-------|
| Runway | Community (single dev) | Combined with Luma AI. Works but maintenance uncertain. |
| Google Imagen | Community only | Google's own repo marked "demo only." Community servers exist. |
| Google Veo | Community only | Veo 2 and Veo 3 servers exist but single-developer projects. |
| Copyscape | **NONE** | Has REST API but no MCP wrapper exists. Build custom. |
| LanguageTool | **NONE** (adjacent exists) | `grammar-police-mcp` does grammar but not via LanguageTool specifically. Easy to wrap. |
| Buffer | **Via Zapier only** | No native MCP server. Zapier MCP bridge or Composio can proxy. |

## Recommendations for This Codebase

### Immediate Wins (Official + Easy Setup)
1. **Firecrawl MCP** - Replace custom `firecrawl_scrape.py` with official MCP server
2. **Brave Search MCP** - Standardized web search
3. **Perplexity MCP** - Replace custom `perplexity_ask.py`
4. **Stripe MCP** - If payment processing needed
5. **GitHub MCP** - Already powerful, official

### High Value for Marketing Platform
1. **Ahrefs MCP** + **SEMrush MCP** - Official SEO data, no custom API wrappers needed
2. **Google Ads MCP** + **Meta Ads MCP** - Ad campaign management
3. **Google Analytics MCP** + **Google Search Console MCP** - Performance data
4. **ElevenLabs MCP** - Voice content generation
5. **Webflow MCP** - If publishing to Webflow sites

### Build Custom MCP Servers For
1. **Copyscape** - Wrap their REST API into MCP (simple)
2. **LanguageTool** - Wrap their API or self-hosted instance (simple)
3. **Buffer** - Wrap their API or use Crosspost MCP as alternative

### Social Media Stack
- **Slack MCP** (official) for team comms
- **Discord MCP** (community) for community management
- **Telegram MCP** (community) for channel management
- **X/Twitter MCP** (community) for social posting
- **LinkedIn MCP** (community) for professional posting
- Consider **Crosspost MCP** or **Apify Social Media MCP** for unified multi-platform posting

### Image/Video Generation Stack
- **fal.ai MCP** - Best single server (600+ models including Flux, SD, Imagen)
- **Replicate MCP** - Good alternative for Flux specifically
- **DALL-E MCP** - For OpenAI-specific generation
- **Runway + Luma MCP** - For video generation
- **Google Veo MCP** - Alternative video generation

## Open Questions
- Will LinkedIn release an official MCP server? (No indication yet)
- Will Twitter/X release an official MCP server? (No indication yet)
- Will YouTube get a Google-official MCP server? (Only community options exist)
- Reddit API restrictions may make Reddit MCP servers unreliable long-term
- Buffer has no roadmap mention of MCP support

## Sources
1. [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
2. [Awesome MCP Servers (mcpservers.org)](https://mcpservers.org/)
3. [Awesome MCP Servers (mcp-awesome.com)](https://mcp-awesome.com/)
4. [PulseMCP Server Directory](https://www.pulsemcp.com/)
5. [Official MCP Registry](https://registry.modelcontextprotocol.io/)
6. [Firecrawl MCP Docs](https://docs.firecrawl.dev/mcp-server)
7. [Brave Search MCP (npm)](https://www.npmjs.com/package/@modelcontextprotocol/server-brave-search)
8. [Perplexity MCP Server](https://docs.perplexity.ai/guides/mcp-server)
9. [Ahrefs MCP Docs](https://docs.ahrefs.com/docs/mcp/reference/introduction)
10. [SEMrush MCP](https://developer.semrush.com/api/basics/semrush-mcp/)
11. [Google Analytics MCP](https://developers.google.com/analytics/devguides/MCP)
12. [Google Ads MCP Blog](https://ads-developers.googleblog.com/2025/10/open-source-google-ads-api-mcp-server.html)
13. [Mailgun MCP](https://github.com/mailgun/mailgun-mcp-server)
14. [Slack MCP (npm)](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)
15. [WordPress MCP Adapter](https://github.com/WordPress/mcp-adapter)
16. [Webflow MCP Docs](https://developers.webflow.com/mcp/reference/overview)
17. [ElevenLabs MCP](https://github.com/elevenlabs/elevenlabs-mcp)
18. [Stripe MCP (npm)](https://www.npmjs.com/package/@stripe/mcp)
19. [Cloudflare MCP (npm)](https://www.npmjs.com/package/@cloudflare/mcp-server-cloudflare)
20. [Vercel MCP Docs](https://vercel.com/docs/mcp/vercel-mcp)
21. [GitHub MCP Server](https://github.com/github/github-mcp-server)
22. [DataForSEO MCP (PyPI)](https://pypi.org/project/dataforseo-mcp-server/)
23. [Ghost MCP](https://github.com/MFYDev/ghost-mcp)
24. [Meta Ads MCP](https://github.com/pipeboard-co/meta-ads-mcp)
25. [RunwayML + Luma MCP](https://github.com/wheattoast11/mcp-video-gen)
26. [Google Veo MCP](https://github.com/mario-andreschak/mcp-veo2)
27. [fal.ai MCP (npm)](https://www.npmjs.com/package/mcp-fal-ai-image)
