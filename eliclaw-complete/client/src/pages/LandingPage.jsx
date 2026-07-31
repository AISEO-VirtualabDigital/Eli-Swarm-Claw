import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Search, Users, Globe, Zap, FileText, Bot, ArrowRight, 
  Check, Star, TrendingUp, Shield, Clock, BarChart3
} from 'lucide-react'

const tools = [
  { icon: Search, title: 'SEO Audit', desc: 'Deep website analysis with actionable recommendations', color: 'from-blue-500 to-cyan-400' },
  { icon: Users, title: 'Competitor Analysis', desc: 'Track competitors and find growth opportunities', color: 'from-purple-500 to-pink-400' },
  { icon: Globe, title: 'Website Analyzer', desc: 'Performance, security & technical deep-dive', color: 'from-green-500 to-emerald-400' },
  { icon: Zap, title: 'Automation', desc: 'Build workflows that run while you sleep', color: 'from-yellow-500 to-orange-400' },
  { icon: FileText, title: 'Content Analysis', desc: 'AI-powered content quality & SEO scoring', color: 'from-red-500 to-rose-400' },
  { icon: Bot, title: 'Swarm Agent', desc: 'Multi-agent AI coordination for complex tasks', color: 'from-indigo-500 to-violet-400' },
]

const stats = [
  { value: '50K+', label: 'Audits Run' },
  { value: '12K+', label: 'Active Users' },
  { value: '99.9%', label: 'Uptime' },
  { value: '4.9★', label: 'Rating' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark-900">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-dark-900/80 backdrop-blur-xl border-b border-dark-700/30">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">E</span>
            </div>
            <span className="text-2xl font-bold gradient-text">EliClaw</span>
          </Link>
          <div className="hidden md:flex items-center gap-8">
            <a href="#tools" className="text-dark-400 hover:text-white transition-colors">Tools</a>
            <a href="#features" className="text-dark-400 hover:text-white transition-colors">Features</a>
            <a href="https://virtualabdigital.com" target="_blank" className="text-dark-400 hover:text-white transition-colors">Agency</a>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-dark-400 hover:text-white transition-colors font-medium">Sign In</Link>
            <Link to="/register" className="btn-primary">Get Started Free</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/20 rounded-full text-primary-400 text-sm font-medium mb-8">
              <Star size={14} fill="currentColor" />
              New: Swarm Agent 2.0 is live
            </div>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              All-in-One AI Platform for
              <span className="gradient-text block mt-2">Digital Growth</span>
            </h1>
            <p className="text-xl text-dark-400 max-w-2xl mx-auto mb-10">
              SEO audits, competitor tracking, automation workflows, and multi-agent AI — 
              all in one powerful dashboard. Built by <a href="https://virtualabdigital.com" target="_blank" className="text-primary-400 hover:underline">Virtualab Digital</a>.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register" className="btn-primary text-lg px-8 py-4 flex items-center gap-2">
                Start Free Audit <ArrowRight size={20} />
              </Link>
              <Link to="/tools/seo" className="btn-secondary text-lg px-8 py-4">
                Try Without Account
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            {stats.map((stat, i) => (
              <div key={i} className="glass-panel p-4 text-center">
                <div className="text-2xl font-bold gradient-text">{stat.value}</div>
                <div className="text-sm text-dark-500">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Tools Grid */}
      <section id="tools" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Every Tool You Need</h2>
            <p className="text-dark-400 text-lg max-w-2xl mx-auto">
              Six powerful tools working together. No more switching between apps.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tools.map((tool, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Link to={i === 0 ? '/tools/seo' : '/register'}>
                  <div className="glass-panel p-6 card-hover h-full">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tool.color} flex items-center justify-center mb-4`}>
                      <tool.icon size={24} className="text-white" />
                    </div>
                    <h3 className="text-xl font-bold mb-2">{tool.title}</h3>
                    <p className="text-dark-400">{tool.desc}</p>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Built for <span className="gradient-text">Serious Growth</span>
              </h2>
              <div className="space-y-4">
                {[
                  { icon: TrendingUp, text: 'Real-time SEO scoring with 200+ checkpoints' },
                  { icon: Shield, text: 'Enterprise-grade security & data privacy' },
                  { icon: Clock, text: 'Automated daily monitoring & alerts' },
                  { icon: BarChart3, text: 'White-label reports for clients' },
                ].map((feature, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center flex-shrink-0">
                      <feature.icon size={20} className="text-primary-400" />
                    </div>
                    <span className="text-lg">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="glass-panel p-8 rounded-2xl">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span>Swarm Agent Active</span>
                  </div>
                  <span className="text-green-400 text-sm">6 agents running</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <span>SEO Monitor</span>
                  </div>
                  <span className="text-blue-400 text-sm">247 sites tracked</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-dark-700/50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
                    <span>Automation Engine</span>
                  </div>
                  <span className="text-purple-400 text-sm">12 workflows active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center glass-panel p-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Grow?</h2>
          <p className="text-dark-400 text-lg mb-8">
            Join 12,000+ marketers and agencies using EliClaw to dominate search rankings.
          </p>
          <Link to="/register" className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-2">
            Create Free Account <ArrowRight size={20} />
          </Link>
          <p className="text-sm text-dark-500 mt-4">No credit card required. Free plan includes 3 audits/month.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-700/50 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">E</span>
            </div>
            <span className="font-bold text-lg">EliClaw</span>
            <span className="text-dark-500 text-sm">by Virtualab Digital</span>
          </div>
          <div className="flex items-center gap-6 text-dark-400">
            <a href="https://virtualabdigital.com" target="_blank" className="hover:text-white transition-colors">Agency</a>
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
          <p className="text-dark-500 text-sm">© 2026 EliClaw by Virtualab Digital. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}