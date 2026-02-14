import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { logActivity } from "./activities";

const platformValidator = v.union(
  v.literal("facebook"),
  v.literal("x"),
  v.literal("linkedin"),
  v.literal("tiktok"),
  v.literal("instagram")
);

// List channels by project
export const list = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("channels")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// Get channel by id
export const get = query({
  args: { id: v.id("channels") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get channel by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("channels")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// Create a new channel
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    name: v.string(),
    slug: v.string(),
    platform: platformValidator,
    description: v.optional(v.string()),
    platformConfig: v.optional(v.object({
      pageUrl: v.optional(v.string()),
      username: v.optional(v.string()),
      pageId: v.optional(v.string()),
      countryRestrictions: v.optional(v.array(v.string())),
    })),
    postingConfig: v.optional(v.object({
      postsPerDay: v.optional(v.number()),
      minSpacingMinutes: v.optional(v.number()),
      primeTimeSlots: v.optional(v.array(v.string())),
      timezone: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("channels")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      throw new Error(`Channel with slug "${args.slug}" already exists`);
    }

    const id = await ctx.db.insert("channels", {
      ...args,
      status: "active",
      createdAt: Date.now(),
    });
    await logActivity(ctx, {
      projectId: args.projectId,
      type: "channel_created",
      agentName: "wookashin",
      message: `Created ${args.platform} channel "${args.name}"`,
    });
    return id;
  },
});

// Update channel (partial)
export const update = mutation({
  args: {
    id: v.id("channels"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    platformConfig: v.optional(v.object({
      pageUrl: v.optional(v.string()),
      username: v.optional(v.string()),
      pageId: v.optional(v.string()),
      countryRestrictions: v.optional(v.array(v.string())),
    })),
    postingConfig: v.optional(v.object({
      postsPerDay: v.optional(v.number()),
      minSpacingMinutes: v.optional(v.number()),
      primeTimeSlots: v.optional(v.array(v.string())),
      timezone: v.optional(v.string()),
    })),
    status: v.optional(v.union(v.literal("active"), v.literal("paused"), v.literal("archived"))),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const channel = await ctx.db.get(id);
    if (!channel) throw new Error("Channel not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    await ctx.db.patch(id, updates);
  },
});

// Delete a channel permanently
export const remove = mutation({
  args: { id: v.id("channels") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
