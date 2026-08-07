---
id: 7f5e52374350e4ca
source: "serverless-saas-README.md"
"title: Serverless Multi-Tenant SaaS Backend"
category: saas
skillTags: ["metric"]
containmentHash: fc081a3491eaaca1cdf9
createdAt: 1786051359174
embeddingSig: "1000:events:cognito|1000:storage:cloudwatch|basic:monitoring:total|cloudwatch:basic:monitoring|cognito:1000:storage|eventbridge:1000:events|events:cognito:1000|monitoring:total:month|month:this:cheap|storage:cloudwatch:basic|this:cheap:idle|total:month:this"
---
$0.005 |
| EventBridge | 1000 events | $0.001 |
| Cognito | 1000 MAU | $0.55 |
| S3 | 1GB storage | $0.023 |
| CloudWatch | Basic monitoring | $0.50 |
| **Total** | | **~$2.50/month** |
**Why This Is Cheap**:
- No idle server costs (pay only for actual usage)
- AWS Free Tier covers most Lambda and DynamoDB usage
- Shared infrastructure across all tenants