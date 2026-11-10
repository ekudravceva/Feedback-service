from .models import Message


def feedback_context(request):
    """Общие данные для шаблонов: название сервиса и число сообщений."""
    return {
        "site_name": "Сервис обратной связи",
        "messages_count": Message.objects.count(),
    }
