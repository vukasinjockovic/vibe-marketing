import { mutation, query } from "./_generated/server";
import { ConvexError, v } from "convex/values";
import { internal } from "./_generated/api";

const TEN_MINUTES_MS = 10 * 60 * 1000;
const MAX_AUTO_RETRIES = 2;

/**
 * Map a pipeline step's outputDir to the corresponding task status.
 * Falls back to the current task status if no mapping exists.
 */
function outputDirToStatus(
  outputDir: string | undefined,
  currentStatus: string
): string {
  const mapping: Record<string, string> = {
    research: "researched",
    briefs: "briefed",
    drafts: "drafted",
    reviewed: "reviewed",
    final: "humanized",
  };
  if (outputDir && mapping[outputDir]) {
    return mapping[outputDir];
  }
  return currentStatus;
}

// ═══════════════════════════════════════════
// acquireLock — Attempt to lock a task for an agent
// ═══════════════════════════════════════════

export const acquireLock = mutation({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    const now = Date.now();

    // Check if locked by someone else recently (non-stale)
    if (
      task.lockedBy &&
      task.lockedBy !== args.agentName &&
      task.lockedAt &&
      now - task.lockedAt < TEN_MINUTES_MS
    ) {
      return { acquired: false, lockedBy: task.lockedBy };
    }

    // Not locked, or lock is stale, or we already hold the lock — acquire
    await ctx.db.patch(args.taskId, {
      lockedBy: args.agentName,
      lockedAt: now,
    });

    // Log activity
    const stepDesc = task.pipeline?.[task.pipelineStep]?.description || `step ${task.pipelineStep}`;
    await ctx.db.insert("activities", {
      projectId: task.projectId,
      type: "start",
      agentName: args.agentName,
      taskId: args.taskId,
      campaignId: task.campaignId,
      message: `Started working on "${stepDesc}"`,
    });

    return { acquired: true };
  },
});

// ═══════════════════════════════════════════
// releaseLock — Release a task lock (only if we own it)
// ═══════════════════════════════════════════

export const releaseLock = mutation({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    if (task.lockedBy !== args.agentName) {
      return { released: false, reason: "Lock held by different agent" };
    }

    await ctx.db.patch(args.taskId, {
      lockedBy: undefined,
      lockedAt: undefined,
    });

    return { released: true };
  },
});

// ═══════════════════════════════════════════
// completeStep — Advance task through its pipeline
// This is the ONLY way to advance a task.
// ═══════════════════════════════════════════

export const completeStep = mutation({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
    qualityScore: v.optional(v.number()),
    outputPath: v.optional(v.string()),
    resourceIds: v.array(v.id("resources")),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    // Verify the caller holds the lock
    if (task.lockedBy !== args.agentName) {
      throw new ConvexError(
        `Lock mismatch: task locked by "${task.lockedBy}", caller is "${args.agentName}"`
      );
    }

    // Verify all resourceIds exist
    if (args.resourceIds.length === 0) {
      throw new ConvexError("resourceIds is required — every step must register at least one resource");
    }
    for (const rid of args.resourceIds) {
      const r = await ctx.db.get(rid);
      if (!r) throw new ConvexError(`Resource ${rid} not found`);
    }

    const currentStepIndex = task.pipelineStep;
    const pipeline = [...task.pipeline];

    // Validate current step exists
    if (currentStepIndex < 0 || currentStepIndex >= pipeline.length) {
      throw new ConvexError(
        `Invalid pipeline step ${currentStepIndex} (pipeline has ${pipeline.length} steps)`
      );
    }

    // Mark current step as completed
    pipeline[currentStepIndex] = {
      ...pipeline[currentStepIndex],
      status: "completed",
    };

    const nextStepIndex = currentStepIndex + 1;
    const hasNextStep = nextStepIndex < pipeline.length;

    let newStatus: string;

    if (hasNextStep) {
      // Mark next step as in_progress
      pipeline[nextStepIndex] = {
        ...pipeline[nextStepIndex],
        status: "in_progress",
      };

      // Derive task status from the completed step's outputDir
      newStatus = outputDirToStatus(
        pipeline[currentStepIndex].outputDir,
        task.status
      );
    } else {
      // No more steps — task is completed
      newStatus = "completed";
    }

    // Build the patch
    const patch: Record<string, unknown> = {
      pipeline,
      pipelineStep: hasNextStep ? nextStepIndex : currentStepIndex,
      status: newStatus,
      lockedBy: undefined,
      lockedAt: undefined,
      stepRetryCount: 0, // Reset retry count on successful step completion
    };

    if (args.qualityScore !== undefined) {
      patch.qualityScore = args.qualityScore;
    }

    // Update resourceProgress.completedCounts from actual resources
    if (task.campaignId || task.contentBatchId) {
      const taskResources = await ctx.db
        .query("resources")
        .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
        .collect();
      const completedCounts: Record<string, number> = {};
      for (const r of taskResources) {
        completedCounts[r.resourceType] = (completedCounts[r.resourceType] || 0) + 1;
      }
      const existing = task.resourceProgress ?? {};
      patch.resourceProgress = {
        ...existing,
        completedCounts,
        lastUpdated: Date.now(),
      };
    }

    await ctx.db.patch(args.taskId, patch);

    // ── Log activity + notification ──

    const completedStepDesc = pipeline[currentStepIndex].description || `step ${currentStepIndex + 1}`;
    const taskTitle = task.title || "Untitled task";

    if (hasNextStep) {
      const nextStepDesc = pipeline[nextStepIndex].description || `step ${nextStepIndex + 1}`;
      const nextAgent = pipeline[nextStepIndex].agent || "unknown";
      // Activity: step advanced
      await ctx.db.insert("activities", {
        projectId: task.projectId,
        type: "progress",
        agentName: args.agentName,
        taskId: args.taskId,
        campaignId: task.campaignId,
        message: `Completed "${completedStepDesc}", advancing to "${nextStepDesc}"`,
        metadata: args.qualityScore !== undefined ? { qualityScore: args.qualityScore } : undefined,
      });

      // TODO:NOTIFICATION_PREFERENCES — Step transition notification
      const stepMsg = `${args.agentName} finished "${completedStepDesc}" → ${nextAgent} starting "${nextStepDesc}" (${taskTitle})`;
      await ctx.db.insert("notifications", {
        mentionedAgent: "@human",
        fromAgent: args.agentName,
        taskId: args.taskId,
        content: stepMsg,
        delivered: false,
      });
      await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
        message: `🔄 ${stepMsg}`,
      });
    } else {
      // Activity: task completed
      await ctx.db.insert("activities", {
        projectId: task.projectId,
        type: "complete",
        agentName: args.agentName,
        taskId: args.taskId,
        campaignId: task.campaignId,
        message: `Task "${taskTitle}" completed all pipeline steps`,
        metadata: args.qualityScore !== undefined ? { qualityScore: args.qualityScore } : undefined,
      });

      // TODO:NOTIFICATION_PREFERENCES — Task completion notification
      const doneMsg = `Task completed: ${taskTitle}`;
      await ctx.db.insert("notifications", {
        mentionedAgent: "@human",
        fromAgent: args.agentName,
        taskId: args.taskId,
        content: doneMsg,
        delivered: false,
      });
      await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
        message: `✅ ${doneMsg}`,
      });
    }

    // ── Auto-dispatch next agent or handle branches ──

    if (hasNextStep) {
      // Check if campaign or content batch is paused — skip dispatch if so
      let parentPaused = false;
      if (task.campaignId) {
        const campaign = await ctx.db.get(task.campaignId);
        if (campaign && campaign.status === "paused") {
          parentPaused = true;
        }
      }
      if (!parentPaused && task.contentBatchId) {
        const batch = await ctx.db.get(task.contentBatchId);
        if (batch && batch.status === "paused") {
          parentPaused = true;
        }
      }

      if (!parentPaused) {
        // Check for parallel branches triggered after the completed step
        let branchesDispatched = false;
        let convergenceStep: number | undefined;

        if (task.campaignId) {
          const campaign = await ctx.db.get(task.campaignId);
          const snapshot = campaign?.pipelineSnapshot as any;
          convergenceStep = snapshot?.convergenceStep;
          const parallelBranches = snapshot?.parallelBranches as any[] | undefined;

          if (parallelBranches?.length) {
            const completedStepOrder = pipeline[currentStepIndex].step;
            const triggered = parallelBranches.filter(
              (b: any) => b.triggerAfterStep === completedStepOrder
            );

            if (triggered.length > 0) {
              branchesDispatched = true;

              // Set pendingBranches on task
              const branchLabels = triggered.map((b: any) => b.label);
              await ctx.db.patch(args.taskId, { pendingBranches: branchLabels });

              // Group branches by model for efficient dispatch
              const byModel: Record<string, { label: string; agent: string }[]> = {};
              for (const b of triggered) {
                const model = b.model || "sonnet";
                if (!byModel[model]) byModel[model] = [];
                byModel[model].push({ label: b.label, agent: b.agent });
              }

              for (const [model, branches] of Object.entries(byModel)) {
                await ctx.scheduler.runAfter(
                  0,
                  internal.orchestrator.requestBranchDispatch,
                  { taskId: args.taskId, branches, model }
                );
              }
            }
          }
        }

        // Content batch parallel branch dispatch
        if (task.contentBatchId && !branchesDispatched) {
          const batch = await ctx.db.get(task.contentBatchId);
          const snapshot = batch?.pipelineSnapshot as any;
          convergenceStep = snapshot?.convergenceStep;
          const parallelBranches = snapshot?.parallelBranches as any[] | undefined;

          if (parallelBranches?.length) {
            const completedStepOrder = pipeline[currentStepIndex].step;
            const triggered = parallelBranches.filter(
              (b: any) => b.triggerAfterStep === completedStepOrder
            );

            if (triggered.length > 0) {
              branchesDispatched = true;

              const branchLabels = triggered.map((b: any) => b.label);
              await ctx.db.patch(args.taskId, { pendingBranches: branchLabels });

              const byModel: Record<string, { label: string; agent: string }[]> = {};
              for (const b of triggered) {
                const model = b.model || "sonnet";
                if (!byModel[model]) byModel[model] = [];
                byModel[model].push({ label: b.label, agent: b.agent });
              }

              for (const [model, branches] of Object.entries(byModel)) {
                await ctx.scheduler.runAfter(
                  0,
                  internal.orchestrator.requestBranchDispatch,
                  { taskId: args.taskId, branches, model }
                );
              }
            }
          }
        }

        // Dispatch next main step — unless convergence gate blocks it
        const nextStepOrder = pipeline[nextStepIndex].step;
        const hasPendingBranches = branchesDispatched || ((task.pendingBranches?.length ?? 0) > 0);
        const blockedByConvergence = convergenceStep !== undefined
          && nextStepOrder >= convergenceStep
          && hasPendingBranches;

        if (!blockedByConvergence) {
          const nextAgent = pipeline[nextStepIndex].agent;
          if (nextAgent) {
            await ctx.scheduler.runAfter(
              0,
              internal.orchestrator.requestDispatch,
              { taskId: args.taskId, agentName: nextAgent }
            );
          }
        }
      }
    } else {
      // Task completed — dispatch next task + check completion for campaign or batch
      if (task.campaignId) {
        await ctx.scheduler.runAfter(
          0,
          internal.orchestrator.dispatchNextTask,
          { campaignId: task.campaignId }
        );
        await ctx.scheduler.runAfter(
          100,
          internal.orchestrator.checkCampaignCompletion,
          { campaignId: task.campaignId }
        );
      }
      if (task.contentBatchId) {
        await ctx.scheduler.runAfter(
          0,
          internal.orchestrator.dispatchNextBatchTask,
          { contentBatchId: task.contentBatchId }
        );
        await ctx.scheduler.runAfter(
          100,
          internal.orchestrator.checkBatchCompletion,
          { contentBatchId: task.contentBatchId }
        );
      }
    }

    return {
      completed: true,
      nextStep: hasNextStep ? nextStepIndex : null,
      newStatus,
    };
  },
});

// ═══════════════════════════════════════════
// completeBranch — Mark a parallel branch as done
// ═══════════════════════════════════════════

export const completeBranch = mutation({
  args: {
    taskId: v.id("tasks"),
    branchLabel: v.string(),
    agentName: v.string(),
    resourceIds: v.array(v.id("resources")),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    // Verify all resourceIds exist
    if (args.resourceIds.length === 0) {
      throw new ConvexError("resourceIds is required — every branch must register at least one resource");
    }
    for (const rid of args.resourceIds) {
      const r = await ctx.db.get(rid);
      if (!r) throw new ConvexError(`Resource ${rid} not found`);
    }

    const pending = (task.pendingBranches || []).filter(
      (label) => label !== args.branchLabel
    );

    await ctx.db.patch(args.taskId, { pendingBranches: pending });

    // Log activity for branch completion
    await ctx.db.insert("activities", {
      projectId: task.projectId,
      type: "progress",
      agentName: args.agentName,
      taskId: args.taskId,
      campaignId: task.campaignId,
      message: `Branch "${args.branchLabel}" completed (${pending.length} remaining)`,
    });

    if (pending.length === 0) {
      // All branches done — dispatch the gated step or advance
      const currentStep = task.pipelineStep;
      const pipeline = [...task.pipeline];
      const currentStepData = pipeline[currentStep];

      // Check campaign/batch pause gate
      let parentPaused = false;
      if (task.campaignId) {
        const campaign = await ctx.db.get(task.campaignId);
        if (campaign && campaign.status === "paused") {
          parentPaused = true;
        }
      }
      if (!parentPaused && task.contentBatchId) {
        const batch = await ctx.db.get(task.contentBatchId);
        if (batch && batch.status === "paused") {
          parentPaused = true;
        }
      }

      if (!parentPaused) {
        if (currentStepData.status === "in_progress" && currentStepData.agent) {
          // Convergence gate held this step — dispatch it now
          await ctx.scheduler.runAfter(
            0,
            internal.orchestrator.requestDispatch,
            { taskId: args.taskId, agentName: currentStepData.agent }
          );
        } else {
          // Current step already ran — dispatch next step
          const nextStepIndex = currentStep + 1;
          if (nextStepIndex < pipeline.length) {
            const nextAgent = pipeline[nextStepIndex].agent;
            if (nextAgent) {
              await ctx.scheduler.runAfter(
                0,
                internal.orchestrator.requestDispatch,
                { taskId: args.taskId, agentName: nextAgent }
              );
            }
          }
        }
      }
    }

    return { remaining: pending.length };
  },
});

// ═══════════════════════════════════════════
// requestRevision — Send task back to an earlier step
// ═══════════════════════════════════════════

export const requestRevision = mutation({
  args: {
    taskId: v.id("tasks"),
    notes: v.string(),
    targetStep: v.number(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    const pipeline = [...task.pipeline];

    if (args.targetStep < 0 || args.targetStep >= pipeline.length) {
      throw new ConvexError(
        `Invalid target step ${args.targetStep} (pipeline has ${pipeline.length} steps)`
      );
    }

    // Reset all steps from targetStep onward to "pending"
    for (let i = args.targetStep; i < pipeline.length; i++) {
      pipeline[i] = { ...pipeline[i], status: "pending" };
    }

    await ctx.db.patch(args.taskId, {
      status: "revision_needed",
      pipelineStep: args.targetStep,
      pipeline,
      rejectionNotes: args.notes,
      revisionCount: (task.revisionCount ?? 0) + 1,
    });

    return { revised: true };
  },
});

// ═══════════════════════════════════════════
// retryStep — Re-attempt current pipeline step with retry count safeguard
// ═══════════════════════════════════════════

export const retryStep = mutation({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    const retryCount = (task.stepRetryCount ?? 0) + 1;

    if (retryCount > MAX_AUTO_RETRIES) {
      // Stop retrying — leave task blocked, notify human
      await ctx.db.patch(args.taskId, {
        status: "blocked",
        stepRetryCount: retryCount,
        rejectionNotes: `Auto-retry limit reached (${MAX_AUTO_RETRIES} retries). Manual intervention required.`,
        lockedBy: undefined,
        lockedAt: undefined,
      });

      const blockMsg = `Task "${task.title}" blocked after ${MAX_AUTO_RETRIES} auto-retries at step ${task.pipelineStep}`;
      await ctx.db.insert("notifications", {
        mentionedAgent: "@human",
        fromAgent: args.agentName,
        taskId: args.taskId,
        content: blockMsg,
        delivered: false,
      });
      await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
        message: `🚫 ${blockMsg}`,
      });

      return { retried: false, reason: "max_retries_exceeded", retryCount };
    }

    // Reset current step to pending and unlock
    const pipeline = [...task.pipeline];
    pipeline[task.pipelineStep] = {
      ...pipeline[task.pipelineStep],
      status: "in_progress",
    };

    await ctx.db.patch(args.taskId, {
      pipeline,
      stepRetryCount: retryCount,
      lockedBy: undefined,
      lockedAt: undefined,
    });

    // Re-dispatch the agent for the current step
    const currentAgent = pipeline[task.pipelineStep].agent;
    if (currentAgent) {
      await ctx.scheduler.runAfter(0, internal.orchestrator.requestDispatch, {
        taskId: args.taskId,
        agentName: currentAgent,
      });
    }

    await ctx.db.insert("activities", {
      projectId: task.projectId,
      type: "retry",
      agentName: args.agentName,
      taskId: args.taskId,
      campaignId: task.campaignId,
      message: `Auto-retry #${retryCount} for step ${task.pipelineStep}`,
    });

    return { retried: true, retryCount };
  },
});

// ═══════════════════════════════════════════
// getTaskPipelineStatus — Full pipeline view for a task
// ═══════════════════════════════════════════

export const getTaskPipelineStatus = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) throw new ConvexError("Task not found");

    return {
      _id: task._id,
      title: task.title,
      status: task.status,
      pipelineStep: task.pipelineStep,
      pipeline: task.pipeline,
      lockedBy: task.lockedBy,
      lockedAt: task.lockedAt,
      qualityScore: task.qualityScore,
      revisionCount: task.revisionCount,
      rejectionNotes: task.rejectionNotes,
    };
  },
});

// ═══════════════════════════════════════════
// listReadyTasks — Tasks available for agents to pick up
// ═══════════════════════════════════════════

export const listReadyTasks = query({
  args: { projectId: v.optional(v.id("projects")) },
  handler: async (ctx, args) => {
    const now = Date.now();

    let tasks;
    if (args.projectId) {
      tasks = await ctx.db
        .query("tasks")
        .withIndex("by_project", (q) => q.eq("projectId", args.projectId!))
        .collect();
    } else {
      tasks = await ctx.db.query("tasks").collect();
    }

    // Filter: not completed/cancelled/blocked, and not actively locked
    return tasks.filter((task) => {
      // Exclude terminal / blocked statuses
      if (["completed", "cancelled", "blocked"].includes(task.status)) {
        return false;
      }

      // Exclude actively locked tasks (non-stale)
      if (
        task.lockedBy &&
        task.lockedAt &&
        now - task.lockedAt < TEN_MINUTES_MS
      ) {
        return false;
      }

      return true;
    });
  },
});
