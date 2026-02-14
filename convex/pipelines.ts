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

// List pipelines by category
export const listByCategory = query({
  args: { category: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("pipelines")
      .withIndex("by_category", (q) => q.eq("category", args.category as any))
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
    category: v.optional(v.union(
      v.literal("sales"),
      v.literal("engagement"),
      v.literal("audience"),
    )),
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

// Rename a pipeline
export const rename = mutation({
  args: {
    id: v.id("pipelines"),
    name: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { name: args.name });
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
      category: original.category,
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

// Update a pipeline
export const update = mutation({
  args: {
    id: v.id("pipelines"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    mainSteps: v.array(stepValidator),
    parallelBranches: v.optional(v.array(branchValidator)),
    convergenceStep: v.optional(v.number()),
    onComplete: v.object({
      telegram: v.boolean(),
      summary: v.boolean(),
      generateManifest: v.boolean(),
    }),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const pipeline = await ctx.db.get(id);
    if (!pipeline) throw new ConvexError("Pipeline not found");

    // Check slug uniqueness if changed
    if (fields.slug !== pipeline.slug) {
      const existing = await ctx.db
        .query("pipelines")
        .withIndex("by_slug", (q) => q.eq("slug", fields.slug))
        .unique();
      if (existing) {
        throw new ConvexError(`Pipeline with slug "${fields.slug}" already exists`);
      }
    }

    await ctx.db.patch(id, fields);
  },
});

// Delete a pipeline
export const remove = mutation({
  args: { id: v.id("pipelines") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// Fix step models to match agent defaults
export const fixStepModels = mutation({
  args: {
    id: v.id("pipelines"),
    agentModelMap: v.any(),
  },
  handler: async (ctx, args) => {
    const pipeline = await ctx.db.get(args.id);
    if (!pipeline) throw new ConvexError("Pipeline not found");
    const map = args.agentModelMap as Record<string, string>;
    const mainSteps = (pipeline.mainSteps || []).map((s: any) => ({
      ...s,
      ...(s.agent && map[s.agent] ? { model: map[s.agent] } : {}),
    }));
    const parallelBranches = (pipeline.parallelBranches || []).map((b: any) => ({
      ...b,
      ...(b.agent && map[b.agent] ? { model: map[b.agent] } : {}),
    }));
    await ctx.db.patch(args.id, { mainSteps, parallelBranches });
  },
});