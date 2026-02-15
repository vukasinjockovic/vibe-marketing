# Vibe Marketing

AI marketing automation platform. 30+ specialized Claude Code agents research, create, review, and publish marketing content across projects, products, and campaigns.

## Architecture

```
                    ┌─────────────────┐
                    │  Nuxt Dashboard  │  :3000
                    │  (Vue 3 + TS)    │
                    └────────┬────────┘
                             │ WebSocket (real-time)
                    ┌────────▼────────┐
                    │  Convex Backend  │  :3210 (self-hosted)
                    │  (27 tables)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌────▼────┐  ┌──────▼──────┐
       │  Pipeline    │ │ Agents  │  │  Services   │
       │  Engine      │ │ (30+)   │  │  Registry   │
       └─────────────┘ └─────────┘  └─────────────┘
```

**Stack:** Self-hosted Convex (Postgres-backed) + Vue 3/Nuxt 3 dashboard + Claude Code agents + PM2 process management.

## Quick Start

### Prerequisites

- Node.js >= 22
- Docker & Docker Compose
- Claude Code CLI (`npm i -g @anthropic-ai/claude-code`)

### 1. Clone and install

```bash
git clone <repo-url> vibe-marketing
cd vibe-marketing
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
# Required
CONVEX_DB_PASSWORD=<strong-password>
CONVEX_INSTANCE_SECRET=$(openssl rand -hex 32)

# Optional (enable as needed)
TELEGRAM_BOT_TOKEN=<your-bot-token>
TELEGRAM_CHAT_ID=<your-chat-id>
# ... see .env.example for all service keys
```

### 3. Start Convex

```bash
# Start Postgres + Convex backend + dashboard
docker compose up -d

# Wait for healthy status
docker compose ps

# Get the admin key from logs
docker compose logs convex-backend 2>&1 | grep "admin key"
# Add it to .env as CONVEX_SELF_HOSTED_ADMIN_KEY=...
```

### 4. Deploy schema and seed data

```bash
# Deploy Convex functions
npx convex deploy --url http://localhost:3210 --admin-key <your-admin-key>

# Seed initial data (service categories, skill categories, pipelines, agents)
npx convex run seed:run --url http://localhost:3210 --admin-key <your-admin-key>

# Seed any missing pipelines (safe to run anytime)
npx convex run seed:seedMissing --url http://localhost:3210 --admin-key <your-admin-key>
```

### 5. Create admin user

```bash
npx convex run admin:createUser \
  '{"email":"you@example.com","name":"Admin","password":"your-password","role":"admin"}' \
  --url http://localhost:3210 --admin-key <your-admin-key>
```

### 6. Start the dashboard

```bash
cd dashboard && npm install
npm run dev
# Opens at http://localhost:3000
```

Login with the admin credentials you created in step 5.

## Dashboard

The Nuxt 3 dashboard uses **real-time WebSocket subscriptions** via `ConvexClient`. All data updates instantly across browser tabs when agents write to Convex.

**Pages:**
- **Dashboard** — Live stats (projects, campaigns, tasks, agents) + recent activity feed
- **Projects** — Project grid with create/archive, nested product and campaign management
- **Products** — Product CRUD with brand voice fields (tone, USPs, competitors)
- **Audiences** — Focus group management with import, research, enrichment tracking
  - Import from document (.md, .txt, .docx, .pdf)
  - Research audiences from scratch (web search + Reddit + competitor analysis)
  - Staging review page (approve/reject/edit before import)
  - Per-group detail with enrichment field status and history timeline
- **Campaigns** — Campaign lifecycle (planning → active → paused → completed), task tables
- **Pipeline** — Kanban board view of tasks across pipeline stages
- **Agents** — Agent registry with status, model, skills, recent runs
- **Services** — Service registry by capability category, toggle active/inactive
- **Activity** — Full activity log across all agents and projects

**190 unit tests, build verified (1.71 MB, 406 kB gzip).**

## Project Structure

```
vibe-marketing/
├── convex/                    # Convex backend (19 modules, 100+ functions)
│   ├── schema.ts              # Database schema (27 tables, 58 indexes)
│   ├── auth.ts                # Email/password auth + sessions
│   ├── admin.ts               # Admin user management
│   ├── projects.ts            # Project CRUD
│   ├── products.ts            # Product CRUD
│   ├── campaigns.ts           # Campaign CRUD + lifecycle
│   ├── tasks.ts               # Task CRUD + assignment
│   ├── pipeline.ts            # Pipeline execution engine (locks, steps, revisions)
│   ├── agents.ts              # Agent registry + heartbeat
│   ├── focusGroups.ts         # Audience profiles + enrichment + batch operations
│   ├── focusGroupStaging.ts   # Staging table for audience import/review
│   ├── messages.ts            # Agent-to-agent messaging
│   ├── activities.ts          # Activity logging
│   ├── notifications.ts       # Agent notifications
│   ├── documents.ts           # Content documents
│   ├── revisions.ts           # Content revision tracking
│   ├── services.ts            # Service registry + capability resolver
│   ├── analytics.ts           # Agent runs, metrics, reports
│   ├── pipelines.ts           # Pipeline templates
│   └── seed.ts                # Initial data seeding (idempotent + incremental)
├── dashboard/                 # Nuxt 3 SPA (Vue 3 + TypeScript + UnoCSS)
│   ├── nuxt.config.ts         # SPA mode, UnoCSS, Convex runtime config
│   ├── plugins/
│   │   └── convex.client.ts   # ConvexClient (WebSocket, real-time subscriptions)
│   ├── composables/
│   │   ├── useConvex.ts       # Reactive query/mutation composables (auto-update)
│   │   ├── useAuth.ts         # Cookie-based auth (30-day sessions)
│   │   ├── useToast.ts        # Global toast notifications
│   │   ├── useCurrentProject.ts # Project context from route slug
│   │   └── useAudienceJobs.ts # Audience research/import task tracking
│   ├── components/            # 18 shared components (auto-imported)
│   │   ├── VPageHeader.vue    # Page title + description + action slot
│   │   ├── VStatusBadge.vue   # Colored status pills
│   │   ├── VModal.vue         # Reusable modal (v-model, Escape, backdrop)
│   │   ├── VConfirmDialog.vue # Confirm action modal
│   │   ├── VDataTable.vue     # Table with loading/empty states + scoped slots
│   │   ├── VEmptyState.vue    # Empty state placeholder
│   │   ├── VChipInput.vue     # Array field input (Enter to add, X to remove)
│   │   ├── VFormField.vue     # Label + input slot + error message
│   │   ├── VToast.vue         # Toast container (auto-dismiss)
│   │   ├── EnrichmentProgressBar.vue  # Color-coded enrichment % bar
│   │   ├── EnrichmentFieldStatus.vue  # Field filled/empty + confidence
│   │   ├── EnrichmentTimeline.vue     # Enrichment audit history
│   │   ├── AudienceImportDialog.vue   # File upload with drag-and-drop
│   │   ├── AudienceResearchDialog.vue # Research trigger with options
│   │   ├── ProductForm.vue    # Product create/edit form
│   │   ├── FocusGroupForm.vue # Focus group form (accordion sections)
│   │   ├── CampaignForm.vue   # Multi-step campaign creation
│   │   └── TaskDetailModal.vue # Task detail with pipeline status
│   ├── pages/                 # 20+ pages (file-based routing)
│   └── tests/                 # 25 test files, 190 tests
├── .claude/skills/            # 70+ agent skill definitions
│   ├── audience-analysis-procedures/    # vibe-audience-parser agent
│   ├── audience-research-procedures/    # vibe-audience-researcher agent
│   ├── audience-enrichment-procedures/  # vibe-audience-enricher agent
│   ├── content-writing-procedures/      # vibe-content-writer agent
│   ├── content-review-procedures/       # vibe-content-reviewer agent
│   ├── image-generation-procedures/     # vibe-image-generator agent
│   ├── image-director-sales/           # vibe-image-director agent (sales)
│   ├── image-director-engagement/     # vibe-image-director agent (engagement)
│   ├── mbook-*/               # 14 marketing book skills (L1-L5 layer model)
│   └── ...                    # + community skills (vue, nuxt, convex, etc.)
├── scripts/
│   ├── invoke-agent.sh        # Agent invocation (Convex skill path resolution + heartbeat)
│   ├── resolve_service.py     # Service registry CLI resolver
│   ├── notify.py              # Telegram notification sender
│   ├── cx.sh                  # Convex CLI shortcut
│   └── docker/
│       └── init-postgres.sh   # Auto-create Convex DB
├── tests/                     # Python agent tests (95+ tests)
│   └── unit/
│       ├── test_parse_audience_doc.py   # 38 tests
│       ├── test_fuzzy_match.py          # 18 tests
│       ├── test_infer_awareness.py      # 15 tests
│       ├── test_infer_sophistication.py # 10 tests
│       ├── test_infer_purchase_behavior.py # 10 tests
│       └── test_extract_pdf_text.py     # 4 tests
├── docker-compose.yml         # Convex + Postgres
├── .env.example               # All environment variables
├── CLAUDE.md                  # Agent behavior contract
└── package.json
```

## Data Model

```
Projects → Products → Focus Groups (audience profiles)
        → Campaigns → Tasks → Content pipeline
                            → Documents
                            → Revisions
                            → Media assets

Agents → Skills (static + dynamic)
      → Agent runs (tracking)
      → Messages (inter-agent)

Services → Service categories (capabilities)
         → Agent service dependencies
```

## Content Pipeline

Each task progresses through a pipeline of agent steps:

```
backlog → researched → briefed → drafted → reviewed → humanized → completed
```

Pipeline execution is lock-based: agents acquire a lock, do their work, then call `completeStep` to advance. The pipeline engine handles:

- **Lock acquisition** with 10-minute stale lock detection
- **Step completion** with automatic status mapping
- **Revision requests** that reset to a target step
- **Parallel branches** triggered after specific main steps

### Pipeline Presets

| Pipeline | Steps | Use Case |
|----------|-------|----------|
| Research Only | keyword research → SERP analysis | Market research |
| Content Draft | research → brief → write → review → humanize | Standard articles |
| Full Content Production | above + hero image, social posts, email excerpt (parallel) | Multi-format content |
| Launch Package | above + landing page, email sequence, ad copy (parallel) | Product launches |
| Audience Discovery | research audiences → enrich profiles | New market audience research |
| Document Import | parse document → enrich profiles | Import existing audience docs |

## Focus Group Intelligence System

Automated audience research and enrichment pipeline:

**Flow A (0 to 1):** Research audiences from scratch using web search, Reddit, competitor analysis, and review mining. Generates 10-30 structured focus group profiles per product.

**Flow B (0.5 to 1):** Parse an uploaded audience document (.md, .txt, .docx, .pdf) into structured focus groups with fuzzy matching against existing records.

Both flows → staging review → approve/reject → import to production → continuous enrichment.

**Enrichment fields** (100-point weighted score):
- Awareness stage (15pt) — Schwartz 5-stage classification
- Purchase behavior (15pt) — buying triggers, price range, decision process
- Sophistication level (10pt) — market sophistication stages 1-5
- Content preferences (10pt) — formats, attention span, tone
- Influence sources (10pt) — trusted voices, media, platforms
- Competitor context (10pt) — current solutions, switch motivators
- Communication style (10pt) — formality, humor, story/data preference
- Negative triggers (10pt) — deal breakers, offensive topics, tone aversions
- Seasonal context (5pt) — peak interest periods, life events
- Awareness signals (5pt) — beliefs, objections, language signals

Core fields (awareness, sophistication, purchase behavior) use **deterministic keyword-matching scripts** — no LLM needed for the 3 highest-weight fields.

## Agent System

Agents are defined as skills in `.claude/skills/{agent-name}/SKILL.md`. When invoked:

1. Read SKILL.md for instructions
2. Check WORKING memory for state
3. Query Convex for assigned tasks
4. Execute work within project context
5. Call `pipeline:completeStep` when done
6. Update WORKING memory

Invoke an agent:
```bash
# Pipeline mode (with task)
./scripts/invoke-agent.sh vibe-content-writer <task-id>

# Heartbeat mode (scheduled check)
./scripts/invoke-agent.sh vibe-audience-enricher --heartbeat
```

### Registered Agents

| Agent | Model | Role |
|-------|-------|------|
| vibe-audience-researcher | opus | Research audiences from scratch |
| vibe-audience-parser | sonnet | Parse uploaded audience documents |
| vibe-audience-enricher | sonnet | Enrich focus group profiles (pipeline + weekly heartbeat) |

## Service Registry

Agents depend on capabilities, not specific services. The registry resolves the best available service:

```bash
# Find the best active service for a capability
python scripts/resolve_service.py seo_keywords
```

Categories include: SEO, scraping, social platforms, image/video generation, email, CMS publishing, content quality, analytics, notifications.

## Convex CLI Shortcut

```bash
# Run any Convex function
./scripts/cx.sh projects:list
./scripts/cx.sh tasks:listByProject '{"projectId":"abc123"}'
```

## Notifications

```bash
# Send a Telegram notification
python scripts/notify.py "Pipeline complete for campaign: summer-launch"
```

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| convex-backend | 3210 | Convex API server |
| convex-dashboard | 6791 | Convex admin dashboard |
| postgres | internal | PostgreSQL 17 (Convex storage) |

Additional self-hosted services (optional):
```bash
docker compose -f scripts/docker-compose.services.yml up -d
```
| Service | Port | Description |
|---------|------|-------------|
| crawl4ai | 11235 | Web scraping (self-hosted) |
| languagetool | 8081 | Grammar checking (self-hosted) |

## Development

```bash
# Watch mode (auto-deploys Convex functions on change)
npm run dev:convex

# Deploy once
npm run deploy:convex

# Full dev (Convex watch + dashboard)
npm run dev

# Run dashboard tests
cd dashboard && npx vitest run

# Run Python agent tests
pytest tests/unit/
```

## Key Design Decisions

- **Self-hosted Convex** over cloud Convex for cost control and data ownership
- **Real-time WebSocket subscriptions** via `ConvexClient` — dashboard updates instantly when agents write data
- **Action-based auth** because bcrypt requires Node.js runtime (not Convex's V8)
- **Internal queries for credentials** to prevent passwordHash exposure via public API
- **Capability-first service registry** so agents are decoupled from specific providers
- **Lock-based pipeline** to prevent concurrent step execution on the same task
- **Staging review gate** for audience imports — agents write to staging, humans approve
- **Deterministic enrichment** for core fields — keyword matching over LLM for speed and consistency
- **Idempotent seeding** so `seed:run` is safe to call multiple times
- **Marketing book layer model** (L1-L5) for structured copy generation using 14 extracted book skills

## License

Private.
