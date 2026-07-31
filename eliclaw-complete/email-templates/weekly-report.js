module.exports = (data) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Weekly Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
    .card { background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 16px; border: 1px solid #334155; }
    .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .stat { background: #0f172a; padding: 20px; border-radius: 12px; text-align: center; }
    .stat-value { font-size: 28px; font-weight: bold; color: #3b82f6; }
    .stat-label { font-size: 12px; color: #94a3b8; margin-top: 4px; }
    .up { color: #22c55e; }
    .down { color: #ef4444; }
    .footer { text-align: center; margin-top: 30px; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div style="text-align: center; margin-bottom: 30px;">
      <span style="font-size: 28px; font-weight: bold; background: linear-gradient(135deg, #3b82f6, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EliClaw</span>
      <h1 style="font-size: 22px; margin-top: 16px;">Weekly Growth Report</h1>
      <p style="color: #94a3b8;">Hi ${data.name || 'there'}, here's how you performed this week.</p>
    </div>

    <div class="card">
      <div class="stats">
        <div class="stat">
          <div class="stat-value">${data.audits || 0}</div>
          <div class="stat-label">Audits Run</div>
        </div>
        <div class="stat">
          <div class="stat-value">${data.leads || 0}</div>
          <div class="stat-label">Leads Captured</div>
        </div>
        <div class="stat">
          <div class="stat-value ${data.scoreChange >= 0 ? 'up' : 'down'}">${data.score || 72}</div>
          <div class="stat-label">Avg SEO Score</div>
        </div>
        <div class="stat">
          <div class="stat-value">${data.competitors || 0}</div>
          <div class="stat-label">Competitors Tracked</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 style="font-size: 18px; margin-bottom: 16px;">This Week's Highlights</h2>
      <ul style="color: #94a3b8; padding-left: 20px; line-height: 1.8;">
        <li>Your highest scoring audit was <strong style="color: #e2e8f0;">${data.bestAudit || 'example.com'}</strong> with <strong style="color: #22c55e;">${data.bestScore || 85}/100</strong></li>
        <li><strong style="color: #e2e8f0;">${data.newLeads || 3}</strong> new leads were captured from your website</li>
        <li>Swarm Agents completed <strong style="color: #e2e8f0;">${data.agentTasks || 12}</strong> tasks automatically</li>
      </ul>
    </div>

    <div style="text-align: center;">
      <a href="https://eliclaw.virtualabdigital.com/dashboard" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600;">View Full Dashboard</a>
    </div>

    <div class="footer">
      <p>You're receiving this because you subscribed to weekly reports.</p>
      <p><a href="https://eliclaw.virtualabdigital.com/settings" style="color: #3b82f6;">Manage preferences</a></p>
    </div>
  </div>
</body>
</html>
`;