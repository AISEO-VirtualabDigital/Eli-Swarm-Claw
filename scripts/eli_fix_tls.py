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

# 1. Check DNS from the server itself
print('=== DNS Check ===')
run('dig +short eli.virtuabaldigital.com @8.8.8.8')
run('dig +short eli.virtuabaldigital.com @1.1.1.1')

# 2. Fix Caddy data dir permissions (caddy user needs write access)
print('\n=== Fix Caddy Permissions ===')
run('mkdir -p /var/lib/caddy/.local/share/caddy')
run('chown -R caddy:caddy /var/lib/caddy')
run('ls -la /var/lib/caddy/')

# 3. Restart Caddy to retry cert
print('\n=== Restart Caddy for TLS retry ===')
run('systemctl restart caddy')
time.sleep(5)

# 4. Watch cert progress
for i in range(12):
    time.sleep(5)
    journal = run('journalctl -u caddy --since "30 sec ago" --no-pager 2>/dev/null | tail -3')
    if 'certificate obtained' in journal.lower():
        print('*** TLS CERT OBTAINED ***')
        break
    if 'error' in journal.lower() or 'failed' in journal.lower():
        print(f'  ...attempt {i+1}: checking...')
    else:
        print(f'  ...attempt {i+1}: waiting...')

# 5. Final verification
print('\n=== Verify ===')
run('systemctl is-active caddy')
run('journalctl -u caddy --since "2 min ago" --no-pager | grep -iE "cert|obtained|error|tls" | tail -8')
run('curl -sI https://eli.virtuabaldigital.com 2>/dev/null | head -10 || echo "HTTPS not ready yet - DNS may still be propagating"')

ssh.close()
print('\nDone.')
