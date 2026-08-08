#!/usr/bin/env python3
"""Eli deploy script — build tar from standalone + static + public, SFTP upload, atomic swap, systemd restart."""
import sys, os, subprocess, time
import paramiko
from scp import SCPClient

HOST = '177.7.49.44'
USER = 'root'
PASS = "2'E3,mCIm)W;rPD9"
LOCAL_TAR = '/tmp/eli-deploy.tar.gz'
REMOTE_TAR = '/root/eli-deploy.tar.gz'
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_remote(ssh, cmds):
    for cmd in cmds:
        print(f'  $ {cmd[:120]}')
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out.strip(): print(f'    {out.strip()[:300]}')
        if err.strip(): print(f'    ERR: {err.strip()[:300]}')

def main():
    # Step 1: Create tarball from standalone build
    print('[DEPLOY] Creating tarball from standalone build...')
    standalone = os.path.join(PROJECT_DIR, '.next', 'standalone')
    static = os.path.join(PROJECT_DIR, '.next', 'static')
    public = os.path.join(PROJECT_DIR, 'public')
    data_dir = os.path.join(PROJECT_DIR, 'data')

    cmd = ['tar', 'czf', LOCAL_TAR,
            '-C', standalone, '.',
            '--transform', f's,^\./,,' ]
    # Add static files
    if os.path.exists(static):
        cmd += ['-C', os.path.dirname(static), os.path.basename(static),
                  '--transform', f's,^{os.path.basename(static)},.next/{os.path.basename(static)},']
    # Add public files
    if os.path.exists(public):
        cmd += ['-C', os.path.dirname(public), os.path.basename(public)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'[DEPLOY] Tar creation failed: {result.stderr[:500]}')
        sys.exit(1)
    size_mb = os.path.getsize(LOCAL_TAR) / 1e6
    print(f'[DEPLOY] Tarball created: {size_mb:.0f}MB')

    # Step 2: Upload
    print('[DEPLOY] Uploading...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)

    with SCPClient(ssh.get_transport(), socket_timeout=60) as scp:
        scp.put(LOCAL_TAR, REMOTE_TAR)
    print(f'[DEPLOY] Uploaded {size_mb:.0f}MB')

    # Step 3: Atomic swap on server
    print('[DEPLOY] Deploying (atomic swap)...')
    run_remote(ssh, [
        'systemctl stop eli || true',
        'rm -rf /opt/eli-new',
        'mkdir -p /opt/eli-new',
        'cd /opt/eli-new && tar xzf /root/eli-deploy.tar.gz',
        'rm /root/eli-deploy.tar.gz',
        'rm -rf /opt/eli-old',
        'mv /opt/eli/app /opt/eli-old || true',
        'mv /opt/eli-new /opt/eli/app',
        'mkdir -p /opt/eli/data/audit',
        'systemctl start eli',
        'sleep 3',
        'systemctl status eli --no-pager -l | head -15',
        'curl -sf http://localhost:3000/api/health | head -c 500',
    ])

    ssh.close()
    print('[DEPLOY] Done.')

if __name__ == '__main__':
    main()
