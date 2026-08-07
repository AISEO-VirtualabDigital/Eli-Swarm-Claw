---
id: d007fac369bece2c
source: "serverless-saas-README.md"
"title: Serverless Multi-Tenant SaaS Backend"
category: saas
skillTags: ["pattern", "code"]
containmentHash: f87d8974bc9858e5c1b4
createdAt: 1786051359174
embeddingSig: "boundaries:cloudwatch:logs|cloudwatch:logs:exclude|data:dynamodb:single|ensure:events:stay|events:stay:within|exclude:sensitive:data|logs:exclude:sensitive|sensitive:data:dynamodb|stay:within:tenant|tenant:boundaries:cloudwatch|ules:ensure:events|within:tenant:boundaries"
---
ules ensure events stay within tenant boundaries
- CloudWatch logs exclude sensitive data
## DynamoDB Single Table Design
### Table Structure
```
Table: SaaSAppTable
Partition Key: PK (String)
Sort Key: SK (String)
```
### Access Patterns

| Entity | PK | SK | Attributes |
|--------|----|----|------------|
| Task | `TENANT#karachi-tech` | `TASK#task-123` | title, status, created_at, assigned_to |