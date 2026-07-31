import { WifiOff, RefreshCw } from 'lucide-react'
import { useState } from 'react'

export default function OfflineBanner() {
  const [isRetrying, setIsRetrying] = useState(false)

  const handleRetry = () => {
    setIsRetrying(true)
    window.location.reload()
  }

  return (
    <div className="offline-banner flex items-center justify-center gap-2">
      <WifiOff size={14} />
      <span>You are offline. Some features may be limited.</span>
      <button 
        onClick={handleRetry}
        disabled={isRetrying}
        className="ml-2 flex items-center gap-1 text-yellow-400 hover:text-yellow-300 font-medium disabled:opacity-50"
      >
        <RefreshCw size={12} className={isRetrying ? 'animate-spin' : ''} />
        {isRetrying ? 'Retrying...' : 'Retry'}
      </button>
    </div>
  )
}