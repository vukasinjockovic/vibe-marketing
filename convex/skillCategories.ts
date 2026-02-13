import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

export const list = query({
  args: {},
  handler: async (ctx) => {
    const cats = await ctx.db.query("skillCategories").collect();
    return cats.sort((a, b) => a.sortOrder - b.sortOrder);
  },
});

export const listForPipeline = query({
  args: { agentNames: v.array(v.string()) },
  handler: async (ctx, args) => {
    const cats = await ctx.db.query("skillCategories").collect();
    const agentSet = new Set(args.agentNames);
    const matched = cats.filter((cat) => {
      if (!cat.pipelineAgentNames?.length) return false;
      return cat.pipelineAgentNames.some((name) => agentSet.has(name));
    });
    return matched.sort((a, b) => a.sortOrder - b.sortOrder);
  },
});

export const upsert = mutation({
  args: {
    key: v.string(),
    displayName: v.string(),
    description: v.string(),
    sortOrder: v.number(),
    scope: v.union(
      v.literal("copy"),
      v.literal("research"),
      v.literal("visual"),
      v.literal("quality"),
      v.literal("general")
    ),
    maxPerPipelineStep: v.optional(v.number()),
    selectionMode: v.optional(v.string()),
    pipelineAgentNames: v.optional(v.array(v.string())),
    allowNone: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("skillCategories")
      .withIndex("by_key", (q) => q.eq("key", args.key))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, args);
      return existing._id;
    } else {
      return await ctx.db.insert("skillCategories", args);
    }
  },
});
