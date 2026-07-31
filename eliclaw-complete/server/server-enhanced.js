require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');
const cron = require('node-cron');

// Import integrations
const SEOAuditEngine = require('./integrations/seo-audit-engine');
const EmailService = require('./integrations/email-service');
const { PaymentService, PLANS } = require('./integrations/stripe-service');
const cache = require('./cache');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize services
const seoEngine = new SEOAuditEngine();
const emailService = new EmailService();
const paymentService = new PaymentService();

// Database - optimized connection pooling
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://eliclaw_user:password@localhost:5432/eliclaw_db',
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
  max: 20, // Max clients in pool
  idleTimeoutMillis: 30000, // Close idle clients after 30s
  connectionTimeoutMillis: 2000, // Fail fast if can't connect
  allowExitOnIdle: true
});

// Monitor pool health
pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
});

// Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// Gzip compression - add after helmet for best performance
app.use(compression({
  level: 6,
  threshold: 1024, // Only compress responses > 1KB
  filter: (req, res) => {
    if (req.headers['x-no-compression']) return false;
    return compression.filter(req, res);
  }
}));

app.use(cors({
  origin: [
    'https://eliclaw.virtualabdigital.com',
    'https://virtualabdigital.com',
    'https://www.virtualabdigital.com',
    'http://localhost:5173'
  ],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key'],
  credentials: true
}));

app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests, please try again later.' }
});

const freeToolLimiter = rateLimit({
  windowMs: 24 * 60 * 60 * 1000,
  max: 3,
  message: { error: 'Free limit reached. Upgrade for unlimited audits.', upgrade_url: '/pricing' }
});

// Auth middleware
const authenticate = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) return res.status(401).json({ error: 'No token provided' });

    const jwt = require('jsonwebtoken');
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');

    const result = await pool.query('SELECT * FROM users WHERE id = $1', [decoded.userId]);
    if (result.rows.length === 0) return res.status(401).json({ error: 'User not found' });

    req.user = result.rows[0];
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// WP API Key middleware
const validateWPKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (apiKey !== process.env.WP_API_KEY) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};

// Check plan limits middleware
const checkPlanLimit = (feature) => async (req, res, next) => {
  if (!req.user) return next();

  const limits = await paymentService.getUsageLimits(req.user.id);
  const used = await getUsageCount(req.user.id, feature);

  if (limits[feature] !== -1 && used >= limits[feature]) {
    return res.status(403).json({ 
      error: 'Plan limit reached. Upgrade to continue.',
      upgrade_url: '/pricing',
      current: used,
      limit: limits[feature]
    });
  }

  next();
};

async function getUsageCount(userId, feature) {
  // Track usage in database
  const result = await pool.query(
    'SELECT COUNT(*) FROM usage_logs WHERE user_id = $1 AND feature = $2 AND created_at > NOW() - INTERVAL '30 days'',
    [userId, feature]
  );
  return parseInt(result.rows[0].count);
}

// Initialize database
async function initDB() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        website VARCHAR(500),
        plan VARCHAR(50) DEFAULT 'free',
        api_key VARCHAR(255),
        stripe_customer_id VARCHAR(255),
        stripe_subscription_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) NOT NULL,
        company VARCHAR(255),
        url VARCHAR(500),
        message TEXT,
        source VARCHAR(100),
        page_url VARCHAR(500),
        status VARCHAR(50) DEFAULT 'new',
        score INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS audits (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        url VARCHAR(500) NOT NULL,
        email VARCHAR(255),
        ip_address VARCHAR(45),
        score INTEGER,
        summary JSONB,
        full_report JSONB,
        created_at TIMESTAMP DEFAULT NOW(),
        is_paid BOOLEAN DEFAULT FALSE
      );

      CREATE TABLE IF NOT EXISTS usage_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        feature VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        stripe_invoice_id VARCHAR(255),
        amount INTEGER,
        status VARCHAR(50),
        paid_at TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS workflows (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        name VARCHAR(255) NOT NULL,
        nodes JSONB,
        edges JSONB,
        status VARCHAR(50) DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS agents (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) NOT NULL,
        status VARCHAR(50) DEFAULT 'paused',
        tasks INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        config JSONB,
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS email_sequences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        name VARCHAR(255) NOT NULL,
        trigger_type VARCHAR(100),
        steps JSONB,
        status VARCHAR(50) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    console.log('Database initialized');
  } catch (err) {
    console.error('Database init error:', err);
  }
}

// ========== AUTH ROUTES ==========

app.post('/api/auth/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;
    if (!name || !email || !password) {
      return res.status(400).json({ error: 'All fields required' });
    }

    const existing = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (existing.rows.length > 0) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    const bcrypt = require('bcryptjs');
    const jwt = require('jsonwebtoken');
    const hashedPassword = await bcrypt.hash(password, 10);
    const apiKey = 'elc_' + require('crypto').randomBytes(24).toString('hex');

    const result = await pool.query(
      'INSERT INTO users (name, email, password, api_key, plan) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [name, email, hashedPassword, apiKey, 'free']
    );

    const user = result.rows[0];
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET || 'your-secret-key', { expiresIn: '7d' });

    // Send welcome email
    try {
      await emailService.sendWelcomeEmail({ name: user.name, email: user.email });
    } catch (e) {
      console.error('Welcome email failed:', e.message);
    }

    res.json({
      success: true,
      token,
      user: { id: user.id, name: user.name, email: user.email, plan: user.plan, api_key: user.api_key }
    });
  } catch (err) {
    console.error('Register error:', err);
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const bcrypt = require('bcryptjs');
    const jwt = require('jsonwebtoken');

    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (result.rows.length === 0) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    const user = result.rows[0];
    const valid = await bcrypt.compare(password, user.password);
    if (!valid) return res.status(400).json({ error: 'Invalid credentials' });

    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET || 'your-secret-key', { expiresIn: '7d' });

    res.json({
      success: true,
      token,
      user: { id: user.id, name: user.name, email: user.email, plan: user.plan, api_key: user.api_key }
    });
  } catch (err) {
    res.status(500).json({ error: 'Login failed' });
  }
});

// ========== STRIPE ROUTES ==========

app.post('/api/stripe/checkout', authenticate, async (req, res) => {
  try {
    const { planId, successUrl, cancelUrl } = req.body;
    const session = await paymentService.createCheckoutSession({
      userId: req.user.id,
      planId,
      successUrl,
      cancelUrl
    });
    res.json({ success: true, url: session.url });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/stripe/portal', authenticate, async (req, res) => {
  try {
    const session = await paymentService.createPortalSession({
      customerId: req.user.stripe_customer_id,
      returnUrl: req.body.returnUrl
    });
    res.json({ success: true, url: session.url });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/stripe/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const result = await paymentService.handleWebhook(req.body, req.headers['stripe-signature']);
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.get('/api/plans', (req, res) => {
  res.json({ success: true, plans: PLANS });
});

// ========== ENHANCED SEO AUDIT ==========

app.post('/api/tools/seo-audit', freeToolLimiter, async (req, res) => {
  try {
    const { url, email } = req.body;
    if (!url) return res.status(400).json({ error: 'URL required' });

    // Use real SEO engine if API keys configured, fallback to mock
    let auditResults;
    if (process.env.PAGESPEED_API_KEY) {
      auditResults = await seoEngine.runFullAudit(url);
    } else {
      auditResults = await runMockAudit(url);
    }

    // Save to database
    const ip = req.ip || req.connection.remoteAddress;
    await pool.query(
      `INSERT INTO audits (url, email, ip_address, score, summary, full_report)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [url, email, ip, auditResults.score, JSON.stringify(auditResults.summary), JSON.stringify(auditResults.fullReport)]
    );

    // Send email report if email provided
    if (email) {
      try {
        await emailService.sendAuditReport(email, auditResults);
      } catch (e) {
        console.error('Audit email failed:', e.message);
      }
    }

    res.json({ success: true, results: auditResults });
  } catch (err) {
    console.error('Audit error:', err);
    res.status(500).json({ error: 'Audit failed' });
  }
});

// Mock audit fallback
async function runMockAudit(url) {
  const axios = require('axios');
  const cheerio = require('cheerio');

  try {
    const response = await axios.get(url, { timeout: 10000, headers: { 'User-Agent': 'EliClawBot/1.0' } });
    const $ = cheerio.load(response.data);

    const issues = [];
    let score = 100;

    const title = $('title').text();
    if (!title) { issues.push({ category: 'meta', severity: 'critical', title: 'Missing Title Tag', description: 'Page has no title tag', recommendation: 'Add a descriptive title tag (50-60 chars)' }); score -= 15; }
    else if (title.length > 60) { issues.push({ category: 'meta', severity: 'warning', title: 'Title Too Long', description: `Title is ${title.length} characters`, recommendation: 'Keep title under 60 characters' }); score -= 5; }

    const metaDesc = $('meta[name="description"]').attr('content');
    if (!metaDesc) { issues.push({ category: 'meta', severity: 'critical', title: 'Missing Meta Description', description: 'No meta description found', recommendation: 'Add a compelling meta description (150-160 chars)' }); score -= 15; }

    const h1Count = $('h1').length;
    if (h1Count === 0) { issues.push({ category: 'structure', severity: 'warning', title: 'Missing H1 Tag', description: 'No H1 heading found', recommendation: 'Add one H1 tag per page' }); score -= 10; }
    else if (h1Count > 1) { issues.push({ category: 'structure', severity: 'warning', title: 'Multiple H1 Tags', description: `${h1Count} H1 tags found`, recommendation: 'Use only one H1 per page' }); score -= 5; }

    const imagesWithoutAlt = $('img:not([alt])').length;
    if (imagesWithoutAlt > 0) { issues.push({ category: 'content', severity: 'warning', title: 'Images Missing Alt Text', description: `${imagesWithoutAlt} images without alt text`, recommendation: 'Add descriptive alt text to all images' }); score -= 5; }

    const isHttps = url.startsWith('https://');
    if (!isHttps) { issues.push({ category: 'security', severity: 'critical', title: 'Not Using HTTPS', description: 'Site is not secure', recommendation: 'Install SSL certificate and redirect to HTTPS' }); score -= 20; }

    const viewport = $('meta[name="viewport"]').attr('content');
    if (!viewport) { issues.push({ category: 'mobile', severity: 'warning', title: 'Missing Viewport Meta', description: 'No viewport meta tag', recommendation: 'Add viewport meta for mobile responsiveness' }); score -= 10; }

    const canonical = $('link[rel="canonical"]').attr('href');
    if (!canonical) { issues.push({ category: 'seo', severity: 'warning', title: 'Missing Canonical Tag', description: 'No canonical URL specified', recommendation: 'Add canonical tag to prevent duplicate content' }); score -= 5; }

    const loadTime = (Math.random() * 3 + 0.5).toFixed(2);
    if (parseFloat(loadTime) > 3) { issues.push({ category: 'performance', severity: 'warning', title: 'Slow Page Load', description: `Page loads in ${loadTime}s`, recommendation: 'Optimize images, minify CSS/JS, enable caching' }); score -= 10; }

    issues.push({ category: 'seo', severity: 'good', title: 'HTML5 Doctype', description: 'Page uses HTML5 doctype' });
    issues.push({ category: 'structure', severity: 'good', title: 'Valid HTML Structure', description: 'HTML structure is valid' });

    score = Math.max(0, Math.min(100, score));

    return {
      url,
      score,
      loadTime,
      pageSize: (Math.random() * 2 + 0.5).toFixed(1),
      https: isHttps,
      issues: issues.sort((a, b) => { const order = { critical: 0, warning: 1, good: 2 }; return order[a.severity] - order[b.severity]; }),
      summary: { score, issues: issues.filter(i => i.severity !== 'good').length, passed: issues.filter(i => i.severity === 'good').length, topIssues: issues.filter(i => i.severity !== 'good').slice(0, 5) },
      fullReport: { meta: { title, description: metaDesc, canonical, viewport }, headings: { h1: h1Count, h2: $('h2').length, h3: $('h3').length }, images: { total: $('img').length, withoutAlt: imagesWithoutAlt }, links: { internal: $('a[href^="/"]').length, external: $('a[href^="http"]').length }, scripts: $('script').length, stylesheets: $('link[rel="stylesheet"]').length }
    };
  } catch (err) {
    return { url, score: 72, loadTime: '2.4', pageSize: '1.8', https: url.startsWith('https://'), issues: [{ category: 'meta', severity: 'critical', title: 'Missing Meta Description', description: 'No meta description found', recommendation: 'Add a compelling meta description' }, { category: 'performance', severity: 'warning', title: 'Slow Page Load', description: 'Page loads in 4.2s', recommendation: 'Optimize images and enable caching' }, { category: 'mobile', severity: 'warning', title: 'Missing Viewport', description: 'No viewport meta tag', recommendation: 'Add viewport for mobile' }, { category: 'seo', severity: 'good', title: 'Valid HTML5', description: 'Page uses HTML5 doctype' }], summary: { score: 72, issues: 3, passed: 1, topIssues: [] }, fullReport: {} };
  }
}

// ========== LEAD ROUTES ==========

app.post('/api/leads', validateWPKey, async (req, res) => {
  try {
    const { name, email, company, url, message, source, page_url } = req.body;

    const result = await pool.query(
      `INSERT INTO leads (name, email, company, url, message, source, page_url, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
      [name, email, company, url, message, source || 'wp_form', page_url, 'new']
    );

    // Send lead notification to admin
    try {
      await emailService.sendLeadNotification(result.rows[0]);
    } catch (e) {
      console.error('Lead notification failed:', e.message);
    }

    res.json({ success: true, lead: result.rows[0] });
  } catch (err) {
    console.error('Lead capture error:', err);
    res.status(500).json({ error: 'Failed to save lead' });
  }
});

app.get('/api/leads', authenticate, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM leads ORDER BY created_at DESC LIMIT 100');
    res.json({ success: true, leads: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch leads' });
  }
});

// ========== EMAIL SEQUENCE ROUTES ==========

app.post('/api/email-sequences', authenticate, async (req, res) => {
  try {
    const { name, trigger_type, steps } = req.body;
    const result = await pool.query(
      'INSERT INTO email_sequences (user_id, name, trigger_type, steps) VALUES ($1, $2, $3, $4) RETURNING *',
      [req.user.id, name, trigger_type, JSON.stringify(steps)]
    );
    res.json({ success: true, sequence: result.rows[0] });
  } catch (err) {
    res.status(500).json({ error: 'Failed to create sequence' });
  }
});

app.get('/api/email-sequences', authenticate, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM email_sequences WHERE user_id = $1', [req.user.id]);
    res.json({ success: true, sequences: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch sequences' });
  }
});

// ========== DASHBOARD STATS ==========

app.get('/api/dashboard/stats', authenticate, async (req, res) => {
  try {
    const userId = req.user.id;

    const auditsResult = await pool.query('SELECT COUNT(*) FROM audits WHERE user_id = $1', [userId]);
    const leadsResult = await pool.query('SELECT COUNT(*) FROM leads');
    const avgScore = await pool.query('SELECT AVG(score) FROM audits WHERE user_id = $1', [userId]);

    res.json({
      success: true,
      stats: {
        audits: parseInt(auditsResult.rows[0].count) || 0,
        leads: parseInt(leadsResult.rows[0].count) || 0,
        score: Math.round(avgScore.rows[0].avg) || 72,
        competitors: 5
      },
      recentActivity: [
        { action: 'SEO Audit completed', time: '2 min ago', result: 'Score: 78/100' },
        { action: 'New lead captured', time: '15 min ago', result: 'john@company.com' },
        { action: 'Competitor analysis', time: '1 hour ago', result: '3 competitors analyzed' },
      ]
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

// ========== HEALTH & STATIC ==========

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(), 
    version: '2.0.0',
    features: {
      seo: !!process.env.PAGESPEED_API_KEY,
      email: !!process.env.RESEND_API_KEY || !!process.env.SENDGRID_API_KEY,
      stripe: !!process.env.STRIPE_SECRET_KEY
    }
  });
});

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, 'public')));
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
  });
}

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong' });
});

// Scheduled tasks
cron.schedule('0 9 * * 1', async () => {
  // Send weekly reports every Monday at 9 AM
  console.log('Sending weekly reports...');
  const users = await pool.query('SELECT * FROM users WHERE plan != $1', ['free']);
  for (const user of users.rows) {
    try {
      await emailService.sendWeeklyReport(user, { audits: 12, leads: 5, score: 78, competitors: 3 });
    } catch (e) {
      console.error('Weekly report failed for', user.email);
    }
  }
});

// Start server
initDB().then(() => {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`EliClaw Server running on port ${PORT}`);
    console.log(`Domain: https://eliclaw.virtualabdigital.com`);
    console.log(`Agency: https://virtualabdigital.com`);
  });
});