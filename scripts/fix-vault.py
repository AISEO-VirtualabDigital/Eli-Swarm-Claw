import paramiko,time

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
sftp=ssh.open_sftp()

def r(c):
    _,o,_=ssh.exec_command(c,timeout=60)
    return o.read().decode().strip()

print('Uploading vault (12MB)...')
sftp.put('/tmp/slim-vault.tar.gz','/tmp/slim-vault.tar.gz')
r('cd /opt/eli/data && mkdir -p eli-vault && cd eli-vault && tar xzf /tmp/slim-vault.tar.gz && rm /tmp/slim-vault.tar.gz')
print('Vault:')
r('ls /opt/eli/data/eli-vault/')
r('ls /opt/eli/data/eli-vault/01-Active/ | wc -l')
print('Uploading search index (6MB)...')
sftp.put('/tmp/eli-vault-index-parts.tar.gz','/tmp/eli-vault-index-parts.tar.gz')
r('cd /opt/eli/data/eli-vault/03-Index && tar xzf /tmp/eli-vault-index-parts.tar.gz && rm /tmp/eli-vault-index-parts.tar.gz')
print('Index:')
r('ls /opt/eli/data/eli-vault/03-Index/')

print('Restarting Eli...')
r('systemctl restart eli')
time.sleep(3)
print('Health:')
r('curl -s http://localhost:3000/api/health | python3 -m json.tool')
print('Chat:')
chat_cmd = "curl -s -X POST http://localhost:3000/api/eli-chat -H 'Content-Type: application/json' -d '{\"message\": \"parasite SEO\"}' | python3 -m json.tool | head -30"
r(chat_cmd)

sftp.close()
ssh.close()
print('Done.')
