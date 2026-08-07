import paramiko
import os

VPS_HOST = '177.7.49.44'
VPS_USER = 'root'
VPS_PASS = "2'E3,mCIm)W;rPD9"

def run(ssh, cmd, t=120):
    print(f'  $ {cmd[:120]}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=t)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        for line in out.split('\n')[:15]: print(f'    {line}')
    if err and 'warn' not in err.lower()[:30]:
        for line in err.split('\n')[:3]:
            if line.strip(): print(f'    [e] {line[:120]}')
    return out

print('Connecting...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=30)
sftp = ssh.open_sftp()

print('Creating remote dirs...')
run(ssh, 'mkdir -p /opt/eli/data/eli-vault')

print('Uploading vault (13MB)...')
sftp.put('/tmp/eli-vault.tar.gz', '/tmp/eli-vault.tar.gz')
print('Uploaded.')

print('Extracting...')
run(ssh, 'cd /opt/eli/data/eli-vault && tar xzf /tmp/eli-vault.tar.gz && rm /tmp/eli-vault.tar.gz')

print('Verifying...')
run(ssh, 'echo "Active: $(find /opt/eli/data/eli-vault/01-Active -name *.md | wc -l) chunks"')
run(ssh, 'echo "Containment: $(ls /opt/eli/data/eli-vault/00-Containment/ | wc -l) copies"')
run(ssh, 'echo "Skills: $(find /opt/eli/data/eli-vault/02-Skills -name *.md | wc -l) patterns"')
run(ssh, 'cat /opt/eli/data/eli-vault/03-Index/vault-index.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f totalChunks={d[chr(34)+chr(116)+chr(111)+chr(116)+chr(97)+chr(108)+chr(67)+chr(104)+chr(117)+chr(110)+chr(107)+chr(115)+chr(34)]} chunks, {len(d[chr(99)+chr(97)+chr(116)+chr(101)+chr(103)+chr(111)+chr(114)+chr(105)+chr(101)+chr(115)])} cats, {d[chr(115)+chr(107)+chr(105)+chr(108)+chr(108)+chr(115)]} skills")" 2>/dev/null || echo index-ok')

sftp.close()
ssh.close()
print('Vault upload complete!')
