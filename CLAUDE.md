# CLAUDE.md — Vibe Marketing Platform

## What This Is
A standalone AI marketing automation platform. 30+ specialized agents
(defined as skills in .claude/skills/) research, create, review, publish,
and analyze marketing content across multiple projects, products, and campaigns.

## Tech Stack
- Runtime: Claude Code (--dangerously-skip-permissions)
- Database: Self-hosted Convex (localhost:3210) — SINGLE database for everything
- Dashboard: Vue 3 / Nuxt 3 (localhost:3000) — email/password auth, session cookies
- Process manager: PM2
- Agent scripts: Python 3.12+ and Bash

## How Agents Work
Each agent is a skill directory in .claude/skills/{agent-name}/.
When invoked, an agent MUST:
1. Read its SKILL.md file first
2. Read memory/WORKING/{agent-name}.md for current state
3. Check Convex for assigned tasks and @mentions (via bash: npx convex run ...)
4. Determine the project context from the task's projectId
5. Execute work according to its skill instructions
6. Update WORKING memory and Convex task status
7. Exit cleanly (non-interactive mode)

## Project Context
All work happens within a project. When working on a task:
1. Get the task's projectId (every task has one)
2. Load the project (Convex: projects:get) — name, slug
3. Use project slug for file paths: projects/{project-slug}/campaigns/{campaign-slug}/
4. Write project-scoped memory to: projects/{project-slug}/memory/WORKING/{agent-name}.md
Global orchestrator state stays in: memory/WORKING/vibe-orchestrator.md

## Convex Access
Interact via CLI: npx convex run <function> '<json>' --url http://localhost:3210
Key functions: tasks:*, messages:*, agents:*, notifications:*,
  content:*, campaigns:*, products:*, focusGroups:*, services:*,
  projects:*, auth:*

## Data Hierarchy
Projects → Products → Focus Groups (audiences) → Campaigns → Tasks → Content
When working on a campaign task:
1. Load campaign details (Convex: campaigns:get) — includes projectId
2. Load the project context (Convex: projects:get)
3. Load the campaign's product context (Convex: products:get)
4. Load the campaign's target focus groups (Convex: focusGroups:getByCampaign)
5. Use focus group data (language patterns, pain points, hooks) in your work

Global entities (no projectId): Pipelines, Agents, Service Registry

## Service Registry
When you need an external service (SEO data, images, scraping, etc.):
1. Read memory/long-term/SERVICE_REGISTRY.md
2. Find the category you need
3. Use the highest-priority ACTIVE service
4. Run the script at the listed path
5. If it fails, try the next priority service in the same category
6. If no services active in category, log warning and skip

## File Conventions
- Project root: projects/{project-slug}/
- Campaign files: projects/{project-slug}/campaigns/{campaign-slug}/
  - Research: .../campaigns/{campaign-slug}/research/
  - Briefs: .../campaigns/{campaign-slug}/briefs/
  - Drafts: .../campaigns/{campaign-slug}/drafts/
  - Reviewed: .../campaigns/{campaign-slug}/reviewed/
  - Final: .../campaigns/{campaign-slug}/final/
  - Images: .../campaigns/{campaign-slug}/assets/images/
  - Social: .../campaigns/{campaign-slug}/assets/social/
  - Email: .../campaigns/{campaign-slug}/assets/email/
  - Artifacts: .../campaigns/{campaign-slug}/artifacts/
- Project memory: projects/{project-slug}/memory/WORKING/{agent-name}.md
- Project uploads: projects/{project-slug}/uploads/
- Global artifacts: artifacts/
- Global agent memory: memory/WORKING/{agent-name}.md
- Daily logs: memory/daily/YYYY-MM-DD.md
- Service registry: memory/long-term/SERVICE_REGISTRY.md
- Shared reference skills: .claude/skills/shared-references/

## Content Pipeline Statuses
backlog → researched → briefed → drafted → reviewed → humanized → completed

## Pipeline Contract
1. ALWAYS acquireLock before starting work — exit if not acquired
2. ALWAYS completeStep as your ABSOLUTE LAST action
3. NEVER update task status directly — only through pipeline:completeStep
4. NEVER auto-post to Reddit/X/LinkedIn — content goes to campaign folder only

## Rules
1. Pipeline runs uninterrupted — no human gates (MVP)
2. NEVER auto-post replies to Reddit/X/LinkedIn — ALWAYS queue for human
3. ALWAYS update memory/WORKING/{agent-name}.md after work
4. ALWAYS log activities to Convex (activities:log)
5. ALWAYS read the campaign's focus groups before creating content
6. ALWAYS check SERVICE_REGISTRY.md before calling any external API
7. Use haiku for heartbeats, sonnet for content, opus for high-stakes
8. Write content in markdown. Conversion happens at publish time.
9. ALWAYS include projectId when creating/querying project-scoped data

## Notification Protocol
To notify another agent:
  npx convex run notifications:create '{"mentionedAgent":"name","content":"msg"}'
Use @all for everyone. Use @human for Telegram notification to owner.

## Error Handling
1. Log error to memory/WORKING/{agent-name}.md
2. Log to Convex: activities:log with type "error"
3. Set task to "blocked" with notes
4. Notify vibe-orchestrator
5. Exit gracefully
