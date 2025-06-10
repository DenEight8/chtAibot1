from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    BonusPoint,
    FAQ,
)

# ﹤──── кастом-UserAdmin з «вкладками» Jazzmin ────﹥
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Вкладки Jazzmin задаються через fieldsets.
    """
    fieldsets = (
        (_('Основне'),              {'fields': ('username', 'password')}),
        (_('Особиста інформація'),  {'fields': ('first_name', 'last_name', 'email')}),
        (_('Дозволи'),              {'fields': ('is_active', 'is_staff',
                                                'is_superuser', 'groups',
                                                'user_permissions')}),
        (_('Важливі дати'),         {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')


# ﹤──── Магазин ────﹥
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'image_tag')
    list_filter = ('category', 'in_stock')
    search_fields = ('name', 'description')
    readonly_fields = ('image_tag',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ('product',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'session_key')
    autocomplete_fields = ('user',)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'total_price', 'paid_with_bonus_points')
    list_filter = ('created', 'paid_with_bonus_points')
    search_fields = ('user__username',)
    autocomplete_fields = ('user',)
    inlines = [OrderItemInline]


@admin.register(BonusPoint)
class BonusPointAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'updated')
    autocomplete_fields = ('user',)
    search_fields = ('user__username',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question',)
