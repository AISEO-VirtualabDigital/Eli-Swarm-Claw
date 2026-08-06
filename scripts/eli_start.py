import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:100]}')
    i, o, e = ssh.exec_command(cmd, timeout=30)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:500])
    if err: print(f'[e] {err[:300]}')
    return out

run('systemctl daemon-reload && systemctl enable eli')
run('systemctl restart eli')
time.sleep(4)
status = run('systemctl is-active eli')
print(f'Eli status: {status}')

health = run('curl -sf http://localhost:3000/api/health')
print(f'Health: {health}')

run('systemctl restart caddy')
time.sleep(2)
cstatus = run('systemctl is-active caddy')
print(f'Caddy status: {cstatus}')

ssh.close()
print('Done.')
