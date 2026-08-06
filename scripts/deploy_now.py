#!/usr/bin/env python3
"""Eli v2 — Deploy update to VPS"""
import os, time
from paramiko import SSHClient, AutoAddPolicy

IP = "177.7.49.44"
PW = "2'E3,mCIm)W;rPD9"
REMOTE = "/opt/eli"

def main():
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    print("Connecting...")
    ssh.connect(IP, port=22, username="root", password=PW, timeout=15)
    sftp = ssh.open_sftp()
    print("Connected.")

    # 1. App update
    print("Uploading app update (23KB)...")
    sftp.put("/tmp/eli-update.tar.gz", "/tmp/eli-update.tar.gz")
    print("  Uploaded.")
    _, o, e = ssh.exec_command("tar xzf /tmp/eli-update.tar.gz -C /opt/eli/app && rm /tmp/eli-update.tar.gz", timeout=30)
    o.read(); e.read()
    print("  Extracted.")

    # 2. Create dirs
    ssh.exec_command(f"mkdir -p {REMOTE}/data/keyword-research {REMOTE}/data/eli-os-delivery/skill-templates")

    # 3. New knowledge files
    kb_dir = "/home/z/my-project/data/uploads/knowledge-sources"
    for f in ["agency-agents-marketing-specialists.md", "digital-marketing-pro-methodology.md",
              "ai-marketing-tools-ecosystem.md", "seo-agency-architecture-patterns.md"]:
        local = os.path.join(kb_dir, f)
        if os.path.exists(local):
            sftp.put(local, f"{REMOTE}/data/uploads/knowledge-sources/{f}")
            print(f"  KB: {f}")

    # 4. Keywords
    os.system("cd /home/z/my-project/data/keyword-research && tar czf /tmp/eli-kw.tar.gz .")
    print("Uploading keywords...")
    sftp.put("/tmp/eli-kw.tar.gz", "/tmp/eli-kw.tar.gz")
    _, o, e = ssh.exec_command(f"tar xzf /tmp/eli-kw.tar.gz -C {REMOTE}/data/keyword-research && rm /tmp/eli-kw.tar.gz", timeout=30)
    o.read(); e.read()
    print("  Keywords deployed.")

    # 5. Skills
    os.system("cd /home/z/my-project/data/eli-os-delivery/skill-templates && tar czf /tmp/eli-sk.tar.gz .")
    print("Uploading skills...")
    sftp.put("/tmp/eli-sk.tar.gz", "/tmp/eli-sk.tar.gz")
    _, o, e = ssh.exec_command(f"tar xzf /tmp/eli-sk.tar.gz -C {REMOTE}/data/eli-os-delivery/skill-templates && rm /tmp/eli-sk.tar.gz", timeout=30)
    o.read(); e.read()
    print("  Skills deployed.")

    # 6. Systemd
    svc = f"""[Unit]
Description=Eli MicroSaaS - AI Growth Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE}/app
Environment=NODE_ENV=production
Environment=DATABASE_URL=file:{REMOTE}/data/custom.db
Environment=KNOWLEDGE_DIR={REMOTE}/data/uploads/knowledge-sources
Environment=KEYWORD_DIR={REMOTE}/data/keyword-research
Environment=PORT=3000
ExecStart=/root/.bun/bin/bun server.js
Restart=always
RestartSec=5
StandardOutput=append:{REMOTE}/logs/eli.log
StandardError=append:{REMOTE}/logs/eli-error.log

[Install]
WantedBy=multi-user.target
"""
    with open("/tmp/eli.service", "w") as f:
        f.write(svc)
    sftp.put("/tmp/eli.service", "/etc/systemd/system/eli.service")
    ssh.exec_command("systemctl daemon-reload && systemctl enable eli")

    # 7. Restart
    print("Restarting Eli...")
    ssh.exec_command("systemctl restart eli")
    time.sleep(3)
    _, o, e = ssh.exec_command("systemctl is-active eli")
    status = o.read().decode().strip()
    print(f"  Status: {status}")

    ssh.exec_command("systemctl restart caddy")
    time.sleep(1)

    # Health
    _, o, e = ssh.exec_command("curl -sf http://localhost:3000/api/health")
    print(f"  Health: {o.read().decode().strip()[:300]}")

    sftp.close()
    ssh.close()
    print("")
    print("=== DEPLOY COMPLETE ===")
    print(f"  https://eli.virtualabdigital.com")
    print(f"  To enable brain: echo 'GEMINI_API_KEY=key' >> {REMOTE}/app/.env")
    print("  Then: systemctl restart eli")

if __name__ == "__main__":
    main()
