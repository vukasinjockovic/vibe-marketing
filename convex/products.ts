import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { logActivity } from "./activities";

// List products by project
export const list = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("products")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// Get product by id
export const get = query({
  args: { id: v.id("products") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get product by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("products")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// Create a new product
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    context: v.object({
      whatItIs: v.string(),
      features: v.array(v.string()),
      pricing: v.optional(v.string()),
      usps: v.array(v.string()),
      targetMarket: v.string(),
      productUrl: v.optional(v.string()),
    }),
    competitorsOverride: v.optional(v.array(v.string())),
    brandVoiceOverride: v.optional(v.object({
      tone: v.string(),
      style: v.string(),
      vocabulary: v.object({
        preferred: v.array(v.string()),
        avoided: v.array(v.string()),
      }),
      examples: v.optional(v.string()),
      notes: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("products")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      throw new Error(`Product with slug "${args.slug}" already exists`);
    }

    const id = await ctx.db.insert("products", {
      projectId: args.projectId,
      name: args.name,
      slug: args.slug,
      description: args.description,
      context: args.context,
      competitorsOverride: args.competitorsOverride,
      brandVoiceOverride: args.brandVoiceOverride,
      status: "active",
    });
    await logActivity(ctx, {
      projectId: args.projectId,
      type: "product_created",
      agentName: "wookashin",
      message: `Created product "${args.name}"`,
    });
    return id;
  },
});

// Update product (partial)
export const update = mutation({
  args: {
    id: v.id("products"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    context: v.optional(v.object({
      whatItIs: v.string(),
      features: v.array(v.string()),
      pricing: v.optional(v.string()),
      usps: v.array(v.string()),
      targetMarket: v.string(),
      productUrl: v.optional(v.string()),
    })),
    competitorsOverride: v.optional(v.array(v.string())),
    brandVoiceOverride: v.optional(v.object({
      tone: v.string(),
      style: v.string(),
      vocabulary: v.object({
        preferred: v.array(v.string()),
        avoided: v.array(v.string()),
      }),
      examples: v.optional(v.string()),
      notes: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const product = await ctx.db.get(args.id);
    if (!product) throw new Error("Product not found");

    const updates: Record<string, unknown> = {};
    if (args.name !== undefined) updates.name = args.name;
    if (args.description !== undefined) updates.description = args.description;
    if (args.context !== undefined) updates.context = args.context;
    if (args.competitorsOverride !== undefined) updates.competitorsOverride = args.competitorsOverride;
    if (args.brandVoiceOverride !== undefined) updates.brandVoiceOverride = args.brandVoiceOverride;

    await ctx.db.patch(args.id, updates);
  },
});

// Archive product
export const archive = mutation({
  args: { id: v.id("products") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: "archived" as const });
  },
});

// Delete a product permanently
export const remove = mutation({
  args: { id: v.id("products") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
