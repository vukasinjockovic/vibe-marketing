import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List latest 50 activities (newest first)
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("activities").order("desc").take(50);
  },
});

// List activities by project
export const listByProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("activities")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .take(50);
  },
});

// List activities by agent name
export const listByAgent = query({
  args: { agentName: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("activities")
      .withIndex("by_agent", (q) => q.eq("agentName", args.agentName))
      .take(50);
  },
});

// Log an activity
export const log = mutation({
  args: {
    projectId: v.optional(v.id("projects")),
    type: v.string(),
    agentName: v.string(),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    message: v.string(),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", {
      projectId: args.projectId,
      type: args.type,
      agentName: args.agentName,
      taskId: args.taskId,
      campaignId: args.campaignId,
      message: args.message,
      metadata: args.metadata,
    });
  },
});
