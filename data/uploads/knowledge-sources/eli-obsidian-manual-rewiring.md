# Eli-OS Manual Rewiring Policy

## MANUAL-REWIRING-POLICY.md

---
id: manual-rewiring-policy
type: workflow_policy
status: accepted
authority: binding
project_id: eli-os
---

# Human Manual Rewiring Policy

## Absolute Rule

A human-authored workflow graph overrides Auto Mode composition.

## Required Behavior

When manual rewiring occurs:

1. Save the previous graph version.
2. Save the new graph version.
3. Record the human actor.
4. Record the reason.
5. Compute the graph diff.
6. Detect affected nodes and outputs.
7. Mark affected outputs stale.
8. Re-run static DAG validation.
9. Re-check validator dominance.
10. Re-check permissions and side-effect policies.
11. Require human confirmation before executing newly introduced destructive paths.

## Auto Mode Restrictions

Auto Mode may not silently:

- Reconnect removed edges
- Restore replaced providers
- Remove human approval nodes
- Remove validators
- Change protected destinations
- Bypass manual-only nodes


## REWIRING-LOG.md

---
id: rewiring-log
type: workflow_rewiring_log
status: active
project_id: eli-os
---

# Manual Rewiring Log

## Entry Template

### Rewire ID

- Human actor:
- Date:
- Workflow:
- Previous version:
- New version:
- Reason:
- Nodes added:
- Nodes removed:
- Edges added:
- Edges removed:
- Providers replaced:
- Validators added:
- Human approvals added:
- Outputs invalidated:
- Revalidation result:
- Execution approval:


## WORKFLOW-GRAPH-TEMPLATE.md

---
id:
type: workflow_graph
status: draft
authority: human_authored
project_id:
workflow_id:
version:
---

# Workflow Graph

## Goal

## Nodes

## Edges

## Protected Actions

## Required Validators

## Human Approval Gates

## Fallback Paths

## Disabled Paths

## Rewiring Notes
