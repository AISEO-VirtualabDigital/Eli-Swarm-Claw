import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

# Write a one-shot systemd service that checks DNS and restarts caddy when ready
watcher_script = '''#!/bin/bash
# Wait for DNS to propagate, then restart Caddy for TLS
for i in $(seq 1 36); do
  IP=$(dig +short eli.virtuabaldigital.com @8.8.8.8 2>/dev/null)
  if [ "$IP" = "177.7.49.44" ]; then
    echo "DNS resolved! Restarting Caddy..."
    systemctl restart caddy
    sleep 10
    # Verify cert obtained
    if journalctl -u caddy --since "15 sec ago" --no-pager 2>/dev/null | grep -q "certificate obtained"; then
      echo "SUCCESS: TLS certificate obtained!"
    else
      echo "Caddy restarted, waiting for cert provisioning..."
    fi
    exit 0
  fi
  echo "DNS not yet propagated (attempt $i/36, got: $IP)"
  sleep 30
done
echo "DNS still not propagated after 18 minutes. Run: systemctl restart caddy"
'''

# Upload and run it via SFTP
sftp = ssh.open_sftp()
with open('/tmp/tls_watcher.sh', 'w') as f: f.write(watcher_script)
sftp.put('/tmp/tls_watcher.sh', '/opt/eli/tls_watcher.sh')
sftp.close()

# Run it in the background via nohup
def run(cmd):
    print(f'$ {cmd[:120]}')
    i, o, e = ssh.exec_command(cmd, timeout=15)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    if out: print(out[:500])
    if err: print(f'[e] {err[:300]}')
    return out

run('chmod +x /opt/eli/tls_watcher.sh')
run('nohup bash /opt/eli/tls_watcher.sh > /opt/eli/logs/tls_watcher.log 2>&1 &')
run('cat /opt/eli/logs/tls_watcher.log')

ssh.close()
print('\nWatcher running in background. Will auto-provision TLS when DNS propagates.')
