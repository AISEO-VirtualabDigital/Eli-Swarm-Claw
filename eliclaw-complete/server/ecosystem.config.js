module.exports = {
  apps: [{
    name: 'eliclaw-api',
    script: 'server-enhanced.js',
    instances: 'max', // Use all CPU cores
    exec_mode: 'cluster',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/error.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss',
    merge_logs: true,
    restart_delay: 4000,
    min_uptime: '10s',
    max_restarts: 10
  }]
};
