from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class ResponseViewsTests(TestCase):
    def test_list(self):
        response = self.client.get(reverse("responses:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_list.html")
        self.assertContains(response, "Всего ответов:")

    def test_list_empty(self):
        with patch("responses.views._load_responses", return_value=[]):
            response = self.client.get("/responses/")
        self.assertContains(response, "Ответы не найдены.")

    def test_detail(self):
        response = self.client.get(reverse("responses:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_detail.html")
        self.assertContains(response, "Починим")
        self.assertContains(response, reverse("feedback:detail", args=[2]))

    def test_detail_not_found(self):
        response = self.client.get("/responses/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Ответ не найден", status_code=404)
