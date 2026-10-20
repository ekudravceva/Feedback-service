from unittest.mock import patch

from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from models import Message, User


class MessageViewsTests(TestCase):
    def test_list(self):
        response = self.client.get(reverse("feedback:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback/message_list.html")
        self.assertTemplateUsed(response, "feedback/includes/message_card.html")
        self.assertTemplateUsed(response, "feedback/includes/message_status.html")
        self.assertContains(response, "Всего сообщений:")

    def test_list_context(self):
        response = self.client.get("/messages/")
        self.assertIn("messages_list", response.context)

    def test_list_empty(self):
        with patch("feedback.views.load_messages", return_value=[]):
            response = self.client.get("/messages/")
        self.assertContains(response, "Сообщения не найдены.")

    def test_detail(self):
        response = self.client.get(reverse("feedback:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback/message_detail.html")
        self.assertContains(response, "Анна Иванова")

    def test_detail_with_response_link(self):
        response = self.client.get("/messages/2/")
        self.assertContains(response, reverse("responses:detail", args=[1]))

    def test_detail_not_found(self):
        response = self.client.get("/messages/999/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "feedback/message_detail.html")
        self.assertContains(
            response, "Сообщение не найдено", status_code=404
        )

    def test_non_int_id_is_not_routed(self):
        self.assertEqual(self.client.get("/messages/abc/").status_code, 404)
        with self.assertRaises(NoReverseMatch):
            reverse("feedback:detail", args=["abc"])

    def test_html_in_text_is_escaped(self):
        author = User(1, "Автор", "a@example.com", "user")
        message = Message(
            1, author, "Общее", "<script>alert(1)</script> текст"
        )
        with patch("feedback.views.load_messages", return_value=[message]):
            response = self.client.get("/messages/1/")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_status_include_variants(self):
        author = User(1, "Автор", "a@example.com", "user")
        for status, css in (
            ("новая", "message-status-new"),
            ("в обработке", "message-status-processing"),
            ("закрыта", "message-status-closed"),
        ):
            message = Message(
                1, author, "Общее", "Достаточно длинный текст", status
            )
            with patch(
                "feedback.views.load_messages", return_value=[message]
            ):
                response = self.client.get("/messages/1/")
            self.assertContains(response, css)
