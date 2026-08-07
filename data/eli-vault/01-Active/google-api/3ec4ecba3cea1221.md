---
id: 3ec4ecba3cea1221
source: "google-maps-scraper-gosom-README.md"
"title: Google Maps Scraper"
category: google-api
skillTags: ["process", "tool", "code"]
containmentHash: f0dd429d42d51141506f
createdAt: 1786051356392
embeddingSig: "browser:requires:significant|create:custom:output|custom:output:handlers|custom:writer:plugins|headless:browser:requires|memory:resources:custom|output:handlers:using|plugins:create:custom|requires:significant:memory|resources:custom:writer|significant:memory:resources|writer:plugins:create"
---
headless browser requires significant CPU/memory resources.
### Custom Writer Plugins

Create custom output handlers using Go plugins:

**1. Write the plugin** (see `examples/plugins/example_writer.go`)
**2. Build:**
```bash
go build -buildmode=plugin -tags=plugin -o myplugin.so myplugin.go
```