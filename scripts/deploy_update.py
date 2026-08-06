#!/usr/bin/env python3
"""Eli — Targeted update deploy (app delta + knowledge + keywords + skills)"""
import sys, os, time, tempfile
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy

PROJECT = Path(__file__).resolve().parent.parent
DOMAIN = "eli.virtualabdigital.com"
REMOTE = "/opt/eli"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def log(m): print(f"{GREEN}[deploy]{NC} {m}")
def err(m): print(f"{RED}[error]{NC} {m}", file=sys.stderr); sys.exit(1)


def ssh_run(ssh, cmd, timeout=60):
    print(f"  $ {cmd[:120]}")
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    out = (o.read().decode(errors='replace') + e.read().decode(errors='replace')).strip()
    if out: print(f"    {out[:500]}")
    return out


def upload_tar(sftp, tar_path, remote_dir, label=""):
    size = os.path.getsize(tar_path)
    log(f"Uploading {label} ({size//1024}KB)...")
    remote_tar = f"/tmp/eli-update.tar.gz"
    sftp.put(tar_path, remote_tar)
    ssh_run(ssh, f"tar xzf {remote_tar} -C {remote_dir} && rm {remote_tar}")
    log(f"  {label} deployed.")


def main():
    if len(sys.argv) < 3:
        err(f"Usage: {sys.argv[0]} <IP> <PASSWORD>")

    ip, pw = sys.argv[1], sys.argv[2]

    log(f"Connecting to root@{ip}...")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, port=22, username="root", password=pw, timeout=15)
    sftp = ssh.open_sftp()
    log("  Connected.")

    # 1. Upload app delta
    app_tar = "/tmp/eli-update.tar.gz"
    if os.path.exists(app_tar):
        upload_tar(sftp, app_tar, f"{REMOTE}/app", "app update")
    else:
        log("No app update tar found, skipping app upload.")

    # 2. Upload new knowledge files (only the 4 new ones)
    kb_dir = PROJECT / "data" / "uploads" / "knowledge-sources"
    new_kb = ["agency-agents-marketing-specialists.md", "digital-marketing-pro-methodology.md",
              "ai-marketing-tools-ecosystem.md", "seo-agency-architecture-patterns.md"]
    for f in new_kb:
        local = kb_dir / f
        if local.exists():
            sftp.put(str(local), f"{REMOTE}/data/uploads/knowledge-sources/{f}")
            log(f"  KB: {f}")

    # 3. Upload keyword data (tar)
    kw_dir = PROJECT / "data" / "keyword-research"
    if kw_dir.exists():
        kw_tar = tempfile.mktemp(suffix=".tar.gz")
        os.system(f"cd {kw_dir} && tar czf {kw_tar} .")
        upload_tar(sftp, kw_tar, f"{REMOTE}/data/keyword-research", "keywords")
        os.unlink(kw_tar)

    # 4. Upload skill templates (tar)
    sk_dir = PROJECT / "data" / "eli-os-delivery" / "skill-templates"
    if sk_dir.exists():
        sk_tar = tempfile.mktemp(suffix=".tar.gz")
        os.system(f"cd {sk_dir} && tar czf {sk_tar} .")
        upload_tar(sftp, sk_tar, f"{REMOTE}/data/eli-os-delivery/skill-templates", "skills")
        os.unlink(sk_tar)

    # 5. Update systemd service with new env vars
    log("Updating systemd service...")
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
    tmp = tempfile.mktemp(suffix=".service")
    with open(tmp, "w") as f: f.write(svc)
    sftp.put(tmp, "/etc/systemd/system/eli.service")
    os.unlink(tmp)
    ssh_run(ssh, "systemctl daemon-reload && systemctl enable eli")

    # 6. Restart
    log("Restarting Eli...")
    ssh_run(ssh, "systemctl restart eli")
    time.sleep(3)

    status = ssh_run(ssh, "systemctl is-active eli")
    if "active" not in status.lower():
        err("Eli failed to start!")
    log("  Eli is RUNNING.")

    ssh_run(ssh, "systemctl restart caddy")
    time.sleep(1)

    # Health check
    log("Health check...")
    h = ssh_run(ssh, "curl -sf http://localhost:3000/api/health")
    print(f"  {h}")

    log("=============================================")
    log(f"  Eli v2 deployed to https://{DOMAIN}")
    log(f"  NEW: Chat uses Gemini if GEMINI_API_KEY set")
    log(f"  NEW: SEO Skills, Keywords, Intro views")
    log(f"  NEW: 4 knowledge files added")
    log(f"")
    log(f"  To enable Eli's brain:")
    log(f"  echo 'GEMINI_API_KEY=your_key' >> {REMOTE}/app/.env")
    log(f"  systemctl restart eli")
    log("=============================================")

    sftp.close()
    ssh.close()


if __name__ == "__main__":
    main()