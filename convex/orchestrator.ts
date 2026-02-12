import { internalAction, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

const DISPATCHER_URL = "http://172.19.0.1:3212";

// ═══════════════════════════════════════════
// sendTelegram — Push notification to Telegram
// TODO:NOTIFICATION_PREFERENCES — Move to a notification dispatcher that checks
// per-user, per-channel, per-notification-type preferences before sending.
// Currently hardcoded: ALL notifications → Telegram + in-app.
// ═══════════════════════════════════════════

export const sendTelegram = internalAction({
  args: { message: v.string() },
  handler: async (_ctx, args) => {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;

    if (!token || !chatId) {
      console.warn("Telegram not configured — skipping notification");
      return;
    }

    try {
      const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: args.message,
          parse_mode: "Markdown",
        }),
      });

      if (!res.ok) {
        const body = await res.text();
        console.error(`Telegram send failed (${res.status}): ${body}`);
      }
    } catch (err: any) {
      console.error(`Telegram network error: ${err.message}`);
    }
  },
});

// ═══════════════════════════════════════════
// generateTasksForCampaign — Create pipeline tasks from campaign config
// ═══════════════════════════════════════════

export const generateTasksForCampaign = internalMutation({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) throw new Error("Campaign not found");

    const articleCount = campaign.targetArticleCount || 5;
    const snapshot = campaign.pipelineSnapshot as any;
    if (!snapshot?.mainSteps?.length) {
      throw new Error("Campaign has no pipeline snapshot with steps");
    }

    const taskIds: string[] = [];

    for (let i = 0; i < articleCount; i++) {
      const pipeline = snapshot.mainSteps.map((s: any, idx: number) => ({
        step: s.order ?? idx,
        status: "pending",
        agent: s.agent,
        model: s.model,
        description: s.label || s.description || `Step ${idx + 1}`,
        outputDir: s.outputDir,
      }));

      // First task's first step starts as in_progress, rest stay pending
      if (i === 0 && pipeline.length > 0) {
        pipeline[0].status = "in_progress";
      }

      const taskId = await ctx.db.insert("tasks", {
        projectId: campaign.projectId,
        title: `${campaign.name} — Article ${i + 1}`,
        description: `Auto-generated task for campaign "${campaign.name}", article ${i + 1} of ${articleCount}.`,
        campaignId: args.campaignId,
        pipeline,
        pipelineStep: 0,
        status: i === 0 ? "backlog" : "backlog",
        priority: "medium",
        createdBy: "orchestrator",
        assigneeNames: [],
        subscriberNames: [],
        focusGroupIds: campaign.targetFocusGroupIds,
        deliverables: campaign.deliverableConfig as any,
        targetKeywords: campaign.seedKeywords,
      });

      taskIds.push(taskId);
    }

    // Log activity + notify
    await ctx.db.insert("activities", {
      projectId: campaign.projectId,
      type: "info",
      agentName: "vibe-orchestrator",
      campaignId: args.campaignId,
      message: `Generated ${taskIds.length} tasks for campaign "${campaign.name}"`,
    });

    // TODO:NOTIFICATION_PREFERENCES — Campaign activation notification
    const activateMsg = `Campaign "${campaign.name}" activated — ${taskIds.length} tasks created`;
    await ctx.db.insert("notifications", {
      mentionedAgent: "@human",
      fromAgent: "vibe-orchestrator",
      content: activateMsg,
      delivered: false,
    });
    await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
      message: `🚀 ${activateMsg}`,
    });

    return taskIds;
  },
});

// ═══════════════════════════════════════════
// requestDispatch — HTTP POST to host dispatcher to invoke an agent
// ═══════════════════════════════════════════

export const requestDispatch = internalAction({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
  },
  handler: async (ctx, args) => {
    try {
      const res = await fetch(`${DISPATCHER_URL}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ taskId: args.taskId, agentName: args.agentName }),
      });

      if (!res.ok) {
        const body = await res.text();
        console.error(`Dispatch failed (${res.status}): ${body}`);
        // Block the task so it's visible in dashboard
        await ctx.runMutation(internal.orchestrator.blockTask, {
          taskId: args.taskId,
          reason: `Dispatcher error: ${res.status} ${body}`,
        });
      }
    } catch (err: any) {
      console.error(`Dispatch network error: ${err.message}`);
      await ctx.runMutation(internal.orchestrator.blockTask, {
        taskId: args.taskId,
        reason: `Dispatcher unreachable: ${err.message}`,
      });
    }
  },
});

// ═══════════════════════════════════════════
// requestBranchDispatch — Dispatch parallel branch agents grouped by model
// ═══════════════════════════════════════════

export const requestBranchDispatch = internalAction({
  args: {
    taskId: v.id("tasks"),
    branches: v.array(v.object({
      label: v.string(),
      agent: v.string(),
    })),
    model: v.string(),
  },
  handler: async (ctx, args) => {
    try {
      const res = await fetch(`${DISPATCHER_URL}/dispatch-branch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          taskId: args.taskId,
          branches: args.branches,
          model: args.model,
        }),
      });

      if (!res.ok) {
        const body = await res.text();
        console.error(`Branch dispatch failed (${res.status}): ${body}`);
      }
    } catch (err: any) {
      console.error(`Branch dispatch network error: ${err.message}`);
    }
  },
});

// ═══════════════════════════════════════════
// dispatchNextTask — Find next pending task for campaign and dispatch it
// ═══════════════════════════════════════════

export const dispatchNextTask = internalMutation({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign || campaign.status !== "active") return;

    // Find all tasks for this campaign
    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();

    // Check if any task is currently in-progress (pipeline running)
    const hasRunning = tasks.some((t) =>
      t.status !== "backlog" && t.status !== "completed" && t.status !== "cancelled" && t.status !== "blocked"
    );

    if (hasRunning) return; // Wait for current task to finish

    // Find first backlog task
    const nextTask = tasks.find((t) => t.status === "backlog");
    if (!nextTask) return; // All tasks started

    // Set first step to in_progress
    const pipeline = [...nextTask.pipeline];
    if (pipeline.length > 0) {
      pipeline[0] = { ...pipeline[0], status: "in_progress" };
    }

    await ctx.db.patch(nextTask._id, { pipeline });

    // Get the agent for the first step
    const firstAgent = pipeline[0]?.agent;
    if (firstAgent) {
      await ctx.scheduler.runAfter(0, internal.orchestrator.requestDispatch, {
        taskId: nextTask._id,
        agentName: firstAgent,
      });
    }
  },
});

// ═══════════════════════════════════════════
// checkCampaignCompletion — Complete campaign if all tasks done
// ═══════════════════════════════════════════

export const checkCampaignCompletion = internalMutation({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) return;
    if (campaign.status === "completed") return;

    const tasks = await ctx.db
      .query("tasks")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .collect();

    if (tasks.length === 0) return;

    const allDone = tasks.every((t) => t.status === "completed" || t.status === "cancelled");
    if (!allDone) return;

    await ctx.db.patch(args.campaignId, {
      status: "completed",
      completedAt: Date.now(),
    });

    // TODO:NOTIFICATION_PREFERENCES — Campaign completion notification
    const completeMsg = `Campaign "${campaign.name}" completed — all ${tasks.length} tasks done`;
    await ctx.db.insert("notifications", {
      mentionedAgent: "@human",
      fromAgent: "vibe-orchestrator",
      content: completeMsg,
      delivered: false,
    });
    await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
      message: `✅ ${completeMsg}`,
    });

    // Log activity
    await ctx.db.insert("activities", {
      projectId: campaign.projectId,
      type: "complete",
      agentName: "vibe-orchestrator",
      campaignId: args.campaignId,
      message: `Campaign "${campaign.name}" completed (${tasks.length} tasks)`,
    });
  },
});

// ═══════════════════════════════════════════
// blockTask — Mark a task as blocked with notes
// ═══════════════════════════════════════════

export const blockTask = internalMutation({
  args: {
    taskId: v.id("tasks"),
    reason: v.string(),
  },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    await ctx.db.patch(args.taskId, {
      status: "blocked",
      rejectionNotes: args.reason,
      lockedBy: undefined,
      lockedAt: undefined,
    });

    // TODO:NOTIFICATION_PREFERENCES — Task blocked notification
    const blockMsg = `Task blocked: ${args.reason}`;
    await ctx.db.insert("notifications", {
      mentionedAgent: "@human",
      fromAgent: "vibe-orchestrator",
      taskId: args.taskId,
      content: blockMsg,
      delivered: false,
    });
    await ctx.scheduler.runAfter(0, internal.orchestrator.sendTelegram, {
      message: `🚫 ${blockMsg}`,
    });

    // Log activity
    await ctx.db.insert("activities", {
      projectId: task?.projectId,
      type: "error",
      agentName: "vibe-orchestrator",
      taskId: args.taskId,
      campaignId: task?.campaignId,
      message: blockMsg,
    });
  },
});
