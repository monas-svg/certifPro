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

INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.staticfiles", "public"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]
ROOT_URLCONF = "public.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("DB_NAME", "certifpro"),
    "USER": os.environ.get("DB_USER", "certifpro"),
    "PASSWORD": os.environ.get("DB_PASSWORD", "certifpro"),
    "HOST": os.environ.get("DB_HOST", "postgres"),
    "PORT": int(os.environ.get("DB_PORT", "5432")),
}}
LANGUAGE_CODE = "fr-fr"; TIME_ZONE = "Africa/Douala"; USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CATALOG_URL = os.environ.get("CATALOG_URL","http://catalog-service:8001")
ORDER_URL = os.environ.get("ORDER_URL","http://order-service:8002")
PAYMENT_URL = os.environ.get("PAYMENT_URL","http://payment-service:8003")
