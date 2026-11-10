from django.contrib import admin, messages

from feedback.models import Message
from responses.models import Response


class ResponseInline(admin.TabularInline):
    """Ответ на сообщение в карточке сообщения (только просмотр)."""

    model = Response
    fields = ("text", "created_at")
    readonly_fields = ("text", "created_at")
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id", "author", "category", "status", "created_at", "is_long",
    )
    list_display_links = ("id",)
    list_filter = ("status", "category", "created_at")
    search_fields = ("author__name", "text")
    ordering = ("-created_at",)
    list_per_page = 20
    list_select_related = ("author",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("author",)
    readonly_fields = ("id", "is_long")
    actions = ("close_messages", "return_to_processing")
    inlines = (ResponseInline,)

    @admin.action(description="Закрыть выбранные сообщения")
    def close_messages(self, request, queryset):
        count = 0
        for message in queryset:
            message.mark_closed()
            count += 1
        self.message_user(
            request, f"Закрыто сообщений: {count}.", messages.SUCCESS,
        )

    @admin.action(description="Вернуть в обработку")
    def return_to_processing(self, request, queryset):
        updated = queryset.update(status=Message.Status.PROCESSING)
        self.message_user(
            request, f"Возвращено в обработку: {updated}.", messages.SUCCESS,
        )
