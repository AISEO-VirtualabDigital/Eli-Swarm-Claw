#!/usr/bin/env python3
"""
Eli MicroSaaS — Deploy via Paramiko (SSH/SFTP)
Used when the native ssh/rsync clients aren't available in the build environment.

Usage:
  python3 scripts/deploy_paramiko.py <IP> <PASSWORD>

What it does:
  1. SSH into the VPS
  2. Install bun + caddy if missing
  3. SFTP the standalone build + knowledge files + database
  4. Create systemd service + Caddy config
  5. Start everything + health check
"""

import sys, os, stat, time
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy


# ─── Config ─────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent
STANDALONE_DIR = PROJECT_DIR / ".next" / "standalone"
KNOWLEDGE_DIR = PROJECT_DIR / "data" / "uploads" / "knowledge-sources"
KEYWORD_DIR = PROJECT_DIR / "data" / "keyword-research"
SKILLS_DIR = PROJECT_DIR / "data" / "eli-os-delivery" / "skill-templates"
KEYWORD_DIR = PROJECT_DIR / "data" / "keyword-research"
SKILLS_DIR = PROJECT_DIR / "data" / "eli-os-delivery" / "skill-templates"
DB_FILE = PROJECT_DIR / "db" / "custom.db"
DOMAIN = "eli.virtualabdigital.com"
REMOTE_BASE = "/opt/eli"

GREEN = "\033[0;32m"
RED = "\033[0;31m"
NC = "\033[0m"


def log(msg):
    print(f"{GREEN}[deploy]{NC} {msg}")


def err(msg):
    print(f"{RED}[error]{NC} {msg}", file=sys.stderr)
    sys.exit(1)


def run_ssh(ssh: SSHClient, cmd: str, timeout: int = 120) -> str:
    """Run a command over SSH, print output, return combined stdout+stderr."""
    print(f"  $ {cmd[:120]}{'...' if len(cmd)>120 else ''}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors="replace")
    err_out = stderr.read().decode(errors="replace")
    if out.strip():
        for line in out.strip().split("\n"):
            print(f"    {line}")
    if err_out.strip():
        for line in err_out.strip().split("\n"):
            print(f"    [stderr] {line}")
    return out + err_out


def sftp_upload_dir(sftp, local_dir: Path, remote_dir: str):
    """Recursively upload a directory via SFTP."""
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        sftp.mkdir(remote_dir)

    count = 0
    for root, dirs, files in os.walk(local_dir):
        rel = Path(root).relative_to(local_dir)
        remote_sub = f"{remote_dir}/{rel}" if str(rel) != "." else remote_dir
        for d in dirs:
            try:
                sftp.stat(f"{remote_sub}/{d}")
            except FileNotFoundError:
                sftp.mkdir(f"{remote_sub}/{d}")
        for f in files:
            local_path = Path(root) / f
            remote_path = f"{remote_sub}/{f}"
            sftp.put(str(local_path), remote_path)
            count += 1
            if count % 50 == 0:
                print(f"    ...uploaded {count} files")
    return count


def main():
    if len(sys.argv) < 3:
        err(f"Usage: {sys.argv[0]} <IP> <PASSWORD>")

    ip = sys.argv[1]
    password = sys.argv[2]

    # Validate local build exists
    if not STANDALONE_DIR.exists():
        err(f"No standalone build found at {STANDALONE_DIR}. Run 'bun run build' first.")
    if not KNOWLEDGE_DIR.exists():
        err(f"No knowledge directory at {KNOWLEDGE_DIR}")

    # ─── Step 1: Connect ───────────────────────────────
    log(f"Connecting to root@{ip}...")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh.connect(ip, port=22, username="root", password=password, timeout=15)
    except Exception as e:
        err(f"Connection failed: {e}")
    log("  Connected.")

    sftp = ssh.open_sftp()

    # ─── Step 2: Prepare server ─────────────────────────
    log("Step 1/5: Preparing server...")
    run_ssh(ssh, f"mkdir -p {REMOTE_BASE}/{{data/uploads/knowledge-sources,data/uploads/docs,data/uploads/design,data/uploads/zips,data/keyword-research,data/eli-os-delivery/skill-templates,db,logs,app}}")

    # Check/install bun
    bun_check = run_ssh(ssh, "which bun 2>/dev/null && bun --version || echo 'NOT_FOUND'")
    if "NOT_FOUND" in bun_check:
        log("  Installing bun...")
        run_ssh(ssh, "curl -fsSL https://bun.sh/install | bash", timeout=60)
    else:
        log(f"  Bun already installed: {bun_check.strip()}")

    # ─── Step 3: Upload files ───────────────────────────
    log("Step 2/5: Uploading app standalone build...")
    count_app = sftp_upload_dir(sftp, STANDALONE_DIR, f"{REMOTE_BASE}/app")
    log(f"  Uploaded {count_app} app files.")

    log("Step 3/5: Uploading knowledge base...")
    count_kb = sftp_upload_dir(sftp, KNOWLEDGE_DIR, f"{REMOTE_BASE}/data/uploads/knowledge-sources")
    log(f"  Uploaded {count_kb} knowledge files.")

    log("Step 3b/5: Uploading keyword research data...")
    if KEYWORD_DIR.exists():
        count_kw = sftp_upload_dir(sftp, KEYWORD_DIR, f"{REMOTE_BASE}/data/keyword-research")
        log(f"  Uploaded {count_kw} keyword files.")
    else:
        log("  No keyword directory found, skipping.")

    log("Step 3c/5: Uploading skill templates...")
    if SKILLS_DIR.exists():
        count_sk = sftp_upload_dir(sftp, SKILLS_DIR, f"{REMOTE_BASE}/data/eli-os-delivery/skill-templates")
        log(f"  Uploaded {count_sk} skill files.")
    else:
        log("  No skill templates found, skipping.")

    log("Uploading database...")
    sftp.put(str(DB_FILE), f"{REMOTE_BASE}/db/custom.db")
    log("  Database uploaded.")

    # ─── Step 4: Systemd service ────────────────────────
    log("Step 4/5: Creating systemd service...")
    service_content = f"""[Unit]
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

    # Write service file via SFTP
    import tempfile
    svc_tmp = tempfile.mktemp(suffix=".service")
    with open(svc_tmp, "w") as f:
        f.write(service_content)
    sftp.put(svc_tmp, "/etc/systemd/system/eli.service")
    os.unlink(svc_tmp)

    run_ssh(ssh, "systemctl daemon-reload && systemctl enable eli")

    # ─── Step 5: Caddy ──────────────────────────────────
    log("Step 5/5: Configuring Caddy...")
    caddy_check = run_ssh(ssh, "which caddy 2>/dev/null && caddy version || echo 'NOT_FOUND'")
    if "NOT_FOUND" in caddy_check:
        log("  Installing Caddy...")
        run_ssh(ssh, "apt-get update -qq && apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https curl", timeout=120)
        run_ssh(ssh, "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg", timeout=30)
        run_ssh(ssh, "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list", timeout=30)
        run_ssh(ssh, "apt-get update -qq && apt-get install -y -qq caddy", timeout=120)
    else:
        log(f"  Caddy already installed: {caddy_check.strip()}")

    caddyfile_content = f"""{{
\temail aiseo.virtualabdigital.com
}}

{DOMAIN} {{
\treverse_proxy localhost:3000 {{
\t\theader_up Host {{host}}
\t\theader_up X-Forwarded-For {{remote_host}}
\t\theader_up X-Forwarded-Proto {{scheme}}
\t\theader_up X-Real-IP {{remote_host}}
\t}}

\t@static path /logo.svg /robots.txt
\theader @static Cache-Control "public, max-age=86400"

\theader {{
\t\tX-Frame-Options "DENY"
\t\tX-Content-Type-Options "nosniff"
\t\tReferrer-Policy "strict-origin-when-cross-origin"
\t}}
}}
"""

    caddy_tmp = tempfile.mktemp(suffix="_Caddyfile")
    with open(caddy_tmp, "w") as f:
        f.write(caddyfile_content)
    sftp.put(caddy_tmp, "/etc/caddy/Caddyfile")
    os.unlink(caddy_tmp)

    # ─── Step 6: Start everything ───────────────────────
    log("Starting Eli...")
    run_ssh(ssh, "systemctl restart eli")
    time.sleep(3)

    status = run_ssh(ssh, "systemctl is-active eli")
    if "active" not in status.lower():
        err(f"Eli failed to start. Check: journalctl -u eli -n 30")
    log("  Eli is RUNNING.")

    log("Restarting Caddy...")
    run_ssh(ssh, "systemctl restart caddy")
    time.sleep(2)

    caddy_status = run_ssh(ssh, "systemctl is-active caddy")
    if "active" not in caddy_status.lower():
        err(f"Caddy failed to start. Check: journalctl -u caddy -n 30")
    log("  Caddy is RUNNING.")

    # Health check
    log("Running health check...")
    health = run_ssh(ssh, "curl -sf http://localhost:3000/api/health 2>/dev/null || echo 'HEALTH_FAIL'")
    print(f"  {health}")

    # DNS reminder
    print()
    log("=============================================")
    log(f"  Eli is deployed!")
    log(f"  URL: https://{DOMAIN}")
    log(f"  Health: https://{DOMAIN}/api/health")
    log(f"")
    log(f"  Make sure this DNS A record exists:")
    log(f"    {DOMAIN} -> {ip}")
    log(f"")
    log(f"  Caddy will auto-provision SSL from Let's Encrypt")
    log(f"  once DNS propagates (usually 1-5 minutes).")
    log("=============================================")

    sftp.close()
    ssh.close()


if __name__ == "__main__":
    main()
