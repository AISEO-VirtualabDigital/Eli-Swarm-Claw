import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

// Initialize desktop-specific features
if (window.eliclawAPI) {
  // Set up system event listeners
  window.eliclawAPI.onSystemSuspend(() => {
    console.log('System suspended - pausing background tasks');
  });

  window.eliclawAPI.onSystemResume(() => {
    console.log('System resumed - resuming background tasks');
  });

  // Log app start
  window.eliclawAPI.log('info', 'EliClaw Desktop renderer started');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <HashRouter>
      <App />
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#fff',
            border: '1px solid #334155'
          }
        }}
      />
    </HashRouter>
  </React.StrictMode>
)