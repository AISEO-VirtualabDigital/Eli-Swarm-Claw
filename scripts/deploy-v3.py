import paramiko, time

VPS='177.7.49.44'
BUN='/root/.bun/bin/bun'

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS,username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
sftp=ssh.open_sftp()

def r(c,t=60):
    print(f'$ {c[:120]}')
    stdin,stdout,stderr = ssh.exec_command(c,timeout=t)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        for l in out.split('\n')[-10:]: print(f'  {l}')
    return out

# Upload source
print('Uploading source...')
sftp.put('/tmp/eli-src.tar.gz','/tmp/eli-src.tar.gz')
r('cd /opt/eli/app && tar xzf /tmp/eli-src.tar.gz && rm /tmp/eli-src.tar.gz')

# Upload search index parts
print('Uploading search index...')
sftp.put('/tmp/eli-vault-parts.tar.gz','/tmp/eli-vault-parts.tar.gz')
r('cd /opt/eli/data/eli-vault && tar xzf /tmp/eli-vault-parts.tar.gz && rm /tmp/eli-vault-parts.tar.gz')

# Build
print('Starting build (waiting 5 min)...')
r('rm -rf /opt/eli/app/.next')
ssh.exec_command(f'cd /opt/eli/app && nohup {BUN} x next build > /tmp/eli-b.log 2>&1 & echo $! > /tmp/eli-b.pid')
time.sleep(300)

r('tail -10 /tmp/eli-b.log')
ok = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')

if 'YES' in ok:
    print('\n=== DEPLOY ===')
    r('cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/')
    r('cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/')
    env = 'NODE_ENV=production\nPORT=3000\nDATABASE_URL=file:/opt/eli/data/custom.db\nKNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources\nOBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault\n'
    with sftp.open('/opt/eli/app/.next/standalone/.env','w') as f:
        f.write(env)
    r('systemctl restart eli')
    time.sleep(3)
    print('Health:')
    r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
    print('Chat test:')
    r("curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{\"message\": \"parasite SEO\"}' | python3 -m json.tool | head -30")
else:
    print('Build not ready yet')

sftp.close()
ssh.close()
print('Done.')
