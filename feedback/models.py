from django.db import models, transaction
from django.db.models.functions import Length
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode

from users.models import User

CATEGORIES = [
    "Общее",
    "Техническая поддержка",
    "Предложение",
    "Жалоба",
]

# С этой длины текста (в символах) сообщение считается длинным.
LONG_TEXT_LENGTH = 200


class MessageQuerySet(models.QuerySet):
    """Повторно используемые условия отбора сообщений."""

    def new(self):
        return self.filter(status=self.model.Status.NEW)

    def processing(self):
        return self.filter(status=self.model.Status.PROCESSING)

    def closed(self):
        return self.filter(status=self.model.Status.CLOSED)

    def for_date(self, selected_date):
        return self.filter(created_at__date=selected_date)

    def unanswered(self):
        # LEFT JOIN с ответами: остаются сообщения без ответа.
        return self.filter(responses__isnull=True)


class MessageManager(models.Manager.from_queryset(MessageQuerySet)):  # type: ignore[misc]
    """Менеджер сообщений с методами MessageQuerySet."""


class Message(models.Model):
    """Сообщение обратной связи, оставленное пользователем."""

    class Status(models.TextChoices):
        NEW = "новая", "Новое сообщение"
        PROCESSING = "в обработке", "Сообщение в обработке"
        CLOSED = "закрыта", "Сообщение обработано"

    CATEGORY_CHOICES = [(category, category) for category in CATEGORIES]

    objects = MessageManager()

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
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )
    # Вычисляется базой данных на основе длины текста.
    is_long = models.GeneratedField(
        expression=models.Case(
            models.When(
                models.lookups.GreaterThanOrEqual(
                    Length("text"), LONG_TEXT_LENGTH,
                ),
                then=models.Value(True),
            ),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Длинное сообщение",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    def save(self, *args, **kwargs):
        # slug формируется один раз: транслитерация категории и идентификатор.
        if not self.slug:
            base_slug = slugify(unidecode(self.category)) or "message"
            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                # Идентификатор появится только после первого сохранения,
                # поэтому сначала сохраняется служебный slug, затем
                # окончательный (обе записи — в одной транзакции).
                with transaction.atomic():
                    self.slug = f"{base_slug}-new"
                    super().save(*args, **kwargs)
                    self.slug = f"{base_slug}-{self.pk}"
                    super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("feedback:detail", kwargs={"slug": self.slug})

    def mark_closed(self):
        self.status = self.Status.CLOSED
        self.save(update_fields=["status"])

    def matches(self, query):
        return query.lower() in self.text.lower()

    def __str__(self):
        return f"[{self.pk}] {self.category}: {self.text[:50]}"

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
