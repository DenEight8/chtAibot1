from pathlib import Path
import os
from dotenv import load_dotenv

# Завантаження .env файлу (має бути у тій же папці, що й manage.py)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ────────────────────────── Django core ─────────────────────────── #
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key-only")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    # 3-rd party
    'rest_framework',
    "channels",
    # local
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "exeshop.urls"
ASGI_APPLICATION = "exeshop.asgi.application"

# Templates (глобальна папка + app-templates)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "shop.context_processors.base_vars",
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]

JAZZMIN_SETTINGS = {
    "site_title": "Dango Admin",
    "site_header": "Dango",
    "site_brand": "Dango",
    "welcome_sign": "Ласкаво просимо в панель керування",
    "copyright": "© 2025 Dango",
    "site_logo": "shop/img/dango_logo.svg",   # <- ваш логотип
    "site_logo_classes": "img-circle",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["shop", "auth"],
    "changeform_format": "tabs",
    "custom_css": "shop/css/admin_extra.css",
    "custom_js": "shop/js/admin_extra.js",
    "icons": {
        "shop.category": "fas fa-tags",
        "shop.product": "fas fa-box-open",
        "shop.cart": "fas fa-shopping-cart",
        "shop.cartitem": "fas fa-list",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users-cog",
    },
    "changeform_format_overrides": {  # <- і конкретно для User
        "auth.user": "tabs",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "far fa-circle",
}

# БД — SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Статика / медіа
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # для collectstatic

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Channels (In-Memory для DEV; prod — Redis через REDIS_URL)
if os.getenv("REDIS_URL"):
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.getenv("REDIS_URL", "redis://127.0.0.1:6379")],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
LOGIN_REDIRECT_URL = "shop:profile"
LOGOUT_REDIRECT_URL = "shop:home"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Додатково: вказати модель для OpenAI (можеш змінювати у .env)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Мова / час
LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
