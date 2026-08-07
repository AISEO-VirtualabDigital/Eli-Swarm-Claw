import paramiko
import os
import time

VPS_HOST = '177.7.49.44'
VPS_USER = 'root'
VPS_PASS = "2'E3,mCIm)W;rPD9"

def run_cmd(ssh, cmd, timeout=120):
    print(f'  $ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        for line in out.split('\n')[:20]:
            print(f'    {line}')
    if err and 'warn' not in err.lower()[:30]:
        for line in err.split('\n')[:5]:
            if line.strip(): print(f'    [e] {line[:150]}')
    return out, err

print('='*60)
print('  ELI VAULT DEPLOYMENT — Micro-Chunk + Skill Containment')
print('='*60)

print('\n[1/5] Connecting to VPS...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
sftp = ssh.open_sftp()

# ─── Upload Vault ────────────────────────────────────────
print('\n[2/5] Uploading vault (13MB)...')
run_cmd(ssh, 'mkdir -p /opt/eli/data/eli-vault')

local_tar = '/tmp/eli-vault.tar.gz'
remote_tar = '/tmp/eli-vault.tar.gz'

# Check if local tar exists
if not os.path.exists(local_tar):
    print(f'  ERROR: {local_tar} not found. Run: cd /home/z/my-project/data/eli-vault && tar czf /tmp/eli-vault.tar.gz .')
    exit(1)

print(f'  Uploading {os.path.getsize(local_tar)/(1024*1024):.1f} MB...')
sftp.put(local_tar, remote_tar)
print('  Extracting...')
run_cmd(ssh, f'cd /opt/eli/data/eli-vault && rm -rf 00-Containment 01-Active 02-Skills 03-Index .vault-meta.json 2>/dev/null; tar xzf {remote_tar} && rm {remote_tar}')

# Verify vault
run_cmd(ssh, 'echo "Active: $(find /opt/eli/data/eli-vault/01-Active -name \'*.md\' | wc -l) chunks"')
run_cmd(ssh, 'echo "Containment: $(ls /opt/eli/data/eli-vault/00-Containment/ | wc -l) copies"')
run_cmd(ssh, 'echo "Skills: $(find /opt/eli/data/eli-vault/02-Skills -name \'*.md\' | wc -l) patterns"')
run_cmd(ssh, 'cat /opt/eli/data/eli-vault/03-Index/vault-index.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Index: {d[\"totalChunks\"]} chunks, {len(d[\"categories\"])} cats, {d[\"skills\"]} skills\")"')

# ─── Upload Source Files ────────────────────────────────
print('\n[3/5] Uploading updated source files...')

src_map = [
    ('/home/z/my-project/src/lib/vault-search.ts', '/opt/eli/app/src/lib/vault-search.ts'),
    ('/home/z/my-project/src/lib/air-llm.ts', '/opt/eli/app/src/lib/air-llm.ts'),
    ('/home/z/my-project/src/lib/obsidian-chunk-engine.ts', '/opt/eli/app/src/lib/obsidian-chunk-engine.ts'),
    ('/home/z/my-project/src/app/api/eli-chat/route.ts', '/opt/eli/app/src/app/api/eli-chat/route.ts'),
    ('/home/z/my-project/src/app/api/health/route.ts', '/opt/eli/app/src/app/api/health/route.ts'),
]

for local, remote in src_map:
    # Ensure remote dir exists
    remote_dir = os.path.dirname(remote)
    run_cmd(ssh, f'mkdir -p {remote_dir}')
    sftp.put(local, remote)
    print(f'  {os.path.basename(local)}')

# ─── Update .env ─────────────────────────────────────────
print('\n[4/5] Updating .env...')
run_cmd(ssh, 'cat /opt/eli/app/.env 2>/dev/null || echo ""')

# Just append vault path if missing
run_cmd(ssh, '''grep -q OBSIDIAN_VAULT_PATH /opt/eli/app/.env 2>/dev/null || echo "OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault" >> /opt/eli/app/.env''')
run_cmd(ssh, '''grep -q KNOWLEDGE_DIR /opt/eli/app/.env 2>/dev/null || echo "KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources" >> /opt/eli/app/.env''')
run_cmd(ssh, 'cat /opt/eli/app/.env')

# ─── Rebuild & Restart ──────────────────────────────────
print('\n[5/5] Rebuilding and restarting...')
run_cmd(ssh, 'cd /opt/eli/app && bun install --production 2>&1 | tail -3', timeout=120)
run_cmd(ssh, 'cd /opt/eli/app && NODE_OPTIONS="--max-old-space-size=4096" bun run build 2>&1 | tail -20', timeout=300)
run_cmd(ssh, 'cp -r /opt/eli/app/.next/static /opt/eli/app/.next/standalone/.next/ 2>/dev/null; cp -r /opt/eli/app/public /opt/eli/app/.next/standalone/ 2>/dev/null; echo done')
run_cmd(ssh, 'systemctl restart eli')
time.sleep(3)
run_cmd(ssh, 'systemctl status eli --no-pager | head -15')

print('\n--- Health Check ---')
run_cmd(ssh, 'curl -s http://localhost:3000/api/health | python3 -m json.tool')

print('\n--- Chat Test (no LLM — vault fallback) ---')
run_cmd(ssh, '''curl -s -X POST http://localhost:3000/api/eli-chat -H "Content-Type: application/json" -d '{"message": "what is parasite SEO"}' | python3 -m json.tool | head -30''')

sftp.close()
ssh.close()
print('\n' + '='*60)
print('  DEPLOYMENT COMPLETE')
print('='*60)
