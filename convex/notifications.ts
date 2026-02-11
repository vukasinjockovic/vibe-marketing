import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List undelivered notifications for an agent
export const listUndelivered = query({
  args: { mentionedAgent: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("notifications")
      .withIndex("by_undelivered", (q) =>
        q.eq("mentionedAgent", args.mentionedAgent).eq("delivered", false)
      )
      .collect();
  },
});

// Create a notification
export const create = mutation({
  args: {
    mentionedAgent: v.string(),
    fromAgent: v.string(),
    taskId: v.optional(v.id("tasks")),
    content: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("notifications", {
      mentionedAgent: args.mentionedAgent,
      fromAgent: args.fromAgent,
      taskId: args.taskId,
      content: args.content,
      delivered: false,
    });
  },
});

// Mark a single notification as delivered
export const markDelivered = mutation({
  args: { id: v.id("notifications") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      delivered: true,
      deliveredAt: Date.now(),
    });
  },
});

// Mark all undelivered notifications for an agent as delivered
export const markAllDelivered = mutation({
  args: { mentionedAgent: v.string() },
  handler: async (ctx, args) => {
    const undelivered = await ctx.db
      .query("notifications")
      .withIndex("by_undelivered", (q) =>
        q.eq("mentionedAgent", args.mentionedAgent).eq("delivered", false)
      )
      .collect();

    for (const n of undelivered) {
      await ctx.db.patch(n._id, {
        delivered: true,
        deliveredAt: Date.now(),
      });
    }
  },
});
