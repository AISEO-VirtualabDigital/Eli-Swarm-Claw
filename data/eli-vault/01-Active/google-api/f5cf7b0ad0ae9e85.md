---
id: f5cf7b0ad0ae9e85
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: cc9580e39fb85dbd26b4
createdAt: 1786051356392
embeddingSig: "5432:postgres:kubernetes|apiversion:apps:kind|apps:kind:deployment|deployment:yaml:apiversion|gres:postgres:postgres|kind:deployment:metadata|kubernetes:deployment:yaml|localhost:5432:postgres|postgres:kubernetes:deployment|postgres:localhost:5432|postgres:postgres:localhost|yaml:apiversion:apps"
---
gres://postgres:postgres@localhost:5432/postgres"
```
### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: google-maps-scraper
spec:
  replicas: 3  # Adjust based on needs
  selector:
    matchLabels:
      app: google-maps-scraper
  template:
    metadata:
      labels:
        app: google-maps-scraper
    spec:
      containers:
      - name: google-maps-scraper