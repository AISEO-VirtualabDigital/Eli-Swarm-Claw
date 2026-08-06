#!/usr/bin/env python3
"""Step 2: Upload files via SFTP in batches"""
import paramiko, os, time
from pathlib import Path

PASSWORD = "2'E3,mCIm)W;rPD9"
IP = '177.7.49.44'
LOCAL_STANDALONE = Path('/home/z/my-project/.next/standalone')
LOCAL_KB = Path('/home/z/my-project/data/uploads/knowledge-sources')
LOCAL_DB = Path('/home/z/my-project/db/custom.db')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(IP, port=22, username='root', password=PASSWORD, timeout=15)
sftp = ssh.open_sftp()

uploaded = 0

def upload_dir(local, remote):
    global uploaded
    for root, dirs, files in os.walk(local):
        rel = Path(root).relative_to(local)
        remote_sub = f"{remote}/{rel}" if str(rel) != '.' else remote
        for d in dirs:
            try: sftp.stat(f"{remote_sub}/{d}")
            except: sftp.mkdir(f"{remote_sub}/{d}")
        for f in files:
            lp = Path(root) / f
            rp = f"{remote_sub}/{f}"
            sftp.put(str(lp), rp)
            uploaded += 1
            if uploaded % 100 == 0:
                print(f"  ...{uploaded} files uploaded")

print("Uploading standalone build (76MB)...")
t0 = time.time()
upload_dir(LOCAL_STANDALONE, '/opt/eli/app')
print(f"  App: {uploaded} files in {time.time()-t0:.0f}s")

print("Uploading knowledge base (163+ files)...")
kb_before = uploaded
t0 = time.time()
upload_dir(LOCAL_KB, '/opt/eli/data/uploads/knowledge-sources')
print(f"  Knowledge: {uploaded - kb_before} files in {time.time()-t0:.0f}s")

print("Uploading database...")
sftp.put(str(LOCAL_DB), '/opt/eli/db/custom.db')
print(f"  DB uploaded.")

print(f"\nTotal: {uploaded + 1} files uploaded.")
sftp.close()
ssh.close()
