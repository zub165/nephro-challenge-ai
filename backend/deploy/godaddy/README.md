# Deploy Backend to GoDaddy VPS

Frontend stays on **GitHub Pages**: https://zub165.github.io/nephro-challenge-ai/  
Backend runs on **GoDaddy VPS**: https://api.nephrochallenge.ai

## Prerequisites

1. GoDaddy VPS (Ubuntu 22.04+ recommended) with SSH access
2. DNS **A record**: `api.nephrochallenge.ai` → your VPS public IP
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
| https://api.nephrochallenge.ai/api/health/ | Health check |
| https://api.nephrochallenge.ai/api/docs/ | Swagger API docs |
| https://api.nephrochallenge.ai/admin/ | Django admin |

**Test login:** `admin` / `admin123` (change immediately)

```bash
cd /var/www/nephro-challenge-ai/backend
source venv/bin/activate
python manage.py changepassword admin
```

## Update after code changes

```bash
sudo bash /var/www/nephro-challenge-ai/backend/deploy/godaddy/deploy.sh
```

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

## DNS not ready yet?

Run install anyway, then when DNS propagates:

```bash
sudo certbot --nginx -d api.nephrochallenge.ai
```
