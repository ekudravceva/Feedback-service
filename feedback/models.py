from django.db import models
from django.utils import timezone

from users.models import User

CATEGORIES = [
    "Общее",
    "Техническая поддержка",
    "Предложение",
    "Жалоба",
]


class Message(models.Model):
    """Сообщение обратной связи, оставленное пользователем."""

    STATUS_NEW = "новая"
    STATUS_PROCESSING = "в обработке"
    STATUS_CLOSED = "закрыта"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новое сообщение"),
        (STATUS_PROCESSING, "Сообщение в обработке"),
        (STATUS_CLOSED, "Сообщение обработано"),
    ]
    CATEGORY_CHOICES = [(category, category) for category in CATEGORIES]

    # Удаление автора запрещено, пока у него есть сообщения.
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="messages",
        verbose_name="Автор",
    )
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        verbose_name="Категория",
    )
    text = models.TextField(
        verbose_name="Текст сообщения",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    def mark_closed(self):
        self.status = self.STATUS_CLOSED
        self.save(update_fields=["status"])

    def matches(self, query):
        return query.lower() in self.text.lower()

    def __str__(self):
        return f"[{self.pk}] {self.category}: {self.text[:50]}"

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
