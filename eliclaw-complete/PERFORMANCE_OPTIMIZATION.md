# EliClaw Performance Optimization Guide

## Executive Summary

This document outlines comprehensive performance optimizations for the EliClaw platform across frontend, backend, database, and infrastructure layers.

---

## 🎯 Critical Performance Issues Identified

### 1. **Frontend Bundle Size** (~3000 lines of JSX/JS)
- Large component files (Dashboard: 225 lines, SwarmAgent: 274 lines, Settings: 248 lines)
- No code splitting configured beyond route-level
- All chart libraries loaded upfront

### 2. **Database Query Performance**
- Missing database indexes on frequently queried columns
- No query result caching
- Sequential API calls in audit engine

### 3. **SEO Audit Engine** 
- Multiple external API calls without timeout management
- No request debouncing for repeated URL audits
- Synchronous processing of heavy cheerio parsing

### 4. **Server Configuration**
- Basic rate limiting (100 req/15min)
- No response compression
- Static file serving without CDN

---

## 🔧 Frontend Optimizations

### 1. Code Splitting & Lazy Loading

**File:** `client/src/App.jsx`

```jsx
import { lazy, Suspense } from 'react'

// Lazy load heavy pages
const Dashboard = lazy(() => import('./pages/Dashboard'))
const SEOTool = lazy(() => import('./pages/SEOTool'))
const CompetitorTool = lazy(() => import('./pages/CompetitorTool'))
const WebsiteAnalyzer = lazy(() => import('./pages/WebsiteAnalyzer'))
const AutomationTool = lazy(() => import('./pages/AutomationTool'))
const ContentTool = lazy(() => import('./pages/ContentTool'))
const SwarmAgent = lazy(() => import('./pages/SwarmAgent'))
const Leads = lazy(() => import('./pages/Leads'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  const { user } = useAuthStore()
  
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
        
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/tools/seo" element={<SEOTool />} />
          {/* ... other routes */}
        </Route>
      </Routes>
    </Suspense>
  )
}
```

### 2. Optimize Vite Build Configuration

**File:** `client/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true, gzipSize: true }) // Analyze bundle
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable in production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          ui: ['framer-motion', 'lucide-react'],
          auth: ['./context/authStore']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    target: 'esnext'
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion']
  }
})
```

### 3. Component Memoization

**File:** `client/src/pages/Dashboard.jsx`

```jsx
import { memo, useMemo, useCallback } from 'react'

// Memoize stat cards to prevent re-renders
const StatCard = memo(({ stat, i }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: i * 0.1 }}
    className="glass-panel p-5"
  >
    {/* ... content */}
  </motion.div>
))

export default function Dashboard() {
  const { user, token } = useAuthStore()
  const [stats, setStats] = useState({ audits: 0, leads: 0, score: 0, competitors: 0 })
  
  // Memoize chart data
  const chartData = useMemo(() => activityData, [])
  const pieData = useMemo(() => scoreData, [])
  
  // Memoize event handlers
  const fetchDashboardData = useCallback(async () => {
    try {
      const data = await api.get('/dashboard/stats', token)
      if (data.success) setStats(data.stats)
    } catch (err) {
      console.error('Dashboard fetch error:', err)
    }
  }, [token])
  
  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])
  
  return (
    <div className="space-y-6">
      {/* Use memoized components */}
      {statCards.map((stat, i) => (
        <StatCard key={i} stat={stat} i={i} />
      ))}
    </div>
  )
}
```

### 4. Virtual Scrolling for Large Lists

**File:** `client/src/pages/Leads.jsx`

```jsx
import { FixedSizeList as List } from 'react-window'

// Instead of mapping all leads
{leads.map(lead => <LeadCard key={lead.id} lead={lead} />)}

// Use virtual scrolling
<List
  height={600}
  itemCount={leads.length}
  itemSize={100}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>
      <LeadCard lead={leads[index]} />
    </div>
  )}
</List>
```

### 5. Image & Asset Optimization

Add to `client/index.html`:

```html
<link rel="preload" as="image" href="/logo.svg" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="dns-prefetch" href="https://api.eliclaw.virtualabdigital.com" />
```

---

## ⚡ Backend Optimizations

### 1. Database Indexing Strategy

**File:** `server/server-enhanced.js` - Update `initDB()`

```javascript
async function initDB() {
  try {
    await pool.query(`
      -- Existing tables...
      
      -- Add indexes for performance
      CREATE INDEX IF NOT EXISTS idx_audits_user_id ON audits(user_id);
      CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_audits_url ON audits(url);
      
      CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
      CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
      
      CREATE INDEX IF NOT EXISTS idx_usage_logs_user_feature ON usage_logs(user_id, feature);
      CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at DESC);
      
      CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
      CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key);
      
      CREATE INDEX IF NOT EXISTS idx_agents_user_id ON agents(user_id);
      CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
      
      -- Composite indexes for common queries
      CREATE INDEX IF NOT EXISTS idx_audits_user_created ON audits(user_id, created_at DESC);
      CREATE INDEX IF NOT EXISTS idx_leads_user_status ON leads(user_id, status);
    `);
    console.log('Database initialized with indexes');
  } catch (err) {
    console.error('Database init error:', err);
  }
}
```

### 2. Redis Caching Layer

**New File:** `server/cache.js`

```javascript
const Redis = require('ioredis');

class CacheService {
  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
    this.defaultTTL = 3600; // 1 hour
  }

  async get(key) {
    try {
      const data = await this.redis.get(key);
      return data ? JSON.parse(data) : null;
    } catch (err) {
      console.error('Cache get error:', err);
      return null;
    }
  }

  async set(key, value, ttl = this.defaultTTL) {
    try {
      await this.redis.setex(key, ttl, JSON.stringify(value));
    } catch (err) {
      console.error('Cache set error:', err);
    }
  }

  async del(key) {
    try {
      await this.redis.del(key);
    } catch (err) {
      console.error('Cache del error:', err);
    }
  }

  // Cache audit results by URL hash
  async getCachedAudit(url) {
    const key = `audit:${this.hashUrl(url)}`;
    return await this.get(key);
  }

  async cacheAudit(url, results) {
    const key = `audit:${this.hashUrl(url)}`;
    await this.set(key, results, 86400); // 24 hours
  }

  hashUrl(url) {
    const crypto = require('crypto');
    return crypto.createHash('md5').update(url).digest('hex');
  }

  async close() {
    await this.redis.quit();
  }
}

module.exports = new CacheService();
```

**Update:** `server/server-enhanced.js`

```javascript
// Add after imports
const cache = require('./cache');

// In SEO audit endpoint
app.post('/api/tools/seo-audit', freeToolLimiter, async (req, res) => {
  try {
    const { url, email } = req.body;
    if (!url) return res.status(400).json({ error: 'URL required' });

    // Check cache first
    const cachedResults = await cache.getCachedAudit(url);
    if (cachedResults) {
      console.log('Cache hit for:', url);
      return res.json({ success: true, results: cachedResults, cached: true });
    }

    let auditResults;
    if (process.env.PAGESPEED_API_KEY) {
      auditResults = await seoEngine.runFullAudit(url);
    } else {
      auditResults = await runMockAudit(url);
    }

    // Cache results
    await cache.cacheAudit(url, auditResults);

    // Save to database (async, don't wait)
    pool.query(
      `INSERT INTO audits (url, email, ip_address, score, summary, full_report)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [url, email, ip, auditResults.score, JSON.stringify(auditResults.summary), JSON.stringify(auditResults.fullReport)]
    ).catch(err => console.error('Audit save error:', err));

    // Send email (async)
    if (email) {
      emailService.sendAuditReport(email, auditResults).catch(e => 
        console.error('Audit email failed:', e.message)
      );
    }

    res.json({ success: true, results: auditResults });
  } catch (err) {
    console.error('Audit error:', err);
    res.status(500).json({ error: 'Audit failed' });
  }
});
```

### 3. Parallel API Calls with Timeout

**File:** `integrations/seo-audit-engine.js`

```javascript
const axios = require('axios');
const AbortController = require('abort-controller');

class SEOAuditEngine {
  constructor() {
    this.apis = {
      pagespeed: process.env.PAGESPEED_API_KEY,
      ahrefs: process.env.AHREFS_API_KEY,
      semrush: process.env.SEMRUSH_API_KEY,
      moz: process.env.MOZ_API_KEY,
    };
    this.timeout = 10000; // 10 seconds
  }

  async runPageSpeed(url) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const [mobile, desktop] = await Promise.all([
        axios.get(
          `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=MOBILE&key=${this.apis.pagespeed}`,
          { signal: controller.signal }
        ),
        axios.get(
          `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=DESKTOP&key=${this.apis.pagespeed}`,
          { signal: controller.signal }
        )
      ]);

      clearTimeout(timeoutId);
      return {
        mobile: this.parsePageSpeed(mobile.data),
        desktop: this.parsePageSpeed(desktop.data)
      };
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        console.error('PageSpeed timeout');
        return null;
      }
      console.error('PageSpeed error:', err.message);
      return null;
    }
  }

  // Add retry logic with exponential backoff
  async runWithRetry(fn, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
      try {
        return await fn();
      } catch (err) {
        if (i === retries - 1) throw err;
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
}
```

### 4. Response Compression

**File:** `server/server-enhanced.js`

```javascript
const compression = require('compression');

// Add after helmet middleware
app.use(compression({
  level: 6,
  threshold: 1024, // Only compress responses > 1KB
  filter: (req, res) => {
    if (req.headers['x-no-compression']) return false;
    return compression.filter(req, res);
  }
}));
```

### 5. Connection Pooling Optimization

**File:** `server/server-enhanced.js`

```javascript
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
```

### 6. Request Debouncing

**File:** `server/server-enhanced.js`

```javascript
// Add debounce middleware for expensive operations
const debouncedRequests = new Map();

const debounceRequest = (key, ms = 1000) => {
  return (req, res, next) => {
    const identifier = `${key}:${req.body.url || req.ip}`;
    
    if (debouncedRequests.has(identifier)) {
      console.log('Debounced request:', identifier);
      return res.status(429).json({ 
        error: 'Request in progress', 
        retry_after: ms / 1000 
      });
    }

    debouncedRequests.set(identifier, true);
    
    res.on('finish', () => {
      setTimeout(() => debouncedRequests.delete(identifier), ms);
    });

    next();
  };
};

// Apply to SEO audit endpoint
app.post('/api/tools/seo-audit', 
  freeToolLimiter, 
  debounceRequest('seo-audit', 5000),
  async (req, res) => { /* ... */ }
);
```

---

## 🗄️ Database Query Optimizations

### 1. Prepared Statements & Query Optimization

**File:** `server/server-enhanced.js`

```javascript
// Bad: Multiple sequential queries
async function getDashboardStats(userId) {
  const audits = await pool.query('SELECT COUNT(*) FROM audits WHERE user_id = $1', [userId]);
  const leads = await pool.query('SELECT COUNT(*) FROM leads WHERE user_id = $1', [userId]);
  // ...
}

// Good: Single query with multiple counts
async function getDashboardStats(userId) {
  const result = await pool.query(`
    SELECT 
      (SELECT COUNT(*) FROM audits WHERE user_id = $1) as audits,
      (SELECT COUNT(*) FROM leads WHERE user_id = $1) as leads,
      (SELECT AVG(score) FROM audits WHERE user_id = $1) as avg_score,
      (SELECT COUNT(DISTINCT competitor_url) FROM competitor_analysis WHERE user_id = $1) as competitors
    FROM users WHERE id = $1
  `, [userId]);
  
  return result.rows[0];
}
```

### 2. Pagination for Large Datasets

**File:** `server/server-enhanced.js`

```javascript
// Add pagination to leads endpoint
app.get('/api/leads', authenticate, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const offset = (page - 1) * limit;

    const [leads, total] = await Promise.all([
      pool.query(
        'SELECT * FROM leads WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
        [req.user.id, limit, offset]
      ),
      pool.query('SELECT COUNT(*) FROM leads WHERE user_id = $1', [req.user.id])
    ]);

    res.json({
      success: true,
      leads: leads.rows,
      pagination: {
        page,
        limit,
        total: parseInt(total.rows[0].count),
        totalPages: Math.ceil(total.rows[0].count / limit)
      }
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch leads' });
  }
});
```

### 3. Materialized Views for Analytics

```sql
-- Create materialized view for dashboard stats
CREATE MATERIALIZED VIEW IF NOT EXISTS user_dashboard_stats AS
SELECT 
  u.id as user_id,
  COUNT(DISTINCT a.id) as total_audits,
  COUNT(DISTINCT l.id) as total_leads,
  AVG(a.score) as avg_seo_score,
  COUNT(DISTINCT ca.id) as total_competitors,
  MAX(a.created_at) as last_audit_date
FROM users u
LEFT JOIN audits a ON u.id = a.user_id
LEFT JOIN leads l ON u.id = l.user_id
LEFT JOIN competitor_analysis ca ON u.id = ca.user_id
GROUP BY u.id;

-- Refresh periodically
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY user_dashboard_stats;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh every hour
SELECT cron.schedule('refresh-stats', '0 * * * *', 'SELECT refresh_dashboard_stats()');
```

---

## 🌐 Infrastructure Optimizations

### 1. Nginx Configuration

**File:** `server/nginx.conf`

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
        
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Client body size limit
    client_max_body_size 10M;

    # Keepalive
    keepalive_timeout 65;
    keepalive_requests 100;
}
```

### 2. PM2 Cluster Mode

**File:** `server/ecosystem.config.js`

```javascript
module.exports = {
  apps: [{
    name: 'eliclaw-api',
    script: 'server-enhanced.js',
    instances: 'max', // Use all CPU cores
    exec_mode: 'cluster',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
```

### 3. CDN Integration

For static assets, configure Cloudflare or similar:

```javascript
// vite.config.js - Add CDN URL
build: {
  outDir: 'dist',
  assetsDir: 'static',
  rollupOptions: {
    output: {
      assetFileNames: 'static/[name].[hash][extname]'
    }
  }
}

// In production, serve from CDN
const CDN_URL = process.env.CDN_URL || '';
<img src={`${CDN_URL}/static/logo.${hash}.svg`} />
```

---

## 📊 Monitoring & Profiling

### 1. Application Performance Monitoring

Install APM tool:

```bash
npm install @elastic/apm-rpm
```

**File:** `server/server-enhanced.js`

```javascript
const apm = require('elastic-apm-node').start({
  serviceName: 'eliclaw-api',
  serverUrl: process.env.ELASTIC_APM_SERVER_URL,
  captureBody: 'errors',
  captureHeaders: true
});
```

### 2. Custom Metrics

**File:** `server/metrics.js`

```javascript
const client = require('prom-client');

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const auditCounter = new client.Counter({
  name: 'seo_audits_total',
  help: 'Total number of SEO audits performed',
  labelNames: ['source']
});

module.exports = { httpRequestDuration, auditCounter };
```

### 3. Bundle Analysis

```bash
# Install visualizer
npm install rollup-plugin-visualizer --save-dev

# Run build and analyze
npm run build
# Opens interactive treemap showing bundle composition
```

---

## 🎯 Quick Wins Checklist

- [ ] Enable gzip compression in Express
- [ ] Add database indexes on foreign keys
- [ ] Implement Redis caching for audit results
- [ ] Lazy load React routes
- [ ] Configure Vite code splitting
- [ ] Add connection pooling limits
- [ ] Implement request debouncing
- [ ] Enable PM2 cluster mode
- [ ] Add Nginx rate limiting
- [ ] Optimize images and assets
- [ ] Use CDN for static files
- [ ] Add query result pagination
- [ ] Profile slow endpoints with APM

---

## 📈 Expected Performance Improvements

| Optimization | Expected Impact |
|-------------|----------------|
| Redis Caching | 80-90% reduction in audit API latency |
| Database Indexes | 10-100x faster queries |
| Code Splitting | 40-60% smaller initial bundle |
| Gzip Compression | 60-70% smaller responses |
| PM2 Clustering | 4-8x throughput increase |
| CDN Assets | 50-80% faster asset loading |
| Connection Pooling | 2-3x DB query throughput |

---

## 🔍 Testing & Validation

```bash
# Lighthouse performance audit
npx lighthouse https://eliclaw.virtualabdigital.com --view

# Load testing
npm install -g artillery
artillery quick --count 10 --num 100 https://api.eliclaw.virtualabdigital.com/api/health

# Bundle analysis
npm run build -- --visualize

# Database query profiling
EXPLAIN ANALYZE SELECT * FROM audits WHERE user_id = 1 ORDER BY created_at DESC LIMIT 20;
```

---

Built with ❤️ by Virtualab Digital
