---
id: 56d99dfd1c24909e
source: "agent-eli-v1-integration-registry.json"
"title: Agent Eli V1 Integration Registry"
category: ai-agent
skillTags: ["tool"]
containmentHash: 02b3fdbad173ad36db3b
createdAt: 1786051352671
embeddingSig: "approval:required:external|commands:approval:required|effect:production:write|external:side:effect|local:commands:approval|ooks:tools:python|production:write:status|python:scripts:local|required:external:side|scripts:local:commands|side:effect:production|tools:python:scripts"
---
ooks",
      "mcp_tools",
      "python_scripts",
      "local_commands"
    ],
    "approval_required": [
      "external_side_effect",
      "production_write"
    ],
    "status": "open"
  },
  {
    "id": "google-drive",
    "name": "Google Drive",
    "category": "knowledge",
    "provider": "google",
    "auth": [
      "oauth",
      "service_account"
    ],
    "capabilities": [
      "search",
      "read",