module.exports = (data) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>New Lead Notification</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 0; }
    .container { max-width: 500px; margin: 0 auto; padding: 40px 20px; }
    .card { background: #1e293b; border-radius: 16px; padding: 24px; border: 1px solid #334155; }
    .badge { display: inline-block; background: #22c55e; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .field { padding: 12px 0; border-bottom: 1px solid #334155; }
    .field:last-child { border-bottom: none; }
    .label { font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .value { font-size: 16px; color: #e2e8f0; margin-top: 4px; }
    .btn { display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; margin-top: 16px; }
  </style>
</head>
<body>
  <div class="container">
    <div style="text-align: center; margin-bottom: 24px;">
      <span style="font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #3b82f6, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EliClaw</span>
    </div>

    <div class="card">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
        <h1 style="font-size: 20px; margin: 0;">New Lead Captured!</h1>
        <span class="badge">NEW</span>
      </div>

      <div class="field">
        <div class="label">Name</div>
        <div class="value">${data.name || 'N/A'}</div>
      </div>
      <div class="field">
        <div class="label">Email</div>
        <div class="value">${data.email}</div>
      </div>
      <div class="field">
        <div class="label">Company</div>
        <div class="value">${data.company || 'N/A'}</div>
      </div>
      <div class="field">
        <div class="label">Website</div>
        <div class="value">${data.url || 'N/A'}</div>
      </div>
      <div class="field">
        <div class="label">Source</div>
        <div class="value">${data.source}</div>
      </div>
      <div class="field">
        <div class="label">Page URL</div>
        <div class="value" style="font-size: 13px;">${data.page_url || 'N/A'}</div>
      </div>

      <a href="https://eliclaw.virtualabdigital.com/leads" class="btn">View in Dashboard</a>
    </div>

    <div style="text-align: center; margin-top: 24px; color: #64748b; font-size: 12px;">
      <p>EliClaw by Virtualab Digital</p>
    </div>
  </div>
</body>
</html>
`;