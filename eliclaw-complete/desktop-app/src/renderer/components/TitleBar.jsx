import { useState, useEffect } from 'react'
import { Minus, Square, X, Menu, Search, Bell, Wifi, WifiOff } from 'lucide-react'

export default function TitleBar() {
  const [isMaximized, setIsMaximized] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [showMenu, setShowMenu] = useState(false)
  const [platform, setPlatform] = useState('win')

  useEffect(() => {
    if (window.platform) {
      setPlatform(window.platform.isMac ? 'mac' : window.platform.isLinux ? 'linux' : 'win')
    }

    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const handleMinimize = () => {
    if (window.eliclawAPI) window.eliclawAPI.minimizeWindow()
  }

  const handleMaximize = () => {
    if (window.eliclawAPI) {
      window.eliclawAPI.maximizeWindow()
      setIsMaximized(!isMaximized)
    }
  }

  const handleClose = () => {
    if (window.eliclawAPI) window.eliclawAPI.closeWindow()
  }

  // macOS style (traffic lights on left, hidden title bar)
  if (platform === 'mac') {
    return (
      <div className="h-8 bg-dark-900/80 backdrop-blur-xl border-b border-dark-700/30 flex items-center justify-center relative select-none">
        <div className="absolute left-4 flex items-center gap-2 no-drag">
          <button 
            onClick={handleClose}
            className="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors"
            title="Close"
          />
          <button 
            onClick={handleMinimize}
            className="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors"
            title="Minimize"
          />
          <button 
            onClick={handleMaximize}
            className="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors"
            title="Maximize"
          />
        </div>
        <span className="text-sm font-medium text-dark-400">EliClaw</span>
        <div className="absolute right-4 flex items-center gap-3 no-drag">
          {isOnline ? <Wifi size={14} className="text-green-400" /> : <WifiOff size={14} className="text-red-400" />}
        </div>
      </div>
    )
  }

  // Windows/Linux style (custom title bar)
  return (
    <div className="h-10 bg-dark-900/80 backdrop-blur-xl border-b border-dark-700/30 flex items-center justify-between select-none drag-region">
      {/* Left: Logo & Menu */}
      <div className="flex items-center gap-3 px-4 no-drag">
        <div className="w-6 h-6 bg-gradient-to-br from-primary-500 to-cyan-400 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-xs">E</span>
        </div>
        <span className="font-semibold text-sm">EliClaw</span>

        {/* App Menu */}
        <div className="relative ml-4">
          <button 
            onClick={() => setShowMenu(!showMenu)}
            className="p-1.5 hover:bg-dark-700 rounded-lg transition-colors"
          >
            <Menu size={16} />
          </button>

          {showMenu && (
            <div className="desktop-menu" onMouseLeave={() => setShowMenu(false)}>
              <div className="desktop-menu-item" onClick={() => { window.location.hash = '/dashboard'; setShowMenu(false); }}>
                Dashboard <span className="ml-auto kbd">Ctrl+D</span>
              </div>
              <div className="desktop-menu-item" onClick={() => { window.location.hash = '/tools/seo'; setShowMenu(false); }}>
                New Audit <span className="ml-auto kbd">Ctrl+N</span>
              </div>
              <div className="desktop-menu-separator" />
              <div className="desktop-menu-item" onClick={() => { window.location.hash = '/settings'; setShowMenu(false); }}>
                Settings <span className="ml-auto kbd">Ctrl+,</span>
              </div>
              <div className="desktop-menu-separator" />
              <div className="desktop-menu-item" onClick={() => { window.location.hash = '/pricing'; setShowMenu(false); }}>
                Upgrade to Pro
              </div>
              <div className="desktop-menu-separator" />
              <div className="desktop-menu-item text-red-400" onClick={() => { if (window.eliclawAPI) window.eliclawAPI.quit(); }}>
                Quit EliClaw
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-md mx-4 no-drag">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-dark-500" />
          <input 
            type="text" 
            placeholder="Search tools, leads, reports... (Ctrl+K)"
            className="w-full h-7 bg-dark-800 border border-dark-600 rounded-lg pl-9 pr-4 text-sm focus:outline-none focus:border-primary-500 transition-colors"
          />
        </div>
      </div>

      {/* Right: Status & Controls */}
      <div className="flex items-center gap-2 px-2 no-drag">
        <div className="flex items-center gap-2 mr-2">
          {isOnline ? (
            <Wifi size={14} className="text-green-400" title="Online" />
          ) : (
            <WifiOff size={14} className="text-red-400" title="Offline" />
          )}
          <button className="p-1.5 hover:bg-dark-700 rounded-lg transition-colors relative">
            <Bell size={16} className="text-dark-400" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
        </div>

        <div className="win-controls border-l border-dark-700 pl-2">
          <button onClick={handleMinimize} className="win-control-btn" title="Minimize">
            <Minus size={16} />
          </button>
          <button onClick={handleMaximize} className="win-control-btn" title={isMaximized ? "Restore" : "Maximize"}>
            <Square size={14} />
          </button>
          <button onClick={handleClose} className="win-control-btn hover:bg-red-500/20 hover:text-red-400" title="Close">
            <X size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}