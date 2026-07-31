import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import toast from 'react-hot-toast'
import {
  FileText, Loader2, CheckCircle, AlertTriangle, XCircle,
  Type, Hash, BookOpen, TrendingUp, Target, Copy, RefreshCw
} from 'lucide-react'

export default function ContentTool() {
  const [content, setContent] = useState('')
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const { token } = useAuthStore()

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!content.trim()) {
      toast.error('Please enter some content')
      return
    }
    setLoading(true)
    try {
      const data = await api.post('/tools/content-analysis', { content, keyword }, token)
      if (data.success) {
        setResults(data.results)
        toast.success('Analysis complete!')
      } else {
        toast.error(data.error || 'Analysis failed')
      }
    } catch (err) {
      toast.error('Network error')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Content Analysis</h1>
        <p className="text-dark-400">AI-powered content quality scoring, readability analysis, and SEO optimization.</p>
      </motion.div>

      <div className="glass-panel p-6">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Target Keyword (optional)</label>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="e.g., digital marketing"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Your Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your article, blog post, or page content here..."
              rows={10}
              className="input-field resize-none"
              required
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-dark-500">{content.length} characters</span>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><FileText size={18} /> Analyze Content</>}
            </button>
          </div>
        </form>
      </div>

      {results && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Overall Score */}
          <div className="glass-panel p-6">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="relative w-40 h-40">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="80" cy="80" r="70" stroke="#1e293b" strokeWidth="10" fill="none" />
                  <circle
                    cx="80" cy="80" r="70"
                    stroke={results.overallScore >= 80 ? '#22c55e' : results.overallScore >= 60 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="10"
                    fill="none"
                    strokeDasharray={`${(results.overallScore / 100) * 439.82} 439.82`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className={`text-4xl font-bold ${getScoreColor(results.overallScore)}`}>{results.overallScore}</span>
                  <span className="text-xs text-dark-500">Overall</span>
                </div>
              </div>
              <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: 'Readability', score: results.readability, icon: BookOpen },
                  { label: 'SEO Score', score: results.seoScore, icon: Target },
                  { label: 'Keyword Density', score: results.keywordDensity, icon: Hash },
                  { label: 'Structure', score: results.structure, icon: Type },
                ].map((item, i) => (
                  <div key={i} className="text-center p-3 bg-dark-700/30 rounded-xl">
                    <item.icon size={20} className={`mx-auto mb-2 ${getScoreColor(item.score)}`} />
                    <div className={`text-xl font-bold ${getScoreColor(item.score)}`}>{item.score}</div>
                    <div className="text-xs text-dark-500">{item.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Issues & Suggestions */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="glass-panel p-6">
              <h3 className="font-bold text-lg mb-4">Issues Found</h3>
              <div className="space-y-3">
                {results.issues.map((issue, i) => (
                  <div key={i} className={`flex items-start gap-3 p-3 rounded-xl ${
                    issue.severity === 'critical' ? 'bg-red-500/5 border border-red-500/20' :
                    issue.severity === 'warning' ? 'bg-yellow-500/5 border border-yellow-500/20' :
                    'bg-green-500/5 border border-green-500/20'
                  }`}>
                    {issue.severity === 'critical' ? <XCircle size={18} className="text-red-400 mt-0.5" /> :
                     issue.severity === 'warning' ? <AlertTriangle size={18} className="text-yellow-400 mt-0.5" /> :
                     <CheckCircle size={18} className="text-green-400 mt-0.5" />}
                    <div>
                      <p className="font-medium text-sm">{issue.title}</p>
                      <p className="text-xs text-dark-400">{issue.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel p-6">
              <h3 className="font-bold text-lg mb-4">AI Suggestions</h3>
              <div className="space-y-3">
                {results.suggestions.map((suggestion, i) => (
                  <div key={i} className="p-3 bg-dark-700/30 rounded-xl">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp size={14} className="text-primary-400" />
                      <span className="font-medium text-sm">{suggestion.title}</span>
                    </div>
                    <p className="text-xs text-dark-400 mb-2">{suggestion.description}</p>
                    <div className="bg-dark-800 rounded-lg p-2 text-xs text-dark-300 font-mono flex items-center justify-between">
                      <span>{suggestion.example}</span>
                      <button 
                        onClick={() => { navigator.clipboard.writeText(suggestion.example); toast.success('Copied!') }}
                        className="p-1 hover:bg-dark-700 rounded transition-colors"
                      >
                        <Copy size={12} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Keyword Analysis */}
          {results.keywordAnalysis && (
            <div className="glass-panel p-6">
              <h3 className="font-bold text-lg mb-4">Keyword Analysis</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-dark-700/30 rounded-xl">
                  <div className="text-sm text-dark-500 mb-1">Keyword Count</div>
                  <div className="text-2xl font-bold">{results.keywordAnalysis.count}</div>
                </div>
                <div className="p-4 bg-dark-700/30 rounded-xl">
                  <div className="text-sm text-dark-500 mb-1">Density</div>
                  <div className="text-2xl font-bold">{results.keywordAnalysis.density}%</div>
                </div>
                <div className="p-4 bg-dark-700/30 rounded-xl">
                  <div className="text-sm text-dark-500 mb-1">Placement</div>
                  <div className="text-2xl font-bold">{results.keywordAnalysis.placementScore}/10</div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  )
}