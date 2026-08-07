import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', username='root', password="2'E3,mCIm)W;rPD9", timeout=30)
sftp = ssh.open_sftp()

def r(c, t=60):
    print(f'$ {c[:100]}')
    _, o, e = ssh.exec_command(c, timeout=t)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out:
        for l in out.split('\n')[-10:]: print(f'  {l}')
    if err and 'warn' not in err.lower()[:20]:
        for l in err.split('\n')[-3:]:
            if l.strip(): print(f'  [e] {l[:120]}')
    return out

BUN = '/root/.bun/bin/bun'

# 1. Fix systemd to include vault path
print('=== Fixing systemd service ===')
service = '''[Unit]
Description=Eli MicroSaaS - AI Growth Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/eli/app/.next/standalone
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=DATABASE_URL=file:/opt/eli/data/custom.db
Environment=KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources
Environment=OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault
ExecStart=/root/.bun/bin/bun server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
'''

with sftp.open('/etc/systemd/system/eli.service', 'w') as f:
    f.write(service)
r('systemctl daemon-reload')

# 2. Build
print('\n=== Building ===')
# Clean old build first
r('rm -rf /opt/eli/app/.next')
r(f'cd /opt/eli/app && {BUN} install 2>&1 | tail -5', t=180)

# Start build in background
print('Starting build (background)...')
ssh.exec_command(f'cd /opt/eli/app && nohup {BUN} run build > /tmp/eli-build.log 2>&1 & echo $! > /tmp/eli-build.pid')

print('Waiting for build (checking every 30s)...')
for i in range(10):  # up to 5 minutes
    time.sleep(30)
    pid = r('cat /tmp/eli-build.pid 2>/dev/null')
    running = r(f'kill -0 {pid} 2>/dev/null && echo RUNNING || echo DONE')
    if 'DONE' in running:
        break
    r('tail -3 /tmp/eli-build.log')
    print(f'  ... still building ({(i+1)*30}s)')

print('\nBuild log tail:')
r('tail -15 /tmp/eli-build.log')

# Check if build output exists
build_ok = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')

if 'YES' in build_ok:
    print('\nBuild succeeded! Deploying...')
    r('cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/')
    r('cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/')
    # Write .env to standalone
    env = 'NODE_ENV=production\nPORT=3000\nDATABASE_URL=file:/opt/eli/data/custom.db\nKNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources\nOBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault\n'
    with sftp.open('/opt/eli/app/.next/standalone/.env', 'w') as f:
        f.write(env)
    r('systemctl restart eli')
    time.sleep(3)
    print('\n=== Health Check ===')
    r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
    print('\n=== Vault Chat Test ===')
    r("""curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message": "parasite SEO"}' | python3 -m json.tool | head -25""")
else:
    print('\nBuild not complete yet. Check: ssh root@177.7.49.44 "tail -20 /tmp/eli-build.log"')

sftp.close()
ssh.close()
print('\nDone.')
