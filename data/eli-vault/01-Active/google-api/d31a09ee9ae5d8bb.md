---
id: d31a09ee9ae5d8bb
source: "google-workspace-api-tools.md"
"title: Google Workspace & Productivity API Tools"
category: google-api
skillTags: ["code"]
containmentHash: 54ee067e08eba6f7f8a5
createdAt: 1786051356911
embeddingSig: "also:install:homebrew|bash:auth:setup|bash:brew:install|brew:bash:brew|brew:install:googleworkspace|googleworkspace:quick:start|homebrew:https:brew|https:brew:bash|install:googleworkspace:quick|install:homebrew:https|quick:start:bash|start:bash:auth"
---
n also install via [Homebrew](https://brew.sh/):

```bash
brew install googleworkspace-cli
```
## Quick Start

```bash
gws auth setup     # walks you through Google Cloud project config
gws auth login     # subsequent OAuth login
gws drive files list --params '{"pageSize": 5}'
```
## Why gws?

**For humans** — stop writing `curl` calls against