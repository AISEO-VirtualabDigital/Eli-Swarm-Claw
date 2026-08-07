---
id: abs-cfos-arch-93fff478
title: "Cloudflare OS — Open Source AI Productivity Environment"
source: https://github.com/cloudflare/cloudflare-os
category: cloudflare-os
skillTags: ["agent-platform", "sandboxed-apps", "security-framework", "gadgets"]
createdAt: 2026-08-07T15:24:11.126Z
absorbedFrom: github-research
---

Cloudflare OS is an "operating system" for AI productivity, originally developed inside Cloudflare. A large portion of Cloudflare's workforce uses it daily.

## Core Concepts

### Gadgets
A new paradigm where every user runs their own copy of productivity apps. When you create a slide deck, the system creates a PRIVATE INSTANCE of the software just for you, running in a separate sandbox.
- Impossible for app bugs to leak data between users
- Users can freely modify code (ask agent to add features) because sandboxing makes it safe
- Departure from 25 years of SaaS architecture — AI changes the equation

### Three Pillars
1. **Agent Chat UI**: Ask agents to do tasks, preloaded with knowledge about how your company operates
2. **Sandboxed App Development**: Ask agents to build "gadgets" (small personal apps), safely share with others
3. **Security Framework (Gatekeepers)**: Guardrails for both agents and apps so non-technical users can safely use AI

## Technical Stack
- Runs on wrangler and workerd (Cloudflare Workers runtime)
- pnpm-based monorepo
- Local dev: pnpm run-local → localhost:8787
- Deploy to Cloudflare account via os.cloudflare.app/deploy

## Key Features
- Built-in blueprints (slides, whiteboard, tic-tac-toe, issue dashboard, Google Docs integration)
- GitHub integration for repo analysis
- Google Docs integration for editing
- Private gadget instances with full code modifiability
- Security by isolation (each gadget = separate sandbox)

## Relevance to Eli
Cloudflare OS's gadget concept maps to Eli's agent architecture: each client gets their own agent instance with isolated knowledge. The Gatekeepers concept maps to Eli's input sanitization and prompt injection guards. The blueprint system maps to Eli's skill system.