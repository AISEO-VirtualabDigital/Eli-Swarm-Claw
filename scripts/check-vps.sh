import paramiko
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
def r(c,t=30):
 _,o,e=ssh.exec_command(c,timeout=t)
 out=o.read().decode().strip()
 err=e.read().decode().strip()
 if out: print(out[:500])
 if err: print('ERR:',err[:300])
r('find / -name "bun" -type f 2>/dev/null | head -5')
r('ls /root/.bun/bin/ 2>/dev/null')
r('cat /etc/systemd/system/eli.service')
