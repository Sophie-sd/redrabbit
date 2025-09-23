from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .cart import Cart


def cart_detail(request):
    """Перегляд кошика"""
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    """Додавання товару в кошик"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart:detail')


@require_POST
def cart_remove(request, product_id):
    """Видалення товару з кошика"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:detail')
