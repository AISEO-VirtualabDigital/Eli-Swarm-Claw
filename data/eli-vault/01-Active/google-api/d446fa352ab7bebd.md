---
id: d446fa352ab7bebd
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["code"]
containmentHash: adb9b9ba92f1f5d8f913
createdAt: 1786051356392
embeddingSig: "bash:google:maps|cafes:peristeri:greece|command:example:bash|example:bash:google|google:maps:scraper|greece:command:example|input:queries:results|maps:scraper:input|peristeri:greece:command|queries:results:peristeri|results:peristeri:cafes|scraper:input:queries"
---
cafes in Peristeri, Greece
```

Command example:

```bash
./google-maps-scraper \
  -input queries.txt \
  -results peristeri-cafes.csv \
  -grid-bbox "38.0077,23.6719,38.0257,23.6947" \
  -grid-cell 0.5 \
  -zoom 16 \
  -depth 1 \
  -c 4
```
Notes:
- `-grid-bbox` guides where searches are launched from, but results are not strictly clipped to the box.