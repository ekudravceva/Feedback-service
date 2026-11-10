from django.contrib import admin

from responses.models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "created_at")
    list_display_links = ("id",)
    search_fields = ("text", "message__text", "message__author__name")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 20
    list_select_related = ("message",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("message",)
    readonly_fields = ("id",)
