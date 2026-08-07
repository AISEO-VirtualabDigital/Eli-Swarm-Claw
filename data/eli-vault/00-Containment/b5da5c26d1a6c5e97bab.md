---
id: fd3a60a1ea1d3e6f
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: b5da5c26d1a6c5e97bab
createdAt: 1786051356392
embeddingSig: "bash:mkdir:gmaps|command:line:bash|community:contributing:contributing|contributing:contributing:license|contributing:license:license|license:license:quick|license:quick:start|line:bash:mkdir|mkdir:gmaps:output|nity:community:contributing|quick:start:command|start:command:line"
---
nity](#community)
- [Contributing](#contributing)
- [License](#license)
---
## Quick Start
### Command Line

```bash
mkdir -p gmaps-output

docker run \
  -v gmaps-playwright-cache:/opt \
  -v "$PWD/example-queries.txt:/queries.txt:ro" \
  -v "$PWD/gmaps-output:/out" \
  gosom/google-maps-scraper \
  -input /queries.txt \
  -results /out/results.csv \
  -depth 1 \
  -exit-on-inactivity 3m