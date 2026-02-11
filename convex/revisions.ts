import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List revisions by task
export const listByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("revisions")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
  },
});

// List revisions by campaign
export const listByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("revisions")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();
  },
});

// Get revision by id
export const get = query({
  args: { id: v.id("revisions") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Create a revision request
export const create = mutation({
  args: {
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    type: v.union(v.literal("fix"), v.literal("rethink"), v.literal("extend")),
    notes: v.string(),
    agents: v.array(v.object({
      agent: v.string(),
      model: v.string(),
      order: v.number(),
    })),
    runMode: v.union(v.literal("sequential"), v.literal("parallel")),
    version: v.number(),
    originalFilePath: v.string(),
    requestedBy: v.literal("human"),
    status: v.optional(v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed"))),
    requestedAt: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("revisions", {
      taskId: args.taskId,
      campaignId: args.campaignId,
      type: args.type,
      notes: args.notes,
      agents: args.agents,
      runMode: args.runMode,
      status: args.status ?? "pending",
      version: args.version,
      originalFilePath: args.originalFilePath,
      requestedAt: args.requestedAt ?? Date.now(),
      requestedBy: args.requestedBy,
    });
  },
});

// Start a revision (set in_progress)
export const start = mutation({
  args: { id: v.id("revisions") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: "in_progress" as const });
  },
});

// Complete a revision
export const complete = mutation({
  args: {
    id: v.id("revisions"),
    revisedFilePath: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "completed" as const,
      completedAt: Date.now(),
      revisedFilePath: args.revisedFilePath,
    });
  },
});
