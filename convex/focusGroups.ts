import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// List focus groups by project
export const listByProject = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("focusGroups")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
  },
});

// List focus groups by product
export const listByProduct = query({
  args: { productId: v.id("products") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("focusGroups")
      .withIndex("by_product", (q) => q.eq("productId", args.productId))
      .collect();
  },
});

// Get focus group by id
export const get = query({
  args: { id: v.id("focusGroups") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

// Get focus groups for a campaign (loads campaign, then each focus group)
export const getByCampaign = query({
  args: { campaignId: v.id("campaigns") },
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.campaignId);
    if (!campaign) throw new Error("Campaign not found");

    const focusGroups = await Promise.all(
      campaign.targetFocusGroupIds.map((id) => ctx.db.get(id))
    );

    return focusGroups.filter((fg) => fg !== null);
  },
});

// Get focus groups for a content batch (loads batch, then each focus group)
export const getByContentBatch = query({
  args: { contentBatchId: v.id("contentBatches") },
  handler: async (ctx, args) => {
    const batch = await ctx.db.get(args.contentBatchId);
    if (!batch) throw new Error("Content batch not found");

    const focusGroups = await Promise.all(
      batch.targetFocusGroupIds.map((id) => ctx.db.get(id))
    );

    return focusGroups.filter((fg) => fg !== null);
  },
});

// Create a focus group
export const create = mutation({
  args: {
    projectId: v.id("projects"),
    productId: v.optional(v.id("products")),
    number: v.number(),
    name: v.string(),
    nickname: v.string(),
    category: v.string(),
    overview: v.string(),
    demographics: v.object({
      ageRange: v.string(),
      gender: v.string(),
      income: v.string(),
      lifestyle: v.string(),
      triggers: v.array(v.string()),
    }),
    psychographics: v.object({
      values: v.array(v.string()),
      beliefs: v.array(v.string()),
      lifestyle: v.string(),
      identity: v.string(),
    }),
    coreDesires: v.array(v.string()),
    painPoints: v.array(v.string()),
    fears: v.array(v.string()),
    beliefs: v.array(v.string()),
    objections: v.array(v.string()),
    emotionalTriggers: v.array(v.string()),
    languagePatterns: v.array(v.string()),
    ebookAngles: v.array(v.string()),
    marketingHooks: v.array(v.string()),
    transformationPromise: v.string(),
    source: v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual")),
    lastEnriched: v.optional(v.number()),
    enrichmentNotes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("focusGroups", args);
  },
});

// Update focus group (partial)
export const update = mutation({
  args: {
    id: v.id("focusGroups"),
    name: v.optional(v.string()),
    nickname: v.optional(v.string()),
    category: v.optional(v.string()),
    overview: v.optional(v.string()),
    demographics: v.optional(v.object({
      ageRange: v.string(),
      gender: v.string(),
      income: v.string(),
      lifestyle: v.string(),
      triggers: v.array(v.string()),
    })),
    psychographics: v.optional(v.object({
      values: v.array(v.string()),
      beliefs: v.array(v.string()),
      lifestyle: v.string(),
      identity: v.string(),
    })),
    coreDesires: v.optional(v.array(v.string())),
    painPoints: v.optional(v.array(v.string())),
    fears: v.optional(v.array(v.string())),
    beliefs: v.optional(v.array(v.string())),
    objections: v.optional(v.array(v.string())),
    emotionalTriggers: v.optional(v.array(v.string())),
    languagePatterns: v.optional(v.array(v.string())),
    ebookAngles: v.optional(v.array(v.string())),
    marketingHooks: v.optional(v.array(v.string())),
    transformationPromise: v.optional(v.string()),
    lastEnriched: v.optional(v.number()),
    enrichmentNotes: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const { id, ...fields } = args;
    const focusGroup = await ctx.db.get(id);
    if (!focusGroup) throw new Error("Focus group not found");

    const updates: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      if (value !== undefined) updates[key] = value;
    }

    await ctx.db.patch(id, updates);
  },
});

// Delete focus group
export const remove = mutation({
  args: { id: v.id("focusGroups") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
  },
});

// ═══════════════════════════════════════════
// NEW: Focus Group Intelligence Functions
// ═══════════════════════════════════════════

// Find by exact name within a project
export const findByName = query({
  args: {
    projectId: v.id("projects"),
    name: v.string(),
  },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroups")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    return all.find((fg) => fg.name === args.name) || null;
  },
});

// Find by nickname (case-insensitive, within project)
export const findByNickname = query({
  args: {
    projectId: v.id("projects"),
    nickname: v.string(),
  },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroups")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const lowerNickname = args.nickname.toLowerCase();
    return all.filter((fg) => fg.nickname.toLowerCase() === lowerNickname);
  },
});

// Search by name (partial match, case-insensitive, within project)
export const searchByName = query({
  args: {
    projectId: v.id("projects"),
    query: v.string(),
  },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroups")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const lowerQuery = args.query.toLowerCase();
    return all.filter((fg) => fg.name.toLowerCase().includes(lowerQuery));
  },
});

// List focus groups needing enrichment (lastEnriched is null or >7 days ago)
export const listNeedingEnrichment = query({
  args: { projectId: v.id("projects") },
  handler: async (ctx, args) => {
    const all = await ctx.db
      .query("focusGroups")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .collect();
    const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    return all.filter(
      (fg) => fg.lastEnriched === undefined || fg.lastEnriched === null || fg.lastEnriched < sevenDaysAgo
    );
  },
});

// Get enrichment progress for a focus group
// Weighted scoring: awarenessStage=15, sophisticationLevel=10, contentPreferences=10,
// influenceSources=10, purchaseBehavior=15, competitorContext=10,
// communicationStyle=10, seasonalContext=5, negativeTriggers=10, awarenessSignals=5
// Total=100
export const getEnrichmentProgress = query({
  args: { id: v.id("focusGroups") },
  handler: async (ctx, args) => {
    const fg = await ctx.db.get(args.id);
    if (!fg) throw new Error("Focus group not found");

    const fieldWeights: Array<{ field: string; weight: number }> = [
      { field: "awarenessStage", weight: 15 },
      { field: "sophisticationLevel", weight: 10 },
      { field: "contentPreferences", weight: 10 },
      { field: "influenceSources", weight: 10 },
      { field: "purchaseBehavior", weight: 15 },
      { field: "competitorContext", weight: 10 },
      { field: "communicationStyle", weight: 10 },
      { field: "seasonalContext", weight: 5 },
      { field: "negativeTriggers", weight: 10 },
      { field: "awarenessSignals", weight: 5 },
    ];

    let filledCount = 0;
    let score = 0;
    const missingFields: string[] = [];

    for (const { field, weight } of fieldWeights) {
      const value = (fg as Record<string, unknown>)[field];
      if (value !== undefined && value !== null) {
        filledCount++;
        score += weight;
      } else {
        missingFields.push(field);
      }
    }

    return {
      filledCount,
      totalCount: fieldWeights.length,
      score,
      missingFields,
    };
  },
});

// Create multiple focus groups at once
export const createBatch = mutation({
  args: {
    groups: v.array(v.object({
      projectId: v.id("projects"),
      productId: v.optional(v.id("products")),
      number: v.number(),
      name: v.string(),
      nickname: v.string(),
      category: v.string(),
      overview: v.string(),
      demographics: v.object({
        ageRange: v.string(),
        gender: v.string(),
        income: v.string(),
        lifestyle: v.string(),
        triggers: v.array(v.string()),
      }),
      psychographics: v.object({
        values: v.array(v.string()),
        beliefs: v.array(v.string()),
        lifestyle: v.string(),
        identity: v.string(),
      }),
      coreDesires: v.array(v.string()),
      painPoints: v.array(v.string()),
      fears: v.array(v.string()),
      beliefs: v.array(v.string()),
      objections: v.array(v.string()),
      emotionalTriggers: v.array(v.string()),
      languagePatterns: v.array(v.string()),
      ebookAngles: v.array(v.string()),
      marketingHooks: v.array(v.string()),
      transformationPromise: v.string(),
      source: v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual")),
      lastEnriched: v.optional(v.number()),
      enrichmentNotes: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const ids = [];
    for (const group of args.groups) {
      const id = await ctx.db.insert("focusGroups", group);
      ids.push(id);
    }
    return ids;
  },
});

// Enrich a single focus group with new data
// Appends to enrichments[] audit trail and updates lastEnriched
export const enrich = mutation({
  args: {
    id: v.id("focusGroups"),
    fields: v.object({
      awarenessStage: v.optional(v.union(
        v.literal("unaware"), v.literal("problem_aware"), v.literal("solution_aware"),
        v.literal("product_aware"), v.literal("most_aware")
      )),
      awarenessConfidence: v.optional(v.union(v.literal("high"), v.literal("medium"), v.literal("low"))),
      awarenessStageSource: v.optional(v.union(v.literal("auto"), v.literal("manual"))),
      awarenessSignals: v.optional(v.object({
        beliefsSignal: v.optional(v.string()),
        objectionsSignal: v.optional(v.string()),
        languageSignal: v.optional(v.string()),
      })),
      contentPreferences: v.optional(v.object({
        preferredFormats: v.optional(v.array(v.string())),
        attentionSpan: v.optional(v.string()),
        tonePreference: v.optional(v.string()),
      })),
      influenceSources: v.optional(v.object({
        trustedVoices: v.optional(v.array(v.string())),
        mediaConsumption: v.optional(v.array(v.string())),
        socialPlatforms: v.optional(v.array(v.string())),
      })),
      purchaseBehavior: v.optional(v.object({
        buyingTriggers: v.optional(v.array(v.string())),
        priceRange: v.optional(v.string()),
        decisionProcess: v.optional(v.string()),
        objectionHistory: v.optional(v.array(v.string())),
      })),
      competitorContext: v.optional(v.object({
        currentSolutions: v.optional(v.array(v.string())),
        switchMotivators: v.optional(v.array(v.string())),
      })),
      sophisticationLevel: v.optional(v.union(
        v.literal("stage1"), v.literal("stage2"), v.literal("stage3"),
        v.literal("stage4"), v.literal("stage5")
      )),
      communicationStyle: v.optional(v.object({
        formalityLevel: v.optional(v.string()),
        humorReceptivity: v.optional(v.string()),
        storyPreference: v.optional(v.string()),
        dataPreference: v.optional(v.string()),
      })),
      seasonalContext: v.optional(v.object({
        peakInterestPeriods: v.optional(v.array(v.string())),
        lifeEvents: v.optional(v.array(v.string())),
        cyclicalBehaviors: v.optional(v.array(v.string())),
      })),
      negativeTriggers: v.optional(v.object({
        dealBreakers: v.optional(v.array(v.string())),
        offensiveTopics: v.optional(v.array(v.string())),
        toneAversions: v.optional(v.array(v.string())),
      })),
    }),
    agentName: v.string(),
    reasoning: v.string(),
  },
  handler: async (ctx, args) => {
    const fg = await ctx.db.get(args.id);
    if (!fg) throw new Error("Focus group not found");

    const now = Date.now();
    const existingEnrichments = fg.enrichments ?? [];
    const newEnrichments = [...existingEnrichments];
    const updates: Record<string, unknown> = {};

    // Process each field in the update
    for (const [field, newValue] of Object.entries(args.fields)) {
      if (newValue === undefined) continue;

      const previousValue = (fg as Record<string, unknown>)[field];

      // Append audit trail entry
      newEnrichments.push({
        timestamp: now,
        source: "pipeline",
        agentName: args.agentName,
        field,
        previousValue: previousValue !== undefined && previousValue !== null
          ? JSON.stringify(previousValue)
          : undefined,
        newValue: JSON.stringify(newValue),
        confidence: "medium" as const,
        reasoning: args.reasoning,
      });

      updates[field] = newValue;
    }

    updates.enrichments = newEnrichments;
    updates.lastEnriched = now;

    await ctx.db.patch(args.id, updates);
  },
});

// Batch version of enrich
export const enrichBatch = mutation({
  args: {
    updates: v.array(v.object({
      id: v.id("focusGroups"),
      fields: v.object({
        awarenessStage: v.optional(v.union(
          v.literal("unaware"), v.literal("problem_aware"), v.literal("solution_aware"),
          v.literal("product_aware"), v.literal("most_aware")
        )),
        awarenessConfidence: v.optional(v.union(v.literal("high"), v.literal("medium"), v.literal("low"))),
        awarenessStageSource: v.optional(v.union(v.literal("auto"), v.literal("manual"))),
        awarenessSignals: v.optional(v.object({
          beliefsSignal: v.optional(v.string()),
          objectionsSignal: v.optional(v.string()),
          languageSignal: v.optional(v.string()),
        })),
        contentPreferences: v.optional(v.object({
          preferredFormats: v.optional(v.array(v.string())),
          attentionSpan: v.optional(v.string()),
          tonePreference: v.optional(v.string()),
        })),
        influenceSources: v.optional(v.object({
          trustedVoices: v.optional(v.array(v.string())),
          mediaConsumption: v.optional(v.array(v.string())),
          socialPlatforms: v.optional(v.array(v.string())),
        })),
        purchaseBehavior: v.optional(v.object({
          buyingTriggers: v.optional(v.array(v.string())),
          priceRange: v.optional(v.string()),
          decisionProcess: v.optional(v.string()),
          objectionHistory: v.optional(v.array(v.string())),
        })),
        competitorContext: v.optional(v.object({
          currentSolutions: v.optional(v.array(v.string())),
          switchMotivators: v.optional(v.array(v.string())),
        })),
        sophisticationLevel: v.optional(v.union(
          v.literal("stage1"), v.literal("stage2"), v.literal("stage3"),
          v.literal("stage4"), v.literal("stage5")
        )),
        communicationStyle: v.optional(v.object({
          formalityLevel: v.optional(v.string()),
          humorReceptivity: v.optional(v.string()),
          storyPreference: v.optional(v.string()),
          dataPreference: v.optional(v.string()),
        })),
        seasonalContext: v.optional(v.object({
          peakInterestPeriods: v.optional(v.array(v.string())),
          lifeEvents: v.optional(v.array(v.string())),
          cyclicalBehaviors: v.optional(v.array(v.string())),
        })),
        negativeTriggers: v.optional(v.object({
          dealBreakers: v.optional(v.array(v.string())),
          offensiveTopics: v.optional(v.array(v.string())),
          toneAversions: v.optional(v.array(v.string())),
        })),
      }),
      agentName: v.string(),
      reasoning: v.string(),
    })),
  },
  handler: async (ctx, args) => {
    const now = Date.now();

    for (const update of args.updates) {
      const fg = await ctx.db.get(update.id);
      if (!fg) continue;

      const existingEnrichments = fg.enrichments ?? [];
      const newEnrichments = [...existingEnrichments];
      const fieldUpdates: Record<string, unknown> = {};

      for (const [field, newValue] of Object.entries(update.fields)) {
        if (newValue === undefined) continue;

        const previousValue = (fg as Record<string, unknown>)[field];

        newEnrichments.push({
          timestamp: now,
          source: "pipeline",
          agentName: update.agentName,
          field,
          previousValue: previousValue !== undefined && previousValue !== null
            ? JSON.stringify(previousValue)
            : undefined,
          newValue: JSON.stringify(newValue),
          confidence: "medium" as const,
          reasoning: update.reasoning,
        });

        fieldUpdates[field] = newValue;
      }

      fieldUpdates.enrichments = newEnrichments;
      fieldUpdates.lastEnriched = now;

      await ctx.db.patch(update.id, fieldUpdates);
    }
  },
});

// Import approved staging records into the focusGroups table
// - "create_new" staging records: insert new focusGroup
// - "enrich_existing" staging records: merge into matched focusGroup
// - Updates staging record reviewStatus to "imported"
export const importFromStaging = mutation({
  args: {
    stagingIds: v.array(v.id("focusGroupStaging")),
  },
  handler: async (ctx, args) => {
    let created = 0;
    let enriched = 0;

    for (const stagingId of args.stagingIds) {
      const staging = await ctx.db.get(stagingId);
      if (!staging) continue;

      // Only process approved or edited records
      if (staging.reviewStatus !== "approved" && staging.reviewStatus !== "edited") {
        continue;
      }

      if (staging.matchStatus === "create_new") {
        // Build a complete focusGroup record from staging data
        const focusGroupData = {
          projectId: staging.projectId,
          productId: staging.productId,
          number: staging.number ?? 0,
          name: staging.name,
          nickname: staging.nickname ?? staging.name,
          category: staging.category ?? "uncategorized",
          overview: staging.overview ?? "",
          demographics: staging.demographics ?? {
            ageRange: "unknown",
            gender: "all",
            income: "unknown",
            lifestyle: "unknown",
            triggers: [],
          },
          psychographics: staging.psychographics ?? {
            values: [],
            beliefs: [],
            lifestyle: "unknown",
            identity: "unknown",
          },
          coreDesires: staging.coreDesires ?? [],
          painPoints: staging.painPoints ?? [],
          fears: staging.fears ?? [],
          beliefs: staging.beliefs ?? [],
          objections: staging.objections ?? [],
          emotionalTriggers: staging.emotionalTriggers ?? [],
          languagePatterns: staging.languagePatterns ?? [],
          ebookAngles: staging.ebookAngles ?? [],
          marketingHooks: staging.marketingHooks ?? [],
          transformationPromise: staging.transformationPromise ?? "",
          source: staging.source ?? ("researched" as const),
          lastEnriched: Date.now(),
          // Copy enrichment fields if present
          ...(staging.awarenessStage !== undefined && { awarenessStage: staging.awarenessStage }),
          ...(staging.awarenessConfidence !== undefined && { awarenessConfidence: staging.awarenessConfidence }),
          ...(staging.awarenessStageSource !== undefined && { awarenessStageSource: staging.awarenessStageSource }),
          ...(staging.awarenessSignals !== undefined && { awarenessSignals: staging.awarenessSignals }),
          ...(staging.contentPreferences !== undefined && { contentPreferences: staging.contentPreferences }),
          ...(staging.influenceSources !== undefined && { influenceSources: staging.influenceSources }),
          ...(staging.purchaseBehavior !== undefined && { purchaseBehavior: staging.purchaseBehavior }),
          ...(staging.competitorContext !== undefined && { competitorContext: staging.competitorContext }),
          ...(staging.sophisticationLevel !== undefined && { sophisticationLevel: staging.sophisticationLevel }),
          ...(staging.communicationStyle !== undefined && { communicationStyle: staging.communicationStyle }),
          ...(staging.seasonalContext !== undefined && { seasonalContext: staging.seasonalContext }),
          ...(staging.negativeTriggers !== undefined && { negativeTriggers: staging.negativeTriggers }),
          ...(staging.researchNotes !== undefined && { researchNotes: staging.researchNotes }),
          enrichments: [{
            timestamp: Date.now(),
            source: "staging_import",
            agentName: "system",
            field: "initial_import",
            previousValue: undefined,
            newValue: "Imported from staging",
            confidence: "high" as const,
            reasoning: "Initial import from focus group staging",
          }],
        };

        await ctx.db.insert("focusGroups", focusGroupData);
        created++;
      } else if (staging.matchStatus === "enrich_existing" && staging.matchedFocusGroupId) {
        // Merge into existing focus group
        const existing = await ctx.db.get(staging.matchedFocusGroupId);
        if (!existing) continue;

        const now = Date.now();
        const existingEnrichments = existing.enrichments ?? [];
        const newEnrichments = [...existingEnrichments];
        const updates: Record<string, unknown> = {};

        // Array fields: union (add new items not already present)
        const arrayFields = [
          "coreDesires", "painPoints", "fears", "beliefs", "objections",
          "emotionalTriggers", "languagePatterns", "ebookAngles", "marketingHooks",
        ] as const;

        for (const field of arrayFields) {
          const stagingValue = staging[field];
          if (stagingValue && stagingValue.length > 0) {
            const existingArr = (existing[field] as string[]) ?? [];
            const existingLower = new Set(existingArr.map((s: string) => s.toLowerCase()));
            const newItems = stagingValue.filter(
              (item: string) => !existingLower.has(item.toLowerCase())
            );
            if (newItems.length > 0) {
              const merged = [...existingArr, ...newItems];
              updates[field] = merged;
              newEnrichments.push({
                timestamp: now,
                source: "staging_import",
                agentName: "system",
                field,
                previousValue: JSON.stringify(existingArr),
                newValue: JSON.stringify(merged),
                confidence: "medium" as const,
                reasoning: `Merged ${newItems.length} new items from staging import`,
              });
            }
          }
        }

        // String fields: keep existing unless empty
        const stringFields = ["overview", "transformationPromise", "researchNotes"] as const;
        for (const field of stringFields) {
          const stagingValue = staging[field];
          const existingValue = existing[field];
          if (stagingValue && (!existingValue || existingValue === "")) {
            updates[field] = stagingValue;
            newEnrichments.push({
              timestamp: now,
              source: "staging_import",
              agentName: "system",
              field,
              previousValue: existingValue ?? undefined,
              newValue: stagingValue,
              confidence: "medium" as const,
              reasoning: "Filled empty field from staging import",
            });
          }
        }

        // Object fields: deep merge (fill missing sub-fields)
        const objectFields = ["demographics", "psychographics"] as const;
        for (const field of objectFields) {
          const stagingValue = staging[field];
          const existingValue = existing[field];
          if (stagingValue && existingValue) {
            // Deep merge: fill in missing sub-fields
            const merged = { ...existingValue } as Record<string, unknown>;
            let changed = false;
            for (const [subKey, subVal] of Object.entries(stagingValue as Record<string, unknown>)) {
              const existingSub = (existingValue as Record<string, unknown>)[subKey];
              if (existingSub === undefined || existingSub === null || existingSub === "" ||
                (Array.isArray(existingSub) && existingSub.length === 0)) {
                merged[subKey] = subVal;
                changed = true;
              }
            }
            if (changed) {
              updates[field] = merged;
              newEnrichments.push({
                timestamp: now,
                source: "staging_import",
                agentName: "system",
                field,
                previousValue: JSON.stringify(existingValue),
                newValue: JSON.stringify(merged),
                confidence: "medium" as const,
                reasoning: "Deep merged missing sub-fields from staging import",
              });
            }
          } else if (stagingValue && !existingValue) {
            updates[field] = stagingValue;
            newEnrichments.push({
              timestamp: now,
              source: "staging_import",
              agentName: "system",
              field,
              previousValue: undefined,
              newValue: JSON.stringify(stagingValue),
              confidence: "medium" as const,
              reasoning: "Filled empty object field from staging import",
            });
          }
        }

        // Enrichment fields: only overwrite if existing is null/undefined
        const enrichmentFields = [
          "awarenessStage", "awarenessConfidence", "awarenessStageSource",
          "awarenessSignals", "contentPreferences", "influenceSources",
          "purchaseBehavior", "competitorContext", "sophisticationLevel",
          "communicationStyle", "seasonalContext", "negativeTriggers",
        ] as const;

        for (const field of enrichmentFields) {
          const stagingValue = staging[field];
          const existingValue = (existing as Record<string, unknown>)[field];
          if (stagingValue !== undefined && stagingValue !== null &&
            (existingValue === undefined || existingValue === null)) {
            updates[field] = stagingValue;
            newEnrichments.push({
              timestamp: now,
              source: "staging_import",
              agentName: "system",
              field,
              previousValue: undefined,
              newValue: JSON.stringify(stagingValue),
              confidence: "medium" as const,
              reasoning: "Filled null enrichment field from staging import",
            });
          }
        }

        updates.enrichments = newEnrichments;
        updates.lastEnriched = now;

        await ctx.db.patch(staging.matchedFocusGroupId, updates);
        enriched++;
      }

      // Mark staging record as imported
      await ctx.db.patch(stagingId, { reviewStatus: "imported" as const });
    }

    return { created, enriched };
  },
});
