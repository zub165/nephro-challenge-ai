#!/usr/bin/env bash
# First-time GoDaddy VPS setup for Nephro Challenge AI backend.
# Run ON THE SERVER as root or with sudo:
#   curl -fsSL https://raw.githubusercontent.com/zub165/nephro-challenge-ai/main/backend/deploy/godaddy/install.sh | bash
# Or after cloning:
#   sudo bash backend/deploy/godaddy/install.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/nephro-challenge-ai}"
REPO_URL="${REPO_URL:-https://github.com/zub165/nephro-challenge-ai.git}"
API_DOMAIN="${API_DOMAIN:-api.nephrochallenge.ai}"
GUNICORN_PORT="${GUNICORN_PORT:-8007}"
DB_NAME="${DB_NAME:-nephro_challenge}"
DB_USER="${DB_USER:-nephro_app}"
DB_PASS="${DB_PASS:-}"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

if [[ -z "$DB_PASS" ]]; then
  DB_PASS="$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)"
  echo "Generated DB password: $DB_PASS"
  echo "Save this password in backend/.env as DB_PASSWORD"
fi

echo "==> Installing system packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
  python3 python3-venv python3-pip python3-dev \
  postgresql postgresql-contrib \
  nginx certbot python3-certbot-nginx \
  git build-essential libpq-dev

echo "==> PostgreSQL database"
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
  || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true

echo "==> Application files"
mkdir -p "$(dirname "$APP_DIR")"
if [[ -f "$APP_DIR/backend/manage.py" ]]; then
  echo "Using existing files at $APP_DIR"
elif [[ ! -d "$APP_DIR/.git" ]]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull --ff-only || true
fi

BACKEND="$APP_DIR/backend"
cd "$BACKEND"

echo "==> Python virtualenv"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Environment file"
if [[ ! -f .env ]]; then
  cp .env.godaddy.example .env
  SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
  sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=$DB_PASS|" .env
  sed -i "s|^DB_USER=.*|DB_USER=$DB_USER|" .env
  sed -i "s|^GUNICORN_PORT=.*|GUNICORN_PORT=$GUNICORN_PORT|" .env
  echo "Created $BACKEND/.env — review before going live."
fi

echo "==> Django migrate + seed"
python manage.py migrate --noinput
python manage.py seed_data || true
python manage.py collectstatic --noinput

echo "==> Permissions"
chown -R www-data:www-data "$APP_DIR"
chmod -R u+rwX,g+rwX "$BACKEND/media" "$BACKEND/static" 2>/dev/null || true

echo "==> Systemd service"
cp deploy/systemd/nephro-api.service /etc/systemd/system/nephro-api.service
systemctl daemon-reload
systemctl enable nephro-api
systemctl restart nephro-api

echo "==> Nginx (Gunicorn on port $GUNICORN_PORT, HTTP first for Certbot)"
cat > "/etc/nginx/sites-available/$API_DOMAIN.conf" <<NGINX_EOF
upstream nephro_api {
    server 127.0.0.1:$GUNICORN_PORT;
}

server {
    listen 80;
    server_name $API_DOMAIN;

    client_max_body_size 20M;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /static/ {
        alias $BACKEND/static/;
        expires 30d;
    }

    location /media/ {
        alias $BACKEND/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://nephro_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
NGINX_EOF
mkdir -p /var/www/certbot
ln -sf "/etc/nginx/sites-available/$API_DOMAIN.conf" /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t
systemctl reload nginx

echo "==> SSL (Let's Encrypt)"
certbot --nginx -d "$API_DOMAIN" --non-interactive --agree-tos -m "admin@nephrochallenge.com" || {
  echo "Certbot failed — point DNS A record for $API_DOMAIN to this server IP, then run:"
  echo "  sudo certbot --nginx -d $API_DOMAIN"
}

echo ""
echo "=============================================="
echo " Backend installed at $BACKEND"
echo " API URL: https://$API_DOMAIN/api/health/"
echo " Admin:   https://$API_DOMAIN/admin/"
echo " Docs:    https://$API_DOMAIN/api/docs/"
echo ""
echo " Login (seed): admin / admin123"
echo " Change admin password: python manage.py changepassword admin"
echo "=============================================="
