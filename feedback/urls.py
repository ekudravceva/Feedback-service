from django.urls import path

from . import views

urlpatterns = [
    path("", views.messages, name="messages"),
    path("<int:message_id>/", views.message_detail, name="message_detail"),
]
