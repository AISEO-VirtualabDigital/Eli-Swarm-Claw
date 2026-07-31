# Eli Claw - AI Search Intelligence SaaS

**Domain:** https://eliclaw.virtualabdigital.com  
**Agency:** https://virtualabdigital.com  
**API:** https://api.eliclaw.virtualabdigital.com

## Overview

Eli Claw is an **AI Search Intelligence SaaS platform** that combines traditional SEO tools with AI-powered optimization, entity mapping, and citation monitoring. Built by Virtualab Digital.

## Core Features

1. **Technical SEO Auditing** - Crawl websites, discover issues, get prioritized recommendations
2. **Keyword Research** - Expand keywords, cluster topics, identify opportunities
3. **Entity & Topic Graph** - Map semantic relationships, track entity coverage
4. **Asset Registry** - Track all content assets across channels
5. **Indexing & Discovery** - Compliant URL submission, sitemap generation, IndexNow
6. **AI Citation Monitoring** - Track brand mentions in AI-generated answers
7. **Content Brief Generator** - Create SEO/GEO-ready content briefs
8. **Competitor Intelligence** - Analyze competitor strategies and gaps
9. **Recommendation Engine** - Prioritized action items with impact/effort scoring
10. **Multi-Agent System** - CrewAI-powered agents for automation

## Tech Stack

### Backend
- **FastAPI** - Modern Python API framework
- **PostgreSQL** - Primary database
- **SQLAlchemy/SQLModel** - ORM and data modeling
- **Alembic** - Database migrations
- **Redis** - Queue and cache (planned)
- **CrewAI** - Multi-agent orchestration

### Frontend (Planned)
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD
- **Nginx** - Reverse proxy
- **PM2** - Process manager (legacy)

## Project Structure

```
Eli-Swarm-Claw/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/           # API routes
│   │   │   ├── core/          # Config, security, deps
│   │   │   ├── models/        # SQLAlchemy models
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── services/      # Business logic
│   │   │   ├── agents/        # CrewAI agents
│   │   │   ├── workers/       # Background tasks
│   │   │   └── tests/         # Test suite
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                   # Next.js frontend (placeholder)
├── packages/
│   └── shared/                # Shared utilities
├── infra/
│   └── docker-compose.yml     # Docker orchestration
├── docs/
│   ├── ARCHITECTURE.md        # System architecture
│   ├── ROADMAP.md             # Product roadmap
│   ├── AGENTS.md              # Agent specifications
│   ├── SAAS_PLAN.md           # SaaS pricing & plans
│   └── API_SPEC.md            # API documentation
├── scripts/
│   ├── bootstrap.sh           # Setup script
│   └── seed.py                # Database seeding
├── .github/
│   └── workflows/
│       └── api-ci.yml         # CI pipeline
├── .env.example               # Environment template
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### Development Setup

```bash
# Clone repository
git clone https://github.com/AISEO-VirtualabDigital/Eli-Swarm-Claw.git
cd Eli-Swarm-Claw

# Copy environment file
cp .env.example .env

# Start services with Docker
docker-compose up -d

# Install Python dependencies
cd apps/api
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed.py

# Start API server
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000 (when implemented)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/domains` | Add domain |
| POST | `/api/v1/crawl/start` | Start crawl |
| GET | `/api/v1/crawl/{job_id}` | Get crawl status |
| POST | `/api/v1/audit` | Run SEO audit |
| POST | `/api/v1/keywords/research` | Keyword research |
| GET | `/api/v1/entities` | Get entity graph |
| POST | `/api/v1/indexing/submit` | Submit URL for indexing |
| GET | `/api/v1/citations/check` | Check AI citations |
| POST | `/api/v1/briefs/generate` | Generate content brief |
| GET | `/api/v1/recommendations` | Get recommendations |
| GET | `/api/v1/reports` | Generate reports |

## Database Schema

Core entities:
- `users` - User accounts
- `organizations` - Multi-tenant orgs
- `workspaces` - Workspace containers
- `projects` - Client projects
- `domains` - Tracked domains
- `pages` - Crawled pages
- `crawls` - Crawl jobs
- `crawl_results` - Crawl data
- `keywords` - Keyword data
- `keyword_clusters` - Topic clusters
- `entities` - Entity records
- `competitors` - Competitor tracking
- `assets` - Content asset registry
- `indexing_jobs` - Indexing queue
- `ai_citation_checks` - Citation monitoring
- `recommendations` - Action items
- `reports` - Generated reports

## AI Agent System

Eli Claw uses CrewAI to orchestrate specialized agents:

1. **Crawler Agent** - Runs website crawls, extracts technical signals
2. **SEO Auditor Agent** - Analyzes crawl results, prioritizes issues
3. **Keyword Agent** - Expands and clusters keywords
4. **Entity Agent** - Maps entities and semantic relationships
5. **Competitor Agent** - Analyzes competitor gaps
6. **Indexing Agent** - Manages discovery submissions
7. **Content Brief Agent** - Generates SEO briefs
8. **AI Citation Agent** - Monitors AI mentions
9. **QA Agent** - Validates data quality
10. **Report Agent** - Creates client reports

See `docs/AGENTS.md` for detailed agent specifications.

## SaaS Plans

| Plan | Price | Projects | Domains | Crawl Credits | AI Checks |
|------|-------|----------|---------|---------------|-----------|
| Free | $0 | 1 | 1 | 100/month | 10/month |
| Starter | $29/mo | 3 | 5 | 1,000/month | 100/month |
| Pro | $79/mo | 10 | 20 | 5,000/month | 500/month |
| Agency | $199/mo | 50 | 100 | 25,000/month | 2,500/month |
| Enterprise | Custom | Unlimited | Unlimited | Custom | Custom |

## Security & Compliance

- ✅ Respects robots.txt
- ✅ Rate-limited crawling
- ✅ No private IP crawling
- ✅ URL validation
- ✅ SSRF protection
- ✅ No credential harvesting
- ✅ GDPR-ready data handling
- ✅ Secure API authentication

## Important Notice

Eli Claw is a **compliant SEO intelligence and discovery acceleration platform**. We do NOT:
- Guarantee search engine indexing
- Manipulate search rankings
- Engage in spam automation
- Scrape protected content
- Harvest credentials or personal data

Our indexing module focuses on **legitimate discovery methods**: sitemaps, IndexNow, RSS feeds, and technical optimization to improve crawlability.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Roadmap](docs/ROADMAP.md) - Product development timeline
- [Agents](docs/AGENTS.md) - AI agent specifications
- [SaaS Plan](docs/SAAS_PLAN.md) - Pricing and features
- [API Spec](docs/API_SPEC.md) - Detailed API documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

- Website: https://virtualabdigital.com
- Eli Claw: https://eliclaw.virtualabdigital.com
- Email: support@virtualabdigital.com

---

Built with ❤️ by **Virtualab Digital**
