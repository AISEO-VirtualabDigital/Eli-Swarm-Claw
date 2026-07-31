# Eli Claw - Repository Scanner & Repurposing Engine

## Overview

The Repository Scanner module ethically scans public GitHub repositories to find reusable architecture patterns, open-source libraries, and implementation references for Eli Claw development.

## Core Principles

### ✅ Allowed Activities
- Use GitHub API or public repository access
- Respect rate limits
- Respect software licenses
- Track license types and attribution requirements
- Extract high-level architecture patterns
- Identify compatible open-source packages
- Generate original implementations inspired by patterns
- Find SEO crawlers, sitemap parsers, keyword clustering examples
- Study FastAPI SaaS boilerplates, Next.js dashboards
- Find CrewAI examples, Reddit API tools, YouTube SEO tools

### ❌ Forbidden Activities
- Copy proprietary code
- Copy code from incompatible licenses (GPL without compliance)
- Collect secrets or credentials
- Scan for exposed credentials
- Exploit vulnerabilities
- Republish code without attribution
- Clone malware, phishing kits, spam tools
- Bypass rate limits
- Ignore license terms

## Architecture

```
Repository Scout Agent
    ↓
Search GitHub by topic/keyword
    ↓
Filter by license, stars, freshness
    ↓
Analyze architecture & patterns
    ↓
Repurposing Strategist Agent
    ↓
Create original implementation plan
    ↓
Project Manager Agent
    ↓
Convert to tasks → Developer → QA → Docs
```

## Data Models

### RepositoryScan
- Repository identification (name, URL, owner)
- Metrics (stars, forks, watchers)
- License information and compatibility
- Architecture analysis
- Reusability assessment
- Compliance notes
- Repurpose recommendation

### RepurposingPlan
- Feature category and description
- Source attribution
- Implementation approach (adopt/adapt/inspired_by)
- Eli Claw module mapping
- Legal review tracking
- Status workflow

### PublicAPIConnector
- API provider details
- Authentication type
- Rate limiting info
- Endpoint tracking
- Compliance notes

### APIKeyStatus
- Key health monitoring (without storing keys)
- Expiration tracking
- Rotation reminders
- Fallback configuration

## API Endpoints

### Repository Scanning
- `POST /api/v1/repositories/scan` - Scan a repository
- `GET /api/v1/repositories` - List scanned repositories
- `GET /api/v1/repositories/{id}` - Get scan details
- `POST /api/v1/repositories/{id}/analyze` - Analyze for patterns
- `DELETE /api/v1/repositories/{id}` - Remove scan

### Repurposing Plans
- `POST /api/v1/repurposing/plans` - Create repurposing plan
- `GET /api/v1/repurposing/plans` - List plans
- `PUT /api/v1/repurposing/plans/{id}` - Update plan
- `POST /api/v1/repurposing/plans/{id}/approve` - Approve plan
- `POST /api/v1/repurposing/plans/{id}/tasks` - Generate tasks

### API Connectors
- `POST /api/v1/api-connectors` - Register connector
- `GET /api/v1/api-connectors` - List connectors
- `POST /api/v1/api-connectors/{id}/test` - Test connection
- `PUT /api/v1/api-connectors/{id}` - Update connector

### API Key Management
- `GET /api/v1/api-keys/status` - Get key statuses
- `POST /api/v1/api-keys/{id}/validate` - Validate key
- `POST /api/v1/api-keys/{id}/rotate` - Schedule rotation
- `GET /api/v1/api-keys/warnings` - Get expiration warnings

## License Compatibility Matrix

| License | Compatible | Attribution Required | Copyleft | Notes |
|---------|-----------|---------------------|----------|-------|
| MIT | ✅ Yes | ✅ Yes | ❌ No | Very permissive |
| Apache 2.0 | ✅ Yes | ✅ Yes | ❌ No | Patent grant included |
| BSD 3-Clause | ✅ Yes | ✅ Yes | ❌ No | Very permissive |
| ISC | ✅ Yes | ✅ Yes | ❌ No | Similar to MIT |
| GPL 2.0 | ⚠️ Conditional | ✅ Yes | ✅ Yes | Viral license |
| GPL 3.0 | ⚠️ Conditional | ✅ Yes | ✅ Yes | Strong copyleft |
| AGPL | ❌ No | ✅ Yes | ✅ Yes | Network use triggers |
| Proprietary | ❌ No | N/A | Varies | Check terms |

## Implementation Workflow

### 1. Repository Discovery
```python
# Search GitHub API
query = "seo crawler python"
filters = {
    "language": "Python",
    "stars": ">100",
    "license": "MIT,Apache-2.0,BSD-3-Clause",
    "pushed": ">2023-01-01"
}
```

### 2. License Analysis
```python
def check_compatibility(license_type: str) -> dict:
    return {
        "compatible": license_type in COMPATIBLE_LICENSES,
        "attribution_required": license_type in ATTRIBUTION_LICENSES,
        "copyleft": license_type in COPYLEFT_LICENSES,
        "risk_level": calculate_risk(license_type)
    }
```

### 3. Pattern Extraction
- Identify main modules
- Extract architecture diagrams
- Map dependencies
- Document key algorithms (without copying code)

### 4. Original Implementation
- Write new code from scratch
- Use patterns as inspiration only
- Add proper attribution in docs
- Ensure license compliance

## Agent Specifications

### Repository Scout Agent
**Role:** Find relevant public repositories
**Goal:** Identify safe, useful architecture patterns
**Inputs:** Feature requirement, technology stack
**Outputs:** Repository list with analysis
**Tools:** GitHub API, License checker

### Repurposing Strategist Agent
**Role:** Convert research into implementation plans
**Goal:** Create original, compliant implementation strategies
**Inputs:** Repository analysis, feature requirements
**Outputs:** Implementation plan with tasks
**Tools:** Pattern matcher, Task generator

## Security Considerations

1. **Never store API keys in code**
2. **Use environment variables for secrets**
3. **Mask key prefixes in logs**
4. **Implement rate limiting on scans**
5. **Validate all URLs before scanning**
6. **Block private IP ranges**
7. **Log all scanning activity**

## Compliance Checklist

- [ ] License verified and compatible
- [ ] Attribution text prepared if required
- [ ] No direct code copying
- [ ] Original implementation planned
- [ ] Legal review completed (if needed)
- [ ] Documentation updated with sources
- [ ] Rate limits respected
- [ ] Terms of service reviewed

## Example Use Cases

### Finding a Sitemap Parser
1. Search: "sitemap parser python"
2. Filter: MIT/Apache license, >50 stars
3. Analyze: Architecture, key functions
4. Plan: Build original parser with similar interface
5. Attribute: Note inspiration in docs

### Finding Crawl Patterns
1. Search: "web crawler respectful robots.txt"
2. Filter: Recent activity, good documentation
3. Analyze: Rate limiting, robots.txt handling
4. Plan: Implement similar patterns in Eli Claw
5. Document: Reference studied repositories

## Related Documentation
- [SAFETY_AND_COMPLIANCE.md](./SAFETY_AND_COMPLIANCE.md)
- [AGENTS.md](./AGENTS.md)
- [API_CONNECTORS.md](./API_CONNECTORS.md)
