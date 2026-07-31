# Eli Claw Indexing Tool - Complete Guide

## Overview

The **Eli Claw Indexing Tool** is a compliant URL discovery and indexing workflow system. It does **NOT** guarantee indexing but improves the probability of discovery, crawling, and indexing through legitimate methods.

## Key Principles

1. **No False Promises**: We never claim guaranteed indexing
2. **Compliant Methods Only**: IndexNow, sitemaps, RSS feeds
3. **Smart Retry Logic**: Only resubmit when content changes
4. **Technical Barriers First**: Check indexability before submission
5. **Change Detection**: Track content hashes to avoid redundant submissions

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Routes    │────▶│  IndexingService │────▶│ External APIs   │
│  /indexing/*    │     │  (Business Logic)│     │ (IndexNow, etc) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Pydantic       │     │  Database Models │
│  Schemas        │     │  (IndexingJob)   │
└─────────────────┘     └──────────────────┘
```

## Available Endpoints

### 1. Submit Single URL

```bash
POST /api/v1/indexing/submit
```

**Request:**
```json
{
  "url": "https://example.com/new-blog-post",
  "project_id": 1,
  "asset_id": 42,
  "method": "manual",
  "content_hash": "abc123...",
  "notes": "Important product launch page"
}
```

**Response:**
```json
{
  "message": "URL queued for discovery workflow",
  "status": "submitted",
  "url": "https://example.com/new-blog-post",
  "job_id": 157
}
```

### 2. Batch Submit URLs

```bash
POST /api/v1/indexing/batch-submit
```

**Request:**
```json
{
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
  ],
  "project_id": 1
}
```

**Response:**
```json
{
  "message": "Batch submission queued (3 URLs)",
  "status": "submitted",
  "url": "3 URLs",
  "details": {
    "jobs": [
      {"job_id": 158, "url": "https://example.com/page1"},
      {"job_id": 159, "url": "https://example.com/page2"},
      {"job_id": 160, "url": "https://example.com/page3"}
    ],
    "submitted_count": 3
  }
}
```

### 3. List Indexing Jobs

```bash
GET /api/v1/indexing/jobs?project_id=1&status=pending&skip=0&limit=50
```

**Query Parameters:**
- `project_id` (optional): Filter by project
- `status` (optional): Filter by status (pending, submitted, crawled, indexed, not_indexed, excluded, error)
- `asset_id` (optional): Filter by asset
- `skip` (default: 0): Pagination offset
- `limit` (default: 100, max: 1000): Results per page

### 4. Get Job Details

```bash
GET /api/v1/indexing/jobs/{job_id}
```

### 5. Generate XML Sitemap

```bash
POST /api/v1/indexing/sitemap/generate
```

**Request:**
```json
{
  "project_id": 1,
  "base_url": "https://example.com",
  "include_only_indexable": true,
  "include_changefreq": false,
  "include_priority": false
}
```

**Response:**
```json
{
  "project_id": 1,
  "urls_count": 47,
  "sitemap_size_bytes": 3842,
  "generated_at": "2025-01-15T10:30:00Z",
  "sitemap_xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset>...</urlset>",
  "download_filename": "sitemap_1.xml",
  "note": "Upload this file to your website root and reference in robots.txt"
}
```

### 6. Check Indexability

```bash
POST /api/v1/indexing/check-indexability
```

**Request:**
```json
{
  "url": "https://example.com/page",
  "crawl_data": {
    "status_code": 200,
    "meta_robots": "",
    "canonical_url": "https://example.com/page",
    "word_count": 850,
    "title": "Page Title",
    "is_duplicate_title": false
  }
}
```

**Response:**
```json
{
  "url": "https://example.com/page",
  "is_indexable": true,
  "indexability_score": 95,
  "status": "ready_for_submission",
  "message": "URL appears technically ready for indexing submission",
  "checked_at": "2025-01-15T10:35:00Z",
  "issues": [],
  "recommendations": []
}
```

### 7. Generate Indexing Report

```bash
GET /api/v1/indexing/report/{project_id}
```

**Response:**
```json
{
  "project": "Client Website",
  "generated_at": "2025-01-15T10:40:00Z",
  "summary": {
    "total_submissions": 120,
    "indexed": 85,
    "crawled_not_indexed": 15,
    "submitted_pending": 10,
    "errors": 5,
    "excluded": 5,
    "success_rate": 70.83
  },
  "status_breakdown": {
    "indexed": 85,
    "crawled": 15,
    "pending": 10,
    "error": 5,
    "excluded": 5
  },
  "health_score": 78,
  "recommendations": [
    {
      "priority": "high",
      "category": "technical",
      "issue": "5 URLs with errors",
      "action": "Investigate errors",
      "message": "Review error messages and fix technical barriers"
    }
  ],
  "next_actions": [
    {
      "priority": 1,
      "action": "fix_errors",
      "description": "Investigate 5 errors",
      "endpoint": "/indexing/jobs?status=error"
    }
  ]
}
```

### 8. Get Retry Recommendation

```bash
POST /api/v1/indexing/retry-recommendation/{job_id}
```

**Request:**
```json
{
  "new_content_hash": "def456..."
}
```

**Response:**
```json
{
  "should_retry": true,
  "reason": "Not indexed previously, but content updated",
  "suggested_action": "Retry with improved content and internal linking",
  "current_retry_count": 1,
  "max_retries": 3,
  "job_status": "not_indexed",
  "content_changed": true
}
```

## Indexing Statuses

| Status | Description | Action Required |
|--------|-------------|-----------------|
| `pending` | Job created, waiting to be processed | Wait for agent processing |
| `submitted` | Submitted to IndexNow/sitemap | Monitor for crawl |
| `crawled` | Search engine crawled the page | Wait for indexing decision |
| `indexed` | Page is indexed | Monitor rankings/citations |
| `not_indexed` | Crawled but not indexed | Improve content/signals |
| `excluded` | Excluded by search engine | Review exclusion reason |
| `duplicate` | Detected as duplicate | Fix canonical/content |
| `canonicalized` | Points to canonical URL | Verify canonical is correct |
| `noindex` | Has noindex directive | Remove if intentional |
| `error` | Submission/technical error | Investigate and fix |

## Indexability Checks

The system checks for these barriers before submission:

### Critical Issues (Block Indexing)
- HTTP 4xx/5xx status codes
- `noindex` meta tag
- `X-Robots-Tag: noindex` header
- Blocked by robots.txt

### High Priority Issues
- Missing title tag
- Very thin content (<100 words)
- Canonical mismatch

### Medium Priority Issues
- Duplicate title tags
- Weak heading structure
- Missing meta description

## Smart Retry Logic

The system only recommends retry when:

1. **Content Changed**: SHA-256 hash differs from last submission
2. **Time Passed**: Minimum intervals respected:
   - Error: 24 hours
   - Not Indexed: 72 hours
   - Excluded: 48 hours
   - Indexed: 168 hours (1 week)
3. **Max Retries Not Reached**: Maximum 3 retries per URL
4. **Status Warrants Retry**: Some statuses don't need retry

## Sitemap Generation Features

### Standard Sitemap
- Follows sitemaps.org protocol
- UTF-8 encoded XML
- Automatic lastmod from asset update dates

### Optional Enhancements
- **changefreq**: Infer from content type (daily for news, weekly for blogs)
- **priority**: Assign based on page importance (1.0 for homepage, 0.6 for blog posts)

### Sitemap Index
For large sites (>50,000 URLs), generate sitemap index files that reference multiple sitemaps.

## Integration with IndexNow

### Setup Requirements

1. **Generate API Key** from Bing Webmaster Tools
2. **Upload key.txt** to website root: `https://domain.com/{key}.txt`
3. **Configure Environment Variable**:
   ```bash
   INDEXNOW_API_KEY=your_api_key_here
   ```

### How It Works

```python
# Service submits to IndexNow
result = await indexing_service.submit_to_indexnow(
    url="https://example.com/page",
    api_key="abc123",
    host="example.com"
)
```

### Error Handling

| HTTP Code | Meaning | Suggestion |
|-----------|---------|------------|
| 400 | Invalid request | Check URL and API key format |
| 401 | Invalid API key | Generate new key from Bing |
| 403 | Key not verified | Upload key.txt to website root |
| 404 | Host not found | Verify domain in Bing Webmaster Tools |
| 429 | Rate limited | Wait before submitting more |
| 500 | Service error | Retry later |

## Health Score Calculation

Overall indexing health score (0-100) calculated as weighted average:

| Status | Weight |
|--------|--------|
| indexed | 100 |
| crawled | 70 |
| submitted | 50 |
| pending | 40 |
| duplicate | 30 |
| canonicalized | 40 |
| not_indexed | 20 |
| excluded | 10 |
| error | 0 |
| noindex | 0 |

## Best Practices

### Before Submission
1. ✅ Run indexability check
2. ✅ Fix critical technical issues
3. ✅ Ensure content is complete
4. ✅ Verify canonical tags
5. ✅ Check robots.txt allows crawling

### After Submission
1. 🕐 Wait at least 24-48 hours
2. 📊 Monitor crawl status
3. 🔍 Check for indexing signals
4. 📈 Track rankings if indexed
5. 🔄 Only resubmit if content changed

### Avoid
- ❌ Submitting the same URL repeatedly
- ❌ Submitting pages with noindex
- ❌ Submitting error pages (404, 500)
- ❌ Submitting thin/duplicate content
- ❌ Ignoring exclusion reasons

## Example Workflow

```python
# 1. Check indexability first
check_result = await client.post(
    "/api/v1/indexing/check-indexability",
    json={"url": "https://example.com/new-page"}
)

if check_result["is_indexable"]:
    # 2. Submit if indexable
    submit_result = await client.post(
        "/api/v1/indexing/submit",
        json={
            "url": "https://example.com/new-page",
            "project_id": 1,
            "content_hash": calculate_hash(content)
        }
    )
    
    # 3. Monitor job
    job = await client.get(f"/api/v1/indexing/jobs/{submit_result['job_id']}")
    
    # 4. Generate report after some time
    report = await client.get("/api/v1/indexing/report/1")
    print(f"Health Score: {report['health_score']}")
else:
    # Fix issues first
    print("Issues found:", check_result["issues"])
    for rec in check_result["recommendations"]:
        print(f"Fix: {rec['message']}")
```

## Monitoring & Alerts

### Recommended Monitoring
- Daily: Check pending queue size
- Weekly: Review indexing success rate
- Monthly: Analyze health score trends

### Alert Thresholds
- ⚠️ Warning: Success rate < 50%
- 🚨 Critical: Success rate < 30%
- ⚠️ Warning: >20 URLs stuck in pending
- 🚨 Critical: >10 URLs with errors

## Future Enhancements (TODO)

- [ ] Google Search Console API integration
- [ ] Automated RSS feed updates
- [ ] Internal linking recommendations for indexability
- [ ] AI-powered content improvement suggestions
- [ ] Competitor indexing comparison
- [ ] Historical trend analysis
- [ ] Automated IndexNow key rotation
- [ ] Multi-search-engine submission tracking

## Compliance Notes

This tool:
- ✅ Respects robots.txt
- ✅ Uses official APIs (IndexNow)
- ✅ Follows rate limits
- ✅ Does not guarantee indexing
- ✅ Does not manipulate search engines
- ✅ Only submits user-owned/authorized URLs
- ✅ Tracks consent and authorization

This tool does NOT:
- ❌ Bypass platform rules
- ❌ Submit without authorization
- ❌ Guarantee ranking improvements
- ❌ Manipulate search algorithms
- ❌ Create fake signals
