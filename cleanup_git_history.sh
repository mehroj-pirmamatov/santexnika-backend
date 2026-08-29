#!/bin/bash
# =====================================================================
# Git History Cleanup Script for Santexnika Backend
# Removes hardcoded secrets and deploy_remote.py from all Git commit history
# =====================================================================

set -e

echo "=== Git History Cleaning Process ==="

# Step 1: Ensure git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "git-filter-repo is not installed. Installing via apt/pip..."
    sudo apt-get update -qq && sudo apt-get install -y git-filter-repo || pip install --break-system-packages git-filter-repo || true
fi


# Step 2: Remove sensitive files from entire git history
echo "Removing deploy_remote.py from git history..."
git filter-repo --invert-paths --path deploy_remote.py --force

# Step 3: Replace any plaintext passwords/IPs across all commits if needed
cat << 'EOF' > expressions.txt
regex:169\.58\.252\.104==>SERVER_IP_REMOVED
regex:qArshi2020i==>PASSWORD_REMOVED
EOF

git filter-repo --replace-text expressions.txt --force
rm expressions.txt

echo ""
echo "=== Git History Cleaning Complete! ==="
echo "To purge historical secrets from your GitHub repository, execute:"
echo "  git remote add origin https://github.com/mehroj-pirmamatov/santexnika-backend.git"
echo "  git push origin --force --all"
echo "  git push origin --force --tags"
