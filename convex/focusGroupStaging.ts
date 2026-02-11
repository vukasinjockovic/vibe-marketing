import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// ═══════════════════════════════════════════
// FOCUS GROUP STAGING
// Temporary holding area for parsed focus groups before review/import
// ═══════════════════════════════════════════

// ── Shared validator for focus group staging fields ──

const stagingFocusGroupFields = {
  number: v.optional(v.number()),
  name: v.string(),
  nickname: v.optional(v.string()),
  category: v.optional(v.string()),
  overview: v.optional(v.string()),
  demographics: v.optional(v.object({
    ageRange: v.string(),
    gender: v.string(),
    income: v.string(),
    lifestyle: v.string(),
    triggers: v.array(v.string()),
  })),
  psychographics: v.optional(v.object({
    values: v.array(v.string()),
    beliefs: v.array(v.string()),
    lifestyle: v.string(),
    identity: v.string(),
  })),
  coreDesires: v.optional(v.array(v.string())),
  painPoints: v.optional(v.array(v.string())),
  fears: v.optional(v.array(v.string())),
  beliefs: v.optional(v.array(v.string())),
  objections: v.optional(v.array(v.string())),
  emotionalTriggers: v.optional(v.array(v.string())),
  languagePatterns: v.optional(v.array(v.string())),
  ebookAngles: v.optional(v.array(v.string())),
  marketingHooks: v.optional(v.array(v.string())),
  transformationPromise: v.optional(v.string()),
  source: v.optional(v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual"))),
  awarenessStage: v.optional(v.union(
    v.literal("unaware"), v.literal("problem_aware"), v.literal("solution_aware"),
    v.literal("product_aware"), v.literal("most_aware")
  )),
  awarenessConfidence: v.optional(v.union(v.literal("high"), v.literal("medium"), v.literal("low"))),
  awarenessStageSource: v.optional(v.union(v.literal("auto"), v.literal("manual"))),
  awarenessSignals: v.optional(v.object({
    beliefsSignal: v.optional(v.string()),
    objectionsSignal: v.optional(v.string()),
    languageSignal: v.optional(v.string()),
  })),
  contentPreferences: v.optional(v.object({
    preferredFormats: v.optional(v.array(v.string())),
    attentionSpan: v.optional(v.string()),
    tonePreference: v.optional(v.string()),
  })),
  influenceSources: v.optional(v.object({
    trustedVoices: v.optional(v.array(v.string())),
    mediaConsumption: v.optional(v.array(v.string())),
    socialPlatforms: v.optional(v.array(v.string())),
  })),
  purchaseBehavior: v.optional(v.object({
    buyingTriggers: v.optional(v.array(v.string())),
    priceRange: v.optional(v.string()),
    decisionProcess: v.optional(v.string()),
    objectionHistory: v.optional(v.array(v.string())),
  })),
  competitorContext: v.optional(v.object({
    currentSolutions: v.optional(v.array(v.string())),
    switchMotivators: v.optional(v.array(v.string())),
  })),
  sophisticationLevel: v.optional(v.union(
    v.literal("stage1"), v.literal("stage2"), v.literal("stage3"),
    v.literal("stage4"), v.literal("stage5")
  )),
  communicationStyle: v.optional(v.object({
    formalityLevel: v.optional(v.string()),
    humorReceptivity: v.optional(v.string()),
    storyPreference: v.optional(v.string()),
    dataPreference: v.optional(v.string()),
  })),
  seasonalContext: v.optional(v.object({
    peakInterestPeriods: v.optional(v.array(v.string())),
    lifeEvents: v.optional(v.array(v.string())),
    cyclicalBehaviors: v.optional(v.array(v.string())),
  })),
  negativeTriggers: v.optional(v.object({
    dealBreakers: v.optional(v.array(v.string())),
    offensiveTopics: v.optional(v.array(v.string())),
    toneAversions: v.optional(v.array(v.string())),
  })),
  researchNotes: v.optional(v.string()),
};

// ── Queries ──

// List all staging records for a task
export const listByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("focusGroupStaging")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
  },
});

// List all staging records for a product
export const listByProduct = query({
  args: { productId: v.id("products") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("focusGroupStaging")
      .withIndex("by_product", (q) => q.eq("productId", args.productId))
      .collect();
  },
});

// List only pending_review records for a task
export const listPendingReview = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroupStaging")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
    return all.filter((r) => r.reviewStatus === "pending_review");
  },
});

// Get a single staging record
export const get = query({
  args: { id: v.id("focusGroupStaging") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get summary counts for a task
export const getSummary = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroupStaging")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();

    return {
      total: all.length,
      pending: all.filter((r) => r.reviewStatus === "pending_review").length,
      approved: all.filter((r) => r.reviewStatus === "approved").length,
      rejected: all.filter((r) => r.reviewStatus === "rejected").length,
      needsEnrichment: all.filter((r) => r.needsEnrichment).length,
    };
  },
});

// ── Mutations ──

// Create a single parsed focus group in staging
export const createFromParsed = mutation({
  args: {
    taskId: v.id("tasks"),
    productId: v.optional(v.id("products")),
    projectId: v.id("projects"),
    sourceDocumentId: v.optional(v.id("documents")),
    matchStatus: v.union(
      v.literal("create_new"),
      v.literal("enrich_existing"),
      v.literal("possible_match"),
      v.literal("skip")
    ),
    matchedFocusGroupId: v.optional(v.id("focusGroups")),
    matchConfidence: v.optional(v.number()),
    matchReason: v.optional(v.string()),
    reviewStatus: v.union(
      v.literal("pending_review"),
      v.literal("approved"),
      v.literal("rejected"),
      v.literal("edited"),
      v.literal("imported")
    ),
    reviewNotes: v.optional(v.string()),
    reviewedAt: v.optional(v.number()),
    completenessScore: v.number(),
    missingFields: v.array(v.string()),
    needsEnrichment: v.boolean(),
    ...stagingFocusGroupFields,
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("focusGroupStaging", args);
  },
});

// Create multiple parsed focus groups in staging at once
export const createBatch = mutation({
  args: {
    groups: v.array(v.object({
      taskId: v.id("tasks"),
      productId: v.optional(v.id("products")),
      projectId: v.id("projects"),
      sourceDocumentId: v.optional(v.id("documents")),
      matchStatus: v.union(
        v.literal("create_new"),
        v.literal("enrich_existing"),
        v.literal("possible_match"),
        v.literal("skip")
      ),
      matchedFocusGroupId: v.optional(v.id("focusGroups")),
      matchConfidence: v.optional(v.number()),
      matchReason: v.optional(v.string()),
      reviewStatus: v.union(
        v.literal("pending_review"),
        v.literal("approved"),
        v.literal("rejected"),
        v.literal("edited"),
        v.literal("imported")
      ),
      reviewNotes: v.optional(v.string()),
      reviewedAt: v.optional(v.number()),
      completenessScore: v.number(),
      missingFields: v.array(v.string()),
      needsEnrichment: v.boolean(),
      ...stagingFocusGroupFields,
    })),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const group of args.groups) {
      const id = await ctx.db.insert("focusGroupStaging", group);
      ids.push(id);
    }
    return ids;
  },
});

// Update review status of a staging record
export const updateReviewStatus = mutation({
  args: {
    id: v.id("focusGroupStaging"),
    reviewStatus: v.union(
      v.literal("pending_review"),
      v.literal("approved"),
      v.literal("rejected"),
      v.literal("edited"),
      v.literal("imported")
    ),
    reviewNotes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const record = await ctx.db.get(args.id);
    if (!record) throw new Error("Staging record not found");

    const updates: Record<string, unknown> = {
      reviewStatus: args.reviewStatus,
      reviewedAt: Date.now(),
    };
    if (args.reviewNotes !== undefined) {
      updates.reviewNotes = args.reviewNotes;
    }
    await ctx.db.patch(args.id, updates);
  },
});

// Update any focus group fields on a staging record (for human edits in review)
export const updateFields = mutation({
  args: {
    id: v.id("focusGroupStaging"),
    ...stagingFocusGroupFields,
    // Also allow updating meta fields
    matchStatus: v.optional(v.union(
      v.literal("create_new"),
      v.literal("enrich_existing"),
      v.literal("possible_match"),
      v.literal("skip")
    )),
    matchedFocusGroupId: v.optional(v.id("focusGroups")),
    matchConfidence: v.optional(v.number()),
    matchReason: v.optional(v.string()),
    completenessScore: v.optional(v.number()),
    missingFields: v.optional(v.array(v.string())),
    needsEnrichment: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const record = await ctx.db.get(id);
    if (!record) throw new Error("Staging record not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    if (Object.keys(updates).length > 0) {
      await ctx.db.patch(id, updates);
    }
  },
});

// Approve multiple staging records at once
export const bulkApprove = mutation({
  args: { ids: v.array(v.id("focusGroupStaging")) },
  handler: async (ctx, args) => {
    const now = Date.now();
    for (const id of args.ids) {
      const record = await ctx.db.get(id);
      if (!record) continue;
      await ctx.db.patch(id, {
        reviewStatus: "approved" as const,
        reviewedAt: now,
      });
    }
  },
});

// Reject multiple staging records at once
export const bulkReject = mutation({
  args: { ids: v.array(v.id("focusGroupStaging")) },
  handler: async (ctx, args) => {
    const now = Date.now();
    for (const id of args.ids) {
      const record = await ctx.db.get(id);
      if (!record) continue;
      await ctx.db.patch(id, {
        reviewStatus: "rejected" as const,
        reviewedAt: now,
      });
    }
  },
});
