import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List all service categories ordered by sortOrder
export const listCategories = query({
  args: {},
  handler: async (ctx) => {
    const categories = await ctx.db.query("serviceCategories").collect();
    return categories.sort((a, b) => a.sortOrder - b.sortOrder);
  },
});

// List services by category
export const listByCategory = query({
  args: { categoryId: v.id("serviceCategories") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("services")
      .withIndex("by_category", (q) => q.eq("categoryId", args.categoryId))
      .collect();
  },
});

// List all active services
export const listActive = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("services")
      .withIndex("by_active", (q) => q.eq("isActive", true))
      .collect();
  },
});

// Get service by id
export const get = query({
  args: { id: v.id("services") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Resolve: find highest-priority active service for a category name
export const resolve = query({
  args: { categoryName: v.string() },
  handler: async (ctx, args) => {
    const category = await ctx.db
      .query("serviceCategories")
      .withIndex("by_name", (q) => q.eq("name", args.categoryName))
      .unique();

    if (!category) return null;

    const services = await ctx.db
      .query("services")
      .withIndex("by_category", (q) => q.eq("categoryId", category._id))
      .collect();

    const active = services
      .filter((s) => s.isActive)
      .sort((a, b) => a.priority - b.priority);

    return active[0] ?? null;
  },
});

// Create a service
export const create = mutation({
  args: {
    categoryId: v.id("serviceCategories"),
    subcategory: v.optional(v.string()),
    name: v.string(),
    displayName: v.string(),
    description: v.string(),
    isActive: v.boolean(),
    priority: v.number(),
    apiKeyEnvVar: v.string(),
    apiKeyConfigured: v.boolean(),
    apiKeyValue: v.optional(v.string()),
    extraConfig: v.optional(v.string()),
    scriptPath: v.string(),
    mcpServer: v.optional(v.string()),
    costInfo: v.string(),
    useCases: v.array(v.string()),
    docsUrl: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("services", {
      categoryId: args.categoryId,
      subcategory: args.subcategory,
      name: args.name,
      displayName: args.displayName,
      description: args.description,
      isActive: args.isActive,
      priority: args.priority,
      apiKeyEnvVar: args.apiKeyEnvVar,
      apiKeyConfigured: args.apiKeyConfigured,
      apiKeyValue: args.apiKeyValue,
      extraConfig: args.extraConfig,
      scriptPath: args.scriptPath,
      mcpServer: args.mcpServer,
      costInfo: args.costInfo,
      useCases: args.useCases,
      docsUrl: args.docsUrl,
    });
  },
});

// Update a service (partial fields)
export const update = mutation({
  args: {
    id: v.id("services"),
    isActive: v.optional(v.boolean()),
    priority: v.optional(v.number()),
    apiKeyConfigured: v.optional(v.boolean()),
    apiKeyValue: v.optional(v.string()),
    extraConfig: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const service = await ctx.db.get(args.id);
    if (!service) throw new Error("Service not found");

    const updates: Record<string, unknown> = {};
    if (args.isActive !== undefined) updates.isActive = args.isActive;
    if (args.priority !== undefined) updates.priority = args.priority;
    if (args.apiKeyConfigured !== undefined) updates.apiKeyConfigured = args.apiKeyConfigured;
    if (args.apiKeyValue !== undefined) updates.apiKeyValue = args.apiKeyValue;
    if (args.extraConfig !== undefined) updates.extraConfig = args.extraConfig;

    await ctx.db.patch(args.id, updates);
  },
});

// Toggle isActive on a service
export const toggleActive = mutation({
  args: { id: v.id("services") },
  handler: async (ctx, args) => {
    const service = await ctx.db.get(args.id);
    if (!service) throw new Error("Service not found");

    await ctx.db.patch(args.id, { isActive: !service.isActive });
  },
});
