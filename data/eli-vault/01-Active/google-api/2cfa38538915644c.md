---
id: 2cfa38538915644c
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: c1bc3dafbbc14c4178e0
createdAt: 1786051356392
embeddingSig: "business:website:find|default:when:enabled|disabled:default:when|each:business:website|email:extraction:disabled|enabled:scraper:visits|extraction:disabled:default|find:email:addresses|scraper:visits:each|visits:each:business|website:find:email|when:enabled:scraper"
---
ion

Email extraction is **disabled by default**. When enabled, the scraper visits each business website to find email addresses.
```bash
./google-maps-scraper -input queries.txt -results results.csv -email
```

> **Note:** Email extraction increases processing time significantly.
### Fast Mode