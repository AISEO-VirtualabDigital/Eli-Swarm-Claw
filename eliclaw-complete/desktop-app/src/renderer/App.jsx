import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuthStore } from './context/authStore'
import TitleBar from './components/TitleBar'
import Layout from './components/Layout'
import OfflineBanner from './components/OfflineBanner'
import UpdateBanner from './components/UpdateBanner'
import KeyboardShortcuts from './components/KeyboardShortcuts'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import SEOTool from './pages/SEOTool'
import CompetitorTool from './pages/CompetitorTool'
import WebsiteAnalyzer from './pages/WebsiteAnalyzer'
import AutomationTool from './pages/AutomationTool'
import ContentTool from './pages/ContentTool'
import SwarmAgent from './pages/SwarmAgent'
import Login from './pages/Login'
import Register from './pages/Register'
import Settings from './pages/Settings'
import Leads from './pages/Leads'
import PricingPage from './pages/PricingPage'

function App() {
  const { user } = useAuthStore()
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [updateAvailable, setUpdateAvailable] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Listen for update availability from main process
    if (window.eliclawAPI) {
      window.eliclawAPI.onNavigate((event, path) => {
        window.location.hash = path;
      });
    }

    // Keyboard shortcuts
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + Shift + K = Keyboard shortcuts
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'K') {
        e.preventDefault();
        setShowShortcuts(true);
      }

      // Cmd/Ctrl + N = New Audit
      if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault();
        window.location.hash = '/tools/seo';
      }

      // Cmd/Ctrl + D = Dashboard
      if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
        e.preventDefault();
        window.location.hash = '/dashboard';
      }

      // Cmd/Ctrl + , = Settings
      if ((e.metaKey || e.ctrlKey) && e.key === ',') {
        e.preventDefault();
        window.location.hash = '/settings';
      }

      // Cmd/Ctrl + Shift + ? = Shortcuts
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === '?') {
        e.preventDefault();
        setShowShortcuts(true);
      }

      // Escape = Close modals
      if (e.key === 'Escape') {
        setShowShortcuts(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  return (
    <div className="h-screen flex flex-col bg-dark-900">
      {/* Native Title Bar */}
      <TitleBar />

      {/* Offline Banner */}
      {!isOnline && <OfflineBanner />}

      {/* Update Banner */}
      {updateAvailable && (
        <UpdateBanner onClick={() => setUpdateAvailable(false)} />
      )}

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <KeyboardShortcuts onClose={() => setShowShortcuts(false)} />
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
          <Route path="/pricing" element={<PricingPage />} />

          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tools/seo" element={<SEOTool />} />
            <Route path="/tools/competitor" element={<CompetitorTool />} />
            <Route path="/tools/analyzer" element={<WebsiteAnalyzer />} />
            <Route path="/tools/automation" element={<AutomationTool />} />
            <Route path="/tools/content" element={<ContentTool />} />
            <Route path="/tools/swarm" element={<SwarmAgent />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </div>
    </div>
  )
}

export default App