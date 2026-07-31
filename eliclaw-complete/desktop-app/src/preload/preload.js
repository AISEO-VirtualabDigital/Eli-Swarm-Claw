const { contextBridge, ipcRenderer } = require('electron');

// Expose protected APIs to renderer process
contextBridge.exposeInMainWorld('eliclawAPI', {
  // App info
  getVersion: () => ipcRenderer.invoke('app:get-version'),
  restart: () => ipcRenderer.invoke('app:restart'),
  quit: () => ipcRenderer.invoke('app:quit'),

  // Settings
  getSetting: (key) => ipcRenderer.invoke('settings:get', key),
  setSetting: (key, value) => ipcRenderer.invoke('settings:set', key, value),
  getAllSettings: () => ipcRenderer.invoke('settings:get-all'),

  // Theme
  getTheme: () => ipcRenderer.invoke('theme:get'),
  setTheme: (theme) => ipcRenderer.invoke('theme:set', theme),

  // File dialogs
  openFile: () => ipcRenderer.invoke('dialog:open-file'),
  saveFile: (options) => ipcRenderer.invoke('dialog:save-file', options),

  // Notifications
  showNotification: (options) => ipcRenderer.invoke('notification:show', options),

  // Shell operations
  openExternal: (url) => ipcRenderer.invoke('shell:open-external', url),
  showItemInFolder: (path) => ipcRenderer.invoke('shell:show-item', path),

  // Clipboard
  writeToClipboard: (text) => ipcRenderer.invoke('clipboard:write', text),

  // Auto-launch
  setAutoLaunch: (enable) => ipcRenderer.invoke('auto-launch:set', enable),
  getAutoLaunch: () => ipcRenderer.invoke('auto-launch:get'),

  // Logging
  log: (level, message) => ipcRenderer.invoke('log:write', level, message),

  // System info
  getSystemInfo: () => ipcRenderer.invoke('system:get-info'),

  // Window controls
  minimizeWindow: () => ipcRenderer.invoke('window:minimize'),
  maximizeWindow: () => ipcRenderer.invoke('window:maximize'),
  closeWindow: () => ipcRenderer.invoke('window:close'),

  // Event listeners
  onNavigate: (callback) => ipcRenderer.on('navigate-to', callback),
  onSystemSuspend: (callback) => ipcRenderer.on('system-suspend', callback),
  onSystemResume: (callback) => ipcRenderer.on('system-resume', callback),

  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Expose platform info
contextBridge.exposeInMainWorld('platform', {
  isMac: process.platform === 'darwin',
  isWindows: process.platform === 'win32',
  isLinux: process.platform === 'linux'
});