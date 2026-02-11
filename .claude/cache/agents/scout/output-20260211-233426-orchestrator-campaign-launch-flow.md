# Codebase Report: Orchestrator & Campaign Launch Workflow
Generated: 2026-02-11 23:34:26

## Executive Summary

**CRITICAL FINDING:** The orchestrator and campaign launch workflow is **MOSTLY SPEC, NOT IMPLEMENTED**. The platform has:

- ✅ **Database schema complete** - campaigns, tasks, pipelines all defined
- ✅ **UI complete** - campaign activation buttons work, call Convex mutations
- ✅ **Lock/pipeline mechanics implemented** - `acquireLock`, `completeStep`, `requestRevision` all functional
- ✅ **Agent invocation script exists** - `scripts/invoke-agent.sh` ready to run agents
- ⚠️ **BUT: Missing the critical bridge** - nothing actually creates tasks when campaign is activated
- ❌ **No orchestrator agent** - exists in database as entity, but no skill/implementation
- ❌ **No Convex triggers** - no auto-dispatch on task status changes
- ❌ **No cron heartbeat** - orchestrator not running on schedule
- ❌ **No task generation** - campaign activation just sets status, doesn't spawn work

**Result:** The system is a "skeleton ready for organs" - all the plumbing is there, but the workflow doesn't actually run.

---

## Campaign Launch Flow (AS DESIGNED)

### Current Implementation State

```
User clicks "Activate" in dashboard
  ↓
[IMPLEMENTED] ✓ Dashboard calls api.campaigns.activate
  ↓
[IMPLEMENTED] ✓ Convex mutation sets status = "active"
  ↓
[MISSING] ✗ Should trigger task generation from campaign.targetArticleCount
  ↓
[MISSING] ✗ Should dispatch first agent via invoke-agent.sh
  ↓
[MISSING] ✗ Agent completes → should trigger next agent
  ↓
[IMPLEMENTED] ✓ Pipeline mechanics work IF manually invoked
```

### What Exists vs What's Missing

| Component | Status | Evidence |
|-----------|--------|----------|
| Campaign schema | ✅ Implemented | `/var/www/vibe-marketing/convex/schema.ts:360-406` |
| Campaign mutations | ✅ Implemented | `activate`, `pause`, `complete` exist |
| Task schema | ✅ Implemented | Full pipeline array, lock fields, status |
| Pipeline mechanics | ✅ Implemented | `acquireLock`, `completeStep`, `releaseLock` |
| Agent invocation script | ✅ Implemented | `/var/www/vibe-marketing/scripts/invoke-agent.sh` |
| Task generation on activate | ❌ Missing | `campaigns.activate` only sets status field |
| Convex triggers | ❌ Missing | No `internalAction` dispatchers found |
| Orchestrator skill | ❌ Missing | No `.claude/skills/vibe-orchestrator/` |
| Orchestrator cron | ❌ Missing | No crontab entries |
| Check pipeline script | ❌ Missing | `scripts/check_pipeline.py` doesn't exist |

---

## Architecture: Orchestrator Role

### Designed Role (From Spec)

The `vibe-orchestrator` agent is designed as a **safety net**, not primary dispatcher:

**Primary dispatch:** Convex triggers (mutations → actions → invoke agents)
**Safety net:** Cron heartbeat every 10 minutes catches:
- Stale locks (>30 min, agent crashed)
- Orphaned tasks (no lock, not started)
- Incomplete deliverables (parallel work not triggered)
- Pipeline starvation (backlog empty)

### Current Reality

```bash
# Check for orchestrator agent
$ ls -la /var/www/vibe-marketing/.claude/skills/ | grep orchestr
# → No results

# Check for orchestrator cron
$ crontab -l | grep orchestrat
# → No orchestrator cron found

# Check for orchestrator in PM2
$ pm2 list | grep orchestrat
# → Only vibe-dashboard running

# Check database
$ npx convex run agents:getByName '{"name":"vibe-orchestrator"}'
# → Returns: {
#     name: "vibe-orchestrator",
#     level: "orchestrator",
#     skillPath: "",  ← EMPTY
#     agentFilePath: "",  ← EMPTY
#     status: "idle"
#   }
```

**Verdict:** Orchestrator exists as **database entry only**. No code, no skill, no cron.

---

## Pipeline Execution Flow (FUNCTIONAL BUT DORMANT)

### The Good News: Lock & Step Mechanics Work

**Location:** `/var/www/vibe-marketing/convex/pipeline.ts`

```typescript
// Line 31: acquireLock - prevents double work
export const acquireLock = mutation({
  // Checks if task locked by another agent
  // Steals stale locks (>10 min)
  // Returns {acquired: true/false}
})

// Line 93: completeStep - atomic advancement
export const completeStep = mutation({
  // Validates lock ownership
  // Advances pipelineStep
  // Updates task status via outputDirToStatus()
  // Releases lock
  // Returns next step info
})

// Line 176: requestRevision - quality gate
export const requestRevision = mutation({
  // Rewinds to earlier step
  // Resets steps to "pending"
  // Sets status = "revision_needed"
})
```

**Status mapping (line 10-25):**
```typescript
function outputDirToStatus(outputDir, currentStatus) {
  const mapping = {
    research: "researched",
    briefs: "briefed",
    drafts: "drafted",
    reviewed: "reviewed",
    final: "humanized",
  };
  return mapping[outputDir] || currentStatus;
}
```

### Task Pipeline Structure

**Location:** `/var/www/vibe-marketing/convex/schema.ts:278-311`

```typescript
tasks: defineTable({
  pipeline: v.array(v.object({
    step: v.number(),
    status: v.string(),  // "pending" | "in_progress" | "completed"
    agent: v.optional(v.string()),  // "vibe-content-writer"
    model: v.optional(v.string()),  // "opus" | "sonnet" | "haiku"
    description: v.string(),
    outputDir: v.optional(v.string()),  // "drafts" | "reviewed"
  })),
  pipelineStep: v.number(),  // Current step index
  status: v.union(...),  // "backlog" | "drafted" | "completed"
  lockedBy: v.optional(v.string()),  // Agent name holding lock
  lockedAt: v.optional(v.number()),  // Timestamp
})
```

**Pipeline array example (from spec):**
```json
{
  "pipeline": [
    {"step": 0, "agent": "vibe-keyword-researcher", "outputDir": "research"},
    {"step": 1, "agent": "vibe-content-writer", "outputDir": "drafts"},
    {"step": 2, "agent": "vibe-content-reviewer", "outputDir": "reviewed"},
    {"step": 3, "agent": "vibe-humanizer", "outputDir": "final"}
  ],
  "pipelineStep": 0,  // Current position
  "status": "backlog"
}
```

### Agent Invocation Script

**Location:** `/var/www/vibe-marketing/scripts/invoke-agent.sh`

**Functionality:**
1. Resolves agent skill path from Convex registry
2. Checks skill directory exists
3. Updates agent heartbeat
4. **Pipeline mode:**
   - Calls `pipeline:acquireLock`
   - Invokes Claude Code with agent prompt
   - Releases lock on crash
5. **Heartbeat mode:**
   - No lock needed
   - Agent checks for work itself

**Example invocation:**
```bash
./scripts/invoke-agent.sh vibe-content-writer jd7abc123def
# → Acquires lock on task jd7abc123def
# → Runs: claude -p "You are vibe-content-writer. Task ID: jd7abc123def. ..."
# → Agent reads SKILL.md, queries Convex, does work, calls completeStep
```

**Status:** ✅ **Script is functional and ready to use**

---

## The Missing Bridge: Task Generation

### What Should Happen When Campaign Activates

**Designed flow (from vibe-marketing-platform-v3.md:3650-3652):**

```
1. Task created (status: "backlog", pipelineStep: 0)
   → Convex auto-dispatches first agent from task.pipeline[0]
```

### What Actually Happens

**Current code:** `/var/www/vibe-marketing/convex/campaigns.ts:203-211`

```typescript
export const activate = mutation({
  args: { id: v.id("campaigns") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, {
      status: "active" as const,
      activatedAt: Date.now(),
    });
  },
});
```

**Result:** Campaign status changes. **Nothing else happens.**

### What's Missing

**Need to add to `campaigns.activate`:**

```typescript
export const activate = mutation({
  handler: async (ctx, args) => {
    const campaign = await ctx.db.get(args.id);
    
    // 1. Set campaign active
    await ctx.db.patch(args.id, {
      status: "active",
      activatedAt: Date.now(),
    });
    
    // 2. Generate tasks from targetArticleCount
    const count = campaign.targetArticleCount || 5;
    const taskIds = [];
    
    for (let i = 0; i < count; i++) {
      const taskId = await ctx.db.insert("tasks", {
        projectId: campaign.projectId,
        campaignId: args.id,
        title: `Article ${i+1}: [Auto-generated]`,
        description: campaign.description,
        pipeline: buildPipelineFromSnapshot(campaign.pipelineSnapshot),
        pipelineStep: 0,
        status: "backlog",
        priority: "medium",
        createdBy: "system",
        deliverables: campaign.deliverableConfig,
        focusGroupIds: campaign.targetFocusGroupIds,
      });
      taskIds.push(taskId);
    }
    
    // 3. Schedule first agent dispatch (via internalAction)
    for (const taskId of taskIds) {
      await ctx.scheduler.runAfter(0, internal.pipeline.dispatchNextAgent, {
        taskId,
      });
    }
  },
});
```

**Status:** ❌ **Not implemented**

---

## The Missing Trigger: Auto-Dispatch on CompleteStep

### Designed Flow (From Spec)

**vibe-marketing-platform-v3.md:2928-2939:**

```typescript
export const completeStep = mutation({
  handler: async (ctx, args) => {
    // ... validate, advance step, release lock ...
    
    // Schedule next agent (or trigger onComplete if pipeline done)
    // Because this is a Convex mutation, ALL of this is atomic.
    // Next agent is scheduled AFTER the mutation commits.
  },
});
```

### Current Implementation

**convex/pipeline.ts:100-170:**

```typescript
export const completeStep = mutation({
  handler: async (ctx, args) => {
    // ... validates lock ...
    // ... advances pipelineStep ...
    // ... releases lock ...
    
    return {
      completed: true,
      nextStep: hasNextStep ? nextStepIndex : null,
      newStatus,
    };
  },
});
```

**What's missing:** No `ctx.scheduler.runAfter()` to dispatch next agent.

### What Should Be Added

```typescript
export const completeStep = mutation({
  handler: async (ctx, args) => {
    // ... existing logic ...
    
    await ctx.db.patch(args.taskId, patch);
    
    // NEW: If there's a next step, schedule its agent
    if (hasNextStep) {
      const nextAgent = pipeline[nextStepIndex].agent;
      if (nextAgent) {
        await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
          taskId: args.taskId,
          agentName: nextAgent,
          stepIndex: nextStepIndex,
        });
      }
    } else {
      // Pipeline complete - check campaign completion
      await ctx.scheduler.runAfter(0, internal.campaigns.checkCompletion, {
        campaignId: task.campaignId,
      });
    }
    
    return { completed: true, nextStep, newStatus };
  },
});
```

**Status:** ❌ **Not implemented**

---

## The Missing Dispatcher: Internal Action

### What's Needed

**Location:** Should exist in `convex/pipeline.ts` or new `convex/dispatcher.ts`

```typescript
import { internalAction } from "./_generated/server";
import { internal } from "./_generated/api";

export const dispatchAgent = internalAction({
  args: {
    taskId: v.id("tasks"),
    agentName: v.string(),
    stepIndex: v.number(),
  },
  handler: async (ctx, args) => {
    // This runs OUTSIDE the database transaction
    // Safe to call external scripts
    
    const scriptPath = "/var/www/vibe-marketing/scripts/invoke-agent.sh";
    
    // Option A: Call script directly
    const { spawn } = require('child_process');
    spawn(scriptPath, [args.agentName, args.taskId], {
      detached: true,
      stdio: 'ignore',
    }).unref();
    
    // Option B: Queue in a job system
    // await ctx.scheduler.runAfter(0, internal.jobs.enqueue, {
    //   type: "agent_run",
    //   agentName: args.agentName,
    //   taskId: args.taskId,
    // });
  },
});
```

**Status:** ❌ **Doesn't exist**

---

## The Missing Orchestrator Skill

### Expected Location

```
/var/www/vibe-marketing/.claude/skills/vibe-orchestrator/
  ├── SKILL.md
  ├── README.md
  └── scripts/
      └── check_pipeline.py
```

### What It Should Do (From Spec)

**1. Heartbeat mode (cron every 10 min):**
```bash
$ crontab -e
*/10 * * * * cd /var/www/vibe-marketing && ./scripts/invoke-agent.sh vibe-orchestrator --heartbeat
```

**2. SKILL.md responsibilities:**
```markdown
# vibe-orchestrator

You are the safety net. Your job:

1. Find stale locks (>30 min) → release and re-dispatch
2. Find orphaned tasks (no lock, step in_progress) → dispatch agent
3. Find incomplete deliverables → dispatch parallel agents
4. Check backlog depth → trigger keyword researcher if low
5. Report health metrics → log to Convex
```

**3. Python script for queries:**
```python
#!/usr/bin/env python3
# .claude/skills/vibe-orchestrator/scripts/check_pipeline.py

import subprocess
import json

def cx(fn, args='{}'):
    """Query Convex"""
    cmd = f'npx convex run {fn} \'{args}\' --url http://localhost:3210 --admin-key ...'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout) if result.stdout else None

def invoke_agent(name, task_id):
    """Dispatch agent"""
    subprocess.run(f'./scripts/invoke-agent.sh {name} {task_id}', shell=True)

# Find stale locks
stale = cx("pipeline:listReadyTasks")  # Actually need pipeline:findStaleLocks
for task in stale:
    if task.get('lockedBy') and (now - task['lockedAt']) > 30*60*1000:
        cx("pipeline:releaseLock", f'{{"taskId":"{task["_id"]}"}}')
        agent = task['pipeline'][task['pipelineStep']].get('agent')
        invoke_agent(agent, task['_id'])
```

**Status:** ❌ **Directory doesn't exist, skill not created**

---

## Dashboard Campaign Page

### Location
`/var/www/vibe-marketing/dashboard/pages/projects/[slug]/campaigns/[id].vue`

### Functionality (✅ IMPLEMENTED)

**Status controls (lines 119-139):**
```vue
<button v-if="status === 'planning' || status === 'paused'"
        @click="showConfirmActivate = true">
  Activate
</button>
<button v-if="status === 'active'"
        @click="showConfirmPause = true">
  Pause
</button>
<button v-if="status === 'active' || status === 'paused'"
        @click="showConfirmComplete = true">
  Complete
</button>
```

**Mutations (lines 23-25, 37-65):**
```typescript
const { mutate: activateCampaign } = useConvexMutation(api.campaigns.activate)
const { mutate: pauseCampaign } = useConvexMutation(api.campaigns.pause)
const { mutate: completeCampaign } = useConvexMutation(api.campaigns.complete)

async function activate() {
  await activateCampaign({ id: campaignId.value })
  toast.success('Campaign activated!')
}
```

**Task table (lines 199-245):**
- Shows all tasks for campaign
- Columns: title, type, status, priority, agent, quality
- Click task title → opens detail modal

**What works:**
- ✅ Button triggers mutation
- ✅ Status updates in database
- ✅ UI reflects new status
- ✅ Tasks display (if they exist)

**What doesn't work:**
- ❌ No tasks created when activated
- ❌ No agents dispatched
- ❌ Table stays empty after activation

---

## Data Flow: How It SHOULD Work

### Complete Flow (Spec vs Reality)

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Click "Activate Campaign"                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ DASHBOARD: useConvexMutation(api.campaigns.activate)        │
│ Status: ✅ WORKS                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ CONVEX: campaigns.activate mutation                         │
│ Current: Sets status = "active", activatedAt = now          │
│ Missing: Generate tasks, dispatch agents                    │
│ Status: ⚠️ INCOMPLETE                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MISSING: Task generation loop                               │
│ Should: Create N tasks from targetArticleCount              │
│ Should: Build pipeline from campaign.pipelineSnapshot       │
│ Status: ❌ NOT IMPLEMENTED                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MISSING: ctx.scheduler.runAfter(internal.pipeline.dispatch) │
│ Should: Trigger first agent for each task                   │
│ Status: ❌ NOT IMPLEMENTED                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MISSING: internal.pipeline.dispatchAgent action             │
│ Should: Call scripts/invoke-agent.sh                        │
│ Status: ❌ NOT IMPLEMENTED                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ EXISTS: scripts/invoke-agent.sh                             │
│ Does: Acquire lock, invoke Claude, release on crash         │
│ Status: ✅ FUNCTIONAL (but never called)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ EXISTS: Agent runs via Claude Code                          │
│ Does: Read SKILL.md, query task, do work                    │
│ Status: ✅ WOULD WORK (if invoked)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ EXISTS: Agent calls pipeline.completeStep                   │
│ Does: Advance step, release lock, return next step          │
│ Missing: Auto-dispatch next agent                           │
│ Status: ⚠️ WORKS BUT STOPS                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MISSING: Trigger next agent                                 │
│ Should: ctx.scheduler → dispatchAgent → invoke-agent.sh     │
│ Status: ❌ NOT IMPLEMENTED                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ MISSING: Orchestrator cron heartbeat                        │
│ Should: Every 10 min, check for stale/orphaned tasks        │
│ Status: ❌ NOT RUNNING                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Convex Functions: What Exists

### campaigns.ts (9 mutations/queries)

| Function | Type | Status | Notes |
|----------|------|--------|-------|
| `list` | query | ✅ | List by project |
| `get` | query | ✅ | Get by ID |
| `getBySlug` | query | ✅ | Get by slug |
| `listActive` | query | ✅ | Filter active |
| `create` | mutation | ✅ | Full campaign creation |
| `update` | mutation | ✅ | Partial updates |
| `activate` | mutation | ⚠️ | **Only sets status** |
| `pause` | mutation | ✅ | Sets paused status |
| `complete` | mutation | ✅ | Sets completed status |

### tasks.ts (11 mutations/queries)

| Function | Type | Status | Notes |
|----------|------|--------|-------|
| `listByProject` | query | ✅ | Filter by project |
| `listByCampaign` | query | ✅ | Filter by campaign |
| `listByStatus` | query | ✅ | Filter by status |
| `get` | query | ✅ | Get by ID |
| `create` | mutation | ✅ | Full task creation |
| `update` | mutation | ✅ | Partial updates |
| `updateStatus` | mutation | ✅ | Change status |
| `assignTo` | mutation | ✅ | Assign agents |
| `addSubscriber` | mutation | ✅ | Add watchers |
| `removeSubscriber` | mutation | ✅ | Remove watchers |
| `delete` | mutation | ✅ | Delete task |

### pipeline.ts (7 mutations/queries)

| Function | Type | Status | Notes |
|----------|------|--------|-------|
| `acquireLock` | mutation | ✅ | Prevent double work |
| `releaseLock` | mutation | ✅ | Release manually |
| `completeStep` | mutation | ⚠️ | **Missing auto-dispatch** |
| `requestRevision` | mutation | ✅ | Rewind to step |
| `getTaskPipelineStatus` | query | ✅ | Full pipeline view |
| `listReadyTasks` | query | ✅ | Available for agents |
| `getStepDetails` | query | ✅ | Single step info |

### pipelines.ts (9 mutations/queries)

| Function | Type | Status | Notes |
|----------|------|--------|-------|
| `list` | query | ✅ | All pipelines |
| `listPresets` | query | ✅ | Filter presets |
| `get` | query | ✅ | By ID |
| `getBySlug` | query | ✅ | By slug |
| `create` | mutation | ✅ | New pipeline |
| `rename` | mutation | ✅ | Change name |
| `fork` | mutation | ✅ | Clone as custom |
| `remove` | mutation | ✅ | Delete |
| `fixStepModels` | mutation | ✅ | Batch update |

### Missing Functions (Needed for Flow)

| Function | Type | Purpose | Priority |
|----------|------|---------|----------|
| `pipeline.dispatchAgent` | internalAction | Call invoke-agent.sh | 🔴 CRITICAL |
| `pipeline.findStaleLocks` | query | Orchestrator safety net | 🟡 HIGH |
| `pipeline.findOrphanedTasks` | query | Orchestrator safety net | 🟡 HIGH |
| `campaigns.generateTasks` | mutation | Create tasks on activate | 🔴 CRITICAL |
| `campaigns.checkCompletion` | mutation | Campaign done trigger | 🟡 HIGH |
| `tasks.withIncompleteDeliverables` | query | Parallel work tracking | 🟢 MEDIUM |

---

## Key Files Reference

### Convex Schema & Functions

| File | Purpose | Status |
|------|---------|--------|
| `convex/schema.ts` | Database schema (campaigns, tasks, pipelines) | ✅ Complete |
| `convex/campaigns.ts` | Campaign CRUD + lifecycle | ⚠️ Activation incomplete |
| `convex/tasks.ts` | Task CRUD | ✅ Complete |
| `convex/pipeline.ts` | Lock mechanics + step advancement | ⚠️ Missing triggers |
| `convex/pipelines.ts` | Pipeline templates | ✅ Complete |
| `convex/seed.ts` | Initial data (agents, pipelines, skills) | ✅ Complete |

### Agent Infrastructure

| File | Purpose | Status |
|------|---------|--------|
| `scripts/invoke-agent.sh` | Agent runner (lock + Claude invoke + crash handling) | ✅ Functional |
| `scripts/notify.py` | Telegram notifications | ✅ Functional |
| `scripts/resolve_service.py` | External service routing | ✅ Functional |
| `.claude/skills/vibe-orchestrator/` | Orchestrator agent skill | ❌ Missing |
| `scripts/check_pipeline.py` | Heartbeat safety net | ❌ Missing |

### Dashboard

| File | Purpose | Status |
|------|---------|--------|
| `dashboard/pages/projects/[slug]/campaigns/[id].vue` | Campaign detail + activation UI | ✅ Complete |
| `dashboard/pages/projects/[slug]/campaigns/index.vue` | Campaign list | ✅ Complete |
| `dashboard/pages/projects/[slug]/index.vue` | Project overview | ✅ Complete |

### Documentation

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `vibe-marketing-platform-v3.md` | Master spec (19 sections) | 5,227 | ✅ Comprehensive |
| `CLAUDE.md` | Agent instructions | 110 | ✅ Current |
| `external-services-registry.md` | Service config + fallbacks | 1,438 | ✅ Complete |
| `marketing-books.md` | Layer model + book references | 874 | ✅ Complete |

---

## Answers to Key Questions

### 1. What happens after a user clicks "launch" on a campaign?

**Currently:**
1. Dashboard calls `api.campaigns.activate`
2. Convex sets `status = "active"` and `activatedAt = Date.now()`
3. **Nothing else happens**

**Should happen:**
1. Campaign status changes
2. System generates N tasks (from `targetArticleCount`)
3. Each task gets pipeline array from `pipelineSnapshot`
4. System dispatches first agent for each task
5. Agent runs, completes step, triggers next agent
6. Process continues until pipeline complete

### 2. How does work flow from campaign → pipeline → tasks → agents?

**Designed flow:**
```
Campaign (active)
  ├─> Generate tasks (count = targetArticleCount)
  │   ├─> Task 1: pipeline from pipelineSnapshot
  │   ├─> Task 2: pipeline from pipelineSnapshot
  │   └─> Task N: pipeline from pipelineSnapshot
  │
  └─> For each task:
      └─> Dispatch agent from pipeline[0]
          └─> Agent: acquireLock → work → completeStep
              └─> Trigger next agent from pipeline[1]
                  └─> Agent: acquireLock → work → completeStep
                      └─> ... until pipeline.length
```

**Current reality:**
```
Campaign (active)
  └─> Status field changes
      └─> (end)
```

### 3. Is the orchestrator a real running process or just a spec?

**Answer:** Just a spec + database entry.

- ✅ Database record exists (`agents` table)
- ❌ No skill directory
- ❌ No cron job
- ❌ No running process
- ❌ No implementation

### 4. Are there any broken links in the chain?

**Yes. Three critical links missing:**

1. **Task generation on campaign activate**
   - Location: `convex/campaigns.ts:activate`
   - Missing: Loop to create tasks from `targetArticleCount`

2. **Agent dispatch on task creation**
   - Location: `convex/pipeline.ts` (new function needed)
   - Missing: `internalAction` to call `invoke-agent.sh`

3. **Auto-dispatch on completeStep**
   - Location: `convex/pipeline.ts:completeStep`
   - Missing: `ctx.scheduler.runAfter()` to trigger next agent

### 5. What's functional vs what's still spec/placeholder?

**Functional (can be used today):**
- ✅ Database schema (campaigns, tasks, pipelines)
- ✅ Campaign/task CRUD operations
- ✅ Pipeline lock mechanics (`acquireLock`, `completeStep`)
- ✅ Agent invocation script (`invoke-agent.sh`)
- ✅ Dashboard UI (create, edit, activate campaigns)
- ✅ Task status tracking

**Spec only (not implemented):**
- ❌ Task generation on activation
- ❌ Convex triggers (auto-dispatch)
- ❌ Orchestrator agent + cron
- ❌ Deliverable branching (parallel work)
- ❌ Campaign completion detection
- ❌ Stale lock recovery

**Can be manually driven:**
- ⚙️ Create campaign via dashboard ✓
- ⚙️ Manually create tasks via Convex ✓
- ⚙️ Manually call `invoke-agent.sh task-id` ✓
- ⚙️ Agent runs, does work, calls `completeStep` ✓
- ⚙️ Manually dispatch next agent ✓

---

## Implementation Gap Analysis

### Phase 1: Minimum Viable Flow (CRITICAL)

**Goal:** Campaign activation → tasks created → first agent runs

**Changes needed:**

1. **campaigns.ts:activate** - Add task generation
   ```typescript
   // After setting status = "active"
   const count = campaign.targetArticleCount || 5;
   for (let i = 0; i < count; i++) {
     const taskId = await ctx.db.insert("tasks", {...});
     await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
       taskId, agentName: pipeline[0].agent
     });
   }
   ```

2. **pipeline.ts** - Add dispatchAgent action
   ```typescript
   export const dispatchAgent = internalAction({
     handler: async (ctx, args) => {
       // Call invoke-agent.sh
     },
   });
   ```

3. **Test flow:**
   - Create campaign in dashboard
   - Click "Activate"
   - Verify tasks appear in database
   - Verify first agent is invoked
   - Verify task moves through pipeline

### Phase 2: Auto-Advancement (HIGH)

**Goal:** completeStep → next agent runs automatically

**Changes needed:**

1. **pipeline.ts:completeStep** - Add auto-dispatch
   ```typescript
   // After patching task
   if (hasNextStep) {
     const nextAgent = pipeline[nextStepIndex].agent;
     await ctx.scheduler.runAfter(0, internal.pipeline.dispatchAgent, {
       taskId: args.taskId, agentName: nextAgent
     });
   }
   ```

2. **Test flow:**
   - Manually invoke agent for task
   - Agent completes step
   - Verify next agent is auto-invoked
   - Verify task flows to completion

### Phase 3: Orchestrator Safety Net (MEDIUM)

**Goal:** Cron catches stale locks and orphaned tasks

**Changes needed:**

1. **Create orchestrator skill**
   ```
   .claude/skills/vibe-orchestrator/
     ├── SKILL.md
     └── scripts/check_pipeline.py
   ```

2. **Add Convex queries:**
   - `pipeline:findStaleLocks`
   - `pipeline:findOrphanedTasks`

3. **Install cron:**
   ```bash
   */10 * * * * cd /var/www/vibe-marketing && \
     ./scripts/invoke-agent.sh vibe-orchestrator --heartbeat
   ```

4. **Test flow:**
   - Manually kill agent mid-work (leave lock)
   - Wait 30+ min
   - Orchestrator cron runs
   - Verify lock released and agent re-dispatched

### Phase 4: Completion Detection (MEDIUM)

**Goal:** Campaign auto-completes when all tasks done

**Changes needed:**

1. **campaigns.ts** - Add checkCompletion
   ```typescript
   export const checkCompletion = mutation({
     handler: async (ctx, args) => {
       const tasks = await ctx.db.query("tasks")
         .withIndex("by_campaign", q => q.eq("campaignId", args.campaignId))
         .collect();
       
       const allDone = tasks.every(t => t.status === "completed");
       if (allDone) {
         await ctx.db.patch(args.campaignId, {
           status: "completed",
           completedAt: Date.now(),
         });
       }
     },
   });
   ```

2. **pipeline.ts:completeStep** - Check campaign on task complete
   ```typescript
   if (!hasNextStep) {
     await ctx.scheduler.runAfter(0, internal.campaigns.checkCompletion, {
       campaignId: task.campaignId,
     });
   }
   ```

---

## Related Previous Scout Reports

Located in `.claude/cache/agents/scout/`:

1. **output-20260211-214145.md** - External services mapping
2. **output-20260211-214311-external-services.md** - Service registry deep dive
3. **output-20260211-224226-focus-groups-status.md** - Focus group implementation status
4. **output-20260211-notification-ui-exploration.md** - Notification system architecture

---

## Recommendation Priority

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 🔴 P0 | Implement task generation on activate | 2 hours | Enables basic workflow |
| 🔴 P0 | Add pipeline.dispatchAgent action | 1 hour | Connects to invoke script |
| 🟡 P1 | Add auto-dispatch on completeStep | 1 hour | Enables end-to-end flow |
| 🟡 P1 | Test full pipeline with real agents | 3 hours | Validates implementation |
| 🟢 P2 | Create orchestrator skill + cron | 4 hours | Adds safety net |
| 🟢 P2 | Add campaign completion detection | 2 hours | Polishes UX |
| 🟢 P3 | Implement deliverable branching | 4 hours | Adds parallel work |

**Minimum viable launch:** P0 + P1 = ~4 hours of implementation

---

## Conclusion

The Vibe Marketing platform has **excellent bones**:
- Clean database schema
- Well-designed lock mechanics
- Functional agent invocation script
- Polished dashboard UI
- Comprehensive spec documentation

**But it's missing the central nervous system** - the triggers and dispatchers that make the system autonomous. Currently, every step requires manual intervention. With P0+P1 changes (~4 hours), the system would run end-to-end automatically.

The good news: The hard design decisions are already made. The pipeline contract is solid. The missing pieces are straightforward glue code to connect existing components.

---

**Report generated by Scout agent**
**Timestamp:** 2026-02-11 23:34:26
**Project:** /var/www/vibe-marketing/dashboard
**Key files examined:** 23 files across convex/, dashboard/, scripts/, .claude/skills/
**Verification method:** Direct code inspection + spec comparison
