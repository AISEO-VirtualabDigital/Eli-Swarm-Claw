---
id: 1d295ddcc0bab2ed
source: "ai-marketing-tools-ecosystem.md"
"title: AI Marketing Tools Ecosystem: Curated Reference"
category: ai-agent
skillTags: ["capability", "tool", "code"]
containmentHash: 5942ab8f930f8bc9f7ac
createdAt: 1786051352674
embeddingSig: "agent:built:openai|allows:tool:agent|built:openai:grok|compatible:format:this|format:this:allows|grok:drop:replacement|openai:compatible:format|openai:grok:drop|responses:openai:compatible|returns:responses:openai|this:allows:tool|tool:agent:built"
---
nd returns responses in OpenAI-compatible format. This allows any tool or agent built for the OpenAI API to use Grok as a drop-in replacement.
**Tech Stack:** Go backend for the API proxy, React admin dashboard for configuration. Deployable via Docker with a single command. Supports streaming (SSE) and function calling.