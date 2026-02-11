import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List messages for a task
export const listByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
  },
});

// Create a new message
export const create = mutation({
  args: {
    taskId: v.id("tasks"),
    fromAgent: v.string(),
    content: v.string(),
    mentions: v.optional(v.array(v.string())),
    attachments: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("messages", {
      taskId: args.taskId,
      fromAgent: args.fromAgent,
      content: args.content,
      mentions: args.mentions ?? [],
      attachments: args.attachments,
    });
  },
});
