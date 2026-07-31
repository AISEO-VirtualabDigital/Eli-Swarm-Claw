module.exports = (data) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to EliClaw</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
    .logo { text-align: center; margin-bottom: 30px; }
    .logo span { font-size: 32px; font-weight: bold; background: linear-gradient(135deg, #3b82f6, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .card { background: #1e293b; border-radius: 16px; padding: 32px; margin-bottom: 24px; border: 1px solid #334155; }
    h1 { font-size: 28px; margin-bottom: 16px; color: #fff; }
    p { color: #94a3b8; line-height: 1.6; font-size: 16px; }
    .btn { display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; margin-top: 20px; }
    .features { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }
    .feature { background: #0f172a; padding: 16px; border-radius: 12px; text-align: center; }
    .feature-icon { font-size: 24px; margin-bottom: 8px; }
    .feature-title { font-size: 14px; font-weight: 600; color: #e2e8f0; }
    .footer { text-align: center; margin-top: 40px; color: #64748b; font-size: 12px; }
    .footer a { color: #3b82f6; }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo"><span>EliClaw</span></div>

    <div class="card">
      <h1>Welcome aboard, ${data.name || 'there'}! 🎉</h1>
      <p>You're now part of the Virtualab Digital growth ecosystem. EliClaw is your all-in-one AI platform for SEO, competitor tracking, and automation.</p>
      <a href="${data.dashboardUrl}" class="btn">Open Dashboard</a>
    </div>

    <div class="card">
      <h2 style="font-size: 20px; margin-bottom: 16px;">Your Free Plan Includes:</h2>
      <div class="features">
        <div class="feature">
          <div class="feature-icon">🔍</div>
          <div class="feature-title">3 SEO Audits/mo</div>
        </div>
        <div class="feature">
          <div class="feature-icon">👥</div>
          <div class="feature-title">1 Competitor Analysis</div>
        </div>
        <div class="feature">
          <div class="feature-icon">🤖</div>
          <div class="feature-title">Swarm Agent Access</div>
        </div>
        <div class="feature">
          <div class="feature-icon">📊</div>
          <div class="feature-title">Basic Analytics</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2 style="font-size: 20px; margin-bottom: 16px;">Quick Start Guide</h2>
      <p>1. <strong>Run your first SEO audit</strong> — Enter any website URL and get instant insights</p>
      <p>2. <strong>Analyze competitors</strong> — Add up to 3 competitor URLs and compare metrics</p>
      <p>3. <strong>Deploy a Swarm Agent</strong> — Let AI agents monitor and optimize for you 24/7</p>
    </div>

    <div class="footer">
      <p>Need help? Reply to this email or visit our <a href="https://virtualabdigital.com/support">Support Center</a></p>
      <p>© 2026 EliClaw by Virtualab Digital. All rights reserved.</p>
      <p><a href="https://eliclaw.virtualabdigital.com">eliclaw.virtualabdigital.com</a> | <a href="https://virtualabdigital.com">virtualabdigital.com</a></p>
    </div>
  </div>
</body>
</html>
`;