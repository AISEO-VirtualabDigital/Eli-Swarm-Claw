#!/usr/bin/env python3
"""Step 1: Prepare server — install bun, create dirs"""
import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

def run(cmd):
    print(f"$ {cmd[:100]}")
    i, o, e = ssh.exec_command(cmd, timeout=120)
    out = o.read().decode(errors='replace')
    err = e.read().decode(errors='replace')
    if out.strip(): print(out.strip()[:500])
    if err.strip(): print(f"[e] {err.strip()[:500]}")
    return out

# Create dirs
run("mkdir -p /opt/eli/{data/uploads/knowledge-sources,db,logs,app}")

# Check bun
r = run("which bun 2>/dev/null && bun --version || echo NONE")
if "NONE" in r:
    print("Installing bun...")
    run("curl -fsSL https://bun.sh/install | bash")
    # Fix path for subsequent commands
    run("export PATH=$HOME/.bun/bin:$PATH && bun --version")
else:
    print(f"Bun already: {r.strip()}")

# Check caddy
r = run("which caddy 2>/dev/null && caddy version || echo NONE")
if "NONE" in r:
    print("Installing Caddy...")
    run("apt-get update -qq 2>&1 | tail -2")
    run("apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https curl 2>&1 | tail -2")
    run("curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg 2>&1")
    run("curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list")
    run("apt-get update -qq 2>&1 | tail -2")
    run("apt-get install -y -qq caddy 2>&1 | tail -3")
else:
    print(f"Caddy already: {r.strip()}")

print("\nServer prepared.")
ssh.close()
