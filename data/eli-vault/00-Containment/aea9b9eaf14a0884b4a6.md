---
id: bd2f5d00fff3f22e
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["tool", "code"]
containmentHash: aea9b9eaf14a0884b4a6
createdAt: 1786051356392
embeddingSig: "bash:export:leadsdb|environment:variable:bash|exit:inactivity:environment|export:leadsdb:your|google:maps:scraper|inactivity:environment:variable|leadsdb:your:google|maps:scraper:input|scraper:input:queries|variable:bash:export|your:exit:inactivity|your:google:maps"
---
api-key "your-api-key" \
  -exit-on-inactivity 3m
```
Or via environment variable:
```bash
export LEADSDB_API_KEY="your-api-key"
./google-maps-scraper -input queries.txt -exit-on-inactivity 3m
```
<details>
<summary><strong>Field Mapping</strong></summary>

| Google Maps | LeadsDB |
|-------------|---------|
| Title | Name |
| Category | Category |
| Categories | Tags |
| Phone | Phone |
| Website | Website |