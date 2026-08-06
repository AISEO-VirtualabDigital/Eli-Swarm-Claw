import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=60)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:600])
    if err: print(f'[e] {err[:400]}')
    return out

# Check CasaOS gateway config format
run('cat /etc/casaos/casaos.conf')
print('===')
run('cat /etc/casaos/gateway.conf 2>/dev/null || echo no gateway.conf')
print('===')
# Check how the gateway binary gets its port
run('strings /usr/bin/casaos-gateway | grep -i "port\|listen\|80\|addr" | head -20')
print('===')
# Check if there's a systemd override
run('ls /etc/systemd/system/casaos-gateway.service.d/ 2>/dev/null; systemctl cat casaos-gateway 2>/dev/null | head -25')

ssh.close()