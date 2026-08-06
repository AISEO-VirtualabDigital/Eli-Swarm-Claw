import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

sftp = ssh.open_sftp()

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=15)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:500])
    if err: print(f'[e] {err[:300]}')
    return out

# Check what's there
run('ls -la /etc/.z-ai-config 2>/dev/null || echo MISSING')
run('ls -la /opt/eli/app/.z-ai-config 2>/dev/null || echo MISSING')
run('ls -la /root/.z-ai-config 2>/dev/null || echo MISSING')

# Upload fresh to all 3 locations
sftp.put('/etc/.z-ai-config', '/etc/.z-ai-config')
sftp.put('/etc/.z-ai-config', '/root/.z-ai-config')
sftp.put('/etc/.z-ai-config', '/opt/eli/app/.z-ai-config')
print('Uploaded to all 3 locations')

# Verify content
run('cat /etc/.z-ai-config | head -1')
run('wc -c /etc/.z-ai-config /root/.z-ai-config /opt/eli/app/.z-ai-config')

# Restart eli
run('systemctl restart eli')
time.sleep(3)
run('systemctl is-active eli')

# Wait a moment then test
print('Waiting for cold start...')
time.sleep(2)

result = run("""curl -s --max-time 90 http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message":"hey eli, what can you do?"}' """, timeout=120)

try:
    data = json.loads(result)
    resp = data.get('response', '')
    print(f'\n=== Eli says ===')
    print(resp[:1000])
except:
    print(f'Raw: {str(result)[:500]}')

print('\n=== Errors ===')
run('tail -3 /opt/eli/logs/eli-error.log')

sftp.close()
ssh.close()
