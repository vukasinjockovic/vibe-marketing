import { mutation, query } from "./_generated/server";
import { ConvexError, v } from "convex/values";

// ── Shared validators ──

const resourceTypeValidator = v.union(
  v.literal("research_material"), v.literal("brief"),
  v.literal("article"), v.literal("landing_page"),
  v.literal("ad_copy"), v.literal("social_post"),
  v.literal("email_sequence"), v.literal("email_excerpt"),
  v.literal("image_prompt"), v.literal("image"),
  v.literal("video_script"), v.literal("lead_magnet"),
  v.literal("report"), v.literal("brand_asset")
);

const statusValidator = v.union(
  v.literal("draft"), v.literal("in_review"),
  v.literal("reviewed"), v.literal("humanized"),
  v.literal("approved"), v.literal("published"),
  v.literal("archived")
);

// ═══════════════════════════════════════════
// Helper: record history inline (avoids internal mutation scheduling)
// ═══════════════════════════════════════════

async function recordHistory(
  ctx: any,
  resourceId: any,
  changeType: string,
  changedBy: string,
  opts?: { changedFields?: string[]; previousValues?: any; note?: string }
) {
  await ctx.db.insert("resourceHistory", {
    resourceId,
    changeType,
    changedBy,
    changedFields: opts?.changedFields,
    previousValues: opts?.previousValues,
    note: opts?.note,
    createdAt: Date.now(),
  });
}

// ═══════════════════════════════════════════
// create — Insert or upsert a resource
// Upsert: if taskId + filePath combo exists, update instead
// ═══════════════════════════════════════════

export const create = mutation({
  args: {
    projectId: v.id("projects"),
    resourceType: resourceTypeValidator,
    title: v.string(),
    slug: v.optional(v.string()),
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
    taskId: v.optional(v.id("tasks")),
    parentResourceId: v.optional(v.id("resources")),
    relatedResourceIds: v.optional(v.array(v.id("resources"))),
    filePath: v.optional(v.string()),
    contentHash: v.optional(v.string()),
    content: v.optional(v.string()),
    fileUrl: v.optional(v.string()),
    mimeType: v.optional(v.string()),
    fileSizeBytes: v.optional(v.number()),
    status: statusValidator,
    pipelineStage: v.optional(v.string()),
    qualityScore: v.optional(v.number()),
    createdBy: v.string(),
    metadata: v.optional(v.any()),
    publishScheduledAt: v.optional(v.number()),
    publishTarget: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // ── Slug uniqueness check ──
    if (args.slug) {
      const existing = await ctx.db
        .query("resources")
        .withIndex("by_slug", (q) => q.eq("slug", args.slug!))
        .collect();
      const conflict = existing.find(
        (r) => r.projectId === args.projectId
      );
      // Only conflict if it's not the same resource we'd upsert into
      if (conflict) {
        // Check if this is an upsert scenario
        const isUpsert = args.taskId && args.filePath &&
          conflict.taskId === args.taskId && conflict.filePath === args.filePath;
        if (!isUpsert) {
          throw new ConvexError(`Slug "${args.slug}" already exists in this project`);
        }
      }
    }

    // ── Upsert: check for existing taskId + filePath combo ──
    if (args.taskId && args.filePath) {
      const existingByTask = await ctx.db
        .query("resources")
        .withIndex("by_task", (q) => q.eq("taskId", args.taskId!))
        .collect();
      const match = existingByTask.find((r) => r.filePath === args.filePath);

      if (match) {
        // Update existing resource
        const patch: Record<string, unknown> = {
          title: args.title,
          resourceType: args.resourceType,
          status: args.status,
          updatedBy: args.createdBy,
          updatedAt: Date.now(),
        };
        if (args.slug !== undefined) patch.slug = args.slug;
        if (args.content !== undefined) patch.content = args.content;
        if (args.contentHash !== undefined) patch.contentHash = args.contentHash;
        if (args.fileUrl !== undefined) patch.fileUrl = args.fileUrl;
        if (args.mimeType !== undefined) patch.mimeType = args.mimeType;
        if (args.fileSizeBytes !== undefined) patch.fileSizeBytes = args.fileSizeBytes;
        if (args.pipelineStage !== undefined) patch.pipelineStage = args.pipelineStage;
        if (args.qualityScore !== undefined) patch.qualityScore = args.qualityScore;
        if (args.metadata !== undefined) patch.metadata = args.metadata;
        if (args.parentResourceId !== undefined) patch.parentResourceId = args.parentResourceId;
        if (args.relatedResourceIds !== undefined) patch.relatedResourceIds = args.relatedResourceIds;
        if (args.campaignId !== undefined) patch.campaignId = args.campaignId;
        if (args.contentBatchId !== undefined) patch.contentBatchId = args.contentBatchId;
        if (args.publishScheduledAt !== undefined) patch.publishScheduledAt = args.publishScheduledAt;
        if (args.publishTarget !== undefined) patch.publishTarget = args.publishTarget;

        await ctx.db.patch(match._id, patch);
        await recordHistory(ctx, match._id, "updated", args.createdBy, {
          note: "Upsert: updated existing resource with same taskId+filePath",
        });
        return match._id;
      }
    }

    // ── Insert new resource ──
    const now = Date.now();
    const id = await ctx.db.insert("resources", {
      projectId: args.projectId,
      resourceType: args.resourceType,
      title: args.title,
      slug: args.slug,
      campaignId: args.campaignId,
      contentBatchId: args.contentBatchId,
      taskId: args.taskId,
      parentResourceId: args.parentResourceId,
      relatedResourceIds: args.relatedResourceIds,
      filePath: args.filePath,
      contentHash: args.contentHash,
      content: args.content,
      fileUrl: args.fileUrl,
      mimeType: args.mimeType,
      fileSizeBytes: args.fileSizeBytes,
      status: args.status,
      pipelineStage: args.pipelineStage,
      qualityScore: args.qualityScore,
      createdBy: args.createdBy,
      metadata: args.metadata,
      createdAt: now,
      publishScheduledAt: args.publishScheduledAt,
      publishTarget: args.publishTarget,
    });

    await recordHistory(ctx, id, "created", args.createdBy);
    return id;
  },
});

// ═══════════════════════════════════════════
// batchCreate — Insert multiple resources
// ═══════════════════════════════════════════

export const batchCreate = mutation({
  args: {
    resources: v.array(v.object({
      projectId: v.id("projects"),
      resourceType: resourceTypeValidator,
      title: v.string(),
      slug: v.optional(v.string()),
      campaignId: v.optional(v.id("campaigns")),
      contentBatchId: v.optional(v.id("contentBatches")),
      taskId: v.optional(v.id("tasks")),
      parentResourceId: v.optional(v.id("resources")),
      filePath: v.optional(v.string()),
      contentHash: v.optional(v.string()),
      content: v.optional(v.string()),
      fileUrl: v.optional(v.string()),
      mimeType: v.optional(v.string()),
      fileSizeBytes: v.optional(v.number()),
      status: statusValidator,
      pipelineStage: v.optional(v.string()),
      createdBy: v.string(),
      metadata: v.optional(v.any()),
    })),
  },
  handler: async (ctx, args) => {
    const ids: string[] = [];
    const now = Date.now();

    for (const r of args.resources) {
      // Upsert check
      if (r.taskId && r.filePath) {
        const existingByTask = await ctx.db
          .query("resources")
          .withIndex("by_task", (q) => q.eq("taskId", r.taskId!))
          .collect();
        const match = existingByTask.find((res) => res.filePath === r.filePath);
        if (match) {
          await ctx.db.patch(match._id, {
            title: r.title,
            resourceType: r.resourceType,
            status: r.status,
            content: r.content,
            contentHash: r.contentHash,
            metadata: r.metadata,
            updatedBy: r.createdBy,
            updatedAt: now,
          });
          await recordHistory(ctx, match._id, "updated", r.createdBy, {
            note: "Batch upsert",
          });
          ids.push(match._id);
          continue;
        }
      }

      const id = await ctx.db.insert("resources", {
        projectId: r.projectId,
        resourceType: r.resourceType,
        title: r.title,
        slug: r.slug,
        campaignId: r.campaignId,
        contentBatchId: r.contentBatchId,
        taskId: r.taskId,
        parentResourceId: r.parentResourceId,
        filePath: r.filePath,
        contentHash: r.contentHash,
        content: r.content,
        fileUrl: r.fileUrl,
        mimeType: r.mimeType,
        fileSizeBytes: r.fileSizeBytes,
        status: r.status,
        pipelineStage: r.pipelineStage,
        createdBy: r.createdBy,
        metadata: r.metadata,
        createdAt: now,
      });
      await recordHistory(ctx, id, "created", r.createdBy);
      ids.push(id);
    }

    return ids;
  },
});

// ═══════════════════════════════════════════
// update — Partial update with diff tracking
// ═══════════════════════════════════════════

export const update = mutation({
  args: {
    id: v.id("resources"),
    title: v.optional(v.string()),
    slug: v.optional(v.string()),
    resourceType: v.optional(resourceTypeValidator),
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
    parentResourceId: v.optional(v.id("resources")),
    relatedResourceIds: v.optional(v.array(v.id("resources"))),
    filePath: v.optional(v.string()),
    contentHash: v.optional(v.string()),
    fileOrphaned: v.optional(v.boolean()),
    content: v.optional(v.string()),
    fileUrl: v.optional(v.string()),
    mimeType: v.optional(v.string()),
    fileSizeBytes: v.optional(v.number()),
    status: v.optional(statusValidator),
    pipelineStage: v.optional(v.string()),
    qualityScore: v.optional(v.number()),
    updatedBy: v.string(),
    metadata: v.optional(v.any()),
    publishScheduledAt: v.optional(v.number()),
    publishTarget: v.optional(v.string()),
    publishedAt: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const resource = await ctx.db.get(args.id);
    if (!resource) throw new ConvexError("Resource not found");

    // Slug uniqueness check
    if (args.slug && args.slug !== resource.slug) {
      const existing = await ctx.db
        .query("resources")
        .withIndex("by_slug", (q) => q.eq("slug", args.slug!))
        .collect();
      const conflict = existing.find(
        (r) => r.projectId === resource.projectId && r._id !== args.id
      );
      if (conflict) {
        throw new ConvexError(`Slug "${args.slug}" already exists in this project`);
      }
    }

    // Compute diff
    const changedFields: string[] = [];
    const previousValues: Record<string, unknown> = {};
    const patch: Record<string, unknown> = { updatedAt: Date.now(), updatedBy: args.updatedBy };

    const fields = [
      "title", "slug", "resourceType", "campaignId", "contentBatchId",
      "parentResourceId", "relatedResourceIds", "filePath", "contentHash",
      "fileOrphaned", "content", "fileUrl", "mimeType", "fileSizeBytes",
      "status", "pipelineStage", "qualityScore", "metadata",
      "publishScheduledAt", "publishTarget", "publishedAt",
    ] as const;

    for (const field of fields) {
      if (args[field] !== undefined && args[field] !== (resource as any)[field]) {
        changedFields.push(field);
        previousValues[field] = (resource as any)[field];
        patch[field] = args[field];
      }
    }

    if (changedFields.length === 0) return resource._id;

    await ctx.db.patch(args.id, patch);

    // Determine change type
    let changeType: string = "updated";
    if (changedFields.includes("status")) changeType = "status_changed";
    else if (changedFields.includes("content")) changeType = "content_changed";
    else if (changedFields.includes("metadata")) changeType = "metadata_changed";

    await recordHistory(ctx, args.id, changeType, args.updatedBy, {
      changedFields,
      previousValues,
    });

    return resource._id;
  },
});

// ═══════════════════════════════════════════
// updateStatus — Convenience for status transitions
// ═══════════════════════════════════════════

export const updateStatus = mutation({
  args: {
    id: v.id("resources"),
    status: statusValidator,
    updatedBy: v.string(),
    note: v.optional(v.string()),
    qualityScore: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const resource = await ctx.db.get(args.id);
    if (!resource) throw new ConvexError("Resource not found");

    const patch: Record<string, unknown> = {
      status: args.status,
      updatedBy: args.updatedBy,
      updatedAt: Date.now(),
    };
    if (args.qualityScore !== undefined) patch.qualityScore = args.qualityScore;
    if (args.status === "published") patch.publishedAt = Date.now();

    await ctx.db.patch(args.id, patch);

    await recordHistory(ctx, args.id, "status_changed", args.updatedBy, {
      changedFields: ["status"],
      previousValues: { status: resource.status },
      note: args.note,
    });

    return args.id;
  },
});

// ═══════════════════════════════════════════
// get — Get resource by ID
// ═══════════════════════════════════════════

export const get = query({
  args: { id: v.id("resources") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// ═══════════════════════════════════════════
// getBySlug — Get resource by slug within project
// ═══════════════════════════════════════════

export const getBySlug = query({
  args: {
    projectId: v.id("projects"),
    slug: v.string(),
  },
  handler: async (ctx, args) => {
    const results = await ctx.db
      .query("resources")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .collect();
    return results.find((r) => r.projectId === args.projectId) || null;
  },
});

// ═══════════════════════════════════════════
// listByProject — Paginated list for a project
// ═══════════════════════════════════════════

export const listByProject = query({
  args: {
    projectId: v.id("projects"),
    paginationOpts: v.optional(v.object({
      cursor: v.optional(v.string()),
      numItems: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const numItems = args.paginationOpts?.numItems || 25;
    const result = await ctx.db
      .query("resources")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .order("desc")
      .paginate({
        cursor: (args.paginationOpts?.cursor as any) || null,
        numItems,
      });
    return result;
  },
});

// ═══════════════════════════════════════════
// listByCampaign — Paginated list for a campaign
// ═══════════════════════════════════════════

export const listByCampaign = query({
  args: {
    campaignId: v.id("campaigns"),
    paginationOpts: v.optional(v.object({
      cursor: v.optional(v.string()),
      numItems: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const numItems = args.paginationOpts?.numItems || 25;
    const result = await ctx.db
      .query("resources")
      .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId))
      .order("desc")
      .paginate({
        cursor: (args.paginationOpts?.cursor as any) || null,
        numItems,
      });
    return result;
  },
});

// ═══════════════════════════════════════════
// listByContentBatch — Paginated list for a content batch
// ═══════════════════════════════════════════

export const listByContentBatch = query({
  args: {
    contentBatchId: v.id("contentBatches"),
    paginationOpts: v.optional(v.object({
      cursor: v.optional(v.string()),
      numItems: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const numItems = args.paginationOpts?.numItems || 25;
    const result = await ctx.db
      .query("resources")
      .withIndex("by_content_batch", (q) => q.eq("contentBatchId", args.contentBatchId))
      .order("desc")
      .paginate({
        cursor: (args.paginationOpts?.cursor as any) || null,
        numItems,
      });
    return result;
  },
});

// ═══════════════════════════════════════════
// listByTask — All resources for a task (small set, no pagination)
// ═══════════════════════════════════════════

export const listByTask = query({
  args: { taskId: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resources")
      .withIndex("by_task", (q) => q.eq("taskId", args.taskId))
      .collect();
  },
});

// ═══════════════════════════════════════════
// listByType — By type in a project, paginated
// ═══════════════════════════════════════════

export const listByType = query({
  args: {
    projectId: v.id("projects"),
    resourceType: resourceTypeValidator,
    paginationOpts: v.optional(v.object({
      cursor: v.optional(v.string()),
      numItems: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const numItems = args.paginationOpts?.numItems || 25;
    const result = await ctx.db
      .query("resources")
      .withIndex("by_project_type", (q) =>
        q.eq("projectId", args.projectId).eq("resourceType", args.resourceType)
      )
      .order("desc")
      .paginate({
        cursor: (args.paginationOpts?.cursor as any) || null,
        numItems,
      });
    return result;
  },
});

// ═══════════════════════════════════════════
// listChildren — Resources with parentResourceId = given ID
// ═══════════════════════════════════════════

export const listChildren = query({
  args: { parentResourceId: v.id("resources") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resources")
      .withIndex("by_parent", (q) => q.eq("parentResourceId", args.parentResourceId))
      .collect();
  },
});

// ═══════════════════════════════════════════
// listRelated — Children + fetch each relatedResourceId
// ═══════════════════════════════════════════

export const listRelated = query({
  args: { resourceId: v.id("resources") },
  handler: async (ctx, args) => {
    const resource = await ctx.db.get(args.resourceId);
    if (!resource) throw new ConvexError("Resource not found");

    const children = await ctx.db
      .query("resources")
      .withIndex("by_parent", (q) => q.eq("parentResourceId", args.resourceId))
      .collect();

    const related: any[] = [];
    if (resource.relatedResourceIds) {
      for (const relId of resource.relatedResourceIds) {
        const rel = await ctx.db.get(relId);
        if (rel) related.push(rel);
      }
    }

    let parent = null;
    if (resource.parentResourceId) {
      parent = await ctx.db.get(resource.parentResourceId);
    }

    return { parent, children, related };
  },
});

// ═══════════════════════════════════════════
// syncFromFile — Update content + hash from filesystem
// ═══════════════════════════════════════════

export const syncFromFile = mutation({
  args: {
    id: v.id("resources"),
    content: v.optional(v.string()),
    contentHash: v.string(),
    fileSizeBytes: v.optional(v.number()),
    syncedBy: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const resource = await ctx.db.get(args.id);
    if (!resource) throw new ConvexError("Resource not found");

    const by = args.syncedBy || "system";

    if (resource.contentHash === args.contentHash) {
      return { updated: false, reason: "Hash unchanged" };
    }

    const patch: Record<string, unknown> = {
      contentHash: args.contentHash,
      fileOrphaned: false,
      updatedAt: Date.now(),
      updatedBy: by,
    };
    if (args.content !== undefined) patch.content = args.content;
    if (args.fileSizeBytes !== undefined) patch.fileSizeBytes = args.fileSizeBytes;

    await ctx.db.patch(args.id, patch);
    await recordHistory(ctx, args.id, "content_changed", by, {
      changedFields: ["contentHash", "content"],
      previousValues: { contentHash: resource.contentHash },
      note: "Synced from filesystem",
    });

    return { updated: true };
  },
});

// ═══════════════════════════════════════════
// stats — Aggregate counts by type and status
// ═══════════════════════════════════════════

export const stats = query({
  args: {
    projectId: v.optional(v.id("projects")),
    campaignId: v.optional(v.id("campaigns")),
    contentBatchId: v.optional(v.id("contentBatches")),
  },
  handler: async (ctx, args) => {
    let resources;
    if (args.campaignId) {
      resources = await ctx.db
        .query("resources")
        .withIndex("by_campaign", (q) => q.eq("campaignId", args.campaignId!))
        .collect();
    } else if (args.contentBatchId) {
      resources = await ctx.db
        .query("resources")
        .withIndex("by_content_batch", (q) => q.eq("contentBatchId", args.contentBatchId!))
        .collect();
    } else if (args.projectId) {
      resources = await ctx.db
        .query("resources")
        .withIndex("by_project", (q) => q.eq("projectId", args.projectId!))
        .collect();
    } else {
      resources = await ctx.db.query("resources").collect();
    }

    const byType: Record<string, number> = {};
    const byStatus: Record<string, number> = {};
    for (const r of resources) {
      byType[r.resourceType] = (byType[r.resourceType] || 0) + 1;
      byStatus[r.status] = (byStatus[r.status] || 0) + 1;
    }

    return { total: resources.length, byType, byStatus };
  },
});

// ═══════════════════════════════════════════
// search — Filter by title substring + type + status
// ═══════════════════════════════════════════

export const search = query({
  args: {
    projectId: v.id("projects"),
    titleQuery: v.optional(v.string()),
    resourceType: v.optional(resourceTypeValidator),
    status: v.optional(statusValidator),
    paginationOpts: v.optional(v.object({
      cursor: v.optional(v.string()),
      numItems: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const numItems = args.paginationOpts?.numItems || 25;

    // Use the most specific index available
    let q;
    if (args.resourceType) {
      q = ctx.db
        .query("resources")
        .withIndex("by_project_type", (idx) =>
          idx.eq("projectId", args.projectId).eq("resourceType", args.resourceType!)
        );
    } else {
      q = ctx.db
        .query("resources")
        .withIndex("by_project", (idx) => idx.eq("projectId", args.projectId));
    }

    const result = await q.order("desc").paginate({
      cursor: (args.paginationOpts?.cursor as any) || null,
      numItems: numItems * 3, // over-fetch to account for filters
    });

    // Apply client-side filters
    let filtered = result.page;
    if (args.status) {
      filtered = filtered.filter((r) => r.status === args.status);
    }
    if (args.titleQuery) {
      const lower = args.titleQuery.toLowerCase();
      filtered = filtered.filter((r) => r.title.toLowerCase().includes(lower));
    }

    return {
      page: filtered.slice(0, numItems),
      continueCursor: result.continueCursor,
      isDone: result.isDone,
    };
  },
});

// ═══════════════════════════════════════════
// remove — Delete resource (block if children exist)
// ═══════════════════════════════════════════

export const remove = mutation({
  args: {
    id: v.id("resources"),
    deletedBy: v.string(),
  },
  handler: async (ctx, args) => {
    const resource = await ctx.db.get(args.id);
    if (!resource) throw new ConvexError("Resource not found");

    // Block if children exist
    const children = await ctx.db
      .query("resources")
      .withIndex("by_parent", (q) => q.eq("parentResourceId", args.id))
      .first();
    if (children) {
      throw new ConvexError(
        "Cannot delete resource with children. Delete or re-parent children first."
      );
    }

    // Record deletion history before deleting
    await recordHistory(ctx, args.id, "deleted", args.deletedBy, {
      previousValues: {
        title: resource.title,
        resourceType: resource.resourceType,
        status: resource.status,
      },
    });

    await ctx.db.delete(args.id);
    return { deleted: true };
  },
});

// ═══════════════════════════════════════════
// getHistory — Return history records for a resource
// ═══════════════════════════════════════════

export const getHistory = query({
  args: { resourceId: v.id("resources") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resourceHistory")
      .withIndex("by_resource", (q) => q.eq("resourceId", args.resourceId))
      .order("desc")
      .collect();
  },
});
