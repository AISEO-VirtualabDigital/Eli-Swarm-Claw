import paramiko, time, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', username='root', password="2'E3,mCIm)W;rPD9", timeout=30)
sftp = ssh.open_sftp()

def r(c, t=60):
    print(f'$ {c[:120]}')
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

# 1. Upload ALL missing config files
print('=== Uploading configs ===')
configs = [
    ('/home/z/my-project/next.config.ts', '/opt/eli/app/next.config.ts'),
    ('/home/z/my-project/tsconfig.json', '/opt/eli/app/tsconfig.json'),
    ('/home/z/my-project/package.json', '/opt/eli/app/package.json'),
    ('/home/z/my-project/tailwind.config.ts', '/opt/eli/app/tailwind.config.ts'),
    ('/home/z/my-project/postcss.config.mjs', '/opt/eli/app/postcss.config.mjs'),
    ('/home/z/my-project/components.json', '/opt/eli/app/components.json'),
    ('/home/z/my-project/eslint.config.mjs', '/opt/eli/app/eslint.config.mjs'),
]
for local, remote in configs:
    if os.path.exists(local):
        sftp.put(local, remote)
        print(f'  {local.split("/")[-1]}')

# 2. Upload ALL src/ files
print('\n=== Uploading all src/ ===')
for root, dirs, files in os.walk('/home/z/my-project/src'):
    dirs[:] = [d for d in dirs if d != 'node_modules']
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, '/home/z/my-project/src')
        remote = f'/opt/eli/app/src/{rel}'
        rdir = os.path.dirname(remote)
        r(f'mkdir -p {rdir}')
        sftp.put(full, remote)
count = sum(1 for _ in os.walk('/home/z/my-project/src') for f in _[2])
print(f'  Uploaded {count} files')

# 3. Install deps
print('\n=== Installing deps ===')
r(f'cd /opt/eli/app && {BUN} install 2>&1 | tail -5', t=180)

# 4. Clean + Build
print('\n=== Building ===')
r('rm -rf /opt/eli/app/.next /opt/eli/app/node_modules/.cache')

# Build directly with next (not via package.json script)
ssh.exec_command(f'cd /opt/eli/app && nohup {BUN} x next build --no-turbopack > /tmp/eli-build3.log 2>&1 & echo $! > /tmp/eli-build3.pid')

print('Building (webpack, no turbopack)...')
for i in range(15):
    time.sleep(30)
    pid = r('cat /tmp/eli-build3.pid 2>/dev/null')
    status = r(f'kill -0 {pid} 2>/dev/null && echo RUNNING || echo DONE')
    if 'DONE' in status:
        break
    print(f'  ... {(i+1)*30}s')

print('\nBuild log tail:')
r('tail -20 /tmp/eli-build3.log')

build_ok = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')

if 'YES' in build_ok:
    print('\n=== Deploying ===')
    r('cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/')
    r('cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/')
    env = 'NODE_ENV=production\nPORT=3000\nDATABASE_URL=file:/opt/eli/data/custom.db\nKNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources\nOBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault\n'
    with sftp.open('/opt/eli/app/.next/standalone/.env', 'w') as f:
        f.write(env)
    r('systemctl restart eli')
    time.sleep(3)
    print('\nHealth:')
    r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
    print('\nChat test:')
    r("""curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message": "parasite SEO"}' | python3 -m json.tool | head -25""")
else:
    # If webpack also fails, try with turbopack
    print('\nWebpack failed too. Trying turbopack...')
    r('rm -rf /opt/eli/app/.next')
    ssh.exec_command(f'cd /opt/eli/app && nohup {BUN} x next build > /tmp/eli-build4.log 2>&1 & echo $! > /tmp/eli-build4.pid')
    for i in range(15):
        time.sleep(30)
        pid = r('cat /tmp/eli-build4.pid 2>/dev/null')
        status = r(f'kill -0 {pid} 2>/dev/null && echo RUNNING || echo DONE')
        if 'DONE' in status:
            break
    r('tail -20 /tmp/eli-build4.log')
    build_ok2 = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')
    if 'YES' in build_ok2:
        r('cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/')
        r('cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/')
        env = 'NODE_ENV=production\nPORT=3000\nDATABASE_URL=file:/opt/eli/data/custom.db\nKNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources\nOBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault\n'
        with sftp.open('/opt/eli/app/.next/standalone/.env', 'w') as f:
            f.write(env)
        r('systemctl restart eli')
        time.sleep(3)
        r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
    else:
        print('Both builds failed.')

sftp.close()
ssh.close()
print('Done.')