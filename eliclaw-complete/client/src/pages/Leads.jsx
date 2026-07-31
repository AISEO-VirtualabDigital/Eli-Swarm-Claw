import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import { api } from '../utils/api'
import {
  UserPlus, Search, Filter, Mail, Globe, Clock, CheckCircle,
  XCircle, MoreHorizontal, Download, Trash2, Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'

const mockLeads = [
  { id: 1, name: 'John Smith', email: 'john@company.com', company: 'Acme Corp', url: 'https://acme.com', source: 'SEO Audit', status: 'new', date: '2026-07-31', score: 78 },
  { id: 2, name: 'Sarah Johnson', email: 'sarah@tech.io', company: 'TechStart', url: 'https://techstart.io', source: 'Contact Form', status: 'contacted', date: '2026-07-30', score: 85 },
  { id: 3, name: 'Mike Chen', email: 'mike@digital.com', company: 'Digital Pro', url: 'https://digitalpro.com', source: 'Competitor Tool', status: 'qualified', date: '2026-07-29', score: 62 },
  { id: 4, name: 'Emma Wilson', email: 'emma@growth.co', company: 'Growth Co', url: 'https://growth.co', source: 'Website Analyzer', status: 'new', date: '2026-07-28', score: 91 },
  { id: 5, name: 'David Park', email: 'david@seo.net', company: 'SEO Masters', url: 'https://seomasters.net', source: 'SEO Audit', status: 'lost', date: '2026-07-27', score: 45 },
]

const statusColors = {
  new: 'bg-blue-500/10 text-blue-400',
  contacted: 'bg-yellow-500/10 text-yellow-400',
  qualified: 'bg-green-500/10 text-green-400',
  lost: 'bg-red-500/10 text-red-400',
  converted: 'bg-purple-500/10 text-purple-400',
}

export default function Leads() {
  const [leads, setLeads] = useState(mockLeads)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedLeads, setSelectedLeads] = useState([])
  const [loading, setLoading] = useState(false)
  const { token } = useAuthStore()

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = lead.name.toLowerCase().includes(search.toLowerCase()) || 
                          lead.email.toLowerCase().includes(search.toLowerCase()) ||
                          lead.company.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'all' || lead.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const toggleSelect = (id) => {
    setSelectedLeads(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const selectAll = () => {
    if (selectedLeads.length === filteredLeads.length) {
      setSelectedLeads([])
    } else {
      setSelectedLeads(filteredLeads.map(l => l.id))
    }
  }

  const deleteSelected = () => {
    setLeads(leads.filter(l => !selectedLeads.includes(l.id)))
    setSelectedLeads([])
    toast.success('Leads deleted')
  }

  const exportLeads = () => {
    const csv = [
      ['Name', 'Email', 'Company', 'URL', 'Source', 'Status', 'Date', 'Score'].join(','),
      ...filteredLeads.map(l => [l.name, l.email, l.company, l.url, l.source, l.status, l.date, l.score].join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'leads.csv'
    a.click()
    toast.success('Leads exported')
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Leads</h1>
            <p className="text-dark-400">Manage and track leads captured from your tools and forms.</p>
          </div>
          <div className="flex gap-2">
            <button onClick={exportLeads} className="btn-secondary flex items-center gap-2">
              <Download size={18} /> Export
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total', value: leads.length, color: 'blue' },
          { label: 'New', value: leads.filter(l => l.status === 'new').length, color: 'blue' },
          { label: 'Contacted', value: leads.filter(l => l.status === 'contacted').length, color: 'yellow' },
          { label: 'Qualified', value: leads.filter(l => l.status === 'qualified').length, color: 'green' },
          { label: 'Converted', value: leads.filter(l => l.status === 'converted').length, color: 'purple' },
        ].map((stat, i) => (
          <div key={i} className="glass-panel p-4 text-center">
            <div className={`text-2xl font-bold text-${stat.color}-400`}>{stat.value}</div>
            <div className="text-xs text-dark-500">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search leads..."
            className="input-field pl-10"
          />
        </div>
        <select 
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input-field w-40"
        >
          <option value="all">All Status</option>
          <option value="new">New</option>
          <option value="contacted">Contacted</option>
          <option value="qualified">Qualified</option>
          <option value="converted">Converted</option>
          <option value="lost">Lost</option>
        </select>
        {selectedLeads.length > 0 && (
          <button onClick={deleteSelected} className="px-4 py-2 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/20 transition-colors flex items-center gap-2">
            <Trash2 size={16} /> Delete ({selectedLeads.length})
          </button>
        )}
      </div>

      {/* Table */}
      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-700">
                <th className="p-4">
                  <input 
                    type="checkbox" 
                    checked={selectedLeads.length === filteredLeads.length && filteredLeads.length > 0}
                    onChange={selectAll}
                    className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-500"
                  />
                </th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Lead</th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Company</th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Source</th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Status</th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Score</th>
                <th className="text-left p-4 text-sm font-medium text-dark-400">Date</th>
                <th className="p-4"></th>
              </tr>
            </thead>
            <tbody>
              {filteredLeads.map((lead) => (
                <tr key={lead.id} className="border-b border-dark-700/50 hover:bg-dark-700/20 transition-colors">
                  <td className="p-4">
                    <input 
                      type="checkbox" 
                      checked={selectedLeads.includes(lead.id)}
                      onChange={() => toggleSelect(lead.id)}
                      className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-500"
                    />
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
                        {lead.name[0]}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{lead.name}</p>
                        <p className="text-xs text-dark-500">{lead.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-sm">
                    <p>{lead.company}</p>
                    <a href={lead.url} target="_blank" className="text-xs text-primary-400 hover:underline">{lead.url}</a>
                  </td>
                  <td className="p-4 text-sm text-dark-400">{lead.source}</td>
                  <td className="p-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${statusColors[lead.status]}`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-dark-600 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${lead.score >= 80 ? 'bg-green-500' : lead.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                          style={{ width: `${lead.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm">{lead.score}</span>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-dark-400">{lead.date}</td>
                  <td className="p-4">
                    <button className="p-2 hover:bg-dark-700 rounded-lg transition-colors">
                      <MoreHorizontal size={16} className="text-dark-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredLeads.length === 0 && (
          <div className="text-center py-12 text-dark-500">
            <UserPlus size={32} className="mx-auto mb-3 opacity-50" />
            <p>No leads found. Run an SEO audit to capture leads!</p>
          </div>
        )}
      </div>
    </div>
  )
}