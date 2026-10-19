from django.test import TestCase


class HomepageTests(TestCase):
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сервис обратной связи")

    def test_unknown_url_returns_custom_404(self):
        response = self.client.get("/nonexistent/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "404 – страница не найдена", status_code=404
        )
