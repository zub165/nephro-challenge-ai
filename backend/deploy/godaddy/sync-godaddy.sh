#!/usr/bin/env bash
# Deploy the backend to the GoDaddy VPS by file copy.
# Run FROM A WORKSTATION, not on the server:
#   bash backend/deploy/godaddy/sync-godaddy.sh
#   bash backend/deploy/godaddy/sync-godaddy.sh --seed
#
# The VPS is not a git checkout: code is copied, never pulled. This script
# verifies locally, copies the code, backs up the server code + database, runs
# `migrate` + `collectstatic`, restarts the service, health-checks port 8007,
# and rolls the code back if any step fails.
#
# It deliberately opens only two SSH connections because the VPS firewall
# rate-limits rapid successive sessions.
set -euo pipefail

SSH_HOST="${SSH_HOST:-godaddy-server}"
APP_DIR="${APP_DIR:-/var/www/nephro-challenge-ai}"
GUNICORN_PORT="${GUNICORN_PORT:-8007}"
PUBLIC_HEALTH_URL="${PUBLIC_HEALTH_URL:-https://nephro-api.schedulemygroup.com/api/health/}"
SEED=0

for arg in "$@"; do
  case "$arg" in
    --seed) SEED=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPO_DIR="$(cd "$BACKEND_DIR/.." && pwd)"

cd "$BACKEND_DIR"

echo "==> Local verification"
if command -v python3 >/dev/null 2>&1; then
  python3 manage.py check
  python3 manage.py seed_board_exam --dry-run >/dev/null
  echo "check and seed validation passed"
else
  echo "python3 not found; skipping local checks" >&2
fi

echo "==> Copying code to $SSH_HOST (connection 1/2)"
# The board exam validator resolves animation assets at <repo>/web/public/animations
# and medical assets at <repo>/web/public/medical, so the web assets ship alongside
# the backend in the same repo-relative layout.
COPYFILE_DISABLE=1 tar -czf - \
  -C "$REPO_DIR" \
  --exclude='backend/venv' \
  --exclude='backend/.env' \
  --exclude='backend/.env.*' \
  --exclude='backend/media' \
  --exclude='backend/static' \
  --exclude='*/__pycache__' \
  --exclude='*.pyc' \
  --exclude='backend/db.sqlite3' \
  --exclude='*.log' \
  backend web/public/animations web/public/medical \
  | ssh "$SSH_HOST" 'rm -rf /tmp/nephro-stage && mkdir -p /tmp/nephro-stage && tar -xzf - -C /tmp/nephro-stage'

echo "==> Backup, install, migrate, restart (connection 2/2)"
ssh "$SSH_HOST" "APP_DIR='$APP_DIR' GUNICORN_PORT='$GUNICORN_PORT' SEED='$SEED' bash -s" <<'REMOTE'
set -euo pipefail

STAGE=/tmp/nephro-stage
BACKEND="$APP_DIR/backend"
TREE="backend"
[ -d "$APP_DIR/web" ] && TREE="$TREE web"

if [ ! -d "$STAGE/backend" ]; then
  echo "staged code missing" >&2
  exit 1
fi
if find "$STAGE" -name '.env*' | grep -q .; then
  echo "refusing to install: an env file was staged" >&2
  exit 1
fi

echo "==> Backing up server code and database"
BACKUP_DIR="/var/backups/nephro/$(date -u +%Y%m%dT%H%M%SZ)"
sudo mkdir -p "$BACKUP_DIR"
cd "$BACKEND"
DB_NAME=$(grep -E '^DB_NAME=' .env | cut -d= -f2-)
DB_USER=$(grep -E '^DB_USER=' .env | cut -d= -f2-)
DB_PASS=$(grep -E '^DB_PASSWORD=' .env | cut -d= -f2-)
DB_HOST=$(grep -E '^DB_HOST=' .env | cut -d= -f2-)
DB_PORT=$(grep -E '^DB_PORT=' .env | cut -d= -f2-)
if [ -n "$DB_NAME" ] && [ -n "$DB_USER" ] && [ -n "$DB_PASS" ]; then
  sudo -E env PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Fc -f "$BACKUP_DIR/db.dump"
  pg_restore -l "$BACKUP_DIR/db.dump" >/dev/null
  echo "database dumped and verified"
else
  echo "DB_* not found in .env; skipping database dump" >&2
fi
sudo tar --exclude=backend/venv --exclude=backend/media --exclude=backend/static \
  --exclude=__pycache__ -czf "$BACKUP_DIR/code.tar.gz" -C "$APP_DIR" $TREE
echo "backup stored at $BACKUP_DIR"

rollback() {
  echo "!! FAILURE - ROLLING BACK CODE !!" >&2
  sudo tar -xzf "$BACKUP_DIR/code.tar.gz" -C "$APP_DIR"
  sudo chown -R www-data:www-data "$BACKEND"
  sudo systemctl restart nephro-api || true
  sleep 5
  systemctl is-active nephro-api || true
  rm -rf "$STAGE"
}
trap rollback ERR

echo "==> Installing code"
sudo cp -a "$STAGE/backend/." "$BACKEND/"
if [ -d "$STAGE/web/public/animations" ]; then
  sudo mkdir -p "$APP_DIR/web/public"
  sudo cp -a "$STAGE/web/public/animations" "$APP_DIR/web/public/"
  echo "animation assets installed ($(ls "$STAGE/web/public/animations" | wc -l) files)"
fi
if [ -d "$STAGE/web/public/medical" ]; then
  sudo mkdir -p "$APP_DIR/web/public"
  rm -rf "$APP_DIR/web/public/medical"
  sudo cp -a "$STAGE/web/public/medical" "$APP_DIR/web/public/"
  echo "medical assets installed ($(find "$APP_DIR/web/public/medical" -type f | wc -l) files)"
fi
sudo find "$BACKEND/api" "$BACKEND/nephro_challenge" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
sudo chown -R www-data:www-data "$BACKEND"

echo "==> Django check + migrate (never makemigrations on the server)"
cd "$BACKEND"
sudo -u www-data venv/bin/python manage.py check
sudo -u www-data venv/bin/python manage.py migrate --noinput
sudo -u www-data venv/bin/python manage.py collectstatic --noinput | tail -1

if [ "$SEED" = "1" ]; then
  echo "==> Seeding board exam content (stays unpublished until clinician review)"
  sudo -u www-data venv/bin/python manage.py seed_board_exam
fi

echo "==> Restart"
sudo systemctl restart nephro-api
sleep 7
systemctl is-active nephro-api
systemctl is-enabled nephro-api
curl -fsS -o /dev/null -w "local_health=%{http_code}\n" "http://127.0.0.1:${GUNICORN_PORT}/api/health/"

trap - ERR
rm -rf "$STAGE"
echo "REMOTE_OK"
REMOTE

echo "==> Public health check"
curl -fsS -o /dev/null -w "public=%{http_code}\n" "$PUBLIC_HEALTH_URL"

echo "Deploy complete."
