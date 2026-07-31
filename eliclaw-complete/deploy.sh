#!/bin/bash
# EliClaw Deployment Script for Hostinger VPS
# Domain: eliclaw.virtualabdigital.com

set -e

echo "🚀 Starting EliClaw deployment..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Update system
echo -e "${BLUE}Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
sudo apt install -y nginx certbot python3-certbot-nginx     nodejs npm postgresql postgresql-contrib ufw fail2ban git

# Create user and directories
echo -e "${BLUE}Setting up directories...${NC}"
sudo useradd -m -s /bin/bash eliclaw 2>/dev/null || true
sudo mkdir -p /home/eliclaw/app
sudo chown -R eliclaw:eliclaw /home/eliclaw/app

# Setup PostgreSQL
echo -e "${BLUE}Configuring PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE USER eliclaw_user WITH PASSWORD 'your_secure_password';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE eliclaw_db OWNER eliclaw_user;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE eliclaw_db TO eliclaw_user;" 2>/dev/null || true

# Clone or copy project
echo -e "${BLUE}Deploying application...${NC}"
# If using git:
# cd /home/eliclaw/app && sudo -u eliclaw git clone https://github.com/yourrepo/eliclaw.git .
# Or copy files manually to /home/eliclaw/app

# Install server dependencies
cd /home/eliclaw/app/server
sudo -u eliclaw npm install

# Install PM2 globally
sudo npm install -g pm2

# Setup environment
echo -e "${BLUE}Setting up environment...${NC}"
cat > /home/eliclaw/app/server/.env << 'EOF'
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://eliclaw_user:your_secure_password@localhost:5432/eliclaw_db
JWT_SECRET=eliclaw_super_secret_key_change_this_$(date +%s)
WP_API_KEY=eliclaw_wp_bridge_key_virtualab_$(date +%s)
AGENCY_DOMAIN=virtualabdigital.com
ELICLAW_DOMAIN=eliclaw.virtualabdigital.com
EOF
sudo chown eliclaw:eliclaw /home/eliclaw/app/server/.env

# Build client
echo -e "${BLUE}Building client...${NC}"
cd /home/eliclaw/app/client
sudo -u eliclaw npm install
sudo -u eliclaw npm run build
sudo -u eliclaw cp -r dist /home/eliclaw/app/server/public

# Setup Nginx
echo -e "${BLUE}Configuring Nginx...${NC}"
sudo cp /home/eliclaw/app/server/nginx.conf /etc/nginx/sites-available/eliclaw.virtualabdigital.com
sudo ln -sf /etc/nginx/sites-available/eliclaw.virtualabdigital.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL Certificate
echo -e "${BLUE}Setting up SSL...${NC}"
sudo certbot --nginx -d eliclaw.virtualabdigital.com -d api.eliclaw.virtualabdigital.com --non-interactive --agree-tos --email admin@virtualabdigital.com

# Firewall
echo -e "${BLUE}Configuring firewall...${NC}"
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

# Start with PM2
echo -e "${BLUE}Starting application...${NC}"
cd /home/eliclaw/app/server
sudo -u eliclaw pm2 start server.js --name eliclaw-api
sudo -u eliclaw pm2 startup systemd
sudo -u eliclaw pm2 save

# Setup auto-renewal for SSL
echo -e "${BLUE}Setting up SSL auto-renewal...${NC}"
(sudo crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl restart nginx'") | sudo crontab -

echo -e "${GREEN}✅ EliClaw deployed successfully!${NC}"
echo -e "${GREEN}🌐 https://eliclaw.virtualabdigital.com${NC}"
echo -e "${GREEN}🏢 Agency: https://virtualabdigital.com${NC}"
echo ""
echo "Next steps:"
echo "1. Update DNS: Point eliclaw.virtualabdigital.com to this VPS IP"
echo "2. Update WP_API_KEY in .env and WordPress plugin"
echo "3. Test the WordPress bridge connection"
echo "4. Monitor logs: sudo -u eliclaw pm2 logs eliclaw-api"