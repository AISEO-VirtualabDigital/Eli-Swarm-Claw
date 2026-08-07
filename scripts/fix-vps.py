import paramiko
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)

def r(c):
 _,o,e=ssh.exec_command(c,timeout=30)
 print(o.read().decode()[:500])
 print(e.read().decode()[:200])

print('=== Files in /opt/eli/app/ (non-hidden) ===')
r('ls -la /opt/eli/app/ | grep -v node_modules | head -30')
print('\n=== app/ dir at root? ===')
r('ls -la /opt/eli/app/app/ 2>/dev/null || echo NO app/ dir')
print('\n=== .next in src? ===')
r('find /opt/eli/app/src -name .next -type d 2>/dev/null')
print('\n=== Any .next dirs? ===')
print('\n=== Cleanup ===')
r('rm -rf /opt/eli/app/app 2>/dev/null; rm -rf /opt/eli/app/src/.next 2>/dev/null; rm -rf /opt/eli/app/.next 2>/dev/null; echo cleaned')
ssh.close()