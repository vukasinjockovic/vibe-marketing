import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";
import { logActivity } from "./activities";

const skillConfigValidator = v.optional(v.object({
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
  }))),
  summary: v.optional(v.string()),
}));

// List content batches by project
export const list = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contentBatches")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// List content batches by channel
export const listByChannel = query({
  args: { channelId: v.id("channels") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contentBatches")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .collect();
  },
});

// Get content batch by id
export const get = query({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get content batch by slug
export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("contentBatches")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
  },
});

// Create a content batch
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    channelId: v.id("channels"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    batchSize: v.number(),
    pipelineId: v.id("pipelines"),
    pipelineSnapshot: v.optional(v.any()),
    targetFocusGroupIds: v.array(v.id("focusGroups")),
    contentThemes: v.optional(v.array(v.string())),
    trendSources: v.optional(v.array(v.string())),
    mixConfig: v.optional(v.object({
      questions: v.optional(v.number()),
      emotional: v.optional(v.number()),
      interactive: v.optional(v.number()),
      debate: v.optional(v.number()),
      textOnly: v.optional(v.number()),
    })),
    skillConfig: skillConfigValidator,
    notes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("contentBatches")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .unique();
    if (existing) {
      throw new Error(`Content batch with slug "${args.slug}" already exists`);
    }

    const id = await ctx.db.insert("contentBatches", {
      ...args,
      status: "planning",
    });
    await logActivity(ctx, {
      projectId: args.projectId,
      type: "batch_created",
      agentName: "wookashin",
      message: `Created content batch "${args.name}"`,
      contentBatchId: id,
    });
    return id;
  },
});

// Update content batch (partial)
export const update = mutation({
  args: {
    id: v.id("contentBatches"),
    name: v.optional(v.string()),
    slug: v.optional(v.string()),
    description: v.optional(v.string()),
    notes: v.optional(v.string()),
    batchSize: v.optional(v.number()),
    targetFocusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    contentThemes: v.optional(v.array(v.string())),
    trendSources: v.optional(v.array(v.string())),
    mixConfig: v.optional(v.object({
      questions: v.optional(v.number()),
      emotional: v.optional(v.number()),
      interactive: v.optional(v.number()),
      debate: v.optional(v.number()),
      textOnly: v.optional(v.number()),
    })),
    skillConfig: skillConfigValidator,
    pipelineId: v.optional(v.id("pipelines")),
    pipelineSnapshot: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const batch = await ctx.db.get(id);
    if (!batch) throw new Error("Content batch not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    await ctx.db.patch(id, updates);
  },
});

// Activate batch — snapshot pipeline, generate tasks, dispatch first agent
export const activate = mutation({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    const batch = await ctx.db.get(args.id);
    if (!batch) throw new Error("Content batch not found");

    // Snapshot pipeline if not already done
    if (!batch.pipelineSnapshot) {
      const pipeline = await ctx.db.get(batch.pipelineId);
      if (pipeline) {
        await ctx.db.patch(args.id, { pipelineSnapshot: pipeline });
      }
    }

    await ctx.db.patch(args.id, {
      status: "active" as const,
      activatedAt: Date.now(),
    });

    await logActivity(ctx, {
      projectId: batch.projectId,
      type: "batch_activated",
      agentName: "wookashin",
      message: `Activated content batch "${batch.name}"`,
      contentBatchId: args.id,
    });

    // Generate tasks (only if none exist yet)
    const existingTasks = await ctx.db
      .query("tasks")
      .withIndex("by_content_batch", (q) => q.eq("contentBatchId", args.id))
      .first();
    if (!existingTasks) {
      await ctx.scheduler.runAfter(0, internal.orchestrator.generateTasksForBatch, {
        contentBatchId: args.id,
      });
    }

    // Dispatch first task (slight delay to let tasks generate)
    await ctx.scheduler.runAfter(500, internal.orchestrator.dispatchNextBatchTask, {
      contentBatchId: args.id,
    });
  },
});

// Pause batch — running agents finish current step but no further dispatch
export const pause = mutation({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "paused" as const,
      pausedAt: Date.now(),
    });
  },
});

// Resume batch — re-dispatch any stuck tasks
export const resume = mutation({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    const batch = await ctx.db.get(args.id);
    if (!batch) throw new Error("Content batch not found");

    await ctx.db.patch(args.id, {
      status: "active" as const,
    });

    // Find tasks that are mid-pipeline with no lock
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_content_batch", (q) => q.eq("contentBatchId", args.id))
      .collect();

    for (const task of tasks) {
      if (
        task.status !== "completed" &&
        task.status !== "cancelled" &&
        task.status !== "blocked" &&
        task.status !== "backlog" &&
        !task.lockedBy
      ) {
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
    await ctx.scheduler.runAfter(100, internal.orchestrator.dispatchNextBatchTask, {
      contentBatchId: args.id,
    });
  },
});

// Complete batch
export const complete = mutation({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    const batch = await ctx.db.get(args.id);
    await ctx.db.patch(args.id, {
      status: "completed" as const,
      completedAt: Date.now(),
    });
    if (batch) {
      await logActivity(ctx, {
        projectId: batch.projectId,
        type: "batch_completed",
        agentName: "system",
        message: `Content batch "${batch.name}" completed`,
        contentBatchId: args.id,
      });
    }
  },
});

// Remove batch
export const remove = mutation({
  args: { id: v.id("contentBatches") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});
