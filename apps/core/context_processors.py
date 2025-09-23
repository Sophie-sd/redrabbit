"""
Контекстні процесори для глобальних змінних
"""
from apps.products.models import Category
from apps.cart.cart import Cart


def base_context(request):
    """
    Додає базовий контекст до всіх шаблонів
    """
    context = {
        'main_categories': Category.objects.filter(parent=None, is_active=True)[:9],
        'site_name': 'Beauty Shop',
        'site_phone': '(068) 175-26-54',
        'site_email': 'beauty_shop_monte@ukr.net',
        'site_address': 'вул. Соборна, 126д, м. Монастирище, 19101, Україна',
    }
    
    # Додаємо кошик до контексту
    if hasattr(request, 'session'):
        cart = Cart(request)
        context['cart'] = cart
        context['cart_total_items'] = len(cart)
        context['cart_total_price'] = cart.get_total_price()
    
    return context
