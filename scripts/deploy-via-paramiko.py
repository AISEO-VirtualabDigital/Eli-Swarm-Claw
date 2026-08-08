#!/usr/bin/env python3
"""Deploy Eli to VPS via SFTP (no ssh binary needed)."""

import paramiko
import os
import sys
import stat

VPS_IP = sys.argv[1] if len(sys.argv) > 1 else '177.7.49.44'
VPS_USER = sys.argv[2] if len(sys.argv) > 2 else 'root'
REMOTE_DIR = '/opt/eli'
PROJECT_DIR = '/home/z/my-project'

def run_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if exit_code != 0:
        print(f'  [WARN] exit {exit_code}: {err.strip() or out.strip()}')
    return out.strip(), err.strip(), exit_code

def upload_dir(sftp, local_dir, remote_dir, exclude_dirs=None, exclude_files=None):
    """Recursively upload a directory."""
    exclude_dirs = exclude_dirs or []
    exclude_files = exclude_files or []
    
    for root, dirs, files in os.walk(local_dir):
        # Filter excluded dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        rel_path = os.path.relpath(root, local_dir)
        remote_path = os.path.join(remote_dir, rel_path).replace('\\', '/')
        
        # Create remote directory
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            sftp.mkdir(remote_path)
            print(f'  mkdir {remote_path}')
        
        for f in files:
            if f in exclude_files:
                continue
            local_file = os.path.join(root, f)
            remote_file = os.path.join(remote_path, f).replace('\\', '/')
            sftp.put(local_file, remote_file)
            size = os.path.getsize(local_file)
            print(f'  upload {rel_path}/{f} ({size:,} bytes)')

def main():
    print(f'[DEPLOY] Connecting to {VPS_USER}@{VPS_IP}...')
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Try key-based auth first, then any available key
    try:
        ssh.connect(VPS_IP, username=VPS_USER, timeout=15)
    except Exception as e:
        print(f'[ERROR] Cannot connect: {e}')
        print('Make sure your SSH key is set up for this VPS.')
        sys.exit(1)
    
    print('[DEPLOY] Connected!')
    
    # Step 1: Prepare remote directories
    print('[1/5] Preparing remote directories...')
    run_cmd(ssh, f'mkdir -p {REMOTE_DIR}/{{app,data/uploads/knowledge-sources,data/uploads/docs,data/uploads/design,data/uploads/zips,db,logs,public}}')
    
    # Check if bun exists on remote
    out, _, _ = run_cmd(ssh, 'which bun || echo NOT_FOUND')
    if 'NOT_FOUND' in out:
        print('  Installing bun on VPS...')
        run_cmd(ssh, 'curl -fsSL https://bun.sh/install | bash')
        out2, _, _ = run_cmd(ssh, 'export PATH=$HOME/.bun/bin:$PATH && which bun')
        print(f'  bun installed at: {out2}')
    else:
        print(f'  bun found: {out}')
    
    # Step 2: Upload standalone build
    print('[2/5] Uploading Next.js standalone build...')
    sftp = ssh.open_sftp()
    
    standalone_dir = os.path.join(PROJECT_DIR, '.next/standalone')
    if os.path.exists(standalone_dir):
        upload_dir(sftp, standalone_dir, f'{REMOTE_DIR}/app',
                   exclude_dirs=['node_modules', '.next', 'cache'],
                   exclude_files=['dev.log', 'server.log'])
    else:
        print('  [WARN] No .next/standalone found, skipping')
    
    # Step 3: Upload public assets (includes PDFs now)
    print('[3/5] Uploading public assets...')
    public_dir = os.path.join(PROJECT_DIR, 'public')
    if os.path.exists(public_dir):
        upload_dir(sftp, public_dir, f'{REMOTE_DIR}/app/public')
    
    # Step 4: Upload knowledge base + DB
    print('[4/5] Uploading knowledge base + database...')
    kb_dir = os.path.join(PROJECT_DIR, 'data/uploads/knowledge-sources')
    if os.path.exists(kb_dir):
        upload_dir(sftp, kb_dir, f'{REMOTE_DIR}/data/uploads/knowledge-sources')
    
    db_path = os.path.join(PROJECT_DIR, 'db/custom.db')
    if os.path.exists(db_path):
        sftp.put(db_path, f'{REMOTE_DIR}/db/custom.db')
        print(f'  upload db/custom.db ({os.path.getsize(db_path):,} bytes)')
    
    # Also upload the eli-vault data
    vault_dir = os.path.join(PROJECT_DIR, 'data/eli-vault')
    if os.path.exists(vault_dir):
        upload_dir(sftp, vault_dir, f'{REMOTE_DIR}/data/eli-vault',
                   exclude_dirs=['.git'])
    
    sftp.close()
    
    # Step 5: Create systemd service + start
    print('[5/5] Setting up systemd service...')
    
    # Read env values
    with open(os.path.join(PROJECT_DIR, '.env')) as f:
        env_content = f.read()
    
    import re
    def get_env(key):
        m = re.search(rf'^{key}=(.*)$', env_content, re.MULTILINE)
        return m.group(1).strip() if m else ''
    
    gemini_key = get_env('GEMINI_API_KEY')
    gemini_proxy = get_env('GEMINI_PROXY')
    eli_api_key = get_env('ELI_API_KEY')
    openinbox_key = get_env('OPENINBOX_API_KEY')
    
    # Detect bun path on remote
    bun_path, _, _ = run_cmd(ssh, 'export PATH=$HOME/.bun/bin:$PATH && which bun')
    if not bun_path:
        bun_path = '/root/.bun/bin/bun'
    
    service = f'''[Unit]
Description=Eli MicroSaaS — AI Growth Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/eli/app
Environment=NODE_ENV=production
Environment=DATABASE_URL=file:/opt/eli/data/custom.db
Environment=KNOWLEDGE_DIR=/opt/eli/data/uploads/knowledge-sources
Environment=KEYWORD_DIR=/opt/eli/data/keyword-research
Environment=OBSIDIAN_VAULT_PATH=/opt/eli/data/eli-vault
Environment=PORT=3000
Environment=GEMINI_API_KEY={gemini_key}
Environment=GEMINI_PROXY={gemini_proxy}
Environment=OPENINBOX_API_KEY={openinbox_key}
Environment=ELI_API_KEY={eli_api_key}
ExecStart={bun_path} server.js
Restart=always
RestartSec=5
StandardOutput=append:/opt/eli/logs/eli.log
StandardError=append:/opt/eli/logs/eli-error.log

[Install]
WantedBy=multi-user.target'''
    
    # Write service file via SFTP
    sftp = ssh.open_sftp()
    import tempfile
    tmp_service = '/tmp/eli.service'
    with open(tmp_service, 'w') as f:
        f.write(service)
    sftp.put(tmp_service, '/etc/systemd/system/eli.service')
    sftp.close()
    os.remove(tmp_service)
    
    run_cmd(ssh, 'systemctl daemon-reload && systemctl enable eli')
    
    # Restart Eli
    print('[DEPLOY] Restarting Eli...')
    out, err, code = run_cmd(ssh, 'systemctl restart eli && sleep 2 && systemctl is-active eli')
    if 'active' in out:
        print(f'  Eli is RUNNING')
    else:
        print(f'  Eli FAILED: {err}')
        out2, _, _ = run_cmd(ssh, 'journalctl -u eli --no-pager -n 15')
        print(f'  Logs: {out2}')
    
    # Health check
    print('[DEPLOY] Health check...')
    out, _, _ = run_cmd(ssh, 'curl -sf http://localhost:3000/api/health 2>/dev/null || echo FAILED')
    print(f'  {out}')
    
    # Caddy config (if caddy exists)
    out, _, _ = run_cmd(ssh, 'which caddy || echo NOT_FOUND')
    if 'NOT_FOUND' not in out:
        print('[DEPLOY] Configuring Caddy...')
        caddyfile = '''{
        email admin@virtuabaldigital.com
}

eli.virtuabaldigital.com {
        reverse_proxy localhost:3000 {
                header_up Host {host}
                header_up X-Forwarded-For {remote_host}
                header_up X-Forwarded-Proto {scheme}
                header_up X-Real-IP {remote_host}
        }

        @static path /logo.svg /robots.txt
        header @static Cache-Control "public, max-age=86400"

        header {
                X-Frame-Options "DENY"
                X-Content-Type-Options "nosniff"
                Referrer-Policy "strict-origin-when-cross-origin"
        }
}'''
        sftp = ssh.open_sftp()
        tmp_caddy = '/tmp/Caddyfile'
        with open(tmp_caddy, 'w') as f:
            f.write(caddyfile)
        sftp.put(tmp_caddy, '/etc/caddy/Caddyfile')
        sftp.close()
        os.remove(tmp_caddy)
        run_cmd(ssh, 'systemctl restart caddy')
        print('  Caddy restarted')
    else:
        print('  Caddy not found — skipping')
    
    ssh.close()
    
    print()
    print('=' * 55)
    print(f'  Eli deployed to {VPS_IP}!')
    print(f'  URL: https://eli.virtuabaldigital.com')
    print(f'  PDFs:')
    print(f'    https://eli.virtuabaldigital.com/eli-safety-guidebook.pdf')
    print(f'    https://eli.virtuabaldigital.com/eli-safety-learning-guide.pdf')
    print('=' * 55)

if __name__ == '__main__':
    main()
