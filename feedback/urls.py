from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.messages, name="list"),
    path("<int:message_id>/", views.message_detail, name="detail"),
]
