module.exports = (data) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Competitor Alert</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 0; }
    .container { max-width: 500px; margin: 0 auto; padding: 40px 20px; }
    .card { background: #1e293b; border-radius: 16px; padding: 24px; border: 1px solid #334155; }
    .alert-badge { display: inline-block; background: #f59e0b; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .change { display: flex; align-items: center; gap: 12px; padding: 12px; background: #0f172a; border-radius: 8px; margin-bottom: 8px; }
    .change-icon { font-size: 20px; }
    .footer { text-align: center; margin-top: 24px; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div style="text-align: center; margin-bottom: 24px;">
      <span style="font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #3b82f6, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EliClaw</span>
    </div>

    <div class="card">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <span class="alert-badge">COMPETITOR ALERT</span>
      </div>

      <h1 style="font-size: 20px; margin-bottom: 8px;">${data.competitor} Made Changes</h1>
      <p style="color: #94a3b8; margin-bottom: 20px;">We detected significant changes that may affect your rankings.</p>

      <h2 style="font-size: 16px; margin-bottom: 12px;">Detected Changes:</h2>
      ${(data.changes || []).map(change => `
        <div class="change">
          <span class="change-icon">${change.type === 'ranking' ? '📈' : change.type === 'content' ? '📝' : change.type === 'backlinks' ? '🔗' : '⚡'}</span>
          <div>
            <div style="font-weight: 600;">${change.title}</div>
            <div style="font-size: 13px; color: #94a3b8;">${change.description}</div>
          </div>
        </div>
      `).join('')}

      <a href="https://eliclaw.virtualabdigital.com/tools/competitor" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; margin-top: 16px;">View Full Analysis</a>
    </div>

    <div class="footer">
      <p>EliClaw Competitor Monitoring by Virtualab Digital</p>
    </div>
  </div>
</body>
</html>
`;