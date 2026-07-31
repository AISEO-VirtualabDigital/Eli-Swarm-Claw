/**
 * EliClaw SEO Integrations
 * Supports: PageSpeed Insights, Ahrefs, SEMrush, Screaming Frog (mock), Moz
 */

const axios = require('axios');

class SEOAuditEngine {
  constructor() {
    this.apis = {
      pagespeed: process.env.PAGESPEED_API_KEY,
      ahrefs: process.env.AHREFS_API_KEY,
      semrush: process.env.SEMRUSH_API_KEY,
      moz: process.env.MOZ_API_KEY,
    };
  }

  // Google PageSpeed Insights (Free tier: 25,000 queries/day)
  async runPageSpeed(url) {
    try {
      const [mobile, desktop] = await Promise.all([
        axios.get(`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=MOBILE&key=${this.apis.pagespeed}`),
        axios.get(`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=DESKTOP&key=${this.apis.pagespeed}`)
      ]);

      return {
        mobile: this.parsePageSpeed(mobile.data),
        desktop: this.parsePageSpeed(desktop.data)
      };
    } catch (err) {
      console.error('PageSpeed error:', err.message);
      return null;
    }
  }

  parsePageSpeed(data) {
    const lighthouse = data.lighthouseResult;
    const categories = lighthouse.categories;

    return {
      score: Math.round(categories.performance.score * 100),
      firstContentfulPaint: lighthouse.audits['first-contentful-paint'].displayValue,
      largestContentfulPaint: lighthouse.audits['largest-contentful-paint'].displayValue,
      timeToInteractive: lighthouse.audits['interactive'].displayValue,
      cumulativeLayoutShift: lighthouse.audits['cumulative-layout-shift'].displayValue,
      totalBlockingTime: lighthouse.audits['total-blocking-time'].displayValue,
      opportunities: lighthouse.audits['opportunities']?.details?.items?.map(item => ({
        title: item.result?.title || 'Optimization',
        savings: item.result?.displayValue || '0 ms'
      })) || []
    };
  }

  // Ahrefs API (Paid - backlink & keyword data)
  async runAhrefsAudit(url) {
    if (!this.apis.ahrefs) return null;
    try {
      const domain = new URL(url).hostname;
      const [backlinks, keywords, organicTraffic] = await Promise.all([
        axios.get(`https://apiv2.ahrefs.com?from=backlinks&target=${domain}&mode=domain&limit=10&token=${this.apis.ahrefs}`),
        axios.get(`https://apiv2.ahrefs.com?from=keywords&target=${domain}&mode=domain&limit=10&token=${this.apis.ahrefs}`),
        axios.get(`https://apiv2.ahrefs.com?from=organic&target=${domain}&mode=domain&token=${this.apis.ahrefs}`)
      ]);

      return {
        domainRating: backlinks.data.domain_rating?.value || 0,
        backlinks: backlinks.data.backlinks?.value || 0,
        referringDomains: backlinks.data.refdomains?.value || 0,
        organicKeywords: keywords.data.keywords?.value || 0,
        organicTraffic: organicTraffic.data.organic?.value || 0,
        topKeywords: keywords.data.keywords?.data?.slice(0, 10) || []
      };
    } catch (err) {
      console.error('Ahrefs error:', err.message);
      return null;
    }
  }

  // SEMrush API (Paid - competitor & keyword data)
  async runSEMrushAudit(url) {
    if (!this.apis.semrush) return null;
    try {
      const domain = new URL(url).hostname;
      const response = await axios.get(`https://api.semrush.com/?type=domain_ranks&domain=${domain}&database=us&key=${this.apis.semrush}`);

      return {
        rank: response.data?.rank || 0,
        organicKeywords: response.data?.organic_keywords || 0,
        organicTraffic: response.data?.organic_traffic || 0,
        paidKeywords: response.data?.paid_keywords || 0,
        paidTraffic: response.data?.paid_traffic || 0
      };
    } catch (err) {
      console.error('SEMrush error:', err.message);
      return null;
    }
  }

  // Moz API (Paid - domain authority)
  async runMozAudit(url) {
    if (!this.apis.moz) return null;
    try {
      const domain = new URL(url).hostname;
      const response = await axios.get(`https://lsapi.seomoz.com/v2/url_metrics?targets=${encodeURIComponent(domain)}`, {
        headers: { 'Authorization': `Bearer ${this.apis.moz}` }
      });

      return {
        domainAuthority: response.data?.results?.[0]?.domain_authority || 0,
        pageAuthority: response.data?.results?.[0]?.page_authority || 0,
        linkingRootDomains: response.data?.results?.[0]?.root_domains_to_page || 0,
        totalLinks: response.data?.results?.[0]?.external_links || 0
      };
    } catch (err) {
      console.error('Moz error:', err.message);
      return null;
    }
  }

  // Unified audit runner
  async runFullAudit(url) {
    console.log(`Running full SEO audit for: ${url}`);

    const [pageSpeed, ahrefs, semrush, moz] = await Promise.all([
      this.runPageSpeed(url),
      this.runAhrefsAudit(url),
      this.runSEMrushAudit(url),
      this.runMozAudit(url)
    ]);

    // Combine all data into comprehensive report
    const combinedScore = this.calculateCombinedScore({ pageSpeed, ahrefs, semrush, moz });

    return {
      url,
      score: combinedScore,
      timestamp: new Date().toISOString(),
      pageSpeed,
      ahrefs,
      semrush,
      moz,
      issues: this.generateIssues({ pageSpeed, ahrefs, semrush, moz }),
      recommendations: this.generateRecommendations({ pageSpeed, ahrefs, semrush, moz })
    };
  }

  calculateCombinedScore(data) {
    let score = 50; // Base score

    if (data.pageSpeed) {
      score += (data.pageSpeed.mobile?.score || 0) * 0.15;
      score += (data.pageSpeed.desktop?.score || 0) * 0.15;
    }

    if (data.ahrefs) {
      score += Math.min(data.ahrefs.domainRating / 100 * 10, 10);
    }

    if (data.moz) {
      score += Math.min(data.moz.domainAuthority / 100 * 10, 10);
    }

    return Math.round(Math.min(100, Math.max(0, score)));
  }

  generateIssues(data) {
    const issues = [];

    if (data.pageSpeed?.mobile?.score < 50) {
      issues.push({
        severity: 'critical',
        category: 'performance',
        title: 'Poor Mobile Performance',
        description: `Mobile score is ${data.pageSpeed.mobile.score}/100`,
        recommendation: 'Optimize images, reduce JavaScript, enable lazy loading'
      });
    }

    if (data.ahrefs?.domainRating < 30) {
      issues.push({
        severity: 'warning',
        category: 'authority',
        title: 'Low Domain Rating',
        description: `DR is ${data.ahrefs.domainRating}/100`,
        recommendation: 'Build high-quality backlinks from authoritative sites'
      });
    }

    if (data.moz?.domainAuthority < 30) {
      issues.push({
        severity: 'warning',
        category: 'authority',
        title: 'Low Domain Authority',
        description: `DA is ${data.moz.domainAuthority}/100`,
        recommendation: 'Improve content quality and earn natural backlinks'
      });
    }

    return issues;
  }

  generateRecommendations(data) {
    const recs = [];

    if (data.pageSpeed?.mobile?.opportunities?.length > 0) {
      recs.push(...data.pageSpeed.mobile.opportunities.slice(0, 3).map(opp => ({
        priority: 'high',
        title: opp.title,
        impact: opp.savings
      })));
    }

    if (data.ahrefs?.backlinks < 100) {
      recs.push({
        priority: 'high',
        title: 'Build Backlinks',
        impact: 'High authority boost'
      });
    }

    return recs;
  }
}

module.exports = SEOAuditEngine;