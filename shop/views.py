from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# !!! залишились лише потрібні форми
from .forms import QuickOrderForm, RegistrationForm
from .models import Cart, CartItem, Category, Order, Product


# ───────────────────────── cart helpers ─────────────────────────────
def _get_cart(request: HttpRequest) -> Cart:
    """Створює / повертає кошик, прив’язаний до session_key."""
    if not request.session.session_key:
        request.session.save()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# ───────────────────────── storefront ───────────────────────────────
def index(request: HttpRequest) -> HttpResponse:
    products = Product.objects.order_by("-id")[:12]
    cart_count = _get_cart(request).items.count() if request.session.session_key else 0
    return render(request, "shop/index.html", {"products": products, "cart_count": cart_count})


def categories(request: HttpRequest) -> HttpResponse:
    return render(request, "shop/categories.html", {"categories": Category.objects.all()})


def product_list(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, "shop/product_list.html", {"category": category, "products": products})


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, slug=slug)
    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "form": QuickOrderForm(initial={"product_id": product.id}),
        },
    )


# ───────────────────────── cart ─────────────────────────────────────
def cart(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    items = cart.items.select_related("product")
    total: Decimal = sum(i.product.price * i.quantity for i in items)
    return render(request, "shop/cart.html", {"cart_items": items, "cart_total": total})


@require_POST
def cart_add(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=request.POST.get("product_id"))
    qty = max(1, int(request.POST.get("quantity", 1)))
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    item.quantity = item.quantity + qty if not created else qty
    item.save()
    return JsonResponse({"cart_count": cart.items.count()})


@require_POST
def cart_remove(request: HttpRequest, item_id: int) -> HttpResponse:
    cart = _get_cart(request)
    CartItem.objects.filter(id=item_id, cart=cart).delete()
    return redirect("shop:cart")


# ───────────────────────── registration / auth ──────────────────────
def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("shop:profile")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("shop:profile")
    return render(request, "shop/register.html", {"form": form})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    orders = Order.objects.filter(user=request.user).order_by("-created")[:10]
    return render(request, "shop/profile.html", {"orders": orders})


# ───────────────────────── AJAX / API ───────────────────────────────
def api_search(request: HttpRequest) -> JsonResponse:
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse([], safe=False)
    q_slug = slugify(q)
    from django.db.models import Q

    products = (
        Product.objects.filter(
            Q(name__icontains=q) |
            Q(slug__icontains=q_slug) |
            Q(description__icontains=q)
        )[:10]
    )
    return JsonResponse(
        [{"label": p.name, "url": p.get_absolute_url()} for p in products],
        safe=False,
    )


@csrf_exempt
@require_POST
def api_quick_order(request: HttpRequest) -> JsonResponse:
    try:
        data: dict[str, Any] = json.loads(request.body.decode())
        product_id = int(data.get("product_id"))
        phone = str(data.get("phone", "")).strip()
        if not (product_id and phone):
            raise ValueError
    except Exception:
        return HttpResponseBadRequest("invalid")

    # тут могла б бути логіка створення «швидкого замовлення»
    return JsonResponse({"ok": True})
