import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../context/authStore'
import {
  LayoutDashboard, Search, Users, Globe, Zap, FileText, 
  Bot, Settings, LogOut, ChevronLeft, ChevronRight,
  BarChart3, UserPlus
} from 'lucide-react'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Search, label: 'SEO Audit', path: '/tools/seo' },
  { icon: Users, label: 'Competitor Analysis', path: '/tools/competitor' },
  { icon: Globe, label: 'Website Analyzer', path: '/tools/analyzer' },
  { icon: Zap, label: 'Automation', path: '/tools/automation' },
  { icon: FileText, label: 'Content Analysis', path: '/tools/content' },
  { icon: Bot, label: 'Swarm Agent', path: '/tools/swarm' },
  { icon: UserPlus, label: 'Leads', path: '/leads' },
  { icon: BarChart3, label: 'Analytics', path: '/dashboard' },
]

const bottomItems = [
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export default function Sidebar({ open, setOpen }) {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  return (
    <aside className={`fixed left-0 top-0 h-full bg-dark-800 border-r border-dark-700/50 z-50 transition-all duration-300 ${open ? 'w-64' : 'w-20'}`}>
      <div className="flex items-center justify-between p-4 border-b border-dark-700/50">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-lg">E</span>
          </div>
          {open && <span className="text-xl font-bold gradient-text">EliClaw</span>}
        </Link>
        <button 
          onClick={() => setOpen(!open)}
          className="p-1.5 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
        >
          {open ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>

      <nav className="p-3 space-y-1">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                isActive 
                  ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30' 
                  : 'text-dark-400 hover:bg-dark-700 hover:text-white'
              }`}
            >
              <item.icon size={20} className={isActive ? 'text-primary-400' : 'group-hover:text-white'} />
              {open && <span className="font-medium text-sm">{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-dark-700/50">
        {bottomItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-dark-400 hover:bg-dark-700 hover:text-white transition-all duration-200 mb-1"
          >
            <item.icon size={20} />
            {open && <span className="font-medium text-sm">{item.label}</span>}
          </Link>
        ))}
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-red-400 hover:bg-red-500/10 transition-all duration-200 w-full"
        >
          <LogOut size={20} />
          {open && <span className="font-medium text-sm">Logout</span>}
        </button>

        {open && user && (
          <div className="mt-3 pt-3 border-t border-dark-700/50 flex items-center gap-3 px-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
              {user.name?.[0] || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <p className="text-xs text-dark-500 truncate">{user.email}</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}