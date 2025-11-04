from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.products.models import Product
from .cart import Cart


def cart_detail(request):
    """Перегляд кошика"""
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


def cart_count(request):
    """API для отримання кількості товарів у кошику"""
    cart = Cart(request)
    return JsonResponse({'count': len(cart)})


@require_POST
def cart_add(request, product_id):
    """Додавання товару в кошик"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        quantity = int(data.get('quantity', request.POST.get('quantity', 1)))
    except:
        quantity = int(request.POST.get('quantity', 1))
    
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'message': 'Товар додано до кошика',
            'cart_count': len(cart)
        })
    
    return redirect('cart:detail')


@require_POST
def cart_remove(request, product_id):
    """Видалення товару з кошика"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:detail')
