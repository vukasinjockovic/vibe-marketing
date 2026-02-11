# Vibe Marketing Platform — Installation Guide

## Quick Start

```bash
git clone <your-repo-url> vibe-marketing
cd vibe-marketing
bash scripts/setup.sh
```

The interactive setup script handles everything. Follow the prompts.

---

## Prerequisites

| Dependency | Version | Required |
|------------|---------|----------|
| Node.js | >= 22 | Yes |
| Docker + Docker Compose | Latest | Yes |
| nginx | Any | Recommended (reverse proxy) |
| certbot | Any | Optional (SSL via Let's Encrypt) |
| PM2 | >= 5 | Auto-installed by setup |

### OS Support

Tested on Ubuntu 22.04+ and Debian 12+. Should work on any Linux with Docker and Node.js 22+.

---

## What the Setup Script Does

The setup script (`scripts/setup.sh`) runs 8 phases:

### Phase 1: System Dependencies
- Checks for Node.js >= 22 (offers to install via nvm)
- Checks for Docker and Docker Compose
- Installs PM2 globally if missing
- Checks for nginx

### Phase 2: Environment Configuration
- Generates `.env` from `.env.example` with auto-generated secrets
- `CONVEX_DB_PASSWORD` — random 16-byte hex
- `CONVEX_INSTANCE_SECRET` — random 32-byte hex
- Prompts for optional API keys (SEO, scraping, social, image gen, etc.)

### Phase 3: Docker Services
- Starts Convex backend (port 3210), Postgres, and Convex dashboard (port 6791)
- Waits for Convex health check before proceeding

### Phase 4: Dependencies & Convex Deploy
- `npm install` for root and dashboard
- Deploys Convex schema and functions
- Optionally seeds the database with initial data (agents, service categories)

### Phase 5: Build & Start Dashboard
- Builds the Nuxt 3 dashboard for production
- Starts it via PM2 on port 3000
- Verifies it responds

### Phase 6: PM2 Startup Persistence
- Configures PM2 to auto-start on boot via systemd
- Saves the current process list

### Phase 7: Nginx Reverse Proxy (optional)
- Generates an nginx config for your domain
- Proxies: `/` → dashboard (3000), `/convex/` → API (3210), `/convex-http/` → HTTP actions (3211), `/convex-dashboard/` → admin (6791)
- Optionally obtains SSL via Let's Encrypt

### Phase 8: Self-Hosted Services (optional)
- Crawl4AI (web scraping, port 11235)
- LanguageTool (grammar checking, port 8081)

---

## Manual Installation

If you prefer to set things up manually instead of using the setup script:

### 1. Clone and install dependencies

```bash
git clone <your-repo-url> vibe-marketing
cd vibe-marketing
npm install
cd dashboard && npm install && cd ..
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
CONVEX_DB_PASSWORD=<run: openssl rand -hex 16>
CONVEX_INSTANCE_SECRET=<run: openssl rand -hex 32>
CONVEX_SELF_HOSTED_URL=http://localhost:3210
CONVEX_SELF_HOSTED_ADMIN_KEY=<set after first deploy>
```

### 3. Start Docker services

```bash
docker compose up -d
```

Wait for Convex to be healthy:

```bash
# Should return version JSON
curl http://localhost:3210/version
```

### 4. Deploy Convex

```bash
ADMIN_KEY=$(grep CONVEX_SELF_HOSTED_ADMIN_KEY .env | cut -d= -f2-)
npx convex deploy --url http://localhost:3210 --admin-key "$ADMIN_KEY" --yes
```

Seed the database:

```bash
npx convex run seed:run --url http://localhost:3210 --admin-key "$ADMIN_KEY"
```

### 5. Build and start the dashboard

```bash
cd dashboard && npx nuxt build && cd ..

# Install PM2 if needed
npm install -g pm2

# Start
pm2 start ecosystem.config.cjs
pm2 save
```

### 6. Configure PM2 auto-start

```bash
pm2 startup
# Run the sudo command it outputs, then:
pm2 save
```

### 7. Configure nginx (optional)

Create `/etc/nginx/sites-available/your-domain.com`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 300;
    }

    location /convex/ {
        proxy_pass http://127.0.0.1:3210/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 300;
    }

    location /convex-http/ {
        proxy_pass http://127.0.0.1:3211/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    location /convex-dashboard/ {
        proxy_pass http://127.0.0.1:6791/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
```

Enable and reload:

```bash
sudo ln -sf /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Get SSL:

```bash
sudo certbot --nginx -d your-domain.com
```

---

## Architecture

```
                    ┌─────────────┐
                    │   nginx     │ :443 (SSL)
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           │               │               │
    /      │    /convex/   │    /convex-    │
           │               │    dashboard/  │
           ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐    ┌──────────┐
    │  Nuxt 3  │   │  Convex  │    │  Convex  │
    │Dashboard │   │ Backend  │    │Dashboard │
    │ (PM2)    │   │ (Docker) │    │ (Docker) │
    │ :3000    │   │ :3210    │    │ :6791    │
    └──────────┘   └────┬─────┘    └──────────┘
                        │
                   ┌────┴─────┐
                   │ Postgres │
                   │ (Docker) │
                   │ :5432    │
                   └──────────┘
```

### Port Map

| Service | Port | Manager | Purpose |
|---------|------|---------|---------|
| Nuxt Dashboard | 3000 | PM2 | Web UI |
| Convex Backend | 3210 | Docker | Database API |
| Convex HTTP Actions | 3211 | Docker | Webhooks, HTTP endpoints |
| Convex Dashboard | 6791 | Docker | Admin UI |
| Postgres | 5432 | Docker | Convex storage |
| Crawl4AI | 11235 | Docker | Web scraping (optional) |
| LanguageTool | 8081 | Docker | Grammar checking (optional) |

### Process Management

| Component | Manager | Auto-restart | Survives reboot |
|-----------|---------|--------------|-----------------|
| Nuxt Dashboard | PM2 | Yes | Yes (pm2 startup) |
| Convex + Postgres | Docker | Yes (unless-stopped) | Yes (Docker daemon) |
| Crawl4AI, LanguageTool | Docker | Yes (unless-stopped) | Yes (Docker daemon) |

---

## Day-to-Day Commands

### Dashboard

```bash
pm2 status                    # Check process
pm2 logs vibe-dashboard       # View logs
pm2 restart vibe-dashboard    # Restart
pm2 stop vibe-dashboard       # Stop
```

### Rebuild after code changes

```bash
cd dashboard && npx nuxt build && cd ..
pm2 restart vibe-dashboard
```

### Convex

```bash
# Redeploy schema/functions
ADMIN_KEY=$(grep CONVEX_SELF_HOSTED_ADMIN_KEY .env | cut -d= -f2-)
npx convex deploy --url http://localhost:3210 --admin-key "$ADMIN_KEY" --yes

# View logs
docker compose logs -f convex-backend

# Restart
docker compose restart convex-backend
```

### Docker services

```bash
docker compose ps                # Status
docker compose logs -f           # All logs
docker compose restart           # Restart all
docker compose down              # Stop all
docker compose up -d             # Start all
```

### Self-hosted services

```bash
docker compose -f scripts/docker-compose.services.yml up -d    # Start
docker compose -f scripts/docker-compose.services.yml down      # Stop
docker compose -f scripts/docker-compose.services.yml logs -f   # Logs
```

---

## Troubleshooting

### 502 Bad Gateway
The dashboard isn't running. Check PM2:
```bash
pm2 status
pm2 logs vibe-dashboard
```
If stopped, restart: `pm2 restart vibe-dashboard`

### Dashboard won't start
Build may be stale or missing:
```bash
cd dashboard && npx nuxt build && cd ..
pm2 restart vibe-dashboard
```

### Convex connection refused
Check Docker:
```bash
docker compose ps
docker compose logs convex-backend
```

### Port already in use
```bash
# Find what's using a port
ss -tlnp | grep :3000
# Kill it
kill <PID>
```

### Reset everything
```bash
docker compose down -v          # Removes volumes (data loss!)
pm2 delete all
rm .env
bash scripts/setup.sh           # Start fresh
```
