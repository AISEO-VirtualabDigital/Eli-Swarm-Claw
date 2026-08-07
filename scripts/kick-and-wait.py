import paramiko, time

VPS='177.7.49.44'
BUN='/root/.bun/bin/bun'

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS,username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
sftp=ssh.open_sftp()

def r(c):
    _,o,_=ssh.exec_command(c,timeout=60)
    return o.read().decode().strip()

# Upload
print('Uploading...')
sftp.put('/tmp/eli-src.tar.gz','/tmp/eli-src.tar.gz')
r('cd /opt/eli/app && tar xzf /tmp/eli-src.tar.gz && rm /tmp/eli-src.tar.gz')
sftp.put('/tmp/eli-vault-parts.tar.gz','/tmp/eli-vault-parts.tar.gz')
r('cd /opt/eli/data/eli-vault && tar xzf /tmp/eli-vault-parts.tar.gz && rm /tmp/eli-vault-parts.tar.gz')

# Build
print('Building (4min wait)...')
r('rm -rf /opt/eli/app/.next')
ssh.exec_command('cd /opt/eli/app && nohup /root/.bun/bin/bun x next build > /tmp/eli-b.log 2>&1 & echo $! > /tmp/eli-b.pid')

for i in range(4):
    time.sleep(60)
    st = r('kill -0 $(cat /tmp/eli-b.pid) 2>/dev/null && echo RUNNING || echo DONE')
    if 'DONE' in st:
        break
    print(f'  {(i+1)*60}s...')

r('tail -5 /tmp/eli-b.log')
ok = r('ls /opt/eli/app/.next/standalone/server.js 2>/dev/null && echo YES || echo NO')

if 'YES' in ok:
    print('Deploying...')
    r('cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/')
    r('cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/')
    env_lines = ['NODE_ENV=production', 'PORT=3000', 'DATABASE_URL=file:/opt/eli/data/custom.db',
                'KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources', 'OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault']
    with sftp.open('/opt/eli/app/.next/standalone/.env', 'w') as f:
        f.write('\n'.join(env_lines) + '\n')
    r('systemctl restart eli')
    time.sleep(3)
    print('Health:')
    r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
    print('Chat:')
    chat_cmd = "curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{ \"message\": \"parasite SEO\" }' | python3 -m json.tool | head -30"
    r(chat_cmd)
else:
    print('Build not done.')
    r('tail -3 /tmp/eli-b.log')

sftp.close()
ssh.close()
print('Done.')
