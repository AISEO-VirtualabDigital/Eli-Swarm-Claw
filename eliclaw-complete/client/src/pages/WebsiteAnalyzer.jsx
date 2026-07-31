import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import toast from 'react-hot-toast'
import {
  Globe, Search, Loader2, Clock, Shield, Server, Code,
  Image, Link2, FileText, AlertTriangle, CheckCircle, XCircle
} from 'lucide-react'

const categoryIcons = {
  performance: Zap,
  security: Shield,
  seo: Search,
  structure: Code,
  media: Image,
  links: Link2,
}

export default function WebsiteAnalyzer() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const { token } = useAuthStore()

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!url) {
      toast.error('Please enter a URL')
      return
    }
    setLoading(true)
    try {
      const data = await api.post('/tools/website-analyzer', { url }, token)
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

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Website Analyzer</h1>
        <p className="text-dark-400">Deep technical analysis of any website — performance, security, structure, and more.</p>
      </motion.div>

      <div className="glass-panel p-6">
        <form onSubmit={handleAnalyze} className="flex gap-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="input-field flex-1"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><Globe size={18} /> Analyze</>}
          </button>
        </form>
      </div>

      {results && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Load Time', value: `${results.loadTime}s`, icon: Clock, color: results.loadTime < 3 ? 'green' : 'yellow' },
              { label: 'Page Size', value: results.pageSize, icon: Server, color: 'blue' },
              { label: 'Security', value: results.https ? 'HTTPS' : 'HTTP', icon: Shield, color: results.https ? 'green' : 'red' },
              { label: 'Tech Stack', value: results.techStack?.[0] || 'Unknown', icon: Code, color: 'purple' },
            ].map((item, i) => (
              <div key={i} className="glass-panel p-4 text-center">
                <div className={`w-10 h-10 rounded-lg bg-${item.color}-500/10 flex items-center justify-center mx-auto mb-2`}>
                  <item.icon size={20} className={`text-${item.color}-400`} />
                </div>
                <div className="text-lg font-bold">{item.value}</div>
                <div className="text-xs text-dark-500">{item.label}</div>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-dark-700">
            {['overview', 'performance', 'security', 'seo', 'structure'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium capitalize transition-all border-b-2 ${
                  activeTab === tab 
                    ? 'border-primary-500 text-primary-400' 
                    : 'border-transparent text-dark-400 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="glass-panel p-6">
            {activeTab === 'overview' && (
              <div className="space-y-4">
                <h3 className="font-bold text-lg">Site Overview</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2 text-dark-400">Meta Information</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="text-dark-500">Title:</span> {results.meta?.title || 'N/A'}</p>
                      <p><span className="text-dark-500">Description:</span> {results.meta?.description || 'N/A'}</p>
                      <p><span className="text-dark-500">Keywords:</span> {results.meta?.keywords || 'N/A'}</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2 text-dark-400">Technical Details</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="text-dark-500">Server:</span> {results.server || 'N/A'}</p>
                      <p><span className="text-dark-500">CMS:</span> {results.cms || 'Unknown'}</p>
                      <p><span className="text-dark-500">Frameworks:</span> {results.frameworks?.join(', ') || 'None detected'}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'performance' && (
              <div className="space-y-4">
                <h3 className="font-bold text-lg">Performance Metrics</h3>
                <div className="space-y-3">
                  {results.performance?.map((metric, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-dark-700/30 rounded-xl">
                      <span className="font-medium">{metric.name}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-dark-600 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${metric.score >= 90 ? 'bg-green-500' : metric.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${metric.score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{metric.score}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-4">
                <h3 className="font-bold text-lg">Security Check</h3>
                <div className="space-y-3">
                  {results.security?.map((check, i) => (
                    <div key={i} className={`flex items-center gap-3 p-3 rounded-xl ${check.passed ? 'bg-green-500/5 border border-green-500/20' : 'bg-red-500/5 border border-red-500/20'}`}>
                      {check.passed ? <CheckCircle size={20} className="text-green-400" /> : <XCircle size={20} className="text-red-400" />}
                      <div>
                        <p className="font-medium">{check.name}</p>
                        <p className="text-sm text-dark-400">{check.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'seo' && (
              <div className="space-y-4">
                <h3 className="font-bold text-lg">SEO Elements</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {results.seoElements?.map((element, i) => (
                    <div key={i} className="p-4 bg-dark-700/30 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{element.name}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${element.found ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          {element.found ? 'Found' : 'Missing'}
                        </span>
                      </div>
                      <p className="text-sm text-dark-400">{element.value || 'Not present'}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'structure' && (
              <div className="space-y-4">
                <h3 className="font-bold text-lg">Page Structure</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  {[
                    { label: 'Headings', value: results.structure?.headings || 0 },
                    { label: 'Images', value: results.structure?.images || 0 },
                    { label: 'Links', value: results.structure?.links || 0 },
                    { label: 'Scripts', value: results.structure?.scripts || 0 },
                    { label: 'Stylesheets', value: results.structure?.stylesheets || 0 },
                    { label: 'Forms', value: results.structure?.forms || 0 },
                  ].map((item, i) => (
                    <div key={i} className="p-4 bg-dark-700/30 rounded-xl text-center">
                      <div className="text-2xl font-bold gradient-text">{item.value}</div>
                      <div className="text-sm text-dark-500">{item.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  )
}