from django.urls import path

from . import views

app_name = "responses"

urlpatterns = [
    path("", views.responses, name="list"),
    path("<int:response_id>/", views.response_detail, name="detail"),
]
