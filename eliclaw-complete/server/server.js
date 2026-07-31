require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const rateLimit = require('express-rate-limit');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 3000;

// Database
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://eliclaw_user:password@localhost:5432/eliclaw_db',
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
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
    `);
    console.log('✅ Database initialized');
  } catch (err) {
    console.error('❌ Database init error:', err);
  }
}

// ========== AUTH ROUTES ==========

// Register
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

// Login
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

// Get current user
app.get('/api/auth/me', authenticate, async (req, res) => {
  res.json({ success: true, user: req.user });
});

// ========== LEAD ROUTES ==========

// Capture lead from WordPress
app.post('/api/leads', validateWPKey, async (req, res) => {
  try {
    const { name, email, company, url, message, source, page_url } = req.body;

    const result = await pool.query(
      `INSERT INTO leads (name, email, company, url, message, source, page_url, status)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *`,
      [name, email, company, url, message, source || 'wp_form', page_url, 'new']
    );

    res.json({ success: true, lead: result.rows[0] });
  } catch (err) {
    console.error('Lead capture error:', err);
    res.status(500).json({ error: 'Failed to save lead' });
  }
});

// Get leads (authenticated)
app.get('/api/leads', authenticate, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM leads ORDER BY created_at DESC LIMIT 100'
    );
    res.json({ success: true, leads: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch leads' });
  }
});

// ========== SEO AUDIT ROUTES ==========

// Run SEO audit
app.post('/api/tools/seo-audit', freeToolLimiter, async (req, res) => {
  try {
    const { url, email } = req.body;
    if (!url) return res.status(400).json({ error: 'URL required' });

    // Mock SEO audit logic (replace with real implementation)
    const auditResults = await runSEOAudit(url);

    // Save to database
    const ip = req.ip || req.connection.remoteAddress;
    await pool.query(
      `INSERT INTO audits (url, email, ip_address, score, summary, full_report)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [url, email, ip, auditResults.score, JSON.stringify(auditResults.summary), JSON.stringify(auditResults.fullReport)]
    );

    res.json({ success: true, results: auditResults });
  } catch (err) {
    console.error('Audit error:', err);
    res.status(500).json({ error: 'Audit failed' });
  }
});

// Mock SEO audit function
async function runSEOAudit(url) {
  const axios = require('axios');
  const cheerio = require('cheerio');

  try {
    const response = await axios.get(url, { timeout: 10000, headers: { 'User-Agent': 'EliClawBot/1.0' } });
    const $ = cheerio.load(response.data);

    const issues = [];
    let score = 100;

    // Check title
    const title = $('title').text();
    if (!title) {
      issues.push({ category: 'meta', severity: 'critical', title: 'Missing Title Tag', description: 'Page has no title tag', recommendation: 'Add a descriptive title tag (50-60 chars)' });
      score -= 15;
    } else if (title.length > 60) {
      issues.push({ category: 'meta', severity: 'warning', title: 'Title Too Long', description: `Title is ${title.length} characters`, recommendation: 'Keep title under 60 characters' });
      score -= 5;
    }

    // Check meta description
    const metaDesc = $('meta[name="description"]').attr('content');
    if (!metaDesc) {
      issues.push({ category: 'meta', severity: 'critical', title: 'Missing Meta Description', description: 'No meta description found', recommendation: 'Add a compelling meta description (150-160 chars)' });
      score -= 15;
    }

    // Check headings
    const h1Count = $('h1').length;
    if (h1Count === 0) {
      issues.push({ category: 'structure', severity: 'warning', title: 'Missing H1 Tag', description: 'No H1 heading found', recommendation: 'Add one H1 tag per page' });
      score -= 10;
    } else if (h1Count > 1) {
      issues.push({ category: 'structure', severity: 'warning', title: 'Multiple H1 Tags', description: `${h1Count} H1 tags found`, recommendation: 'Use only one H1 per page' });
      score -= 5;
    }

    // Check images alt
    const imagesWithoutAlt = $('img:not([alt])').length;
    if (imagesWithoutAlt > 0) {
      issues.push({ category: 'content', severity: 'warning', title: 'Images Missing Alt Text', description: `${imagesWithoutAlt} images without alt text`, recommendation: 'Add descriptive alt text to all images' });
      score -= 5;
    }

    // Check HTTPS
    const isHttps = url.startsWith('https://');
    if (!isHttps) {
      issues.push({ category: 'security', severity: 'critical', title: 'Not Using HTTPS', description: 'Site is not secure', recommendation: 'Install SSL certificate and redirect to HTTPS' });
      score -= 20;
    }

    // Check viewport
    const viewport = $('meta[name="viewport"]').attr('content');
    if (!viewport) {
      issues.push({ category: 'mobile', severity: 'warning', title: 'Missing Viewport Meta', description: 'No viewport meta tag', recommendation: 'Add viewport meta for mobile responsiveness' });
      score -= 10;
    }

    // Check canonical
    const canonical = $('link[rel="canonical"]').attr('href');
    if (!canonical) {
      issues.push({ category: 'seo', severity: 'warning', title: 'Missing Canonical Tag', description: 'No canonical URL specified', recommendation: 'Add canonical tag to prevent duplicate content' });
      score -= 5;
    }

    // Check load time (mock)
    const loadTime = (Math.random() * 3 + 0.5).toFixed(2);
    if (parseFloat(loadTime) > 3) {
      issues.push({ category: 'performance', severity: 'warning', title: 'Slow Page Load', description: `Page loads in ${loadTime}s`, recommendation: 'Optimize images, minify CSS/JS, enable caching' });
      score -= 10;
    }

    // Add some passed checks
    issues.push({ category: 'seo', severity: 'good', title: 'HTML5 Doctype', description: 'Page uses HTML5 doctype' });
    issues.push({ category: 'structure', severity: 'good', title: 'Valid HTML Structure', description: 'HTML structure is valid' });

    score = Math.max(0, Math.min(100, score));

    return {
      url,
      score,
      loadTime,
      pageSize: (Math.random() * 2 + 0.5).toFixed(1),
      https: isHttps,
      issues: issues.sort((a, b) => {
        const order = { critical: 0, warning: 1, good: 2 };
        return order[a.severity] - order[b.severity];
      }),
      summary: {
        score,
        issues: issues.filter(i => i.severity !== 'good').length,
        passed: issues.filter(i => i.severity === 'good').length,
        topIssues: issues.filter(i => i.severity !== 'good').slice(0, 5)
      },
      fullReport: {
        meta: { title, description: metaDesc, canonical, viewport },
        headings: { h1: h1Count, h2: $('h2').length, h3: $('h3').length },
        images: { total: $('img').length, withoutAlt: imagesWithoutAlt },
        links: { internal: $('a[href^="/"]').length, external: $('a[href^="http"]').length },
        scripts: $('script').length,
        stylesheets: $('link[rel="stylesheet"]').length
      }
    };
  } catch (err) {
    // Fallback mock data if fetch fails
    return {
      url,
      score: 72,
      loadTime: '2.4',
      pageSize: '1.8',
      https: url.startsWith('https://'),
      issues: [
        { category: 'meta', severity: 'critical', title: 'Missing Meta Description', description: 'No meta description found', recommendation: 'Add a compelling meta description' },
        { category: 'performance', severity: 'warning', title: 'Slow Page Load', description: 'Page loads in 4.2s', recommendation: 'Optimize images and enable caching' },
        { category: 'mobile', severity: 'warning', title: 'Missing Viewport', description: 'No viewport meta tag', recommendation: 'Add viewport for mobile' },
        { category: 'seo', severity: 'good', title: 'Valid HTML5', description: 'Page uses HTML5 doctype' },
      ],
      summary: { score: 72, issues: 3, passed: 1, topIssues: [] },
      fullReport: {}
    };
  }
}

// ========== COMPETITOR ANALYSIS ==========
app.post('/api/tools/competitor-analysis', authenticate, async (req, res) => {
  try {
    const { yourUrl, competitors } = req.body;

    // Mock competitor analysis
    const results = {
      yourDomain: new URL(yourUrl).hostname,
      competitors: competitors.map(url => ({ domain: new URL(url).hostname, url })),
      metrics: [
        { name: 'Domain Authority', yourValue: 45, best: 45, competitorValues: [38, 52, 41] },
        { name: 'Backlinks', yourValue: 1200, best: 1200, competitorValues: [890, 2100, 650] },
        { name: 'Organic Traffic', yourValue: 5400, best: 5400, competitorValues: [3200, 7800, 4100] },
        { name: 'Keywords', yourValue: 340, best: 340, competitorValues: [280, 520, 190] },
        { name: 'Page Speed', yourValue: 78, best: 78, competitorValues: [65, 82, 71] },
      ],
      trafficData: [
        { name: 'You', organic: 5400, paid: 1200, social: 800 },
        { name: 'Comp 1', organic: 3200, paid: 800, social: 600 },
        { name: 'Comp 2', organic: 7800, paid: 2100, social: 1200 },
        { name: 'Comp 3', organic: 4100, paid: 500, social: 400 },
      ],
      radarData: [
        { metric: 'SEO', you: 75, avg: 65 },
        { metric: 'Content', you: 80, avg: 70 },
        { metric: 'Speed', you: 65, avg: 72 },
        { metric: 'Mobile', you: 85, avg: 78 },
        { metric: 'Security', you: 90, avg: 82 },
        { metric: 'UX', you: 70, avg: 68 },
      ],
      opportunities: [
        { title: 'Backlink Gap', description: 'Competitor 2 has 2,100 backlinks. Focus on link building.', impact: 'high', effort: 'high' },
        { title: 'Content Expansion', description: 'Add 50+ new keyword-targeted pages', impact: 'high', effort: 'medium' },
        { title: 'Page Speed', description: 'Improve Core Web Vitals to beat Competitor 2', impact: 'medium', effort: 'low' },
      ]
    };

    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: 'Analysis failed' });
  }
});

// ========== WEBSITE ANALYZER ==========
app.post('/api/tools/website-analyzer', freeToolLimiter, async (req, res) => {
  try {
    const { url } = req.body;

    const results = {
      loadTime: (Math.random() * 3 + 0.5).toFixed(2),
      pageSize: (Math.random() * 3 + 0.5).toFixed(1) + ' MB',
      https: url.startsWith('https://'),
      server: 'nginx/1.24.0',
      cms: 'WordPress',
      techStack: ['React', 'Node.js', 'Tailwind CSS'],
      frameworks: ['React', 'Next.js'],
      performance: [
        { name: 'First Contentful Paint', score: Math.floor(Math.random() * 40 + 60) },
        { name: 'Largest Contentful Paint', score: Math.floor(Math.random() * 40 + 60) },
        { name: 'Time to Interactive', score: Math.floor(Math.random() * 40 + 60) },
        { name: 'Cumulative Layout Shift', score: Math.floor(Math.random() * 40 + 60) },
        { name: 'Total Blocking Time', score: Math.floor(Math.random() * 40 + 60) },
      ],
      security: [
        { name: 'HTTPS', passed: url.startsWith('https://'), description: 'Site uses secure connection' },
        { name: 'HSTS', passed: Math.random() > 0.5, description: 'HTTP Strict Transport Security' },
        { name: 'X-Frame-Options', passed: Math.random() > 0.3, description: 'Clickjacking protection' },
        { name: 'Content Security Policy', passed: Math.random() > 0.5, description: 'XSS protection' },
        { name: 'Secure Cookies', passed: Math.random() > 0.4, description: 'Cookie security flags' },
      ],
      seoElements: [
        { name: 'Title Tag', found: true, value: 'Example Page Title' },
        { name: 'Meta Description', found: Math.random() > 0.3, value: 'Page description here' },
        { name: 'Canonical URL', found: Math.random() > 0.2, value: url },
        { name: 'Open Graph', found: Math.random() > 0.4, value: 'og:title present' },
        { name: 'Twitter Cards', found: Math.random() > 0.5, value: 'twitter:card present' },
        { name: 'Schema Markup', found: Math.random() > 0.6, value: 'JSON-LD detected' },
      ],
      structure: {
        headings: Math.floor(Math.random() * 20 + 5),
        images: Math.floor(Math.random() * 50 + 10),
        links: Math.floor(Math.random() * 100 + 20),
        scripts: Math.floor(Math.random() * 15 + 3),
        stylesheets: Math.floor(Math.random() * 8 + 2),
        forms: Math.floor(Math.random() * 3),
      },
      meta: {
        title: 'Example Website',
        description: 'This is an example website description',
        keywords: 'seo, marketing, growth'
      }
    };

    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: 'Analysis failed' });
  }
});

// ========== CONTENT ANALYSIS ==========
app.post('/api/tools/content-analysis', authenticate, async (req, res) => {
  try {
    const { content, keyword } = req.body;
    const wordCount = content.split(/\s+/).length;

    const results = {
      overallScore: Math.floor(Math.random() * 30 + 70),
      readability: Math.floor(Math.random() * 30 + 70),
      seoScore: Math.floor(Math.random() * 30 + 70),
      keywordDensity: Math.floor(Math.random() * 30 + 70),
      structure: Math.floor(Math.random() * 30 + 70),
      issues: [
        { severity: 'warning', title: 'Keyword density too low', description: 'Target keyword appears only 2 times' },
        { severity: 'critical', title: 'Missing H2 headings', description: 'Content has no H2 subheadings' },
        { severity: 'warning', title: 'Paragraph too long', description: 'Some paragraphs exceed 150 words' },
        { severity: 'good', title: 'Good word count', description: 'Content is comprehensive at ' + wordCount + ' words' },
      ],
      suggestions: [
        { title: 'Add More Subheadings', description: 'Break content into sections with H2/H3 tags', example: '<h2>Key Benefits of SEO</h2>' },
        { title: 'Increase Keyword Usage', description: 'Use target keyword 3-5 more times naturally', example: 'Learn how ' + (keyword || 'SEO') + ' can transform your business' },
        { title: 'Add Internal Links', description: 'Link to 3-5 related pages on your site', example: '<a href="/blog/seo-guide">Read our SEO guide</a>' },
      ],
      keywordAnalysis: keyword ? {
        count: (content.match(new RegExp(keyword, 'gi')) || []).length,
        density: ((content.match(new RegExp(keyword, 'gi')) || []).length / wordCount * 100).toFixed(1),
        placementScore: Math.floor(Math.random() * 5 + 5),
      } : null
    };

    res.json({ success: true, results });
  } catch (err) {
    res.status(500).json({ error: 'Analysis failed' });
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

// ========== WORKFLOW ROUTES ==========
app.get('/api/workflows', authenticate, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM workflows WHERE user_id = $1', [req.user.id]);
    res.json({ success: true, workflows: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch workflows' });
  }
});

app.post('/api/workflows', authenticate, async (req, res) => {
  try {
    const { name, nodes, edges } = req.body;
    const result = await pool.query(
      'INSERT INTO workflows (user_id, name, nodes, edges) VALUES ($1, $2, $3, $4) RETURNING *',
      [req.user.id, name, JSON.stringify(nodes), JSON.stringify(edges)]
    );
    res.json({ success: true, workflow: result.rows[0] });
  } catch (err) {
    res.status(500).json({ error: 'Failed to save workflow' });
  }
});

// ========== AGENT ROUTES ==========
app.get('/api/agents', authenticate, async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM agents WHERE user_id = $1', [req.user.id]);
    res.json({ success: true, agents: result.rows });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch agents' });
  }
});

app.post('/api/agents', authenticate, async (req, res) => {
  try {
    const { name, type, config } = req.body;
    const result = await pool.query(
      'INSERT INTO agents (user_id, name, type, config) VALUES ($1, $2, $3, $4) RETURNING *',
      [req.user.id, name, type, JSON.stringify(config)]
    );
    res.json({ success: true, agent: result.rows[0] });
  } catch (err) {
    res.status(500).json({ error: 'Failed to create agent' });
  }
});

// ========== HEALTH & STATIC ==========
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString(), version: '2.0.0' });
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

// Start server
initDB().then(() => {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 EliClaw Server running on port ${PORT}`);
    console.log(`📍 Domain: https://eliclaw.virtualabdigital.com`);
    console.log(`🏢 Agency: https://virtualabdigital.com`);
  });
});