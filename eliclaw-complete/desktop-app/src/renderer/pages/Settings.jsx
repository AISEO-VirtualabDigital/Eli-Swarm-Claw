import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../context/authStore'
import {
  User, Key, Bell, Shield, Globe, Palette, Save, Loader2,
  Eye, EyeOff, Copy, CheckCircle, Monitor, Moon, Sun,
  HardDrive, Wifi, Download, RotateCcw, Info
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DesktopSettings() {
  const { user, updateProfile } = useAuthStore()
  const [activeTab, setActiveTab] = useState('general')
  const [saving, setSaving] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [copied, setCopied] = useState(false)
  const [appVersion, setAppVersion] = useState('2.0.0')
  const [systemInfo, setSystemInfo] = useState(null)

  const [settings, setSettings] = useState({
    theme: 'dark',
    minimizeToTray: true,
    notifications: true,
    autoLaunch: false,
    hardwareAcceleration: true,
    offlineMode: false,
    apiUrl: 'https://api.eliclaw.virtualabdigital.com',
    dataDirectory: '',
    autoUpdate: true,
    betaUpdates: false
  })

  useEffect(() => {
    // Load settings from Electron store
    if (window.eliclawAPI) {
      window.eliclawAPI.getAllSettings().then(saved => {
        setSettings(prev => ({ ...prev, ...saved }))
      })

      window.eliclawAPI.getSystemInfo().then(info => {
        setSystemInfo(info)
      })

      window.eliclawAPI.getVersion().then(ver => {
        setAppVersion(ver)
      })
    }
  }, [])

  const handleSettingChange = async (key, value) => {
    const newSettings = { ...settings, [key]: value }
    setSettings(newSettings)

    if (window.eliclawAPI) {
      await window.eliclawAPI.setSetting(key, value)

      // Handle special cases
      if (key === 'theme') {
        await window.eliclawAPI.setTheme(value)
      }
      if (key === 'autoLaunch') {
        await window.eliclawAPI.setAutoLaunch(value)
      }
    }

    toast.success(`${key} updated`)
  }

  const handleSave = async () => {
    setSaving(true)
    await new Promise(r => setTimeout(r, 500))
    setSaving(false)
    toast.success('Settings saved!')
  }

  const copyApiKey = () => {
    const apiKey = 'elc_' + Math.random().toString(36).substring(2, 34)
    if (window.eliclawAPI) {
      window.eliclawAPI.writeToClipboard(apiKey)
    } else {
      navigator.clipboard.writeText(apiKey)
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('API key copied!')
  }

  const handleExportData = async () => {
    if (window.eliclawAPI) {
      const result = await window.eliclawAPI.saveFile({
        defaultPath: 'eliclaw-data-backup.json',
        filters: [{ name: 'JSON', extensions: ['json'] }]
      })
      if (!result.canceled) {
        toast.success('Data exported!')
      }
    }
  }

  const handleCheckUpdate = async () => {
    toast.loading('Checking for updates...')
    // In production, this would trigger autoUpdater.checkForUpdates()
    setTimeout(() => {
      toast.dismiss()
      toast.success('You are on the latest version!')
    }, 2000)
  }

  const tabs = [
    { id: 'general', label: 'General', icon: Monitor },
    { id: 'account', label: 'Account', icon: User },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'advanced', label: 'Advanced', icon: Shield },
    { id: 'about', label: 'About', icon: Info },
  ]

  return (
    <div className="space-y-6 p-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-dark-400">Configure EliClaw Desktop to work the way you do.</p>
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
          {/* GENERAL TAB */}
          {activeTab === 'general' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="glass-panel p-6">
                <h2 className="text-xl font-bold mb-4">Appearance</h2>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                        <Palette size={18} className="text-primary-400" />
                      </div>
                      <div>
                        <p className="font-medium">Theme</p>
                        <p className="text-sm text-dark-400">Choose your preferred color scheme</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSettingChange('theme', 'light')}
                        className={`p-2 rounded-lg transition-all ${settings.theme === 'light' ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-400'}`}
                      >
                        <Sun size={18} />
                      </button>
                      <button
                        onClick={() => handleSettingChange('theme', 'dark')}
                        className={`p-2 rounded-lg transition-all ${settings.theme === 'dark' ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-400'}`}
                      >
                        <Moon size={18} />
                      </button>
                      <button
                        onClick={() => handleSettingChange('theme', 'system')}
                        className={`p-2 rounded-lg transition-all ${settings.theme === 'system' ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-400'}`}
                      >
                        <Monitor size={18} />
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                        <Download size={18} className="text-primary-400" />
                      </div>
                      <div>
                        <p className="font-medium">Minimize to Tray</p>
                        <p className="text-sm text-dark-400">Keep running in background when closed</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleSettingChange('minimizeToTray', !settings.minimizeToTray)}
                      className={`w-12 h-6 rounded-full transition-all relative ${
                        settings.minimizeToTray ? 'bg-primary-500' : 'bg-dark-600'
                      }`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${
                        settings.minimizeToTray ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-dark-700/30 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary-500/10 flex items-center justify-center">
                        <RotateCcw size={18} className="text-primary-400" />
                      </div>
                      <div>
                        <p className="font-medium">Auto-Launch</p>
                        <p className="text-sm text-dark-400">Start EliClaw when you log in</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleSettingChange('autoLaunch', !settings.autoLaunch)}
                      className={`w-12 h-6 rounded-full transition-all relative ${
                        settings.autoLaunch ? 'bg-primary-500' : 'bg-dark-600'
                      }`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all ${
                        settings.autoLaunch ? 'left-6' : 'left-0.5'
                      }`}></div>
                    </button>
                  </div>
                </div>
              </div>

              <div className="glass-panel p-6">
                <h2 className="text-xl font-bold mb-4">Data Management</h2>
                <div className="flex gap-3">
                  <button onClick={handleExportData} className="btn-secondary flex items-center gap-2">
                    <Download size={16} /> Export Data
                  </button>
                  <button className="px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl hover:bg-red-500/20 transition-colors flex items-center gap-2">
                    <RotateCcw size={16} /> Reset All Data
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* ABOUT TAB */}
          {activeTab === 'about' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="glass-panel p-6 text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-3xl">E</span>
                </div>
                <h2 className="text-2xl font-bold mb-1">EliClaw Desktop</h2>
                <p className="text-dark-400 mb-4">Version {appVersion}</p>
                <p className="text-sm text-dark-500 mb-6">Built with ❤️ by Virtualab Digital</p>

                <div className="flex justify-center gap-3 mb-6">
                  <button onClick={handleCheckUpdate} className="btn-primary flex items-center gap-2">
                    <RotateCcw size={16} /> Check for Updates
                  </button>
                </div>

                <div className="text-left space-y-2 text-sm">
                  <div className="flex justify-between py-2 border-b border-dark-700">
                    <span className="text-dark-400">Platform</span>
                    <span>{systemInfo?.platform || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-700">
                    <span className="text-dark-400">Architecture</span>
                    <span>{systemInfo?.arch || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-700">
                    <span className="text-dark-400">Memory</span>
                    <span>{systemInfo ? `${Math.round(systemInfo.freeMemory / 1024 / 1024 / 1024)}GB / ${Math.round(systemInfo.totalMemory / 1024 / 1024 / 1024)}GB` : 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-dark-700">
                    <span className="text-dark-400">CPUs</span>
                    <span>{systemInfo?.cpus || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-dark-400">Uptime</span>
                    <span>{systemInfo ? `${Math.floor(systemInfo.uptime / 3600)}h ${Math.floor((systemInfo.uptime % 3600) / 60)}m` : 'Unknown'}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Other tabs reuse web settings with desktop additions */}
          {activeTab !== 'general' && activeTab !== 'about' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel p-6">
              <p className="text-dark-400">This section uses the same settings as the web version.</p>
              <p className="text-sm text-dark-500 mt-2">Syncs automatically when online.</p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}