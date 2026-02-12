import { mutation, query, MutationCtx } from "./_generated/server";
import { v } from "convex/values";
import { Id } from "./_generated/dataModel";

// Internal helper — call from other mutations to log activity inline
export async function logActivity(
  ctx: MutationCtx,
  opts: {
    projectId?: Id<"projects">;
    type: string;
    agentName: string;
    message: string;
    taskId?: Id<"tasks">;
    campaignId?: Id<"campaigns">;
    metadata?: any;
  },
) {
  await ctx.db.insert("activities", {
    projectId: opts.projectId,
    type: opts.type,
    agentName: opts.agentName,
    message: opts.message,
    taskId: opts.taskId,
    campaignId: opts.campaignId,
    metadata: opts.metadata,
  });
}

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
