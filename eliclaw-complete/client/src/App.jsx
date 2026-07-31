import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './context/authStore'
import Layout from './components/Layout'
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

function App() {
  const { user } = useAuthStore()

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />

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
  )
}

export default App