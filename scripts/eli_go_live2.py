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

# CasaOS gateway reads port from environment variable PORT
# Override it in a systemd override
print('=== Moving CasaOS to port 81 ===')
run('mkdir -p /etc/systemd/system/casaos-gateway.service.d')

with open('/tmp/casaos-override.conf', 'w') as f:
    f.write('[Service]\nEnvironment=PORT=81\n')
sftp.put('/tmp/casaos-override.conf', '/etc/systemd/system/casaos-gateway.service.d/override.conf')
print('Override written.')

run('systemctl daemon-reload')
run('systemctl start casaos-gateway')
time.sleep(2)

# Verify casaos moved to 81
run('ss -tlnp | grep casaos')

# Verify port 80 is free
run('ss -tlnp | grep :80')

# 2. Update Caddyfile with email
print('\n=== Updating Caddy config ===')
caddyfile = '''{
	email aiseo.virtualabdigital@gmail.com
}

eli.virtuabaldigital.com {
	reverse_proxy localhost:3000

	@static path /logo.svg /robots.txt
	header @static Cache-Control "public, max-age=86400"

	header {
		X-Frame-Options "DENY"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
	}
}
'''
with open('/tmp/Caddyfile', 'w') as f:
    f.write(caddyfile)
sftp.put('/tmp/Caddyfile', '/etc/caddy/Caddyfile')
print('Caddyfile updated.')

# 3. Start Caddy
print('\n=== Starting Caddy ===')
run('systemctl restart caddy')
time.sleep(5)

status = run('systemctl is-active caddy')
print(f'Caddy: {status}')

# Check if cert was obtained
run('journalctl -u caddy --no-pager -n 20 | tail -15')

# Test HTTPS
run('curl -sI https://eli.virtuabaldigital.com 2>&1 | head -10')

sftp.close()
ssh.close()
print('\nDone.')
