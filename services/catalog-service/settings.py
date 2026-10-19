import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_env_file():
    candidates = [
        BASE_DIR.parent.parent / ".env",
        BASE_DIR.parent / ".env",
        BASE_DIR / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as env_file:
                for line in env_file:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


load_env_file()

DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes", "on"}
SECRET_KEY = os.environ.get("SECRET_KEY") or ("dev-insecure-key" if DEBUG else "change-me-in-production")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",") if os.environ.get("ALLOWED_HOSTS") else ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "catalog",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "catalog_db"),
    "USER": os.environ.get("DB_USER", "certifpro"),
    "PASSWORD": os.environ.get("DB_PASSWORD", "certifpro"),
    "HOST": os.environ.get("DB_HOST", "postgres"),
    "PORT": int(os.environ.get("DB_PORT", "5432")),
}}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}
LANGUAGE_CODE = "fr-fr"; TIME_ZONE = "Africa/Douala"; USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN", "dev-service-token")

