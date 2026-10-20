from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class HomepageTests(TestCase):
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сервис обратной связи")

    def test_index_uses_templates(self):
        response = self.client.get(reverse("homepage:index"))
        self.assertTemplateUsed(response, "homepage/index.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "includes/navigation.html")

    def test_unknown_url_returns_custom_404(self):
        response = self.client.get("/nonexistent/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "homepage/404.html")
        self.assertContains(
            response, "404 – страница не найдена", status_code=404
        )

    def test_navigation_links_use_named_urls(self):
        response = self.client.get("/")
        self.assertContains(response, f'href="{reverse("feedback:list")}"')
        self.assertContains(response, f'href="{reverse("responses:list")}"')

    def test_static_files_connected(self):
        response = self.client.get("/")
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/js/main.js")
        self.assertContains(response, "/static/homepage/img/logo.png")
        self.assertContains(response, 'id="current-year"')

    def test_static_files_exist(self):
        static_dir = Path(settings.BASE_DIR) / "homepage/static/homepage"
        for name in ("css/style.css", "js/main.js", "img/logo.png"):
            self.assertTrue((static_dir / name).is_file(), name)

    def test_views_do_not_build_html_in_python(self):
        for app in ("homepage", "feedback", "responses"):
            source = (Path(settings.BASE_DIR) / app / "views.py").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("page(", source.replace("page_not_found(", ""))
            self.assertNotIn("HttpResponse", source)
            self.assertIn("render(", source)
