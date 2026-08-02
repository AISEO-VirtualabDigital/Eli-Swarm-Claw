const initialState = {
  health: {
    status: 'Healthy',
    message: 'Pilot runner ready for dry-run submissions.',
    lastUpdated: 'just now',
  },
  status: {
    submittedCommands: 0,
    approvedCount: 0,
    completedCount: 0,
    blockedCount: 0,
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
    approvalMode: 'manual review',
    lastCommand: 'None',
  },
};

let state = structuredClone(initialState);

function render() {
  renderHealthPanel();
  renderLatestResult();
  renderAudit();
  renderSummary();
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
      <dd>${state.status.submittedCommands}</dd>
    </div>
  `;
}

function renderLatestResult() {
  const container = document.getElementById('latestResult');
  container.textContent = `${state.latestResult.status}\n${state.latestResult.message}`;
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
      <strong>${state.pilotState.approvalMode}</strong>
    </div>
    <div class="summary-card">
      <span>Completed</span>
      <strong>${state.status.completedCount}</strong>
    </div>
    <div class="summary-card">
      <span>Blocked</span>
      <strong>${state.status.blockedCount}</strong>
    </div>
    <div class="summary-card">
      <span>Last command</span>
      <strong>${state.pilotState.lastCommand}</strong>
    </div>
  `;
}

function submitDryRun(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const command = document.getElementById('commandInput').value.trim();
  const approvalRequested = document.getElementById('approvalToggle').checked;

  state.status.submittedCommands += 1;
  state.pilotState.lastCommand = command || 'empty command';

  if (!command) {
    state.latestResult = {
      status: 'Blocked',
      message: 'Command input is empty. Submission requires a dry-run description.',
    };
    state.status.blockedCount += 1;
    state.audit.unshift({
      label: 'blocked',
      detail: 'Submission rejected because the command field was empty.',
    });
    render();
    return;
  }

  if (approvalRequested) {
    state.latestResult = {
      status: 'Dry Run Approved',
      message: `Approval requested for: ${command}`,
    };
    state.status.approvedCount += 1;
    state.status.completedCount += 1;
    state.audit.unshift({
      label: 'approved',
      detail: `Approval requested for ${command}`,
    });
  } else {
    state.latestResult = {
      status: 'Blocked',
      message: `No approval was supplied for: ${command}`,
    };
    state.status.blockedCount += 1;
    state.audit.unshift({
      label: 'blocked',
      detail: `Dry-run blocked pending approval for ${command}`,
    });
  }

  state.health.lastUpdated = new Date().toLocaleTimeString();
  render();
  form.reset();
}

window.addEventListener('DOMContentLoaded', () => {
  render();
  document.getElementById('commandForm').addEventListener('submit', submitDryRun);
});
