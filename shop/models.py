from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.urls import reverse

# Категорії товарів
class Category(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

# Товари
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=0)   # 0-5
    in_stock = models.BooleanField(default=True)

    def get_absolute_url(self) -> str:
        """Return the canonical product URL."""
        return reverse("shop:product_detail", args=[self.slug])

    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="60" />')
        return "—"

    image_tag.short_description = "Зображення"

    def __str__(self):
        return self.name

# Кошики
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=64, null=True, blank=True)
    def __str__(self):
        return f"Cart #{self.pk} (User: {self.user})"

# Товари в кошику
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product} x{self.quantity}"

# Замовлення
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    delivery_address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_with_bonus_points = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"

# Позиції в замовленні
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x{self.quantity}"

# Бонуси
class BonusPoint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    reason = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f"{self.user}: {self.points} points"

# Часті питання
class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.question[:60]

# Чат-бот звернення/історія діалогів (опціонально)
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'Bot' if self.is_bot else self.user}: {self.message[:40]}"

