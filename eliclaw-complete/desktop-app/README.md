# EliClaw Desktop

Cross-platform desktop application for EliClaw Agent OS.

## Features

- **Native Performance** — Built with Electron for fast, responsive experience
- **Offline Support** — Work without internet, sync when connected
- **System Tray** — Minimize to tray, quick access from taskbar
- **Auto-Updates** — Automatic updates via electron-updater
- **Keyboard Shortcuts** — Power-user shortcuts for all actions
- **Native Notifications** — Desktop notifications for alerts and reports
- **File System Access** — Export/import data, save reports locally
- **Hardware Acceleration** — GPU-accelerated rendering
- **Dark/Light/System Theme** — Match your OS theme

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build renderer only
npm run build:renderer

# Build for production
npm run build
```

## Building for Distribution

### Windows
```bash
npm run build:win
# Output: dist/EliClaw-Setup.exe, dist/EliClaw-Portable.exe
```

### macOS
```bash
npm run build:mac
# Output: dist/EliClaw.dmg, dist/EliClaw.zip
```

### Linux
```bash
npm run build:linux
# Output: dist/EliClaw.AppImage, dist/eliclaw.deb, dist/eliclaw.rpm
```

### All Platforms
```bash
./scripts/build.sh all
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New SEO Audit |
| `Ctrl/Cmd + D` | Open Dashboard |
| `Ctrl/Cmd + ,` | Open Settings |
| `Ctrl/Cmd + Shift + K` | Search Everything |
| `Ctrl/Cmd + Shift + ?` | Show Shortcuts |
| `Esc` | Close Modal / Go Back |
| `Ctrl/Cmd + E` | Export Report |
| `Ctrl/Cmd + P` | Print Report |
| `F11` | Toggle Fullscreen |
| `Ctrl/Cmd + Q` | Quit EliClaw |

## Architecture

```
desktop-app/
├── src/
│   ├── main/           # Electron main process
│   │   └── main.js     # Window management, IPC, auto-updater
│   ├── preload/        # Secure bridge between main and renderer
│   │   └── preload.js  # ContextBridge API exposure
│   └── renderer/       # React frontend (same as web app)
│       ├── components/ # Desktop-specific components
│       ├── pages/      # Tool pages
│       └── App.jsx     # Desktop app entry
├── assets/             # Icons, images
├── build/              # Build configuration
└── scripts/            # Build scripts
```

## Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
ELICLAW_API_URL=https://api.eliclaw.virtualabdigital.com

# Auto-Updater (GitHub releases)
GH_TOKEN=your_github_token

# Sentry (error tracking)
SENTRY_DSN=your_sentry_dsn
```

## License

Copyright © 2026 Virtualab Digital. All rights reserved.