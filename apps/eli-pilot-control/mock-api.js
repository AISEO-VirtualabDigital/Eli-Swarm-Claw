function createMockPilotApiAdapter() {
  const initialSnapshot = {
    health: {
      status: 'healthy',
      message: 'Pilot runner ready for dry-run submissions.',
    },
    status: {
      total_submitted_commands: 0,
      approved_count: 0,
      completed_count: 0,
      blocked_count: 0,
    },
    auditReport: {
      total_count: 0,
      approved_count: 0,
      completed_count: 0,
      blocked_count: 0,
    },
    pilotState: {
      mode: 'Dry Run Only',
      approval_mode: 'manual review',
      latest_command: 'None',
    },
  };

  let snapshot = structuredClone(initialSnapshot);

  return {
    async getHealth() {
      // TODO: replace this mock response with the real Phase 6 runner-backed API later.
      return Promise.resolve(snapshot.health);
    },

    async getStatus() {
      // TODO: replace this mock response with the real Phase 6 runner-backed API later.
      return Promise.resolve(snapshot.status);
    },

    async submitDryRun({ command, approval_required }) {
      // TODO: replace this mock submission flow with the real local pilot runner contract later.
      snapshot.status.total_submitted_commands += 1;

      if (!command || command.trim().length === 0) {
        snapshot.status.blocked_count += 1;
        snapshot.auditReport.blocked_count += 1;
        snapshot.auditReport.total_count += 1;
        snapshot.pilotState.latest_command = 'empty command';
        return Promise.resolve({
          status: 'blocked',
          message: 'Command input is empty. Submission requires a dry-run description.',
        });
      }

      if (approval_required) {
        snapshot.status.approved_count += 1;
        snapshot.status.completed_count += 1;
        snapshot.auditReport.approved_count += 1;
        snapshot.auditReport.completed_count += 1;
        snapshot.auditReport.total_count += 1;
        snapshot.pilotState.latest_command = command;
        return Promise.resolve({
          status: 'dry_run_approved',
          message: `Dry-run accepted for review: ${command}`,
        });
      }

      snapshot.status.blocked_count += 1;
      snapshot.auditReport.blocked_count += 1;
      snapshot.auditReport.total_count += 1;
      snapshot.pilotState.latest_command = command;
      return Promise.resolve({
        status: 'blocked',
        message: `Dry-run blocked pending approval: ${command}`,
      });
    },

    async getAuditReport() {
      // TODO: replace this mock response with the real Phase 6 runner-backed API later.
      return Promise.resolve(snapshot.auditReport);
    },

    async getPilotState() {
      // TODO: replace this mock response with the real Phase 6 runner-backed API later.
      return Promise.resolve(snapshot.pilotState);
    },
  };
}
