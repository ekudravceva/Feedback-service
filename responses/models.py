from django.db import models
from django.utils import timezone

from feedback.models import Message


class Response(models.Model):
    """Ответ администратора на сообщение пользователя."""

    # Удаление сообщения запрещено, пока на него есть ответ.
    message = models.ForeignKey(
        Message,
        on_delete=models.PROTECT,
        related_name="responses",
        verbose_name="Сообщение",
    )
    text = models.TextField(
        verbose_name="Текст ответа",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    def __str__(self):
        return f"Ответ №{self.pk} на сообщение №{self.message_id}"

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        constraints = [
            # Одно сообщение может иметь не более одного ответа.
            models.UniqueConstraint(
                fields=["message"],
                name="unique_response_per_message",
            ),
        ]
