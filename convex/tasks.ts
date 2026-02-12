import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List tasks by project
export const listByProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// List tasks by campaign
export const listByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();
  },
});

// List tasks by project + status
export const listByStatus = query({
  args: {
    projectId: v.id("projects"),
    status: v.union(
      v.literal("backlog"),
      v.literal("researched"),
      v.literal("briefed"),
      v.literal("drafted"),
      v.literal("reviewed"),
      v.literal("revision_needed"),
      v.literal("humanized"),
      v.literal("completed"),
      v.literal("cancelled"),
      v.literal("blocked")
    ),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_project_status", (q) =>
        q.eq("projectId", args.projectId).eq("status", args.status)
      )
      .collect();
  },
});

// Get task by id
export const get = query({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Create a task
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    title: v.string(),
    description: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    pipeline: v.array(v.object({
      step: v.number(),
      status: v.string(),
      agent: v.optional(v.string()),
      model: v.optional(v.string()),
      description: v.string(),
      outputDir: v.optional(v.string()),
    })),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("urgent")),
    createdBy: v.string(),
    contentType: v.optional(v.string()),
    contentSlug: v.optional(v.string()),
    contentBrief: v.optional(v.string()),
    deliverables: v.optional(v.object({
      blogPost: v.optional(v.boolean()),
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
    })),
    targetKeywords: v.optional(v.array(v.string())),
    focusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      ...args,
      status: "backlog",
      pipelineStep: 0,
      subscriberNames: [],
      assigneeNames: [],
    });
  },
});

// Update task (partial)
export const update = mutation({
  args: {
    id: v.id("tasks"),
    status: v.optional(v.union(
      v.literal("backlog"),
      v.literal("researched"),
      v.literal("briefed"),
      v.literal("drafted"),
      v.literal("reviewed"),
      v.literal("revision_needed"),
      v.literal("humanized"),
      v.literal("completed"),
      v.literal("cancelled"),
      v.literal("blocked")
    )),
    title: v.optional(v.string()),
    description: v.optional(v.string()),
    pipeline: v.optional(v.array(v.object({
      step: v.number(),
      status: v.string(),
      agent: v.optional(v.string()),
      model: v.optional(v.string()),
      description: v.string(),
      outputDir: v.optional(v.string()),
    }))),
    pipelineStep: v.optional(v.number()),
    priority: v.optional(v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("urgent"))),
    contentType: v.optional(v.string()),
    contentSlug: v.optional(v.string()),
    contentBrief: v.optional(v.string()),
    deliverables: v.optional(v.object({
      blogPost: v.optional(v.boolean()),
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
    })),
    deliverableStatus: v.optional(v.any()),
    qualityScore: v.optional(v.number()),
    readabilityScore: v.optional(v.number()),
    revisionCount: v.optional(v.number()),
    rejectionNotes: v.optional(v.string()),
    targetKeywords: v.optional(v.array(v.string())),
    focusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    publishedUrl: v.optional(v.string()),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const task = await ctx.db.get(id);
    if (!task) throw new Error("Task not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    await ctx.db.patch(id, updates);
  },
});

// Update task status only
export const updateStatus = mutation({
  args: {
    id: v.id("tasks"),
    status: v.union(
      v.literal("backlog"),
      v.literal("researched"),
      v.literal("briefed"),
      v.literal("drafted"),
      v.literal("reviewed"),
      v.literal("revision_needed"),
      v.literal("humanized"),
      v.literal("completed"),
      v.literal("cancelled"),
      v.literal("blocked")
    ),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: args.status });
  },
});

// Assign agent to task
export const assignAgent = mutation({
  args: {
    id: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.id);
    if (!task) throw new Error("Task not found");

    const assigneeNames = task.assigneeNames.includes(args.agentName)
      ? task.assigneeNames
      : [...task.assigneeNames, args.agentName];

    await ctx.db.patch(args.id, {
      assigneeNames,
      lockedBy: args.agentName,
      lockedAt: Date.now(),
    });
  },
});

// Unassign (clear lock)
export const unassign = mutation({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      lockedBy: undefined,
      lockedAt: undefined,
    });
  },
});

// Subscribe agent to task
export const subscribe = mutation({
  args: {
    id: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.id);
    if (!task) throw new Error("Task not found");

    if (!task.subscriberNames.includes(args.agentName)) {
      await ctx.db.patch(args.id, {
        subscriberNames: [...task.subscriberNames, args.agentName],
      });
    }
  },
});

// Unsubscribe agent from task
export const unsubscribe = mutation({
  args: {
    id: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.id);
    if (!task) throw new Error("Task not found");

    await ctx.db.patch(args.id, {
      subscriberNames: task.subscriberNames.filter((n) => n !== args.agentName),
    });
  },
});
