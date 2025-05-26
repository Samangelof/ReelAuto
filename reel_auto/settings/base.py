# reel_auto/settings/base.py
# ------------------------------------------------
#! Трогать base.py можно. Желательно в перчатках.
#! Разработал @Samangelof
# ------------------------------------------------
from pathlib import Path
import os
import sys
from datetime import timedelta
from .config import (
    DEBUG,
    SECRET_KEY,
    HOST_DATEBASE,
    NAME_DATEBASE,
    USER_DATEBASE,
    PASSWORD_DATEBASE,
    PORT_DATEBASE
)


# ------------------------------------------------
# Path and hosts
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'apps'))

ALLOWED_HOSTS = ['127.0.0.1', 'localhost:8000']


# ------------------------------------------------
# Apps
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reel_auto.apps.core.apps.CoreConfig',
]


# ------------------------------------------------
# Middleware | Templates | Validators
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'settings.urls'
WSGI_APPLICATION = 'deploy.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ------------------------------------------------
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': NAME_DATEBASE,
        'USER': USER_DATEBASE,
        'PASSWORD': PASSWORD_DATEBASE,
        'HOST': HOST_DATEBASE,
        'PORT': PORT_DATEBASE,
    }
}


# ------------------------------------------------
# logging
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "simple": {
            "format": "[%(levelname)s] %(message)s"
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            # "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        "production_file": {
            "level": "WARNING",
            "filters": ["require_debug_false"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "production.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "debug_file": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "errors_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "errors.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "debug_file", "production_file", "errors_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["debug_file"] if DEBUG else [],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["production_file", "errors_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "debug_file", "production_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# ------------------------------------------------
# Jazzmin настройки
JAZZMIN_SETTINGS = {
    "site_title": "Reels Exporter",
    "site_header": "Reels Exporter Admin",
    "site_brand": "Reels Exporter",
    "welcome_sign": "Добро пожаловать в Reels Exporter",
    "search_model": ["core.SearchTask"],

    "topmenu_links": [
        {"model": "core.searchtask"},
        {"name": "Разработал Samangelof",
            "url": "https://t.me/Samangelof", "new_window": True},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "core.searchtask": "fas fa-search",
        "auth.user": "fas fa-users",
    },
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
    "hide_models": ["auth.user", "auth.group"],     # Скрываю поля в сайдбаре (Пользователи и группы)

}


# ------------------------------------------------
# Celery
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json" 


# ------------------------------------------------
# Other
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# STATIC_URL = '/static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# ------------------------------------------------
# Security settings
# MIME-sniffing и clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"


# ------------------------------------------------
# Уроню, если не будет переменных окружения
if not DEBUG:
    required_env_vars = ['DB_NAME', 'DB_HOST', 'SECRET_KEY']
    for var in required_env_vars:
        if not os.getenv(var):
            raise ValueError(f"Не задана env-переменная: {var}")
