"""Тесты моделей и ORM-запросов (ПР9)."""

from datetime import datetime

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from feedback.models import Message
from responses.models import Response
from users.models import User


def aware(year, month, day, hour=12):
    return timezone.make_aware(datetime(year, month, day, hour))


class OrmViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anna = User.objects.create(name="Анна", email="a@x.ru")
        cls.boris = User.objects.create(name="Борис", email="b@x.ru")
        cls.idle = User.objects.create(name="Без сообщений", email="i@x.ru")
        cls.m1 = Message.objects.create(
            author=cls.anna, category="Жалоба", text="Не работает ВХОД",
            created_at=aware(2026, 9, 1),
        )
        cls.m2 = Message.objects.create(
            author=cls.boris, category="Общее", text="Спасибо за сервис",
            status="закрыта", created_at=aware(2026, 9, 2),
        )
        cls.response = Response.objects.create(message=cls.m2, text="Рады")

    def page(self, **params):
        response = self.client.get(reverse("feedback:list"), params)
        self.assertEqual(response.status_code, 200)
        return response.context["page_obj"]

    def test_missing_objects_return_404(self):
        for name in ("feedback:detail", "responses:detail"):
            self.assertEqual(
                self.client.get(reverse(name, args=[999])).status_code, 404
            )

    def test_filters_exclude_and_sort(self):
        self.assertEqual(list(self.page(category="Жалоба")), [self.m1])
        self.assertEqual(list(self.page(hide_closed="1")), [self.m1])
        self.assertEqual(list(self.page(author=self.boris.pk)), [self.m2])
        self.assertEqual(list(self.page(sort="author")), [self.m1, self.m2])
        self.assertEqual(list(self.page(sort="date_asc")), [self.m1, self.m2])
        # Неизвестные значения параметров не ломают страницу.
        self.assertEqual(
            len(self.page(sort="id; DROP", status="x", page="abc")), 2
        )

    def test_pagination_keeps_params(self):
        for i in range(6):
            Message.objects.create(
                author=self.anna, category="Жалоба", text=f"т{i}"
            )
        page = self.page(category="Жалоба")
        self.assertEqual(page.paginator.num_pages, 2)
        response = self.client.get(reverse("feedback:list"), {"category": "Жалоба"})
        self.assertContains(response, "page=2")
        self.assertContains(response, "category=")

    def test_search_cyrillic_case_insensitive(self):
        url = reverse("feedback:search")
        results = self.client.get(url, {"q": "вход"}).context["results"]
        self.assertEqual(list(results), [self.m1])
        results = self.client.get(url, {"q": "БОРИС"}).context["results"]
        self.assertEqual(list(results), [self.m2])
        results = self.client.get(url, {"q": ".*"}).context["results"]
        self.assertEqual(list(results), [])
        response = self.client.get(url, {"date_from": "не-дата"})
        self.assertTrue(response.context["date_error"])

    def test_unanswered(self):
        response = self.client.get(reverse("feedback:unanswered"))
        self.assertEqual(list(response.context["messages_list"]), [self.m1])

    def test_statistics(self):
        context = self.client.get(reverse("feedback:statistics")).context
        self.assertEqual(context["total"]["messages_count"], 2)
        self.assertEqual(context["unanswered_count"], 1)
        names = [row["author_name"] for row in context["by_author"]]
        self.assertIn("Без сообщений", names)
        self.assertEqual(list(context["active_authors"]), [])
        response = self.client.get(reverse("feedback:statistics"), {"more_than": "0"})
        self.assertEqual(len(response.context["active_authors"]), 2)

    def test_statistics_empty_database(self):
        Response.objects.all().delete()
        Message.objects.all().delete()
        response = self.client.get(reverse("feedback:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"]["messages_count"], 0)


class ModelsTestCase(TestCase):
    def test_crud_and_constraints(self):
        user = User.objects.create(name="Анна", email="a@x.ru")
        self.assertTrue(user.can_create_message())
        message = Message.objects.create(author=user, category="Общее", text="текст")
        message.mark_closed()
        message.refresh_from_db()
        self.assertEqual(message.status, "закрыта")
        Response.objects.create(message=message, text="ответ")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Response.objects.create(message=message, text="второй")
        with self.assertRaises(ProtectedError):
            message.delete()
        with self.assertRaises(ProtectedError):
            user.delete()
        Response.objects.all().delete()
        message.delete()
        self.assertEqual(Message.objects.count(), 0)
