"""Вспомогательные средства для тестов: тестовые данные в базе Django (ORM)."""

from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from feedback.models import Message
from responses.models import Response
from users.models import User

USERS = [
    (1, "Анна Иванова", "anna@example.com", "user"),
    (2, "Администратор", "admin@example.com", "admin"),
    (3, "Сергей Сергеев", "sergeev@mail.com", "user"),
]

MESSAGES = [
    (1, 1, "Техническая поддержка",
     "Не могу войти в личный кабинет, пишет ошибка 504", "новая",
     "2026-09-14 12:00"),
    (2, 3, "Жалоба", "Не могу авторизоваться", "закрыта",
     "2026-09-15 18:45"),
    (3, 1, "Общее", "<script>alert(1)</script> Вопрос по тарифам", "в обработке",
     "2026-10-19 20:22"),
]

RESPONSES = [
    (1, 2, "Починим", "2026-09-15 18:46"),
]


def _dt(value):
    return timezone.make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M"))


def create_test_data():
    """Заполнить тестовую базу Django данными через ORM."""
    for pk, name, email, role in USERS:
        User.objects.create(pk=pk, name=name, email=email, role=role)
    for pk, author_id, category, text, status, created_at in MESSAGES:
        Message.objects.create(
            pk=pk, author_id=author_id, category=category, text=text,
            status=status, created_at=_dt(created_at),
        )
    for pk, message_id, text, created_at in RESPONSES:
        Response.objects.create(
            pk=pk, message_id=message_id, text=text, created_at=_dt(created_at),
        )


class SampleDataTestCase(TestCase):
    """Базовый класс: тесты работают с одними и теми же данными в тестовой БД."""

    @classmethod
    def setUpTestData(cls):
        create_test_data()
