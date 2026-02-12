import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("skills").collect();
  },
});

export const get = query({
  args: { id: v.id("skills") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("skills")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .first();
  },
});

export const listByCategory = query({
  args: { category: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("skills")
      .withIndex("by_category", (q) => q.eq("category", args.category))
      .collect();
  },
});

export const listCampaignSelectable = query({
  args: {},
  handler: async (ctx) => {
    const all = await ctx.db.query("skills").collect();
    return all.filter((s) => s.isCampaignSelectable);
  },
});

export const update = mutation({
  args: {
    id: v.id("skills"),
    displayName: v.optional(v.string()),
    description: v.optional(v.string()),
    category: v.optional(v.string()),
    type: v.optional(v.union(v.literal("mbook"), v.literal("procedure"), v.literal("community"), v.literal("custom"))),
    isAutoActive: v.optional(v.boolean()),
    isCampaignSelectable: v.optional(v.boolean()),
    tagline: v.optional(v.string()),
    dashboardDescription: v.optional(v.string()),
    subSelections: v.optional(v.array(v.object({
      key: v.string(),
      label: v.string(),
      description: v.optional(v.string()),
    }))),
  },
  handler: async (ctx, { id, ...fields }) => {
    const existing = await ctx.db.get(id);
    if (!existing) throw new Error("Skill not found");
    await ctx.db.patch(id, fields);
    return id;
  },
});

export const remove = mutation({
  args: { id: v.id("skills") },
  handler: async (ctx, args) => {
    const existing = await ctx.db.get(args.id);
    if (!existing) throw new Error("Skill not found");
    await ctx.db.delete(args.id);
  },
});

export const markMissing = mutation({
  args: { id: v.id("skills") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { syncStatus: "file_missing" as const });
  },
});

export const listGroupedByCategory = query({
  args: {},
  handler: async (ctx) => {
    const skills = await ctx.db.query("skills").collect();
    const categories = await ctx.db.query("skillCategories").collect();
    categories.sort((a, b) => a.sortOrder - b.sortOrder);

    const grouped: { category: typeof categories[0]; skills: typeof skills }[] = [];
    const skillsByCategory = new Map<string, typeof skills>();

    for (const skill of skills) {
      const list = skillsByCategory.get(skill.category) || [];
      list.push(skill);
      skillsByCategory.set(skill.category, list);
    }

    for (const cat of categories) {
      const catSkills = skillsByCategory.get(cat.key) || [];
      catSkills.sort((a, b) => a.displayName.localeCompare(b.displayName));
      grouped.push({ category: cat, skills: catSkills });
    }

    // Include uncategorized skills
    const knownKeys = new Set(categories.map((c) => c.key));
    const uncategorized = skills.filter((s) => !knownKeys.has(s.category));
    if (uncategorized.length > 0) {
      grouped.push({
        category: { _id: "" as any, _creationTime: 0, key: "other", displayName: "Other", description: "Uncategorized skills", sortOrder: 999, scope: "general" as const },
        skills: uncategorized.sort((a, b) => a.displayName.localeCompare(b.displayName)),
      });
    }

    return grouped;
  },
});

export const upsertBySlug = mutation({
  args: {
    slug: v.string(),
    name: v.string(),
    displayName: v.string(),
    description: v.string(),
    category: v.string(),
    type: v.union(v.literal("mbook"), v.literal("procedure"), v.literal("community"), v.literal("custom")),
    isAutoActive: v.boolean(),
    isCampaignSelectable: v.boolean(),
    subSelections: v.optional(v.array(v.object({
      key: v.string(),
      label: v.string(),
      description: v.optional(v.string()),
    }))),
    filePath: v.string(),
    fileHash: v.optional(v.string()),
    tagline: v.optional(v.string()),
    dashboardDescription: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("skills")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .first();

    if (existing) {
      await ctx.db.patch(existing._id, {
        ...args,
        lastSyncedAt: Date.now(),
        syncStatus: "synced" as const,
      });
      return existing._id;
    } else {
      return await ctx.db.insert("skills", {
        ...args,
        lastSyncedAt: Date.now(),
        syncStatus: "synced" as const,
      });
    }
  },
});
