from django.db import models


class User(models.Model):
    """Пользователь сервиса обратной связи (не модель аутентификации Django)."""

    ROLE_USER = "user"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_USER, "Пользователь"),
        (ROLE_ADMIN, "Администратор"),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name="Роль",
        help_text="Только пользователь с ролью «Пользователь» может создавать сообщения.",
    )

    def get_role_description(self):
        return self.get_role_display()

    def can_create_message(self):
        return self.role == self.ROLE_USER

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
