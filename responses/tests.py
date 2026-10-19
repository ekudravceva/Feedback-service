from django.test import TestCase


class ResponseViewsTests(TestCase):
    def test_list(self):
        response = self.client.get("/responses/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ответы")

    def test_detail(self):
        response = self.client.get("/responses/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Починим")

    def test_detail_not_found(self):
        response = self.client.get("/responses/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Ответ не найден", status_code=404)
