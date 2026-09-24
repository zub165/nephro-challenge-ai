"""Gunicorn config for GoDaddy VPS.

Default port 8007 — avoids occupied ports on shared VPS:
  8000 (uvicorn), 8004, 8011, 8012, 8082
Override: GUNICORN_PORT=8010 in backend/.env
"""
import multiprocessing
import os

_port = os.environ.get("GUNICORN_PORT", "8007")
bind = f"127.0.0.1:{_port}"
workers = max(2, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
