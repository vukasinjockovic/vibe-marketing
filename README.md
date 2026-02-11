# Vibe Marketing

AI marketing automation platform. 30+ specialized Claude Code agents research, create, review, and publish marketing content across projects, products, and campaigns.

## Architecture

```
                    ┌─────────────────┐
                    │  Nuxt Dashboard  │  :3000
                    │  (Vue 3 + TS)   │
                    └────────┬────────┘
                             │
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

# Or use the init profile (does deploy + seed in one shot)
docker compose --profile init up convex-init
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

**Dashboard pages:** Dashboard home, Projects, Agents, Services, Activity log.

## Project Structure

```
vibe-marketing/
├── convex/                    # Convex backend (19 modules, 94+ functions)
│   ├── schema.ts              # Database schema (27 tables, 58 indexes)
│   ├── auth.ts                # Email/password auth + sessions
│   ├── admin.ts               # Admin user management
│   ├── projects.ts            # Project CRUD
│   ├── products.ts            # Product CRUD
│   ├── campaigns.ts           # Campaign CRUD + lifecycle
│   ├── tasks.ts               # Task CRUD + assignment
│   ├── pipeline.ts            # Pipeline execution engine (locks, steps, revisions)
│   ├── agents.ts              # Agent registry + heartbeat
│   ├── focusGroups.ts         # Audience profiles
│   ├── messages.ts            # Agent-to-agent messaging
│   ├── activities.ts          # Activity logging
│   ├── notifications.ts       # Agent notifications
│   ├── documents.ts           # Content documents
│   ├── revisions.ts           # Content revision tracking
│   ├── services.ts            # Service registry + capability resolver
│   ├── analytics.ts           # Agent runs, metrics, reports
│   ├── pipelines.ts           # Pipeline templates
│   └── seed.ts                # Initial data seeding (idempotent)
├── dashboard/                 # Nuxt 3 SPA (Vue 3 + TypeScript + UnoCSS)
│   ├── nuxt.config.ts         # SPA mode, UnoCSS, Convex runtime config
│   ├── plugins/
│   │   └── convex.client.ts   # ConvexHttpClient provider (browser-only)
│   ├── composables/
│   │   ├── useConvex.ts       # Convex query/mutation/action composables
│   │   └── useAuth.ts         # Cookie-based auth (30-day sessions)
│   ├── middleware/
│   │   └── auth.global.ts     # Auto-redirect to /login if unauthenticated
│   ├── layouts/
│   │   ├── default.vue        # Sidebar navigation + user info
│   │   └── auth.vue           # Centered login layout
│   └── pages/
│       ├── login.vue          # Email/password login
│       ├── index.vue          # Dashboard home (stats + activity)
│       ├── projects/index.vue # Project grid
│       ├── agents.vue         # Agent table (status, model, tasks)
│       ├── services.vue       # Service registry by category
│       └── activity.vue       # Activity log
├── scripts/
│   ├── invoke-agent.sh        # Agent invocation wrapper
│   ├── resolve_service.py     # Service registry CLI resolver
│   ├── notify.py              # Telegram notification sender
│   ├── cx.sh                  # Convex CLI shortcut
│   └── docker/
│       └── init-postgres.sh   # Auto-create Convex DB
├── docker-compose.yml         # Convex + Postgres + Dashboard
├── .claude/skills/            # 70+ agent skill definitions
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

## Agent System

Agents are defined as skills in `.claude/skills/{agent-name}/SKILL.md`. When invoked:

1. Read SKILL.md for instructions
2. Check WORKING memory for state
3. Query Convex for assigned tasks
4. Execute work within project context
5. Call `pipeline:completeStep` when done
6. Update WORKING memory

Invoke an agent manually:
```bash
./scripts/invoke-agent.sh vibe-content-writer <task-id>
```

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
```

## Key Design Decisions

- **Self-hosted Convex** over cloud Convex for cost control and data ownership
- **Action-based auth** because bcrypt requires Node.js runtime (not Convex's V8)
- **Internal queries for credentials** to prevent passwordHash exposure via public API
- **Capability-first service registry** so agents are decoupled from specific providers
- **Lock-based pipeline** to prevent concurrent step execution on the same task
- **Idempotent seeding** so `seed:run` is safe to call multiple times

## License

Private.
