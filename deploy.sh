#!/bin/bash
set -e

echo "========================================================="
echo "1. GitHub-ga loyihani push qilish"
echo "========================================================="
git add .
git commit -m "Production deployment setup with Docker, Nginx, PostgreSQL, SSL" || true
git remote remove origin || true
git remote add origin https://github.com/mehroj-pirmamatov/santexnika-backend.git
git branch -M main
git push -u origin main

echo ""
echo "========================================================="
echo "2. Serverga SSH orqali ulanib deploy qilish va SSL o'rnatish"
echo "========================================================="
python3 deploy_remote.py
