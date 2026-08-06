import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=30)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:600])
    if err: print(f'[e] {err[:400]}')
    return out

# Check DNS from multiple vantage points
print('=== DNS Check ===')
run('dig +short eli.virtuabaldigital.com A @8.8.8.8')
run('dig +short eli.virtuabaldigital.com A @1.1.1.1')
run('host eli.virtuabaldigital.com 2>&1')

# Also check the base domain
run('dig +short virtuabaldigital.com A @8.8.8.8')

print('\n=== Retry Caddy ===')
run('systemctl restart caddy')
time.sleep(8)
run('journalctl -u caddy --no-pager -n 15 | tail -10')

# Test
run('curl -sI https://eli.virtuabaldigital.com 2>&1 | head -10')
run('curl -sI http://eli.virtuabaldigital.com 2>&1 | head -5')

ssh.close()