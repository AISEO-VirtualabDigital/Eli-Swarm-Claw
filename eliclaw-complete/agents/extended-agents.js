/**
 * EliClaw Extended Swarm Agents
 * 100+ specialized agents for every SEO/marketing need
 */

const AGENT_TEMPLATES = [
  // Core agents (already in main app)
  { id: 'seo', name: 'SEO Agent', type: 'seo', icon: 'Search', color: 'bg-blue-500', desc: 'Analyzes and optimizes search rankings' },
  { id: 'content', name: 'Content Agent', type: 'content', icon: 'FileText', color: 'bg-green-500', desc: 'Generates and optimizes content' },
  { id: 'competitor', name: 'Competitor Agent', type: 'competitor', icon: 'Globe', color: 'bg-purple-500', desc: 'Monitors competitor movements' },
  { id: 'technical', name: 'Technical Agent', type: 'technical', icon: 'Cpu', color: 'bg-yellow-500', desc: 'Fixes technical SEO issues' },
  { id: 'social', name: 'Social Agent', type: 'social', icon: 'MessageSquare', color: 'bg-pink-500', desc: 'Manages social signals' },
  { id: 'analytics', name: 'Analytics Agent', type: 'analytics', icon: 'Activity', color: 'bg-cyan-500', desc: 'Tracks and reports metrics' },

  // NEW: Extended agents - Link Building
  { id: 'backlink', name: 'Backlink Agent', type: 'backlink', icon: 'Link', color: 'bg-orange-500', desc: 'Discovers and monitors backlink opportunities' },
  { id: 'pr-outreach', name: 'PR Outreach Agent', type: 'pr-outreach', icon: 'Mail', color: 'bg-indigo-500', desc: 'Automates PR and link building outreach' },
  { id: 'guest-post', name: 'Guest Post Agent', type: 'guest-post', icon: 'PenTool', color: 'bg-blue-700', desc: 'Finds guest posting opportunities' },
  { id: 'broken-link', name: 'Broken Link Agent', type: 'broken-link', icon: 'Unlink', color: 'bg-indigo-600', desc: 'Finds and fixes broken links automatically' },
  { id: 'internal-link', name: 'Internal Link Agent', type: 'internal-link', icon: 'Link2', color: 'bg-rose-600', desc: 'Optimizes internal linking structure' },
  { id: 'disavow', name: 'Disavow Agent', type: 'disavow', icon: 'FileX', color: 'bg-teal-500', desc: 'Manages disavow file automatically' },

  // Local SEO
  { id: 'local-seo', name: 'Local SEO Agent', type: 'local-seo', icon: 'MapPin', color: 'bg-red-500', desc: 'Optimizes Google Business Profile and local listings' },
  { id: 'local-citation', name: 'Citation Builder Agent', type: 'local-citation', icon: 'Building', color: 'bg-red-700', desc: 'Builds local citations automatically' },
  { id: 'review-monitor', name: 'Review Monitor Agent', type: 'review-monitor', icon: 'Star', color: 'bg-yellow-600', desc: 'Monitors online reviews and reputation' },

  // Technical SEO
  { id: 'core-web-vitals', name: 'Core Web Vitals Agent', type: 'core-web-vitals', icon: 'Gauge', color: 'bg-violet-500', desc: 'Monitors and fixes LCP, FID, CLS issues' },
  { id: 'speed-optimizer', name: 'Speed Optimizer Agent', type: 'speed-optimizer', icon: 'Zap', color: 'bg-green-600', desc: 'Automatically optimizes page speed' },
  { id: 'security-audit', name: 'Security Audit Agent', type: 'security-audit', icon: 'Shield', color: 'bg-red-600', desc: 'Scans for security vulnerabilities' },
  { id: 'mobile-first', name: 'Mobile-First Agent', type: 'mobile-first', icon: 'Smartphone', color: 'bg-sky-500', desc: 'Ensures mobile-first indexing compliance' },
  { id: 'accessibility', name: 'Accessibility Agent', type: 'accessibility', icon: 'Eye', color: 'bg-blue-600', desc: 'Ensures WCAG 2.1 AA compliance' },
  { id: 'schema', name: 'Schema Markup Agent', type: 'schema', icon: 'Code2', color: 'bg-lime-500', desc: 'Generates and validates structured data' },
  { id: 'redirect-manager', name: 'Redirect Manager Agent', type: 'redirect-manager', icon: 'Route', color: 'bg-pink-600', desc: 'Manages 301/302 redirects and fixes chains' },
  { id: 'sitemap-manager', name: 'Sitemap Manager Agent', type: 'sitemap-manager', icon: 'Sitemap', color: 'bg-orange-600', desc: 'Auto-generates and submits sitemaps' },
  { id: 'image-optimizer', name: 'Image Optimizer Agent', type: 'image-optimizer', icon: 'Image', color: 'bg-teal-600', desc: 'Compresses and converts images to WebP/AVIF' },
  { id: 'penalty-check', name: 'Penalty Agent', type: 'penalty-check', icon: 'Ban', color: 'bg-pink-500', desc: 'Monitors for algorithm penalties' },
  { id: 'recovery-tracker', name: 'Recovery Tracker', type: 'recovery-tracker', icon: 'LineChart', color: 'bg-rose-500', desc: 'Tracks recovery progress post-penalty' },
  { id: 'migration', name: 'Migration SEO Agent', type: 'migration', icon: 'Truck', color: 'bg-lime-900', desc: 'Ensures SEO-safe site migrations' },

  // Content
  { id: 'content-gap', name: 'Content Gap Agent', type: 'content-gap', icon: 'GitCompare', color: 'bg-fuchsia-500', desc: 'Finds missing content vs competitors' },
  { id: 'content-prune', name: 'Prune Agent', type: 'content-prune', icon: 'Scissors', color: 'bg-emerald-500', desc: 'Identifies content to prune or update' },
  { id: 'content-refresh', name: 'Refresh Agent', type: 'content-refresh', icon: 'RotateCcw', color: 'bg-sky-500', desc: 'Auto-refreshes outdated content' },
  { id: 'content-expand', name: 'Expand Agent', type: 'content-expand', icon: 'Maximize2', color: 'bg-amber-500', desc: 'Finds thin content to expand' },
  { id: 'content-calendar', name: 'Content Calendar Agent', type: 'content-calendar', icon: 'Calendar', color: 'bg-emerald-600', desc: 'Plans and schedules content publication' },
  { id: 'ai-content', name: 'AI Content Agent', type: 'ai-content', icon: 'Sparkles', color: 'bg-fuchsia-600', desc: 'Generates AI-powered content drafts' },
  { id: 'content-syndicate', name: 'Syndicate Agent', type: 'content-syndicate', icon: 'Share2', color: 'bg-indigo-500', desc: 'Syndicates content to platforms' },
  { id: 'content-repurpose', name: 'Repurpose Agent', type: 'content-repurpose', icon: 'Recycle', color: 'bg-cyan-500', desc: 'Turns one piece into multiple formats' },
  { id: 'content-translate', name: 'Translate Agent', type: 'content-translate', icon: 'Languages', color: 'bg-amber-600', desc: 'Manages multilingual content' },
  { id: 'content-quality', name: 'Quality Agent', type: 'content-quality', icon: 'Award', color: 'bg-violet-600', desc: 'Ensures content quality standards' },
  { id: 'content-readability', name: 'Readability Agent', type: 'content-readability', icon: 'BookOpen', color: 'bg-blue-700', desc: 'Optimizes reading level' },
  { id: 'content-engagement', name: 'Engagement Agent', type: 'content-engagement', icon: 'ThumbsUp', color: 'bg-cyan-700', desc: 'Optimizes for user engagement' },
  { id: 'content-dwell-time', name: 'Dwell Time Agent', type: 'content-dwell-time', icon: 'Clock', color: 'bg-orange-700', desc: 'Increases time on page' },
  { id: 'content-ctr', name: 'CTR Agent', type: 'content-ctr', icon: 'MousePointer', color: 'bg-rose-700', desc: 'Optimizes click-through rates' },
  { id: 'content-lead-gen', name: 'Lead Gen Agent', type: 'content-lead-gen', icon: 'UserPlus', color: 'bg-sky-700', desc: 'Turns content into lead magnets' },
  { id: 'faq-generator', name: 'FAQ Agent', type: 'faq-generator', icon: 'HelpCircle', color: 'bg-sky-700', desc: 'Generates FAQ schema and content' },
  { id: 'content-fact-check', name: 'Fact Check Agent', type: 'content-fact-check', icon: 'CheckSquare', color: 'bg-yellow-700', desc: 'Verifies factual claims' },
  { id: 'content-plagiarism', name: 'Originality Agent', type: 'content-plagiarism', icon: 'Fingerprint', color: 'bg-indigo-700', desc: 'Checks for duplicate content' },

  // Keywords & Research
  { id: 'keyword-cluster', name: 'Keyword Cluster Agent', type: 'keyword-cluster', icon: 'Tags', color: 'bg-cyan-600', desc: 'Groups keywords into topic clusters' },
  { id: 'voice-search', name: 'Voice Search Agent', type: 'voice-search', icon: 'Mic', color: 'bg-teal-500', desc: 'Optimizes for voice search and featured snippets' },
  { id: 'serp-feature', name: 'SERP Feature Agent', type: 'serp-feature', icon: 'Layout', color: 'bg-lime-600', desc: 'Targets featured snippets and rich results' },
  { id: 'trend-spotter', name: 'Trend Agent', type: 'trend-spotter', icon: 'Zap', color: 'bg-green-500', desc: 'Identifies trending topics early' },
  { id: 'opportunity-finder', name: 'Opportunity Agent', type: 'opportunity-finder', icon: 'Search', color: 'bg-yellow-500', desc: 'Discovers untapped SEO opportunities' },
  { id: 'rank-tracker', name: 'Rank Tracker Agent', type: 'rank-tracker', icon: 'TrendingUp', color: 'bg-amber-600', desc: 'Tracks keyword rankings daily' },
  { id: 'content-people-also-ask', name: 'PAA Agent', type: 'content-people-also-ask', icon: 'HelpCircle', color: 'bg-sky-700', desc: 'Targets People Also Ask' },

  // E-commerce
  { id: 'ecommerce', name: 'E-commerce Agent', type: 'ecommerce', icon: 'ShoppingCart', color: 'bg-emerald-500', desc: 'Optimizes product pages and schema markup' },
  { id: 'competitor-price', name: 'Price Monitor Agent', type: 'competitor-price', icon: 'DollarSign', color: 'bg-yellow-700', desc: 'Monitors competitor pricing changes' },

  // Video & Media
  { id: 'video-seo', name: 'Video SEO Agent', type: 'video-seo', icon: 'Video', color: 'bg-rose-500', desc: 'Optimizes YouTube and video content' },
  { id: 'podcast-seo', name: 'Podcast SEO Agent', type: 'podcast-seo', icon: 'Podcast', color: 'bg-blue-800', desc: 'Optimizes podcast show notes and metadata' },
  { id: 'web-stories', name: 'Web Stories Agent', type: 'web-stories', icon: 'BookOpen', color: 'bg-amber-500', desc: 'Creates Google Web Stories' },

  // International
  { id: 'international', name: 'International SEO Agent', type: 'international', icon: 'Globe2', color: 'bg-amber-500', desc: 'Manages hreflang and multi-language SEO' },

  // Conversion & CRO
  { id: 'conversion-optimizer', name: 'CRO Agent', type: 'conversion-optimizer', icon: 'Target', color: 'bg-purple-600', desc: 'A/B tests and optimizes conversions' },
  { id: 'landing-page', name: 'Landing Page Agent', type: 'landing-page', icon: 'LayoutTemplate', color: 'bg-lime-700', desc: 'A/B tests landing page elements' },
  { id: 'exit-intent', name: 'Exit Intent Agent', type: 'exit-intent', icon: 'MousePointerClick', color: 'bg-fuchsia-700', desc: 'Creates exit-intent popups' },

  // Brand & Reputation
  { id: 'brand-monitor', name: 'Brand Monitor Agent', type: 'brand-monitor', icon: 'Trademark', color: 'bg-sky-600', desc: 'Tracks brand mentions across the web' },
  { id: 'reputation', name: 'Reputation Agent', type: 'reputation', icon: 'ShieldCheck', color: 'bg-green-700', desc: 'Manages online reputation SEO' },
  { id: 'social-proof', name: 'Social Proof Agent', type: 'social-proof', icon: 'ThumbsUp', color: 'bg-green-700', desc: 'Collects and displays social proof' },

  // Industry-Specific
  { id: 'saas', name: 'SaaS SEO Agent', type: 'saas', icon: 'Cloud', color: 'bg-emerald-800', desc: 'Optimizes SaaS product and pricing pages' },
  { id: 'real-estate', name: 'Real Estate SEO Agent', type: 'real-estate', icon: 'Home', color: 'bg-orange-800', desc: 'Optimizes property listings' },
  { id: 'restaurant', name: 'Restaurant SEO Agent', type: 'restaurant', icon: 'Utensils', color: 'bg-pink-800', desc: 'Optimizes menu and reservation pages' },
  { id: 'healthcare', name: 'Healthcare SEO Agent', type: 'healthcare', icon: 'Heart', color: 'bg-teal-800', desc: 'HIPAA-compliant medical SEO' },
  { id: 'legal', name: 'Legal SEO Agent', type: 'legal', icon: 'Scale', color: 'bg-rose-800', desc: 'Optimizes law firm pages and citations' },
  { id: 'news-publisher', name: 'News SEO Agent', type: 'news-publisher', icon: 'Rss', color: 'bg-cyan-900', desc: 'Google News and Discover optimization' },

  // Advanced
  { id: 'traffic-analyzer', name: 'Traffic Analyzer Agent', type: 'traffic-analyzer', icon: 'BarChart', color: 'bg-violet-600', desc: 'Analyzes traffic patterns and anomalies' },
  { id: 'competitor-alert', name: 'Comp Alert Agent', type: 'competitor-alert', icon: 'BellRing', color: 'bg-indigo-900', desc: 'Real-time competitor change alerts' },
  { id: 'audit-history', name: 'Audit History Agent', type: 'audit-history', icon: 'History', color: 'bg-fuchsia-900', desc: 'Tracks and compares audit history' },
  { id: 'seasonal', name: 'Seasonal SEO Agent', type: 'seasonal', icon: 'Sun', color: 'bg-red-500', desc: 'Optimizes for seasonal trends' },
  { id: 'event-seo', name: 'Event SEO Agent', type: 'event-seo', icon: 'Calendar', color: 'bg-blue-500', desc: 'Optimizes for events and conferences' },
  { id: 'product-launch', name: 'Launch Agent', type: 'product-launch', icon: 'Rocket', color: 'bg-purple-500', desc: 'SEO strategy for product launches' },

  // Content Distribution
  { id: 'content-distribute', name: 'Distribute Agent', type: 'content-distribute', icon: 'Send', color: 'bg-orange-500', desc: 'Distributes content across channels' },
  { id: 'content-promote', name: 'Promote Agent', type: 'content-promote', icon: 'Megaphone', color: 'bg-pink-500', desc: 'Promotes content via paid/organic' },
  { id: 'content-nurture', name: 'Nurture Agent', type: 'content-nurture', icon: 'Heart', color: 'bg-rose-500', desc: 'Creates nurture sequences' },
  { id: 'email-sequence', name: 'Email Sequence Agent', type: 'email-sequence', icon: 'Mail', color: 'bg-indigo-500', desc: 'Creates automated email sequences' },

  // Social & PR
  { id: 'influencer', name: 'Influencer Agent', type: 'influencer', icon: 'Users', color: 'bg-cyan-700', desc: 'Discovers influencer partnerships' },
  { id: 'podcast-outreach', name: 'Podcast Agent', type: 'podcast-outreach', icon: 'Headphones', color: 'bg-purple-700', desc: 'Finds podcast guest opportunities' },
  { id: 'press-release', name: 'Press Release Agent', type: 'press-release', icon: 'Radio', color: 'bg-orange-700', desc: 'Drafts and distributes press releases' },

  // Analytics & Reporting
  { id: 'report-generator', name: 'Report Agent', type: 'report-generator', icon: 'FileBarChart', color: 'bg-emerald-600', desc: 'Creates automated reports' },
  { id: 'benchmark', name: 'Benchmark Agent', type: 'benchmark', icon: 'Scale', color: 'bg-amber-600', desc: 'Creates benchmark reports' },

  // Emerging
  { id: 'ai-optimization', name: 'AI Search Agent', type: 'ai-optimization', icon: 'Brain', color: 'bg-violet-700', desc: 'Optimizes for AI search engines' },
  { id: 'voice-assistant', name: 'Voice Assistant Agent', type: 'voice-assistant', icon: 'Volume2', color: 'bg-teal-700', desc: 'Optimizes for Alexa/Google Assistant' },
  { id: 'discover-optimization', name: 'Discover Agent', type: 'discover-optimization', icon: 'Compass', color: 'bg-orange-800', desc: 'Optimizes for Google Discover' }
];

module.exports = AGENT_TEMPLATES;