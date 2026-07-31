const { app, BrowserWindow, ipcMain, dialog, shell, nativeTheme, Tray, Menu, Notification, powerMonitor } = require('electron');
const path = require('path');
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');

// Initialize store for settings
const store = new Store({
  name: 'eliclaw-config',
  defaults: {
    windowBounds: { width: 1400, height: 900, x: undefined, y: undefined },
    theme: 'dark',
    apiUrl: 'https://api.eliclaw.virtualabdigital.com',
    offlineMode: false,
    notifications: true,
    autoLaunch: false,
    minimizeToTray: true,
    hardwareAcceleration: true
  }
});

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Global references to prevent garbage collection
let mainWindow = null;
let tray = null;
let isQuitting = false;

// App metadata
const APP_NAME = 'EliClaw';
const APP_VERSION = app.getVersion();

// Create main window
function createMainWindow() {
  const bounds = store.get('windowBounds');

  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    x: bounds.x,
    y: bounds.y,
    minWidth: 1000,
    minHeight: 700,
    title: APP_NAME,
    show: false, // Show when ready
    backgroundColor: '#0f172a',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    trafficLightPosition: process.platform === 'darwin' ? { x: 15, y: 15 } : undefined,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, '../preload/preload.js'),
      sandbox: false,
      allowRunningInsecureContent: false,
      experimentalFeatures: false
    },
    icon: path.join(__dirname, '../../assets/icons/icon.png'),
    frame: process.platform !== 'darwin', // Custom frame on Windows/Linux
    ...(process.platform === 'win32' && {
      titleBarOverlay: {
        color: '#0f172a',
        symbolColor: '#ffffff',
        height: 40
      }
    })
  });

  // Load app
  const isDev = !app.isPackaged;
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../dist-renderer/index.html'));
  }

  // Window events
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();

    // Check for updates on startup (production only)
    if (!isDev) {
      autoUpdater.checkForUpdatesAndNotify();
    }
  });

  mainWindow.on('close', (event) => {
    if (!isQuitting && store.get('minimizeToTray') && process.platform !== 'darwin') {
      event.preventDefault();
      mainWindow.hide();
      return;
    }

    // Save window bounds
    store.set('windowBounds', mainWindow.getBounds());
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.on('resize', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  mainWindow.on('move', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  return mainWindow;
}

// Create system tray
function createTray() {
  const iconPath = path.join(__dirname, '../../assets/icons/tray-icon.png');
  tray = new Tray(iconPath);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open EliClaw',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        } else {
          createMainWindow();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Run Quick Audit',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate-to', '/tools/seo');
        }
      }
    },
    {
      label: 'View Dashboard',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.webContents.send('navigate-to', '/dashboard');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Check for Updates',
      click: () => {
        autoUpdater.checkForUpdatesAndNotify();
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('EliClaw — AI-Powered Digital Growth');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    } else {
      createMainWindow();
    }
  });

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// App event handlers
app.whenReady().then(() => {
  log.info(`EliClaw v${APP_VERSION} starting...`);

  createMainWindow();
  createTray();

  // macOS dock
  if (process.platform === 'darwin') {
    app.dock.setIcon(path.join(__dirname, '../../assets/icons/icon.png'));
    app.dock.setMenu(Menu.buildFromTemplate([
      {
        label: 'New Audit',
        click: () => {
          if (mainWindow) {
            mainWindow.webContents.send('navigate-to', '/tools/seo');
          }
        }
      },
      {
        label: 'New Competitor Analysis',
        click: () => {
          if (mainWindow) {
            mainWindow.webContents.send('navigate-to', '/tools/competitor');
          }
        }
      }
    ]));
  }

  // Power monitoring for background tasks
  powerMonitor.on('suspend', () => {
    log.info('System suspending - pausing background tasks');
    if (mainWindow) {
      mainWindow.webContents.send('system-suspend');
    }
  });

  powerMonitor.on('resume', () => {
    log.info('System resuming - resuming background tasks');
    if (mainWindow) {
      mainWindow.webContents.send('system-resume');
    }
  });

  // Auto-updater events
  autoUpdater.on('checking-for-update', () => {
    log.info('Checking for updates...');
  });

  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info.version);
    new Notification({
      title: 'EliClaw Update Available',
      body: `Version ${info.version} is ready to install.`,
      icon: path.join(__dirname, '../../assets/icons/icon.png')
    }).show();
  });

  autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info.version);
    new Notification({
      title: 'EliClaw Update Ready',
      body: 'Restart to install the latest version.',
      icon: path.join(__dirname, '../../assets/icons/icon.png')
    }).show();

    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: `EliClaw ${info.version} has been downloaded.`,
      detail: 'The application will restart to complete the installation.',
      buttons: ['Restart Now', 'Later'],
      defaultId: 0
    }).then(({ response }) => {
      if (response === 0) {
        autoUpdater.quitAndInstall(false, true);
      }
    });
  });

  autoUpdater.on('error', (err) => {
    log.error('Auto-updater error:', err);
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  } else if (mainWindow) {
    mainWindow.show();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
});

// IPC Handlers

// Get app version
ipcMain.handle('app:get-version', () => {
  return APP_VERSION;
});

// Get/store settings
ipcMain.handle('settings:get', (event, key) => {
  return store.get(key);
});

ipcMain.handle('settings:set', (event, key, value) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('settings:get-all', () => {
  return store.store;
});

// Native theme
ipcMain.handle('theme:get', () => {
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
});

ipcMain.handle('theme:set', (event, theme) => {
  nativeTheme.themeSource = theme;
  return theme;
});

// File operations
ipcMain.handle('dialog:open-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

ipcMain.handle('dialog:save-file', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: options.defaultPath || 'eliclaw-export.csv',
    filters: options.filters || [
      { name: 'CSV', extensions: ['csv'] },
      { name: 'PDF', extensions: ['pdf'] },
      { name: 'JSON', extensions: ['json'] }
    ]
  });
  return result;
});

// Show notification
ipcMain.handle('notification:show', (event, { title, body, silent = false }) => {
  const notification = new Notification({
    title: title || 'EliClaw',
    body: body || '',
    icon: path.join(__dirname, '../../assets/icons/icon.png'),
    silent
  });

  notification.on('click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  notification.show();
  return true;
});

// Open external URL
ipcMain.handle('shell:open-external', (event, url) => {
  shell.openExternal(url);
  return true;
});

// Open path in folder
ipcMain.handle('shell:show-item', (event, fullPath) => {
  shell.showItemInFolder(fullPath);
  return true;
});

// Clipboard
ipcMain.handle('clipboard:write', (event, text) => {
  const { clipboard } = require('electron');
  clipboard.writeText(text);
  return true;
});

// Auto-launch
ipcMain.handle('auto-launch:set', async (event, enable) => {
  const AutoLaunch = require('auto-launch');
  const autoLauncher = new AutoLaunch({
    name: APP_NAME,
    path: app.getPath('exe')
  });

  if (enable) {
    await autoLauncher.enable();
  } else {
    await autoLauncher.disable();
  }

  store.set('autoLaunch', enable);
  return true;
});

// Check auto-launch status
ipcMain.handle('auto-launch:get', async () => {
  return store.get('autoLaunch');
});

// Log to file
ipcMain.handle('log:write', (event, level, message) => {
  log[level](message);
  return true;
});

// Get system info
ipcMain.handle('system:get-info', () => {
  return {
    platform: process.platform,
    arch: process.arch,
    version: os.release(),
    totalMemory: os.totalmem(),
    freeMemory: os.freemem(),
    cpus: os.cpus().length,
    hostname: os.hostname(),
    uptime: os.uptime()
  };
});

// Restart app
ipcMain.handle('app:restart', () => {
  app.relaunch();
  app.quit();
  return true;
});

// Quit app
ipcMain.handle('app:quit', () => {
  isQuitting = true;
  app.quit();
  return true;
});

// Minimize to tray
ipcMain.handle('window:minimize', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
  return true;
});

ipcMain.handle('window:maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
  return true;
});

ipcMain.handle('window:close', () => {
  if (mainWindow) {
    if (store.get('minimizeToTray')) {
      mainWindow.hide();
    } else {
      mainWindow.close();
    }
  }
  return true;
});

// Handle renderer crashes
app.on('render-process-gone', (event, webContents, details) => {
  log.error('Renderer process gone:', details);
  dialog.showErrorBox(
    'EliClaw Error',
    `The application encountered an error and needs to restart.\n\nReason: ${details.reason}`
  );
});

// Security: prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});