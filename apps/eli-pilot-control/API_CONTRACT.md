# Pilot Control API Contract (Future Subdomain Backend)

The following endpoints describe the intended contract for a future subdomain backend that will power the Eli pilot control panel.

## GET /health
Returns the current pilot health.

Example response:
{
  "status": "healthy",
  "message": "Pilot runner ready"
}

## GET /status
Returns pilot execution and state counters.

Example response:
{
  "total_submitted_commands": 1,
  "approved_count": 1,
  "completed_count": 1,
  "blocked_count": 0
}

## POST /dry-run
Submits a dry-run command.

Example request:
{
  "command": "preview audit trail",
  "approval_required": true
}

Example response:
{
  "status": "dry_run_pending",
  "message": "Dry run accepted for review"
}

## GET /audit-report
Returns the current audit report.

Example response:
{
  "total_count": 2,
  "approved_count": 1,
  "completed_count": 1,
  "blocked_count": 0
}

## GET /pilot-state
Returns the latest pilot state summary.

Example response:
{
  "mode": "Dry Run Only",
  "approval_mode": "manual review",
  "latest_command": "preview audit trail"
}
