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

echo "==> Pull latest code"
git -C "$APP_DIR" pull --ff-only

echo "==> Install dependencies"
cd "$BACKEND"
source venv/bin/activate
pip install -r requirements.txt

echo "==> Migrate + static"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "==> Seed data + sync medical references"
python manage.py seed_data
python manage.py verify_medical_content --sync-db

echo "==> Restart API"
systemctl restart nephro-api
systemctl status nephro-api --no-pager

GUNICORN_PORT="${GUNICORN_PORT:-8007}"

echo "==> Health check"
curl -fsS "http://127.0.0.1:${GUNICORN_PORT}/api/health/" \
  || curl -fsS "https://api.nephrochallenge.ai/api/health/" || true
echo ""
echo "Deploy complete."
