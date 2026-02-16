import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List all agents
export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("agents").collect();
  },
});

// Get agent by id
export const get = query({
  args: { id: v.id("agents") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get agent by name
export const getByName = query({
  args: { name: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("agents")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .unique();
  },
});

// List agents that are active or idle
export const listActive = query({
  args: {},
  handler: async (ctx) => {
    const all = await ctx.db.query("agents").collect();
    return all.filter((a) => a.status === "active" || a.status === "idle");
  },
});

// Register a new agent
export const register = mutation({
  args: {
    name: v.string(),
    displayName: v.string(),
    role: v.string(),
    heartbeatCron: v.string(),
    defaultModel: v.string(),
    skillPath: v.string(),
    level: v.union(v.literal("intern"), v.literal("specialist"), v.literal("lead"), v.literal("orchestrator")),
    agentFilePath: v.string(),
    status: v.optional(v.union(v.literal("idle"), v.literal("active"), v.literal("blocked"), v.literal("offline"))),
    staticSkillIds: v.optional(v.array(v.id("skills"))),
    dynamicSkillIds: v.optional(v.array(v.id("skills"))),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("agents", {
      name: args.name,
      displayName: args.displayName,
      role: args.role,
      status: args.status ?? "idle",
      lastHeartbeat: Date.now(),
      heartbeatCron: args.heartbeatCron,
      defaultModel: args.defaultModel,
      skillPath: args.skillPath,
      level: args.level,
      stats: { tasksCompleted: 0, lastActive: Date.now() },
      staticSkillIds: args.staticSkillIds ?? [],
      dynamicSkillIds: args.dynamicSkillIds ?? [],
      agentFilePath: args.agentFilePath,
    });
  },
});

// Heartbeat: update lastHeartbeat by agent name
export const heartbeat = mutation({
  args: { name: v.string() },
  handler: async (ctx, args) => {
    const agent = await ctx.db
      .query("agents")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .unique();
    if (!agent) throw new Error(`Agent "${args.name}" not found`);

    await ctx.db.patch(agent._id, {
      lastHeartbeat: Date.now(),
      stats: { ...agent.stats, lastActive: Date.now() },
    });
  },
});

// Rename an agent
export const rename = mutation({
  args: {
    id: v.id("agents"),
    name: v.string(),
    displayName: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const patch: Record<string, any> = { name: args.name };
    if (args.displayName !== undefined) patch.displayName = args.displayName;
    await ctx.db.patch(args.id, patch);
  },
});

// Update agent default model
export const updateModel = mutation({
  args: {
    id: v.id("agents"),
    defaultModel: v.union(v.literal("haiku"), v.literal("sonnet"), v.literal("opus")),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { defaultModel: args.defaultModel });
  },
});

// Update agent status
export const updateStatus = mutation({
  args: {
    id: v.id("agents"),
    status: v.union(v.literal("idle"), v.literal("active"), v.literal("blocked"), v.literal("offline")),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: args.status });
  },
});

// Assign a task to an agent
export const assignTask = mutation({
  args: { id: v.id("agents"), taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      currentTaskId: args.taskId,
      status: "active" as const,
    });
  },
});

// Update agent paths (skillPath, agentFilePath)
export const updatePaths = mutation({
  args: {
    id: v.id("agents"),
    skillPath: v.optional(v.string()),
    agentFilePath: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const agent = await ctx.db.get(args.id);
    if (!agent) throw new Error("Agent not found");
    const patch: Record<string, any> = {};
    if (args.skillPath !== undefined) patch.skillPath = args.skillPath;
    if (args.agentFilePath !== undefined) patch.agentFilePath = args.agentFilePath;
    await ctx.db.patch(args.id, patch);
  },
});

// Update agent skill assignments
export const updateSkills = mutation({
  args: {
    id: v.id("agents"),
    staticSkillIds: v.optional(v.array(v.id("skills"))),
    dynamicSkillIds: v.optional(v.array(v.id("skills"))),
  },
  handler: async (ctx, args) => {
    const agent = await ctx.db.get(args.id);
    if (!agent) throw new Error("Agent not found");
    const patch: Record<string, any> = {};
    if (args.staticSkillIds !== undefined) patch.staticSkillIds = args.staticSkillIds;
    if (args.dynamicSkillIds !== undefined) patch.dynamicSkillIds = args.dynamicSkillIds;
    await ctx.db.patch(args.id, patch);
  },
});

// List agents with skill IDs
export const listWithSkills = query({
  args: {},
  handler: async (ctx) => {
    const agents = await ctx.db.query("agents").collect();
    return agents.map((a) => ({
      _id: a._id,
      name: a.name,
      displayName: a.displayName,
      role: a.role,
      staticSkillIds: a.staticSkillIds,
      dynamicSkillIds: a.dynamicSkillIds,
    }));
  },
});

// Complete the current task
export const completeTask = mutation({
  args: { id: v.id("agents") },
  handler: async (ctx, args) => {
    const agent = await ctx.db.get(args.id);
    if (!agent) throw new Error("Agent not found");

    await ctx.db.patch(args.id, {
      currentTaskId: undefined,
      status: "idle" as const,
      stats: {
        ...agent.stats,
        tasksCompleted: agent.stats.tasksCompleted + 1,
      },
    });
  },
});
