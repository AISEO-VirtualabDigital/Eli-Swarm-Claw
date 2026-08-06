#!/usr/bin/env python3
"""
Eli MicroSaaS — Deploy v2
Uploads app build + knowledge + keywords + skills via tar + SFTP.
"""

import sys, os, time, tempfile
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy

PROJECT_DIR = Path(__file__).resolve().parent.parent
STANDALONE_DIR = PROJECT_DIR / ".next" / "standalone"
KNOWLEDGE_DIR = PROJECT_DIR / "data" / "uploads" / "knowledge-sources"
KEYWORD_DIR = PROJECT_DIR / "data" / "keyword-research"
SKILLS_DIR = PROJECT_DIR / "data" / "eli-os-delivery" / "skill-templates"
DB_FILE = PROJECT_DIR / "db" / "custom.db"
DOMAIN = "eli.virtualabdigital.com"
REMOTE_BASE = "/opt/eli"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def log(msg):
    print(f"{GREEN}[deploy]{NC} {msg}


def err(msg):
    print(f"{RED}[error]{NC} {msg}", file=sys.stderr)
    sys.exit(1)


def run_ssh(ssh, cmd, timeout=120):
    print(f"  $ {cmd[:120]}{'...' if len(cmd)>120 else ''}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors="replace")
    err_out = stderr.read().decode(errors="replace")
    for line in (out + err_out).strip().split("\n"):
        if line.strip(): print(f"    {line}")
    return out + err_out


def main():
    if len(sys.argv) < 3:
        err(f"Usage: {sys.argv[0]} <IP> <PASSWORD>")

    ip, password = sys.argv[1], sys.argv[2]

    if not STANDALONE_DIR.exists():
        err(f"No standalone build at {STANDALONE_DIR}. Run 'npm run build' first.")

    # Connect
    log(f"Connecting to root@{ip}...")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(ip, port=22, username="root", password=password, timeout=15)
    sftp = ssh.open_sftp()
    log("  Connected.")

    # Prepare server directories
    log("Preparing server...")
    run_ssh(ssh, f"mkdir -p {REMOTE_BASE}/{{data/uploads/knowledge-sources,data/keyword-research,data/eli-os-delivery/skill-templates,db,logs,app}}")

    # ─── Upload app as tar ─────────────────────────────
    log("Packing app build...")
    app_tar = tempfile.mktemp(suffix=".tar.gz")
    os.system(f"cd {STANDALONE_DIR} && tar czf {app_tar} .")
    remote_tar = f"/tmp/eli-app.tar.gz"
    log(f"Uploading app ({os.path.getsize(app_tar)//1024}KB)...")
    sftp.put(app_tar, remote_tar)
    os.unlink(app_tar)
    run_ssh(ssh, f"rm -rf {REMOTE_BASE}/app/* && tar xzf {remote_tar} -C {REMOTE_BASE}/app && rm {remote_tar}")
    log("  App deployed.")

    # ─── Upload knowledge as tar ───────────────────────
    if KNOWLEDGE_DIR.exists():
        log("Packing knowledge base...")
        kb_tar = tempfile.mktemp(suffix=".tar.gz")
        os.system(f"cd {KNOWLEDGE_DIR} && tar czf {kb_tar} .")
        remote_tar = f"/tmp/eli-kb.tar.gz"
        log(f"Uploading knowledge ({os.path.getsize(kb_tar)//1024}KB)...")
        sftp.put(kb_tar, remote_tar)
        os.unlink(kb_tar)
        run_ssh(ssh, f"tar xzf {remote_tar} -C {REMOTE_BASE}/data/uploads/knowledge-sources && rm {remote_tar}")
        log("  Knowledge base deployed.")

    # ─── Upload keyword data ───────────────────────────
    if KEYWORD_DIR.exists():
        log("Packing keyword research data...")
        kw_tar = tempfile.mktemp(suffix=".tar.gz")
        os.system(f"cd {KEYWORD_DIR} && tar czf {kw_tar} .")
        remote_tar = f"/tmp/eli-kw.tar.gz"
        log(f"Uploading keywords ({os.path.getsize(kw_tar)//1024}KB)...")
        sftp.put(kw_tar, remote_tar)
        os.unlink(kw_tar)
        run_ssh(ssh, f"tar xzf {remote_tar} -C {REMOTE_BASE}/data/keyword-research && rm {remote_tar}")
        log("  Keywords deployed.")

    # ─── Upload skill templates ────────────────────────
    if SKILLS_DIR.exists():
        log("Packing skill templates...")
        sk_tar = tempfile.mktemp(suffix=".tar.gz")
        os.system(f"cd {SKILLS_DIR} && tar czf {sk_tar} .")
        remote_tar = f"/tmp/eli-sk.tar.gz"
        log(f"Uploading skills ({os.path.getsize(sk_tar)//1024}KB)...")
        sftp.put(sk_tar, remote_tar)
        os.unlink(sk_tar)
        run_ssh(ssh, f"tar xzf {remote_tar} -C {REMOTE_BASE}/data/eli-os-delivery/skill-templates && rm {remote_tar}")
        log("  Skills deployed.")

    # ─── Upload database ───────────────────────────────
    if DB_FILE.exists():
        log("Uploading database...")
        sftp.put(str(DB_FILE), f"{REMOTE_BASE}/db/custom.db")
        log("  Database uploaded.")

    # ─── Systemd service (with new env vars) ────────────
    log("Updating systemd service...")
    service = f"""[Unit]
Description=Eli MicroSaaS - AI Growth Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE_BASE}/app
Environment=NODE_ENV=production
Environment=DATABASE_URL=file:{REMOTE_BASE}/data/custom.db
Environment=KNOWLEDGE_DIR={REMOTE_BASE}/data/uploads/knowledge-sources
Environment=KEYWORD_DIR={REMOTE_BASE}/data/keyword-research
Environment=PORT=3000
ExecStart=/root/.bun/bin/bun server.js
Restart=always
RestartSec=5
StandardOutput=append:{REMOTE_BASE}/logs/eli.log
StandardError=append:{REMOTE_BASE}/logs/eli-error.log

[Install]
WantedBy=multi-user.target
"""
    svc_tmp = tempfile.mktemp(suffix=".service")
    with open(svc_tmp, "w") as f:
        f.write(service)
    sftp.put(svc_tmp, "/etc/systemd/system/eli.service")
    os.unlink(svc_tmp)
    run_ssh(ssh, "systemctl daemon-reload && systemctl enable eli")

    # ─── Restart ───────────────────────────────────────
    log("Restarting Eli...")
    run_ssh(ssh, "systemctl restart eli")
    time.sleep(3)
    status = run_ssh(ssh, "systemctl is-active eli")
    if "active" not in status.lower():
        err("Eli failed to start. Check: journalctl -u eli -n 30")
    log("  Eli is RUNNING.")

    log("Restarting Caddy...")
    run_ssh(ssh, "systemctl restart caddy")
    time.sleep(2)

    # Health check
    log("Health check...")
    health = run_ssh(ssh, "curl -sf http://localhost:3000/api/health")
    print(f"  {health}")

    log("=============================================")
    log(f"  Eli deployed to https://{DOMAIN}")
    log(f"  Health: https://{DOMAIN}/api/health")
    log(f"")
    log(f"  NEW: Set GEMINI_API_KEY in /opt/eli/app/.env")
    log(f"  to enable Eli's brain (Gemini 2.0 Flash)")
    log("=============================================")

    sftp.close()
    ssh.close()


if __name__ == "__main__":
    main()
