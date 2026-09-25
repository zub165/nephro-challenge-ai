#!/usr/bin/env bash
# Update backend on GoDaddy VPS after code changes.
# Run ON THE SERVER:
#   sudo bash /var/www/nephro-challenge-ai/backend/deploy/godaddy/deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/nephro-challenge-ai}"
BACKEND="$APP_DIR/backend"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

if [[ -d "$APP_DIR/.git" ]]; then
  echo "==> WARNING: $APP_DIR is a git checkout; the VPS is updated by file copy (rsync/scp)."
  echo "==> Refusing to run 'git pull' here. Copy files from a workstation instead."
  exit 1
fi

echo "==> Install dependencies"
cd "$BACKEND"
source venv/bin/activate
pip install -r requirements.txt

echo "==> Migrate + static"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "==> Seed data + sync medical references"
if grep -q '^ADMIN_USERNAME=.' "$BACKEND/.env" && grep -q '^ADMIN_PASSWORD=.' "$BACKEND/.env"; then
  python manage.py seed_data
else
  echo "Skipping seed_data: ADMIN_USERNAME/ADMIN_PASSWORD are not set in .env"
  echo "Seed the exam content instead: python manage.py seed_board_exam"
fi
python manage.py verify_medical_content --sync-db

echo "==> Restart API"
systemctl restart nephro-api
systemctl status nephro-api --no-pager

GUNICORN_PORT="${GUNICORN_PORT:-$(grep -E '^GUNICORN_PORT=' "$BACKEND/.env" | cut -d= -f2)}"
GUNICORN_PORT="${GUNICORN_PORT:-8007}"

echo "==> Health check"
curl -fsS "http://127.0.0.1:${GUNICORN_PORT}/api/health/" \
  || curl -fsS "https://nephro-api.schedulemygroup.com/api/health/" || true
echo ""
echo "Deploy complete."
