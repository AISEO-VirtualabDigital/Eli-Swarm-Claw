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

# Fix Caddyfile with correct domain
caddyfile = """{
	email aiseo.virtualabdigital@gmail.com
}

eli.virtualabdigital.com {
	reverse_proxy localhost:3000

	@static path /logo.svg /robots.txt
	header @static Cache-Control "public, max-age=86400"

	header {
		X-Frame-Options "DENY"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
	}
}
"""

with open('/tmp/Caddyfile', 'w') as f:
    f.write(caddyfile)
sftp.put('/tmp/Caddyfile', '/etc/caddy/Caddyfile')
print('Caddyfile fixed: virtualabdigital.com')

# Clear old certs and restart
run('rm -rf /var/lib/caddy/.local/share/caddy/acme/')
run('chown -R caddy:caddy /var/lib/caddy')
run('systemctl restart caddy')
print('Caddy restarted...')

# Wait for TLS
for i in range(12):
    time.sleep(5)
    journal = run('journalctl -u caddy --since "30 sec ago" --no-pager 2>/dev/null | grep -iE "cert|obtained|error|tls" | tail -3')
    if 'certificate obtained' in journal.lower():
        print('*** SSL CERT OBTAINED ***')
        break
    print(f'  Attempt {i+1}: waiting...')

print('\n=== Verify ===')
run('systemctl is-active caddy')
run('curl -sI https://eli.virtualabdigital.com 2>&1 | head -12')

sftp.close()
ssh.close()
print('Done.')
