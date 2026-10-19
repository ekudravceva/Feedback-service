from django.test import TestCase


class MessageViewsTests(TestCase):
    def test_list(self):
        response = self.client.get("/messages/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сообщения")

    def test_detail(self):
        response = self.client.get("/messages/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Анна Иванова")

    def test_detail_not_found(self):
        response = self.client.get("/messages/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "Сообщение не найдено", status_code=404
        )

    def test_non_int_id_is_not_routed(self):
        self.assertEqual(self.client.get("/messages/abc/").status_code, 404)
