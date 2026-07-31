import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import {
  Bot, Play, Pause, RotateCcw, Plus, Trash2, Activity,
  Cpu, MessageSquare, Globe, Search, FileText, Zap,
  CheckCircle, XCircle, Clock, Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'

const agentTypes = [
  { id: 'seo', name: 'SEO Agent', icon: Search, color: 'bg-blue-500', desc: 'Analyzes and optimizes search rankings' },
  { id: 'content', name: 'Content Agent', icon: FileText, color: 'bg-green-500', desc: 'Generates and optimizes content' },
  { id: 'competitor', name: 'Competitor Agent', icon: Globe, color: 'bg-purple-500', desc: 'Monitors competitor movements' },
  { id: 'technical', name: 'Technical Agent', icon: Cpu, color: 'bg-yellow-500', desc: 'Fixes technical SEO issues' },
  { id: 'social', name: 'Social Agent', icon: MessageSquare, color: 'bg-pink-500', desc: 'Manages social signals' },
  { id: 'analytics', name: 'Analytics Agent', icon: Activity, color: 'bg-cyan-500', desc: 'Tracks and reports metrics' },
]

const mockAgents = [
  { id: 1, name: 'SEO Agent Alpha', type: 'seo', status: 'running', tasks: 12, completed: 89, lastActive: '2 min ago' },
  { id: 2, name: 'Content Bot 1', type: 'content', status: 'running', tasks: 5, completed: 34, lastActive: '5 min ago' },
  { id: 3, name: 'Competitor Watcher', type: 'competitor', status: 'paused', tasks: 0, completed: 156, lastActive: '1 hour ago' },
  { id: 4, name: 'Tech Fixer', type: 'technical', status: 'running', tasks: 3, completed: 67, lastActive: '10 min ago' },
]

const mockLogs = [
  { time: '14:32:01', agent: 'SEO Agent Alpha', action: 'Completed audit for example.com', type: 'success' },
  { time: '14:31:45', agent: 'Content Bot 1', action: 'Generated blog outline', type: 'info' },
  { time: '14:30:12', agent: 'Tech Fixer', action: 'Fixed 3 broken links', type: 'success' },
  { time: '14:28:55', agent: 'Competitor Watcher', action: 'Detected ranking change', type: 'warning' },
  { time: '14:25:30', agent: 'SEO Agent Alpha', action: 'Started keyword research', type: 'info' },
]

export default function SwarmAgent() {
  const [agents, setAgents] = useState(mockAgents)
  const [logs, setLogs] = useState(mockLogs)
  const [showCreate, setShowCreate] = useState(false)
  const [selectedType, setSelectedType] = useState(null)
  const [agentName, setAgentName] = useState('')
  const [activeTab, setActiveTab] = useState('agents')

  const toggleAgent = (id) => {
    setAgents(agents.map(a => 
      a.id === id ? { ...a, status: a.status === 'running' ? 'paused' : 'running' } : a
    ))
    toast.success('Agent status updated')
  }

  const deleteAgent = (id) => {
    setAgents(agents.filter(a => a.id !== id))
    toast.success('Agent removed')
  }

  const createAgent = () => {
    if (!selectedType || !agentName) {
      toast.error('Select type and name')
      return
    }
    const type = agentTypes.find(t => t.id === selectedType)
    const newAgent = {
      id: agents.length + 1,
      name: agentName,
      type: selectedType,
      status: 'running',
      tasks: 0,
      completed: 0,
      lastActive: 'Just now'
    }
    setAgents([...agents, newAgent])
    setShowCreate(false)
    setAgentName('')
    setSelectedType(null)
    toast.success(`${type.name} created!`)
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Swarm Agent</h1>
            <p className="text-dark-400">Multi-agent AI coordination. Deploy specialized agents to work together.</p>
          </div>
          <button 
            onClick={() => setShowCreate(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={18} /> Deploy Agent
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Active Agents', value: agents.filter(a => a.status === 'running').length, icon: Bot, color: 'green' },
          { label: 'Total Tasks', value: agents.reduce((a, b) => a + b.tasks, 0), icon: Activity, color: 'blue' },
          { label: 'Completed', value: agents.reduce((a, b) => a + b.completed, 0), icon: CheckCircle, color: 'purple' },
          { label: 'Uptime', value: '99.8%', icon: Clock, color: 'yellow' },
        ].map((stat, i) => (
          <div key={i} className="glass-panel p-4 text-center">
            <div className={`w-10 h-10 rounded-lg bg-${stat.color}-500/10 flex items-center justify-center mx-auto mb-2`}>
              <stat.icon size={20} className={`text-${stat.color}-400`} />
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-xs text-dark-500">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-700">
        {['agents', 'logs', 'templates'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 text-sm font-medium capitalize transition-all border-b-2 ${
              activeTab === tab ? 'border-primary-500 text-primary-400' : 'border-transparent text-dark-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Agents Tab */}
      {activeTab === 'agents' && (
        <div className="grid md:grid-cols-2 gap-4">
          {agents.map((agent) => {
            const type = agentTypes.find(t => t.id === agent.type)
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-panel p-5"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${type?.color || 'bg-primary-500'} rounded-xl flex items-center justify-center`}>
                      {type && <type.icon size={20} className="text-white" />}
                    </div>
                    <div>
                      <h3 className="font-bold">{agent.name}</h3>
                      <p className="text-xs text-dark-500">{type?.desc}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${agent.status === 'running' ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></span>
                    <span className="text-xs text-dark-500 capitalize">{agent.status}</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center p-2 bg-dark-700/30 rounded-lg">
                    <div className="text-lg font-bold">{agent.tasks}</div>
                    <div className="text-xs text-dark-500">Active</div>
                  </div>
                  <div className="text-center p-2 bg-dark-700/30 rounded-lg">
                    <div className="text-lg font-bold">{agent.completed}</div>
                    <div className="text-xs text-dark-500">Done</div>
                  </div>
                  <div className="text-center p-2 bg-dark-700/30 rounded-lg">
                    <div className="text-lg font-bold">{agent.lastActive}</div>
                    <div className="text-xs text-dark-500">Last Active</div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button 
                    onClick={() => toggleAgent(agent.id)}
                    className="flex-1 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1"
                  >
                    {agent.status === 'running' ? <><Pause size={14} /> Pause</> : <><Play size={14} /> Resume</>}
                  </button>
                  <button 
                    onClick={() => deleteAgent(agent.id)}
                    className="p-2 bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="glass-panel p-6">
          <div className="space-y-2">
            {logs.map((log, i) => (
              <div key={i} className="flex items-center gap-4 p-3 bg-dark-700/30 rounded-xl text-sm">
                <span className="text-dark-500 font-mono text-xs w-20">{log.time}</span>
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  log.type === 'success' ? 'bg-green-500' : log.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                }`}></span>
                <span className="font-medium w-32 text-dark-400">{log.agent}</span>
                <span className="flex-1">{log.action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agentTypes.map((type, i) => (
            <div key={i} className="glass-panel p-5 card-hover cursor-pointer" onClick={() => { setSelectedType(type.id); setShowCreate(true); }}>
              <div className={`w-12 h-12 ${type.color} rounded-xl flex items-center justify-center mb-4`}>
                <type.icon size={24} className="text-white" />
              </div>
              <h3 className="font-bold mb-1">{type.name}</h3>
              <p className="text-sm text-dark-400 mb-3">{type.desc}</p>
              <button className="text-primary-400 text-sm font-medium flex items-center gap-1">
                <Plus size={14} /> Deploy
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-panel p-6 max-w-md w-full"
          >
            <h3 className="text-xl font-bold mb-4">Deploy New Agent</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Agent Name</label>
                <input
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder="e.g., SEO Agent Beta"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Agent Type</label>
                <div className="grid grid-cols-2 gap-2">
                  {agentTypes.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => setSelectedType(type.id)}
                      className={`p-3 rounded-xl border transition-all text-left ${
                        selectedType === type.id 
                          ? 'border-primary-500 bg-primary-500/10' 
                          : 'border-dark-600 hover:border-dark-500'
                      }`}
                    >
                      <type.icon size={18} className={`mb-1 ${selectedType === type.id ? 'text-primary-400' : 'text-dark-400'}`} />
                      <div className="text-sm font-medium">{type.name}</div>
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setShowCreate(false)} className="flex-1 btn-secondary">Cancel</button>
                <button onClick={createAgent} className="flex-1 btn-primary">Deploy</button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}