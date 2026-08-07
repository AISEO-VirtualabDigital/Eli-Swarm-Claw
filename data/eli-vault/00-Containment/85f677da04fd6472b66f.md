---
id: 4cead6aa34b5b2a5
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: 85f677da04fd6472b66f
createdAt: 1786051356392
embeddingSig: "args:depth:postgres|containers:name:google|depth:postgres:user|google:maps:scraper|gosom:google:maps|image:gosom:google|latest:args:depth|maps:scraper:image|maps:scraper:latest|name:google:maps|scraper:image:gosom|scraper:latest:args"
---
containers:
      - name: google-maps-scraper
        image: gosom/google-maps-scraper:latest
        args: ["-c", "1", "-depth", "10", "-dsn", "postgres://user:pass@host:5432/db"]
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
```
> **Note:** The headless browser requires significant CPU/memory