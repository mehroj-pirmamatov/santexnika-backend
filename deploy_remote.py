#!/usr/bin/env python3
import subprocess
import os
import sys

REPO_URL = "https://github.com/mehroj-pirmamatov/santexnika-backend"
SERVER_IP = "169.58.252.104"
SERVER_PASS = "qArshi2020i"
SERVER_USER = "root"
DOMAIN = "santexnika-loyha.duckdns.org"

def run(cmd, check=True):
    print(f"==> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"Error executing command: {res.stderr}")
        sys.exit(res.returncode)
    return res.stdout.strip()

def main():
    print("--- 1. Git status & push ---")
    run("git add .")
    res = subprocess.run("git commit -m 'Setup Docker, Nginx, PostgreSQL deployment and SSL domain'", shell=True, capture_output=True, text=True)
    
    # Check remote
    remotes = run("git remote -v", check=False)
    if REPO_URL not in remotes:
        run(f"git remote add origin {REPO_URL}", check=False)
    
    print("Pushing to GitHub...")
    run("git push -u origin main || git push -u origin master", check=False)

    print("\n--- 2. Connecting to remote server and deploying ---")
    ssh_cmd = f"sshpass -p '{SERVER_PASS}' ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_IP}"
    
    remote_script = f"""
set -e
echo "Updating package list & installing docker, git, certbot if needed..."
apt-get update -y
apt-get install -y git docker.0 docker-compose certbot python3-certbot-nginx || apt-get install -y git docker.io docker-compose-plugin certbot python3-certbot-nginx

# Enable and start Docker
systemctl enable docker || true
systemctl start docker || true

# Clone or pull repository
if [ ! -d "/root/santexnika-backend" ]; then
    git clone {REPO_URL} /root/santexnika-backend
else
    cd /root/santexnika-backend
    git fetch --all
    git reset --hard origin/main || git reset --hard origin/master
fi

cd /root/santexnika-backend

# Prepare .env file
cat << 'EOF' > .env
SECRET_KEY=9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f
DATABASE_URL=postgresql://santex_user:santex_secret_pass@db:5432/santexnika_db
POSTGRES_USER=santex_user
POSTGRES_PASSWORD=santex_secret_pass
POSTGRES_DB=santexnika_db
CORS_ORIGINS=*
GUNICORN_WORKERS=4
EOF

# Ensure docker-compose is available
COMPOSE_BIN="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    COMPOSE_BIN="docker-compose"
fi

# Stop existing containers if running
$COMPOSE_BIN down || true

# Build and start services
$COMPOSE_BIN up -d --build

echo "Waiting for services to start..."
sleep 10

# Obtain & configure SSL certificate with Certbot
echo "Setting up SSL certificate for {DOMAIN}..."
certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@{DOMAIN} --redirect || echo "Certbot failed or domain not pointing to IP yet."

echo "Deployment complete! App is running at https://{DOMAIN}"
"""

    deploy_command = f"{ssh_cmd} '{remote_script}'"
    print("Executing remote deployment on server...")
    subprocess.run(deploy_command, shell=True)

if __name__ == "__main__":
    main()
