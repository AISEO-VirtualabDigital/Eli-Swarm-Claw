import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import toast from 'react-hot-toast'
import {
  Search, Globe, AlertTriangle, CheckCircle, XCircle, ArrowRight,
  Clock, TrendingUp, Shield, Smartphone, Zap, Loader2
} from 'lucide-react'

const issueCategories = [
  { id: 'meta', label: 'Meta Tags', icon: Globe },
  { id: 'performance', label: 'Performance', icon: Zap },
  { id: 'mobile', label: 'Mobile', icon: Smartphone },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'content', label: 'Content', icon: TrendingUp },
]

export default function SEOTool() {
  const [url, setUrl] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [activeCategory, setActiveCategory] = useState('all')
  const { token } = useAuthStore()

  const handleAudit = async (e) => {
    e.preventDefault()
    if (!url) {
      toast.error('Please enter a URL')
      return
    }

    setLoading(true)
    try {
      const data = await api.post('/tools/seo-audit', { url, email }, token)
      if (data.success) {
        setResults(data.results)
        toast.success('Audit complete!')
      } else {
        toast.error(data.error || 'Audit failed')
      }
    } catch (err) {
      toast.error('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBg = (score) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">SEO Audit Tool</h1>
        <p className="text-dark-400">Analyze any website for SEO issues, performance, and optimization opportunities.</p>
      </motion.div>

      {/* Input Form */}
      <div className="glass-panel p-6">
        <form onSubmit={handleAudit} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="input-field"
              required
            />
          </div>
          <div className="md:w-64">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email for full report (optional)"
              className="input-field"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50 whitespace-nowrap"
          >
            {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><Search size={18} /> Run Audit</>}
          </button>
        </form>
        <p className="text-xs text-dark-500 mt-3">
          Free users: 3 audits per day. Results are cached for 24 hours.
        </p>
      </div>

      {/* Results */}
      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Score Header */}
          <div className="glass-panel p-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="64" cy="64" r="56" stroke="#1e293b" strokeWidth="8" fill="none" />
                  <circle
                    cx="64" cy="64" r="56"
                    stroke={results.score >= 80 ? '#22c55e' : results.score >= 60 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${(results.score / 100) * 351.86} 351.86`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-3xl font-bold ${getScoreColor(results.score)}`}>{results.score}</span>
                </div>
              </div>
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold mb-2">{results.url}</h2>
                <p className="text-dark-400 mb-4">
                  {results.score >= 80 
                    ? 'Great job! Your site is well-optimized.' 
                    : results.score >= 60 
                    ? 'Good start, but there are improvements to make.' 
                    : 'Critical issues found. Immediate action recommended.'}
                </p>
                <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                  <span className="px-3 py-1 bg-dark-700 rounded-full text-sm flex items-center gap-1">
                    <Clock size={14} /> {results.loadTime}s load time
                  </span>
                  <span className="px-3 py-1 bg-dark-700 rounded-full text-sm flex items-center gap-1">
                    <Globe size={14} /> {results.pageSize}MB page size
                  </span>
                  <span className="px-3 py-1 bg-dark-700 rounded-full text-sm flex items-center gap-1">
                    <Shield size={14} /> {results.https ? 'HTTPS Secure' : 'HTTP Insecure'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Category Filters */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveCategory('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeCategory === 'all' ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-400 hover:text-white'
              }`}
            >
              All Issues ({results.issues.length})
            </button>
            {issueCategories.map((cat) => {
              const count = results.issues.filter(i => i.category === cat.id).length
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                    activeCategory === cat.id ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-400 hover:text-white'
                  }`}
                >
                  <cat.icon size={14} /> {cat.label} ({count})
                </button>
              )
            })}
          </div>

          {/* Issues List */}
          <div className="space-y-3">
            {results.issues
              .filter(issue => activeCategory === 'all' || issue.category === activeCategory)
              .map((issue, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`glass-panel p-4 border-l-4 ${
                  issue.severity === 'critical' ? 'border-red-500' :
                  issue.severity === 'warning' ? 'border-yellow-500' : 'border-green-500'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`mt-0.5 ${
                    issue.severity === 'critical' ? 'text-red-400' :
                    issue.severity === 'warning' ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {issue.severity === 'critical' ? <XCircle size={20} /> :
                     issue.severity === 'warning' ? <AlertTriangle size={20} /> :
                     <CheckCircle size={20} />}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold">{issue.title}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        issue.severity === 'critical' ? 'bg-red-500/10 text-red-400' :
                        issue.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-400' :
                        'bg-green-500/10 text-green-400'
                      }`}>
                        {issue.severity}
                      </span>
                    </div>
                    <p className="text-sm text-dark-400 mb-2">{issue.description}</p>
                    {issue.recommendation && (
                      <div className="bg-dark-700/50 rounded-lg p-3 text-sm">
                        <span className="text-primary-400 font-medium">Fix:</span> {issue.recommendation}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button className="btn-primary flex items-center gap-2">
              <ArrowRight size={18} /> Download Full Report (PDF)
            </button>
            <button className="btn-secondary flex items-center gap-2">
              <TrendingUp size={18} /> Schedule Monitoring
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}