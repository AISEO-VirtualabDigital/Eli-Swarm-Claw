---
id: fedfff3a0d94e97f
source: "serverless-saas-README.md"
"title: Serverless Multi-Tenant SaaS Backend"
category: saas
skillTags: ["process", "code"]
containmentHash: 9c3923efd4b3ada27c62
createdAt: 1786051359174
embeddingSig: "begins:with:task|karachi:tech:begins|python:response:table|response:table:item|specific:task:python|table:item:tenant|task:python:response|task:specific:task|tech:begins:with|tenant:karachi:tech|with:task:specific|xpression:tenant:karachi"
---
xpression=Key('PK').eq('TENANT#karachi-tech') & 
                          Key('SK').begins_with('TASK#')
)
```
**Get specific task:**
```python
response = table.get_item(
    Key={
        'PK': 'TENANT#karachi-tech',
        'SK': 'TASK#task-123'
    }
)
```
### Why Single Table?

1. **Performance**: Single-digit millisecond latency
2. **Cost**: One table vs hundreds of tables
3.