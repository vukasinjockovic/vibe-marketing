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
        { key: "L1_audience", displayName: "L1: Audience Understanding", description: "Auto-active. Matches copy to reader awareness stage.", sortOrder: 1, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "auto" },
        { key: "L2_offer", displayName: "L2: Offer Structure", description: "Frameworks for structuring irresistible offers.", sortOrder: 2, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "radio" },
        { key: "L3_persuasion", displayName: "L3: Persuasion & Narrative", description: "Psychological influence and storytelling frameworks.", sortOrder: 3, scope: "copy" as const, maxPerPipelineStep: 2, selectionMode: "checkbox" },
        { key: "L4_craft", displayName: "L4: Copywriting Craft", description: "Headline formulas, body copy style, writing techniques.", sortOrder: 4, scope: "copy" as const, maxPerPipelineStep: 1, selectionMode: "radio" },
        { key: "L5_quality", displayName: "L5: Quality Assurance", description: "Auto-active. AI pattern removal and clarity rules.", sortOrder: 5, scope: "quality" as const, maxPerPipelineStep: 2, selectionMode: "auto" },
        { key: "research_method", displayName: "Research Methods", description: "How agents gather and analyze information.", sortOrder: 6, scope: "research" as const },
        { key: "content_format", displayName: "Content Formats", description: "Format-specific guides (email, social, ads, ebook, video).", sortOrder: 7, scope: "general" as const },
        { key: "visual_style", displayName: "Visual Style", description: "Image prompt engineering and generation procedures.", sortOrder: 8, scope: "visual" as const },
        { key: "agent_procedure", displayName: "Agent Procedures", description: "Step-by-step SOPs that define how agents execute tasks.", sortOrder: 9, scope: "general" as const },
      ];
      for (const cat of skillCategories) {
        await ctx.db.insert("skillCategories", cat);
      }
      results.push(`Seeded ${skillCategories.length} skill categories`);
    } else {
      results.push(`Skill categories already exist (${existingSkillCats.length}), skipping`);
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
            { triggerAfterStep: 3, agent: "vibe-image-director", model: "sonnet", label: "Hero Image", description: "Generate image prompts for article" },
            { triggerAfterStep: 3, agent: "vibe-social-writer", model: "opus", label: "Social Posts", description: "Create social media posts from article" },
            { triggerAfterStep: 3, agent: "vibe-content-repurposer", model: "opus", label: "Email Excerpt", description: "Create email newsletter excerpt" },
          ],
          convergenceStep: 5,
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "Launch Package",
          slug: "launch-package",
          type: "preset" as const,
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
            { triggerAfterStep: 3, agent: "vibe-image-director", model: "sonnet", label: "Hero Image", description: "Generate image prompts for article" },
            { triggerAfterStep: 3, agent: "vibe-social-writer", model: "opus", label: "Social Posts", description: "Create social media posts from article" },
            { triggerAfterStep: 3, agent: "vibe-content-repurposer", model: "opus", label: "Email Excerpt", description: "Create email newsletter excerpt" },
            { triggerAfterStep: 2, agent: "vibe-landing-page-writer", model: "opus", label: "Landing Page", description: "Write high-converting landing page" },
            { triggerAfterStep: 2, agent: "vibe-email-writer", model: "opus", label: "Email Sequence", description: "Write nurture email sequence" },
            { triggerAfterStep: 2, agent: "vibe-ad-writer", model: "opus", label: "Ad Copy Set", description: "Write ad copy for Google/Meta/LinkedIn" },
          ],
          convergenceStep: 5,
          onComplete: { telegram: true, summary: true, generateManifest: true },
        },
        {
          name: "[Audience Discovery] From Scratch",
          slug: "audience-discovery",
          type: "preset" as const,
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
          slug: "document-import",
          type: "preset" as const,
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
    const tables = ["agents", "agentServiceDeps", "pipelines", "serviceCategories", "skillCategories"] as const;
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
      .withIndex("by_slug", (q) => q.eq("slug", "document-import"))
      .unique();
    if (!docImport) {
      await ctx.db.insert("pipelines", {
        name: "[Audience Discovery] From Existing Document",
        slug: "document-import",
        type: "preset" as const,
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

    return results;
  },
});
