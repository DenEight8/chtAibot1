from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .chat_api import ChatBotAPIView

app_name = "shop"

urlpatterns = [
    # storefront
    path("", views.index, name="home"),
    path("categories/", views.categories, name="categories"),
    path("category/<slug:slug>/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    # cart
    path("cart/", views.cart, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),

    # auth
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="shop/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="shop:home"), name="logout"),
    path("profile/", views.profile, name="profile"),

    # ajax / api
    path("api/chat/", ChatBotAPIView.as_view(), name="chat_api"),
    path("api/search/", views.api_search, name="api_search"),
    path("api/quick_order/", views.api_quick_order, name="api_quick_order"),
]
