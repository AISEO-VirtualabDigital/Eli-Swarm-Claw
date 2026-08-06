import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)
sftp = ssh.open_sftp()

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
# CasaOS uses a config file for its port - find and update it
run('find /etc /opt /var -name "*.yaml" -o -name "*.yml" -o -name "*.json" 2>/dev/null | xargs rg -l "port.*80" 2>/dev/null | head -10')
run('cat /etc/casaos/gateway.yaml 2>/dev/null || cat /opt/casaos/gateway.yaml 2>/dev/null || echo NO_YAML')
run('rg -r "" "80" /usr/bin/casaos-gateway 2>/dev/null | head -3 || echo binary')
# CasaOS gateway port is set via env or config
run('systemctl cat casaos-gateway 2>/dev/null | head -20')
run('cat /etc/systemd/system/casaos-gateway.service 2>/dev/null || systemctl cat casaos-gateway 2>/dev/null | grep -E "Exec|Env|Port"')

ssh.close()
