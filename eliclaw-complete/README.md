# EliClaw 2.0 — Agent OS

**Domain:** https://eliclaw.virtualabdigital.com  
**Agency:** https://virtualabdigital.com  
**API:** https://api.eliclaw.virtualabdigital.com

## Complete AI-Powered Digital Growth Platform

### Architecture
```
virtualabdigital.com (WordPress)  ←→  eliclaw.virtualabdigital.com (Agent OS)
     │                                          │
     │    [WP Plugin] ──API──► [Node.js API]   │
     │                                          │
     └────────── Leads, Audits, Analytics ──────┘
```

### Tools
| Tool | Endpoint | Status |
|------|----------|--------|
| SEO Audit | `/tools/seo` | Full |
| Competitor Analysis | `/tools/competitor` | Full |
| Website Analyzer | `/tools/analyzer` | Full |
| Automation Workflows | `/tools/automation` | Full |
| Content Analysis | `/tools/content` | Full |
| Swarm Agent | `/tools/swarm` | Full |

### Tech Stack
- **Frontend:** React 18 + Vite + Tailwind CSS + Framer Motion
- **Backend:** Node.js + Express + PostgreSQL
- **Auth:** JWT (custom, no OAuth issues)
- **Hosting:** Hostinger VPS (Ubuntu) + Nginx + PM2

### Deployment
```bash
# 1. Upload files to VPS
scp -r eliclaw/ root@YOUR_VPS_IP:/home/

# 2. Run deployment script
ssh root@YOUR_VPS_IP
chmod +x /home/eliclaw/deploy.sh
./deploy.sh

# 3. Update DNS
# Point eliclaw.virtualabdigital.com → VPS IP
```

### WordPress Integration
1. Upload `wordpress-plugin/eliclaw-bridge.php` to `/wp-content/plugins/`
2. Activate in WP Admin
3. Enter API key from EliClaw Settings
4. Use shortcodes: `[eliclaw_audit]`, `[eliclaw_tools_link]`

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| POST | `/api/leads` | Capture lead from WP |
| POST | `/api/tools/seo-audit` | Run SEO audit |
| POST | `/api/tools/competitor-analysis` | Competitor comparison |
| POST | `/api/tools/website-analyzer` | Technical analysis |
| POST | `/api/tools/content-analysis` | Content scoring |
| GET | `/api/dashboard/stats` | Dashboard data |

### Environment Variables
```env
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/eliclaw_db
JWT_SECRET=your-secret-key
WP_API_KEY=your-wp-bridge-key
```

---
Built with love by Virtualab Digital

## 🚀 New Integrations Added

### 1. Real SEO Audit APIs
- **Google PageSpeed Insights** — Core Web Vitals, performance scoring
- **Ahrefs API** — Domain rating, backlinks, organic traffic
- **SEMrush API** — Keyword rankings, competitor data
- **Moz API** — Domain authority, page authority
- **Cheerio crawler** — On-page SEO analysis (always active)

### 2. Email Automation
- **Resend** (recommended) — Modern email API
- **SendGrid** — Enterprise email delivery
- **SMTP fallback** — Any email provider
- **Templates:** Welcome, Audit Report, Lead Notification, Weekly Report, Competitor Alert
- **Scheduled:** Weekly reports every Monday at 9 AM

### 3. Stripe Payments
- **Plans:** Free ($0), Starter ($29/mo), Pro ($79/mo), Agency ($199/mo)
- **Features:** Checkout, Customer Portal, Webhooks, Auto-renewal
- **Usage tracking:** Per-feature limits per plan

### 4. Custom Branding
- **Virtualab Digital colors** — Indigo/purple gradient palette
- **Logo animations** — Pulse effect
- **Glow effects** — Branded shadows
- **Agency badge** — "by Virtualab Digital" styling

### 5. Extended Swarm Agents (100+)
From 6 core agents to 100+ specialized agents:
- **Link Building:** Backlink, PR Outreach, Guest Post, Broken Link, Internal Link
- **Local SEO:** Local SEO, Citation Builder, Review Monitor
- **Technical:** Core Web Vitals, Speed Optimizer, Security, Mobile-First, Accessibility
- **Content:** Content Gap, Prune, Refresh, AI Content, FAQ, Quality
- **Keywords:** Keyword Cluster, Voice Search, SERP Features, Trends
- **E-commerce:** E-commerce, Price Monitor
- **Video/Media:** Video SEO, Podcast SEO, Web Stories
- **Industry-Specific:** SaaS, Real Estate, Restaurant, Healthcare, Legal, News
- **Advanced:** Traffic Analyzer, Competitor Alerts, AI Search, Voice Assistant

## 📋 Setup Checklist

### Step 1: VPS Setup
```bash
# Upload project
scp -r eliclaw/ root@YOUR_VPS_IP:/home/

# SSH in and deploy
ssh root@YOUR_VPS_IP
chmod +x /home/eliclaw/deploy.sh
./deploy.sh
```

### Step 2: Configure Environment
```bash
cd /home/eliclaw/server
cp .env.example .env
nano .env
# Fill in your API keys
```

### Step 3: DNS
- `eliclaw.virtualabdigital.com` → A record → VPS IP
- `api.eliclaw.virtualabdigital.com` → A record → VPS IP

### Step 4: SSL
```bash
sudo certbot --nginx -d eliclaw.virtualabdigital.com -d api.eliclaw.virtualabdigital.com
```

### Step 5: WordPress Plugin
1. Upload `wordpress-plugin/eliclaw-bridge.php`
2. Activate in WP Admin
3. Go to Settings → EliClaw
4. Enter API key from EliClaw Settings page
5. Add `[eliclaw_audit]` shortcode to any page

### Step 6: Stripe (Optional - for payments)
1. Create account at stripe.com
2. Create products: Starter ($29), Pro ($79), Agency ($199)
3. Copy price IDs to `.env`
4. Add webhook endpoint: `https://eliclaw.virtualabdigital.com/api/stripe/webhook`

### Step 7: Email (Optional - for automation)
1. Create account at resend.com (recommended)
2. Verify domain: `eliclaw.virtualabdigital.com`
3. Copy API key to `.env`

### Step 8: SEO APIs (Optional - for real data)
1. Get PageSpeed API key (free): https://developers.google.com/speed/docs/insights/v5/get-started
2. Add to `.env`
3. Without keys, system uses intelligent mock data

## 🔧 File Structure

```
eliclaw/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/        # Layout, Sidebar, Header
│   │   ├── pages/            # All tool pages + Pricing
│   │   ├── context/          # Auth store
│   │   └── utils/            # API helpers
│   ├── package.json
│   └── vite.config.js
├── server/                    # Node.js backend
│   ├── server.js             # Original server
│   ├── server-enhanced.js    # Full integrations server
│   ├── .env                  # Production config
│   ├── .env.example          # All available options
│   ├── nginx.conf            # Nginx config
│   └── package.json
├── integrations/            # Third-party services
│   ├── seo-audit-engine.js   # PageSpeed, Ahrefs, SEMrush, Moz
│   ├── email-service.js      # Resend, SendGrid, SMTP
│   └── stripe-service.js     # Payments & subscriptions
├── email-templates/          # HTML email templates
│   ├── welcome.js
│   ├── audit-report.js
│   ├── lead-notification.js
│   ├── weekly-report.js
│   └── competitor-alert.js
├── agents/                   # Swarm agent definitions
│   └── extended-agents.js    # 100+ agent types
├── branding/                 # Virtualab Digital branding
│   └── virtualab-branding.css
├── wordpress-plugin/         # WP integration
│   └── eliclaw-bridge.php
├── deploy.sh                 # One-command deployment
└── README.md
```

## 🌐 Domains

| Service | URL |
|---------|-----|
| EliClaw App | https://eliclaw.virtualabdigital.com |
| API | https://api.eliclaw.virtualabdigital.com |
| Agency | https://virtualabdigital.com |

## 📞 Support

Built with ❤️ by **Virtualab Digital**
- Website: https://virtualabdigital.com
- EliClaw: https://eliclaw.virtualabdigital.com
