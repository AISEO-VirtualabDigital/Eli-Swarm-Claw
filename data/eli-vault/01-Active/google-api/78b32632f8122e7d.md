---
id: 78b32632f8122e7d
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: []
containmentHash: ad94bcca1964fdf183fe
createdAt: 1786051356392
embeddingSig: "active:pages:lowering|bottleneck:reduce:total|browser:bottleneck:reduce|browser:product:browser|lowering:pages:browser|number:active:pages|pages:browser:bottleneck|pages:browser:product|pages:lowering:pages|reduce:pages:browser|reduce:total:number|total:number:active"
---
ize` low and reduce `-c` or `-pages-per-browser`.
- If CPU is the bottleneck, reduce the total number of active pages by lowering `-c` or `-pages-per-browser`.
- The product `-browser-pool-size × -pages-per-browser` should roughly equal or exceed `-c` to keep all jobs busy.
- Setting an explicit `-browser-pool-size` is most useful in containerized