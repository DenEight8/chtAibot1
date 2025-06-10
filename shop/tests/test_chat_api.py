import os
import django
from django.urls import reverse
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exeshop.settings")
os.environ.setdefault("ALLOWED_HOSTS", "testserver")
django.setup()

from shop.chat_api import _run_safe_sql  # noqa: E402
from shop.models import Category, Product  # noqa: E402


class ChatApiTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Cat", slug="cat")
        Product.objects.create(category=self.cat, name="A", slug="a", description="d", price=1)

    def test_run_safe_sql_valid(self):
        rows = _run_safe_sql("SELECT name, price FROM Product")
        self.assertEqual(rows[0]["name"], "A")

    def test_run_safe_sql_invalid(self):
        self.assertIsNone(_run_safe_sql("DELETE FROM Product"))

    def test_chat_sql_endpoint(self):
        url = reverse("shop:chat_api")
        resp = self.client.post(
            url,
            data="{\"message\": \"#sql: SELECT name FROM Product\"}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("| name |", resp.json()["answer"])
