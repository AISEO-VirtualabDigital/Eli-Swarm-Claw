import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd, timeout=90):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=timeout)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:1200])
    if err: print(f'[e] {err[:500]}')
    return out

# Check if service restarted
run('systemctl is-active eli')

# Test with longer timeout
print('Testing Eli...')
result = run("""curl -s --max-time 60 http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message":"hey eli, what can you do?"}' """, timeout=120)

try:
    data = json.loads(result)
    print(f"\n=== Eli's response ===")
    print(data.get('response', result)[:800])
except:
    print(f'Raw: {result[:500]}')

# Check error log
print('\n=== Error log ===')
run('tail -5 /opt/eli/logs/eli-error.log')

ssh.close()