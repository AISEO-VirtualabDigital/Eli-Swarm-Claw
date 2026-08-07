import paramiko
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
_,o,_=ssh.exec_command('journalctl -u eli --since "1 min ago" --no-pager 2>&1 | tail -30',timeout=30)
print(o.read().decode())
ssh.close()