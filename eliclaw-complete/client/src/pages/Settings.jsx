import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import {
  User, Key, Bell, Shield, Globe, Palette, Save, Loader2,
  Eye, EyeOff, Copy, CheckCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user, updateProfile } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [saving, setSaving] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [copied, setCopied] = useState(false)

  const [profile, setProfile] = useState({
    name: user?.name || '',
    email: user?.email || '',
    company: user?.company || '',
    website: user?.website || '',
  })

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    weeklyReport: true,
    competitorChanges: false,
    newLeads: true,
  })

  const apiKey = 'elc_' + Math.random().toString(36).substring(2, 34)

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 1000))
    updateProfile(profile)
    setSaving(false)
    toast.success('Settings saved!')
  }

  const copyApiKey = () => {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('API key copied!')
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
  ]

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-dark-400">Manage your account, API keys, and preferences.</p>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Tabs */}
        <div className="lg:w-64 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all ${
                activeTab === tab.id 
                  ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30' 
                  : 'text-dark-400 hover:bg-dark-700 hover:text-white'
              }`}
            >
              <tab.icon size={18} />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel p-6 space-y-6">
              <h2 className="text-xl font-bold">Profile Information</h2>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-cyan-400 flex items-center justify-center text-2xl font-bold">
                  {profile.name?.[0] || 'U'}
                </div>
                <div>
                  <button className="text-sm text-primary-400 hover:text-primary-300 font-medium">Change Avatar</button>
                  <p className="text-xs text-dark-500">JPG, PNG. Max 2MB.</p>
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({...profile, name: e.target.value})}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Company</label>
                  <input
                    type="text"
                    value={profile.company}
                    onChange={(e) => setProfile({...profile, company: e.target.value})}
                    className="input-field"
                    placeholder="Your company name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Website</label>
                  <input
                    type="url"
                    value={profile.website}
                    onChange={(e) => setProfile({...profile, website: e.target.value})}
                    className="input-field"
                    placeholder="https://yourcompany.com"
                  />
                </div>
              </div>
              <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2">
                {saving ? <><Loader2 size={16} className="animate-spin" /> Saving...</> : <><Save size={16} /> Save Changes</>}
              </button>
            </motion.div>
          )}

          {activeTab === 'api' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel p-6 space-y-6">
              <h2 className="text-xl font-bold">API Keys</h2>
              <p className="text-dark-400 text-sm">Use these keys to connect your WordPress site and other integrations.</p>

              <div className="bg-dark-700/50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Production API Key</span>
                  <span className="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-full">Active</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-dark-800 rounded-lg px-3 py-2 font-mono text-sm flex items-center gap-2">
                    {showApiKey ? apiKey : '••••••••••••••••••••••••••'}
                    <button onClick={() => setShowApiKey(!showApiKey)} className="ml-auto">
                      {showApiKey ? <EyeOff size={14} className="text-dark-500" /> : <Eye size={14} className="text-dark-500" />}
                    </button>
                  </div>
                  <button onClick={copyApiKey} className="p-2 bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors">
                    {copied ? <CheckCircle size={18} className="text-green-400" /> : <Copy size={18} className="text-dark-400" />}
                  </button>
                </div>
                <p className="text-xs text-dark-500 mt-2">Last used: 2 hours ago • Created: Jul 31, 2026</p>
              </div>

              <div className="bg-dark-700/50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">WordPress Integration</span>
                  <span className="text-xs px-2 py-1 bg-blue-500/10 text-blue-400 rounded-full">Connected</span>
                </div>
                <p className="text-sm text-dark-400">Connected to virtualabdigital.com</p>
                <div className="mt-3 p-3 bg-dark-800 rounded-lg">
                  <p className="text-xs text-dark-500 mb-1">Webhook URL</p>
                  <code className="text-sm text-primary-400">https://{DOMAIN}/api/webhooks/wordpress</code>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'notifications' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel p-6 space-y-6">
              <h2 className="text-xl font-bold">Notification Preferences</h2>
              <div className="space-y-4">
                {[
                  { key: 'emailAlerts', label: 'Email Alerts', desc: 'Receive alerts for critical SEO issues', icon: Mail },
                  { key: 'weeklyReport', label: 'Weekly Reports', desc: 'Get a summary every Monday', icon: Globe },
                  { key: 'competitorChanges', label: 'Competitor Changes', desc: 'Alert when competitors rank changes', icon: TrendingUp },
                  { key: 'newLeads', label: 'New Leads', desc: 'Instant notification for new captured leads', icon: UserPlus },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-4 bg-dark-700/30 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                        <item.icon size={18} className="text-primary-400" />
                      </div>
                      <div>
                        <p className="font-medium">{item.label}</p>
                        <p className="text-sm text-dark-400">{item.desc}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setNotifications({...notifications, [item.key]: !notifications[item.key]})}
                      className={`w-12 h-6 rounded-full transition-all relative ${
                        notifications[item.key] ? 'bg-primary-500' : 'bg-dark-600'
                      }`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${
                        notifications[item.key] ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </button>
                  </div>
                ))}
              </div>
              <button onClick={handleSave} className="btn-primary flex items-center gap-2">
                <Save size={16} /> Save Preferences
              </button>
            </motion.div>
          )}

          {activeTab === 'security' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel p-6 space-y-6">
              <h2 className="text-xl font-bold">Security</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Current Password</label>
                  <input type="password" placeholder="••••••••" className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">New Password</label>
                  <input type="password" placeholder="••••••••" className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Confirm New Password</label>
                  <input type="password" placeholder="••••••••" className="input-field" />
                </div>
              </div>
              <button className="btn-primary">Update Password</button>

              <div className="mt-6 pt-6 border-t border-dark-700">
                <h3 className="font-bold mb-4 text-red-400">Danger Zone</h3>
                <button className="px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl hover:bg-red-500/20 transition-colors">
                  Delete Account
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}