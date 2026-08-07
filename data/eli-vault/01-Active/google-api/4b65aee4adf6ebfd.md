---
id: 4b65aee4adf6ebfd
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: 77c93900465739a0d746
createdAt: 1786051356392
embeddingSig: "bash:docker:pull|docker:image:uses|docker:pull:gosom|google:maps:scraper|gosom:google:maps|image:uses:playwright|maps:scraper:build|playwright:bash:docker|published:docker:image|pull:gosom:google|scraper:build:from|uses:playwright:bash"
---
ed)

The published Docker image uses Playwright:

```bash
docker pull gosom/google-maps-scraper
```
### Build from Source

Requirements: Go 1.26.5+

```bash
git clone https://github.com/gosom/google-maps-scraper.git
cd google-maps-scraper
go mod download
go build
./google-maps-scraper -input example-queries.txt -results results.csv -exit-on-inactivity 3m