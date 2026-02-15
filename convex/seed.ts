import { internalMutation, mutation } from "./_generated/server";

// ═══════════════════════════════════════════
// SEED DATA — Runs once on first deploy via:
//   npx convex run seed:run --url http://localhost:3210
// Idempotent: skips if data already exists.
// ═══════════════════════════════════════════

export const run = internalMutation({
  args: {},
  handler: async (ctx) => {
    const results: string[] = [];

    // ── Service Categories ──
    const existingServiceCats = await ctx.db.query("serviceCategories").collect();
    if (existingServiceCats.length === 0) {
      const serviceCategories = [
        { name: "seo_keywords", displayName: "SEO & Keywords", description: "Keyword research, search volume, difficulty analysis", icon: "🔍", sortOrder: 1 },
        { name: "serp_tracking", displayName: "SERP & Rank Tracking", description: "Search result positions, rank monitoring", icon: "📊", sortOrder: 2 },
        { name: "web_scraping", displayName: "Web Scraping", description: "Website content extraction, crawling", icon: "🕷️", sortOrder: 3 },
        { name: "social_x", displayName: "Social: X/Twitter", description: "X/Twitter data collection and monitoring", icon: "𝕏", sortOrder: 4 },
        { name: "social_reddit", displayName: "Social: Reddit", description: "Reddit discussions, trends, sentiment", icon: "🤖", sortOrder: 5 },
        { name: "social_linkedin", displayName: "Social: LinkedIn", description: "LinkedIn profiles, companies, posts", icon: "💼", sortOrder: 6 },
        { name: "social_meta", displayName: "Social: Facebook/Instagram", description: "Meta platform data and insights", icon: "📱", sortOrder: 7 },
        { name: "social_tiktok", displayName: "Social: TikTok", description: "TikTok trends and content analysis", icon: "🎵", sortOrder: 8 },
        { name: "social_youtube", displayName: "Social: YouTube", description: "YouTube videos, channels, analytics", icon: "▶️", sortOrder: 9 },
        { name: "image_generation", displayName: "Image Generation", description: "AI image creation (hero images, product shots, graphics)", icon: "🎨", sortOrder: 10 },
        { name: "templated_images", displayName: "Templated Images", description: "Social graphics, banners from templates", icon: "🖼️", sortOrder: 11 },
        { name: "video_generation", displayName: "Video Generation", description: "AI video creation (ads, social clips)", icon: "🎬", sortOrder: 12 },
        { name: "ai_presenter", displayName: "AI Presenter", description: "Talking head / avatar videos", icon: "🧑‍💼", sortOrder: 13 },
        { name: "email_sending", displayName: "Email Sending", description: "Transactional and marketing email delivery", icon: "📧", sortOrder: 14 },
        { name: "social_publishing", displayName: "Social Publishing", description: "Auto-posting to social platforms", icon: "📤", sortOrder: 15 },
        { name: "cms_publishing", displayName: "CMS Publishing", description: "Content publishing to CMS platforms", icon: "📝", sortOrder: 16 },
        { name: "content_quality", displayName: "Content Quality", description: "Plagiarism checking, grammar, readability", icon: "✅", sortOrder: 17 },
        { name: "web_search", displayName: "Web Search", description: "General web search for agent research", icon: "🌐", sortOrder: 18 },
        { name: "analytics", displayName: "Analytics & Tracking", description: "Traffic, rankings, performance data", icon: "📈", sortOrder: 19 },
        { name: "document_generation", displayName: "Document Generation", description: "PDF, EPUB, DOCX creation from markdown", icon: "📄", sortOrder: 20 },
        { name: "notifications", displayName: "Notifications", description: "Alerts via Telegram, Discord, Slack", icon: "🔔", sortOrder: 21 },
      ];
      for (const cat of serviceCategories) {
        await ctx.db.insert("serviceCategories", cat);
      }
      results.push(`Seeded ${serviceCategories.length} service categories`);
    } else {
      results.push(`Service categories already exist (${existingServiceCats.length}), skipping`);
    }

    // ── Skill Categories ──
    const existingSkillCats = await ctx.db.query("skillCategories").collect();
    if (existingSkillCats.length === 0) {
      const skillCategories = [
        { key: "L1_audience", displayName: "L1: Audience Awareness", description: "Auto-active. Routes copy via Awareness × Sophistication matrix.", sortOrder: 10, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "single", pipelineAgentNames: ["vibe-content-writer", "vibe-email-writer", "vibe-social-writer", "vibe-ad-writer"] },
        { key: "L2_offer", displayName: "L2: Offer Framework", description: "Frameworks for structuring irresistible offers.", sortOrder: 20, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "single", pipelineAgentNames: ["vibe-content-writer", "vibe-landing-page-writer", "vibe-ad-writer", "vibe-email-writer"] },
        { key: "L3_persuasion", displayName: "L3: Persuasion & Narrative", description: "Psychological influence and storytelling frameworks.", sortOrder: 30, scope: "copy" as const, maxPerPipelineStep: 2, selectionMode: "multiple", pipelineAgentNames: ["vibe-content-writer", "vibe-landing-page-writer", "vibe-ad-writer", "vibe-email-writer", "vibe-social-writer"] },
        { key: "L4_craft", displayName: "L4: Copy Style", description: "Headline formulas, body copy style, writing techniques.", sortOrder: 40, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "single", pipelineAgentNames: ["vibe-content-writer", "vibe-landing-page-writer", "vibe-email-writer"] },
        { key: "L5_quality", displayName: "L5: Quality", description: "Auto-active. AI pattern removal and clarity rules.", sortOrder: 50, scope: "quality" as const, maxPerPipelineStep: 2, selectionMode: "single", pipelineAgentNames: ["vibe-content-writer", "vibe-email-writer", "vibe-social-writer"] },
        { key: "research", displayName: "Research & Analysis", description: "How agents gather and analyze audience information.", sortOrder: 6, scope: "research" as const },
        { key: "content", displayName: "Content Production", description: "Format-specific guides (email, social, ads, ebook, video).", sortOrder: 7, scope: "general" as const },
        { key: "media", displayName: "Visual & Media", description: "Image prompt engineering and generation procedures.", sortOrder: 8, scope: "visual" as const },
        { key: "marketing", displayName: "Marketing & CRO", description: "Marketing strategy, CRO, SEO, and growth skills.", sortOrder: 9, scope: "general" as const },
        { key: "audience", displayName: "Audience Operations", description: "Audience enrichment and profiling procedures.", sortOrder: 11, scope: "research" as const },
        { key: "quality", displayName: "Quality Assurance", description: "Content review rubrics and quality scoring.", sortOrder: 12, scope: "quality" as const },
        { key: "utility", displayName: "Utility", description: "Cross-cutting agent SOPs and writing procedures.", sortOrder: 13, scope: "general" as const },
      ];
      for (const cat of skillCategories) {
        await ctx.db.insert("skillCategories", cat);
      }
      results.push(`Seeded ${skillCategories.length} skill categories`);
    } else {
      results.push(`Skill categories already exist (${existingSkillCats.length}), skipping`);
    }

    // ── Skills ──
    const existingSkills = await ctx.db.query("skills").collect();
    const skillIdMap: Record<string, any> = {};
    if (existingSkills.length === 0) {
      const skills = [
        // L1: Audience Awareness
        { slug: "mbook-schwarz-awareness", name: "mbook-schwarz-awareness", displayName: "Schwartz Awareness Levels", description: "Routes copy via 5 Stages of Awareness × Market Sophistication matrix. Determines opening strategy based on where the reader is.", category: "L1_audience", type: "mbook" as const, isAutoActive: true, isCampaignSelectable: false, filePath: ".claude/skills/mbook-schwarz-awareness/SKILL.md", tagline: "Know your reader before you write", dashboardDescription: "Auto-applied. Routes content strategy through Awareness × Sophistication matrix." },
        // L2: Offer Framework
        { slug: "mbook-brunson-dotcom", name: "mbook-brunson-dotcom", displayName: "Brunson DotCom Funnels", description: "Build sales funnels and email sequences using the Value Ladder, funnel types, and traffic strategies.", category: "L2_offer", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-brunson-dotcom/SKILL.md", tagline: "Every business is one funnel away", dashboardDescription: "Sales funnel architecture. Best for funnel copy, email sequences, upsell flows." },
        { slug: "mbook-brunson-expert", name: "mbook-brunson-expert", displayName: "Brunson Expert Secrets", description: "Authority positioning, origin stories, the Epiphany Bridge, and mass movement frameworks.", category: "L2_offer", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-brunson-expert/SKILL.md", tagline: "Create a mass movement of people who pay", dashboardDescription: "Expert positioning frameworks. Best for webinars, authority content, origin stories." },
        { slug: "mbook-hormozi-leads", name: "mbook-hormozi-leads", displayName: "Hormozi Lead Generation", description: "Lead magnet frameworks, lead generation copy, outreach scripts, and audience-building funnels.", category: "L2_offer", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-hormozi-leads/SKILL.md", tagline: "Turn strangers into leads at scale", dashboardDescription: "Lead generation frameworks. Best for lead magnets, outreach, audience building." },
        { slug: "mbook-hormozi-offers", name: "mbook-hormozi-offers", displayName: "Hormozi Value Equation", description: "Structure irresistible offers using the Value Equation: Dream Outcome × Perceived Likelihood / Time Delay × Effort & Sacrifice.", category: "L2_offer", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-hormozi-offers/SKILL.md", tagline: "Make offers so good people feel stupid saying no", dashboardDescription: "Value Equation framework for structuring offers. Best for landing pages, sales pages, ad copy." },
        // L3: Persuasion & Narrative
        { slug: "mbook-cialdini-influence", name: "mbook-cialdini-influence", displayName: "Cialdini Influence Principles", description: "Apply the 7 principles of persuasion: Reciprocity, Liking, Social Proof, Authority, Scarcity, Commitment/Consistency, Unity.", category: "L3_persuasion", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-cialdini-influence/SKILL.md", tagline: "The science of ethical persuasion", dashboardDescription: "7 persuasion principles with sub-selections. Best for any persuasive content.", subSelections: [{ key: "reciprocity", label: "Reciprocity", description: "Give value first to create obligation" }, { key: "liking", label: "Liking", description: "Build rapport and similarity" }, { key: "social_proof", label: "Social Proof", description: "Show others doing the same thing" }, { key: "authority", label: "Authority", description: "Establish expertise and credibility" }, { key: "scarcity", label: "Scarcity", description: "Limited availability creates urgency" }, { key: "commitment", label: "Commitment/Consistency", description: "Small yeses lead to big yeses" }, { key: "unity", label: "Unity", description: "Shared identity and belonging" }] },
        { slug: "mbook-miller-storybrand", name: "mbook-miller-storybrand", displayName: "Miller StoryBrand", description: "Structure marketing messages using the 7-part StoryBrand framework: Character, Problem, Guide, Plan, CTA, Failure, Success.", category: "L3_persuasion", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-miller-storybrand/SKILL.md", tagline: "Make the customer the hero", dashboardDescription: "Narrative framework. Best for brand messaging, ebooks, video scripts, website copy." },
        { slug: "mbook-sugarman-copywriting", name: "mbook-sugarman-copywriting", displayName: "Sugarman Psychological Triggers", description: "Apply the Slippery Slide framework and 31 Psychological Triggers for compelling copy.", category: "L3_persuasion", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-sugarman-copywriting/SKILL.md", tagline: "Every sentence sells the next sentence", dashboardDescription: "Psychological triggers with sub-selections. Best for email, social, short-form copy.", subSelections: [{ key: "curiosity", label: "Curiosity", description: "Open loops that compel reading" }, { key: "storytelling", label: "Storytelling", description: "Narrative hooks and payoffs" }, { key: "specificity", label: "Specificity", description: "Concrete details build credibility" }, { key: "urgency", label: "Urgency", description: "Time pressure and deadlines" }, { key: "exclusivity", label: "Exclusivity", description: "Limited access creates desire" }] },
        { slug: "mbook-voss-negotiation", name: "mbook-voss-negotiation", displayName: "Voss Tactical Empathy", description: "Apply tactical empathy, mirroring, labeling, and calibrated questions to marketing copy.", category: "L3_persuasion", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-voss-negotiation/SKILL.md", tagline: "Never split the difference with your reader", dashboardDescription: "Tactical empathy for copy. Best for objection handling, email sequences, video scripts." },
        { slug: "mbook-berger-contagious", name: "mbook-berger-contagious", displayName: "Berger Contagious STEPPS", description: "Apply the 6 STEPPS principles of virality: Social Currency, Triggers, Emotion, Public, Practical Value, Stories. Score content for shareability and engineer word-of-mouth.", category: "L3_persuasion", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-berger-contagious/SKILL.md", tagline: "Will anyone share this?", dashboardDescription: "Virality and shareability framework. Best for social content, launch campaigns, referral programs, any content that needs to spread.", subSelections: [{ key: "social_currency", label: "Social Currency", description: "Make sharing make the sharer look good" }, { key: "triggers", label: "Triggers", description: "Tie content to everyday environmental cues" }, { key: "emotion", label: "Emotion", description: "Evoke high-arousal emotions (awe, humor, anger)" }, { key: "public", label: "Public", description: "Make behavior observable and imitable" }, { key: "practical_value", label: "Practical Value", description: "Package useful content for forwarding" }, { key: "stories", label: "Stories", description: "Embed message in narratives people retell" }] },
        // L4: Copy Style
        { slug: "mbook-halbert-boron", name: "mbook-halbert-boron", displayName: "Halbert Direct Response", description: "Direct response copywriting fundamentals: A-pile mail, headline formulas, urgency, personal tone.", category: "L4_craft", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-halbert-boron/SKILL.md", tagline: "Write like you are talking to one person", dashboardDescription: "Direct response style. Best for sales letters, email, ad copy, landing pages." },
        { slug: "mbook-ogilvy-advertising", name: "mbook-ogilvy-advertising", displayName: "Ogilvy Advertising Craft", description: "David Ogilvy advertising craft: headline rules, body copy techniques, research-driven advertising.", category: "L4_craft", type: "mbook" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/mbook-ogilvy-advertising/SKILL.md", tagline: "The consumer is not a moron, she is your wife", dashboardDescription: "Advertising craft style. Best for brand content, blog posts, authority articles." },
        // L5: Quality
        { slug: "humanizer", name: "humanizer", displayName: "Humanizer", description: "Removes signs of AI-generated writing. Applied as a post-processing pass.", category: "L5_quality", type: "procedure" as const, isAutoActive: true, isCampaignSelectable: false, filePath: ".claude/skills/humanizer/SKILL.md", tagline: "Remove AI writing patterns", dashboardDescription: "Auto-applied post-processing. Removes AI-generated writing patterns from final content." },
        { slug: "writing-clearly-and-concisely", name: "writing-clearly-and-concisely", displayName: "Writing Clearly & Concisely", description: "Applies Strunk-style rules for clear, concise prose. Runs during content generation.", category: "L5_quality", type: "procedure" as const, isAutoActive: true, isCampaignSelectable: false, filePath: ".claude/skills/writing-clearly-and-concisely/SKILL.md", tagline: "Omit needless words", dashboardDescription: "Auto-applied during writing. Enforces Strunk-style clarity and conciseness rules." },
        // Audience
        { slug: "audience-enrichment-procedures", name: "audience-enrichment-procedures", displayName: "Audience Enrichment Procedures", description: "SOP for vibe-audience-enricher agent. Fills missing enrichment fields on focus groups using inference from existing data and external research. Works in pipeline mode (staging records) and heartbeat mode (production records weekly).", category: "audience", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/audience-enrichment-procedures/SKILL.md" },
        // Research
        { slug: "audience-analysis-procedures", name: "audience-analysis-procedures", displayName: "Audience Analysis Procedures", description: "SOP for the vibe-audience-parser agent. Parses uploaded audience research documents into structured focus group profiles, runs fuzzy matching against existing groups, and stages results for human review.", category: "research", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/audience-analysis-procedures/SKILL.md" },
        { slug: "audience-research-procedures", name: "audience-research-procedures", displayName: "Audience Research Procedures", description: "SOP for vibe-audience-researcher agent. Conducts comprehensive market research, identifies audience segments, builds detailed focus group profiles with real language patterns, and stages structured data for human review. Produces 15-30 distinct audience profiles per product with demographics, psychographics, pain points, awareness stages, and marketing hooks.", category: "research", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/audience-research-procedures/SKILL.md" },
        // Content
        { slug: "content-strategy", name: "content-strategy", displayName: "Content Strategy", description: "Plan content strategy, decide what content to create, figure out topics to cover. Covers topic clusters, content calendars, and content planning.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/content-strategy/SKILL.md" },
        { slug: "copy-editing", name: "copy-editing", displayName: "Copy Editing", description: "Systematic approach to editing marketing copy through multiple focused passes. Covers proofreading, polish, and copy sweeps.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/copy-editing/SKILL.md" },
        { slug: "copywriting", name: "copywriting", displayName: "Copywriting", description: "Write or improve marketing copy for any page — homepage, landing pages, pricing, feature pages, about pages, or product pages.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/copywriting/SKILL.md" },
        { slug: "ebook-analysis", name: "ebook-analysis", displayName: "Ebook Analysis", description: "Parse ebooks, extract concepts and entities with citation traceability, classify by type/layer, and synthesize across book collections.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/ebook-analysis/SKILL.md" },
        { slug: "ebook-procedures", name: "ebook-procedures", displayName: "Ebook Creation Procedures", description: "Dual-mode ebook creation skill for vibe-ebook-writer agent. Mode 1 (Full Book) produces authority content (8-15 chapters). Mode 2 (Lead Magnet) produces short opt-in ebooks (3-7 chapters). Both output markdown + cover spec JSON for image generation handoff.", category: "content", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/ebook-procedures/SKILL.md" },
        { slug: "email-sequence", name: "email-sequence", displayName: "Email Sequence", description: "Create or optimize email sequences, drip campaigns, automated email flows, or lifecycle email programs. Covers welcome sequences, nurture sequences, and re-engagement.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/email-sequence/SKILL.md" },
        { slug: "social-content", name: "social-content", displayName: "Social Content", description: "Create, schedule, or optimize social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook. Covers content creation, repurposing, and platform-specific strategies.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/social-content/SKILL.md" },
        { slug: "facebook-engagement-engine", name: "facebook-engagement-engine", displayName: "Facebook Engagement Engine", description: "Generate maximum-engagement Facebook posts using embedded STEPPS virality, Voss tactical empathy, FB Monetization mechanics, and hook craft. Pure engagement — no selling. Outputs text copy + image briefs + STEPPS scores.", category: "content", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/facebook-engagement-engine/SKILL.md", tagline: "Engineer every post for maximum engagement", dashboardDescription: "Facebook-specific engagement engine. Generates batches of 24/36/48 posts with STEPPS scoring, Voss techniques, and hook craft. Pure engagement, zero sales." },
        { slug: "video-script-guide", name: "video-script-guide", displayName: "Video Script Guide", description: "Multi-format video script creation skill for vibe-script-writer agent. Routes to 8 sub-formats (YouTube long-form, short-form, VSL, webinar, explainer, testimonial, LinkedIn video, ad) based on campaign deliverableConfig. Outputs two-column AV scripts with timing, visual cues, and speaker directions.", category: "content", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/video-script-guide/SKILL.md" },
        // Media
        { slug: "image-generation-procedures", name: "image-generation-procedures", displayName: "Image Generation Procedures", description: "SOP for vibe-image-generator agent. Receives prompt specs from vibe-image-director, resolves which image service to call (FLUX.2 Pro/Turbo, GPT Image, Ideogram, Imagen, etc.) via service registry priority, handles aspect ratios, retries on failure, saves generated images to campaign assets.", category: "media", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/image-generation-procedures/SKILL.md" },
        { slug: "image-prompt-engineering", name: "image-prompt-engineering", displayName: "Image Prompt Engineering", description: "SOP for vibe-image-director agent. Reads content (articles, landing pages, ebooks, social posts), extracts visual concepts, and produces detailed image generation prompts with style/mood/composition directives and negative prompts. Does NOT call image APIs — outputs structured prompt JSON for vibe-image-generator.", category: "media", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/image-prompt-engineering/SKILL.md" },
        { slug: "image-director-engagement", name: "image-director-engagement", displayName: "Image Director — Engagement", description: "Specialized image prompt engineering for engagement social posts. Produces scroll-stopping visuals using STEPPS virality scoring, platform-specific formats (TOBI, meme, grid, quote card, nostalgic photo), and engagement psychology. Reads post content to infer visual intent when no explicit imageIntent is provided.", category: "media", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/image-director-engagement/SKILL.md" },
        { slug: "video-script-engagement", name: "video-script-engagement", displayName: "Video Script Writer — Engagement", description: "Specialized short-form video script writing for engagement social content. Produces scroll-stopping Reels, TikTok, and FB video scripts using STEPPS virality scoring, platform-specific formats (hook-story-CTA, POV, trending audio, duet-bait, green screen), and engagement psychology. Reads post content to infer video format when no explicit videoIntent is provided.", category: "media", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/video-script-engagement/SKILL.md" },
        // Quality
        { slug: "content-review-procedures", name: "content-review-procedures", displayName: "Content Review Procedures", description: "SOP for vibe-content-reviewer agent. Quality rubric for evaluating all content types — awareness match, CTA clarity, proof density, SEO, readability, voice consistency, AI pattern detection. Scores 1-10, auto-approves at 7+, requests revision with actionable notes at <7.", category: "quality", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/content-review-procedures/SKILL.md" },
        // Utility
        { slug: "content-writing-procedures", name: "content-writing-procedures", displayName: "Content Writing Procedures", description: "Autonomous agent SOP for all writing agents. Defines the step-by-step process for reading briefs, loading campaign skills, researching, drafting, self-reviewing, and outputting content.", category: "utility", type: "procedure" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/content-writing-procedures/SKILL.md" },
        // Marketing & CRO (20 skills)
        { slug: "ab-test-setup", name: "ab-test-setup", displayName: "A/B Test Setup", description: "Plan, design, or implement A/B tests and experiments. Covers split tests, multivariate tests, and hypothesis formation.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/ab-test-setup/SKILL.md" },
        { slug: "analytics-tracking", name: "analytics-tracking", displayName: "Analytics Tracking", description: "Set up, improve, or audit analytics tracking and measurement. Covers GA4, GTM, conversion tracking, event tracking, UTM parameters.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/analytics-tracking/SKILL.md" },
        { slug: "competitor-alternatives", name: "competitor-alternatives", displayName: "Competitor Alternatives", description: "Create competitor comparison or alternative pages for SEO and sales enablement. Four formats: singular alternative, plural alternatives, you vs competitor, and competitor vs competitor.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/competitor-alternatives/SKILL.md" },
        { slug: "form-cro", name: "form-cro", displayName: "Form CRO", description: "Optimize lead capture forms, contact forms, demo request forms, application forms, survey forms, or checkout forms.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/form-cro/SKILL.md" },
        { slug: "free-tool-strategy", name: "free-tool-strategy", displayName: "Free Tool Strategy", description: "Plan, evaluate, or build free tools for marketing purposes — lead generation, SEO value, or brand awareness.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/free-tool-strategy/SKILL.md" },
        { slug: "launch-strategy", name: "launch-strategy", displayName: "Launch Strategy", description: "Plan product launches, feature announcements, or release strategies. Covers phased launches, channel strategy, and launch momentum.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/launch-strategy/SKILL.md" },
        { slug: "marketing-ideas", name: "marketing-ideas", displayName: "Marketing Ideas", description: "139 proven marketing approaches organized by category for SaaS and software products.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/marketing-ideas/SKILL.md" },
        { slug: "marketing-psychology", name: "marketing-psychology", displayName: "Marketing Psychology", description: "70+ mental models organized for marketing application. Covers cognitive biases, persuasion principles, and behavioral science.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/marketing-psychology/SKILL.md" },
        { slug: "onboarding-cro", name: "onboarding-cro", displayName: "Onboarding CRO", description: "Optimize post-signup onboarding, user activation, first-run experience, and time-to-value.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/onboarding-cro/SKILL.md" },
        { slug: "page-cro", name: "page-cro", displayName: "Page CRO", description: "Optimize conversions on any marketing page — homepage, landing pages, pricing pages, feature pages, or blog posts.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/page-cro/SKILL.md" },
        { slug: "paid-ads", name: "paid-ads", displayName: "Paid Ads", description: "Paid advertising campaigns on Google Ads, Meta, LinkedIn, Twitter/X. Covers campaign strategy, ad creation, audience targeting, and optimization.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/paid-ads/SKILL.md" },
        { slug: "paywall-upgrade-cro", name: "paywall-upgrade-cro", displayName: "Paywall Upgrade CRO", description: "Create or optimize in-app paywalls, upgrade screens, upsell modals, or feature gates for freemium conversion.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/paywall-upgrade-cro/SKILL.md" },
        { slug: "popup-cro", name: "popup-cro", displayName: "Popup CRO", description: "Create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/popup-cro/SKILL.md" },
        { slug: "pricing-strategy", name: "pricing-strategy", displayName: "Pricing Strategy", description: "Pricing decisions, packaging, and monetization strategy. Covers pricing research, tier structure, and packaging.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/pricing-strategy/SKILL.md" },
        { slug: "product-marketing-context", name: "product-marketing-context", displayName: "Product Marketing Context", description: "Create or update product marketing context document. Covers positioning and foundational information referenced by other marketing skills.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/product-marketing-context/SKILL.md" },
        { slug: "programmatic-seo", name: "programmatic-seo", displayName: "Programmatic SEO", description: "Create SEO-driven pages at scale using templates and data. Covers directory pages, location pages, comparison pages, and integration pages.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/programmatic-seo/SKILL.md" },
        { slug: "referral-program", name: "referral-program", displayName: "Referral Program", description: "Create, optimize, or analyze referral programs, affiliate programs, or word-of-mouth strategies.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/referral-program/SKILL.md" },
        { slug: "schema-markup", name: "schema-markup", displayName: "Schema Markup", description: "Add, fix, or optimize schema markup and structured data. Covers JSON-LD, rich snippets, FAQ schema, product schema.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/schema-markup/SKILL.md" },
        { slug: "seo-audit", name: "seo-audit", displayName: "SEO Audit", description: "Audit, review, or diagnose SEO issues. Covers technical SEO, on-page SEO, meta tags, and SEO health checks.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/seo-audit/SKILL.md" },
        { slug: "signup-flow-cro", name: "signup-flow-cro", displayName: "Signup Flow CRO", description: "Optimize signup, registration, account creation, or trial activation flows.", category: "marketing", type: "custom" as const, isAutoActive: false, isCampaignSelectable: true, filePath: ".claude/skills/signup-flow-cro/SKILL.md" },
      ];
      for (const skill of skills) {
        const id = await ctx.db.insert("skills", {
          ...skill,
          lastSyncedAt: Date.now(),
          syncStatus: "synced" as const,
        });
        skillIdMap[skill.slug] = id;
      }
      results.push(`Seeded ${skills.length} skills`);
    } else {
      // Build skillIdMap from existing skills
      for (const skill of existingSkills) {
        skillIdMap[skill.slug] = skill._id;
      }
      results.push(`Skills already exist (${existingSkills.length}), skipping`);
    }

    // ── Preset Pipelines ──
    const existingPipelines = await ctx.db
      .query("pipelines")
      .withIndex("by_type", (q) => q.eq("type", "preset"))
      .collect();
    if (existingPipelines.length === 0) {
      const presets = [
        {
          name: "Research Only",
          slug: "research-only",
          type: "preset" as const,
          category: "sales" as const,
          description: "Keyword research + SERP analysis. Output: research reports only.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-keyword-researcher", model: "sonnet", label: "Keyword Research", description: "Research keywords and search intent", outputDir: "research" },
            { order: 2, agent: "vibe-serp-analyzer", model: "sonnet", label: "SERP Analysis", description: "Analyze search results and competition", outputDir: "research" },
          ],
          parallelBranches: [],
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "Content Draft",
          slug: "content-draft",
          type: "preset" as const,
          category: "sales" as const,
          description: "Research → write → review → humanize. Output: final articles ready for review.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-keyword-researcher", model: "sonnet", label: "Keyword Research", description: "Research keywords and search intent", outputDir: "research" },
            { order: 2, agent: "vibe-keyword-researcher", model: "sonnet", label: "Content Brief", description: "Generate content brief from research", outputDir: "briefs" },
            { order: 3, agent: "vibe-content-writer", model: "opus", label: "Write Article", description: "Write long-form article from brief", outputDir: "drafts" },
            { order: 4, agent: "vibe-content-reviewer", model: "sonnet", label: "Quality Review", description: "Review for quality, accuracy, SEO", outputDir: "reviewed" },
            { order: 5, agent: "vibe-humanizer", model: "opus", label: "Humanize", description: "Remove AI patterns, add human voice", outputDir: "final" },
          ],
          parallelBranches: [],
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "Full Content Production",
          slug: "full-content-production",
          type: "preset" as const,
          category: "sales" as const,
          description: "Articles + images + social posts + email excerpts. The standard pipeline.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-keyword-researcher", model: "sonnet", label: "Keyword Research", description: "Research keywords and search intent", outputDir: "research" },
            { order: 2, agent: "vibe-keyword-researcher", model: "sonnet", label: "Content Brief", description: "Generate content brief from research", outputDir: "briefs" },
            { order: 3, agent: "vibe-content-writer", model: "opus", label: "Write Article", description: "Write long-form article from brief", outputDir: "drafts" },
            { order: 4, agent: "vibe-content-reviewer", model: "sonnet", label: "Quality Review", description: "Review for quality, accuracy, SEO", outputDir: "reviewed" },
            { order: 5, agent: "vibe-humanizer", model: "opus", label: "Humanize", description: "Remove AI patterns, add human voice", outputDir: "final" },
          ],
          parallelBranches: [
            { triggerAfterStep: 3, agent: "vibe-image-director", model: "sonnet", label: "Hero Image", description: "Generate hero image prompt for article" },
            { triggerAfterStep: 3, agent: "vibe-social-writer", model: "opus", label: "Social Posts", description: "Create social media posts from article" },
            { triggerAfterStep: 3, agent: "vibe-content-repurposer", model: "opus", label: "Email Excerpt", description: "Create email newsletter excerpt" },
            { triggerAfterStep: 5, agent: "vibe-image-director", model: "sonnet", label: "Ad & Social Images", description: "Generate image prompts for all ad creatives and social posts" },
          ],
          convergenceStep: 5,
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "Launch Package",
          slug: "launch-package",
          type: "preset" as const,
          category: "sales" as const,
          description: "Everything: articles + landing page + email sequence + ads + images + social.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-keyword-researcher", model: "sonnet", label: "Keyword Research", description: "Research keywords and search intent", outputDir: "research" },
            { order: 2, agent: "vibe-keyword-researcher", model: "sonnet", label: "Content Brief", description: "Generate content brief from research", outputDir: "briefs" },
            { order: 3, agent: "vibe-content-writer", model: "opus", label: "Write Article", description: "Write long-form article from brief", outputDir: "drafts" },
            { order: 4, agent: "vibe-content-reviewer", model: "sonnet", label: "Quality Review", description: "Review for quality, accuracy, SEO", outputDir: "reviewed" },
            { order: 5, agent: "vibe-humanizer", model: "opus", label: "Humanize", description: "Remove AI patterns, add human voice", outputDir: "final" },
          ],
          parallelBranches: [
            { triggerAfterStep: 3, agent: "vibe-image-director", model: "sonnet", label: "Hero Image", description: "Generate hero image prompt for article" },
            { triggerAfterStep: 3, agent: "vibe-social-writer", model: "opus", label: "Social Posts", description: "Create social media posts from article" },
            { triggerAfterStep: 3, agent: "vibe-content-repurposer", model: "opus", label: "Email Excerpt", description: "Create email newsletter excerpt" },
            { triggerAfterStep: 2, agent: "vibe-landing-page-writer", model: "opus", label: "Landing Page", description: "Write high-converting landing page" },
            { triggerAfterStep: 2, agent: "vibe-email-writer", model: "opus", label: "Email Sequence", description: "Write nurture email sequence" },
            { triggerAfterStep: 2, agent: "vibe-ad-writer", model: "opus", label: "Ad Copy Set", description: "Write ad copy for Google/Meta/LinkedIn" },
            { triggerAfterStep: 5, agent: "vibe-image-director", model: "sonnet", label: "Ad & Social Images", description: "Generate image prompts for all ad creatives and social posts" },
          ],
          convergenceStep: 5,
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "[Audience Discovery] From Scratch",
          slug: "audience-discovery",
          type: "preset" as const,
          category: "audience" as const,
          description: "Generate focus group profiles from scratch for a new market.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-audience-researcher", model: "opus", label: "Research Audiences", description: "Generate audience segments from scratch", outputDir: "research" },
            { order: 2, agent: "vibe-audience-enricher", model: "sonnet", label: "Enrich Profiles", description: "Add psychographics, language patterns", outputDir: "research" },
          ],
          parallelBranches: [],
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "[Audience Discovery] From Existing Document",
          slug: "audience-discovery-import",
          type: "preset" as const,
          category: "audience" as const,
          description: "Parse an uploaded audience document into structured focus groups.",
          mainSteps: [
            { order: 0, label: "Created", description: "Task created", outputDir: "" },
            { order: 1, agent: "vibe-audience-parser", model: "sonnet", label: "Parse Document", description: "Extract focus groups from uploaded document", outputDir: "research" },
            { order: 2, agent: "vibe-audience-enricher", model: "sonnet", label: "Enrich Profiles", description: "Fill missing enrichment fields", outputDir: "research" },
          ],
          parallelBranches: [],
          onComplete: { telegram: true, summary: true, generateManifest: false },
        },
      ];
      for (const pipeline of presets) {
        await ctx.db.insert("pipelines", pipeline);
      }
      results.push(`Seeded ${presets.length} preset pipelines`);
    } else {
      results.push(`Preset pipelines already exist (${existingPipelines.length}), skipping`);
    }

    // ── Agents ──
    const existingAgents = await ctx.db.query("agents").collect();
    if (existingAgents.length === 0) {
      const agents = [
        // ── Audience Agents ──
        {
          name: "vibe-audience-parser",
          displayName: "Audience Parser",
          role: "Parses uploaded audience documents into structured focus group profiles. Handles .md, .txt, .docx, .pdf formats with fuzzy matching against existing groups.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/audience-analysis-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/audience-analysis-procedures/vibe-audience-parser.md",
        },
        {
          name: "vibe-audience-researcher",
          displayName: "Audience Researcher",
          role: "Researches and generates focus group profiles from scratch using web search, Reddit scraping, competitor analysis, and review mining.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/audience-research-procedures",
          level: "lead" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/audience-research-procedures/vibe-audience-researcher.md",
        },
        {
          name: "vibe-audience-enricher",
          displayName: "Audience Enricher",
          role: "Fills missing enrichment fields on focus groups (awareness stage, sophistication, purchase behavior) using deterministic inference and web research.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 3 * * 1",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/audience-enrichment-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/audience-enrichment-procedures/vibe-audience-enricher.md",
        },
        // ── Research Agents ──
        {
          name: "vibe-keyword-researcher",
          displayName: "Keyword Researcher",
          role: "Researches keywords, search intent, and content gaps. Generates content briefs with target keywords, headings, and competitor analysis.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/content-writing-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/content-writing-procedures/vibe-keyword-researcher.md",
        },
        {
          name: "vibe-serp-analyzer",
          displayName: "SERP Analyzer",
          role: "Analyzes search engine results pages for target keywords. Identifies content gaps, featured snippet opportunities, and competitive positioning.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/content-writing-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/content-writing-procedures/vibe-serp-analyzer.md",
        },
        // ── Content Creation Agents ──
        {
          name: "vibe-content-writer",
          displayName: "Content Writer",
          role: "Writes long-form articles, blog posts, and guides from content briefs. Applies marketing psychology, focus group language patterns, and SEO optimization.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */4 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/content-writing-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/content-writing-procedures/vibe-content-writer.md",
        },
        {
          name: "vibe-content-reviewer",
          displayName: "Content Reviewer",
          role: "Reviews content for quality, accuracy, SEO compliance, and brand voice. Scores against rubric and provides actionable revision notes.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */4 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/content-review-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/content-review-procedures/vibe-content-reviewer.md",
        },
        {
          name: "vibe-humanizer",
          displayName: "Humanizer",
          role: "Removes AI writing patterns, adds human voice and authenticity. Final quality pass before publishing. Uses L5 quality skills.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */4 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/humanizer",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/humanizer/SKILL.md",
        },
        {
          name: "vibe-content-repurposer",
          displayName: "Content Repurposer",
          role: "Transforms long-form content into email excerpts, newsletter snippets, and other derivative formats.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/content-writing-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/content-writing-procedures/vibe-content-repurposer.md",
        },
        // ── Channel-Specific Agents ──
        {
          name: "vibe-social-writer",
          displayName: "Social Writer",
          role: "Creates platform-optimized social media posts (X, LinkedIn, Facebook, Instagram) from articles and briefs. Handles hashtags, hooks, and character limits.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/social-content",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/social-content/SKILL.md",
        },
        {
          name: "vibe-facebook-engine",
          displayName: "Facebook Engagement Engine",
          role: "Generates maximum-engagement Facebook posts using embedded STEPPS virality, Voss tactical empathy, FB Monetization mechanics, and hook craft. Outputs text copy + image briefs + STEPPS scores. Pure engagement — no selling.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/facebook-engagement-engine",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/facebook-engagement-engine/SKILL.md",
        },
        {
          name: "vibe-email-writer",
          displayName: "Email Writer",
          role: "Writes nurture email sequences, welcome series, and promotional emails. Applies direct response techniques and segmentation.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/email-sequence",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/email-sequence/SKILL.md",
        },
        {
          name: "vibe-ad-writer",
          displayName: "Ad Writer",
          role: "Creates ad copy for Google Ads, Meta Ads, and LinkedIn Ads. Generates headlines, descriptions, and CTAs optimized per platform specs.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/paid-ads",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/paid-ads/SKILL.md",
        },
        {
          name: "vibe-landing-page-writer",
          displayName: "Landing Page Writer",
          role: "Writes high-converting landing pages with hero sections, benefit stacks, testimonials, FAQ, and CTAs. Applies CRO best practices.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/page-cro",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/page-cro/SKILL.md",
        },
        // ── Visual & Media Agents ──
        {
          name: "vibe-image-director",
          displayName: "Image Director",
          role: "Generates detailed image prompts for AI image generation. Creates hero images, social graphics, and product visuals. Directs style, composition, and branding.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/image-prompt-engineering",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/image-prompt-engineering/SKILL.md",
        },
        {
          name: "vibe-image-generator",
          displayName: "Image Generator",
          role: "Executes image generation using AI services (fal.ai, DALL-E, Ideogram, Recraft). Receives prompts from Image Director and produces final assets.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/image-generation-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/image-generation-procedures/SKILL.md",
        },
        {
          name: "vibe-script-writer",
          displayName: "Script Writer",
          role: "Writes video scripts for YouTube, TikTok, Reels, and ads. Handles hooks, pacing, B-roll notes, and CTAs per platform format.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "sonnet",
          skillPath: ".claude/skills/video-script-guide",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/video-script-guide/SKILL.md",
        },
        {
          name: "vibe-ebook-writer",
          displayName: "Ebook Writer",
          role: "Creates lead magnet ebooks and long-form downloadable content. Handles chapter structure, design notes, and CTA placement.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "0 */6 * * *",
          defaultModel: "opus",
          skillPath: ".claude/skills/ebook-procedures",
          level: "specialist" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: ".claude/skills/ebook-procedures/SKILL.md",
        },
        // ── Orchestration ──
        {
          name: "vibe-orchestrator",
          displayName: "Orchestrator",
          role: "Coordinates pipeline execution. Assigns tasks, monitors progress, handles failures, and triggers parallel branches. The brain of the system.",
          status: "idle" as const,
          lastHeartbeat: Date.now(),
          heartbeatCron: "*/5 * * * *",
          defaultModel: "sonnet",
          skillPath: "",
          level: "orchestrator" as const,
          stats: { tasksCompleted: 0, lastActive: Date.now() },
          staticSkillIds: [] as any[],
          dynamicSkillIds: [] as any[],
          agentFilePath: "",
        },
      ];
      for (const agent of agents) {
        await ctx.db.insert("agents", agent);
      }
      results.push(`Seeded ${agents.length} agents`);
    } else {
      results.push(`Agents already exist (${existingAgents.length}), skipping`);
    }

    // ── Agent-Skill Relations ──
    // Wire staticSkillIds on agents using the skillIdMap built above
    const agentSkillMap: Record<string, string[]> = {
      "vibe-content-writer": ["content-writing-procedures", "mbook-schwarz-awareness", "humanizer", "writing-clearly-and-concisely"],
      "vibe-email-writer": ["email-sequence", "mbook-schwarz-awareness", "humanizer", "writing-clearly-and-concisely"],
      "vibe-social-writer": ["social-content", "mbook-schwarz-awareness", "humanizer", "writing-clearly-and-concisely"],
      "vibe-facebook-engine": ["facebook-engagement-engine", "humanizer", "writing-clearly-and-concisely"],
      "vibe-ad-writer": ["paid-ads", "mbook-schwarz-awareness"],
      "vibe-landing-page-writer": ["page-cro"],
      "vibe-content-reviewer": ["content-review-procedures", "writing-clearly-and-concisely"],
      "vibe-humanizer": ["humanizer", "writing-clearly-and-concisely"],
      "vibe-content-repurposer": ["content-writing-procedures"],
      "vibe-audience-parser": ["audience-analysis-procedures"],
      "vibe-audience-researcher": ["audience-research-procedures"],
      "vibe-audience-enricher": ["audience-enrichment-procedures"],
      "vibe-keyword-researcher": ["content-writing-procedures"],
      "vibe-serp-analyzer": ["content-writing-procedures"],
      "vibe-image-director": ["image-prompt-engineering", "image-director-engagement"],
      "vibe-image-generator": ["image-generation-procedures"],
      "vibe-script-writer": ["video-script-guide", "video-script-engagement"],
      "vibe-ebook-writer": ["ebook-procedures"],
    };
    const allAgents = await ctx.db.query("agents").collect();
    let wiredCount = 0;
    for (const agent of allAgents) {
      const slugs = agentSkillMap[agent.name];
      if (!slugs) continue;
      const ids = slugs.map((s) => skillIdMap[s]).filter(Boolean);
      if (ids.length > 0 && agent.staticSkillIds.length === 0) {
        await ctx.db.patch(agent._id, { staticSkillIds: ids });
        wiredCount++;
      }
    }
    if (wiredCount > 0) {
      results.push(`Wired skills to ${wiredCount} agents`);
    } else {
      results.push(`Agent-skill relations already wired or no skills to wire`);
    }

    // ── Agent Service Dependencies ──
    const existingDeps = await ctx.db.query("agentServiceDeps").collect();
    if (existingDeps.length === 0) {
      const deps = [
        // Audience Researcher — needs web_search (required), web_scraping and reddit (optional)
        { agentName: "vibe-audience-researcher", capability: "web_search", required: true },
        { agentName: "vibe-audience-researcher", capability: "web_scraping", required: false },
        { agentName: "vibe-audience-researcher", capability: "social_reddit", required: false },
        // Audience Enricher — all optional (uses deterministic inference as primary, web as supplemental)
        { agentName: "vibe-audience-enricher", capability: "web_search", required: false },
        { agentName: "vibe-audience-enricher", capability: "social_reddit", required: false },
        // Audience Parser — no external service dependencies (filesystem only)
        // Keyword Researcher
        { agentName: "vibe-keyword-researcher", capability: "seo_keywords", required: false },
        { agentName: "vibe-keyword-researcher", capability: "web_search", required: true },
        // SERP Analyzer
        { agentName: "vibe-serp-analyzer", capability: "seo_keywords", required: true },
        { agentName: "vibe-serp-analyzer", capability: "web_scraping", required: false },
        // Content Writer — no external deps (uses Claude + skills)
        // Content Reviewer
        { agentName: "vibe-content-reviewer", capability: "content_quality", required: false },
        // Humanizer — no external deps (Claude only)
        // Social Writer
        { agentName: "vibe-social-writer", capability: "social_publishing", required: false },
        // Email Writer
        { agentName: "vibe-email-writer", capability: "email_sending", required: false },
        // Ad Writer
        { agentName: "vibe-ad-writer", capability: "analytics", required: false },
        // Landing Page Writer — no external deps
        // Image Director — no external deps (generates prompts only)
        // Image Generator
        { agentName: "vibe-image-generator", capability: "image_generation", required: true },
        // Script Writer — no external deps
        // Ebook Writer
        { agentName: "vibe-ebook-writer", capability: "document_generation", required: false },
      ];
      for (const dep of deps) {
        await ctx.db.insert("agentServiceDeps", dep);
      }
      results.push(`Seeded ${deps.length} agent service dependencies`);
    } else {
      results.push(`Agent service deps already exist (${existingDeps.length}), skipping`);
    }

    return results;
  },
});

// Clear all seeded data and re-run seed from scratch
export const clearAndReseed = mutation({
  args: {},
  handler: async (ctx) => {
    const tables = ["agents", "agentServiceDeps", "pipelines", "serviceCategories", "skillCategories", "skills"] as const;
    const counts: Record<string, number> = {};
    for (const table of tables) {
      const rows = await ctx.db.query(table).collect();
      for (const row of rows) {
        await ctx.db.delete(row._id);
      }
      counts[table] = rows.length;
    }
    return counts;
  },
});

// Incremental seeder: adds missing pipelines/agents without wiping existing data
export const seedMissing = internalMutation({
  args: {},
  handler: async (ctx) => {
    const results: string[] = [];

    // Check for missing audience pipelines
    const audienceDiscovery = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", "audience-discovery"))
      .unique();
    if (!audienceDiscovery) {
      await ctx.db.insert("pipelines", {
        name: "[Audience Discovery] From Scratch",
        slug: "audience-discovery",
        type: "preset" as const,
        category: "audience" as const,
        description: "Generate focus group profiles from scratch for a new market.",
        mainSteps: [
          { order: 0, label: "Created", description: "Task created", outputDir: "" },
          { order: 1, agent: "vibe-audience-researcher", model: "opus", label: "Research Audiences", description: "Generate audience segments from scratch", outputDir: "research" },
          { order: 2, agent: "vibe-audience-enricher", model: "sonnet", label: "Enrich Profiles", description: "Add psychographics, language patterns", outputDir: "research" },
        ],
        parallelBranches: [],
        onComplete: { telegram: true, summary: true, generateManifest: true },
      });
      results.push("Seeded [Audience Discovery] From Scratch pipeline");
    } else {
      results.push("[Audience Discovery] From Scratch pipeline already exists");
    }

    const docImport = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", "audience-discovery-import"))
      .unique();
    if (!docImport) {
      await ctx.db.insert("pipelines", {
        name: "[Audience Discovery] From Existing Document",
        slug: "audience-discovery-import",
        type: "preset" as const,
        category: "audience" as const,
        description: "Parse an uploaded audience document into structured focus groups.",
        mainSteps: [
          { order: 0, label: "Created", description: "Task created", outputDir: "" },
          { order: 1, agent: "vibe-audience-parser", model: "sonnet", label: "Parse Document", description: "Extract focus groups from uploaded document", outputDir: "research" },
          { order: 2, agent: "vibe-audience-enricher", model: "sonnet", label: "Enrich Profiles", description: "Fill missing enrichment fields", outputDir: "research" },
        ],
        parallelBranches: [],
        onComplete: { telegram: true, summary: true, generateManifest: false },
      });
      results.push("Seeded [Audience Discovery] From Existing Document pipeline");
    } else {
      results.push("[Audience Discovery] From Existing Document pipeline already exists");
    }

    // ── Engagement Pipeline: Quick (3-step) ──
    // Single-task model: one task produces ALL posts in a single pipeline run
    const quickEngagementData = {
      name: "Quick Engagement Batch",
      slug: "quick-engagement-batch",
      type: "preset" as const,
      category: "engagement" as const,
      description: "Generate → review → humanize. All posts produced in a single pipeline run without trend research.",
      mainSteps: [
        { order: 0, label: "Created", description: "Task created", outputDir: "" },
        { order: 1, agent: "vibe-facebook-engine", model: "opus", label: "Generate Posts", description: "Generate all engagement posts for the batch in one pass", outputDir: "drafts" },
        { order: 2, agent: "vibe-content-reviewer", model: "sonnet", label: "Review Posts", description: "Review all posts for quality and engagement potential", outputDir: "reviewed" },
        { order: 3, agent: "vibe-humanizer", model: "opus", label: "Humanize", description: "Remove AI patterns, add authentic voice to all posts", outputDir: "final" },
      ],
      parallelBranches: [
        { triggerAfterStep: 1, agent: "vibe-image-director", model: "sonnet", label: "Image Prompts", description: "Generate image prompts for each post resource" },
        { triggerAfterStep: 1, agent: "vibe-script-writer", model: "sonnet", label: "Reels Scripts", description: "Generate short-form video scripts for each post resource" },
      ],
      convergenceStep: 2,
      onComplete: { telegram: true, summary: true, generateManifest: true },
    };
    const existingQuickEngagement = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", "quick-engagement-batch"))
      .unique();
    if (!existingQuickEngagement) {
      await ctx.db.insert("pipelines", quickEngagementData);
      results.push("Seeded Quick Engagement Batch pipeline");
    } else {
      await ctx.db.patch(existingQuickEngagement._id, quickEngagementData);
      results.push("Updated Quick Engagement Batch pipeline");
    }

    // ── Engagement Pipeline: Full (4-step + branch) ──
    // Single-task model: one task produces ALL posts in a single pipeline run
    const fullEngagementData = {
      name: "Full Engagement Batch",
      slug: "full-engagement-batch",
      type: "preset" as const,
      category: "engagement" as const,
      description: "Trend research → generate → review → humanize. All posts produced in a single pipeline run with trend-driven content.",
      mainSteps: [
        { order: 0, label: "Created", description: "Task created", outputDir: "" },
        { order: 1, agent: "vibe-engagement-trend-researcher", model: "sonnet", label: "Trend Research", description: "Scrape trends from Reddit/web, cross-reference with focus groups", outputDir: "research" },
        { order: 2, agent: "vibe-facebook-engine", model: "opus", label: "Generate Posts", description: "Generate all trend-driven engagement posts for the batch", outputDir: "drafts" },
        { order: 3, agent: "vibe-content-reviewer", model: "sonnet", label: "Review Posts", description: "Review all posts for quality and engagement potential", outputDir: "reviewed" },
        { order: 4, agent: "vibe-humanizer", model: "opus", label: "Humanize", description: "Remove AI patterns, add authentic voice to all posts", outputDir: "final" },
      ],
      parallelBranches: [
        { triggerAfterStep: 2, agent: "vibe-image-director", model: "sonnet", label: "Image Prompts", description: "Generate image prompts for each post resource" },
        { triggerAfterStep: 2, agent: "vibe-script-writer", model: "sonnet", label: "Reels Scripts", description: "Generate short-form video scripts for each post resource" },
      ],
      convergenceStep: 3,
      onComplete: { telegram: true, summary: true, generateManifest: true },
    };
    const existingFullEngagement = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", "full-engagement-batch"))
      .unique();
    if (!existingFullEngagement) {
      await ctx.db.insert("pipelines", fullEngagementData);
      results.push("Seeded Full Engagement Batch pipeline");
    } else {
      await ctx.db.patch(existingFullEngagement._id, fullEngagementData);
      results.push("Updated Full Engagement Batch pipeline");
    }

    // ── Trend Researcher Agent ──
    const existingTrendResearcher = await ctx.db
      .query("agents")
      .withIndex("by_name", (q) => q.eq("name", "vibe-engagement-trend-researcher"))
      .unique();
    if (!existingTrendResearcher) {
      await ctx.db.insert("agents", {
        name: "vibe-engagement-trend-researcher",
        displayName: "Engagement Trend Researcher",
        role: "Scrapes configured subreddits and web sources, cross-references with focus group data, scores trends using STEPPS framework, and outputs trend briefs per post.",
        status: "idle" as const,
        lastHeartbeat: Date.now(),
        heartbeatCron: "0 */6 * * *",
        defaultModel: "sonnet",
        skillPath: ".claude/skills/trend-research-procedures",
        level: "specialist" as const,
        stats: { tasksCompleted: 0, lastActive: Date.now() },
        staticSkillIds: [] as any[],
        dynamicSkillIds: [] as any[],
        agentFilePath: ".claude/skills/trend-research-procedures/SKILL.md",
      });
      results.push("Seeded vibe-engagement-trend-researcher agent");
    } else {
      results.push("vibe-engagement-trend-researcher agent already exists");
    }

    // ── Trend Research Skill ──
    const existingTrendSkill = await ctx.db
      .query("skills")
      .withIndex("by_slug", (q) => q.eq("slug", "trend-research-procedures"))
      .unique();
    if (!existingTrendSkill) {
      await ctx.db.insert("skills", {
        name: "trend-research-procedures",
        slug: "trend-research-procedures",
        displayName: "Trend Research Procedures",
        description: "SOP for vibe-engagement-trend-researcher agent. Scrapes Reddit and web for trending topics, scores them with STEPPS virality framework, matches to focus group psychographics, and outputs trend briefs for engagement post generation.",
        category: "research",
        type: "procedure" as const,
        isAutoActive: false,
        isCampaignSelectable: false,
        filePath: ".claude/skills/trend-research-procedures/SKILL.md",
        lastSyncedAt: Date.now(),
        syncStatus: "pending_setup" as const,
      });
      results.push("Seeded trend-research-procedures skill");
    } else {
      results.push("trend-research-procedures skill already exists");
    }

    return results;
  },
});
