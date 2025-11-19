from apps.products.models import Category
from apps.cart.cart import Cart
from apps.wishlist.wishlist import Wishlist
from django.db.models import Count, Q, Prefetch


def base_context(request):
    new_category_slugs = [
        'for-women', 'for-men', 'for-couples', 
        'lubricants', 'foreplay', 'underwear-costumes', 
        'bdsm-fetish', 'sexual-health'
    ]
    
    children_queryset = Category.objects.filter(
        is_active=True
    ).annotate(
        products_count=Count('products', filter=Q(products__is_active=True), distinct=True) +
                       Count('primary_products', filter=Q(primary_products__is_active=True), distinct=True)
    ).filter(products_count__gt=0).order_by('sort_order', 'name')
    
    context = {
        'main_categories': Category.objects.filter(
            parent=None, 
            is_active=True,
            slug__in=new_category_slugs
        ).prefetch_related(
            Prefetch('children', queryset=children_queryset)
        ).order_by('sort_order', 'name'),
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
