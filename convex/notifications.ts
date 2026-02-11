import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List recent dashboard-visible notifications (for @human or @all)
export const listForDashboard = query({
  args: { token: v.string() },
  handler: async (ctx, args) => {
    // Validate session
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_token", (q) => q.eq("token", args.token))
      .unique();
    if (!session || session.expiresAt < Date.now()) return [];

    const user = await ctx.db.get(session.userId);
    if (!user || user.status === "disabled") return [];

    // Get recent notifications for @human and @all
    const allNotifications = await ctx.db
      .query("notifications")
      .order("desc")
      .take(200);

    return allNotifications
      .filter((n) => n.mentionedAgent === "@human" || n.mentionedAgent === "@all")
      .slice(0, 50)
      .map((n) => ({
        _id: n._id,
        _creationTime: n._creationTime,
        fromAgent: n.fromAgent,
        content: n.content,
        isRead: user.notificationsReadAt
          ? n._creationTime <= user.notificationsReadAt
          : false,
      }));
  },
});

// Count unread dashboard notifications
export const countUnread = query({
  args: { token: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_token", (q) => q.eq("token", args.token))
      .unique();
    if (!session || session.expiresAt < Date.now()) return 0;

    const user = await ctx.db.get(session.userId);
    if (!user || user.status === "disabled") return 0;

    const readAt = user.notificationsReadAt || 0;

    const allNotifications = await ctx.db
      .query("notifications")
      .order("desc")
      .take(200);

    return allNotifications.filter(
      (n) =>
        (n.mentionedAgent === "@human" || n.mentionedAgent === "@all") &&
        n._creationTime > readAt
    ).length;
  },
});

// Mark all notifications as read for the current user
export const markAllRead = mutation({
  args: { token: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_token", (q) => q.eq("token", args.token))
      .unique();
    if (!session || session.expiresAt < Date.now()) return;

    await ctx.db.patch(session.userId, {
      notificationsReadAt: Date.now(),
    });
  },
});

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
