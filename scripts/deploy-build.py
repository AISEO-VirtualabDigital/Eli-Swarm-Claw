import paramiko, time

VPS = '177.7.49.44'
BUN = '/root/.bun/bin/bun'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS, username='root', password="2'E3,mCIm)W;rPD9", timeout=30)
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

# Clean and build
r('rm -rf /opt/eli/app/.next /opt/eli/app/node_modules/.cache')
ssh.exec_command(f'cd /opt/eli/app && nohup {BUN} x next build > /tmp/eli-b.log 2>&1 & echo $! > /tmp/eli-b.pid')

print('Building with turbopack...')
for i in range(15):
    time.sleep(30)
    pid = r('cat /tmp/eli-b.pid 2>/dev/null')
    st = r(f'kill -0 {pid} 2>/dev/null && echo RUNNING || echo DONE')
    if 'DONE' in st: break
    print(f'  {(i+1)*30}s...')

r('tail -20 /tmp/eli-b.log')
ok = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')

if 'YES' in ok:
    print('\n=== DEPLOY ===')
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
    print('\nBuild still failed. Full log:')
    r('cat /tmp/eli-b.log | head -50')

sftp.close()
ssh.close()
print('Done.')