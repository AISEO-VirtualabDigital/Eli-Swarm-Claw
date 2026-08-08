---
id: abs-cfos-security-92d428da
title: "Cloudflare OS Gatekeepers — Security Framework for AI Agents"
source: https://github.com/cloudflare/cloudflare-os
category: cloudflare-os
skillTags: ["security", "guardrails", "agent-safety", "sandbox"]
createdAt: 2026-08-07T15:24:11.126Z
absorbedFrom: github-research
---

Cloudflare OS includes a security framework called Gatekeepers that applies guardrails to both agents and applications, enabling non-technical users to safely use AI.

## Design Principles
- Security team can sleep at night — guardrails are built-in, not bolted on
- Non-technical users can "go nuts" and nothing bad will happen
- Sandboxed gadget instances control all access to user data
- Each user's app instance is isolated from every other user's instance

## Architecture
- Gatekeepers sit between the agent layer and the execution layer
- Every agent action passes through gatekeeper evaluation
- Guardrails are configurable per-workspace, per-user, and per-app
- The framework is designed to be extensible — organizations can add custom gatekeepers

## Mapping to Eli
- Eli needs a similar guardkeeper system for the Open Claw engine
- Before executing any action (creating inboxes, reading emails, injecting keys), a gatekeeper should validate the action
- Prevents the claw from being abused (e.g., rate limiting, domain restrictions, key validation)
- The sandbox concept applies: each Eli user session should have isolated state

## Open Source Release
Cloudflare OS went open source in August 2026. The repo is at github.com/cloudflare/cloudflare-os. It's version 2, a complete rewrite from v1 lessons learned.