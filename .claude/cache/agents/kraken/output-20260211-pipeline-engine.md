# Implementation Report: Pipeline Execution Engine & Supporting Scripts
Generated: 2026-02-11T18:10:00Z

## Task
Build the pipeline execution engine (convex/pipeline.ts) and supporting scripts
(invoke-agent.sh, resolve_service.py, notify.py) for the vibe-marketing platform.

## Files Created

### 1. convex/pipeline.ts -- Pipeline Execution Engine
6 exported functions that drive task progression through pipeline steps:

- **acquireLock** (mutation) -- Locks a task for an agent. Implements stale lock detection
  (10-minute threshold). Returns `{acquired: true}` or `{acquired: false, lockedBy: "..."}`.

- **releaseLock** (mutation) -- Releases a task lock. Only releases if the caller owns the lock.

- **completeStep** (mutation) -- THE ONLY way to advance a task. Verifies lock ownership,
  marks current step "completed", advances to next step (marks "in_progress"), maps task
  status from the completed step's outputDir, clears the lock. Status mapping:
  - outputDir "research" -> task status "researched"
  - outputDir "briefs" -> task status "briefed"
  - outputDir "drafts" -> task status "drafted"
  - outputDir "reviewed" -> task status "reviewed"
  - outputDir "final" -> task status "humanized"
  - No next step -> task status "completed"

- **requestRevision** (mutation) -- Sends a task back to an earlier step. Resets all steps
  from targetStep onward to "pending", sets status "revision_needed", increments revisionCount.

- **getTaskPipelineStatus** (query) -- Returns full pipeline view for a task.

- **listReadyTasks** (query) -- Returns tasks not completed/cancelled/blocked and not
  actively locked (supports optional projectId filter).

### 2. scripts/invoke-agent.sh -- Agent Invocation Wrapper
Bash script that the pipeline/cron system calls to invoke a Claude Code agent:
- Loads .env configuration
- Validates skill directory exists
- Logs agent run start via analytics:startRun
- Acquires pipeline lock
- Invokes Claude Code with --skill and --dangerously-skip-permissions
- Captures output to logs/ directory
- On crash: releases lock and logs error to activities

### 3. scripts/resolve_service.py -- Service Registry Fallback Resolver
Python script that agents call to find the best service for a capability:
- Calls services:resolve Convex function
- Returns JSON service config on success
- Exits 1 with error JSON when no active service found

### 4. scripts/notify.py -- Telegram Notification Script
Python script for sending Telegram notifications:
- Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from env or .env
- Accepts message as CLI argument or stdin
- Uses urllib (no external dependencies)
- Exits with clear error if credentials missing

## Verification Results

All pipeline functions tested against live Convex instance:

| Test | Result |
|------|--------|
| acquireLock (first caller) | acquired: true |
| acquireLock (competing caller) | acquired: false, lockedBy correct |
| releaseLock (owner) | released: true |
| completeStep (step 0, research) | status: "researched" |
| completeStep (step 1, briefs) | status: "briefed" |
| completeStep (step 2, drafts) | status: "drafted" |
| completeStep (step 3, reviewed) | status: "reviewed" |
| completeStep (step 4, final, last) | status: "completed" |
| completeStep (final, not last) | status: "humanized" |
| requestRevision (to step 0) | revised: true, revisionCount: 1, all steps reset |
| listReadyTasks | Returns unlocked, non-terminal tasks |
| getTaskPipelineStatus | Returns full pipeline view |
| resolve_service.py (no service) | Correct error, exit 1 |
| notify.py (no credentials) | Correct error, exit 1 |
| invoke-agent.sh (syntax check) | Valid bash |

## Deployment
- Deployed to Convex with `npx convex dev --once --typecheck=disable`
- typecheck=disable needed due to pre-existing dist/ directory conflict (TS5055)
- All scripts chmod +x
- logs/ directory exists and is in .gitignore

## Notes
- The analytics:startRun function already existed in convex/analytics.ts
- The services:resolve function already existed in convex/services.ts
- No schema changes were needed -- the tasks table already had all required fields
  (pipeline, pipelineStep, lockedBy, lockedAt, revisionCount, rejectionNotes, qualityScore)
- Test data (project + tasks) was created during verification and remains in the database
