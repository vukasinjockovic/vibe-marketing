import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { ConvexError } from "convex/values";

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

// ═══════════════════════════════════════════
// CHAIN RESOLUTION
// ═══════════════════════════════════════════

// Return ALL active services for a category, sorted by priority
export const resolveChain = query({
  args: { categoryName: v.string() },
  handler: async (ctx, args) => {
    const category = await ctx.db
      .query("serviceCategories")
      .withIndex("by_name", (q) => q.eq("name", args.categoryName))
      .unique();
    if (!category) return [];

    const services = await ctx.db
      .query("services")
      .withIndex("by_category_priority", (q) => q.eq("categoryId", category._id))
      .collect();

    return services
      .filter((s) => s.isActive)
      .sort((a, b) => a.priority - b.priority);
  },
});

// Chain with campaign/batch overrides applied
export const resolveChainWithOverrides = query({
  args: {
    categoryName: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
  },
  handler: async (ctx, args) => {
    const category = await ctx.db
      .query("serviceCategories")
      .withIndex("by_name", (q) => q.eq("name", args.categoryName))
      .unique();
    if (!category) return [];

    // Check for batch-level override first, then campaign-level
    let override = null;
    if (args.contentBatchId) {
      override = await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_batch_category", (q) =>
          q.eq("contentBatchId", args.contentBatchId).eq("categoryId", category._id))
        .first();
    }
    if (!override && args.campaignId) {
      override = await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_campaign_category", (q) =>
          q.eq("campaignId", args.campaignId).eq("categoryId", category._id))
        .first();
    }

    if (override) {
      // Return services in the override's order
      const chain = [];
      for (const serviceId of override.serviceChain) {
        const svc = await ctx.db.get(serviceId);
        if (svc && svc.isActive) chain.push(svc);
      }
      return chain;
    }

    // Fall back to global priority order
    const services = await ctx.db
      .query("services")
      .withIndex("by_category_priority", (q) => q.eq("categoryId", category._id))
      .collect();

    return services
      .filter((s) => s.isActive)
      .sort((a, b) => a.priority - b.priority);
  },
});

// ═══════════════════════════════════════════
// PRIORITY MANAGEMENT
// ═══════════════════════════════════════════

// Batch priority update from drag-and-drop
export const reorderServices = mutation({
  args: {
    categoryId: v.id("serviceCategories"),
    serviceIds: v.array(v.id("services")),
  },
  handler: async (ctx, args) => {
    for (let i = 0; i < args.serviceIds.length; i++) {
      const svc = await ctx.db.get(args.serviceIds[i]);
      if (!svc) throw new ConvexError(`Service not found: ${args.serviceIds[i]}`);
      if (svc.categoryId !== args.categoryId) {
        throw new ConvexError(`Service ${svc.name} does not belong to this category`);
      }
      await ctx.db.patch(args.serviceIds[i], { priority: i + 1 });
    }
  },
});

// ═══════════════════════════════════════════
// AGENT SERVICE STATUS
// ═══════════════════════════════════════════

// Returns agent's dependency status: enabled/degraded/disabled
export const getAgentServiceStatus = query({
  args: { agentName: v.string() },
  handler: async (ctx, args) => {
    const deps = await ctx.db
      .query("agentServiceDeps")
      .withIndex("by_agent", (q) => q.eq("agentName", args.agentName))
      .collect();

    if (deps.length === 0) return { status: "enabled" as const, capabilities: [] };

    const capabilities = [];
    let hasRequired = false;
    let requiredMissing = false;
    let optionalMissing = false;

    for (const dep of deps) {
      const category = await ctx.db
        .query("serviceCategories")
        .withIndex("by_name", (q) => q.eq("name", dep.capability))
        .unique();

      let activeCount = 0;
      let providers: string[] = [];
      if (category) {
        const services = await ctx.db
          .query("services")
          .withIndex("by_category", (q) => q.eq("categoryId", category._id))
          .collect();
        const active = services.filter((s) => s.isActive);
        activeCount = active.length;
        providers = active.sort((a, b) => a.priority - b.priority).map((s) => s.displayName);
      }

      capabilities.push({
        capability: dep.capability,
        required: dep.required,
        activeCount,
        providers,
      });

      if (dep.required) {
        hasRequired = true;
        if (activeCount === 0) requiredMissing = true;
      } else {
        if (activeCount === 0) optionalMissing = true;
      }
    }

    const status = requiredMissing ? "disabled" : (optionalMissing ? "degraded" : "enabled");
    return { status: status as "enabled" | "degraded" | "disabled", capabilities };
  },
});

// Pre-flight check for a campaign — all pipeline agents' service status
export const getCampaignServiceHealth = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) throw new ConvexError("Campaign not found");

    // Get all agent deps
    const allDeps = await ctx.db.query("agentServiceDeps").collect();
    const agentNames = [...new Set(allDeps.map((d) => d.agentName))];

    const agents = [];
    let overallStatus: "ready" | "degraded" | "blocked" = "ready";

    for (const agentName of agentNames) {
      const deps = allDeps.filter((d) => d.agentName === agentName);
      const capabilities = [];
      let agentStatus: "enabled" | "degraded" | "disabled" = "enabled";

      for (const dep of deps) {
        const category = await ctx.db
          .query("serviceCategories")
          .withIndex("by_name", (q) => q.eq("name", dep.capability))
          .unique();

        let activeCount = 0;
        let providers: string[] = [];
        if (category) {
          // Check for campaign-level override
          const override = await ctx.db
            .query("serviceChainOverrides")
            .withIndex("by_campaign_category", (q) =>
              q.eq("campaignId", args.campaignId).eq("categoryId", category._id))
            .first();

          if (override) {
            for (const sid of override.serviceChain) {
              const s = await ctx.db.get(sid);
              if (s && s.isActive) {
                activeCount++;
                providers.push(s.displayName);
              }
            }
          } else {
            const services = await ctx.db
              .query("services")
              .withIndex("by_category", (q) => q.eq("categoryId", category._id))
              .collect();
            const active = services.filter((s) => s.isActive);
            activeCount = active.length;
            providers = active.sort((a, b) => a.priority - b.priority).map((s) => s.displayName);
          }
        }

        capabilities.push({
          capability: dep.capability,
          required: dep.required,
          activeCount,
          providers,
        });

        if (dep.required && activeCount === 0) agentStatus = "disabled";
        else if (activeCount === 0 && agentStatus !== "disabled") agentStatus = "degraded";
      }

      agents.push({ agentName, status: agentStatus, capabilities });

      if (agentStatus === "disabled") overallStatus = "blocked";
      else if (agentStatus === "degraded" && overallStatus !== "blocked") overallStatus = "degraded";
    }

    return { overallStatus, agents };
  },
});

// ═══════════════════════════════════════════
// CHAIN OVERRIDES (campaign/batch level)
// ═══════════════════════════════════════════

export const setChainOverride = mutation({
  args: {
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
    categoryId: v.id("serviceCategories"),
    serviceChain: v.array(v.id("services")),
    setBy: v.string(),
  },
  handler: async (ctx, args) => {
    // Find existing override
    let existing = null;
    if (args.contentBatchId) {
      existing = await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_batch_category", (q) =>
          q.eq("contentBatchId", args.contentBatchId).eq("categoryId", args.categoryId))
        .first();
    } else if (args.campaignId) {
      existing = await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_campaign_category", (q) =>
          q.eq("campaignId", args.campaignId).eq("categoryId", args.categoryId))
        .first();
    }

    if (existing) {
      await ctx.db.patch(existing._id, {
        serviceChain: args.serviceChain,
        setBy: args.setBy,
        setAt: Date.now(),
      });
      return existing._id;
    }

    return await ctx.db.insert("serviceChainOverrides", {
      campaignId: args.campaignId,
      contentBatchId: args.contentBatchId,
      categoryId: args.categoryId,
      serviceChain: args.serviceChain,
      setBy: args.setBy,
      setAt: Date.now(),
    });
  },
});

export const removeChainOverride = mutation({
  args: { id: v.id("serviceChainOverrides") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

export const listChainOverrides = query({
  args: {
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
  },
  handler: async (ctx, args) => {
    if (args.contentBatchId) {
      return await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_content_batch", (q) => q.eq("contentBatchId", args.contentBatchId))
        .collect();
    }
    if (args.campaignId) {
      return await ctx.db
        .query("serviceChainOverrides")
        .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
        .collect();
    }
    return [];
  },
});

// ═══════════════════════════════════════════
// EXECUTION LOGGING
// ═══════════════════════════════════════════

export const logServiceExecution = mutation({
  args: {
    serviceId: v.id("services"),
    categoryName: v.string(),
    agentName: v.string(),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
    status: v.union(v.literal("success"), v.literal("failed"),
      v.literal("timeout"), v.literal("rate_limited")),
    durationMs: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
    retryAttempt: v.number(),
    estimatedCost: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("serviceExecutionLog", {
      ...args,
      executedAt: Date.now(),
    });

    // Update service health fields
    const updates: Record<string, unknown> = {
      lastHealthCheck: Date.now(),
    };
    if (args.status === "success") {
      updates.lastHealthStatus = "healthy";
      updates.lastSuccessAt = Date.now();
      updates.failureCount = 0;
    } else {
      const svc = await ctx.db.get(args.serviceId);
      const newCount = (svc?.failureCount ?? 0) + 1;
      updates.failureCount = newCount;
      updates.lastFailureAt = Date.now();
      updates.lastHealthStatus = newCount >= 3 ? "unreachable" : "degraded";
    }
    await ctx.db.patch(args.serviceId, updates);
  },
});

// ═══════════════════════════════════════════
// MANIFEST SYNC (used by sync_services.py)
// ═══════════════════════════════════════════

export const upsertFromManifest = mutation({
  args: {
    categoryName: v.string(),
    name: v.string(),
    displayName: v.string(),
    description: v.string(),
    scriptPath: v.string(),
    mcpServer: v.optional(v.string()),
    apiKeyEnvVar: v.string(),
    costInfo: v.string(),
    useCases: v.array(v.string()),
    docsUrl: v.optional(v.string()),
    defaultPriority: v.number(),
    manifestVersion: v.optional(v.string()),
    integrationType: v.optional(v.union(
      v.literal("script"), v.literal("mcp"),
      v.literal("both"), v.literal("local")
    )),
    selfHostedConfig: v.optional(v.object({
      dockerCompose: v.optional(v.string()),
      healthCheckUrl: v.optional(v.string()),
      defaultPort: v.optional(v.number()),
    })),
    freeTier: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    // Resolve category
    const category = await ctx.db
      .query("serviceCategories")
      .withIndex("by_name", (q) => q.eq("name", args.categoryName))
      .unique();
    if (!category) throw new ConvexError(`Unknown category: ${args.categoryName}`);

    // Check if service already exists
    const existing = await ctx.db
      .query("services")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .first();

    if (existing) {
      // Update metadata but preserve isActive, priority, apiKeyConfigured, apiKeyValue
      await ctx.db.patch(existing._id, {
        displayName: args.displayName,
        description: args.description,
        scriptPath: args.scriptPath,
        mcpServer: args.mcpServer,
        apiKeyEnvVar: args.apiKeyEnvVar,
        costInfo: args.costInfo,
        useCases: args.useCases,
        docsUrl: args.docsUrl,
        manifestVersion: args.manifestVersion,
        integrationType: args.integrationType,
        selfHostedConfig: args.selfHostedConfig,
        freeTier: args.freeTier,
      });
      return { action: "updated" as const, id: existing._id };
    }

    // Insert new service (inactive by default)
    const id = await ctx.db.insert("services", {
      categoryId: category._id,
      name: args.name,
      displayName: args.displayName,
      description: args.description,
      isActive: false,
      priority: args.defaultPriority,
      apiKeyEnvVar: args.apiKeyEnvVar,
      apiKeyConfigured: false,
      scriptPath: args.scriptPath,
      mcpServer: args.mcpServer,
      costInfo: args.costInfo,
      useCases: args.useCases,
      docsUrl: args.docsUrl,
      manifestVersion: args.manifestVersion,
      integrationType: args.integrationType,
      selfHostedConfig: args.selfHostedConfig,
      freeTier: args.freeTier,
    });
    return { action: "created" as const, id };
  },
});

// List all services grouped by category (for dashboard)
export const listAllGrouped = query({
  args: {},
  handler: async (ctx) => {
    const categories = await ctx.db.query("serviceCategories").collect();
    const result = [];
    for (const cat of categories.sort((a, b) => a.sortOrder - b.sortOrder)) {
      const services = await ctx.db
        .query("services")
        .withIndex("by_category", (q) => q.eq("categoryId", cat._id))
        .collect();
      result.push({
        ...cat,
        services: services.sort((a, b) => a.priority - b.priority),
      });
    }
    return result;
  },
});

// Stats for the services page header
export const stats = query({
  args: {},
  handler: async (ctx) => {
    const all = await ctx.db.query("services").collect();
    return {
      total: all.length,
      active: all.filter((s) => s.isActive).length,
      degraded: all.filter((s) => s.lastHealthStatus === "degraded" || s.lastHealthStatus === "unreachable").length,
      inactive: all.filter((s) => !s.isActive).length,
      freeTier: all.filter((s) => s.freeTier).length,
    };
  },
});
