# exeshop/views.py
from types import SimpleNamespace
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


# ──────────────────────────────────────────────────────────────
# Головна
def index(request):
    context = {
        "featured_products": [],
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "shop/index.html", context)


# ──────────────────────────────────────────────────────────────
# Список усіх категорій
def categories_list(request):
    context = {
        "categories": [],  # сюди підставиться queryset, коли з’явиться модель
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "shop/categories.html", context)


# ──────────────────────────────────────────────────────────────
# Товари певної категорії
def category(request, slug):                     # ←  **саме таке ім’я в shop/urls.py**
    context = {
        "category": SimpleNamespace(name=slug.capitalize()),
        "products": [],                          # queryset після появи моделей
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "shop/product_list.html", context)


# ──────────────────────────────────────────────────────────────
# Детальна сторінка товару
def product_detail(request, slug):
    context = {
        "product": SimpleNamespace(name=slug.capitalize()),
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "shop/product_detail.html", context)


# ──────────────────────────────────────────────────────────────
# Кошик
def cart(request):
    # тимчасова логіка кошика – тільки лічильник у сесії
    if request.method == "POST":
        request.session["cart_count"] = request.session.get("cart_count", 0) + 1
        return redirect("cart")

    context = {
        "cart_items": [],
        "cart_total": 0,
        "cart_count": request.session.get("cart_count", 0),
    }
    return render(request, "shop/cart.html", context)


# ──────────────────────────────────────────────────────────────
# AJAX-ендпойнт чату
@require_POST
def chat_endpoint(request):
    msg = request.POST.get("message", "").lower().strip()
    if msg in {"привіт", "добрий день", "вітаю"}:
        reply = "Вітаю! Чим можу допомогти?"
    elif msg:
        reply = f'Ви написали: «{msg}». Ще вчуся відповідати на складні запитання.'
    else:
        reply = "Поставте, будь ласка, запитання."
    return JsonResponse({"response": reply})


def order_create(request):
    # Заглушка для сторінки оформлення замовлення
    return render(request, "shop/order_create.html")
