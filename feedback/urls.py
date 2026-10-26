from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.messages, name="list"),
    path("search/", views.search, name="search"),
    path("unanswered/", views.unanswered, name="unanswered"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:message_id>/", views.message_detail, name="detail"),
]
