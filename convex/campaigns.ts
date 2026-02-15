import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";
import { logActivity } from "./activities";

// Shared skillConfig validator (new generic format + legacy compat)
const skillConfigValidator = v.optional(v.object({
  // Legacy fields
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
  // New generic format
  selections: v.optional(v.array(v.object({
    categoryKey: v.string(),
    skillId: v.id("skills"),
    subSelections: v.optional(v.array(v.string())),
  }))),
  agentOverrides: v.optional(v.array(v.object({
    agentName: v.string(),
    pipelineStep: v.optional(v.number()),
    selections: v.optional(v.array(v.object({
      categoryKey: v.string(),
      skillId: v.id("skills"),
      subSelections: v.optional(v.array(v.string())),
    }))),
    skillOverrides: v.optional(v.array(v.object({
      skillId: v.id("skills"),
      subSelections: v.optional(v.array(v.string())),
    }))),
  }))),
  summary: v.optional(v.string()),
}));

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
    products: v.array(v.object({
      productId: v.id("products"),
      role: v.union(v.literal("main"), v.literal("upsell"), v.literal("addon"), v.literal("downsell")),
    })),
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
    skillConfig: skillConfigValidator,
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
    targetArticleCount: v.optional(v.number()),
    productionManifest: v.optional(v.object({
      articles: v.object({
        count: v.number(),
        perArticle: v.object({
          heroImage: v.optional(v.boolean()),
          socialPosts: v.optional(v.object({
            facebook: v.optional(v.number()),
            instagram: v.optional(v.number()),
            x: v.optional(v.number()),
            linkedin: v.optional(v.number()),
            tiktok: v.optional(v.number()),
            pinterest: v.optional(v.number()),
            vk: v.optional(v.number()),
          })),
          emailExcerpt: v.optional(v.boolean()),
          videoScript: v.optional(v.boolean()),
          redditVersion: v.optional(v.boolean()),
        }),
      }),
      standalone: v.optional(v.object({
        emailSequence: v.optional(v.number()),
        landingPage: v.optional(v.number()),
        leadMagnet: v.optional(v.number()),
        adCopySet: v.optional(v.number()),
        pressRelease: v.optional(v.number()),
        ebookFull: v.optional(v.number()),
      })),
    })),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("campaigns")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      throw new Error(`Campaign with slug "${args.slug}" already exists`);
    }

    const id = await ctx.db.insert("campaigns", {
      ...args,
      status: "planning",
    });
    await logActivity(ctx, {
      projectId: args.projectId,
      type: "campaign_created",
      agentName: "wookashin",
      message: `Created campaign "${args.name}"`,
      campaignId: id,
    });
    return id;
  },
});

// Update campaign (partial)
export const update = mutation({
  args: {
    id: v.id("campaigns"),
    name: v.optional(v.string()),
    slug: v.optional(v.string()),
    description: v.optional(v.string()),
    notes: v.optional(v.string()),
    products: v.optional(v.array(v.object({
      productId: v.id("products"),
      role: v.union(v.literal("main"), v.literal("upsell"), v.literal("addon"), v.literal("downsell")),
    }))),
    targetFocusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    pipelineId: v.optional(v.id("pipelines")),
    pipelineSnapshot: v.optional(v.any()),
    targetArticleCount: v.optional(v.number()),
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
    skillConfig: skillConfigValidator,
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
    productionManifest: v.optional(v.object({
      articles: v.object({
        count: v.number(),
        perArticle: v.object({
          heroImage: v.optional(v.boolean()),
          socialPosts: v.optional(v.object({
            facebook: v.optional(v.number()),
            instagram: v.optional(v.number()),
            x: v.optional(v.number()),
            linkedin: v.optional(v.number()),
            tiktok: v.optional(v.number()),
            pinterest: v.optional(v.number()),
            vk: v.optional(v.number()),
          })),
          emailExcerpt: v.optional(v.boolean()),
          videoScript: v.optional(v.boolean()),
          redditVersion: v.optional(v.boolean()),
        }),
      }),
      standalone: v.optional(v.object({
        emailSequence: v.optional(v.number()),
        landingPage: v.optional(v.number()),
        leadMagnet: v.optional(v.number()),
        adCopySet: v.optional(v.number()),
        pressRelease: v.optional(v.number()),
        ebookFull: v.optional(v.number()),
      })),
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

// Activate campaign — generates tasks and dispatches first agent
export const activate = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.id);
    if (!campaign) throw new Error("Campaign not found");

    // Snapshot pipeline if not already done
    if (!campaign.pipelineSnapshot) {
      const pipeline = await ctx.db.get(campaign.pipelineId);
      if (pipeline) {
        await ctx.db.patch(args.id, { pipelineSnapshot: pipeline });
      }
    }

    await ctx.db.patch(args.id, {
      status: "active" as const,
      activatedAt: Date.now(),
    });

    await logActivity(ctx, {
      projectId: campaign.projectId,
      type: "campaign_activated",
      agentName: "wookashin",
      message: `Activated campaign "${campaign.name}"`,
      campaignId: args.id,
    });

    // Generate tasks from pipeline template (only if none exist yet)
    const existingTasks = await ctx.db
      .query("tasks")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.id))
      .first();
    if (!existingTasks) {
      await ctx.scheduler.runAfter(0, internal.orchestrator.generateTasksForCampaign, {
        campaignId: args.id,
      });
    }

    // Dispatch first task's first agent (slight delay to let tasks generate)
    await ctx.scheduler.runAfter(500, internal.orchestrator.dispatchNextTask, {
      campaignId: args.id,
    });
  },
});

// Pause campaign — running agents finish current step but no further dispatch
export const pause = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "paused" as const,
      pausedAt: Date.now(),
    });
  },
});

// Resume campaign — re-dispatch any stuck tasks
export const resume = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.id);
    if (!campaign) throw new Error("Campaign not found");

    await ctx.db.patch(args.id, {
      status: "active" as const,
    });

    // Find tasks that are mid-pipeline but have no lock (agent finished or crashed)
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.id))
      .collect();

    for (const task of tasks) {
      if (
        task.status !== "completed" &&
        task.status !== "cancelled" &&
        task.status !== "blocked" &&
        task.status !== "backlog" &&
        !task.lockedBy
      ) {
        // Task is mid-pipeline with no lock — re-dispatch current step agent
        const currentStep = task.pipeline[task.pipelineStep];
        if (currentStep?.agent) {
          await ctx.scheduler.runAfter(0, internal.orchestrator.requestDispatch, {
            taskId: task._id,
            agentName: currentStep.agent,
          });
        }
      }
    }

    // Also try dispatching next task if none are running
    await ctx.scheduler.runAfter(100, internal.orchestrator.dispatchNextTask, {
      campaignId: args.id,
    });
  },
});

// Complete campaign
export const complete = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.id);
    await ctx.db.patch(args.id, {
      status: "completed" as const,
      completedAt: Date.now(),
    });
    if (campaign) {
      await logActivity(ctx, {
        projectId: campaign.projectId,
        type: "campaign_completed",
        agentName: "system",
        message: `Campaign "${campaign.name}" completed`,
        campaignId: args.id,
      });
    }
  },
});
