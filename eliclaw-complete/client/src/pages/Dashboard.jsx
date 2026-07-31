import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import {
  Search, Users, Globe, Zap, FileText, Bot, TrendingUp,
  Activity, Clock, ArrowUpRight, ArrowDownRight, BarChart3
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const tools = [
  { icon: Search, title: 'SEO Audit', path: '/tools/seo', color: 'bg-blue-500', desc: 'Analyze any website' },
  { icon: Users, title: 'Competitor', path: '/tools/competitor', color: 'bg-purple-500', desc: 'Track rivals' },
  { icon: Globe, title: 'Analyzer', path: '/tools/analyzer', color: 'bg-green-500', desc: 'Deep technical scan' },
  { icon: Zap, title: 'Automation', path: '/tools/automation', color: 'bg-yellow-500', desc: 'Build workflows' },
  { icon: FileText, title: 'Content', path: '/tools/content', color: 'bg-red-500', desc: 'AI content score' },
  { icon: Bot, title: 'Swarm', path: '/tools/swarm', color: 'bg-indigo-500', desc: 'Multi-agent AI' },
]

const activityData = [
  { name: 'Mon', audits: 4, leads: 2 },
  { name: 'Tue', audits: 3, leads: 1 },
  { name: 'Wed', audits: 7, leads: 4 },
  { name: 'Thu', audits: 5, leads: 3 },
  { name: 'Fri', audits: 8, leads: 5 },
  { name: 'Sat', audits: 2, leads: 1 },
  { name: 'Sun', audits: 3, leads: 2 },
]

const scoreData = [
  { name: 'Good', value: 65, color: '#22c55e' },
  { name: 'Needs Work', value: 25, color: '#f59e0b' },
  { name: 'Critical', value: 10, color: '#ef4444' },
]

export default function Dashboard() {
  const { user, token } = useAuthStore()
  const [stats, setStats] = useState({ audits: 0, leads: 0, score: 0, competitors: 0 })
  const [recentActivity, setRecentActivity] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [token])

  const fetchDashboardData = async () => {
    try {
      const data = await api.get('/dashboard/stats', token)
      if (data.success) {
        setStats(data.stats)
        setRecentActivity(data.recentActivity || [])
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.name?.split(' ')[0] || 'User'} 👋</h1>
        <p className="text-dark-400">Here's what's happening with your projects today.</p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Audits', value: stats.audits, icon: Search, change: '+12%', up: true, color: 'blue' },
          { label: 'Leads Captured', value: stats.leads, icon: Users, change: '+8%', up: true, color: 'purple' },
          { label: 'Avg SEO Score', value: `${stats.score || 72}`, icon: Activity, change: '+5%', up: true, color: 'green' },
          { label: 'Competitors', value: stats.competitors, icon: Globe, change: '-2%', up: false, color: 'orange' },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-panel p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 rounded-lg bg-${stat.color}-500/10 flex items-center justify-center`}>
                <stat.icon size={20} className={`text-${stat.color}-400`} />
              </div>
              <span className={`flex items-center gap-1 text-sm ${stat.up ? 'text-green-400' : 'text-red-400'}`}>
                {stat.up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                {stat.change}
              </span>
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-sm text-dark-500">{stat.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Quick Tools */}
      <div>
        <h2 className="text-xl font-bold mb-4">Quick Tools</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {tools.map((tool, i) => (
            <Link key={i} to={tool.path}>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="glass-panel p-4 text-center card-hover cursor-pointer"
              >
                <div className={`w-12 h-12 ${tool.color} rounded-xl flex items-center justify-center mx-auto mb-3`}>
                  <tool.icon size={22} className="text-white" />
                </div>
                <h3 className="font-semibold text-sm mb-1">{tool.title}</h3>
                <p className="text-xs text-dark-500">{tool.desc}</p>
              </motion.div>
            </Link>
          ))}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Activity Chart */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-bold text-lg">Activity Overview</h3>
            <select className="bg-dark-700 border border-dark-600 rounded-lg px-3 py-1 text-sm">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
            </select>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="colorAudits" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                itemStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="audits" stroke="#3b82f6" fillOpacity={1} fill="url(#colorAudits)" strokeWidth={2} />
              <Area type="monotone" dataKey="leads" stroke="#22c55e" fillOpacity={1} fill="url(#colorLeads)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Score Distribution */}
        <div className="glass-panel p-6">
          <h3 className="font-bold text-lg mb-6">SEO Score Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={scoreData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {scoreData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-4">
            {scoreData.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-dark-400">{item.name}</span>
                </div>
                <span className="font-medium">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-lg">Recent Activity</h3>
          <Link to="/leads" className="text-primary-400 text-sm hover:text-primary-300">View all</Link>
        </div>
        <div className="space-y-3">
          {recentActivity.length > 0 ? recentActivity.map((activity, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-dark-700/30 rounded-xl">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-primary-500/10 flex items-center justify-center">
                  <Clock size={16} className="text-primary-400" />
                </div>
                <div>
                  <p className="font-medium text-sm">{activity.action}</p>
                  <p className="text-xs text-dark-500">{activity.time}</p>
                </div>
              </div>
              <span className="text-xs text-dark-500">{activity.result}</span>
            </div>
          )) : (
            <div className="text-center py-8 text-dark-500">
              <Activity size={32} className="mx-auto mb-3 opacity-50" />
              <p>No recent activity. Run your first audit to get started!</p>
              <Link to="/tools/seo" className="btn-primary mt-4 inline-block text-sm">Run SEO Audit</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}