---
id: 703a53c9ccdff3c9
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: 8f8f5dbceab9e9f5e814
createdAt: 1786051356392
embeddingSig: "business:websites:email|depth:exit:inactivity|emails:from:business|exit:inactivity:useful|extract:emails:from|flag:extract:emails|from:business:websites|inactivity:useful:options|need:flag:extract|options:need:flag|sults:depth:exit|useful:options:need"
---
sults.csv \
  -depth 1 \
  -exit-on-inactivity 3m
```
Useful options:

| Need | Flag |
|---|---|
| Extract emails from business websites | `-email` |
| Write JSON instead of CSV | `-json -results /out/results.json` |
| Collect extra reviews | `-extra-reviews -json -results /out/results.json` |
| Increase concurrency | `-c 4`, `-c 8`, or `-c 16` |
| Run multiple pages per browser | `-pages-per-browser 4` |