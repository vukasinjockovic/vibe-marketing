import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List all active projects
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("projects")
      .withIndex("by_status", (q) => q.eq("status", "active"))
      .collect();
  },
});

// Get project by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("projects")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// Create a new project
export const create = mutation({
  args: {
    name: v.string(),
    slug: v.string(),
    description: v.optional(v.string()),
    icon: v.optional(v.string()),
    color: v.string(),
  },
  handler: async (ctx, args) => {
    // Check slug uniqueness
    const existing = await ctx.db
      .query("projects")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();

    if (existing) {
      throw new Error(`Project with slug "${args.slug}" already exists`);
    }

    return await ctx.db.insert("projects", {
      name: args.name,
      slug: args.slug,
      description: args.description,
      appearance: {
        icon: args.icon,
        color: args.color,
      },
      status: "active",
      stats: {
        productCount: 0,
        campaignCount: 0,
        activeCampaignCount: 0,
        taskCount: 0,
        completedTaskCount: 0,
      },
      createdAt: Date.now(),
    });
  },
});

// Update project
export const update = mutation({
  args: {
    id: v.id("projects"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    icon: v.optional(v.string()),
    color: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const project = await ctx.db.get(args.id);
    if (!project) throw new Error("Project not found");

    const updates: Record<string, unknown> = {};
    if (args.name !== undefined) updates.name = args.name;
    if (args.description !== undefined) updates.description = args.description;
    if (args.icon !== undefined || args.color !== undefined) {
      updates.appearance = {
        ...project.appearance,
        ...(args.icon !== undefined && { icon: args.icon }),
        ...(args.color !== undefined && { color: args.color }),
      };
    }

    await ctx.db.patch(args.id, updates);
  },
});

// Archive project
export const archive = mutation({
  args: { id: v.id("projects") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: "archived" as const });
  },
});

// Update denormalized stats
export const updateStats = mutation({
  args: {
    id: v.id("projects"),
    stats: v.object({
      productCount: v.number(),
      campaignCount: v.number(),
      activeCampaignCount: v.number(),
      taskCount: v.number(),
      completedTaskCount: v.number(),
      lastActivityAt: v.optional(v.number()),
    }),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { stats: args.stats });
  },
});

// Compute live stats for a project (not denormalized)
export const getStats = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const products = await ctx.db
      .query("products")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const campaigns = await ctx.db
      .query("campaigns")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();

    return {
      productCount: products.length,
      campaignCount: campaigns.length,
      activeCampaignCount: campaigns.filter((c) => c.status === "active").length,
      taskCount: tasks.length,
      completedTaskCount: tasks.filter((t) => t.status === "completed").length,
    };
  },
});

// Delete a project
export const remove = mutation({
  args: { id: v.id("projects") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
