import paramiko,time
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('177.7.49.44',username='root',password="2'E3,mCIm)W;rPD9",timeout=30)
# Clear logs and make a request
ssh.exec_command('journalctl --rotate -u eli -n 0',timeout=10)
time.sleep(1)
ssh.exec_command('curl -s -X POST http://localhost:3000/api/eli-chat -H "Content-Type: application/json" -d \'{ "message": "parasite SEO" }\'',timeout=30)
time.sleep(1)
_,o,_=ssh.exec_command('journalctl -u eli --since "5s ago" --no-pager | tail -20',timeout=30)
print(o.read().decode())
ssh.close()