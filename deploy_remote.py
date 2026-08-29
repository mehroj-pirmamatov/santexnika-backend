#!/usr/bin/env python3
"""
Secure Remote Deployment Script for Santexnika Backend.

This script deploys the application to a remote Linux server using SSH Key authentication.
NO IP ADDRESSES, PASSWORDS, OR API KEYS ARE HARDCODED IN THIS SCRIPT.

Usage:
  SERVER_IP="x.x.x.x" SERVER_USER="root" python3 deploy_remote.py
"""

import os
import sys
import subprocess

# Read configuration from environment variables
SERVER_IP = os.environ.get("SERVER_IP")
SERVER_USER = os.environ.get("SERVER_USER", "root")
SSH_KEY_PATH = os.environ.get("SSH_KEY_PATH", "")
REPO_URL = os.environ.get("REPO_URL", "https://github.com/mehroj-pirmamatov/santexnika-backend.git")
REMOTE_PATH = os.environ.get("REMOTE_PATH", "/root/santexnika-backend")

def run_local(cmd, check=True):
    print(f"==> Local Exec: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"Error executing command: {res.stderr}")
        sys.exit(res.returncode)
    return res.stdout.strip()

def main():
    if not SERVER_IP:
        print("Error: SERVER_IP environment variable is not set.")
        print("Example usage: SERVER_IP='1.2.3.4' SERVER_USER='root' python3 deploy_remote.py")
        sys.exit(1)

    ssh_opts = "-o StrictHostKeyChecking=no"
    if SSH_KEY_PATH:
        ssh_opts += f" -i {SSH_KEY_PATH}"

    ssh_target = f"{SERVER_USER}@{SERVER_IP}"

    print("--- 1. Checking Git Status & Pushing to Remote ---")
    run_local("git add .")
    subprocess.run("git commit -m 'Apply security hardening and refactor add-admin endpoint'", shell=True, capture_output=True)
    run_local("git push origin main || git push origin master", check=False)

    print(f"\n--- 2. Transferring local .env to remote server ({ssh_target}) ---")
    if os.path.exists(".env"):
        scp_cmd = f"scp {ssh_opts} .env {ssh_target}:{REMOTE_PATH}/.env"
        run_local(f"ssh {ssh_opts} {ssh_target} 'mkdir -p {REMOTE_PATH}'")
        run_local(scp_cmd)
        print("Successfully uploaded local .env to server via SCP.")
    else:
        print("Warning: Local .env file not found. Ensure .env exists on remote server.")

    print(f"\n--- 3. Executing Remote Deployment over SSH ---")
    remote_script = f"""
set -e
echo "Updating remote code repository..."
if [ ! -d "{REMOTE_PATH}" ]; then
    git clone {REPO_URL} {REMOTE_PATH}
else
    cd {REMOTE_PATH}
    git fetch --all
    git reset --hard origin/main || git reset --hard origin/master
fi

cd {REMOTE_PATH}

# Ensure docker & docker compose plugin are present
if ! command -v docker >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y docker.io docker-compose-v2 certbot python3-certbot-nginx
    systemctl enable --now docker
fi

COMPOSE_BIN="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    COMPOSE_BIN="docker-compose"
fi

echo "Building and restarting Docker Compose containers..."
$COMPOSE_BIN up -d --build

echo "Deployment finished successfully!"
"""

    ssh_exec_cmd = f"ssh {ssh_opts} {ssh_target} '{remote_script}'"
    subprocess.run(ssh_exec_cmd, shell=True)

if __name__ == "__main__":
    main()
