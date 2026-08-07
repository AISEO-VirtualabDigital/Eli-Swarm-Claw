---
id: 8ba519ab7d723d1b
source: "seo-agency-architecture-patterns.md"
"title: SEO Agency Architecture Patterns: Building AI-Powered Marketing SaaS"
category: seo
skillTags: ["pattern", "metric", "code"]
containmentHash: 55dbdc4f8e3811cbc3ec
createdAt: 1786051359012
embeddingSig: "client:defined:schedules|dashboards:output:formats|data:export:scheduling|defined:schedules:weekly|export:scheduling:reports|formats:weasyprint:html|generated:client:defined|html:data:export|output:formats:weasyprint|reports:generated:client|scheduling:reports:generated|weasyprint:html:data"
---
js for web dashboards) -> Output Formats (PDF via WeasyPrint, HTML for web, CSV for data export).
**Scheduling:** Reports are generated on client-defined schedules (weekly, monthly, quarterly). Each report generation is an async job that runs at the configured time and delivers via email and in-app notification.
---
## Integration Patterns
### Google Search Console