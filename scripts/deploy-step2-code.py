import paramiko
import time

VPS_HOST = '177.7.49.44'
VPS_USER = 'root'
VPS_PASS = "2'E3,mCIm)W;rPD9"

def run(ssh, cmd, t=120):
    print(f'  $ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        for line in out.split('\n')[:20]: print(f'    {line}')
    if err and 'warn' not in err.lower()[:30]:
        for line in err.split('\n')[:5]:
            if line.strip(): print(f'    [e] {line[:150]}')
    return out

print('Connecting...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
sftp = ssh.open_sftp()

# Upload source files
print('Uploading source files...')
files = [
    ('/home/z/my-project/src/lib/vault-search.ts', '/opt/eli/app/src/lib/vault-search.ts'),
    ('/home/z/my-project/src/lib/air-llm.ts', '/opt/eli/app/src/lib/air-llm.ts'),
    ('/home/z/my-project/src/lib/obsidian-chunk-engine.ts', '/opt/eli/app/src/lib/obsidian-chunk-engine.ts'),
    ('/home/z/my-project/src/app/api/eli-chat/route.ts', '/opt/eli/app/src/app/api/eli-chat/route.ts'),
    ('/home/z/my-project/src/app/api/health/route.ts', '/opt/eli/app/src/app/api/health/route.ts'),
]

for local, remote in files:
    run(ssh, f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    print(f'  OK: {local.split("/")[-1]}')

# Update .env
print('Updating .env...')
run(ssh, 'grep -q OBSIDIAN_VAULT_PATH /opt/eli/app/.env 2>/dev/null || echo "OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault" >> /opt/eli/app/.env')
run(ssh, 'grep -q KNOWLEDGE_DIR /opt/eli/app/.env 2>/dev/null || echo "KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources" >> /opt/eli/app/.env')
run(ssh, 'cat /opt/eli/app/.env')

# Rebuild
print('Rebuilding...')
run(ssh, 'cd /opt/eli/app && bun install --production 2>&1 | tail -5', t=180)
run(ssh, 'cd /opt/eli/app && NODE_OPTIONS="--max-old-space-size=4096" bun run build 2>&1 | tail -20', t=300)

# Deploy standalone
run(ssh, 'cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/ 2>/dev/null; cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/ 2>/dev/null; echo "deployed"')

# Restart
print('Restarting Eli...')
run(ssh, 'systemctl restart eli')
time.sleep(3)
run(ssh, 'systemctl status eli --no-pager | head -12')

print('Health check...')
run(ssh, 'curl -s http://localhost:3000/api/health | python3 -m json.tool')

print('Chat test...')
run(ssh, """curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message": "what is parasite SEO"}' | python3 -m json.tool | head -30""")

sftp.close()
ssh.close()
print('DONE!')
