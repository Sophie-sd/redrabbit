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
        'main_categories': Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name')[:9],
        'site_name': 'redrabbit',
        'site_phone': '+38 (093) 700-88-06',
        'site_email': 'redrabbit.store001@gmail.com',
        'site_address': 'Дискретна доставка по всій Україні',
    }
    
    # Додаємо кошик до контексту
    if hasattr(request, 'session'):
        cart = Cart(request)
        context['cart'] = cart
        context['cart_total_items'] = len(cart)
        context['cart_total_price'] = cart.get_total_price()
    
    return context
