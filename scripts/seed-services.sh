#!/usr/bin/env bash
# Seed service providers into Convex services table
# Run: bash scripts/seed-services.sh

set -euo pipefail

CONVEX_URL="http://localhost:3210"

create_service() {
  local json="$1"
  npx convex run services:create "$json" --url "$CONVEX_URL" 2>/dev/null && echo "  OK" || echo "  FAIL"
}

echo "=== Seeding Service Providers ==="
echo ""

# ── Category IDs (from Convex) ──
CAT_SEO="m975nnwb3fq7ce72btst546vdd80ybfd"
CAT_SERP="m97f71ve7x4hqwa79t17qjvvjh80ydwe"
CAT_SCRAPING="m97c6tpmw0wawc66njrx4sk72580y6bz"
CAT_SOCIAL_X="m978xe59jpyskf6tgp8saswcw180yfcs"
CAT_SOCIAL_REDDIT="m9720wsb84pd8gbqe9dree982h80zkxt"
CAT_SOCIAL_LINKEDIN="m9764h4z78e6zs7st161pkcah580zk9s"
CAT_SOCIAL_META="m978crmws6megkg46w6rr8xfws80y1mw"
CAT_SOCIAL_TIKTOK="m972ad8tm8tt7xmhhjnvwp18ed80zb5p"
CAT_SOCIAL_YOUTUBE="m972qsk5m5apc8mear0vxj68h180zzms"
CAT_IMAGE="m975tsys6n6hrpbphw59z1dv1h80zq9t"
CAT_TEMPLATED="m976tf1m4x6tvwa7zbmwdh0ypd80zgwm"
CAT_VIDEO="m97678hnf34bvsztvyhsvgqja180z2ps"
CAT_PRESENTER="m97ek59epys9982awkvabcwv1s80zfdp"
CAT_EMAIL="m97c60vxey50w0n0nszrn3qmts80ymm2"
CAT_SOCIAL_PUB="m974ts9ryqwrk9nza6geyrkx2580zsej"
CAT_CMS="m9780md3g8r0r3t4c2h1z2jetn80z8pk"
CAT_QUALITY="m97fcsyzp3tzkstw8vd4cnzf3x80ydyk"
CAT_SEARCH="m977mrzh875fp077w0338g5fr580zn1a"
CAT_ANALYTICS="m973dz6f5q5dghpbtc0feq3h0980zjcq"
CAT_DOCGEN="m975e5x8g31y1r2ff7j1nrcgfn80y761"
CAT_NOTIFY="m97a5ajp0fvdfha7002cbydk6580ywry"

# ═══════════════════════════════════════════
# 1. WEB SEARCH
# ═══════════════════════════════════════════
echo "--- Web Search ---"

echo -n "  Brave Search (free 2K/mo)..."
create_service "{\"categoryId\":\"$CAT_SEARCH\",\"name\":\"brave-search\",\"displayName\":\"Brave Search API\",\"description\":\"Web search with 2,000 free queries/month. Official Anthropic MCP server.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"BRAVE_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://brave-search\",\"mcpServer\":\"brave-search\",\"costInfo\":\"Free: 2K queries/mo. Paid: \$3/1K queries\",\"useCases\":[\"agent_research\",\"competitor_analysis\",\"trend_detection\"],\"docsUrl\":\"https://brave.com/search/api/\"}"

echo -n "  Perplexity (paid, \$1/M tokens)..."
create_service "{\"categoryId\":\"$CAT_SEARCH\",\"name\":\"perplexity\",\"displayName\":\"Perplexity Sonar\",\"description\":\"AI-powered web search with citations. Official MCP. Models: sonar, sonar-pro, sonar-deep-research.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"PERPLEXITY_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://perplexity\",\"mcpServer\":\"perplexity\",\"costInfo\":\"\$1/M input tokens, \$1/M output tokens. Pro subs get \$5/mo credit.\",\"useCases\":[\"deep_research\",\"fact_checking\",\"market_analysis\"],\"docsUrl\":\"https://docs.perplexity.ai/guides/mcp-server\"}"

echo -n "  Google Custom Search (free 100/day)..."
create_service "{\"categoryId\":\"$CAT_SEARCH\",\"name\":\"google-cse\",\"displayName\":\"Google Custom Search\",\"description\":\"Google search via Custom Search Engine API. Free 100 queries/day.\",\"isActive\":false,\"priority\":3,\"apiKeyEnvVar\":\"GOOGLE_CSE_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/search/google_search.py\",\"costInfo\":\"Free: 100/day. Paid: \$5/1K queries\",\"useCases\":[\"site_search\",\"specific_domain_search\"],\"docsUrl\":\"https://developers.google.com/custom-search/v1/overview\"}"

# ═══════════════════════════════════════════
# 2. SEO & KEYWORDS
# ═══════════════════════════════════════════
echo ""
echo "--- SEO & Keywords ---"

echo -n "  DataForSEO (\$1 free credit)..."
create_service "{\"categoryId\":\"$CAT_SEO\",\"name\":\"dataforseo\",\"displayName\":\"DataForSEO\",\"description\":\"Keyword research, search volume, difficulty, SERP data. Official MCP. \$1 free credit on signup.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"DATAFORSEO_LOGIN\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://dataforseo\",\"mcpServer\":\"dataforseo\",\"costInfo\":\"\$1 free credit. Then \$0.60/1K SERP queries. \$50 min top-up.\",\"useCases\":[\"keyword_research\",\"search_volume\",\"keyword_difficulty\",\"serp_analysis\"],\"docsUrl\":\"https://dataforseo.com/apis\"}"

echo -n "  Google Keyword Planner (free)..."
create_service "{\"categoryId\":\"$CAT_SEO\",\"name\":\"google-kp\",\"displayName\":\"Google Keyword Planner\",\"description\":\"Free keyword ideas and search volume via Google Ads API. Requires Google Ads account (free to create).\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"GOOGLE_ADS_DEVELOPER_TOKEN\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/seo/query_gkp.py\",\"costInfo\":\"Free (requires Google Ads account)\",\"useCases\":[\"keyword_ideas\",\"search_volume_estimates\"],\"docsUrl\":\"https://developers.google.com/google-ads/api/docs/start\"}"

# ═══════════════════════════════════════════
# 3. SERP TRACKING
# ═══════════════════════════════════════════
echo ""
echo "--- SERP & Rank Tracking ---"

echo -n "  Google Search Console (free)..."
create_service "{\"categoryId\":\"$CAT_SERP\",\"name\":\"google-search-console\",\"displayName\":\"Google Search Console\",\"description\":\"Free rank tracking, search queries, click data. Requires site verification.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"GSC_SERVICE_ACCOUNT_JSON\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/seo/query_gsc.py\",\"costInfo\":\"Free\",\"useCases\":[\"rank_tracking\",\"search_queries\",\"click_data\",\"indexing_status\"],\"docsUrl\":\"https://developers.google.com/webmaster-tools/v1/api_reference_index\"}"

# ═══════════════════════════════════════════
# 4. WEB SCRAPING
# ═══════════════════════════════════════════
echo ""
echo "--- Web Scraping ---"

echo -n "  Crawl4AI (free, self-hosted)..."
create_service "{\"categoryId\":\"$CAT_SCRAPING\",\"name\":\"crawl4ai\",\"displayName\":\"Crawl4AI (Self-Hosted)\",\"description\":\"Free self-hosted web scraper. Docker container on port 11235. MCP server available.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"CRAWL4AI_URL\",\"apiKeyConfigured\":false,\"extraConfig\":\"http://localhost:11235\",\"scriptPath\":\"mcp://crawl4ai\",\"mcpServer\":\"crawl4ai\",\"costInfo\":\"Free (self-hosted Docker)\",\"useCases\":[\"batch_scraping\",\"content_extraction\",\"competitor_pages\"],\"docsUrl\":\"https://github.com/unclecode/crawl4ai\"}"

echo -n "  Firecrawl (500 free credits)..."
create_service "{\"categoryId\":\"$CAT_SCRAPING\",\"name\":\"firecrawl\",\"displayName\":\"Firecrawl\",\"description\":\"LLM-ready markdown scraping. Official MCP. 500 free credits on signup. Best for JS-heavy sites.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"FIRECRAWL_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://firecrawl\",\"mcpServer\":\"firecrawl\",\"costInfo\":\"500 free credits. Hobby: \$19/mo (3K credits)\",\"useCases\":[\"js_rendered_scraping\",\"llm_ready_markdown\",\"site_crawling\"],\"docsUrl\":\"https://docs.firecrawl.dev/\"}"

# ═══════════════════════════════════════════
# 5. SOCIAL: REDDIT
# ═══════════════════════════════════════════
echo ""
echo "--- Social: Reddit ---"

echo -n "  Reddit MCP (free, no API key)..."
create_service "{\"categoryId\":\"$CAT_SOCIAL_REDDIT\",\"name\":\"reddit-mcp\",\"displayName\":\"Reddit MCP (Read-Only)\",\"description\":\"Free read-only Reddit access via public API. No API key needed. Subreddits, posts, comments.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"NONE\",\"apiKeyConfigured\":true,\"scriptPath\":\"mcp://reddit\",\"mcpServer\":\"reddit\",\"costInfo\":\"Free (public API, read-only)\",\"useCases\":[\"subreddit_monitoring\",\"trend_detection\",\"audience_research\"],\"docsUrl\":\"https://github.com/Hawstein/mcp-server-reddit\"}"

# ═══════════════════════════════════════════
# 6. SOCIAL: X/TWITTER
# ═══════════════════════════════════════════
echo ""
echo "--- Social: X/Twitter ---"

echo -n "  Twitter MCP (free tier 1,500/mo)..."
create_service "{\"categoryId\":\"$CAT_SOCIAL_X\",\"name\":\"twitter-mcp\",\"displayName\":\"Twitter/X MCP\",\"description\":\"Post tweets, search tweets. Free tier: 1,500 tweets/mo write. Requires developer account.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"TWITTER_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://twitter\",\"mcpServer\":\"twitter\",\"costInfo\":\"Free: 1,500 tweets/mo write. Basic: \$100/mo\",\"useCases\":[\"social_monitoring\",\"trend_analysis\",\"content_research\"],\"docsUrl\":\"https://github.com/EnesCinr/twitter-mcp\"}"

# ═══════════════════════════════════════════
# 7. SOCIAL: YOUTUBE
# ═══════════════════════════════════════════
echo ""
echo "--- Social: YouTube ---"

echo -n "  YouTube MCP (free, no API key)..."
create_service "{\"categoryId\":\"$CAT_SOCIAL_YOUTUBE\",\"name\":\"youtube-mcp\",\"displayName\":\"YouTube Transcript MCP\",\"description\":\"Free YouTube transcript extraction via yt-dlp. No API key needed. Great for content research.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"NONE\",\"apiKeyConfigured\":true,\"scriptPath\":\"mcp://youtube\",\"mcpServer\":\"youtube\",\"costInfo\":\"Free (uses yt-dlp)\",\"useCases\":[\"video_transcripts\",\"content_research\",\"competitor_video_analysis\"],\"docsUrl\":\"https://github.com/anaisbetts/mcp-youtube\"}"

echo -n "  YouTube Data API v3 (free 10K/day)..."
create_service "{\"categoryId\":\"$CAT_SOCIAL_YOUTUBE\",\"name\":\"youtube-data-api\",\"displayName\":\"YouTube Data API v3\",\"description\":\"Official YouTube API. Search videos, channel stats, engagement metrics. Free 10K quota units/day.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"YOUTUBE_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/social/youtube_api.py\",\"costInfo\":\"Free: 10K quota units/day\",\"useCases\":[\"video_search\",\"channel_analytics\",\"engagement_metrics\"],\"docsUrl\":\"https://developers.google.com/youtube/v3\"}"

# ═══════════════════════════════════════════
# 8. IMAGE GENERATION
# ═══════════════════════════════════════════
echo ""
echo "--- Image Generation ---"

echo -n "  Together AI / Flux Schnell (FREE)..."
create_service "{\"categoryId\":\"$CAT_IMAGE\",\"name\":\"together-ai\",\"displayName\":\"Together AI (Free Flux)\",\"description\":\"Free Flux.1 Schnell model for image generation. Zero cost. Good quality for drafts and social media.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"TOGETHER_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://together\",\"mcpServer\":\"together\",\"costInfo\":\"Free: Flux.1 Schnell-Free model. \$1 credit on signup.\",\"useCases\":[\"social_graphics\",\"blog_images\",\"quick_drafts\"],\"docsUrl\":\"https://github.com/manascb1344/together-mcp-server\"}"

echo -n "  fal.ai (free credits, \$0.025/img)..."
create_service "{\"categoryId\":\"$CAT_IMAGE\",\"name\":\"fal-ai\",\"displayName\":\"fal.ai (FLUX Pro/Dev)\",\"description\":\"600+ AI models. FLUX Pro for hero images, FLUX Dev for drafts. Free credits on signup.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"FAL_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://fal\",\"mcpServer\":\"fal\",\"costInfo\":\"Free credits on signup. FLUX Dev: \$0.025/img. Pro: \$0.05/img.\",\"useCases\":[\"hero_images\",\"product_shots\",\"photorealism\",\"bulk_generation\"],\"docsUrl\":\"https://fal.ai/models\"}"

echo -n "  Recraft V3 (free 50/day)..."
create_service "{\"categoryId\":\"$CAT_IMAGE\",\"name\":\"recraft\",\"displayName\":\"Recraft V3\",\"description\":\"Vector/SVG generation, icons, text positioning. Official Anthropic MCP. Free 50 images/day.\",\"isActive\":false,\"priority\":3,\"apiKeyEnvVar\":\"RECRAFT_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://recraft\",\"mcpServer\":\"recraft\",\"costInfo\":\"Free: 50/day. Paid: \$10-48/mo\",\"useCases\":[\"vector_graphics\",\"icons\",\"text_in_images\",\"brand_assets\"],\"docsUrl\":\"https://www.recraft.ai/\"}"

# ═══════════════════════════════════════════
# 9. EMAIL SENDING
# ═══════════════════════════════════════════
echo ""
echo "--- Email Sending ---"

echo -n "  Resend (free 3K/mo)..."
create_service "{\"categoryId\":\"$CAT_EMAIL\",\"name\":\"resend\",\"displayName\":\"Resend\",\"description\":\"Modern email API. 3,000 emails/month free. Official MCP server. Simple developer-friendly API.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"RESEND_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://resend\",\"mcpServer\":\"resend\",\"costInfo\":\"Free: 3K emails/mo (100/day). Paid: \$20/mo (50K)\",\"useCases\":[\"transactional_email\",\"marketing_campaigns\",\"drip_sequences\"],\"docsUrl\":\"https://resend.com/docs\"}"

echo -n "  SendGrid (free 100/day)..."
create_service "{\"categoryId\":\"$CAT_EMAIL\",\"name\":\"sendgrid\",\"displayName\":\"SendGrid\",\"description\":\"Email delivery with templates, contact lists, stats. Free 100 emails/day. Community MCP.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"SENDGRID_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/email/sendgrid.py\",\"mcpServer\":\"sendgrid\",\"costInfo\":\"Free: 100/day. Essentials: \$20/mo\",\"useCases\":[\"bulk_email\",\"templates\",\"marketing_campaigns\"],\"docsUrl\":\"https://docs.sendgrid.com/\"}"

# ═══════════════════════════════════════════
# 10. CONTENT QUALITY
# ═══════════════════════════════════════════
echo ""
echo "--- Content Quality ---"

echo -n "  LanguageTool (free, self-hosted)..."
create_service "{\"categoryId\":\"$CAT_QUALITY\",\"name\":\"languagetool\",\"displayName\":\"LanguageTool (Self-Hosted)\",\"description\":\"Free self-hosted grammar and style checker. Docker container on port 8081. Unlimited checks.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"LANGUAGETOOL_URL\",\"apiKeyConfigured\":false,\"extraConfig\":\"http://localhost:8081\",\"scriptPath\":\"scripts/services/quality/languagetool.py\",\"costInfo\":\"Free (self-hosted Docker)\",\"useCases\":[\"grammar_check\",\"style_check\",\"readability\"],\"docsUrl\":\"https://languagetool.org/dev\"}"

echo -n "  Copyscape (\$0.03/check)..."
create_service "{\"categoryId\":\"$CAT_QUALITY\",\"name\":\"copyscape\",\"displayName\":\"Copyscape\",\"description\":\"Plagiarism detection. \$0.03 per check. No free tier but very cheap.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"COPYSCAPE_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/quality/copyscape.py\",\"costInfo\":\"\$0.03/check (~\$2/mo for 60 articles)\",\"useCases\":[\"plagiarism_detection\",\"content_originality\"],\"docsUrl\":\"https://www.copyscape.com/apiconfigure.php\"}"

# ═══════════════════════════════════════════
# 11. DOCUMENT GENERATION
# ═══════════════════════════════════════════
echo ""
echo "--- Document Generation ---"

echo -n "  Pandoc (free, local)..."
create_service "{\"categoryId\":\"$CAT_DOCGEN\",\"name\":\"pandoc\",\"displayName\":\"Pandoc\",\"description\":\"Universal document converter. Markdown to HTML, PDF, DOCX, EPUB. Free, runs locally.\",\"isActive\":true,\"priority\":1,\"apiKeyEnvVar\":\"NONE\",\"apiKeyConfigured\":true,\"scriptPath\":\"pandoc\",\"costInfo\":\"Free (local tool)\",\"useCases\":[\"md_to_html\",\"md_to_pdf\",\"md_to_docx\",\"ebook_generation\"],\"docsUrl\":\"https://pandoc.org/\"}"

# ═══════════════════════════════════════════
# 12. NOTIFICATIONS
# ═══════════════════════════════════════════
echo ""
echo "--- Notifications ---"

echo -n "  Telegram Bot (free)..."
create_service "{\"categoryId\":\"$CAT_NOTIFY\",\"name\":\"telegram\",\"displayName\":\"Telegram Bot\",\"description\":\"Free push notifications via Telegram Bot API. Create bot via @BotFather. MCP available.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"TELEGRAM_BOT_TOKEN\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/notifications/telegram_notify.py\",\"costInfo\":\"Free\",\"useCases\":[\"task_alerts\",\"pipeline_completion\",\"error_notifications\"],\"docsUrl\":\"https://core.telegram.org/bots/api\"}"

echo -n "  Slack (free)..."
create_service "{\"categoryId\":\"$CAT_NOTIFY\",\"name\":\"slack\",\"displayName\":\"Slack\",\"description\":\"Team notifications via Slack Bot. Official Anthropic MCP server. Free with Slack workspace.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"SLACK_BOT_TOKEN\",\"apiKeyConfigured\":false,\"scriptPath\":\"mcp://slack\",\"mcpServer\":\"slack\",\"costInfo\":\"Free (with Slack workspace)\",\"useCases\":[\"team_alerts\",\"pipeline_updates\",\"review_requests\"],\"docsUrl\":\"https://api.slack.com/\"}"

echo -n "  Discord (free)..."
create_service "{\"categoryId\":\"$CAT_NOTIFY\",\"name\":\"discord\",\"displayName\":\"Discord Webhook\",\"description\":\"Community notifications via Discord webhooks. Free.\",\"isActive\":false,\"priority\":3,\"apiKeyEnvVar\":\"DISCORD_WEBHOOK_URL\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/notifications/discord_notify.py\",\"costInfo\":\"Free\",\"useCases\":[\"community_alerts\",\"public_updates\"],\"docsUrl\":\"https://discord.com/developers/docs/resources/webhook\"}"

# ═══════════════════════════════════════════
# 13. ANALYTICS
# ═══════════════════════════════════════════
echo ""
echo "--- Analytics ---"

echo -n "  Google Analytics 4 (free)..."
create_service "{\"categoryId\":\"$CAT_ANALYTICS\",\"name\":\"google-analytics\",\"displayName\":\"Google Analytics 4\",\"description\":\"Free web analytics. Traffic, user behavior, conversions. Official Google MCP.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"GA4_PROPERTY_ID\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/analytics/ga4_analytics.py\",\"costInfo\":\"Free\",\"useCases\":[\"traffic_analysis\",\"user_behavior\",\"conversion_tracking\"],\"docsUrl\":\"https://developers.google.com/analytics\"}"

# ═══════════════════════════════════════════
# 14. CMS PUBLISHING
# ═══════════════════════════════════════════
echo ""
echo "--- CMS Publishing ---"

echo -n "  WordPress (free, official MCP)..."
create_service "{\"categoryId\":\"$CAT_CMS\",\"name\":\"wordpress\",\"displayName\":\"WordPress REST API\",\"description\":\"Publish to WordPress sites. Official MCP adapter (WP plugin). Free.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"WORDPRESS_APP_PASSWORD\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/publishing/wp_publish.py\",\"costInfo\":\"Free\",\"useCases\":[\"blog_publishing\",\"page_creation\",\"content_management\"],\"docsUrl\":\"https://developer.wordpress.org/rest-api/\"}"

echo -n "  Static Markdown (free, built-in)..."
create_service "{\"categoryId\":\"$CAT_CMS\",\"name\":\"static-markdown\",\"displayName\":\"Static (Markdown Files)\",\"description\":\"Write content as markdown files to campaign folders. No external service needed. Always available.\",\"isActive\":true,\"priority\":5,\"apiKeyEnvVar\":\"NONE\",\"apiKeyConfigured\":true,\"scriptPath\":\"scripts/services/publishing/static_publish.py\",\"costInfo\":\"Free (local files)\",\"useCases\":[\"draft_output\",\"static_sites\",\"manual_publishing\"],\"docsUrl\":\"\"}"

# ═══════════════════════════════════════════
# 15. SOCIAL PUBLISHING
# ═══════════════════════════════════════════
echo ""
echo "--- Social Publishing ---"

echo -n "  Buffer (free tier)..."
create_service "{\"categoryId\":\"$CAT_SOCIAL_PUB\",\"name\":\"buffer\",\"displayName\":\"Buffer\",\"description\":\"Social media scheduling. Free plan: 3 channels, 10 posts/channel. Paid: \$6/channel/mo.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"BUFFER_ACCESS_TOKEN\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/social/buffer_post.py\",\"costInfo\":\"Free: 3 channels, 10 posts each. Paid: \$6/channel/mo\",\"useCases\":[\"social_scheduling\",\"multi_platform_posting\"],\"docsUrl\":\"https://buffer.com/developers/api\"}"

# ═══════════════════════════════════════════
# 16. VIDEO GENERATION
# ═══════════════════════════════════════════
echo ""
echo "--- Video Generation ---"

echo -n "  Pika Labs (free tier)..."
create_service "{\"categoryId\":\"$CAT_VIDEO\",\"name\":\"pika\",\"displayName\":\"Pika Labs 2.0\",\"description\":\"AI video generation. Free tier with limited daily credits. Good for short social content.\",\"isActive\":false,\"priority\":1,\"apiKeyEnvVar\":\"PIKA_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/video/pika_generate.py\",\"costInfo\":\"Free tier (limited). Paid: \$8+/mo\",\"useCases\":[\"social_clips\",\"short_videos\",\"ad_teasers\"],\"docsUrl\":\"https://pika.art/\"}"

echo -n "  Runway Gen-4 (\$12+/mo)..."
create_service "{\"categoryId\":\"$CAT_VIDEO\",\"name\":\"runway\",\"displayName\":\"Runway Gen-4\",\"description\":\"Premium AI video generation. 4K output, motion control. Best quality.\",\"isActive\":false,\"priority\":2,\"apiKeyEnvVar\":\"RUNWAY_API_KEY\",\"apiKeyConfigured\":false,\"scriptPath\":\"scripts/services/video/runway_generate.py\",\"costInfo\":\"\$12-76/mo depending on plan\",\"useCases\":[\"hero_videos\",\"ad_videos\",\"4k_content\"],\"docsUrl\":\"https://runwayml.com/\"}"

echo ""
echo "=== Done! Seeded service providers. ==="
echo ""
echo "Run 'npx convex run services:listActive {} --url http://localhost:3210' to verify."
