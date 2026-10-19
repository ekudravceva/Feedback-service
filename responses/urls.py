from django.urls import path

from . import views

urlpatterns = [
    path("", views.responses, name="responses"),
    path("<int:response_id>/", views.response_detail, name="response_detail"),
]
