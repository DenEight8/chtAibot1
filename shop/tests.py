from django.urls import reverse
from django.test import TestCase

from .models import Category, Product


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat", slug="cat")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            slug="test-product",
            description="desc",
            price="9.99",
        )

    def test_get_absolute_url_returns_correct_path(self):
        expected = reverse("shop:product_detail", args=[self.product.slug])
        self.assertEqual(self.product.get_absolute_url(), expected)


class ApiSearchTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Other", slug="other")
        self.product = Product.objects.create(
            category=self.category,
            name="Awesome Widget",
            slug="awesome-widget",
            description="desc",
            price="1.99",
        )

    def test_api_search_returns_expected_structure(self):
        url = reverse("shop:api_search")
        response = self.client.get(url, {"q": "Awesome"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0],
            {"label": self.product.name, "url": self.product.get_absolute_url()},
        )
