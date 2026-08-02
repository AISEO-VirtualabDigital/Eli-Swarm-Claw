const initialState = {
  health: {
    status: 'Healthy',
    message: 'Pilot runner ready for dry-run submissions.',
    lastUpdated: 'just now',
  },
  status: {
    total_submitted_commands: 0,
    approved_count: 0,
    completed_count: 0,
    blocked_count: 0,
  },
  latestResult: {
    status: 'Idle',
    message: 'No submissions yet.',
  },
  audit: [
    {
      label: 'boot',
      detail: 'Pilot control panel initialized in dry-run mode.',
    },
  ],
  pilotState: {
    mode: 'Dry Run Only',
    approval_mode: 'manual review',
    latest_command: 'None',
  },
  ui: {
    isLoading: false,
    state: 'success',
    message: 'Pilot control panel ready.',
  },
};

let state = structuredClone(initialState);
const api = createMockPilotApiAdapter();

function applyHealth(payload) {
  state.health = {
    status: payload.status || 'healthy',
    message: payload.message || 'Pilot runner ready',
    lastUpdated: new Date().toLocaleTimeString(),
  };
}

function applyStatus(payload) {
  state.status = {
    total_submitted_commands: payload.total_submitted_commands || 0,
    approved_count: payload.approved_count || 0,
    completed_count: payload.completed_count || 0,
    blocked_count: payload.blocked_count || 0,
  };
}

function applyAuditReport(payload) {
  state.audit = [
    {
      label: 'audit-report',
      detail: `approved=${payload.approved_count || 0}, completed=${payload.completed_count || 0}, blocked=${payload.blocked_count || 0}`,
    },
    ...state.audit,
  ];
}

function applyPilotState(payload) {
  state.pilotState = {
    mode: payload.mode || 'Dry Run Only',
    approval_mode: payload.approval_mode || 'manual review',
    latest_command: payload.latest_command || 'None',
  };
}

function render() {
  renderHealthPanel();
  renderLatestResult();
  renderAudit();
  renderSummary();
  renderBanner();
}

function renderHealthPanel() {
  const panel = document.getElementById('healthPanel');
  panel.innerHTML = `
    <div class="status-list">
      <dt>Overall health</dt>
      <dd>${state.health.status}</dd>
      <dt>Message</dt>
      <dd>${state.health.message}</dd>
      <dt>Last update</dt>
      <dd>${state.health.lastUpdated}</dd>
      <dt>Submitted commands</dt>
      <dd>${state.status.total_submitted_commands}</dd>
    </div>
  `;
}

function renderLatestResult() {
  const container = document.getElementById('latestResult');
  container.textContent = `${state.latestResult.status}\n${state.latestResult.message}`;
  container.dataset.state = state.ui.state;
}

function renderAudit() {
  const list = document.getElementById('auditList');
  list.innerHTML = state.audit
    .map((entry) => `<li><strong>${entry.label}</strong><br />${entry.detail}</li>`)
    .join('');
}

function renderSummary() {
  const grid = document.getElementById('summaryGrid');
  grid.innerHTML = `
    <div class="summary-card">
      <span>Mode</span>
      <strong>${state.pilotState.mode}</strong>
    </div>
    <div class="summary-card">
      <span>Approval mode</span>
      <strong>${state.pilotState.approval_mode}</strong>
    </div>
    <div class="summary-card">
      <span>Completed</span>
      <strong>${state.status.completed_count}</strong>
    </div>
    <div class="summary-card">
      <span>Blocked</span>
      <strong>${state.status.blocked_count}</strong>
    </div>
    <div class="summary-card">
      <span>Last command</span>
      <strong>${state.pilotState.latest_command}</strong>
    </div>
  `;
}

function renderBanner() {
  const badge = document.getElementById('modeBadge');
  badge.textContent = `Pilot Mode / Dry Run Only · ${state.ui.state.toUpperCase()}`;
}

async function refreshPanel() {
  state.ui.isLoading = true;
  state.ui.state = 'loading';
  state.ui.message = 'Loading pilot data...';
  render();

  try {
    const [health, status, auditReport, pilotState] = await Promise.all([
      api.getHealth(),
      api.getStatus(),
      api.getAuditReport(),
      api.getPilotState(),
    ]);

    applyHealth(health);
    applyStatus(status);
    applyAuditReport(auditReport);
    applyPilotState(pilotState);
    state.ui.state = 'success';
    state.ui.message = 'Pilot data refreshed.';
  } catch (error) {
    state.ui.state = 'error';
    state.ui.message = error.message || 'Unable to refresh pilot data.';
  } finally {
    state.ui.isLoading = false;
    render();
  }
}

async function submitDryRun(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const command = document.getElementById('commandInput').value.trim();
  const approvalRequested = document.getElementById('approvalToggle').checked;
  const submitButton = form.querySelector('button[type="submit"]');

  state.ui.isLoading = true;
  state.ui.state = 'loading';
  state.ui.message = 'Submitting dry-run request...';
  submitButton.disabled = true;
  render();

  try {
    const payload = await api.submitDryRun({
      command,
      approval_required: approvalRequested,
    });

    if (payload.status === 'blocked') {
      state.ui.state = 'blocked';
      state.ui.message = payload.message;
      state.latestResult = {
        status: 'Blocked',
        message: payload.message,
      };
    } else {
      state.ui.state = 'success';
      state.ui.message = payload.message;
      state.latestResult = {
        status: payload.status === 'dry_run_approved' ? 'Dry Run Approved' : 'Accepted',
        message: payload.message,
      };
    }

    await refreshPanel();
    form.reset();
  } catch (error) {
    state.ui.state = 'error';
    state.ui.message = error.message || 'Pilot submission failed.';
    state.latestResult = {
      status: 'Error',
      message: state.ui.message,
    };
    render();
  } finally {
    submitButton.disabled = false;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  render();
  document.getElementById('commandForm').addEventListener('submit', submitDryRun);
  refreshPanel();
});
