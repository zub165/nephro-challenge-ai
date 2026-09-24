import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

_secret = os.getenv("SECRET_KEY", "")
if not _secret:
    if DEBUG:
        _secret = "django-insecure-change-me-in-production"
    else:
        raise ValueError("SECRET_KEY environment variable is required when DEBUG=False")
SECRET_KEY = _secret

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

# Production behind Nginx (GoDaddy VPS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://api.nephrochallenge.ai,https://zub165.github.io,https://nephrochallenge.ai",
    ).split(",")
    if o.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    # Local
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nephro_challenge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nephro_challenge.wsgi.application"

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,https://zub165.github.io",
    ).split(",")
    if o.strip()
]

CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "nephro_challenge"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "api.User"

AUTHENTICATION_BACKENDS = [
    "api.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Nephro Challenge AI API",
    "DESCRIPTION": "API for the Nephro Challenge AI medical quiz application",
    "VERSION": "1.3.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# GoDaddy VPS — local Ollama (OpenAI-compatible /v1 endpoint)
# Default: qwen2.5:0.5b-instruct (~397 MB, fits 4 GB VPS). ollama pull qwen2.5:0.5b-instruct
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto")  # auto | ollama | llama | openai
LLAMA_BASE_URL = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "qwen2.5:0.5b-instruct")
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "ollama")

# RAG-style learning: inject approved corrections into Ollama prompts (no fine-tuning on VPS)
AI_LEARNING_ENABLED = os.getenv("AI_LEARNING_ENABLED", "true").lower() in ("1", "true", "yes")
AI_LEARNING_MAX_CONTEXT = int(os.getenv("AI_LEARNING_MAX_CONTEXT", "8"))
AI_LEARNING_AUTO_EXPORT = os.getenv("AI_LEARNING_AUTO_EXPORT", "true").lower() in ("1", "true", "yes")


# Email (GoDaddy SMTP relay)
import os as _os
EMAIL_BACKEND = _os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = _os.getenv('EMAIL_HOST', 'dedrelay.secureserver.net')
EMAIL_PORT = int(_os.getenv('EMAIL_PORT', '25'))
EMAIL_USE_TLS = _os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = _os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = _os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = _os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = _os.getenv('DEFAULT_FROM_EMAIL', 'noreply@mywaitime.com')
SERVER_EMAIL = _os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_TIMEOUT = int(_os.getenv('EMAIL_TIMEOUT', '30'))

