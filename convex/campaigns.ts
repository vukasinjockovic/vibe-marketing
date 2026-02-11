import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List campaigns by project
export const list = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("campaigns")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// Get campaign by id
export const get = query({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get campaign by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("campaigns")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// List active campaigns
export const listActive = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("campaigns")
      .withIndex("by_status", (q) => q.eq("status", "active"))
      .collect();
  },
});

// Create a campaign
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    productId: v.id("products"),
    pipelineId: v.id("pipelines"),
    pipelineSnapshot: v.any(),
    targetFocusGroupIds: v.array(v.id("focusGroups")),
    deliverableConfig: v.optional(v.object({
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      socialTikTok: v.optional(v.boolean()),
      socialPinterest: v.optional(v.boolean()),
      socialVK: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
      landingPage: v.optional(v.boolean()),
      emailSequence: v.optional(v.boolean()),
      leadMagnet: v.optional(v.boolean()),
      adCopySet: v.optional(v.boolean()),
      pressRelease: v.optional(v.boolean()),
      ebookFull: v.optional(v.boolean()),
    })),
    seedKeywords: v.array(v.string()),
    competitorUrls: v.array(v.string()),
    notes: v.optional(v.string()),
    skillConfig: v.optional(v.object({
      offerFramework: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      persuasionSkills: v.optional(v.array(v.object({
        skillId: v.id("skills"),
        subSelections: v.optional(v.array(v.string())),
      }))),
      primaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      secondaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      agentOverrides: v.optional(v.array(v.object({
        agentName: v.string(),
        pipelineStep: v.number(),
        skillOverrides: v.array(v.object({
          skillId: v.id("skills"),
          subSelections: v.optional(v.array(v.string())),
        })),
      }))),
      summary: v.optional(v.string()),
    })),
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
    targetArticleCount: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("campaigns")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      throw new Error(`Campaign with slug "${args.slug}" already exists`);
    }

    return await ctx.db.insert("campaigns", {
      ...args,
      status: "planning",
    });
  },
});

// Update campaign (partial)
export const update = mutation({
  args: {
    id: v.id("campaigns"),
    name: v.optional(v.string()),
    description: v.optional(v.string()),
    notes: v.optional(v.string()),
    seedKeywords: v.optional(v.array(v.string())),
    competitorUrls: v.optional(v.array(v.string())),
    deliverableConfig: v.optional(v.object({
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      socialTikTok: v.optional(v.boolean()),
      socialPinterest: v.optional(v.boolean()),
      socialVK: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
      landingPage: v.optional(v.boolean()),
      emailSequence: v.optional(v.boolean()),
      leadMagnet: v.optional(v.boolean()),
      adCopySet: v.optional(v.boolean()),
      pressRelease: v.optional(v.boolean()),
      ebookFull: v.optional(v.boolean()),
    })),
    skillConfig: v.optional(v.object({
      offerFramework: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      persuasionSkills: v.optional(v.array(v.object({
        skillId: v.id("skills"),
        subSelections: v.optional(v.array(v.string())),
      }))),
      primaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      secondaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      agentOverrides: v.optional(v.array(v.object({
        agentName: v.string(),
        pipelineStep: v.number(),
        skillOverrides: v.array(v.object({
          skillId: v.id("skills"),
          subSelections: v.optional(v.array(v.string())),
        })),
      }))),
      summary: v.optional(v.string()),
    })),
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const campaign = await ctx.db.get(id);
    if (!campaign) throw new Error("Campaign not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    await ctx.db.patch(id, updates);
  },
});

// Activate campaign
export const activate = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "active" as const,
      activatedAt: Date.now(),
    });
  },
});

// Pause campaign
export const pause = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "paused" as const,
      pausedAt: Date.now(),
    });
  },
});

// Complete campaign
export const complete = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "completed" as const,
      completedAt: Date.now(),
    });
  },
});
