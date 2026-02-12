# Notification & Activities Investigation Report
Generated: 2026-02-12

## Summary

**Issue 1: No in-app notifications during pipeline progression**
- VERIFIED: Notifications infrastructure exists but is NOT triggered during pipeline execution
- `pipeline:completeStep` does NOT create notifications
- `orchestrator.*` functions do NOT create notifications
- Only documented usage is manual `npx convex run notifications:create` for agent-to-agent communication

**Issue 2: Activities page shows nothing**
- VERIFIED: Activities page is correctly wired and queries `activities:list`
- PROBLEM: Agents are NOT actually logging activities during execution
- Only error cases in `invoke-agent.sh` log activities
- No success/completion activity logging exists

---

## Question 1: Are notifications created during pipeline progression?

**NO** (VERIFIED)

### Evidence

#### File: `/var/www/vibe-marketing/convex/notifications.ts` (144 lines)
**Functions:**
- `listForDashboard` - query for @human/@all notifications
- `countUnread` - count unread notifications
- `markAllRead` - mark all as read for user
- `listUndelivered` - query for agent notifications
- `create` - **MUTATION to create notifications**
- `markDelivered` - mark single notification delivered
- `markAllDelivered` - bulk mark delivered

**Create function signature:**
```typescript
export const create = mutation({
  args: {
    mentionedAgent: v.string(),
    fromAgent: v.string(),
    taskId: v.optional(v.id("tasks")),
    content: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("notifications", { ... });
  },
});
```

#### File: `/var/www/vibe-marketing/convex/pipeline.ts` (409 lines)
**completeStep function (lines 94-260):**
- Updates task status
- Advances pipeline step
- Dispatches next agent via `internal.orchestrator.requestDispatch`
- Handles parallel branches
- **DOES NOT call notifications:create**
- **DOES NOT create any notifications**

Key section:
```typescript
// completeStep — Advance task through its pipeline
export const completeStep = mutation({
  args: { taskId, agentName, qualityScore, outputPath },
  handler: async (ctx, args) => {
    // ... updates task status
    // ... advances pipeline
    // ... dispatches next agent
    // NO NOTIFICATION CREATION
  }
});
```

#### File: `/var/www/vibe-marketing/convex/orchestrator.ts` (226 lines)
**Functions:**
- `requestDispatch` - dispatch agent via invoke-agent.sh
- `requestBranchDispatch` - dispatch parallel branches
- `dispatchNextTask` - dispatch next campaign task
- `checkCampaignCompletion` - check if campaign done
- `pauseCampaign` - pause campaign
- `resumeCampaign` - resume campaign

**NONE of these create notifications**

#### Grep Results: `notifications:create` usage
Only 3 occurrences:
1. `/var/www/vibe-marketing/CLAUDE.md:102` - documentation
2. `CONVEX_API_CATALOG.md:743` - documentation
3. `/var/www/vibe-marketing/vibe-marketing-platform-v3.md:1086` - documentation

**NO ACTUAL USAGE in code**

### Dashboard Implementation

#### File: `/var/www/vibe-marketing/dashboard/layouts/default.vue`
- **VERIFIED**: Has `<NotificationDropdown />` component in topbar
- Shows bell icon with unread count badge

#### File: `/var/www/vibe-marketing/dashboard/components/NotificationDropdown.vue`
- Uses `useNotifications()` composable
- Shows unread count badge
- Dropdown with notification list
- "Mark all read" button

#### File: `/var/www/vibe-marketing/dashboard/composables/useNotifications.ts`
- Queries `api.notifications.listForDashboard`
- Queries `api.notifications.countUnread`
- Both require user token (session-based)
- Filters for `@human` and `@all` mentions only

**Conclusion:** Dashboard notification UI is fully implemented and working. The problem is that **no notifications are ever created** during pipeline execution.

---

## Question 2: Why is the Activities page empty?

**Agents are NOT logging activities** (VERIFIED)

### Evidence

#### File: `/var/www/vibe-marketing/convex/activities.ts` (56 lines)
**Functions:**
- `list` - query latest 50 activities (NO ARGS, just ordered desc)
- `listByProject` - query by projectId
- `listByAgent` - query by agentName
- `log` - **MUTATION to create activity**

**Log function signature:**
```typescript
export const log = mutation({
  args: {
    projectId: v.optional(v.id("projects")),
    type: v.string(),
    agentName: v.string(),
    taskId: v.optional(v.id("tasks")),
    campaignId: v.optional(v.id("campaigns")),
    message: v.string(),
    metadata: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("activities", { ... });
  },
});
```

#### File: `/var/www/vibe-marketing/dashboard/pages/activity.vue`
**VERIFIED: Correctly implemented**
- Uses `useConvexQuery(api.activities.list, {})`
- Shows empty state when no activities
- Renders activity cards with type color, agentName, message
- No issues with the page implementation

#### Grep Results: `activities:log` usage
Found in:
1. `CLAUDE.md` - documentation (lines 93, 107)
2. `vibe-marketing-platform-v3.md` - documentation
3. `scripts/invoke-agent.sh` - **ONLY error logging**:
   - Line 63: Skill directory not found error
   - Line 104: Agent crashed error
   - Line 120: Heartbeat crashed error
4. Skill SKILL.md files - documentation/examples only

**NO success/completion logging exists**

#### File: `/var/www/vibe-marketing/scripts/invoke-agent.sh`
**Only 3 activities:log calls (all errors):**

```bash
# Line 63 - Skill not found
npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"message\":\"Skill directory not found: ${SKILL_DIR}\"}"

# Line 104 - Agent crash
npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"taskId\":\"${TASK_ID}\",\"message\":\"Agent crashed with exit code ${EXIT_CODE}\"}"

# Line 120 - Heartbeat crash
npx convex run activities:log "{\"type\":\"error\",\"agentName\":\"${AGENT_NAME}\",\"message\":\"Heartbeat crashed with exit code ${EXIT_CODE}\"}"
```

**NO logging for:**
- Agent started
- Agent acquired lock
- Agent completed step
- Agent released lock
- Step advanced
- Status changed
- Quality score recorded

**Conclusion:** The activities page works correctly. The problem is that **agents don't log their activities** during normal execution—only errors are logged.

---

## What's Missing

### For Notifications

**Pipeline completion notifications:**
1. Add to `pipeline:completeStep` after status update:
```typescript
// Notify @human when task completes
if (newStatus === "completed") {
  await ctx.db.insert("notifications", {
    mentionedAgent: "@human",
    fromAgent: "vibe-pipeline",
    taskId: args.taskId,
    content: `Task completed: ${task.title || 'Untitled'}`,
    delivered: false,
  });
}
```

**Pipeline progression notifications:**
2. Add to `pipeline:completeStep` when advancing steps:
```typescript
if (hasNextStep) {
  const nextStep = pipeline[nextStepIndex];
  await ctx.db.insert("notifications", {
    mentionedAgent: "@human",
    fromAgent: "vibe-pipeline",
    taskId: args.taskId,
    content: `Task advanced to ${nextStep.step} (${nextStep.agent})`,
    delivered: false,
  });
}
```

**Campaign notifications:**
3. Add to `orchestrator:checkCampaignCompletion`:
```typescript
await ctx.db.insert("notifications", {
  mentionedAgent: "@human",
  fromAgent: "vibe-orchestrator",
  content: `Campaign "${campaign.name}" completed`,
  delivered: false,
});
```

### For Activities

**Add to `pipeline:completeStep`:**
```typescript
// Log activity after successful step completion
await ctx.db.insert("activities", {
  projectId: task.projectId,
  type: "complete",
  agentName: args.agentName,
  taskId: args.taskId,
  campaignId: task.campaignId,
  message: `Completed ${pipeline[currentStepIndex].step}${hasNextStep ? `, advancing to ${pipeline[nextStepIndex].step}` : ', task finished'}`,
  metadata: { qualityScore: args.qualityScore },
});
```

**Add to `pipeline:acquireLock`:**
```typescript
await ctx.db.insert("activities", {
  projectId: task.projectId,
  type: "start",
  agentName: args.agentName,
  taskId: args.taskId,
  campaignId: task.campaignId,
  message: `Started working on ${pipeline[task.pipelineStep].step}`,
});
```

**Add to `orchestrator:requestDispatch`:**
```typescript
await ctx.db.insert("activities", {
  projectId: task.projectId,
  type: "dispatch",
  agentName: args.agentName,
  taskId: args.taskId,
  campaignId: task.campaignId,
  message: `Dispatched ${args.agentName} for task`,
});
```

---

## Schema Reference

### Notifications Table
```typescript
notifications: defineTable({
  mentionedAgent: v.string(),       // "@human", "@all", or agent name
  fromAgent: v.string(),            // which agent sent it
  taskId: v.optional(v.id("tasks")),
  content: v.string(),
  delivered: v.boolean(),
  deliveredAt: v.optional(v.number()),
}).index("by_undelivered", ["mentionedAgent", "delivered"])
```

### Activities Table
```typescript
activities: defineTable({
  projectId: v.optional(v.id("projects")),
  type: v.string(),                 // "error", "warning", "complete", "start", etc.
  agentName: v.string(),
  taskId: v.optional(v.id("tasks")),
  campaignId: v.optional(v.id("campaigns")),
  message: v.string(),
  metadata: v.optional(v.any()),
}).index("by_type", ["type"])
  .index("by_agent", ["agentName"])
  .index("by_project", ["projectId"])
```

---

## Key Files

| File | Purpose | Status |
|------|---------|--------|
| `/var/www/vibe-marketing/convex/notifications.ts` | Notification CRUD | Working, unused |
| `/var/www/vibe-marketing/convex/activities.ts` | Activity logging | Working, unused |
| `/var/www/vibe-marketing/convex/pipeline.ts` | Pipeline execution | Missing notification/activity calls |
| `/var/www/vibe-marketing/convex/orchestrator.ts` | Agent dispatch | Missing notification/activity calls |
| `/var/www/vibe-marketing/dashboard/pages/activity.vue` | Activity UI | Working correctly |
| `/var/www/vibe-marketing/dashboard/components/NotificationDropdown.vue` | Notification UI | Working correctly |
| `/var/www/vibe-marketing/scripts/invoke-agent.sh` | Agent execution | Only logs errors |

---

## Architecture Notes

**Notification Flow:**
```
User Session (dashboard)
    ↓ (token-based auth)
useNotifications composable
    ↓ (queries)
notifications:listForDashboard
    ↓ (filters @human/@all)
notifications table
```

**Activity Flow:**
```
Agent execution
    ↓ (should log but doesn't)
activities:log mutation
    ↓ (inserts)
activities table
    ↓ (queries)
activities:list
    ↓
activity.vue page
```

**Current Reality:**
- Notification infrastructure: BUILT ✓, WIRED ✗
- Activity infrastructure: BUILT ✓, WIRED ✗
- Dashboard UI: BUILT ✓, WORKING ✓
- Problem: **Events are not being logged at the source**

---

## Recommendations

### Priority 1: Add Notifications to Pipeline
Edit `/var/www/vibe-marketing/convex/pipeline.ts`:
- Add notification on task completion (line ~240)
- Add notification on step advance (line ~220)

### Priority 2: Add Activities to Pipeline
Edit `/var/www/vibe-marketing/convex/pipeline.ts`:
- Add activity log in `completeStep` (after status update)
- Add activity log in `acquireLock` (when lock acquired)

### Priority 3: Add Activities to Orchestrator
Edit `/var/www/vibe-marketing/convex/orchestrator.ts`:
- Add activity log in `requestDispatch`
- Add activity log in `checkCampaignCompletion`

### Priority 4: Add Success Logging to invoke-agent.sh
Edit `/var/www/vibe-marketing/scripts/invoke-agent.sh`:
- Log activity when agent starts successfully
- Log activity when agent completes successfully (not just errors)

---

## Open Questions

1. Should notifications be created for EVERY step, or only major milestones?
2. Should activities include timing/duration metadata?
3. Should there be notification preferences (user can disable certain types)?
4. Should activities be pruned after N days to avoid bloat?
