import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import toast from 'react-hot-toast'
import {
  Users, Plus, X, ArrowRight, TrendingUp, TrendingDown, Minus,
  Search, BarChart3, Globe, Loader2, Target
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts'

export default function CompetitorTool() {
  const [competitors, setCompetitors] = useState([''])
  const [yourUrl, setYourUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const { token } = useAuthStore()

  const addCompetitor = () => {
    if (competitors.length < 5) {
      setCompetitors([...competitors, ''])
    } else {
      toast.error('Maximum 5 competitors in free plan')
    }
  }

  const removeCompetitor = (index) => {
    setCompetitors(competitors.filter((_, i) => i !== index))
  }

  const updateCompetitor = (index, value) => {
    const updated = [...competitors]
    updated[index] = value
    setCompetitors(updated)
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    const validCompetitors = competitors.filter(c => c.trim() !== '')
    if (!yourUrl || validCompetitors.length === 0) {
      toast.error('Enter your URL and at least one competitor')
      return
    }

    setLoading(true)
    try {
      const data = await api.post('/tools/competitor-analysis', {
        yourUrl,
        competitors: validCompetitors
      }, token)
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
        <h1 className="text-3xl font-bold mb-2">Competitor Analysis</h1>
        <p className="text-dark-400">Compare your site against competitors across SEO, performance, and content metrics.</p>
      </motion.div>

      {/* Input Form */}
      <div className="glass-panel p-6">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Your Website</label>
            <input
              type="url"
              value={yourUrl}
              onChange={(e) => setYourUrl(e.target.value)}
              placeholder="https://yourwebsite.com"
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Competitors</label>
            <div className="space-y-3">
              {competitors.map((comp, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    type="url"
                    value={comp}
                    onChange={(e) => updateCompetitor(i, e.target.value)}
                    placeholder={`Competitor ${i + 1} URL`}
                    className="input-field"
                  />
                  {competitors.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCompetitor(i)}
                      className="p-3 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/20 transition-colors"
                    >
                      <X size={18} />
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addCompetitor}
              className="mt-3 flex items-center gap-2 text-primary-400 hover:text-primary-300 text-sm font-medium"
            >
              <Plus size={16} /> Add competitor ({5 - competitors.length} remaining)
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <><Loader2 size={18} className="animate-spin" /> Analyzing...</> : <><Target size={18} /> Run Analysis</>}
          </button>
        </form>
      </div>

      {/* Results */}
      {results && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Comparison Table */}
          <div className="glass-panel p-6 overflow-x-auto">
            <h3 className="font-bold text-lg mb-4">Side-by-Side Comparison</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-700">
                  <th className="text-left py-3 px-4 text-dark-400 font-medium">Metric</th>
                  <th className="text-center py-3 px-4 text-primary-400 font-medium">You</th>
                  {results.competitors.map((comp, i) => (
                    <th key={i} className="text-center py-3 px-4 text-dark-400 font-medium">{comp.domain}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.metrics.map((metric, i) => (
                  <tr key={i} className="border-b border-dark-700/50 hover:bg-dark-700/20">
                    <td className="py-3 px-4 font-medium">{metric.name}</td>
                    <td className="py-3 px-4 text-center">
                      <span className={`font-bold ${metric.yourValue >= metric.best ? 'text-green-400' : ''}`}>
                        {metric.yourValue}
                      </span>
                      {metric.yourValue >= metric.best && <span className="text-green-400 ml-1">★</span>}
                    </td>
                    {metric.competitorValues.map((val, j) => (
                      <td key={j} className="py-3 px-4 text-center text-dark-400">{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="glass-panel p-6">
              <h3 className="font-bold text-lg mb-4">Traffic Comparison</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={results.trafficData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                  <Legend />
                  <Bar dataKey="organic" fill="#3b82f6" name="Organic" />
                  <Bar dataKey="paid" fill="#22c55e" name="Paid" />
                  <Bar dataKey="social" fill="#a855f7" name="Social" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="glass-panel p-6">
              <h3 className="font-bold text-lg mb-4">Strength Radar</h3>
              <ResponsiveContainer width="100%" height={250}>
                <RadarChart data={results.radarData}>
                  <PolarGrid stroke="#334155" />
                  <PolarAngleAxis dataKey="metric" stroke="#64748b" fontSize={12} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" fontSize={10} />
                  <Radar name="You" dataKey="you" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  <Radar name="Avg Competitor" dataKey="avg" stroke="#ef4444" fill="#ef4444" fillOpacity={0.1} />
                  <Legend />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Opportunities */}
          <div className="glass-panel p-6">
            <h3 className="font-bold text-lg mb-4">Growth Opportunities</h3>
            <div className="space-y-3">
              {results.opportunities.map((opp, i) => (
                <div key={i} className="flex items-start gap-3 p-4 bg-dark-700/30 rounded-xl">
                  <div className={`mt-0.5 ${opp.impact === 'high' ? 'text-green-400' : 'text-yellow-400'}`}>
                    {opp.impact === 'high' ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">{opp.title}</h4>
                    <p className="text-sm text-dark-400">{opp.description}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        opp.impact === 'high' ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                      }`}>
                        {opp.impact} impact
                      </span>
                      <span className="text-xs text-dark-500">{opp.effort} effort</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}