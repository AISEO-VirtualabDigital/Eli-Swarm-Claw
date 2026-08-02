# Eli Pilot Test Plan

## Pilot scenario checklist

- [ ] Open the static control panel locally
- [ ] Verify the Pilot Mode / Dry Run Only banner is visible
- [ ] Check the health/status panel
- [ ] Submit an approved dry-run command
- [ ] Submit an unapproved dry-run command
- [ ] Confirm the blocked unsafe/live execution path remains blocked
- [ ] Inspect the audit/report output
- [ ] Confirm no live execution endpoint exists

## Expected outcomes

- The panel loads without runtime execution
- The health and status views reflect mock dry-run state
- Approved dry-run submissions are tracked as completed
- Unapproved or unsafe submissions remain blocked
- Audit/report output stays visible and inspectable
