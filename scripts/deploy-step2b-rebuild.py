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
        for line in out.split('\n')[-15:]: print(f'    {line}')
    if err and 'warn' not in err.lower()[:30]:
        for line in err.split('\n')[-5:]:
            if line.strip(): print(f'    [e] {line[:150]}')
    return out

print('Connecting...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)

# Find bun
print('Finding bun...')
bun_path = run(ssh, 'which bun || find / -name bun -type f 2>/dev/null | head -3')
print(f'Bun at: {bun_path}')

# Start build in background with full PATH
print('Starting background build...')
run(ssh, f'cd /opt/eli/app && nohup bash -c "export PATH=$PATH:/root/.bun/bin && {bun_path.split(chr(10))[0]} install && NODE_OPTIONS=--max-old-space-size=4096 {bun_path.split(chr(10))[0]} run build && cp -r .next/static .next/standalone/.next/ && cp -r public .next/standalone/ && systemctl restart eli && echo BUILD_OK > /tmp/eli-build-status" > /tmp/eli-build.log 2>&1 &')

print('Build running. Waiting 120s...')
time.sleep(120)

print('Checking status...')
run(ssh, 'cat /tmp/eli-build-status 2>/dev/null || echo "STILL_RUNNING"')
print('Build log:')
run(ssh, 'tail -20 /tmp/eli-build.log 2>/dev/null')

status = run(ssh, 'cat /tmp/eli-build-status 2>/dev/null')
if 'BUILD_OK' in status:
    print('\nBUILD SUCCESS! Health check:')
    time.sleep(2)
    run(ssh, 'curl -s http://localhost:3000/api/health | python3 -m json.tool')
    print('\nVault chat test:')
    run(ssh, """curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message": "parasite SEO"}' | python3 -m json.tool | head -30""")
else:
    print('\nStill building. Wait or check VPS manually.')

ssh.close()