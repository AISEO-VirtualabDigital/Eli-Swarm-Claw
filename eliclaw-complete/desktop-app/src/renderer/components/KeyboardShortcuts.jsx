import { X, Command, CornerDownLeft } from 'lucide-react'
import { useEffect } from 'react'

export default function KeyboardShortcuts({ onClose }) {
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  const shortcuts = [
    { keys: ['Ctrl', 'N'], action: 'New SEO Audit' },
    { keys: ['Ctrl', 'D'], action: 'Open Dashboard' },
    { keys: ['Ctrl', ','], action: 'Open Settings' },
    { keys: ['Ctrl', 'Shift', 'K'], action: 'Search Everything' },
    { keys: ['Ctrl', 'Shift', '?'], action: 'Show Shortcuts' },
    { keys: ['Esc'], action: 'Close Modal / Go Back' },
    { keys: ['Ctrl', '1-6'], action: 'Switch between tools' },
    { keys: ['Ctrl', 'R'], action: 'Refresh Data' },
    { keys: ['Ctrl', 'E'], action: 'Export Report' },
    { keys: ['Ctrl', 'P'], action: 'Print Report' },
    { keys: ['Ctrl', '+'], action: 'Zoom In' },
    { keys: ['Ctrl', '-'], action: 'Zoom Out' },
    { keys: ['Ctrl', '0'], action: 'Reset Zoom' },
    { keys: ['F11'], action: 'Toggle Fullscreen' },
    { keys: ['Ctrl', 'M'], action: 'Minimize to Tray' },
    { keys: ['Ctrl', 'Q'], action: 'Quit EliClaw' },
  ]

  const platform = window.platform?.isMac ? 'mac' : 'win'
  const modifier = platform === 'mac' ? '⌘' : 'Ctrl'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="glass-panel p-6 max-w-lg w-full mx-4 animate-fade-in" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Command size={20} className="text-primary-400" />
            Keyboard Shortcuts
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-dark-700 rounded-lg transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {shortcuts.map((shortcut, i) => (
            <div key={i} className="flex items-center justify-between py-2 px-3 bg-dark-700/30 rounded-lg">
              <span className="text-sm text-dark-300">{shortcut.action}</span>
              <div className="flex items-center gap-1">
                {shortcut.keys.map((key, j) => (
                  <span key={j} className="kbd">
                    {key === 'Ctrl' ? modifier : key}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <p className="text-xs text-dark-500 mt-4 text-center">
          Press <kbd className="kbd">Esc</kbd> to close this dialog
        </p>
      </div>
    </div>
  )
}