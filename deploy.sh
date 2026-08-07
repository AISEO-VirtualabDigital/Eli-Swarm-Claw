#!/usr/bin/env bash
#
# deploy.sh — Deploy Eli MicroSaaS to production VPS
# Usage: ./deploy.sh <SERVER_IP> [SSH_USER]
#   SSH_USER defaults to 'root'
#
# Prerequisites on your LOCAL machine:
#   - bun installed
#   - rsync installed
#   - SSH key access to the server (passwordless)
#
# What this does:
#   1. Builds the Next.js standalone app locally
#   2. Rsyncs the standalone build + data + db to /opt/eli/ on the server
#   3. Installs bun on the server if missing
#   4. Creates a systemd service (eli.service)
#   5. Installs/configures Caddy with auto-HTTPS for eli.virtuabaldigital.com
#   6. Starts everything
#

set -euo pipefail

# ─── Config ───────────────────────────────────────────────
SERVER_IP="${1:?Usage: ./deploy.sh <SERVER_IP> [SSH_USER]}"
SSH_USER="${2:-root}"
REMOTE="$SSH_USER@$SERVER_IP"
DEPLOY_DIR="/opt/eli"
DOMAIN="eli.virtuabaldigital.com"
SERVICE_NAME="eli"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[deploy]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }
err()  { echo -e "${RED}[error]${NC} $1" >&2; exit 1; }

# ─── Step 1: Build locally ───────────────────────────────
log "Step 1/6: Building Next.js standalone..."
cd "$(dirname "$0")"

# Install deps if needed
if [ ! -d "node_modules" ]; then
  bun install
fi

# Build
NODE_ENV=production bun run build || err "Build failed. Fix TypeScript errors first."
log "  Build complete."

# ─── Step 2: Prepare deploy directory on server ──────────
log "Step 2/6: Preparing remote server..."
ssh "$REMOTE" bash -s <<REMOTE_SETUP
set -e

# Create deploy directory structure
mkdir -p $DEPLOY_DIR/{data/uploads/knowledge-sources,data/uploads/docs,data/uploads/design,data/uploads/zips,db,logs}

# Install bun if missing
if ! command -v bun &>/dev/null; then
  echo "  Installing bun..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="\$HOME/.bun/bin:\$PATH"
fi

echo "  Server prepared."
REMOTE_SETUP

# ─── Step 3: Rync files to server ────────────────────────
log "Step 3/6: Syncing files to server..."

# Sync standalone build (exclude dev artifacts)
rsync -az --delete \
  --exclude='node_modules' \
  --exclude='.next/cache' \
  --exclude='dev.log' \
  --exclude='server.log' \
  .next/standalone/ "$REMOTE:$DEPLOY_DIR/app/"

# Sync knowledge-sources (the brain — 163+ files)
log "  Syncing knowledge base..."
rsync -az --delete \
  data/uploads/knowledge-sources/ "$REMOTE:$DEPLOY_DIR/data/uploads/knowledge-sources/"

# Sync database
log "  Syncing database..."
rsync -az db/custom.db "$REMOTE:$DEPLOY_DIR/db/custom.db"

# Sync public assets (logo, robots.txt)
rsync -az public/ "$REMOTE:$DEPLOY_DIR/app/public/"

log "  Files synced."

# ─── Step 4: Create systemd service ──────────────────────
log "Step 4/6: Setting up systemd service..."
ssh "$REMOTE" bash -s <<SERVICE_SETUP
set -e

cat > /etc/systemd/system/${SERVICE_NAME}.service <<'UNIT'
[Unit]
Description=Eli MicroSaaS — AI Growth Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/eli/app
Environment=NODE_ENV=production
Environment=DATABASE_URL=file:/opt/eli/data/custom.db
Environment=KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources
Environment=KEYWORD_DIR=/opt/eli/data/keyword-research
Environment=OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault
Environment=PORT=3000
Environment=GEMINI_API_KEY=${GEMINI_API_KEY:-}
Environment=OPENINBOX_API_KEY=${OPENINBOX_API_KEY:-}
Environment=ELI_INTRO_VIDEO_URL=${ELI_INTRO_VIDEO_URL:-}
ExecStart=/root/.bun/bin/bun .next/standalone/server.js
Restart=always
RestartSec=5
StandardOutput=append:/opt/eli/logs/eli.log
StandardError=append:/opt/eli/logs/eli-error.log

[Install]
WantedBy=multi-user.target
UNIT

# Fix the ExecStart path — standalone server.js is at the app root
sed -i 's|ExecStart=/root/.bun/bin/bun .next/standalone/server.js|ExecStart=/root/.bun/bin/bun server.js|' /etc/systemd/system/${SERVICE_NAME}.service

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
echo "  Service installed."
SERVICE_SETUP

# ─── Step 5: Configure Caddy ─────────────────────────────
log "Step 5/6: Configuring Caddy with auto-HTTPS for ${DOMAIN}..."
ssh "$REMOTE" bash -s <<CADDY_SETUP
set -e

# Install Caddy if missing
if ! command -v caddy &>/dev/null; then
  echo "  Installing Caddy..."
  apt-get update -qq
  apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https curl
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -qq
  apt-get install -y -qq caddy
fi

# Write Caddyfile for Eli
mkdir -p /etc/caddy
cat > /etc/caddy/Caddyfile <<'CADDYFILE'
{
        # Global options
        email admin@virtuabaldigital.com
}

eli.virtuabaldigital.com {
        reverse_proxy localhost:3000 {
                header_up Host {host}
                header_up X-Forwarded-For {remote_host}
                header_up X-Forwarded-Proto {scheme}
                header_up X-Real-IP {remote_host}
        }

        # Static files cache
        @static path /logo.svg /robots.txt
        header @static Cache-Control "public, max-age=86400"

        # Security headers (Caddy adds HSTS automatically)
        header {
                X-Frame-Options "DENY"
                X-Content-Type-Options "nosniff"
                Referrer-Policy "strict-origin-when-cross-origin"
        }
}
CADDYFILE

echo "  Caddy configured."
CADDY_SETUP

# ─── Step 6: Start everything ────────────────────────────
log "Step 6/6: Starting Eli..."
ssh "$REMOTE" bash -s <<STARTUP
set -e

# Restart Eli
systemctl restart ${SERVICE_NAME}
sleep 2

# Check status
if systemctl is-active --quiet ${SERVICE_NAME}; then
  echo "  Eli is RUNNING."
else
  echo "  Eli FAILED to start. Checking logs:"
  journalctl -u ${SERVICE_NAME} --no-pager -n 20
  exit 1
fi

# Restart Caddy to pick up new config
systemctl restart caddy
sleep 2

if systemctl is-active --quiet caddy; then
  echo "  Caddy is RUNNING."
else
  echo "  Caddy FAILED. Checking logs:"
  journalctl -u caddy --no-pager -n 20
  exit 1
fi

# Health check
echo "  Running health check..."
HEALTH=\$(curl -sf http://localhost:3000/api/health 2>/dev/null || echo '{}')
echo "  Health: \$HEALTH"
STARTUP

echo ""
log "═══════════════════════════════════════════════"
log "  Eli deployed successfully!"
log "  URL: https://${DOMAIN}"
log "  Health: https://${DOMAIN}/api/health"
log "  SSH: ssh ${SSH_USER}@${SERVER_IP}"
log "  Logs: ssh ${SSH_USER}@${SERVER_IP} 'journalctl -u eli -f'"
log "═══════════════════════════════════════════════"
