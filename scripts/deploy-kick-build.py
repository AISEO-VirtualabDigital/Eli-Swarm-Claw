import paramiko, time
VPS='177.7.49.44'
def r(c):
    _,o,e=paramiko.SSHClient().__getattribute__('exec_command' if False else '')
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS,username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
# Find bun
_,o,_=ssh.exec_command('which bun')
bun=o.read().decode().strip()
print(f'Bun: {bun}')
# Kick build
ssh.exec_command(f'cd /opt/eli/app && nohup bash -c "export PATH=$PATH:/root/.bun/bin && {bun} install 2>&1 && NODE_OPTIONS=--max-old-space-size=4096 {bun} run build 2>&1 && cp -r .next/static .next/standalone/.next/ && cp -r public .next/standalone/ && systemctl restart eli && echo BUILD_OK > /tmp/eli-build-status" > /tmp/eli-build.log 2>&1 &')
print('Build kicked. Waiting 60s...')
time.sleep(60)
_,o,_=ssh.exec_command('cat /tmp/eli-build-status 2>/dev/null')
s=o.read().decode().strip()
print(f'Status: {s or "still running"}')
_,o,_=ssh.exec_command('tail -10 /tmp/eli-build.log 2>/dev/null')
print('Log:', o.read().decode()[-500:])
if 'BUILD_OK' in s:
    time.sleep(2)
    _,o,_=ssh.exec_command('curl -s http://localhost:3000/api/health')
    print('Health:', o.read().decode()[:300])
ssh.close()
print('Done.')
