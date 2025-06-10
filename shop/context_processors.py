from .models import Category, CartItem


def base_vars(request):
    """Підкидає всі категорії й лічильник кошика в кожен шаблон."""
    categories = Category.objects.all()
    cart_count = 0
    if request.session.session_key:
        cart_count = CartItem.objects.filter(
            cart__session_key=request.session.session_key
        ).count()
    return {"all_categories": categories, "cart_count": cart_count}
