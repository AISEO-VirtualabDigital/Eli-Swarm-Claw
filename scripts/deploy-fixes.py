import paramiko
import os
import sys

HOST = '177.7.49.44'
USER = 'root'
PASS = "2'E3,mCIm)W;rPD9"
REMOTE_DEPLOY = '/opt/eli/app'

def ssh_exec(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if err and 'warning' not in err.lower():
        print(f'  STDERR: {err[:500]}')
    return out

def sftp_upload(sftp, local_path, remote_path):
    if os.path.isfile(local_path):
        sftp.put(local_path, remote_path)
        print(f'  Uploaded: {os.path.basename(local_path)} -> {remote_path}')
    elif os.path.isdir(local_path):
        try:
            sftp.stat(remote_path)
        except FileNotFoundError:
            sftp.mkdir(remote_path)
        for item in os.listdir(local_path):
            sftp_upload(sftp, os.path.join(local_path, item), os.path.join(remote_path, os.path.basename(item)))

def main():
    print('[1/5] Connecting to VPS...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=30)
    sftp = ssh.open_sftp()

    # Ensure remote directories exist
    print('[2/5] Ensuring remote directories...')
    for d in ['src/lib', 'src/app/api/vault-sync', 'src/app/api/eli-chat', 'src/app/api/health', 'src/app/api/knowledge-stats']:
        remote_d = f'{REMOTE_DEPLOY}/{d}'
        try:
            sftp.stat(remote_d)
        except FileNotFoundError:
            sftp.mkdir(remote_d)
            print(f'  Created: {remote_d}')

    # Upload fixed source files
    print('[3/5] Uploading fixed source files...')
    files_to_upload = [
        ('src/lib/vault-search.ts', f'{REMOTE_DEPLOY}/src/lib/vault-search.ts'),
        ('src/lib/knowledge-search.ts', f'{REMOTE_DEPLOY}/src/lib/knowledge-search.ts'),
        ('src/lib/obsidian-chunk-engine.ts', f'{REMOTE_DEPLOY}/src/lib/obsidian-chunk-engine.ts'),
        ('src/lib/air-llm.ts', f'{REMOTE_DEPLOY}/src/lib/air-llm.ts'),
        ('src/app/api/eli-chat/route.ts', f'{REMOTE_DEPLOY}/src/app/api/eli-chat/route.ts'),
        ('src/app/api/vault-sync/route.ts', f'{REMOTE_DEPLOY}/src/app/api/vault-sync/route.ts'),
    ]
    
    for local, remote in files_to_upload:
        full_local = f'/home/z/my-project/{local}'
        if os.path.exists(full_local):
            sftp.put(full_local, remote)
            print(f'  Uploaded: {local}')
        else:
            print(f'  SKIP (not found): {local}')

    # Update systemd service with new env vars
    print('[4/5] Updating systemd service...')
    service_content = '''[Unit]
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
ExecStart=/root/.bun/bin/bun server.js
Restart=always
RestartSec=5
StandardOutput=append:/opt/eli/logs/eli.log
StandardError=append:/opt/eli/logs/eli-error.log

[Install]
WantedBy=multi-user.target
'''
    
    # Write service file locally then upload
    local_svc = '/tmp/eli.service'
    with open(local_svc, 'w') as f:
        f.write(service_content)
    sftp.put(local_svc, '/etc/systemd/system/eli.service')
    print('  Uploaded: eli.service')

    # Reload and restart
    print('[5/5] Restarting Eli...')
    print(ssh_exec(ssh, 'systemctl daemon-reload'))
    print(ssh_exec(ssh, 'systemctl restart eli'))
    import time; time.sleep(3)
    
    status = ssh_exec(ssh, 'systemctl is-active eli').strip()
    print(f'  Eli status: {status}')

    # Health check
    health = ssh_exec(ssh, 'curl -sf http://localhost:3000/api/health 2>/dev/null || echo FAILED')
    print(f'  Health: {health[:300]}')
    
    # Test vault-sync endpoint
    sync = ssh_exec(ssh, 'curl -sf http://localhost:3000/api/vault-sync?action=stats 2>/dev/null || echo FAILED')
    print(f'  Vault sync: {sync[:300]}')

    sftp.close()
    ssh.close()
    print('\nDone! All fixes deployed.')

if __name__ == '__main__':
    main()
