from django.urls import NoReverseMatch, reverse

from db.testing import TempDatabaseTestCase


class MessageViewsTests(TempDatabaseTestCase):
    def test_list(self):
        response = self.client.get(reverse("feedback:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback/message_list.html")
        self.assertTemplateUsed(response, "feedback/includes/message_card.html")
        self.assertTemplateUsed(response, "feedback/includes/message_status.html")
        self.assertContains(response, "Всего сообщений: 3")
        self.assertContains(response, "Анна Иванова")

    def test_list_context_contains_rows_from_sql(self):
        response = self.client.get("/messages/")
        messages = response.context["messages_list"]
        self.assertEqual(len(messages), 3)
        # Строки результата доступны по именам столбцов (sqlite3.Row).
        self.assertEqual(messages[0]["author_name"], "Анна Иванова")
        # Порядок задан ORDER BY created_at DESC: самое новое сообщение первое.
        self.assertEqual([m["id"] for m in messages], [3, 2, 1])

    def test_list_empty(self):
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM responses")
        conn.execute("DELETE FROM messages")
        conn.commit()
        conn.close()
        response = self.client.get("/messages/")
        self.assertContains(response, "Сообщения не найдены.")

    def test_detail(self):
        response = self.client.get(reverse("feedback:detail", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback/message_detail.html")
        self.assertContains(response, "Анна Иванова")
        self.assertContains(response, "ответа пока нет")

    def test_detail_with_response_link(self):
        response = self.client.get("/messages/2/")
        self.assertContains(response, reverse("responses:detail", args=[1]))

    def test_detail_not_found(self):
        response = self.client.get("/messages/999/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(
            response, "Сообщение не найдено", status_code=404
        )

    def test_non_int_id_is_not_routed(self):
        self.assertEqual(self.client.get("/messages/abc/").status_code, 404)
        with self.assertRaises(NoReverseMatch):
            reverse("feedback:detail", args=["abc"])

    def test_sql_injection_in_url_is_not_possible(self):
        response = self.client.get("/messages/1 OR 1=1/")
        self.assertEqual(response.status_code, 404)

    def test_html_in_text_is_escaped(self):
        response = self.client.get("/messages/3/")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_status_include_variants(self):
        for message_id, css in (
            (1, "message-status-new"),
            (3, "message-status-processing"),
            (2, "message-status-closed"),
        ):
            response = self.client.get(f"/messages/{message_id}/")
            self.assertContains(response, css)

    def test_unanswered(self):
        response = self.client.get(reverse("feedback:unanswered"))
        self.assertEqual(response.status_code, 200)
        ids = [m["id"] for m in response.context["messages_list"]]
        self.assertEqual(ids, [1, 3])
        self.assertContains(response, "Всего: 2")


class MessageSearchTests(TempDatabaseTestCase):
    def search(self, **params):
        return self.client.get(reverse("feedback:search"), params)

    def ids(self, response):
        return [m["id"] for m in response.context["results"]]

    def test_form_without_parameters_does_not_query(self):
        response = self.search()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["searched"])
        self.assertContains(response, "Задайте одно или несколько условий")

    def test_by_category(self):
        self.assertEqual(self.ids(self.search(category="Жалоба")), [2])

    def test_by_status(self):
        self.assertEqual(self.ids(self.search(status="новая")), [1])

    def test_by_text_is_case_insensitive_for_cyrillic(self):
        self.assertEqual(self.ids(self.search(q="НЕ МОГУ")), [2, 1])
        self.assertEqual(self.ids(self.search(q="не могу")), [2, 1])

    def test_by_date(self):
        self.assertEqual(self.ids(self.search(date_from="2026-10-01")), [3])

    def test_several_conditions(self):
        response = self.search(q="не могу", status="закрыта")
        self.assertEqual(self.ids(response), [2])

    def test_nothing_found(self):
        response = self.search(q="такого нет")
        self.assertEqual(self.ids(response), [])
        self.assertContains(response, "По заданным условиям сообщений не найдено.")

    def test_invalid_date_is_ignored(self):
        response = self.search(date_from="abc", category="Жалоба")
        self.assertTrue(response.context["date_error"])
        self.assertEqual(self.ids(response), [2])

    def test_sql_injection_is_treated_as_text(self):
        response = self.search(q="' OR '1'='1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ids(response), [])


class StatisticsTests(TempDatabaseTestCase):
    def test_statistics(self):
        response = self.client.get(reverse("feedback:statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "feedback/statistics.html")
        self.assertEqual(response.context["total"]["messages_count"], 3)
        self.assertEqual(
            response.context["unanswered_count"]["unanswered_count"], 2
        )
        by_status = {
            row["status"]: row["messages_count"]
            for row in response.context["by_status"]
        }
        self.assertEqual(
            by_status, {"новая": 1, "закрыта": 1, "в обработке": 1}
        )

    def test_authors_include_those_without_messages(self):
        response = self.client.get("/messages/statistics/")
        authors = {
            row["author_name"]: row["messages_count"]
            for row in response.context["by_author"]
        }
        self.assertEqual(authors["Администратор"], 0)
        self.assertEqual(authors["Анна Иванова"], 2)

    def test_having_threshold(self):
        response = self.client.get("/messages/statistics/", {"more_than": 1})
        names = [r["author_name"] for r in response.context["active_authors"]]
        self.assertEqual(names, ["Анна Иванова"])
        response = self.client.get("/messages/statistics/", {"more_than": 2})
        self.assertEqual(response.context["active_authors"], [])
        self.assertContains(response, "Нет авторов")

    def test_invalid_threshold_falls_back_to_default(self):
        response = self.client.get("/messages/statistics/", {"more_than": "x"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["more_than"], 1)
