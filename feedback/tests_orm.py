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
        self.assertEqual(
            self.client.get(
                reverse("feedback:detail", kwargs={"slug": "zhaloba-999"})
            ).status_code, 404
        )
        self.assertEqual(
            self.client.get(reverse("responses:detail", args=[999])).status_code,
            404,
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


class ManagerSlugGeneratedFieldTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(name="Анна", email="a@x.ru")
        cls.new = Message.objects.create(
            author=cls.user, category="Жалоба", text="короткий",
            created_at=aware(2026, 9, 1),
        )
        cls.processing = Message.objects.create(
            author=cls.user, category="Общее", text="в работе",
            status=Message.Status.PROCESSING, created_at=aware(2026, 9, 2),
        )
        cls.closed = Message.objects.create(
            author=cls.user, category="Предложение", text="x" * 200,
            status=Message.Status.CLOSED, created_at=aware(2026, 9, 2),
        )
        Response.objects.create(message=cls.closed, text="ответ")

    def test_manager_methods(self):
        self.assertEqual(list(Message.objects.new()), [self.new])
        self.assertEqual(list(Message.objects.processing()), [self.processing])
        self.assertEqual(list(Message.objects.closed()), [self.closed])
        self.assertEqual(Message.objects.count(), 3)
        selected = datetime(2026, 9, 2).date()
        self.assertEqual(Message.objects.for_date(selected).count(), 2)
        self.assertEqual(
            Message.objects.for_date(selected).closed().count(), 1
        )
        self.assertEqual(
            set(Message.objects.unanswered()), {self.new, self.processing}
        )

    def test_slug_is_transliterated_and_unique(self):
        self.assertEqual(self.new.slug, f"zhaloba-{self.new.pk}")
        self.assertEqual(
            self.new.get_absolute_url(), f"/messages/zhaloba-{self.new.pk}/"
        )
        slugs = Message.objects.values_list("slug", flat=True)
        self.assertEqual(len(set(slugs)), 3)
        response = self.client.get(self.new.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_slug_is_not_changed_on_save(self):
        old_slug = self.new.slug
        self.new.category = "Общее"
        self.new.save()
        self.new.refresh_from_db()
        self.assertEqual(self.new.slug, old_slug)

    def test_generated_field_is_long(self):
        self.new.refresh_from_db()
        self.closed.refresh_from_db()
        self.assertFalse(self.new.is_long)
        self.assertTrue(self.closed.is_long)
        self.new.text = "y" * 300
        self.new.save()
        self.new.refresh_from_db()
        self.assertTrue(self.new.is_long)


class ContextProcessorTestCase(TestCase):
    def test_site_name_and_count_in_context(self):
        user = User.objects.create(name="Анна", email="a@x.ru")
        Message.objects.create(author=user, category="Общее", text="т")
        response = self.client.get(reverse("homepage:index"))
        self.assertEqual(response.context["site_name"], "Сервис обратной связи")
        self.assertEqual(response.context["messages_count"], 1)
        self.assertContains(response, "Сообщения (1)")


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User as AuthUser

        AuthUser.objects.create_superuser("root", "r@x.ru", "pass12345")
        cls.user = User.objects.create(name="Анна", email="a@x.ru")
        cls.message = Message.objects.create(
            author=cls.user, category="Жалоба", text="Не работает вход",
        )
        Response.objects.create(message=cls.message, text="ответ")

    def setUp(self):
        self.client.login(username="root", password="pass12345")

    def test_changelists_and_search(self):
        for name, query in (
            ("users_user", "Анна"),
            ("feedback_message", "Анна"),
            ("responses_response", "вход"),
        ):
            url = reverse(f"admin:{name}_changelist")
            self.assertEqual(self.client.get(url).status_code, 200)
            response = self.client.get(url, {"q": query})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["cl"].result_count, 1)

    def test_change_pages_with_inlines(self):
        for name, obj in (
            ("users_user", self.user), ("feedback_message", self.message),
        ):
            url = reverse(f"admin:{name}_change", args=[obj.pk])
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_actions(self):
        url = reverse("admin:feedback_message_changelist")
        self.client.post(url, {
            "action": "close_messages", "_selected_action": [self.message.pk],
        })
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.CLOSED)
        self.client.post(url, {
            "action": "return_to_processing",
            "_selected_action": [self.message.pk],
        })
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.PROCESSING)
