"""Корневая маршрутизация проекта: подключает маршруты приложений."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("messages/", include("feedback.urls")),
    path("responses/", include("responses.urls")),
]

# Маршруты панели отладки подключаются только в режиме отладки.
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

handler404 = "homepage.views.page_not_found"
