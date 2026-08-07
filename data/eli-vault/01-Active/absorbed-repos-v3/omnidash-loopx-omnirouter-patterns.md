---
id: absorbed-omnidash-loopx-omnirouter-20250808
source: https://github.com/lalitdotdev/omnidash + https://github.com/huangruiteng/loopx + GitHub omni-router search
title: OmniDash + LoopX + OmniRouter Patterns
category: saas
skillTags: ["pattern", "strategy", "code"]
containmentHash: sha256-absorbed-omnidash-loopx
embeddingSig: trigram:dash:state:routing
---

# OmniDash + LoopX + OmniRouter — Absorbed Patterns

## From OmniDash

### Multi-Tenant Route Groups
- app/(auth)/ and app/(dashboard)/[storeId]/ route groups
- All routes scoped by dynamic storeId parameter
- Server components fetch tenant data, client components handle interaction

→ PATTERN NOTED: Eli could use route groups for multi-client support

### Horizontal + Vertical Navigation
- Top navbar: server component with DB-fetched store switcher + horizontal nav
- SideNav: client component with collapsible state, icon-only mode with tooltips
- usePathname() + useParams() for active state detection

→ PATTERN NOTED: for future Eli dashboard redesign

### Data-Driven Widget Cards
- Overview card takes generic data prop → renders Recharts BarChart
- Pattern: data-in, chart-out — fully decoupled from data source

→ PATTERN NOTED: for Eli dashboard when real metrics exist

## From LoopX

### Typed Turn Results
- Pre-execution: ready_for_host, repair_required, replan_required, user_action_required, wait, blocked
- Post-execution: validated_progress, validated_completion, repair_required, replan_required, user_action_required, wait, host_failure, validation_failed, writeback_failed, quota_spend_failed

→ WIRED into: omni-route.ts TurnResultKind type + recordResult() method

### Repair vs Replan
- repair_required: fix and retry same approach
- replan_required: restructure the entire approach
- These are distinct recovery routes, not just "try again"

→ WIRED into: omni-route.ts recordResult() switches on result kind

### State Ownership Boundaries
- Agent owns: planning, analysis, tool use, bounded execution
- Provider owns: external calls, observations, effect results
- Capability owns: outcome contract, normalization, validation
- Kernel owns: goal, todo, claim, gate, monitor, quota, writeback

→ PATTERN NOTED: clean separation for future Eli agent architecture

### Quiet Skip Policy
- Preflight failures and dry-run previews do NOT spend quota
- Failed turns are typed — cannot be silently discarded

→ PATTERN NOTED: for Eli's usage tracking

## From OmniRoute (diegosouzapw)

### 19 Routing Strategies
- priority, fill-first, weighted, round-robin, p2c (power-of-two-choices)
- least-used, random, cost-optimized, headroom, reset-window, reset-aware
- context-relay, context-optimized, cache-optimized, lkgp (last-known-good)
- auto (12-factor live scoring), fusion (fan-out + judge), pipeline (chain)

→ PATTERN NOTED: naming convention used for decision headers (X-Omni-Strategy)

### 3-Layer Resilience
- Layer 1: auto-combo (strategy selection)
- Layer 2: per-provider retry
- Layer 3: cross-combo fallback

→ WIRED into: omni-route.ts rotate() with maxAttempts + skipProviders

### Transparent Decision Headers
- X-OmniRoute-Decision on every response
- Names the strategy, provider, and latency used

→ WIRED into: eli-chat response headers via getDecisionHeaders()

### Quota-Share Routing
- Split shared account quotas fairly across pooled keys
- Work-conserving: uses full quota before moving to next

→ PATTERN NOTED: for future multi-key pooling in omni-route

## From Capitec Omni Router
- Web component SPA router with route guards, lazy loading, animation types
- Shadow/Light DOM support
- Not directly applicable to Eli (server-side app)

## From Apple ML Omni-Router
- Shared cross-layer MoE routing for consistent expert activation
- Model architecture pattern, not applicable to Eli's key rotation

## From ArdentCode Omni Router
- 7 lifecycle hooks: onGetRouteStart through onOpenRouteAbort
- Composable processor pipeline (HTML, Redirect, Meta, custom)
- Not directly applicable but the processor chain concept is useful
