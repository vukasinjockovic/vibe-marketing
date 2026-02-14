import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";

// ═══════════════════════════════════════════
// Internal helper — record a history entry for a resource
// Called by resources.ts mutations, not exposed as public API
// ═══════════════════════════════════════════

export const record = internalMutation({
  args: {
    resourceId: v.id("resources"),
    changeType: v.union(
      v.literal("created"),
      v.literal("updated"),
      v.literal("status_changed"),
      v.literal("content_changed"),
      v.literal("metadata_changed"),
      v.literal("deleted")
    ),
    changedBy: v.string(),
    changedFields: v.optional(v.array(v.string())),
    previousValues: v.optional(v.any()),
    note: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("resourceHistory", {
      resourceId: args.resourceId,
      changeType: args.changeType,
      changedBy: args.changedBy,
      changedFields: args.changedFields,
      previousValues: args.previousValues,
      note: args.note,
      createdAt: Date.now(),
    });
  },
});

// ═══════════════════════════════════════════
// Query: get history for a resource
// ═══════════════════════════════════════════

export const listByResource = query({
  args: { resourceId: v.id("resources") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resourceHistory")
      .withIndex("by_resource", (q) => q.eq("resourceId", args.resourceId))
      .order("desc")
      .collect();
  },
});
