# Eli Claw - Agent Architecture

## Overview

Eli Claw uses a multi-agent system powered by CrewAI, OpenClaw, Qwen, and Kimi to automate SEO operations while maintaining human oversight and compliance.

## Agent Categories

### 1. Core SEO Agents

#### Crawler Agent
**Role:** Website crawling and technical data extraction
**Goal:** Discover pages, extract SEO signals, identify issues
**Inputs:** Domain URL, crawl settings, project ID
**Outputs:** Crawl results, page data, broken links, technical issues
**Tools:** HTTP client, robots.txt parser, HTML parser
**API Endpoints:** `/api/v1/crawl/start`, `/api/v1/crawl/status`

#### SEO Auditor Agent
**Role:** Technical SEO analysis and issue prioritization
**Goal:** Review crawl results, prioritize fixes
**Inputs:** Crawl data, project settings
**Outputs:** Audit report, prioritized issues, recommendations
**Tools:** Rule engine, scoring algorithms
**API Endpoints:** `/api/v1/audit/analyze`, `/api/v1/recommendations`

#### Keyword Agent
**Role:** Keyword research and clustering
**Goal:** Expand keywords, identify opportunities
**Inputs:** Seed keywords, industry, location, competitors
**Outputs:** Keyword list, clusters, intent classification, opportunity scores
**Tools:** LLM expansion, rule-based modifiers, competitor extraction
**API Endpoints:** `/api/v1/keywords/research`, `/api/v1/keywords/cluster`

#### Entity Agent
**Role:** Entity extraction and semantic mapping
**Goal:** Map entities, find coverage gaps
**Inputs:** Page content, topic, industry
**Outputs:** Entity list, related entities, missing entities, coverage score
**Tools:** NLP extraction, knowledge graph
**API Endpoints:** `/api/v1/entities/extract`, `/api/v1/entities/map`

#### Competitor Agent
**Role:** Competitive intelligence
**Goal:** Analyze competitor strategies, find gaps
**Inputs:** Competitor URLs, project keywords
**Outputs:** Competitor analysis, content gaps, opportunity areas
**Tools:** Comparison algorithms, gap analysis
**API Endpoints:** `/api/v1/competitors/analyze`

### 2. Content & Publishing Agents

#### Content Brief Agent
**Role:** SEO content brief generation
**Goal:** Create comprehensive content briefs
**Inputs:** Keyword, topic, competitors, brand details
**Outputs:** Brief with structure, entities, FAQs, schema recommendations
**Tools:** Template engine, entity mapper, SERP analyzer
**API Endpoints:** `/api/v1/briefs/generate`

#### Parasite SEO Strategist Agent
**Role:** Third-party publishing opportunities
**Goal:** Find legitimate platforms for content distribution
**Inputs:** Industry, topics, target keywords
**Outputs:** Platform recommendations, content angles, risk assessment
**Tools:** Platform database, authority checker
**API Endpoints:** `/api/v1/parasite-seo/opportunities`

#### YouTube SEO Agent
**Role:** Video optimization
**Goal:** Optimize videos for YouTube and Google Video search
**Inputs:** Video URL/topic, target keywords
**Outputs:** Optimized titles, descriptions, tags, chapters, thumbnail ideas
**Tools:** YouTube API, keyword research
**API Endpoints:** `/api/v1/youtube/optimize`

#### Social SEO Agent
**Role:** Social media search optimization
**Goal:** Optimize social profiles and posts for discovery
**Inputs:** Platform, content, keywords
**Outputs:** Optimized captions, hashtags, profile bios, posting strategy
**Tools:** Platform-specific optimizers
**API Endpoints:** `/api/v1/social/optimize`

### 3. Research & Intelligence Agents

#### Reddit Research Agent
**Role:** Reddit market research
**Goal:** Find pain points, questions, content ideas
**Inputs:** Industry, location, services, keywords
**Outputs:** Relevant subreddits, top posts, pain points, content angles
**Tools:** Reddit API, sentiment analysis
**API Endpoints:** `/api/v1/reddit/research`

#### Reddit Lead Intelligence Agent
**Role:** Ethical lead identification
**Goal:** Find high-intent discussions without spamming
**Inputs:** Client domain, services, location
**Outputs:** Lead opportunities, suggested responses, compliance notes
**Tools:** Intent classifier, relevance scorer
**API Endpoints:** `/api/v1/reddit/leads`

#### Repository Scout Agent
**Role:** Open-source research
**Goal:** Find reusable architecture patterns and libraries
**Inputs:** Feature requirement, tech stack
**Outputs:** Repository list, license analysis, pattern summary
**Tools:** GitHub API, license checker
**API Endpoints:** `/api/v1/repositories/scan`

#### Repurposing Strategist Agent
**Role:** Convert research into implementation plans
**Goal:** Create original, compliant build plans
**Inputs:** Repository analysis, feature specs
**Outputs:** Implementation plan, tasks, attribution notes
**Tools:** Pattern matcher, task generator
**API Endpoints:** `/api/v1/repurposing/plans`

### 4. Operations & Management Agents

#### Indexing Agent
**Role:** Compliant URL submission and tracking
**Goal:** Improve discovery and indexing probability
**Inputs:** URLs, sitemap data, project settings
**Outputs:** Submission status, IndexNow results, recommendations
**Tools:** IndexNow API, sitemap generator
**API Endpoints:** `/api/v1/indexing/submit`, `/api/v1/indexing/status`

#### AI Citation Agent
**Role:** AI search visibility monitoring
**Goal:** Track brand mentions in AI-generated answers
**Inputs:** Brand/domain, competitor brands, prompts
**Outputs:** Citation report, mention tracking, competitor comparison
**Tools:** AI answer testing (mocked initially)
**API Endpoints:** `/api/v1/citations/check`

#### Project Manager Agent
**Role:** Task creation and sprint planning
**Goal:** Convert recommendations into actionable tasks
**Inputs:** Recommendations, team capacity, deadlines
**Outputs:** Tasks, sprints, priorities, assignments
**Tools:** Task planner, priority scorer
**API Endpoints:** `/api/v1/tasks/create-from-recommendations`

#### API Key Steward Agent
**Role:** API key health monitoring
**Goal:** Ensure API keys are working and rotated
**Inputs:** Configured API connectors
**Outputs:** Key status, expiration warnings, rotation reminders
**Tools:** Key validator (without storing keys)
**API Endpoints:** `/api/v1/api-keys/status`

#### Visual Builder Agent
**Role:** Page structure and wireframe generation
**Goal:** Turn SEO strategy into page designs
**Inputs:** Content brief, brand guidelines, SEO goals
**Outputs:** Wireframes, component specs, layout recommendations
**Tools:** Design system, template library
**API Endpoints:** `/api/v1/visual-builder/generate`

#### Web Development Agent
**Role:** Frontend/backend implementation guidance
**Goal:** Implement SEO-optimized pages
**Inputs:** Wireframes, content, technical requirements
**Outputs:** Component code, deployment instructions, optimization checks
**Tools:** Code generators, linters
**API Endpoints:** `/api/v1/dev/implement`

### 5. Quality & Reporting Agents

#### QA Agent
**Role:** Quality assurance and validation
**Goal:** Verify data quality and recommendation accuracy
**Inputs:** Generated outputs, validation rules
**Outputs:** QA report, issues found, approval status
**Tools:** Validation engine, test runner
**API Endpoints:** `/api/v1/qa/validate`

#### Report Agent
**Role:** Client and internal reporting
**Goal:** Create clear, actionable reports
**Inputs:** Project data, time period, audience
**Outputs:** PDF/PPT reports, dashboards, executive summaries
**Tools:** Report templates, chart generators
**API Endpoints:** `/api/v1/reports/generate`

#### SaaS Product Manager Agent
**Role:** Product alignment and UX oversight
**Goal:** Ensure features align with SaaS strategy
**Inputs:** Feature proposals, user feedback, metrics
**Outputs:** Product recommendations, prioritization, roadmap updates
**Tools:** Analytics, user research synthesis
**API Endpoints:** Internal use only

---

## Multi-Agent Workflows

### Workflow 1: Full SEO Audit
```
1. Crawler Agent → Crawl website
2. SEO Auditor Agent → Analyze results
3. QA Agent → Validate findings
4. Project Manager Agent → Create tasks
5. Report Agent → Generate client report
```

### Workflow 2: Content Production
```
1. Keyword Agent → Research keywords
2. Entity Agent → Map entities
3. Content Brief Agent → Generate brief
4. Visual Builder Agent → Create wireframe
5. Web Development Agent → Implement page
6. Indexing Agent → Submit for discovery
7. QA Agent → Review before publish
```

### Workflow 3: Market Research
```
1. Reddit Research Agent → Find discussions
2. Reddit Lead Intelligence → Identify opportunities
3. Competitor Agent → Analyze competition
4. Repository Scout → Find tools/patterns
5. Repurposing Strategist → Create implementation plan
6. Project Manager → Convert to tasks
```

### Workflow 4: Repository Repurposing
```
1. Input: Feature needed (e.g., "sitemap parser")
2. Repository Scout Agent → Search GitHub
3. Filter by license, stars, freshness
4. Repository Scout → Analyze architecture
5. Repurposing Strategist → Create original plan
6. QA Agent → Check compliance
7. Project Manager → Generate tasks
8. Developer Agent → Implement
9. Documentation Agent → Update docs
```

---

## Agent Configuration

### CrewAI Integration
```python
from crewai import Agent, Task, Crew

crawler_agent = Agent(
    role="Website Crawler",
    goal="Crawl websites respectfully and extract technical SEO data",
    backstory="Expert web crawler with focus on compliance and data quality",
    tools=[crawl_tool, robots_parser],
    verbose=True,
    allow_delegation=False
)
```

### Memory Requirements
- **Short-term:** Current task context, intermediate results
- **Long-term:** Project history, user preferences, learned patterns
- **Shared:** Cross-agent communication queue

### Rate Limiting per Agent
| Agent | Requests/Hour | Notes |
|-------|--------------|-------|
| Crawler | 1000 pages | Respect target site limits |
| Reddit Research | 100 API calls | Use official API |
| Repository Scout | 60 API calls | GitHub rate limit |
| Keyword Agent | 500 expansions | LLM calls |
| AI Citation | 100 checks | Mocked initially |

---

## Human Oversight

### Approval Required For
- Publishing content to external platforms
- API key rotations
- High-risk recommendations
- Large-scale automation (>100 actions)
- Legal/compliance decisions

### Escalation Triggers
- Uncertain license compatibility
- Potential terms of service violations
- Unusual error patterns
- High-impact recommendations
- Customer data access requests

---

## Agent Monitoring

### Metrics to Track
- Tasks completed per agent
- Success rate
- Average execution time
- Error frequency
- Human override rate
- Cost per operation (LLM tokens)

### Logging Requirements
```json
{
  "agent": "crawler_agent",
  "task_id": "12345",
  "action": "crawl_page",
  "url": "https://example.com/page",
  "status": "success",
  "duration_ms": 450,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Future Enhancements

### Planned Agents
- **Local SEO Agent:** GBP optimization, citation building
- **International SEO Agent:** Hreflang, localization
- **Ecommerce SEO Agent:** Product page optimization
- **News SEO Agent:** News sitemap, trending topics
- **App Store SEO Agent:** ASO optimization (placeholder)

### Advanced Capabilities
- Autonomous sprint planning
- Predictive issue detection
- Automated A/B testing
- Real-time ranking monitoring
- Cross-platform syndication

---

## Related Documentation

- [SAFETY_AND_COMPLIANCE.md](./SAFETY_AND_COMPLIANCE.md)
- [REPOSITORY_REPURPOSING.md](./REPOSITORY_REPURPOSING.md)
- [SAAS_PLAN.md](./SAAS_PLAN.md)
- [ROADMAP.md](./ROADMAP.md)
