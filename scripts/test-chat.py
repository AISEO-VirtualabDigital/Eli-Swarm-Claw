import paramiko,json,time

ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
sftp=ssh.open_sftp()
def r(c):
    _,o,_=ssh.exec_command(c,timeout=60)
    return o.read().decode().strip()

sftp.put('/tmp/eli-test.json','/tmp/eli-test.json')
time.sleep(2)
try:
    ssh.exec_command('curl -s -X POST http://localhost:3000/api/eli-chat -H Content-Type: application/json -d @/tmp/eli-test.json',timeout=30)
    time.sleep(2)
    ssh.exec_command('journalctl -u eli --since 5s --no-pager | tail -20')
except:
        pass
sftp.close()
ssh.close()