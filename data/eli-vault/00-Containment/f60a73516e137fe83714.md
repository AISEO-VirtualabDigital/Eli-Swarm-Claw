---
id: 2abf961c85cbdded
source: "seo-agency-architecture-patterns.md"
"title: SEO Agency Architecture Patterns: Building AI-Powered Marketing SaaS"
category: seo
skillTags: ["pattern", "tool"]
containmentHash: f60a73516e137fe83714
createdAt: 1786051359012
embeddingSig: "account:pull:search|console:google:search|console:oauth2:service|google:search:console|integration:patterns:google|oauth2:service:account|patterns:google:search|pull:search:performance|search:console:google|search:console:oauth2|search:performance:data|service:account:pull"
---
## Integration Patterns
### Google Search Console
Use the Google Search Console API (OAuth2 service account) to pull search performance data, index coverage reports, and sitemap status. Data syncs daily. Store raw data in the analytics warehouse for trend analysis beyond GSC's 16-month retention.
### Google Analytics
GA4 Data API (v1) via OAuth2 service account. Pull user acquisition, engagement, and conversion data.