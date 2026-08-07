#!/usr/bin/env python3
"""Eli deploy script — SFTP upload + remote extract + systemd restart."""
import sys, os, time
import paramiko
from scp import SCPClient

HOST = '177.7.49.44'
USER = 'root'
PASS = "2'E3,mCIm)W;rPD9"
LOCAL_TAR = '/tmp/eli-deploy.tar.gz'
REMOTE_TAR = '/root/eli-deploy.tar.gz'
REMOTE_DIR = '/root/eli'

def run_cmds(ssh, cmds):
    for cmd in cmds:
        print(f'  $ {cmd[:100]}')
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out.strip(): print(f'    {out.strip()[:200]}')
        if err.strip(): print(f'    ERR: {err.strip()[:200]}')

def main():
    print('[DEPLOY] Connecting...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=15)

    # Upload
    print('[DEPLOY] Uploading tar...')
    with SCPClient(ssh.get_transport(), socket_timeout=30) as scp:
        scp.put(LOCAL_TAR, REMOTE_TAR)
    print(f'[DEPLOY] Uploaded {os.path.getsize(LOCAL_TAR) / 1e6:.0f}MB')

    # Stop, extract, start
    print('[DEPLOY] Stopping service...')
    run_cmds(ssh, [
        'systemctl stop eli || true',
        f'rm -rf {REMOTE_DIR}/bak && mv {REMOTE_DIR} {REMOTE_DIR}/bak || true',
        f'mkdir -p {REMOTE_DIR} && cd {REMOTE_DIR} && tar xzf {REMOTE_TAR}',
        f'rm {REMOTE_TAR}',
        'systemctl start eli',
        'sleep 2',
        'systemctl status eli --no-pager -l | head -20',
        'curl -sf http://localhost:3000/api/health | head -c 300',
    ])

    ssh.close()
    print('[DEPLOY] Done.')

if __name__ == '__main__':
    main()
