from paramiko import SSHClient, AutoAddPolicy

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect('177.7.49.44', port=22, username='root', password="2'E3,mCIm)W;rPD9", timeout=15)

# Check the keywords action chunk content
_, o, e = ssh.exec_command('cat /opt/eli/app/.next/server/chunks/_next-internal_server_app_api_keywords_route_actions_ea913865.js')
print('KEYWORDS CHUNK:')
print(o.read().decode().strip()[:500])

# Check the health action chunk for comparison
_, o, e = ssh.exec_command('cat /opt/eli/app/.next/server/chunks/_next-internal_server_app_api_health_route_actions_da3433c4.js')
print('\nHEALTH CHUNK:')
print(o.read().decode().strip()[:500])

ssh.close()
