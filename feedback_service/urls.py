"""Корневая маршрутизация проекта: подключает маршруты приложений."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("messages/", include("feedback.urls")),
    path("responses/", include("responses.urls")),
]

handler404 = "homepage.views.page_not_found"
