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

# Check full caddy journal for the actual error
run('journalctl -u caddy --no-pager -n 50 | tail -30')
print('===')
# Check DNS
run('dig +short eli.virtuabaldigital.com A 2>/dev/null || nslookup eli.virtuabaldigital.com 2>&1 | tail -5')
print('===')
# Check what port 80/443 are bound to
run('ss -tlnp | grep -E "80|443"')
print('===')
# Check if docker or something else is using 80/443
run('docker ps 2>/dev/null | head -5')

ssh.close()