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
}


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
