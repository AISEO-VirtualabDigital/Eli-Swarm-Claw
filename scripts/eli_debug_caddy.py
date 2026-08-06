import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=30)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:800])
    if err: print(f'[e] {err[:500]}')
    return out

run('journalctl -u caddy --no-pager -n 30')
print('---')
run('caddy validate --config /etc/caddy/Caddyfile 2>&1')
print('---')
run('cat /etc/caddy/Caddyfile')

ssh.close()