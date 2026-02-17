import { mutation } from "./_generated/server";

// ═══════════════════════════════════════════
// SEED SERVICE PROVIDERS — Runs via:
//   npx convex run seedServices:seedProviders --url http://localhost:3210
// Idempotent: uses upsertFromManifest (skips if exists).
// ═══════════════════════════════════════════

interface ProviderSeed {
  categoryName: string;
  name: string;
  displayName: string;
  description: string;
  scriptPath: string;
  mcpServer?: string;
  apiKeyEnvVar: string;
  costInfo: string;
  useCases: string[];
  docsUrl?: string;
  defaultPriority: number;
  integrationType: "script" | "mcp" | "both" | "local";
  freeTier: boolean;
  selfHostedConfig?: {
    dockerCompose?: string;
    healthCheckUrl?: string;
    defaultPort?: number;
  };
}

const providers: ProviderSeed[] = [
  // ── SEO & Keywords ──
  {
    categoryName: "seo_keywords", name: "dataforseo-keywords", displayName: "DataForSEO Keywords",
    description: "Keyword research, search volume, difficulty, CPC data via DataForSEO API",
    scriptPath: "services/dataforseo-keywords/query.py", apiKeyEnvVar: "DATAFORSEO_LOGIN",
    costInfo: "$0.075/request", useCases: ["keyword_research", "search_volume", "keyword_difficulty"],
    docsUrl: "https://docs.dataforseo.com/", defaultPriority: 1, integrationType: "mcp", freeTier: false,
    mcpServer: "dataforseo",
  },
  {
    categoryName: "seo_keywords", name: "google-keyword-planner", displayName: "Google Keyword Planner",
    description: "Google Ads Keyword Planner for search volume and forecasts",
    scriptPath: "services/google-keyword-planner/query.py", apiKeyEnvVar: "GOOGLE_ADS_API_KEY",
    costInfo: "Free with Google Ads account", useCases: ["keyword_research", "search_volume"],
    docsUrl: "https://ads.google.com/", defaultPriority: 2, integrationType: "script", freeTier: true,
  },

  // ── SERP & Rank Tracking ──
  {
    categoryName: "serp_tracking", name: "dataforseo-serp", displayName: "DataForSEO SERP",
    description: "SERP analysis, rank tracking, featured snippets via DataForSEO",
    scriptPath: "services/dataforseo-serp/query.py", apiKeyEnvVar: "DATAFORSEO_LOGIN",
    costInfo: "$0.075/request", useCases: ["serp_analysis", "rank_tracking"],
    docsUrl: "https://docs.dataforseo.com/", defaultPriority: 1, integrationType: "mcp", freeTier: false,
    mcpServer: "dataforseo",
  },
  {
    categoryName: "serp_tracking", name: "google-search-console", displayName: "Google Search Console",
    description: "Google Search Console for organic search performance data",
    scriptPath: "services/google-search-console/query.py", apiKeyEnvVar: "GSC_SERVICE_ACCOUNT",
    costInfo: "Free", useCases: ["rank_tracking", "impressions", "ctr"],
    docsUrl: "https://search.google.com/search-console/", defaultPriority: 2, integrationType: "script", freeTier: true,
  },

  // ── Web Scraping ──
  {
    categoryName: "web_scraping", name: "firecrawl", displayName: "Firecrawl",
    description: "AI-powered web scraping with markdown extraction",
    scriptPath: "services/firecrawl/crawl.py", mcpServer: "firecrawl", apiKeyEnvVar: "FIRECRAWL_API_KEY",
    costInfo: "Free: 500 credits/mo", useCases: ["web_scraping", "content_extraction"],
    docsUrl: "https://firecrawl.dev/", defaultPriority: 1, integrationType: "mcp", freeTier: true,
  },
  {
    categoryName: "web_scraping", name: "crawl4ai", displayName: "Crawl4AI",
    description: "Self-hosted AI web crawler with LLM-ready markdown output",
    scriptPath: "services/crawl4ai/crawl.py", apiKeyEnvVar: "CRAWL4AI_URL",
    costInfo: "Free (self-hosted)", useCases: ["web_scraping", "content_extraction"],
    docsUrl: "https://github.com/unclecode/crawl4ai", defaultPriority: 2, integrationType: "local", freeTier: true,
    selfHostedConfig: { dockerCompose: "services/crawl4ai/docker-compose.yml", healthCheckUrl: "http://localhost:11235/health", defaultPort: 11235 },
  },
  {
    categoryName: "web_scraping", name: "apify", displayName: "Apify",
    description: "Web scraping platform with pre-built actors",
    scriptPath: "services/apify/scrape.py", apiKeyEnvVar: "APIFY_API_TOKEN",
    costInfo: "Free: $5/mo credits", useCases: ["web_scraping", "structured_data"],
    docsUrl: "https://apify.com/", defaultPriority: 3, integrationType: "script", freeTier: true,
  },

  // ── Web Search ──
  {
    categoryName: "web_search", name: "brave-search", displayName: "Brave Search",
    description: "Privacy-focused web search API",
    scriptPath: "services/brave-search/search.py", mcpServer: "brave-search", apiKeyEnvVar: "BRAVE_API_KEY",
    costInfo: "Free: 2K queries/mo", useCases: ["web_search", "research"],
    docsUrl: "https://brave.com/search/api/", defaultPriority: 1, integrationType: "mcp", freeTier: true,
  },
  {
    categoryName: "web_search", name: "perplexity-search", displayName: "Perplexity",
    description: "AI-powered search with cited answers",
    scriptPath: "services/perplexity/search.py", mcpServer: "perplexity", apiKeyEnvVar: "PERPLEXITY_API_KEY",
    costInfo: "Free tier available", useCases: ["web_search", "research", "summarization"],
    docsUrl: "https://docs.perplexity.ai/", defaultPriority: 2, integrationType: "mcp", freeTier: true,
  },
  {
    categoryName: "web_search", name: "google-custom-search", displayName: "Google Custom Search",
    description: "Google Programmable Search Engine API",
    scriptPath: "services/google-custom-search/search.py", apiKeyEnvVar: "GOOGLE_CSE_API_KEY",
    costInfo: "Free: 100/day, then $5/1K", useCases: ["web_search"],
    docsUrl: "https://developers.google.com/custom-search/", defaultPriority: 3, integrationType: "script", freeTier: true,
  },

  // ── Image Generation ──
  {
    categoryName: "image_generation", name: "fal-flux-pro", displayName: "FLUX.2 Pro (fal.ai)",
    description: "FLUX.2 Pro image generation via fal.ai",
    scriptPath: "services/fal-flux-pro/generate.py", mcpServer: "fal", apiKeyEnvVar: "FAL_KEY",
    costInfo: "$0.03/image", useCases: ["hero_images", "product_shots", "social_graphics"],
    docsUrl: "https://fal.ai/", defaultPriority: 1, integrationType: "mcp", freeTier: false,
  },
  {
    categoryName: "image_generation", name: "fal-flux-dev", displayName: "FLUX.2 Dev (fal.ai)",
    description: "FLUX.2 Dev — faster, cheaper image generation",
    scriptPath: "services/fal-flux-dev/generate.py", mcpServer: "fal", apiKeyEnvVar: "FAL_KEY",
    costInfo: "$0.01/image", useCases: ["drafts", "iterations", "social_graphics"],
    docsUrl: "https://fal.ai/", defaultPriority: 2, integrationType: "mcp", freeTier: false,
  },
  {
    categoryName: "image_generation", name: "together-images", displayName: "Together.ai Images",
    description: "Image generation via Together.ai (FLUX, SDXL)",
    scriptPath: "services/together-images/generate.py", mcpServer: "together", apiKeyEnvVar: "TOGETHER_API_KEY",
    costInfo: "$0.02/image", useCases: ["hero_images", "social_graphics"],
    docsUrl: "https://together.ai/", defaultPriority: 3, integrationType: "mcp", freeTier: false,
  },
  {
    categoryName: "image_generation", name: "recraft-v3", displayName: "Recraft v3",
    description: "Recraft v3 AI image and vector generation",
    scriptPath: "services/recraft-v3/generate.py", apiKeyEnvVar: "RECRAFT_API_KEY",
    costInfo: "$0.04/image", useCases: ["brand_graphics", "vector_art", "product_shots"],
    docsUrl: "https://recraft.ai/", defaultPriority: 4, integrationType: "script", freeTier: false,
  },
  {
    categoryName: "image_generation", name: "gpt-image", displayName: "GPT Image (OpenAI)",
    description: "OpenAI image generation (DALL-E / GPT-4o image)",
    scriptPath: "services/gpt-image/generate.py", apiKeyEnvVar: "OPENAI_API_KEY",
    costInfo: "$0.04/image", useCases: ["hero_images", "conceptual_art"],
    docsUrl: "https://platform.openai.com/docs/guides/images", defaultPriority: 5, integrationType: "script", freeTier: false,
  },
  {
    categoryName: "image_generation", name: "higgsfield-images", displayName: "Higgsfield AI Images",
    description: "Cinematic image generation — Nano Banana Pro (4K), Soul (character consistency), 8+ models. API priced per-call, not subscription.",
    scriptPath: "services/higgsfield-images/generate.py", apiKeyEnvVar: "HF_API_KEY",
    costInfo: "API: ~$0.23/image (Nano Banana Pro). Web subscription cheaper but not for API.", useCases: ["hero_images", "product_shots", "social_graphics", "cinematic_images"],
    docsUrl: "https://cloud.higgsfield.ai/", defaultPriority: 6, integrationType: "script", freeTier: true,
  },

  // ── Video Generation ──
  {
    categoryName: "video_generation", name: "together-video", displayName: "Together.ai Video",
    description: "AI video generation via Together.ai",
    scriptPath: "services/together-video/generate.py", mcpServer: "together", apiKeyEnvVar: "TOGETHER_API_KEY",
    costInfo: "~$0.50/clip", useCases: ["social_clips", "ad_videos"],
    docsUrl: "https://together.ai/", defaultPriority: 1, integrationType: "mcp", freeTier: false,
  },
  {
    categoryName: "video_generation", name: "runway-gen4", displayName: "Runway Gen-4",
    description: "Runway Gen-4 text/image-to-video",
    scriptPath: "services/runway-gen4/generate.py", apiKeyEnvVar: "RUNWAY_API_KEY",
    costInfo: "~$0.50/5s clip", useCases: ["product_videos", "ad_creatives"],
    docsUrl: "https://runwayml.com/", defaultPriority: 2, integrationType: "script", freeTier: false,
  },
  {
    categoryName: "video_generation", name: "pika-labs", displayName: "Pika Labs",
    description: "Pika text/image-to-video generation",
    scriptPath: "services/pika-labs/generate.py", apiKeyEnvVar: "PIKA_API_KEY",
    costInfo: "Free tier: 250 credits/mo", useCases: ["social_clips", "ad_videos"],
    docsUrl: "https://pika.art/", defaultPriority: 3, integrationType: "script", freeTier: true,
  },

  // ── Social: X/Twitter ──
  {
    categoryName: "social_x", name: "x-api-v2", displayName: "X API v2",
    description: "X/Twitter API for posting and analytics",
    scriptPath: "services/x-api/post.py", mcpServer: "twitter", apiKeyEnvVar: "X_BEARER_TOKEN",
    costInfo: "Free: read only, Basic $100/mo", useCases: ["social_posting", "analytics"],
    docsUrl: "https://developer.x.com/", defaultPriority: 1, integrationType: "mcp", freeTier: true,
  },

  // ── Social: Reddit ──
  {
    categoryName: "social_reddit", name: "reddit-api", displayName: "Reddit API",
    description: "Reddit API for monitoring and engagement",
    scriptPath: "services/reddit-api/query.py", mcpServer: "reddit", apiKeyEnvVar: "REDDIT_CLIENT_ID",
    costInfo: "Free: 100 req/min", useCases: ["social_monitoring", "engagement"],
    docsUrl: "https://www.reddit.com/dev/api/", defaultPriority: 1, integrationType: "mcp", freeTier: true,
  },

  // ── Social: YouTube ──
  {
    categoryName: "social_youtube", name: "youtube-data-api", displayName: "YouTube Data API",
    description: "YouTube video info, comments, search",
    scriptPath: "services/youtube-api/query.py", mcpServer: "youtube", apiKeyEnvVar: "YOUTUBE_API_KEY",
    costInfo: "Free: 10K units/day", useCases: ["video_research", "competitor_analysis"],
    docsUrl: "https://developers.google.com/youtube/", defaultPriority: 1, integrationType: "mcp", freeTier: true,
  },

  // ── Email Sending ──
  {
    categoryName: "email_sending", name: "resend", displayName: "Resend",
    description: "Modern email API for transactional and marketing emails",
    scriptPath: "services/resend/send.py", apiKeyEnvVar: "RESEND_API_KEY",
    costInfo: "Free: 3K emails/mo", useCases: ["transactional", "marketing_email"],
    docsUrl: "https://resend.com/docs", defaultPriority: 1, integrationType: "script", freeTier: true,
  },
  {
    categoryName: "email_sending", name: "sendgrid", displayName: "SendGrid",
    description: "Twilio SendGrid email delivery platform",
    scriptPath: "services/sendgrid/send.py", apiKeyEnvVar: "SENDGRID_API_KEY",
    costInfo: "Free: 100 emails/day", useCases: ["transactional", "marketing_email"],
    docsUrl: "https://docs.sendgrid.com/", defaultPriority: 2, integrationType: "script", freeTier: true,
  },
  {
    categoryName: "email_sending", name: "brevo", displayName: "Brevo",
    description: "Brevo (ex-Sendinblue) email marketing platform",
    scriptPath: "services/brevo/send.py", apiKeyEnvVar: "BREVO_API_KEY",
    costInfo: "Free: 300 emails/day", useCases: ["marketing_email", "automations"],
    docsUrl: "https://developers.brevo.com/", defaultPriority: 3, integrationType: "script", freeTier: true,
  },

  // ── Content Quality ──
  {
    categoryName: "content_quality", name: "languagetool", displayName: "LanguageTool",
    description: "Self-hosted grammar, style, and spell checker",
    scriptPath: "services/languagetool/check.py", apiKeyEnvVar: "LANGUAGETOOL_URL",
    costInfo: "Free (self-hosted)", useCases: ["grammar", "style", "spelling"],
    docsUrl: "https://languagetool.org/dev", defaultPriority: 1, integrationType: "local", freeTier: true,
    selfHostedConfig: { dockerCompose: "services/languagetool/docker-compose.yml", healthCheckUrl: "http://localhost:8081/v2/languages", defaultPort: 8081 },
  },
  {
    categoryName: "content_quality", name: "copyscape", displayName: "Copyscape",
    description: "Plagiarism detection API",
    scriptPath: "services/copyscape/check.py", apiKeyEnvVar: "COPYSCAPE_API_KEY",
    costInfo: "$0.05/search", useCases: ["plagiarism_check"],
    docsUrl: "https://www.copyscape.com/apiconfigure.php", defaultPriority: 2, integrationType: "script", freeTier: false,
  },

  // ── Notifications ──
  {
    categoryName: "notifications", name: "telegram-bot", displayName: "Telegram Bot",
    description: "Telegram Bot API for notifications and alerts",
    scriptPath: "services/telegram-bot/notify.py", apiKeyEnvVar: "TELEGRAM_BOT_TOKEN",
    costInfo: "Free", useCases: ["notifications", "alerts"],
    docsUrl: "https://core.telegram.org/bots/api", defaultPriority: 1, integrationType: "script", freeTier: true,
  },
  {
    categoryName: "notifications", name: "discord-webhook", displayName: "Discord Webhook",
    description: "Discord webhook for team notifications",
    scriptPath: "services/discord-webhook/notify.py", apiKeyEnvVar: "DISCORD_WEBHOOK_URL",
    costInfo: "Free", useCases: ["notifications", "team_alerts"],
    docsUrl: "https://discord.com/developers/docs/resources/webhook", defaultPriority: 2, integrationType: "script", freeTier: true,
  },

  // ── Document Generation ──
  {
    categoryName: "document_generation", name: "pandoc", displayName: "Pandoc",
    description: "Universal document converter — markdown to PDF/EPUB/DOCX",
    scriptPath: "services/pandoc/convert.py", apiKeyEnvVar: "",
    costInfo: "Free (local)", useCases: ["pdf", "epub", "docx"],
    docsUrl: "https://pandoc.org/", defaultPriority: 1, integrationType: "local", freeTier: true,
  },
  {
    categoryName: "document_generation", name: "calibre", displayName: "Calibre",
    description: "Ebook management and conversion (epub, mobi, pdf)",
    scriptPath: "services/calibre/convert.py", apiKeyEnvVar: "",
    costInfo: "Free (local)", useCases: ["epub", "mobi", "ebook"],
    docsUrl: "https://calibre-ebook.com/", defaultPriority: 2, integrationType: "local", freeTier: true,
  },

  // ── CMS Publishing ──
  {
    categoryName: "cms_publishing", name: "wordpress", displayName: "WordPress",
    description: "WordPress REST API for publishing posts and pages",
    scriptPath: "services/wordpress/publish.py", apiKeyEnvVar: "WP_APPLICATION_PASSWORD",
    costInfo: "Free (self-hosted)", useCases: ["blog_posts", "pages", "cms"],
    docsUrl: "https://developer.wordpress.org/rest-api/", defaultPriority: 1, integrationType: "script", freeTier: true,
  },
  {
    categoryName: "cms_publishing", name: "static-markdown", displayName: "Static Markdown",
    description: "Export as markdown files for static site generators",
    scriptPath: "services/static-markdown/export.py", apiKeyEnvVar: "",
    costInfo: "Free (local)", useCases: ["static_site", "hugo", "astro"],
    defaultPriority: 2, integrationType: "local", freeTier: true,
  },

  // ── Analytics ──
  {
    categoryName: "analytics", name: "gsc-analytics", displayName: "Google Search Console",
    description: "Organic search analytics from GSC",
    scriptPath: "services/google-search-console/analytics.py", apiKeyEnvVar: "GSC_SERVICE_ACCOUNT",
    costInfo: "Free", useCases: ["organic_traffic", "rankings", "ctr"],
    docsUrl: "https://search.google.com/search-console/", defaultPriority: 1, integrationType: "script", freeTier: true,
  },
  {
    categoryName: "analytics", name: "plausible", displayName: "Plausible Analytics",
    description: "Privacy-friendly website analytics",
    scriptPath: "services/plausible/query.py", apiKeyEnvVar: "PLAUSIBLE_API_KEY",
    costInfo: "Free (self-hosted) or $9/mo", useCases: ["page_views", "traffic_sources"],
    docsUrl: "https://plausible.io/docs", defaultPriority: 2, integrationType: "script", freeTier: true,
  },
];

export const seedProviders = mutation({
  args: {},
  handler: async (ctx) => {
    const results: string[] = [];
    let created = 0;
    let updated = 0;
    let errors = 0;

    for (const p of providers) {
      // Resolve category
      const category = await ctx.db
        .query("serviceCategories")
        .withIndex("by_name", (q) => q.eq("name", p.categoryName))
        .unique();
      if (!category) {
        results.push(`ERROR: Unknown category '${p.categoryName}' for ${p.name}`);
        errors++;
        continue;
      }

      // Check if exists
      const existing = await ctx.db
        .query("services")
        .withIndex("by_name", (q) => q.eq("name", p.name))
        .first();

      if (existing) {
        await ctx.db.patch(existing._id, {
          displayName: p.displayName,
          description: p.description,
          scriptPath: p.scriptPath,
          mcpServer: p.mcpServer,
          apiKeyEnvVar: p.apiKeyEnvVar,
          costInfo: p.costInfo,
          useCases: p.useCases,
          docsUrl: p.docsUrl,
          integrationType: p.integrationType,
          freeTier: p.freeTier,
          selfHostedConfig: p.selfHostedConfig,
        });
        updated++;
      } else {
        await ctx.db.insert("services", {
          categoryId: category._id,
          name: p.name,
          displayName: p.displayName,
          description: p.description,
          isActive: false,
          priority: p.defaultPriority,
          apiKeyEnvVar: p.apiKeyEnvVar,
          apiKeyConfigured: false,
          scriptPath: p.scriptPath,
          mcpServer: p.mcpServer,
          costInfo: p.costInfo,
          useCases: p.useCases,
          docsUrl: p.docsUrl,
          integrationType: p.integrationType,
          freeTier: p.freeTier,
          selfHostedConfig: p.selfHostedConfig,
        });
        created++;
      }
    }

    return { created, updated, errors, details: results };
  },
});
