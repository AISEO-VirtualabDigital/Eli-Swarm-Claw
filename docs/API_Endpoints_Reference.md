# API Endpoints Reference

> Complete REST API documentation for Eli Claw SaaS Platform

**Base URL:** `http://localhost:8000/api/v1`

**Tags:** #api #fastapi #rest #endpoints

---

## Authentication

> ⚠️ **Note:** Authentication endpoints are planned but not yet implemented. All current endpoints are open for development testing.

**Planned Endpoints:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user profile

---

## Health Check

### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Projects

### `POST /projects`
Create a new project.

**Request:**
```json
{
  "name": "Acme Corp SEO",
  "workspace_id": 1,
  "description": "Complete SEO overhaul",
  "industry": "SaaS",
  "location": "San Francisco, CA",
  "target_audience": "B2B Tech Decision Makers"
}
```

**Response:**
```json
{
  "id": 42,
  "name": "Acme Corp SEO",
  "workspace_id": 1,
  "status": "active",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### `GET /projects`
List all projects (with optional filters).

**Query Parameters:**
- `workspace_id` (int, optional)
- `status` (str, optional): active | archived
- `skip` (int, default: 0)
- `limit` (int, default: 100)

**Response:**
```json
{
  "total": 15,
  "items": [
    {
      "id": 42,
      "name": "Acme Corp SEO",
      "workspace_id": 1,
      "status": "active"
    }
  ]
}
```

---

### `GET /projects/{project_id}`
Get project details.

**Response:**
```json
{
  "id": 42,
  "name": "Acme Corp SEO",
  "description": "Complete SEO overhaul",
  "industry": "SaaS",
  "location": "San Francisco, CA",
  "domains": [...],
  "assets": [...],
  "campaigns": [...]
}
```

---

### `PUT /projects/{project_id}`
Update project.

**Request:**
```json
{
  "name": "Acme Corp SEO - Phase 2",
  "status": "active"
}
```

---

### `DELETE /projects/{project_id}`
Archive/delete project.

**Response:**
```json
{
  "message": "Project archived successfully"
}
```

---

## Domains

### `POST /domains`
Add domain to project.

**Request:**
```json
{
  "domain_name": "example.com",
  "protocol": "https",
  "project_id": 42,
  "crawl_enabled": true
}
```

**Response:**
```json
{
  "id": 101,
  "domain_name": "example.com",
  "protocol": "https",
  "project_id": 42,
  "health_score": null,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### `GET /domains`
List domains.

**Query Parameters:**
- `project_id` (int, required)
- `crawl_enabled` (bool, optional)

---

### `GET /domains/{domain_id}`
Get domain details with crawl history.

---

### `POST /domains/{domain_id}/crawl`
Trigger crawl for domain.

**Request:**
```json
{
  "max_depth": 3,
  "max_pages": 500,
  "respect_robots_txt": true
}
```

**Response:**
```json
{
  "crawl_job_id": 789,
  "status": "pending",
  "estimated_time_minutes": 15
}
```

---

## Crawl

### `POST /crawl/start`
Start a new crawl job.

**Request:**
```json
{
  "domain_id": 101,
  "max_depth": 3,
  "max_pages": 500,
  "respect_robots_txt": true,
  "exclude_patterns": ["/admin/*", "/wp-admin/*"]
}
```

**Response:**
```json
{
  "job_id": 789,
  "status": "pending",
  "domain_id": 101,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### `GET /crawl/jobs`
List crawl jobs.

**Query Parameters:**
- `domain_id` (int, optional)
- `status` (str, optional): pending | running | completed | failed
- `skip`, `limit`

---

### `GET /crawl/jobs/{job_id}`
Get crawl job status and results.

**Response:**
```json
{
  "id": 789,
  "domain_id": 101,
  "status": "completed",
  "pages_crawled": 342,
  "errors_count": 5,
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:45:00Z",
  "results": {
    "broken_links": [...],
    "duplicate_titles": [...],
    "missing_meta": [...],
    "schema_findings": [...]
  }
}
```

---

### `GET /crawl/results/{job_id}`
Get detailed crawl results.

**Query Parameters:**
- `status_code` (int, optional)
- `has_issue` (bool, optional)
- `skip`, `limit`

---

## Audit

### `POST /audit/analyze`
Run technical SEO audit on crawled data.

**Request:**
```json
{
  "domain_id": 101,
  "crawl_job_id": 789,
  "audit_types": ["technical", "content", "schema", "performance"]
}
```

**Response:**
```json
{
  "audit_id": 456,
  "domain_id": 101,
  "overall_score": 72,
  "issues_found": 47,
  "critical": 5,
  "high": 12,
  "medium": 20,
  "low": 10,
  "recommendations": [...]
}
```

---

### `GET /audit/{audit_id}`
Get audit results.

**Response:**
```json
{
  "id": 456,
  "overall_score": 72,
  "categories": {
    "technical": {
      "score": 68,
      "issues": [...]
    },
    "content": {
      "score": 75,
      "issues": [...]
    },
    "schema": {
      "score": 80,
      "issues": [...]
    }
  },
  "top_recommendations": [
    {
      "priority": "critical",
      "issue": "5 pages with noindex tag",
      "recommendation": "Review and remove noindex if pages should be indexed",
      "affected_urls": [...]
    }
  ]
}
```

---

## Keywords

### `POST /keywords/research`
Generate keyword research.

**Request:**
```json
{
  "seed_keywords": ["ai seo", "technical seo"],
  "industry": "SaaS",
  "location": "United States",
  "services": ["SEO audit", "content strategy"],
  "competitor_urls": ["https://competitor.com"],
  "generate_clusters": true,
  "generate_ai_prompts": true
}
```

**Response:**
```json
{
  "research_id": 234,
  "total_keywords": 156,
  "clusters_created": 12,
  "keywords": [
    {
      "keyword": "ai seo tools",
      "parent_topic": "AI SEO",
      "cluster": "Tools & Software",
      "intent": "commercial",
      "commercial_score": 85,
      "opportunity_score": 72,
      "suggested_title": "Best AI SEO Tools in 2025",
      "ai_prompt_variations": [...]
    }
  ],
  "clusters": [...]
}
```

---

### `GET /keywords`
List keywords.

**Query Parameters:**
- `project_id` (int, optional)
- `cluster_id` (int, optional)
- `intent` (str, optional)
- `min_commercial_score` (int, optional)
- `skip`, `limit`

---

### `POST /keywords/cluster`
Cluster existing keywords.

**Request:**
```json
{
  "keyword_ids": [1, 2, 3, 4, 5],
  "clustering_method": "semantic_similarity"
}
```

---

## Entities

### `POST /entities/extract`
Extract entities from URL or text.

**Request:**
```json
{
  "url": "https://example.com/about",
  "text": "Optional raw text",
  "project_id": 42
}
```

**Response:**
```json
{
  "extraction_id": 567,
  "entities_found": 23,
  "entities": [
    {
      "name": "VirtuaLab Digital",
      "entity_type": "Organization",
      "confidence_score": 0.95,
      "schema_org_type": "ProfessionalService"
    },
    {
      "name": "San Francisco",
      "entity_type": "Location",
      "confidence_score": 0.92,
      "schema_org_type": "City"
    }
  ],
  "entity_coverage_score": 68,
  "missing_entities": [...]
}
```

---

### `GET /entities/graph`
Get entity graph for project.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "topical_authority_score": 72
}
```

---

## Indexing

### `POST /indexing/submit`
Submit URL for discovery workflow.

**Request:**
```json
{
  "url": "https://example.com/blog/new-post",
  "project_id": 42,
  "asset_id": 123,
  "submission_method": "indexnow"
}
```

**Response:**
```json
{
  "job_id": 890,
  "url": "https://example.com/blog/new-post",
  "status": "submitted",
  "message": "URL queued for discovery workflow"
}
```

---

### `POST /indexing/batch-submit`
Submit multiple URLs (up to 1000).

**Request:**
```json
{
  "project_id": 42,
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2"
  ]
}
```

**Response:**
```json
{
  "submitted": 2,
  "failed": 0,
  "jobs": [890, 891]
}
```

---

### `GET /indexing/jobs`
List indexing jobs.

**Query Parameters:**
- `project_id` (int, optional)
- `status` (str, optional)
- `asset_id` (int, optional)
- `skip`, `limit`

---

### `GET /indexing/jobs/{job_id}`
Get job details.

**Response:**
```json
{
  "id": 890,
  "url": "https://example.com/blog/new-post",
  "status": "indexed",
  "submission_method": "indexnow",
  "submitted_at": "2025-01-15T10:30:00Z",
  "last_checked_at": "2025-01-15T12:00:00Z",
  "retry_count": 0,
  "content_hash": "sha256:abc123..."
}
```

---

### `POST /indexing/sitemap/generate`
Generate XML sitemap.

**Request:**
```json
{
  "project_id": 42,
  "domain_id": 101,
  "include_changefreq": true,
  "include_priority": true,
  "max_urls": 50000
}
```

**Response:**
```json
{
  "sitemap_url": "https://example.com/sitemap.xml",
  "urls_included": 342,
  "generated_at": "2025-01-15T10:30:00Z"
}
```

---

### `POST /indexing/check-indexability`
Check if URL is indexable.

**Request:**
```json
{
  "url": "https://example.com/page"
}
```

**Response:**
```json
{
  "is_indexable": false,
  "indexability_score": 40,
  "status": "blocked",
  "issues": [
    {
      "type": "noindex_meta",
      "severity": "critical",
      "message": "Page has noindex meta tag"
    }
  ],
  "recommendations": [
    {
      "action": "remove_noindex",
      "message": "Remove noindex directive if page should be indexed"
    }
  ]
}
```

---

### `GET /indexing/report/{project_id}`
Get comprehensive indexing report.

**Response:**
```json
{
  "health_score": 76,
  "summary": {
    "total_submissions": 245,
    "indexed": 178,
    "not_indexed": 45,
    "error": 22,
    "success_rate": 72.65
  },
  "recommendations": [...],
  "next_actions": [...]
}
```

---

### `POST /indexing/retry-recommendation/{job_id}`
Get smart retry recommendation.

**Response:**
```json
{
  "should_retry": true,
  "reason": "Content changed since last submission",
  "recommended_wait_hours": 24,
  "content_changed": true,
  "time_since_last_submission_hours": 48,
  "retry_count": 1,
  "max_retries": 3
}
```

---

## Citations

### `POST /citations/check`
Check AI citation for brand/domain.

**Request:**
```json
{
  "prompt_question": "What are the best AI SEO tools?",
  "target_brand": "Eli Claw",
  "target_domain": "eliclaw.com",
  "competitor_brands": ["CompetitorA", "CompetitorB"],
  "ai_system": "perplexity",
  "project_id": 42
}
```

**Response:**
```json
{
  "check_id": 678,
  "brand_mentioned": true,
  "competitor_mentioned": true,
  "url_cited": false,
  "citation_position": null,
  "ai_citation_score": 45,
  "answer_text": "...",
  "sources_cited": [...]
}
```

---

### `GET /citations/history`
Get citation check history.

**Query Parameters:**
- `project_id` (int, required)
- `ai_system` (str, optional)
- `date_from`, `date_to`

---

## Recommendations

### `GET /recommendations`
List recommendations.

**Query Parameters:**
- `project_id` (int, required)
- `category` (str, optional)
- `priority` (str, optional)
- `status` (str, optional)
- `skip`, `limit`

**Response:**
```json
{
  "total": 47,
  "items": [
    {
      "id": 1001,
      "project_id": 42,
      "url": "https://example.com/page",
      "category": "technical",
      "issue": "Missing H1 tag",
      "recommendation": "Add descriptive H1 tag",
      "impact": "high",
      "effort": "low",
      "priority_score": 85,
      "status": "backlog"
    }
  ]
}
```

---

### `POST /recommendations`
Create recommendation.

**Request:**
```json
{
  "project_id": 42,
  "url": "https://example.com/page",
  "category": "technical",
  "issue": "Missing H1 tag",
  "recommendation": "Add descriptive H1 tag",
  "impact": "high",
  "effort": "low"
}
```

---

### `PUT /recommendations/{rec_id}`
Update recommendation status.

**Request:**
```json
{
  "status": "in_progress"
}
```

---

## Reports

### `GET /reports/dashboard/{project_id}`
Get dashboard data for project.

**Response:**
```json
{
  "project_id": 42,
  "crawl_health_score": 78,
  "indexing_health_score": 76,
  "total_pages_crawled": 342,
  "indexed_assets": 178,
  "pages_with_issues": 47,
  "critical_errors": 5,
  "keyword_opportunities": 23,
  "ai_citation_score": 45,
  "top_recommendations": [...],
  "recent_crawls": [...],
  "recent_submissions": [...]
}
```

---

### `POST /reports/export`
Export report.

**Request:**
```json
{
  "project_id": 42,
  "report_type": "full_audit",
  "format": "pdf",
  "include_recommendations": true,
  "include_keyword_data": true
}
```

**Response:**
```json
{
  "export_id": 999,
  "status": "processing",
  "download_url": null,
  "message": "Report generation started. Check status at /reports/export/{export_id}"
}
```

---

### `GET /reports/export/{export_id}`
Check export status.

**Response:**
```json
{
  "export_id": 999,
  "status": "completed",
  "download_url": "https://storage.example.com/reports/999.pdf",
  "expires_at": "2025-01-22T10:30:00Z"
}
```

---

## Project Management (Planned)

### `POST /campaigns`
Create SEO campaign.

### `POST /tasks`
Create task.

### `PUT /tasks/{task_id}`
Update task status.

### `GET /campaigns/{campaign_id}/tasks`
List campaign tasks.

---

## Parasite SEO (Planned)

### `POST /parasite/opportunities`
Identify parasite SEO opportunities.

### `GET /parasite/opportunities`
List opportunities.

---

## Reddit Research (Planned)

### `POST /reddit/search`
Search Reddit for insights.

### `GET /reddit/findings`
List findings.

---

## YouTube SEO (Planned)

### `POST /youtube/optimize`
Optimize video metadata.

### `GET /youtube/videos`
List tracked videos.

---

## Social SEO (Planned)

### `POST /social/optimize`
Optimize social post.

### `GET /social/posts`
List tracked posts.

---

## Repository Scanner (Planned)

### `POST /repositories/scan`
Scan public repository.

### `GET /repositories/scans`
List scans.

---

## Error Responses

All endpoints may return standard HTTP error codes:

**400 Bad Request:**
```json
{
  "detail": "Invalid request body",
  "errors": [
    {"field": "url", "message": "Invalid URL format"}
  ]
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "error_id": "ERR-12345"
}
```

---

## Rate Limiting

> ⚠️ **Note:** Rate limiting is planned for production deployment.

**Planned Limits:**
- Free plan: 100 requests/hour
- Starter: 500 requests/hour
- Pro: 2000 requests/hour
- Agency: 10000 requests/hour
- Enterprise: Custom

---

## Interactive Documentation

Access interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

*See also: [[Eli_Claw_Master_Index]], [[Database_Models_Reference]]*
