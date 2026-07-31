module.exports = (data) => `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SEO Audit Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
    .header { text-align: center; margin-bottom: 30px; }
    .score-ring { width: 120px; height: 120px; border-radius: 50%; border: 8px solid ${data.score >= 80 ? '#22c55e' : data.score >= 60 ? '#f59e0b' : '#ef4444'}; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; font-size: 36px; font-weight: bold; }
    .card { background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 16px; border: 1px solid #334155; }
    h1 { font-size: 24px; margin-bottom: 8px; }
    .url { color: #3b82f6; font-size: 14px; word-break: break-all; }
    .metric { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #334155; }
    .metric:last-child { border-bottom: none; }
    .btn { display: inline-block; background: linear-gradient(135deg, #3b82f6, #22d3ee); color: #fff; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; }
    .footer { text-align: center; margin-top: 30px; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="score-ring">${data.score}</div>
      <h1>SEO Audit Report</h1>
      <p class="url">${data.url}</p>
      <p style="color: #94a3b8;">${new Date().toLocaleDateString()}</p>
    </div>

    <div class="card">
      <h2 style="font-size: 18px; margin-bottom: 16px;">Key Metrics</h2>
      <div class="metric">
        <span>Load Time</span>
        <span style="font-weight: 600;">${data.loadTime || '2.4s'}</span>
      </div>
      <div class="metric">
        <span>Page Size</span>
        <span style="font-weight: 600;">${data.pageSize || '1.8 MB'}</span>
      </div>
      <div class="metric">
        <span>Issues Found</span>
        <span style="font-weight: 600; color: #ef4444;">${data.issues?.length || 0}</span>
      </div>
      <div class="metric">
        <span>HTTPS Secure</span>
        <span style="font-weight: 600; color: ${data.https ? '#22c55e' : '#ef4444'};">${data.https ? 'Yes' : 'No'}</span>
      </div>
    </div>

    <div class="card">
      <h2 style="font-size: 18px; margin-bottom: 16px;">Top Issues</h2>
      ${(data.issues || []).slice(0, 5).map(issue => `
        <div style="padding: 12px; background: #0f172a; border-radius: 8px; margin-bottom: 8px;">
          <div style="font-weight: 600; color: ${issue.severity === 'critical' ? '#ef4444' : '#f59e0b'};">${issue.title}</div>
          <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">${issue.recommendation}</div>
        </div>
      `).join('')}
    </div>

    <div style="text-align: center; margin-top: 24px;">
      <a href="https://eliclaw.virtualabdigital.com/tools/seo" class="btn">View Full Report</a>
    </div>

    <div class="footer">
      <p>Powered by EliClaw — <a href="https://virtualabdigital.com" style="color: #3b82f6;">Virtualab Digital</a></p>
    </div>
  </div>
</body>
</html>
`;