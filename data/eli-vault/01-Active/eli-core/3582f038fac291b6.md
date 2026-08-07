---
id: 3582f038fac291b6
source: "youtube-marketing-skills-README.md"
"title: YouTube Marketing Skills"
category: eli-core
skillTags: ["strategy", "metric", "code"]
containmentHash: f2b6ab330a050cdbf3ad
createdAt: 1786051359720
embeddingSig: "back:install:hosted|channel:data:write|client:type:youtube|commands:live:channel|data:write:back|have:commands:live|live:channel:data|skills:client:type|strategy:have:commands|type:youtube:strategy|write:back:install|youtube:strategy:have"
---
MCP+Skills client) and type `/youtube-strategy`. You now have all 21 commands + live channel data + SEO write-back.
*A no-install hosted option is coming soon for users who don't want to set up Node + Google Cloud.*

Add to Claude Code `settings.json`:
```json
{
  "mcpServers": {
    "youtube": {
      "command": "npx",
      "args": ["youtube-channel-mcp"]
    }
  },