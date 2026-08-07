import paramiko, time, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=120)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:1200])
    if err: print(f'[e] {err[:500]}')
    return out

print('Testing Eli after config fix...')
result = run("""curl -s --max-time 90 http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{"message":"hey eli, what can you do?"}' """)

try:
    data = json.loads(result)
    resp = data.get('response', '')
    print(f'\n=== Eli says ===')
    print(resp[:1000])
except:
    print(f'Raw: {str(result)[:500]}')

print('\n=== Errors ===')
run('tail -3 /opt/eli/logs/eli-error.log')

ssh.close()