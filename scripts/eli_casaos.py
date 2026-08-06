import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=15)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:600])
    if err: print(f'[e] {err[:400]}')
    return out

# Check casaos and nginx setup
run('systemctl list-units --type=service | grep -iE "casa|nginx|caddy|apache"')
print('===')
run('ls /etc/nginx/sites-enabled/ 2>/dev/null; ls /etc/nginx/conf.d/ 2>/dev/null')
print('===')
# Check if there's a domain already pointing here
run('dig +short virtuabaldigital.com A 2>/dev/null; dig +short www.virtuabaldigital.com A 2>/dev/null')
print('===')
# Check what casaos-gateway actually is
run('file $(which casaos-gateway 2>/dev/null) 2>/dev/null; ls -la /usr/bin/casaos* 2>/dev/null; dpkg -l | grep casaos 2>/dev/null | head -5')
print('===')
run('cat /etc/nginx/sites-enabled/default 2>/dev/null | head -40')

ssh.close()