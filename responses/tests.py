from django.urls import reverse

from db.testing import SampleDataTestCase
from feedback.models import Message
from responses.models import Response


class ResponseViewsTests(SampleDataTestCase):
    def test_list(self):
        response = self.client.get(reverse("responses:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_list.html")
        self.assertContains(response, "Всего ответов: 1")

    def test_list_empty(self):
        Response.objects.all().delete()
        response = self.client.get("/responses/")
        self.assertContains(response, "Ответы не найдены.")

    def test_detail_shows_joined_data(self):
        response = self.client.get(reverse("responses:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_detail.html")
        self.assertContains(response, "Починим")
        self.assertContains(response, "Сергей Сергеев")
        self.assertContains(response, "Не могу авторизоваться")
        self.assertContains(response, Message.objects.get(pk=2).get_absolute_url())

    def test_detail_not_found(self):
        response = self.client.get("/responses/999/")
        self.assertEqual(response.status_code, 404)
