from apps.products.models import Category
from apps.cart.cart import Cart
from apps.wishlist.wishlist import Wishlist
from django.db.models import Prefetch, Count, Q
from django.core.cache import cache


def base_context(request):
    main_categories = cache.get('main_categories_menu')
    
    if main_categories is None:
        children_queryset = Category.objects.filter(
            is_active=True,
            parent__isnull=False
        ).select_related('parent').only('id', 'name', 'slug', 'parent_id', 'sort_order')
        
        main_categories = list(Category.objects.filter(
            parent=None, 
            is_active=True
        ).prefetch_related(
            Prefetch('children', queryset=children_queryset)
        ).only('id', 'name', 'slug', 'sort_order').order_by('sort_order', 'name'))
        
        cache.set('main_categories_menu', main_categories, 3600)
    
    context = {
        'main_categories': main_categories,
        'site_name': 'redrabbit',
        'site_phone': '+38 (093) 700-88-06',
        'site_email': 'redrabbit.store001@gmail.com',
        'site_address': 'Дискретна доставка по всій Україні',
    }
    
    if hasattr(request, 'session'):
        cart = Cart(request)
        context['cart'] = cart
        context['cart_total_items'] = len(cart)
        context['cart_total_price'] = cart.get_total_price()
        
        wishlist = Wishlist(request)
        context['wishlist_count'] = len(wishlist)
    
    return context
