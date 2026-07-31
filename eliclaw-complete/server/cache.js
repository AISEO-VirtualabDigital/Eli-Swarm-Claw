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

  // Cache user dashboard stats
  async getUserDashboardStats(userId) {
    const key = `dashboard:${userId}`;
    return await this.get(key);
  }

  async cacheUserDashboardStats(userId, stats) {
    const key = `dashboard:${userId}`;
    await this.set(key, stats, 300); // 5 minutes
  }

  // Invalidate user cache on important actions
  async invalidateUserCache(userId) {
    const pattern = `dashboard:${userId}`;
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  hashUrl(url) {
    const crypto = require('crypto');
    return crypto.createHash('md5').update(url).digest('hex');
  }

  async close() {
    await this.redis.quit();
  }

  // Health check
  async health() {
    try {
      await this.redis.ping();
      return { status: 'healthy', service: 'redis' };
    } catch (err) {
      return { status: 'unhealthy', service: 'redis', error: err.message };
    }
  }
}

module.exports = new CacheService();
