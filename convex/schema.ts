import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({

  // ═══════════════════════════════════════════
  // USERS & AUTH
  // ═══════════════════════════════════════════

  users: defineTable({
    email: v.string(),
    name: v.string(),
    passwordHash: v.string(),
    role: v.union(v.literal("admin"), v.literal("editor"), v.literal("viewer")),
    status: v.union(v.literal("active"), v.literal("disabled")),
    lastLoginAt: v.optional(v.number()),
  }).index("by_email", ["email"]),

  sessions: defineTable({
    userId: v.id("users"),
    token: v.string(),
    expiresAt: v.number(),
    userAgent: v.optional(v.string()),
    ip: v.optional(v.string()),
  }).index("by_token", ["token"])
    .index("by_user", ["userId"]),

  // ═══════════════════════════════════════════
  // PROJECTS
  // ═══════════════════════════════════════════

  projects: defineTable({
    name: v.string(),
    slug: v.string(),
    description: v.optional(v.string()),
    appearance: v.object({
      icon: v.optional(v.string()),
      color: v.string(),
      coverImage: v.optional(v.string()),
    }),
    status: v.union(v.literal("active"), v.literal("archived")),
    stats: v.optional(v.object({
      productCount: v.number(),
      campaignCount: v.number(),
      activeCampaignCount: v.number(),
      taskCount: v.number(),
      completedTaskCount: v.number(),
      lastActivityAt: v.optional(v.number()),
    })),
    createdBy: v.optional(v.id("users")),
    createdAt: v.number(),
  }).index("by_slug", ["slug"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // PRODUCTS
  // ═══════════════════════════════════════════

  products: defineTable({
    projectId: v.id("projects"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    context: v.object({
      whatItIs: v.string(),
      features: v.array(v.string()),
      pricing: v.optional(v.string()),
      usps: v.array(v.string()),
      targetMarket: v.string(),
      website: v.optional(v.string()),
      competitors: v.array(v.string()),
    }),
    brandVoice: v.object({
      tone: v.string(),
      style: v.string(),
      vocabulary: v.object({
        preferred: v.array(v.string()),
        avoided: v.array(v.string()),
      }),
      examples: v.optional(v.string()),
      notes: v.optional(v.string()),
    }),
    status: v.union(v.literal("active"), v.literal("archived")),
  }).index("by_slug", ["slug"])
    .index("by_status", ["status"])
    .index("by_project", ["projectId"]),

  // ═══════════════════════════════════════════
  // FOCUS GROUPS
  // ═══════════════════════════════════════════

  focusGroups: defineTable({
    projectId: v.id("projects"),
    productId: v.id("products"),
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
    // Enrichment fields (populated by agents, viewed by humans)
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
    enrichments: v.optional(v.array(v.object({
      timestamp: v.number(),
      source: v.string(),
      agentName: v.string(),
      field: v.string(),
      previousValue: v.optional(v.string()),
      newValue: v.string(),
      confidence: v.union(v.literal("high"), v.literal("medium"), v.literal("low")),
      reasoning: v.string(),
    }))),
    researchNotes: v.optional(v.string()),
  }).index("by_product", ["productId"])
    .index("by_project", ["projectId"])
    .index("by_category", ["category"])
    .index("by_name", ["productId", "name"]),

  // ═══════════════════════════════════════════
  // FOCUS GROUP STAGING
  // ═══════════════════════════════════════════

  focusGroupStaging: defineTable({
    // Context
    taskId: v.id("tasks"),
    productId: v.id("products"),
    projectId: v.id("projects"),
    sourceDocumentId: v.optional(v.id("documents")),

    // Match resolution
    matchStatus: v.union(
      v.literal("create_new"),
      v.literal("enrich_existing"),
      v.literal("possible_match"),
      v.literal("skip")
    ),
    matchedFocusGroupId: v.optional(v.id("focusGroups")),
    matchConfidence: v.optional(v.number()),
    matchReason: v.optional(v.string()),

    // Review status
    reviewStatus: v.union(
      v.literal("pending_review"),
      v.literal("approved"),
      v.literal("rejected"),
      v.literal("edited"),
      v.literal("imported")
    ),
    reviewNotes: v.optional(v.string()),
    reviewedAt: v.optional(v.number()),

    // Completeness tracking
    completenessScore: v.number(),
    missingFields: v.array(v.string()),
    needsEnrichment: v.boolean(),

    // Focus group fields (most optional for staging)
    number: v.optional(v.number()),
    name: v.string(),
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
    source: v.optional(v.union(v.literal("uploaded"), v.literal("researched"), v.literal("manual"))),
    // Enrichment fields
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
    researchNotes: v.optional(v.string()),
  }).index("by_task", ["taskId"])
    .index("by_product", ["productId"])
    .index("by_project", ["projectId"])
    .index("by_review_status", ["reviewStatus"]),

  // ═══════════════════════════════════════════
  // PIPELINES
  // ═══════════════════════════════════════════

  pipelines: defineTable({
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    type: v.union(v.literal("preset"), v.literal("custom")),
    forkedFrom: v.optional(v.id("pipelines")),
    mainSteps: v.array(v.object({
      order: v.number(),
      agent: v.optional(v.string()),
      model: v.optional(v.string()),
      label: v.string(),
      description: v.optional(v.string()),
      outputDir: v.optional(v.string()),
      skillOverrides: v.optional(v.array(v.object({
        skillId: v.id("skills"),
        subSelections: v.optional(v.array(v.string())),
      }))),
    })),
    parallelBranches: v.optional(v.array(v.object({
      triggerAfterStep: v.number(),
      agent: v.string(),
      model: v.optional(v.string()),
      label: v.string(),
      description: v.optional(v.string()),
      skillOverrides: v.optional(v.array(v.object({
        skillId: v.id("skills"),
        subSelections: v.optional(v.array(v.string())),
      }))),
    }))),
    convergenceStep: v.optional(v.number()),
    onComplete: v.object({
      telegram: v.boolean(),
      summary: v.boolean(),
      generateManifest: v.boolean(),
    }),
    requiredAgentCategories: v.optional(v.array(v.string())),
  }).index("by_type", ["type"])
    .index("by_slug", ["slug"]),

  // ═══════════════════════════════════════════
  // CAMPAIGNS
  // ═══════════════════════════════════════════

  campaigns: defineTable({
    projectId: v.id("projects"),
    name: v.string(),
    slug: v.string(),
    description: v.string(),
    productId: v.id("products"),
    pipelineId: v.id("pipelines"),
    pipelineSnapshot: v.any(),
    targetFocusGroupIds: v.array(v.id("focusGroups")),
    deliverableConfig: v.optional(v.object({
      heroImage: v.optional(v.boolean()),
      socialX: v.optional(v.boolean()),
      socialLinkedIn: v.optional(v.boolean()),
      socialInstagram: v.optional(v.boolean()),
      socialFacebook: v.optional(v.boolean()),
      socialTikTok: v.optional(v.boolean()),
      socialPinterest: v.optional(v.boolean()),
      socialVK: v.optional(v.boolean()),
      emailExcerpt: v.optional(v.boolean()),
      redditVersion: v.optional(v.boolean()),
      videoScript: v.optional(v.boolean()),
      landingPage: v.optional(v.boolean()),
      emailSequence: v.optional(v.boolean()),
      leadMagnet: v.optional(v.boolean()),
      adCopySet: v.optional(v.boolean()),
      pressRelease: v.optional(v.boolean()),
      ebookFull: v.optional(v.boolean()),
    })),
    seedKeywords: v.array(v.string()),
    competitorUrls: v.array(v.string()),
    notes: v.optional(v.string()),
    skillConfig: v.optional(v.object({
      offerFramework: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      persuasionSkills: v.optional(v.array(v.object({
        skillId: v.id("skills"),
        subSelections: v.optional(v.array(v.string())),
      }))),
      primaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      secondaryCopyStyle: v.optional(v.object({
        skillId: v.id("skills"),
      })),
      agentOverrides: v.optional(v.array(v.object({
        agentName: v.string(),
        pipelineStep: v.number(),
        skillOverrides: v.array(v.object({
          skillId: v.id("skills"),
          subSelections: v.optional(v.array(v.string())),
        })),
      }))),
      summary: v.optional(v.string()),
    })),
    publishConfig: v.optional(v.object({
      cmsService: v.optional(v.string()),
      siteUrl: v.optional(v.string()),
      authorName: v.optional(v.string()),
      categoryId: v.optional(v.string()),
    })),
    status: v.union(
      v.literal("planning"),
      v.literal("active"),
      v.literal("paused"),
      v.literal("in_revision"),
      v.literal("completed")
    ),
    activatedAt: v.optional(v.number()),
    pausedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    targetArticleCount: v.optional(v.number()),
  }).index("by_slug", ["slug"])
    .index("by_product", ["productId"])
    .index("by_project", ["projectId"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // TASKS & CONTENT PIPELINE
  // ═══════════════════════════════════════════

  tasks: defineTable({
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
    pipelineStep: v.number(),
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
    lockedBy: v.optional(v.string()),
    lockedAt: v.optional(v.number()),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high"), v.literal("urgent")),
    assigneeNames: v.array(v.string()),
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
    deliverableStatus: v.optional(v.any()),
    qualityScore: v.optional(v.number()),
    readabilityScore: v.optional(v.number()),
    revisionCount: v.optional(v.number()),
    rejectionNotes: v.optional(v.string()),
    targetKeywords: v.optional(v.array(v.string())),
    focusGroupIds: v.optional(v.array(v.id("focusGroups"))),
    publishedUrl: v.optional(v.string()),
    subscriberNames: v.array(v.string()),
    metadata: v.optional(v.any()),
  }).index("by_status", ["status"])
    .index("by_campaign", ["campaignId"])
    .index("by_project", ["projectId"])
    .index("by_project_status", ["projectId", "status"])
    .index("by_priority", ["priority"]),

  // ═══════════════════════════════════════════
  // AGENTS
  // ═══════════════════════════════════════════

  agents: defineTable({
    name: v.string(),
    displayName: v.string(),
    role: v.string(),
    status: v.union(v.literal("idle"), v.literal("active"), v.literal("blocked"), v.literal("offline")),
    currentTaskId: v.optional(v.id("tasks")),
    lastHeartbeat: v.number(),
    heartbeatCron: v.string(),
    defaultModel: v.string(),
    skillPath: v.string(),
    level: v.union(v.literal("intern"), v.literal("specialist"), v.literal("lead")),
    stats: v.object({
      tasksCompleted: v.number(),
      avgQualityScore: v.optional(v.number()),
      lastActive: v.number(),
    }),
    staticSkillIds: v.array(v.id("skills")),
    dynamicSkillIds: v.array(v.id("skills")),
    agentFilePath: v.string(),
  }).index("by_name", ["name"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // SKILLS REGISTRY
  // ═══════════════════════════════════════════

  skills: defineTable({
    name: v.string(),
    slug: v.string(),
    displayName: v.string(),
    description: v.string(),
    category: v.string(),
    type: v.union(v.literal("mbook"), v.literal("procedure"), v.literal("community"), v.literal("custom")),
    isAutoActive: v.boolean(),
    isCampaignSelectable: v.boolean(),
    subSelections: v.optional(v.array(v.object({
      key: v.string(),
      label: v.string(),
      description: v.optional(v.string()),
    }))),
    categoryConstraints: v.optional(v.object({
      maxPerCampaign: v.optional(v.number()),
      selectionMode: v.optional(v.string()),
    })),
    filePath: v.string(),
    fileHash: v.optional(v.string()),
    tagline: v.optional(v.string()),
    dashboardDescription: v.optional(v.string()),
    lastSyncedAt: v.number(),
    syncStatus: v.union(
      v.literal("synced"),
      v.literal("file_missing"),
      v.literal("pending_sync"),
      v.literal("pending_setup")
    ),
  }).index("by_slug", ["slug"])
    .index("by_category", ["category"])
    .index("by_type", ["type"])
    .index("by_selectable", ["isCampaignSelectable"]),

  // ═══════════════════════════════════════════
  // SKILL CATEGORIES
  // ═══════════════════════════════════════════

  skillCategories: defineTable({
    key: v.string(),
    displayName: v.string(),
    description: v.string(),
    sortOrder: v.number(),
    scope: v.union(
      v.literal("copy"),
      v.literal("research"),
      v.literal("visual"),
      v.literal("quality"),
      v.literal("general")
    ),
    maxPerPipelineStep: v.optional(v.number()),
    selectionMode: v.optional(v.string()),
  }).index("by_key", ["key"])
    .index("by_scope", ["scope"]),

  // ═══════════════════════════════════════════
  // MESSAGES & ACTIVITIES
  // ═══════════════════════════════════════════

  messages: defineTable({
    taskId: v.id("tasks"),
    fromAgent: v.string(),
    content: v.string(),
    attachments: v.optional(v.array(v.string())),
    mentions: v.array(v.string()),
  }).index("by_task", ["taskId"]),

  activities: defineTable({
    projectId: v.optional(v.id("projects")),
    type: v.string(),
    agentName: v.string(),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    message: v.string(),
    metadata: v.optional(v.any()),
  }).index("by_type", ["type"])
    .index("by_agent", ["agentName"])
    .index("by_project", ["projectId"]),

  notifications: defineTable({
    mentionedAgent: v.string(),
    fromAgent: v.string(),
    taskId: v.optional(v.id("tasks")),
    content: v.string(),
    delivered: v.boolean(),
    deliveredAt: v.optional(v.number()),
  }).index("by_undelivered", ["mentionedAgent", "delivered"]),

  documents: defineTable({
    projectId: v.optional(v.id("projects")),
    title: v.string(),
    content: v.string(),
    type: v.union(
      v.literal("deliverable"),
      v.literal("research"),
      v.literal("brief"),
      v.literal("report"),
      v.literal("audience_doc")
    ),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    productId: v.optional(v.id("products")),
    createdBy: v.string(),
    filePath: v.optional(v.string()),
  }).index("by_task", ["taskId"])
    .index("by_type", ["type"])
    .index("by_product", ["productId"])
    .index("by_project", ["projectId"]),

  // ═══════════════════════════════════════════
  // REVISIONS
  // ═══════════════════════════════════════════

  revisions: defineTable({
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    type: v.union(v.literal("fix"), v.literal("rethink"), v.literal("extend")),
    notes: v.string(),
    agents: v.array(v.object({
      agent: v.string(),
      model: v.string(),
      order: v.number(),
    })),
    runMode: v.union(v.literal("sequential"), v.literal("parallel")),
    status: v.union(v.literal("pending"), v.literal("in_progress"), v.literal("completed")),
    agentResults: v.optional(v.any()),
    version: v.number(),
    originalFilePath: v.string(),
    revisedFilePath: v.optional(v.string()),
    requestedAt: v.number(),
    completedAt: v.optional(v.number()),
    requestedBy: v.literal("human"),
  }).index("by_task", ["taskId"])
    .index("by_campaign", ["campaignId"])
    .index("by_status", ["status"]),

  // ═══════════════════════════════════════════
  // SERVICE REGISTRY
  // ═══════════════════════════════════════════

  serviceCategories: defineTable({
    name: v.string(),
    displayName: v.string(),
    description: v.string(),
    icon: v.string(),
    sortOrder: v.number(),
  }).index("by_name", ["name"]),

  services: defineTable({
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
  }).index("by_category", ["categoryId"])
    .index("by_active", ["isActive"])
    .index("by_name", ["name"]),

  // ═══════════════════════════════════════════
  // AGENT SERVICE DEPENDENCIES
  // ═══════════════════════════════════════════

  agentServiceDeps: defineTable({
    agentName: v.string(),
    capability: v.string(),
    required: v.boolean(),
  }).index("by_agent", ["agentName"])
    .index("by_capability", ["capability"]),

  // ═══════════════════════════════════════════
  // ANALYTICS & TRACKING
  // ═══════════════════════════════════════════

  agentRuns: defineTable({
    projectId: v.optional(v.id("projects")),
    agentName: v.string(),
    campaignId: v.optional(v.id("campaigns")),
    startedAt: v.number(),
    finishedAt: v.optional(v.number()),
    durationSeconds: v.optional(v.number()),
    model: v.string(),
    status: v.union(v.literal("running"), v.literal("completed"), v.literal("failed")),
    itemsProcessed: v.optional(v.number()),
    errorLog: v.optional(v.string()),
  }).index("by_agent", ["agentName"])
    .index("by_campaign", ["campaignId"])
    .index("by_project", ["projectId"]),

  keywordClusters: defineTable({
    campaignId: v.id("campaigns"),
    primaryKeyword: v.string(),
    secondaryKeywords: v.array(v.string()),
    lsiKeywords: v.array(v.string()),
    searchVolume: v.number(),
    keywordDifficulty: v.number(),
    opportunityScore: v.number(),
    searchIntent: v.string(),
    serpAnalysis: v.optional(v.any()),
    contentBrief: v.optional(v.string()),
  }).index("by_campaign", ["campaignId"]),

  contentMetrics: defineTable({
    taskId: v.id("tasks"),
    campaignId: v.id("campaigns"),
    publishedUrl: v.optional(v.string()),
    rankings: v.optional(v.any()),
    organicTraffic: v.optional(v.number()),
    impressions: v.optional(v.number()),
    clicks: v.optional(v.number()),
    ctr: v.optional(v.number()),
    socialEngagement: v.optional(v.any()),
    emailMetrics: v.optional(v.any()),
    lastUpdated: v.number(),
  }).index("by_task", ["taskId"])
    .index("by_campaign", ["campaignId"]),

  mediaAssets: defineTable({
    projectId: v.optional(v.id("projects")),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    type: v.union(v.literal("image"), v.literal("video")),
    provider: v.string(),
    promptUsed: v.string(),
    filePath: v.string(),
    fileUrl: v.optional(v.string()),
    dimensions: v.optional(v.string()),
    generationCost: v.optional(v.number()),
  }).index("by_task", ["taskId"])
    .index("by_project", ["projectId"]),

  reports: defineTable({
    projectId: v.optional(v.id("projects")),
    type: v.union(
      v.literal("weekly_seo"),
      v.literal("weekly_content"),
      v.literal("monthly_roi"),
      v.literal("daily_standup")
    ),
    campaignId: v.optional(v.id("campaigns")),
    periodStart: v.number(),
    periodEnd: v.number(),
    data: v.any(),
    summary: v.string(),
    actionItems: v.optional(v.array(v.string())),
  }).index("by_type", ["type"])
    .index("by_project", ["projectId"]),
});
