from django.shortcuts import render, redirect
from django.contrib import messages
from apps.cart.cart import Cart


def order_create(request):
    """Створення замовлення"""
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Ваш кошик порожній')
        return redirect('cart:detail')
    
    if request.method == 'POST':
        # Тут буде логіка створення замовлення
        # Поки що просто очищуємо кошик
        cart.clear()
        messages.success(request, 'Ваше замовлення прийнято!')
        return redirect('orders:success')
    
    return render(request, 'orders/create.html', {'cart': cart})


def order_success(request):
    """Сторінка успішного замовлення"""
    return render(request, 'orders/success.html')
