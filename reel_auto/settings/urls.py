# reel_auto/settings/urls.py
"""URL конфигурация проекта"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from settings.config import ADMIN_SITE_URL


urlpatterns = [
    path(ADMIN_SITE_URL, admin.site.urls),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)