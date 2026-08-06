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

# 1. Move CasaOS gateway from port 80 to port 81
print('=== Moving CasaOS to port 81 ===')
run('systemctl stop casaos-gateway')
# CasaOS stores its config - check for env file or config
run('cat /etc/systemd/system/casaos-gateway.service 2>/dev/null | head -20')
print('---')
# Check how casaos gateway is configured
run('export GATEWAY_PORT=81 && sed -i "s/Environment=.*/&\nEnvironment=GATEWAY_PORT=81/" /etc/systemd/system/casaos-gateway.service 2>/dev/null')
run('grep -r "PORT" /etc/systemd/system/casaos-gateway.service 2>/dev/null')
print('---')
# CasaOS uses a config file - let's find it
run('find /etc/casaos /var/lib/casaos /opt/casaos -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.conf" 2>/dev/null | head -20')
print('---')
run('cat /etc/casaos/gateway.yaml 2>/dev/null || cat /etc/casaos/casaos.yaml 2>/dev/null || echo "no yaml found"')

ssh.close()