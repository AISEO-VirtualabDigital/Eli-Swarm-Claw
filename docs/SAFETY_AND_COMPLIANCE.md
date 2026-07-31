# Eli Claw - Safety and Compliance Guidelines

## Positioning Statement

**Eli Claw is an AI-powered SEO operations platform for agencies, consultants, and growth teams.**

We combine crawling, keyword intelligence, technical SEO, AI search visibility, project management, content strategy, parasite SEO planning, Reddit research, YouTube SEO, social SEO, indexing workflows, and autonomous agent-assisted execution.

## What Eli Claw IS

✅ A compliant SEO intelligence platform
✅ An asset discovery and crawl acceleration system
✅ A technical SEO auditing tool
✅ A keyword research and topic clustering engine
✅ An entity and semantic mapping system
✅ A content brief generator
✅ A project management system for SEO work
✅ An AI citation monitoring tool
✅ A repository research and repurposing assistant
✅ A multi-agent automation platform

## What Eli Claw IS NOT

❌ A spam automation tool
❌ A black-hat indexing service
❌ A scraper abuse platform
❌ A forced ranking tool
❌ A fake traffic generator
❌ A system that bypasses platform rules
❌ A credential harvesting tool
❌ A malware distribution system
❌ An API key stealing tool
❌ A vote manipulation platform
❌ A ban evasion system

---

## Core Ethical Principles

### 1. Respect Platform Rules
- Always read and follow robots.txt
- Respect rate limits on all APIs
- Never attempt to bypass CAPTCHAs
- Honor terms of service for all platforms
- Use official APIs when available

### 2. Data Privacy
- Never collect personal data without consent
- Never store sensitive credentials
- Mask API keys in logs and UI
- Comply with GDPR, CCPA, and other regulations
- Allow users to export/delete their data

### 3. Transparency
- Clearly document what data is collected
- Explain how recommendations are generated
- Disclose use of AI/automation
- Provide audit logs for all actions
- Show source attribution for research

### 4. License Compliance
- Respect open-source licenses
- Track attribution requirements
- Never copy proprietary code
- Verify license compatibility before repurposing
- Document all third-party inspirations

### 5. No Manipulation
- No fake link building
- No review manipulation
- No rating inflation
- No artificial engagement
- No deceptive practices

---

## Module-Specific Guidelines

### Crawler Module
**Allowed:**
- Crawling publicly accessible pages
- Respecting robots.txt directives
- Following sitemap files
- Storing technical SEO data
- Analyzing page structure

**Forbidden:**
- Ignoring robots.txt
- Bypassing access controls
- Scraping login-protected content
- Aggressive crawling that impacts server performance
- Collecting personal data

### Reddit Research Module
**Allowed:**
- Reading public posts and comments
- Analyzing trending topics
- Identifying pain points
- Finding content opportunities
- Using official Reddit API

**Forbidden:**
- Automated posting without disclosure
- Vote manipulation
- Sockpuppet accounts
- Spam comments
- Harvesting user emails
- Ban evasion

### Parasite SEO Module
**Allowed:**
- Identifying high-authority platforms
- Planning legitimate content contributions
- Educational content strategies
- Community-appropriate posts
- Following platform guidelines

**Forbidden:**
- Spam articles
- Hidden links
- Deceptive bylines
- Mass automated posting
- Terms of service violations

### Repository Scanner Module
**Allowed:**
- Public GitHub repository analysis
- Architecture pattern study
- License compatibility checking
- Original implementation from patterns
- Proper attribution

**Forbidden:**
- Copying proprietary code
- Ignoring license terms
- Credential scanning
- Vulnerability exploitation
- Plagiarism

### API Key Management
**Allowed:**
- Storing key metadata (not keys themselves)
- Health checking configured keys
- Expiration reminders
- Approved rotation workflows
- Fallback key switching (user-configured)

**Forbidden:**
- Storing raw API keys in database
- Printing full keys in logs
- Auto-generating unauthorized keys
- Scraping keys from sources
- Sharing keys between users

### Indexing Module
**Allowed:**
- IndexNow submission
- Sitemap generation
- RSS feed updates
- Internal linking recommendations
- Crawl status monitoring

**Forbidden:**
- Guaranteed indexing promises
- Search Console API abuse
- Automated mass submission
- Manipulation tactics
- Fake sitemaps

---

## Security Requirements

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost/eliclaw
SECRET_KEY=your-secret-key-here
API_V1_PREFIX=/api/v1

# Optional API keys (never commit these)
# GITHUB_TOKEN=
# REDDIT_CLIENT_ID=
# REDDIT_CLIENT_SECRET=
# GOOGLE_API_KEY=
```

### SSRF Protection
All URL validation must block:
- Private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
- Localhost (127.x.x.x)
- Link-local addresses (169.254.x.x)
- IPv6 localhost (::1)
- Internal hostnames

### Rate Limiting
Implement rate limits on:
- Crawl jobs per project
- API requests per user
- Repository scans per hour
- Keyword lookups per day
- AI citation checks per month

### Logging Best Practices
```python
# ✅ Good: Masked key
logger.info(f"Using API key {key_prefix}*** for provider {name}")

# ❌ Bad: Exposed key
logger.info(f"Using API key {full_key} for provider {name}")
```

---

## Legal Considerations

### Terms of Service Compliance
Before integrating any platform:
1. Read the full Terms of Service
2. Read the Developer Agreement (if applicable)
3. Check rate limit policies
4. Verify allowed use cases
5. Document compliance notes

### Copyright and Licenses
- MIT, Apache 2.0, BSD: Generally safe with attribution
- GPL: Requires careful consideration (copyleft)
- AGPL: Avoid for SaaS products
- Proprietary: Do not use without explicit permission

### Data Protection
- Implement user consent mechanisms
- Provide data export functionality
- Support data deletion requests
- Encrypt sensitive data at rest
- Use HTTPS for all communications

---

## Agent Behavior Guidelines

All CrewAI/OpenClaw agents must:

1. **Follow Instructions**: Execute only approved tasks
2. **Respect Limits**: Adhere to rate limits and quotas
3. **Log Actions**: Record all significant operations
4. **Validate Inputs**: Check URLs, parameters, permissions
5. **Error Gracefully**: Fail safely without side effects
6. **No Secrets**: Never output credentials or tokens
7. **Human Oversight**: Escalate uncertain decisions

### Agent Approval Workflow
```
Agent proposes action
    ↓
Check against safety rules
    ↓
If risky → require human approval
    ↓
If safe → execute with logging
    ↓
Report results
```

---

## Compliance Checklist

Before launching any feature:

- [ ] Terms of service reviewed for all integrations
- [ ] License compatibility verified
- [ ] Rate limits implemented
- [ ] Input validation in place
- [ ] SSRF protection enabled
- [ ] Credentials handled securely
- [ ] Logging configured (no secrets)
- [ ] User consent mechanisms ready
- [ ] Data retention policy defined
- [ ] Error handling tested
- [ ] Documentation complete

---

## Reporting Violations

If you discover:
- Security vulnerabilities
- Compliance issues
- Unethical feature requests
- Potential misuse

Report immediately to: security@virtualabdigital.com

---

## Continuous Improvement

This document should be:
- Reviewed quarterly
- Updated with new regulations
- Expanded with new modules
- Shared with all team members
- Included in onboarding

---

## Related Documentation

- [REPOSITORY_REPURPOSING.md](./REPOSITORY_REPURPOSING.md)
- [AGENTS.md](./AGENTS.md)
- [SAAS_PLAN.md](./SAAS_PLAN.md)
- [API_SPEC.md](./API_SPEC.md)
