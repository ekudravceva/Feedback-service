from django.urls import reverse

from db.testing import TempDatabaseTestCase


class ResponseViewsTests(TempDatabaseTestCase):
    def test_list(self):
        response = self.client.get(reverse("responses:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_list.html")
        self.assertContains(response, "Всего ответов: 1")

    def test_list_empty(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM responses")
        conn.commit()
        conn.close()
        response = self.client.get("/responses/")
        self.assertContains(response, "Ответы не найдены.")

    def test_detail_shows_joined_data(self):
        response = self.client.get(reverse("responses:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "responses/response_detail.html")
        self.assertContains(response, "Починим")
        self.assertContains(response, "Сергей Сергеев")
        self.assertContains(response, "Не могу авторизоваться")
        self.assertContains(response, reverse("feedback:detail", args=[2]))

    def test_detail_not_found(self):
        response = self.client.get("/responses/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Ответ не найден", status_code=404)
