from django.contrib import admin
from django.db.models import Count

from feedback.models import Message
from users.models import User


class MessageInline(admin.TabularInline):
    """Сообщения пользователя в его карточке (только просмотр истории)."""

    model = Message
    fields = ("category", "status", "created_at")
    readonly_fields = ("category", "status", "created_at")
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "role", "messages_count")
    list_display_links = ("name",)
    list_editable = ("role",)
    search_fields = ("name", "email")
    list_filter = ("role",)
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id",)
    inlines = (MessageInline,)

    def get_queryset(self, request):
        # Количество сообщений считается в самом запросе списка.
        return super().get_queryset(request).annotate(
            total_messages=Count("messages"),
        )

    @admin.display(description="Сообщений", ordering="total_messages")
    def messages_count(self, obj):
        return obj.total_messages
