import { query } from "./_generated/server";

// Global dashboard stats — aggregates all key metrics in one reactive query
export const globalStats = query({
  args: {},
  handler: async (ctx) => {
    // Projects
    const projects = await ctx.db
      .query("projects")
      .withIndex("by_status", (q) => q.eq("status", "active"))
      .collect();

    // Campaigns
    const allCampaigns = await ctx.db.query("campaigns").collect();
    const activeCampaigns = allCampaigns.filter((c) => c.status === "active");

    // Tasks — count by status
    const allTasks = await ctx.db.query("tasks").collect();
    const tasksByStatus: Record<string, number> = {};
    for (const t of allTasks) {
      tasksByStatus[t.status] = (tasksByStatus[t.status] || 0) + 1;
    }

    // Agents
    const agents = await ctx.db.query("agents").collect();
    const activeAgents = agents.filter(
      (a) => a.status === "active" || a.status === "idle",
    );

    // Services
    const services = await ctx.db.query("services").collect();
    const activeServices = services.filter((s) => s.isActive);
    const degradedServices = services.filter(
      (s) =>
        s.isActive &&
        (s.lastHealthStatus === "degraded" ||
          s.lastHealthStatus === "unreachable"),
    );

    // Resources
    const resources = await ctx.db.query("resources").collect();
    const resourcesByType: Record<string, number> = {};
    for (const r of resources) {
      resourcesByType[r.resourceType] = (resourcesByType[r.resourceType] || 0) + 1;
    }

    // Pipelines
    const pipelines = await ctx.db.query("pipelines").collect();

    // Content batches
    const batches = await ctx.db.query("contentBatches").collect();

    // Focus groups
    const focusGroups = await ctx.db.query("focusGroups").collect();

    return {
      projects: {
        total: projects.length,
        list: projects.map((p) => ({
          _id: p._id,
          name: p.name,
          slug: p.slug,
          color: p.appearance?.color || "#6366f1",
          icon: p.appearance?.icon || null,
          stats: p.stats || {},
        })),
      },
      campaigns: {
        total: allCampaigns.length,
        active: activeCampaigns.length,
        recent: activeCampaigns
          .sort((a, b) => (b._creationTime || 0) - (a._creationTime || 0))
          .slice(0, 5)
          .map((c) => ({
            _id: c._id,
            name: c.name,
            slug: c.slug,
            status: c.status,
            projectId: c.projectId,
            _creationTime: c._creationTime,
          })),
      },
      tasks: {
        total: allTasks.length,
        byStatus: tasksByStatus,
        completed: tasksByStatus["completed"] || 0,
        inProgress:
          (tasksByStatus["drafted"] || 0) +
          (tasksByStatus["reviewed"] || 0) +
          (tasksByStatus["briefed"] || 0) +
          (tasksByStatus["researched"] || 0) +
          (tasksByStatus["humanized"] || 0),
        blocked: tasksByStatus["blocked"] || 0,
        backlog: tasksByStatus["backlog"] || 0,
      },
      agents: {
        total: agents.length,
        active: activeAgents.length,
      },
      services: {
        total: services.length,
        active: activeServices.length,
        degraded: degradedServices.length,
      },
      resources: {
        total: resources.length,
        byType: resourcesByType,
      },
      pipelines: {
        total: pipelines.length,
      },
      contentBatches: {
        total: batches.length,
      },
      focusGroups: {
        total: focusGroups.length,
      },
    };
  },
});
