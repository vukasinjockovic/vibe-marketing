#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Vibe Marketing Platform — Interactive Setup Script
# Installs and configures everything on a fresh Ubuntu/Debian server.
# Run: bash scripts/setup.sh
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Helpers ──
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }
step()    { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${NC}\n"; }

ask() {
  local prompt="$1" default="${2:-}"
  if [[ -n "$default" ]]; then
    read -rp "$(echo -e "${BOLD}$prompt${NC} [$default]: ")" answer
    echo "${answer:-$default}"
  else
    read -rp "$(echo -e "${BOLD}$prompt${NC}: ")" answer
    echo "$answer"
  fi
}

ask_yes_no() {
  local prompt="$1" default="${2:-y}"
  local answer
  answer=$(ask "$prompt (y/n)" "$default")
  [[ "${answer,,}" == "y" || "${answer,,}" == "yes" ]]
}

check_cmd() { command -v "$1" &>/dev/null; }

# ── Detect project root ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BOLD}${CYAN}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║       Vibe Marketing Platform Setup           ║"
echo "  ║       AI Marketing Automation                 ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  Project root: $PROJECT_ROOT"
echo ""

# ═══════════════════════════════════════════════════════════════
# PHASE 1: System Dependencies
# ═══════════════════════════════════════════════════════════════
step "Phase 1: System Dependencies"

# ── Node.js ──
if check_cmd node; then
  NODE_VERSION=$(node -v)
  success "Node.js $NODE_VERSION found"
  NODE_MAJOR=$(echo "$NODE_VERSION" | sed 's/v\([0-9]*\).*/\1/')
  if (( NODE_MAJOR < 22 )); then
    error "Node.js >= 22 required (found $NODE_VERSION)"
    if ask_yes_no "Install Node.js 22 via nvm?"; then
      if ! check_cmd nvm; then
        info "Installing nvm..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        # shellcheck disable=SC1091
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
      fi
      nvm install 22
      nvm use 22
      success "Node.js $(node -v) installed"
    else
      error "Cannot continue without Node.js >= 22"
      exit 1
    fi
  fi
else
  error "Node.js not found"
  if ask_yes_no "Install Node.js 22 via nvm?"; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    # shellcheck disable=SC1091
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm install 22
    success "Node.js $(node -v) installed"
  else
    error "Cannot continue without Node.js"
    exit 1
  fi
fi

# ── Docker ──
if check_cmd docker; then
  success "Docker $(docker --version | grep -oP '\d+\.\d+\.\d+')"
else
  error "Docker not found"
  if ask_yes_no "Install Docker?"; then
    info "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    success "Docker installed. You may need to log out and back in for group changes."
  else
    error "Cannot continue without Docker"
    exit 1
  fi
fi

if check_cmd docker && docker compose version &>/dev/null; then
  success "Docker Compose $(docker compose version --short 2>/dev/null || echo 'available')"
else
  warn "Docker Compose plugin not found. Install it: sudo apt install docker-compose-plugin"
fi

# ── PM2 ──
if check_cmd pm2; then
  success "PM2 $(pm2 -v) found"
else
  info "Installing PM2..."
  npm install -g pm2
  success "PM2 $(pm2 -v) installed"
fi

# ── nginx ──
NGINX_BIN=""
if check_cmd nginx; then
  NGINX_BIN="nginx"
elif [[ -x /usr/sbin/nginx ]]; then
  NGINX_BIN="/usr/sbin/nginx"
fi

if [[ -n "$NGINX_BIN" ]]; then
  success "nginx $($NGINX_BIN -v 2>&1 | grep -oP '[\d.]+')"
else
  warn "nginx not found"
  if ask_yes_no "Install nginx?"; then
    sudo apt update && sudo apt install -y nginx
    success "nginx installed"
  else
    warn "Skipping nginx — you'll need to configure a reverse proxy manually"
  fi
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 2: Environment Configuration
# ═══════════════════════════════════════════════════════════════
step "Phase 2: Environment Configuration"

if [[ -f .env ]]; then
  warn ".env file already exists"
  if ask_yes_no "Reconfigure .env?" "n"; then
    CONFIGURE_ENV=true
  else
    CONFIGURE_ENV=false
    success "Keeping existing .env"
  fi
else
  CONFIGURE_ENV=true
fi

if [[ "$CONFIGURE_ENV" == "true" ]]; then
  info "Generating secrets..."

  CONVEX_DB_PASSWORD=$(openssl rand -hex 16)
  CONVEX_INSTANCE_SECRET=$(openssl rand -hex 32)

  cat > .env <<EOF
# ═══════════════════════════════════════
# Convex Self-Hosted (auto-generated)
# ═══════════════════════════════════════
CONVEX_DB_PASSWORD=$CONVEX_DB_PASSWORD
CONVEX_INSTANCE_SECRET=$CONVEX_INSTANCE_SECRET
CONVEX_SELF_HOSTED_URL=http://localhost:3210
CONVEX_SELF_HOSTED_ADMIN_KEY=placeholder_will_be_set_after_first_deploy
EOF

  success ".env created with generated secrets"

  echo ""
  info "Optional API keys (press Enter to skip any):"
  echo ""

  # Read optional keys from .env.example (skip Convex section and empty lines)
  declare -A OPTIONAL_KEYS
  if [[ -f .env.example ]]; then
    while IFS= read -r line; do
      # Skip comments, empty lines, and Convex keys (already handled)
      [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
      [[ "$line" =~ ^CONVEX_ ]] && continue

      KEY=$(echo "$line" | cut -d= -f1)
      CURRENT_VAL=$(echo "$line" | cut -d= -f2-)

      if [[ -z "$CURRENT_VAL" ]]; then
        VALUE=$(ask "  $KEY" "")
        if [[ -n "$VALUE" ]]; then
          echo "$KEY=$VALUE" >> .env
        fi
      fi
    done < .env.example
  fi

  success "Environment configured"
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 3: Docker Services (Convex + Postgres)
# ═══════════════════════════════════════════════════════════════
step "Phase 3: Docker Services"

info "Starting Convex backend, Postgres, and Convex dashboard..."
docker compose up -d 2>&1 | tail -5
echo ""

# Wait for Convex to be healthy
info "Waiting for Convex backend to be healthy..."
RETRIES=0
MAX_RETRIES=30
while ! curl -sf http://localhost:3210/version &>/dev/null; do
  RETRIES=$((RETRIES + 1))
  if (( RETRIES >= MAX_RETRIES )); then
    error "Convex backend did not start within ${MAX_RETRIES}s"
    error "Check: docker compose logs convex-backend"
    exit 1
  fi
  sleep 2
  echo -n "."
done
echo ""
success "Convex backend is healthy"

# ═══════════════════════════════════════════════════════════════
# PHASE 4: Install Dependencies + Deploy Convex
# ═══════════════════════════════════════════════════════════════
step "Phase 4: Dependencies & Convex Deploy"

info "Installing root dependencies..."
npm install 2>&1 | tail -3

info "Installing dashboard dependencies..."
(cd dashboard && npm install 2>&1 | tail -3)

# Source .env for admin key
set -a
# shellcheck disable=SC1091
source .env
set +a

info "Deploying Convex schema and functions..."
rm -rf convex/dist  # Prevent TS5055 stale build artifact errors
ADMIN_KEY=$(grep CONVEX_SELF_HOSTED_ADMIN_KEY .env | cut -d= -f2-)
npx convex deploy --url http://localhost:3210 --admin-key "$ADMIN_KEY" --yes 2>&1 | tail -5
success "Convex deployed"

# Run seed data
if ask_yes_no "Seed database with initial data (service categories, agents, etc.)?"; then
  info "Seeding database..."
  npx convex run seed:run --url http://localhost:3210 --admin-key "$ADMIN_KEY" 2>&1 | tail -3
  success "Database seeded"
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 5: Build & Start Dashboard
# ═══════════════════════════════════════════════════════════════
step "Phase 5: Build & Start Dashboard"

info "Building Nuxt dashboard for production..."
(cd dashboard && npx nuxt build 2>&1 | tail -5)
success "Dashboard built"

info "Starting dashboard via PM2..."
pm2 delete vibe-dashboard 2>/dev/null || true
pm2 start ecosystem.config.cjs 2>&1 | tail -5
echo ""

# Verify
sleep 2
if curl -sf -o /dev/null http://127.0.0.1:3000/; then
  success "Dashboard running on port 3000"
else
  error "Dashboard failed to start — check: pm2 logs vibe-dashboard"
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 6: PM2 Startup (survive reboots)
# ═══════════════════════════════════════════════════════════════
step "Phase 6: PM2 Startup Persistence"

info "Configuring PM2 to start on boot..."
PM2_STARTUP_CMD=$(pm2 startup 2>&1 | grep "sudo" | head -1)

if [[ -n "$PM2_STARTUP_CMD" ]]; then
  echo ""
  info "PM2 needs to run the following command with sudo:"
  echo -e "  ${YELLOW}$PM2_STARTUP_CMD${NC}"
  echo ""
  if ask_yes_no "Run this command now?"; then
    eval "$PM2_STARTUP_CMD"
    pm2 save
    success "PM2 will auto-start on boot"
  else
    warn "Run the command above manually to enable auto-start"
  fi
else
  pm2 save
  success "PM2 startup configured"
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 7: Nginx Configuration (optional)
# ═══════════════════════════════════════════════════════════════
step "Phase 7: Nginx Reverse Proxy (optional)"

DOMAIN=$(ask "Domain name for the dashboard (or 'skip')" "skip")

if [[ "$DOMAIN" != "skip" ]]; then
  NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"

  cat > /tmp/vibe-nginx.conf <<NGINX_EOF
# Vibe Marketing Platform — $DOMAIN
# Generated by scripts/setup.sh

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name $DOMAIN;

    # SSL — update paths after running certbot or placing certs
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    client_max_body_size 100M;

    # Nuxt dashboard
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 300;
    }

    # Convex client API
    location /convex/ {
        proxy_pass http://127.0.0.1:3210/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        proxy_read_timeout 300;
    }

    # Convex HTTP actions
    location /convex-http/ {
        proxy_pass http://127.0.0.1:3211/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
    }

    # Convex dashboard (admin)
    location /convex-dashboard/ {
        proxy_pass http://127.0.0.1:6791/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
NGINX_EOF

  info "Nginx config written to /tmp/vibe-nginx.conf"

  if ask_yes_no "Install nginx config now (requires sudo)?"; then
    sudo cp /tmp/vibe-nginx.conf "$NGINX_CONF"
    sudo ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/$DOMAIN"
    sudo nginx -t 2>&1 && sudo systemctl reload nginx
    success "Nginx configured for $DOMAIN"

    # SSL via certbot
    if check_cmd certbot; then
      if ask_yes_no "Obtain SSL certificate via Let's Encrypt?"; then
        sudo certbot --nginx -d "$DOMAIN"
        success "SSL certificate installed"
      fi
    else
      warn "certbot not found — install it for SSL: sudo apt install certbot python3-certbot-nginx"
    fi
  else
    info "Copy the config manually:"
    echo "  sudo cp /tmp/vibe-nginx.conf $NGINX_CONF"
    echo "  sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/$DOMAIN"
    echo "  sudo nginx -t && sudo systemctl reload nginx"
  fi
else
  info "Skipping nginx config. Dashboard available at http://localhost:3000"
fi

# ═══════════════════════════════════════════════════════════════
# PHASE 8: Self-Hosted Services (optional)
# ═══════════════════════════════════════════════════════════════
step "Phase 8: Self-Hosted Services (optional)"

info "Optional self-hosted services (free, run in Docker):"
echo "  - Crawl4AI: Web scraping (port 11235)"
echo "  - LanguageTool: Grammar/spell checking (port 8081)"
echo ""

if ask_yes_no "Start self-hosted services?"; then
  docker compose -f scripts/docker-compose.services.yml up -d 2>&1 | tail -5
  success "Self-hosted services started"
else
  info "Skipping — start later with: docker compose -f scripts/docker-compose.services.yml up -d"
fi

# ═══════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════
echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║         Setup Complete!                       ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  Services running:"
echo "    Dashboard:        http://localhost:3000"
echo "    Convex API:       http://localhost:3210"
echo "    Convex Dashboard: http://localhost:6791"
if [[ "$DOMAIN" != "skip" ]]; then
  echo "    Public URL:       https://$DOMAIN"
fi
echo ""
echo "  Management commands:"
echo "    pm2 status              — check dashboard process"
echo "    pm2 logs vibe-dashboard — view dashboard logs"
echo "    pm2 restart all         — restart dashboard"
echo "    docker compose ps       — check Docker services"
echo "    docker compose logs -f  — view Docker logs"
echo ""
echo "  Next steps:"
echo "    1. Create an admin user in the Convex dashboard (http://localhost:6791)"
echo "    2. Configure API keys in .env for the services you need"
echo "    3. Start creating projects and campaigns"
echo ""
