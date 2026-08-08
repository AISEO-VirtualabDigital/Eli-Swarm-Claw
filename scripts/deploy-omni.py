import paramiko
import os
import sys

HOST = '177.7.49.44'
USER = 'root'
PASS = "2'E3,mCIm)W;rPD9"
REMOTE_DEPLOY = '/opt/eli/app'

def main():
    print('[1/3] Connecting to VPS...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=30)
    sftp = ssh.open_sftp()

    # Ensure directories
    print('[2/3] Creating omni directory...')
    try:
        sftp.stat(f'{REMOTE_DEPLOY}/src/app/api/omni')
    except FileNotFoundError:
        sftp.mkdir(f'{REMOTE_DEPLOY}/src/app/api/omni')
        print(f'  Created: {REMOTE_DEPLOY}/src/app/api/omni')

    # Upload files
    files = [
        ('src/lib/omni-route.ts', f'{REMOTE_DEPLOY}/src/lib/omni-route.ts'),
        ('src/app/api/omni/route.ts', f'{REMOTE_DEPLOY}/src/app/api/omni/route.ts'),
        ('src/app/api/eli-chat/route.ts', f'{REMOTE_DEPLOY}/src/app/api/eli-chat/route.ts'),
    ]

    for local, remote in files:
        full = f'/home/z/my-project/{local}'
        if os.path.exists(full):
            sftp.put(full, remote)
            print(f'  Uploaded: {local}')
        else:
            print(f'  SKIP: {local}')

    # Add OPENINBOX_API_KEY to systemd
    print('[3/3] Restarting Eli...')
    stdin, stdout, stderr = ssh.exec_command('systemctl restart eli')
    stdout.read()
    import time; time.sleep(3)

    status = ssh.exec_command('systemctl is-active eli')[1].read().decode().strip()
    print(f'  Eli status: {status}')

    # Test omni endpoint
    health = ssh.exec_command('curl -s http://localhost:3000/api/health 2>/dev/null || echo FAILED')[1].read().decode()[:200]
    print(f'  Health: {health}')

    sftp.close()
    ssh.close()
    print('Done!')

if __name__ == '__main__':
    main()
