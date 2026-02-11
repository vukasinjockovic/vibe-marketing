# Convex Backend API Catalog
**Generated:** 2026-02-11 18:20
**Location:** `/var/www/vibe-marketing/convex/`

Complete catalog of all PUBLIC API functions that the Vue dashboard can call.

---

## 1. Projects (`projects.ts`)

### Queries (read-only)

#### `projects:list`
**Args:** `{}`
**Returns:** Array of all active projects
**Purpose:** Homepage, project switcher

#### `projects:getBySlug`
**Args:** `{ slug: string }`
**Returns:** Single project or null
**Purpose:** Load project context by URL slug

### Mutations (writes)

#### `projects:create`
**Args:**
```typescript
{
  name: string
  slug: string
  description?: string
  icon?: string
  color: string
}
```
**Returns:** Project ID
**Purpose:** Create new project

#### `projects:update`
**Args:**
```typescript
{
  id: Id<"projects">
  name?: string
  description?: string
  icon?: string
  color?: string
}
```
**Returns:** void
**Purpose:** Update project metadata

#### `projects:archive`
**Args:** `{ id: Id<"projects"> }`
**Returns:** void
**Purpose:** Archive project (soft delete)

#### `projects:updateStats`
**Args:**
```typescript
{
  id: Id<"projects">
  stats: {
    productCount: number
    campaignCount: number
    activeCampaignCount: number
    taskCount: number
    completedTaskCount: number
    lastActivityAt?: number
  }
}
```
**Returns:** void
**Purpose:** Update denormalized counts (called by agents)

---

## 2. Products (`products.ts`)

### Queries

#### `products:list`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of products for project
**Purpose:** Products page, campaign setup

#### `products:get`
**Args:** `{ id: Id<"products"> }`
**Returns:** Single product
**Purpose:** Product detail view

#### `products:getBySlug`
**Args:** `{ slug: string }`
**Returns:** Single product or null
**Purpose:** Load by URL slug

### Mutations

#### `products:create`
**Args:**
```typescript
{
  projectId: Id<"projects">
  name: string
  slug: string
  description: string
  context: {
    whatItIs: string
    features: string[]
    pricing?: string
    usps: string[]
    targetMarket: string
    website?: string
    competitors: string[]
  }
  brandVoice: {
    tone: string
    style: string
    vocabulary: {
      preferred: string[]
      avoided: string[]
    }
    examples?: string
    notes?: string
  }
}
```
**Returns:** Product ID
**Purpose:** Create new product

#### `products:update`
**Args:** Same as create, all optional except `id`
**Returns:** void
**Purpose:** Update product

#### `products:archive`
**Args:** `{ id: Id<"products"> }`
**Returns:** void
**Purpose:** Archive product

---

## 3. Focus Groups (`focusGroups.ts`)

### Queries

#### `focusGroups:listByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of focus groups
**Purpose:** Audiences page

#### `focusGroups:listByProduct`
**Args:** `{ productId: Id<"products"> }`
**Returns:** Array of focus groups for product
**Purpose:** Product → audiences view

#### `focusGroups:get`
**Args:** `{ id: Id<"focusGroups"> }`
**Returns:** Single focus group
**Purpose:** Audience detail view

#### `focusGroups:getByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of focus groups targeted by campaign
**Purpose:** Campaign detail view

### Mutations

#### `focusGroups:create`
**Args:**
```typescript
{
  projectId: Id<"projects">
  productId: Id<"products">
  number: number
  name: string
  nickname: string
  category: string
  overview: string
  demographics: {
    ageRange: string
    gender: string
    income: string
    lifestyle: string
    triggers: string[]
  }
  psychographics: {
    values: string[]
    beliefs: string[]
    lifestyle: string
    identity: string
  }
  coreDesires: string[]
  painPoints: string[]
  fears: string[]
  beliefs: string[]
  objections: string[]
  emotionalTriggers: string[]
  languagePatterns: string[]
  ebookAngles: string[]
  marketingHooks: string[]
  transformationPromise: string
  source: "uploaded" | "researched" | "manual"
  lastEnriched?: number
  enrichmentNotes?: string
}
```
**Returns:** Focus group ID
**Purpose:** Create audience segment

#### `focusGroups:update`
**Args:** Same as create, all optional except `id`
**Returns:** void
**Purpose:** Update focus group

#### `focusGroups:remove`
**Args:** `{ id: Id<"focusGroups"> }`
**Returns:** void
**Purpose:** Delete focus group (hard delete)

---

## 4. Campaigns (`campaigns.ts`)

### Queries

#### `campaigns:list`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of campaigns
**Purpose:** Campaigns page

#### `campaigns:get`
**Args:** `{ id: Id<"campaigns"> }`
**Returns:** Single campaign
**Purpose:** Campaign detail view

#### `campaigns:getBySlug`
**Args:** `{ slug: string }`
**Returns:** Single campaign or null
**Purpose:** Load by URL slug

#### `campaigns:listActive`
**Args:** `{}`
**Returns:** All active campaigns (cross-project)
**Purpose:** Global active work view

### Mutations

#### `campaigns:create`
**Args:**
```typescript
{
  projectId: Id<"projects">
  name: string
  slug: string
  description: string
  productId: Id<"products">
  pipelineId: Id<"pipelines">
  pipelineSnapshot: any  // Frozen copy of pipeline config
  targetFocusGroupIds: Id<"focusGroups">[]
  deliverableConfig?: {
    heroImage?: boolean
    socialX?: boolean
    socialLinkedIn?: boolean
    socialInstagram?: boolean
    socialFacebook?: boolean
    socialTikTok?: boolean
    socialPinterest?: boolean
    socialVK?: boolean
    emailExcerpt?: boolean
    redditVersion?: boolean
    videoScript?: boolean
    landingPage?: boolean
    emailSequence?: boolean
    leadMagnet?: boolean
    adCopySet?: boolean
    pressRelease?: boolean
    ebookFull?: boolean
  }
  seedKeywords: string[]
  competitorUrls: string[]
  notes?: string
  skillConfig?: {
    offerFramework?: { skillId: Id<"skills"> }
    persuasionSkills?: { skillId: Id<"skills">, subSelections?: string[] }[]
    primaryCopyStyle?: { skillId: Id<"skills"> }
    secondaryCopyStyle?: { skillId: Id<"skills"> }
    agentOverrides?: {
      agentName: string
      pipelineStep: number
      skillOverrides: { skillId: Id<"skills">, subSelections?: string[] }[]
    }[]
    summary?: string
  }
  publishConfig?: {
    cmsService?: string
    siteUrl?: string
    authorName?: string
    categoryId?: string
  }
  targetArticleCount?: number
}
```
**Returns:** Campaign ID
**Purpose:** Create new campaign

#### `campaigns:update`
**Args:** Same as create, all optional except `id`
**Returns:** void
**Purpose:** Update campaign

#### `campaigns:activate`
**Args:** `{ id: Id<"campaigns"> }`
**Returns:** void
**Purpose:** Start campaign (status = active, set activatedAt)

#### `campaigns:pause`
**Args:** `{ id: Id<"campaigns"> }`
**Returns:** void
**Purpose:** Pause campaign (status = paused, set pausedAt)

#### `campaigns:complete`
**Args:** `{ id: Id<"campaigns"> }`
**Returns:** void
**Purpose:** Complete campaign (status = completed, set completedAt)

---

## 5. Tasks (`tasks.ts`)

### Queries

#### `tasks:listByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of tasks
**Purpose:** Project task board

#### `tasks:listByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of tasks
**Purpose:** Campaign task board

#### `tasks:listByStatus`
**Args:**
```typescript
{
  projectId: Id<"projects">
  status: "backlog" | "researched" | "briefed" | "drafted" | "reviewed" 
    | "revision_needed" | "humanized" | "completed" | "cancelled" | "blocked"
}
```
**Returns:** Array of tasks
**Purpose:** Filtered task lists

#### `tasks:get`
**Args:** `{ id: Id<"tasks"> }`
**Returns:** Single task
**Purpose:** Task detail view

### Mutations

#### `tasks:create`
**Args:**
```typescript
{
  projectId: Id<"projects">
  title: string
  description: string
  campaignId?: Id<"campaigns">
  pipeline: {
    step: number
    status: string
    agent?: string
    model?: string
    description: string
    outputDir?: string
  }[]
  priority: "low" | "medium" | "high" | "urgent"
  createdBy: string
  contentType?: string
  contentSlug?: string
  contentBrief?: string
  deliverables?: {
    blogPost?: boolean
    heroImage?: boolean
    socialX?: boolean
    socialLinkedIn?: boolean
    socialInstagram?: boolean
    socialFacebook?: boolean
    emailExcerpt?: boolean
    redditVersion?: boolean
    videoScript?: boolean
  }
  targetKeywords?: string[]
  focusGroupIds?: Id<"focusGroups">[]
  metadata?: any
}
```
**Returns:** Task ID
**Purpose:** Create new task

#### `tasks:update`
**Args:** Same as create, all optional except `id`
**Returns:** void
**Purpose:** Update task

#### `tasks:updateStatus`
**Args:**
```typescript
{
  id: Id<"tasks">
  status: "backlog" | "researched" | "briefed" | "drafted" | "reviewed" 
    | "revision_needed" | "humanized" | "completed" | "cancelled" | "blocked"
}
```
**Returns:** void
**Purpose:** Change task status (usually done via pipeline, not directly)

#### `tasks:assignAgent`
**Args:** `{ id: Id<"tasks">, agentName: string }`
**Returns:** void
**Purpose:** Assign agent to task (sets lock)

#### `tasks:unassign`
**Args:** `{ id: Id<"tasks"> }`
**Returns:** void
**Purpose:** Clear lock

#### `tasks:subscribe`
**Args:** `{ id: Id<"tasks">, agentName: string }`
**Returns:** void
**Purpose:** Subscribe agent to task notifications

#### `tasks:unsubscribe`
**Args:** `{ id: Id<"tasks">, agentName: string }`
**Returns:** void
**Purpose:** Unsubscribe agent

---

## 6. Pipeline (`pipeline.ts`)

Pipeline execution functions. Agents use these to advance tasks.

### Queries

#### `pipeline:getTaskPipelineStatus`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:**
```typescript
{
  _id: Id<"tasks">
  title: string
  status: string
  pipelineStep: number
  pipeline: { step: number, status: string, agent?: string, ... }[]
  lockedBy?: string
  lockedAt?: number
  qualityScore?: number
  revisionCount?: number
  rejectionNotes?: string
}
```
**Purpose:** Dashboard pipeline status view

#### `pipeline:listReadyTasks`
**Args:** `{ projectId?: Id<"projects"> }`
**Returns:** Array of tasks available for agents (not locked, not terminal)
**Purpose:** Agent task picker, work queue

### Mutations

#### `pipeline:acquireLock`
**Args:** `{ taskId: Id<"tasks">, agentName: string }`
**Returns:** `{ acquired: boolean, lockedBy?: string }`
**Purpose:** Agent locks task before work (10min stale timeout)

#### `pipeline:releaseLock`
**Args:** `{ taskId: Id<"tasks">, agentName: string }`
**Returns:** `{ released: boolean, reason?: string }`
**Purpose:** Agent releases lock after work

#### `pipeline:completeStep`
**Args:**
```typescript
{
  taskId: Id<"tasks">
  agentName: string
  qualityScore?: number
  outputPath?: string
}
```
**Returns:** `{ completed: boolean, nextStep: number | null, newStatus: string }`
**Purpose:** Agent completes current step, advances to next (THE ONLY WAY to advance tasks)

#### `pipeline:requestRevision`
**Args:**
```typescript
{
  taskId: Id<"tasks">
  notes: string
  targetStep: number
}
```
**Returns:** `{ revised: boolean }`
**Purpose:** Send task back to earlier step (human or agent)

---

## 7. Pipelines (`pipelines.ts`)

Pipeline templates and presets.

### Queries

#### `pipelines:list`
**Args:** `{}`
**Returns:** Array of all pipelines
**Purpose:** Pipeline management page

#### `pipelines:listPresets`
**Args:** `{}`
**Returns:** Array of preset pipelines (type = "preset")
**Purpose:** Campaign setup wizard

#### `pipelines:get`
**Args:** `{ id: Id<"pipelines"> }`
**Returns:** Single pipeline
**Purpose:** Pipeline detail view

#### `pipelines:getBySlug`
**Args:** `{ slug: string }`
**Returns:** Single pipeline or null
**Purpose:** Load by URL slug

### Mutations

#### `pipelines:create`
**Args:**
```typescript
{
  name: string
  slug: string
  description: string
  type: "preset" | "custom"
  forkedFrom?: Id<"pipelines">
  mainSteps: {
    order: number
    agent?: string
    model?: string
    label: string
    description?: string
    outputDir?: string
    skillOverrides?: { skillId: Id<"skills">, subSelections?: string[] }[]
  }[]
  parallelBranches?: {
    triggerAfterStep: number
    agent: string
    model?: string
    label: string
    description?: string
    skillOverrides?: { skillId: Id<"skills">, subSelections?: string[] }[]
  }[]
  convergenceStep?: number
  onComplete: {
    telegram: boolean
    summary: boolean
    generateManifest: boolean
  }
  requiredAgentCategories?: string[]
}
```
**Returns:** Pipeline ID
**Purpose:** Create custom pipeline

#### `pipelines:fork`
**Args:**
```typescript
{
  pipelineId: Id<"pipelines">
  newName: string
  newSlug: string
}
```
**Returns:** New pipeline ID
**Purpose:** Fork preset into custom copy

---

## 8. Agents (`agents.ts`)

Agent registry and status.

### Queries

#### `agents:list`
**Args:** `{}`
**Returns:** Array of all agents
**Purpose:** Agents dashboard

#### `agents:get`
**Args:** `{ id: Id<"agents"> }`
**Returns:** Single agent
**Purpose:** Agent detail view

#### `agents:getByName`
**Args:** `{ name: string }`
**Returns:** Single agent or null
**Purpose:** Lookup agent by name

#### `agents:listActive`
**Args:** `{}`
**Returns:** Array of agents with status "active" or "idle"
**Purpose:** Available agents view

### Mutations

#### `agents:register`
**Args:**
```typescript
{
  name: string
  displayName: string
  role: string
  heartbeatCron: string
  defaultModel: string
  skillPath: string
  level: "intern" | "specialist" | "lead"
  agentFilePath: string
  status?: "idle" | "active" | "blocked" | "offline"
  staticSkillIds?: Id<"skills">[]
  dynamicSkillIds?: Id<"skills">[]
}
```
**Returns:** Agent ID
**Purpose:** Register new agent (usually done by setup script)

#### `agents:heartbeat`
**Args:** `{ name: string }`
**Returns:** void
**Purpose:** Update lastHeartbeat timestamp (agent keepalive)

#### `agents:updateStatus`
**Args:** `{ id: Id<"agents">, status: "idle" | "active" | "blocked" | "offline" }`
**Returns:** void
**Purpose:** Change agent status

#### `agents:assignTask`
**Args:** `{ id: Id<"agents">, taskId: Id<"tasks"> }`
**Returns:** void
**Purpose:** Assign task to agent (sets currentTaskId, status = active)

#### `agents:completeTask`
**Args:** `{ id: Id<"agents"> }`
**Returns:** void
**Purpose:** Clear currentTaskId, increment tasksCompleted, status = idle

---

## 9. Messages (`messages.ts`)

Task-scoped message thread (agent-to-agent or agent-to-human).

### Queries

#### `messages:listByTask`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:** Array of messages
**Purpose:** Task message thread view

### Mutations

#### `messages:create`
**Args:**
```typescript
{
  taskId: Id<"tasks">
  fromAgent: string
  content: string
  mentions?: string[]  // Agent names
  attachments?: string[]  // File paths
}
```
**Returns:** Message ID
**Purpose:** Post message to task thread

---

## 10. Activities (`activities.ts`)

Activity log (audit trail).

### Queries

#### `activities:list`
**Args:** `{}`
**Returns:** Latest 50 activities (newest first)
**Purpose:** Global activity feed

#### `activities:listByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Latest 50 activities for project
**Purpose:** Project activity feed

#### `activities:listByAgent`
**Args:** `{ agentName: string }`
**Returns:** Latest 50 activities by agent
**Purpose:** Agent activity history

### Mutations

#### `activities:log`
**Args:**
```typescript
{
  projectId?: Id<"projects">
  type: string
  agentName: string
  taskId?: Id<"tasks">
  campaignId?: Id<"campaigns">
  message: string
  metadata?: any
}
```
**Returns:** Activity ID
**Purpose:** Log activity (called by agents)

---

## 11. Notifications (`notifications.ts`)

Agent @mentions and notifications.

### Queries

#### `notifications:listUndelivered`
**Args:** `{ mentionedAgent: string }`
**Returns:** Array of undelivered notifications
**Purpose:** Agent notification polling

### Mutations

#### `notifications:create`
**Args:**
```typescript
{
  mentionedAgent: string
  fromAgent: string
  taskId?: Id<"tasks">
  content: string
}
```
**Returns:** Notification ID
**Purpose:** Send notification to agent

#### `notifications:markDelivered`
**Args:** `{ id: Id<"notifications"> }`
**Returns:** void
**Purpose:** Mark single notification as delivered

#### `notifications:markAllDelivered`
**Args:** `{ mentionedAgent: string }`
**Returns:** void
**Purpose:** Mark all notifications for agent as delivered

---

## 12. Documents (`documents.ts`)

Artifact storage (research reports, briefs, etc).

### Queries

#### `documents:listByTask`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:** Array of documents
**Purpose:** Task artifacts view

#### `documents:listByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of documents
**Purpose:** Project documents library

#### `documents:listByType`
**Args:** `{ type: "deliverable" | "research" | "brief" | "report" | "audience_doc" }`
**Returns:** Array of documents
**Purpose:** Filtered document lists

#### `documents:get`
**Args:** `{ id: Id<"documents"> }`
**Returns:** Single document
**Purpose:** Document detail view

### Mutations

#### `documents:create`
**Args:**
```typescript
{
  projectId?: Id<"projects">
  title: string
  content: string
  type: "deliverable" | "research" | "brief" | "report" | "audience_doc"
  taskId?: Id<"tasks">
  campaignId?: Id<"campaigns">
  productId?: Id<"products">
  createdBy: string
  filePath?: string
}
```
**Returns:** Document ID
**Purpose:** Store document

#### `documents:update`
**Args:** `{ id: Id<"documents">, title?: string, content?: string, filePath?: string }`
**Returns:** void
**Purpose:** Update document

#### `documents:remove`
**Args:** `{ id: Id<"documents"> }`
**Returns:** void
**Purpose:** Delete document

---

## 13. Revisions (`revisions.ts`)

Revision requests (human asks for rework).

### Queries

#### `revisions:listByTask`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:** Array of revisions
**Purpose:** Task revision history

#### `revisions:listByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of revisions
**Purpose:** Campaign revision history

#### `revisions:get`
**Args:** `{ id: Id<"revisions"> }`
**Returns:** Single revision
**Purpose:** Revision detail view

### Mutations

#### `revisions:create`
**Args:**
```typescript
{
  taskId: Id<"tasks">
  campaignId: Id<"campaigns">
  type: "fix" | "rethink" | "extend"
  notes: string
  agents: { agent: string, model: string, order: number }[]
  runMode: "sequential" | "parallel"
  version: number
  originalFilePath: string
  requestedBy: "human"
  status?: "pending" | "in_progress" | "completed"
  requestedAt?: number
}
```
**Returns:** Revision ID
**Purpose:** Request revision

#### `revisions:start`
**Args:** `{ id: Id<"revisions"> }`
**Returns:** void
**Purpose:** Mark revision as in progress

#### `revisions:complete`
**Args:** `{ id: Id<"revisions">, revisedFilePath: string }`
**Returns:** void
**Purpose:** Mark revision as completed

---

## 14. Services (`services.ts`)

External service registry.

### Queries

#### `services:listCategories`
**Args:** `{}`
**Returns:** Array of service categories (sorted by sortOrder)
**Purpose:** Service registry page

#### `services:listByCategory`
**Args:** `{ categoryId: Id<"serviceCategories"> }`
**Returns:** Array of services
**Purpose:** Category detail view

#### `services:listActive`
**Args:** `{}`
**Returns:** Array of active services
**Purpose:** Service status dashboard

#### `services:get`
**Args:** `{ id: Id<"services"> }`
**Returns:** Single service
**Purpose:** Service detail view

#### `services:resolve`
**Args:** `{ categoryName: string }`
**Returns:** Highest-priority active service for category or null
**Purpose:** Agent service resolution

### Mutations

#### `services:create`
**Args:**
```typescript
{
  categoryId: Id<"serviceCategories">
  subcategory?: string
  name: string
  displayName: string
  description: string
  isActive: boolean
  priority: number
  apiKeyEnvVar: string
  apiKeyConfigured: boolean
  apiKeyValue?: string
  extraConfig?: string
  scriptPath: string
  mcpServer?: string
  costInfo: string
  useCases: string[]
  docsUrl?: string
}
```
**Returns:** Service ID
**Purpose:** Add service

#### `services:update`
**Args:**
```typescript
{
  id: Id<"services">
  isActive?: boolean
  priority?: number
  apiKeyConfigured?: boolean
  apiKeyValue?: string
  extraConfig?: string
}
```
**Returns:** void
**Purpose:** Update service config

#### `services:toggleActive`
**Args:** `{ id: Id<"services"> }`
**Returns:** void
**Purpose:** Toggle service on/off

---

## 15. Analytics (`analytics.ts`)

Agent runs, keyword clusters, content metrics, media assets, reports.

### Agent Runs

#### `analytics:listRunsByAgent`
**Args:** `{ agentName: string }`
**Returns:** Array of agent runs

#### `analytics:listRunsByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of agent runs

#### `analytics:startRun`
**Args:** `{ projectId?: Id<"projects">, agentName: string, campaignId?: Id<"campaigns">, model: string }`
**Returns:** Run ID

#### `analytics:completeRun`
**Args:** `{ id: Id<"agentRuns">, itemsProcessed?: number }`
**Returns:** void

#### `analytics:failRun`
**Args:** `{ id: Id<"agentRuns">, errorLog?: string }`
**Returns:** void

### Keyword Clusters

#### `analytics:listKeywordsByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of keyword clusters

#### `analytics:createKeywordCluster`
**Args:**
```typescript
{
  campaignId: Id<"campaigns">
  primaryKeyword: string
  secondaryKeywords: string[]
  lsiKeywords: string[]
  searchVolume: number
  keywordDifficulty: number
  opportunityScore: number
  searchIntent: string
  serpAnalysis?: any
  contentBrief?: string
}
```
**Returns:** Cluster ID

#### `analytics:updateKeywordCluster`
**Args:** Same as create, all optional except `id`
**Returns:** void

### Content Metrics

#### `analytics:getMetricsByTask`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:** Single content metrics record (unique per task)

#### `analytics:listMetricsByCampaign`
**Args:** `{ campaignId: Id<"campaigns"> }`
**Returns:** Array of content metrics

#### `analytics:upsertMetrics`
**Args:**
```typescript
{
  taskId: Id<"tasks">
  campaignId: Id<"campaigns">
  publishedUrl?: string
  rankings?: any
  organicTraffic?: number
  impressions?: number
  clicks?: number
  ctr?: number
  socialEngagement?: any
  emailMetrics?: any
}
```
**Returns:** Metrics ID
**Purpose:** Update or insert metrics

### Media Assets

#### `analytics:listAssetsByTask`
**Args:** `{ taskId: Id<"tasks"> }`
**Returns:** Array of media assets

#### `analytics:listAssetsByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of media assets

#### `analytics:createAsset`
**Args:**
```typescript
{
  projectId?: Id<"projects">
  taskId?: Id<"tasks">
  campaignId?: Id<"campaigns">
  type: "image" | "video"
  provider: string
  promptUsed: string
  filePath: string
  fileUrl?: string
  dimensions?: string
  generationCost?: number
}
```
**Returns:** Asset ID

#### `analytics:deleteAsset`
**Args:** `{ id: Id<"mediaAssets"> }`
**Returns:** void

### Reports

#### `analytics:listReportsByProject`
**Args:** `{ projectId: Id<"projects"> }`
**Returns:** Array of reports

#### `analytics:listReportsByType`
**Args:** `{ type: "weekly_seo" | "weekly_content" | "monthly_roi" | "daily_standup" }`
**Returns:** Array of reports

#### `analytics:createReport`
**Args:**
```typescript
{
  projectId?: Id<"projects">
  type: "weekly_seo" | "weekly_content" | "monthly_roi" | "daily_standup"
  campaignId?: Id<"campaigns">
  periodStart: number
  periodEnd: number
  data: any
  summary: string
  actionItems?: string[]
}
```
**Returns:** Report ID

#### `analytics:getReport`
**Args:** `{ id: Id<"reports"> }`
**Returns:** Single report

---

## 16. Auth (`auth.ts`)

Authentication (email/password + session tokens).

### Actions (Node.js runtime)

#### `auth:signIn`
**Args:** `{ email: string, password: string }`
**Returns:**
```typescript
{
  token: string
  user: { _id: Id<"users">, email: string, name: string, role: string }
}
```
**Purpose:** Login (runs bcrypt in Node.js)

### Queries

#### `auth:validateSession`
**Args:** `{ token: string }`
**Returns:** User object or null
**Purpose:** Check if session token is valid

#### `auth:me`
**Args:** `{ token: string }`
**Returns:** Current user or null
**Purpose:** Get current user info

### Mutations

#### `auth:signOut`
**Args:** `{ token: string }`
**Returns:** void
**Purpose:** Logout (deletes session)

### Internal Functions (NOT public)

- `auth:getUserByEmail` (internalQuery)
- `auth:createSession` (internalMutation)

---

## 17. Admin (`admin.ts`)

User management (internal only - called by setup scripts).

### Internal Actions (NOT public)

#### `admin:createUser`
**Args:** `{ email: string, name: string, password: string, role: "admin" | "editor" | "viewer" }`
**Returns:** User ID
**Purpose:** Create user (hashes password with bcrypt)

### Internal Mutations (NOT public)

- `admin:insertUser` (internalMutation)

---

## 18. Seed (`seed.ts`)

Database initialization (internal only).

### Internal Mutations (NOT public)

#### `seed:run`
**Args:** `{}`
**Returns:** Array of strings (what was seeded)
**Purpose:** Seed service categories, skill categories, preset pipelines (idempotent)

---

## Summary: Function Counts by File

| File | Queries | Mutations | Actions | Internal | Total Public |
|------|---------|-----------|---------|----------|--------------|
| projects.ts | 2 | 4 | 0 | 0 | 6 |
| products.ts | 3 | 3 | 0 | 0 | 6 |
| focusGroups.ts | 4 | 3 | 0 | 0 | 7 |
| campaigns.ts | 4 | 5 | 0 | 0 | 9 |
| tasks.ts | 4 | 7 | 0 | 0 | 11 |
| pipeline.ts | 2 | 4 | 0 | 0 | 6 |
| pipelines.ts | 4 | 2 | 0 | 0 | 6 |
| agents.ts | 4 | 5 | 0 | 0 | 9 |
| messages.ts | 1 | 1 | 0 | 0 | 2 |
| activities.ts | 3 | 1 | 0 | 0 | 4 |
| notifications.ts | 1 | 3 | 0 | 0 | 4 |
| documents.ts | 4 | 3 | 0 | 0 | 7 |
| revisions.ts | 3 | 3 | 0 | 0 | 6 |
| services.ts | 5 | 3 | 0 | 0 | 8 |
| analytics.ts | 10 | 9 | 0 | 0 | 19 |
| auth.ts | 2 | 1 | 1 | 2 | 4 |
| admin.ts | 0 | 0 | 0 | 2 | 0 |
| seed.ts | 0 | 0 | 0 | 1 | 0 |
| **TOTAL** | **56** | **57** | **1** | **5** | **114** |

---

## Dashboard Integration Notes

### Authentication Flow
1. Dashboard calls `auth:signIn` → gets token
2. Store token in localStorage or cookie
3. Include token in all subsequent calls
4. Use `auth:validateSession` or `auth:me` to check if still valid
5. Call `auth:signOut` on logout

### Typical Dashboard Pages

**Homepage**
- `projects:list` → show all projects
- `campaigns:listActive` → show active campaigns across all projects

**Project Detail**
- `projects:getBySlug` → load project
- `campaigns:list` → campaigns for project
- `products:list` → products for project
- `focusGroups:listByProject` → audiences for project
- `tasks:listByProject` → all tasks
- `activities:listByProject` → activity feed

**Campaign Detail**
- `campaigns:get` → campaign info
- `tasks:listByCampaign` → campaign tasks
- `focusGroups:getByCampaign` → target audiences
- `analytics:listKeywordsByCampaign` → keyword research
- `analytics:listMetricsByCampaign` → performance metrics

**Task Detail**
- `tasks:get` → task info
- `pipeline:getTaskPipelineStatus` → pipeline status
- `messages:listByTask` → task thread
- `documents:listByTask` → task artifacts
- `revisions:listByTask` → revision history

**Settings**
- `agents:list` → all agents
- `pipelines:list` → all pipelines
- `services:listCategories` + `services:listByCategory` → service registry

### Real-time Updates
Convex supports subscriptions. Dashboard can subscribe to queries:
```typescript
const tasks = useQuery(api.tasks.listByCampaign, { campaignId })
// Auto-updates when data changes
```

---

## Key Design Patterns

1. **Project-scoped data**: Most entities have `projectId`
2. **Pipeline contract**: Only `pipeline:completeStep` advances tasks
3. **Locking**: `pipeline:acquireLock` prevents concurrent work (10min stale timeout)
4. **Denormalized stats**: Projects store counts (updated by agents)
5. **Slugs**: Most entities have slugs for URL routing
6. **Internal functions**: Auth/admin use internal functions for security
7. **Idempotent seed**: `seed:run` can be called multiple times safely

---

## Next Steps for Dashboard

1. **Auth pages**: Login form → `auth:signIn` → store token
2. **Project list**: Homepage → `projects:list`
3. **Campaign board**: Kanban → `tasks:listByCampaign` + `tasks:updateStatus`
4. **Pipeline viewer**: Visual pipeline → `pipeline:getTaskPipelineStatus`
5. **Service config**: Settings → `services:listCategories` + `services:update`
6. **Agent dashboard**: Agent status → `agents:list` + live heartbeats

