import { mutation, query } from "./_generated/server";
import { ConvexError, v } from "convex/values";

const stepValidator = v.object({
  order: v.number(),
  agent: v.optional(v.string()),
  model: v.optional(v.string()),
  label: v.string(),
  description: v.optional(v.string()),
  outputDir: v.optional(v.string()),
  skillOverrides: v.optional(v.array(v.object({
    skillId: v.id("skills"),
    subSelections: v.optional(v.array(v.string())),
  }))),
});

const branchValidator = v.object({
  triggerAfterStep: v.number(),
  agent: v.string(),
  model: v.optional(v.string()),
  label: v.string(),
  description: v.optional(v.string()),
  skillOverrides: v.optional(v.array(v.object({
    skillId: v.id("skills"),
    subSelections: v.optional(v.array(v.string())),
  }))),
});

// List all pipelines
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("pipelines").collect();
  },
});

// List preset pipelines
export const listPresets = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("pipelines")
      .withIndex("by_type", (q) => q.eq("type", "preset"))
      .collect();
  },
});

// Get pipeline by id
export const get = query({
  args: { id: v.id("pipelines") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get pipeline by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// Create a pipeline
export const create = mutation({
  args: {
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    type: v.union(v.literal("preset"), v.literal("custom")),
    forkedFrom: v.optional(v.id("pipelines")),
    mainSteps: v.array(stepValidator),
    parallelBranches: v.optional(v.array(branchValidator)),
    convergenceStep: v.optional(v.number()),
    onComplete: v.object({
      telegram: v.boolean(),
      summary: v.boolean(),
      generateManifest: v.boolean(),
    }),
    requiredAgentCategories: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      return { error: `Pipeline with slug "${args.slug}" already exists` };
    }

    const id = await ctx.db.insert("pipelines", args);
    return { id };
  },
});

// Fork a pipeline into a custom copy
export const fork = mutation({
  args: {
    pipelineId: v.id("pipelines"),
    newName: v.string(),
    newSlug: v.string(),
  },
  handler: async (ctx, args) => {
    const original = await ctx.db.get(args.pipelineId);
    if (!original) {
      return { error: "Pipeline not found" };
    }

    const existing = await ctx.db
      .query("pipelines")
      .withIndex("by_slug", (q) => q.eq("slug", args.newSlug))
      .unique();
    if (existing) {
      return { error: `Pipeline with slug "${args.newSlug}" already exists` };
    }

    const id = await ctx.db.insert("pipelines", {
      name: args.newName,
      slug: args.newSlug,
      description: original.description,
      type: "custom",
      forkedFrom: args.pipelineId,
      mainSteps: original.mainSteps,
      parallelBranches: original.parallelBranches,
      convergenceStep: original.convergenceStep,
      onComplete: original.onComplete,
      requiredAgentCategories: original.requiredAgentCategories,
    });
    return { id };
  },
});
