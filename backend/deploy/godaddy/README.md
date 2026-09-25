# Deploy Backend to GoDaddy VPS

Frontend stays on **GitHub Pages**: https://zub165.github.io/nephro-challenge-ai/  
Backend runs on **GoDaddy VPS**: https://nephro-api.schedulemygroup.com

There is no DNS A record for `api.nephrochallenge.ai`; every deploy file in this
repo uses the live host `nephro-api.schedulemygroup.com`. `deploy/nginx/api.nephrochallenge.ai.conf`
is a blueprint only — do not install it until that record actually exists.

## Prerequisites

1. GoDaddy VPS (Ubuntu 22.04+ recommended) with SSH access
2. DNS **A record**: `nephro-api.schedulemygroup.com` → your VPS public IP
3. Ports **80** and **443** open in GoDaddy firewall

## Port

Gunicorn listens on **`127.0.0.1:8007`** (not 8000 — that port is used by another app on the VPS).

Set `GUNICORN_PORT` in `backend/.env` if you need a different free port. Nginx proxies HTTPS → that port.

## One-time install (on VPS)

SSH into your server:

```bash
ssh root@YOUR_VPS_IP
```

Clone and run installer:

```bash
git clone https://github.com/zub165/nephro-challenge-ai.git /var/www/nephro-challenge-ai
cd /var/www/nephro-challenge-ai/backend
sudo bash deploy/godaddy/install.sh
```

Or set a custom DB password:

```bash
sudo DB_PASS='your-strong-password' bash deploy/godaddy/install.sh
```

## After install

| URL | Purpose |
|-----|---------|
| https://nephro-api.schedulemygroup.com/api/health/ | Health check |
| https://nephro-api.schedulemygroup.com/api/docs/ | Swagger API docs |
| https://nephro-api.schedulemygroup.com/admin/ | Django admin |

No default admin credentials are created. Create a superuser on the VPS:

```bash
cd /var/www/nephro-challenge-ai/backend
source venv/bin/activate
python manage.py createsuperuser
```

## Update after code changes

The VPS is **not** a git checkout and must never be updated with `git pull`.

From a workstation, run the one-shot sync script. It verifies the local code,
stages it, copies it, backs up the database and code on the server, runs
`migrate` + `collectstatic`, restarts the service, health-checks port 8007, and
rolls back automatically on any failure:

```bash
bash backend/deploy/godaddy/sync-godaddy.sh            # deploy
bash backend/deploy/godaddy/sync-godaddy.sh --seed     # also seed (unpublished)
```

If you prefer to copy the files yourself, then finish on the server:

```bash
sudo bash /var/www/nephro-challenge-ai/backend/deploy/godaddy/deploy.sh
```

`deploy.sh` never runs `makemigrations`; generate migrations locally and copy
them with the code.

## Optional: Ollama (LLaMA AI on same VPS)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
systemctl enable ollama
```

## Troubleshooting

```bash
# API logs
sudo journalctl -u nephro-api -f

# Nginx
sudo nginx -t
sudo systemctl status nginx

# Restart everything
sudo systemctl restart nephro-api nginx
```

## TLS certificate

`install.sh` already requests a certificate for the live host:

```bash
sudo certbot --nginx -d nephro-api.schedulemygroup.com
```

Only run this for `api.nephrochallenge.ai` after its DNS A record exists.
