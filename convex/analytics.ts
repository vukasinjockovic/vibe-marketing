import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ═══════════════════════════════════════════
// AGENT RUNS
// ═══════════════════════════════════════════

// List agent runs by agent name
export const listRunsByAgent = query({
  args: { agentName: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("agentRuns")
      .withIndex("by_agent", (q) => q.eq("agentName", args.agentName))
      .collect();
  },
});

// List agent runs by campaign
export const listRunsByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("agentRuns")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();
  },
});

// Start an agent run
export const startRun = mutation({
  args: {
    projectId: v.optional(v.id("projects")),
    agentName: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    model: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("agentRuns", {
      projectId: args.projectId,
      agentName: args.agentName,
      campaignId: args.campaignId,
      model: args.model,
      status: "running",
      startedAt: Date.now(),
    });
  },
});

// Complete an agent run
export const completeRun = mutation({
  args: {
    id: v.id("agentRuns"),
    itemsProcessed: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const run = await ctx.db.get(args.id);
    if (!run) throw new Error("Agent run not found");

    const now = Date.now();
    await ctx.db.patch(args.id, {
      status: "completed" as const,
      finishedAt: now,
      durationSeconds: Math.round((now - run.startedAt) / 1000),
      itemsProcessed: args.itemsProcessed,
    });
  },
});

// Fail an agent run
export const failRun = mutation({
  args: {
    id: v.id("agentRuns"),
    errorLog: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const run = await ctx.db.get(args.id);
    if (!run) throw new Error("Agent run not found");

    const now = Date.now();
    await ctx.db.patch(args.id, {
      status: "failed" as const,
      finishedAt: now,
      durationSeconds: Math.round((now - run.startedAt) / 1000),
      errorLog: args.errorLog,
    });
  },
});

// ═══════════════════════════════════════════
// KEYWORD CLUSTERS
// ═══════════════════════════════════════════

// List keyword clusters by campaign
export const listKeywordsByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("keywordClusters")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();
  },
});

// Create a keyword cluster
export const createKeywordCluster = mutation({
  args: {
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
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("keywordClusters", {
      campaignId: args.campaignId,
      primaryKeyword: args.primaryKeyword,
      secondaryKeywords: args.secondaryKeywords,
      lsiKeywords: args.lsiKeywords,
      searchVolume: args.searchVolume,
      keywordDifficulty: args.keywordDifficulty,
      opportunityScore: args.opportunityScore,
      searchIntent: args.searchIntent,
      serpAnalysis: args.serpAnalysis,
      contentBrief: args.contentBrief,
    });
  },
});

// Update a keyword cluster (partial)
export const updateKeywordCluster = mutation({
  args: {
    id: v.id("keywordClusters"),
    primaryKeyword: v.optional(v.string()),
    secondaryKeywords: v.optional(v.array(v.string())),
    lsiKeywords: v.optional(v.array(v.string())),
    searchVolume: v.optional(v.number()),
    keywordDifficulty: v.optional(v.number()),
    opportunityScore: v.optional(v.number()),
    searchIntent: v.optional(v.string()),
    serpAnalysis: v.optional(v.any()),
    contentBrief: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const cluster = await ctx.db.get(args.id);
    if (!cluster) throw new Error("Keyword cluster not found");

    const updates: Record<string, unknown> = {};
    if (args.primaryKeyword !== undefined) updates.primaryKeyword = args.primaryKeyword;
    if (args.secondaryKeywords !== undefined) updates.secondaryKeywords = args.secondaryKeywords;
    if (args.lsiKeywords !== undefined) updates.lsiKeywords = args.lsiKeywords;
    if (args.searchVolume !== undefined) updates.searchVolume = args.searchVolume;
    if (args.keywordDifficulty !== undefined) updates.keywordDifficulty = args.keywordDifficulty;
    if (args.opportunityScore !== undefined) updates.opportunityScore = args.opportunityScore;
    if (args.searchIntent !== undefined) updates.searchIntent = args.searchIntent;
    if (args.serpAnalysis !== undefined) updates.serpAnalysis = args.serpAnalysis;
    if (args.contentBrief !== undefined) updates.contentBrief = args.contentBrief;

    await ctx.db.patch(args.id, updates);
  },
});

// ═══════════════════════════════════════════
// CONTENT METRICS
// ═══════════════════════════════════════════

// Get content metrics by task (unique)
export const getMetricsByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contentMetrics")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .unique();
  },
});

// List content metrics by campaign
export const listMetricsByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contentMetrics")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();
  },
});

// Upsert content metrics: update if exists, insert if not
export const upsertMetrics = mutation({
  args: {
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    publishedUrl: v.optional(v.string()),
    rankings: v.optional(v.any()),
    organicTraffic: v.optional(v.number()),
    impressions: v.optional(v.number()),
    clicks: v.optional(v.number()),
    ctr: v.optional(v.number()),
    socialEngagement: v.optional(v.any()),
    emailMetrics: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("contentMetrics")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .unique();

    const data = {
      taskId: args.taskId,
      campaignId: args.campaignId,
      publishedUrl: args.publishedUrl,
      rankings: args.rankings,
      organicTraffic: args.organicTraffic,
      impressions: args.impressions,
      clicks: args.clicks,
      ctr: args.ctr,
      socialEngagement: args.socialEngagement,
      emailMetrics: args.emailMetrics,
      lastUpdated: Date.now(),
    };

    if (existing) {
      await ctx.db.patch(existing._id, data);
      return existing._id;
    } else {
      return await ctx.db.insert("contentMetrics", data);
    }
  },
});

// ═══════════════════════════════════════════
// MEDIA ASSETS
// ═══════════════════════════════════════════

// List media assets by task
export const listAssetsByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("mediaAssets")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
  },
});

// List media assets by project
export const listAssetsByProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("mediaAssets")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// Create a media asset
export const createAsset = mutation({
  args: {
    projectId: v.optional(v.id("projects")),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    type: v.union(v.literal("image"), v.literal("video")),
    provider: v.string(),
    promptUsed: v.string(),
    filePath: v.string(),
    fileUrl: v.optional(v.string()),
    dimensions: v.optional(v.string()),
    generationCost: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("mediaAssets", {
      projectId: args.projectId,
      taskId: args.taskId,
      campaignId: args.campaignId,
      type: args.type,
      provider: args.provider,
      promptUsed: args.promptUsed,
      filePath: args.filePath,
      fileUrl: args.fileUrl,
      dimensions: args.dimensions,
      generationCost: args.generationCost,
    });
  },
});

// Delete a media asset
export const deleteAsset = mutation({
  args: { id: v.id("mediaAssets") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// ═══════════════════════════════════════════
// REPORTS
// ═══════════════════════════════════════════

// List reports by project
export const listReportsByProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("reports")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// List reports by type
export const listReportsByType = query({
  args: {
    type: v.union(
      v.literal("weekly_seo"),
      v.literal("weekly_content"),
      v.literal("monthly_roi"),
      v.literal("daily_standup")
    ),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("reports")
      .withIndex("by_type", (q) => q.eq("type", args.type))
      .collect();
  },
});

// Create a report
export const createReport = mutation({
  args: {
    projectId: v.optional(v.id("projects")),
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
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("reports", {
      projectId: args.projectId,
      type: args.type,
      campaignId: args.campaignId,
      periodStart: args.periodStart,
      periodEnd: args.periodEnd,
      data: args.data,
      summary: args.summary,
      actionItems: args.actionItems,
    });
  },
});

// Get report by id
export const getReport = query({
  args: { id: v.id("reports") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});
