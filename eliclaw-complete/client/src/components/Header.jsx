import { Bell, Search, Menu } from 'lucide-react'
import { useAuthStore } from '../context/authStore'

export default function Header({ sidebarOpen, setSidebarOpen }) {
  const { user } = useAuthStore()

  return (
    <header className="h-16 bg-dark-800/80 backdrop-blur-xl border-b border-dark-700/50 flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors lg:hidden"
        >
          <Menu size={20} />
        </button>
        <div className="relative hidden sm:block">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
          <input 
            type="text" 
            placeholder="Search tools, leads, reports..."
            className="pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-xl text-sm w-64 focus:outline-none focus:border-primary-500 transition-colors"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="relative p-2 rounded-xl bg-dark-700 hover:bg-dark-600 transition-colors">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="flex items-center gap-3">
          <span className="text-sm text-dark-400 hidden sm:block">{user?.plan || 'Free Plan'}</span>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-cyan-400 flex items-center justify-center text-sm font-bold">
            {user?.name?.[0] || 'U'}
          </div>
        </div>
      </div>
    </header>
  )
}